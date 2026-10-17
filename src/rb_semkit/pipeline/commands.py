"""A command for each entry of the step table: the options from the signature of its function, the help from its docstring.

An argument of the function becomes an option `--name` (`-n` for a one-letter name) with its default: a Literal gives
the choices, a bool a flag (`--name/--no-name` when it is on by default), an argument that takes items (an
`Iterable[str]`) a list in the form `items` reads. The arguments of the table itself (data, column, inplace) and the
ones with no command-line form (a lemmatizer, a Series) are left out. The first required argument is also taken
positionally (`remove-chars punctuation` is `remove-chars --kind punctuation`). A change step also takes `--as NAME`.

A step that takes items gets `ListsHelp`: its help ends with the names of the word lists (`takes_items` finds such a step).

The help of an option is the line of the docstring that starts with its name («mode: …»). The command checks every
option before any input is read: Click checks the types and choices, `Step.prepare` the rest.
"""

from __future__ import annotations

import collections.abc
import inspect
import re
import shlex
import typing
from collections.abc import Callable, Collection
from dataclasses import dataclass, replace
from itertools import takewhile
from types import NoneType, UnionType
from typing import Any, Literal

import typer
from rich.markup import escape
from typer.core import TyperCommand

from .. import output
from ..core import wordlists
from ..core.errors import InvalidArguments
from ..core.version import cli_name
from ..steps import ARGUMENT_LINE, LIST_ITEM, Prepared, Step, argument_names, doc_lines, parameter_names
from .items import SYNTAX, items
from .state import Planned

TABLE_ARGUMENTS = frozenset({"data", "column", "inplace"})
PLAIN_TYPES = (bool, int, float, str)
ITEM_TYPES = (collections.abc.Iterable, list, tuple)
# The files of tests/steps/fixtures that an example reads, by the option that takes the file.
FILE_EXAMPLES = {
    "against": "texts.csv",
    "competitors": "competitors.csv",
    "freq": "freq.csv",
    "pairs": "pairs.csv",
    "synonyms": "synonyms.csv",
    "dictionary": "dictionary.csv",
}
LIST_EXAMPLE = "@minus/universal"
NAME_EXAMPLES = {
    "what": "words",
    "to": "en",
    "tag": "source",
    "pattern": r"\d+",
    "query": "купить диван",
    "case": "genitive",
    "word": "диван",
}
PLAIN_EXAMPLES = {str: "купить", int: "2", float: "0.5"}
AS_HELP = "Write the result to a new column NAME and keep the working column as it is."
MISSING_HELP = "See the description above."
POSITIONAL_PREFIX = "positional_"  # the parameter of the command that takes the first required argument positionally


@dataclass(frozen=True)
class StepOption:
    """An argument of the function as a command-line option."""

    name: str
    annotation: Any  # what the command takes: a plain type, a Literal, or one of them | None
    default: Any  # ... when the option is required
    takes_items: bool
    help: str
    positional: bool = False  # the first required argument: also taken positionally, so neither form is required

    def flag(self) -> str:
        name = self.name.replace("_", "-")
        if len(name) == 1:
            return f"-{name}"
        return f"--{name}/--no-{name}" if self.annotation is bool and self.default is True else f"--{name}"

    def metavar(self) -> str:
        return self.name.upper()

    def value(self, values: dict[str, Any]) -> Any:
        """The value the function takes for what the command line gave, as the option or positionally."""
        given = self._given(values)
        return items(given) if self.takes_items and given is not None else given

    def _given(self, values: dict[str, Any]) -> Any:
        option = values[self.name]
        if not self.positional:
            return option
        argument = values[POSITIONAL_PREFIX + self.name]
        if option is not None and argument is not None:
            raise InvalidArguments(
                f"{self.flag()}: given twice, as {self.metavar()} {argument!r} and as {self.flag()} {option!r};"
                " allowed: one of them."
            )
        if option is None and argument is None:
            raise InvalidArguments(
                f"{self.metavar()}: not given; allowed: {self.metavar()} or {self.flag()} {self.metavar()}."
            )
        return argument if option is None else option

    def example(self) -> str:
        """The option as a runnable example: a file shows a file, a list a bundled list, a choice one of its values."""
        choices = typing.get_args(self.annotation) if typing.get_origin(self.annotation) is Literal else ()
        file = FILE_EXAMPLES.get(self.name)
        value = file or (choices[0] if choices else self._example_value())
        text = str(value) if re.fullmatch(r"[\w@/.,+=:-]+", str(value)) else shlex.quote(str(value))
        return text if self.positional and not file else f"{self.flag()} {text}"

    def _example_value(self) -> Any:
        if self.takes_items:
            return LIST_EXAMPLE
        return NAME_EXAMPLES.get(self.name) or PLAIN_EXAMPLES[self.annotation]


class ListsHelp(TyperCommand):
    """A step that takes items: its help ends with the word lists that exist when the help is shown."""

    @property
    def epilog(self) -> str:
        names = ", ".join(f"@{entry.name}" for entry in wordlists.names())
        return escape(f"Lists for @NAME: {names}. Run '{cli_name()} lists' for their sources and descriptions.")

    @epilog.setter
    def epilog(self, value: str | None) -> None:
        """Click sets the epilog in its constructor; the help takes it from the lists instead."""


def takes_items(step: Step) -> bool:
    """Whether an option of the step takes items."""
    return any(option.takes_items for option in step_options(step.function))


def help_hint(step: str) -> str:
    """The action of a step's usage error: read the help of the step."""
    return f"Run '{cli_name()} read IN {step} --help' for its options and their values."


def _resolved(function: Callable[..., Any], annotation: Any) -> Any:
    """An annotation of `function` as an object; one that names a type imported only for type checking is None."""

    def holder() -> None: ...

    holder.__annotations__ = {"value": annotation}
    try:
        return typing.get_type_hints(holder, globalns=getattr(function, "__globals__", {}))["value"]
    except NameError:
        return None


def _command_line_type(annotation: Any) -> tuple[Any, bool]:
    """What the command takes for `annotation` and whether it is a list of items; (None, False) for no form."""
    if typing.get_origin(annotation) is Literal or annotation in PLAIN_TYPES:
        return annotation, False
    if typing.get_origin(annotation) in ITEM_TYPES:
        return str, True
    if isinstance(annotation, UnionType) or typing.get_origin(annotation) is typing.Union:
        return _union_type(typing.get_args(annotation))
    return None, False


def _union_type(members: tuple[Any, ...]) -> tuple[Any, bool]:
    """A union takes items when a member does (`str | Iterable[str]`); else its one member with a form, maybe None."""
    forms = [_command_line_type(member) for member in members if member is not NoneType]
    takes_items = any(listed for _, listed in forms)
    single = str if takes_items else (forms[0][0] if len(forms) == 1 else None)
    if single is None or NoneType not in members:
        return single, takes_items
    return single | None, takes_items


def _option_help(doc: str, name: str, parameters: Collection[str]) -> str:
    """The text of the line of `doc` that names `name` («name: …», «name, other: …»), with the items of a list after it."""
    for paragraph in doc.split("\n\n"):
        lines = doc_lines(paragraph, parameters)
        for index, line in enumerate(lines):
            start = ARGUMENT_LINE.match(line)
            if start and name in argument_names(start):
                items = takewhile(LIST_ITEM.match, lines[index + 1 :])
                return "\n".join([line[start.end() :], *items])
    return ""


def _step_option(function: Callable[..., Any], parameter: inspect.Parameter) -> StepOption | None:
    """The option of one argument of `function`; None for an argument the command line does not give."""
    annotation, takes_items = _command_line_type(_resolved(function, parameter.annotation))
    required = parameter.default is inspect.Parameter.empty
    if parameter.name in TABLE_ARGUMENTS or (annotation is None and not required):
        return None
    if annotation is None:
        raise TypeError(f"{function!r}: the required argument {parameter.name!r} has no command-line form")
    text = _option_help(inspect.getdoc(function) or "", parameter.name, parameter_names(function)) or MISSING_HELP
    help_text = f"{text} {SYNTAX}" if takes_items else text
    return StepOption(parameter.name, annotation, ... if required else parameter.default, takes_items, help_text)


def step_options(function: Callable[..., Any]) -> list[StepOption]:
    """The options of the step whose function is `function`; the first required one is also positional."""
    found = [
        option
        for parameter in inspect.signature(function).parameters.values()
        if (option := _step_option(function, parameter))
    ]
    first = next((index for index, option in enumerate(found) if option.default is ...), None)
    if first is not None:
        found[first] = replace(found[first], positional=True)
    return found


def _help(step: Step, options: list[StepOption]) -> str:
    """The help of the step without the lines on arguments it has no option for, then its example."""
    given = step.example
    if given is None:
        given = " ".join(option.example() for option in options if option.default is ...)
    command = " ".join(part for part in ("{cli} read", step.source, step.name, given, "write out.csv") if part)
    return f"{shown_help(step, options)}\n\nExample: {command}"


def shown_help(step: Step, options: list[StepOption]) -> str:
    """The help of the step as the command line shows it: no line explains an argument the step has no option for."""
    names = {option.name for option in options}
    paragraphs = []
    for paragraph in step.help().split("\n\n"):
        lines = [line for line in paragraph.splitlines() if _for_options(line, names)]
        if lines:
            paragraphs.append("\n".join(lines))
    return "\n\n".join(paragraphs)


def _for_options(line: str, names: Collection[str]) -> bool:
    """Whether a line of the help is no explanation of arguments, or explains an option among `names`."""
    found = ARGUMENT_LINE.match(line)
    return not found or any(name in names for name in argument_names(found))


def _option_parameters(option: StepOption) -> list[inspect.Parameter]:
    """The option, and for the first required argument also the positional argument; then neither is required."""
    if not option.positional:
        default = typer.Option(option.default, option.flag(), help=escape(option.help))
        return [
            inspect.Parameter(
                option.name, inspect.Parameter.KEYWORD_ONLY, default=default, annotation=option.annotation
            )
        ]
    annotation = option.annotation | None
    help_text = escape(f"{option.help} The same as {option.flag()} {option.metavar()}.")
    argument = typer.Argument(None, metavar=option.metavar(), help=help_text, show_default=False)
    flag = typer.Option(None, option.flag(), metavar=option.metavar(), help=escape(option.help))
    return [
        inspect.Parameter(
            POSITIONAL_PREFIX + option.name, inspect.Parameter.KEYWORD_ONLY, default=argument, annotation=annotation
        ),
        inspect.Parameter(option.name, inspect.Parameter.KEYWORD_ONLY, default=flag, annotation=annotation),
    ]


def _parameters(step: Step, options: list[StepOption]) -> list[inspect.Parameter]:
    context = inspect.Parameter("ctx", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=typer.Context)
    found = [parameter for option in options for parameter in _option_parameters(option)]
    if step.kind == "change":
        found.append(
            inspect.Parameter(
                "as_column",
                inspect.Parameter.KEYWORD_ONLY,
                default=typer.Option(None, "--as", metavar="NAME", help=AS_HELP),
                annotation=str | None,
            )
        )
    return [context, *found]


def _in_cli_terms(message: str, options: list[StepOption]) -> str:
    """A message of the library with its argument names as the options of the command line: «mode='x'» → «--mode 'x'»."""
    for option in options:
        flag = option.flag().split("/")[0]
        message = re.sub(rf"(?<![\w-]){option.name}=", f"{flag} ", message)
        message = re.sub(rf"^`?{option.name}`?:", f"{flag}:", message)
    return message


def _refused(step: Step, options: list[StepOption], error: InvalidArguments) -> InvalidArguments:
    """An error of the step as the command line names it: the step, its options, an action in CLI terms."""
    message = _in_cli_terms(error.message, options)
    named = [flag for option in options if (flag := option.flag().split("/")[0]) in message]
    action = help_hint(step.name)
    if named:
        action = f"Give {', '.join(named)} a value the message allows. {action}"
    return InvalidArguments(f"{step.name}: {message}", action=error.action or action)


def _reported_run(step: Step, options: list[StepOption], prepared: Prepared) -> Prepared:
    """The prepared step; an error it raises on the table names the step and its options."""

    def run(table, column):
        try:
            return prepared(table, column)
        except InvalidArguments as error:
            raise _refused(step, options, error) from None

    return run


def step_command(step: Step) -> Callable[..., Planned]:
    """The command of `step`: it checks its options and gives the step planned, or a usage error naming it."""
    options = step_options(step.function)

    def command(ctx: typer.Context, as_column: str | None = None, **values: Any) -> Planned:
        try:
            arguments = {option.name: option.value(values) for option in options}
            return Planned(step, _reported_run(step, options, step.prepare(arguments)), as_column)
        except InvalidArguments as error:
            raise _refused(step, options, error) from None

    parameters = _parameters(step, options)
    command.__signature__ = inspect.Signature(parameters)  # ty: ignore[unresolved-attribute]
    command.__annotations__ = {parameter.name: parameter.annotation for parameter in parameters}
    command.__name__ = command.__qualname__ = step.name.replace("-", "_")
    command.__doc__ = _help(step, options)
    command.opencli_metadata = {"x-rb-kind": step.kind}  # ty: ignore[unresolved-attribute]
    return output.guard(command)
