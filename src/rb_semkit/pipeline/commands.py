"""A command for each entry of the step table: the options from the signature of its function, the help from its docstring.

An argument of the function becomes an option `--name` (`-n` for a one-letter name) with its default: a Literal gives
the choices, a bool a flag (`--name/--no-name` when it is on by default), an argument that takes items (an
`Iterable[str]`) a list in the form `items` reads. The arguments of the table itself (data, column, inplace) and the
ones with no command-line form (a lemmatizer, a Series) are left out. A change step also takes `--as NAME`.

The help of an option is the line of the docstring that starts with its name («mode: …»). The command checks every
option before any input is read: Click checks the types and choices, `Step.prepare` the rest.
"""

from __future__ import annotations

import collections.abc
import inspect
import typing
from collections.abc import Callable
from dataclasses import dataclass
from types import NoneType, UnionType
from typing import Any, Literal

import typer
from rich.markup import escape

from .. import output
from ..core.errors import InvalidArguments
from ..core.version import cli_name
from ..steps import ARGUMENT_LINE, Step
from .items import SYNTAX, items
from .state import Planned

TABLE_ARGUMENTS = frozenset({"data", "column", "inplace"})
PLAIN_TYPES = (bool, int, float, str)
ITEM_TYPES = (collections.abc.Iterable, list, tuple)
EXAMPLE_VALUES = {str: "купить", int: "2", float: "0.5"}
AS_HELP = "Write the result to a new column NAME and keep the working column as it is."
MISSING_HELP = "See the description above."


@dataclass(frozen=True)
class StepOption:
    """An argument of the function as a command-line option."""

    name: str
    annotation: Any  # what the command takes: a plain type, a Literal, or one of them | None
    default: Any  # ... when the option is required
    takes_items: bool
    help: str

    def flag(self) -> str:
        name = self.name.replace("_", "-")
        if len(name) == 1:
            return f"-{name}"
        return f"--{name}/--no-{name}" if self.annotation is bool and self.default is True else f"--{name}"

    def value(self, given: Any) -> Any:
        """The value the function takes for what the command line gave."""
        return items(given) if self.takes_items and given is not None else given

    def example(self) -> str:
        choices = typing.get_args(self.annotation) if typing.get_origin(self.annotation) is Literal else ()
        value = choices[0] if choices else EXAMPLE_VALUES[str if self.takes_items else self.annotation]
        return f"{self.flag()} {value}"


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


def _option_help(doc: str, name: str) -> str:
    """The line of `doc` that starts with `name:`, and the lines after it up to a blank one or another such line."""
    lines = doc.splitlines()
    for index, line in enumerate(lines):
        start = ARGUMENT_LINE.match(line)
        if start and start.group(1) == name:
            found = [line[start.end() :]]
            for following in lines[index + 1 :]:
                if not following.strip() or ARGUMENT_LINE.match(following):
                    break
                found.append(following.strip())
            return " ".join(found)
    return ""


def step_options(function: Callable[..., Any]) -> list[StepOption]:
    """The options of the step whose function is `function`."""
    doc = inspect.getdoc(function) or ""
    found = []
    for name, parameter in inspect.signature(function).parameters.items():
        annotation, takes_items = _command_line_type(_resolved(function, parameter.annotation))
        required = parameter.default is inspect.Parameter.empty
        if name in TABLE_ARGUMENTS or (annotation is None and not required):
            continue
        if annotation is None:
            raise TypeError(f"{function!r}: the required argument {name!r} has no command-line form")
        text = _option_help(doc, name) or MISSING_HELP
        default = ... if required else parameter.default
        found.append(StepOption(name, annotation, default, takes_items, f"{text} {SYNTAX}" if takes_items else text))
    return found


def _help(step: Step, options: list[StepOption]) -> str:
    required = "".join(f" {option.example()}" for option in options if option.default is ...)
    return f"{step.help()}\n\nExample: {{cli}} read core.csv {step.name}{required} write out.csv"


def _parameters(step: Step, options: list[StepOption]) -> list[inspect.Parameter]:
    context = inspect.Parameter("ctx", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=typer.Context)
    found = [
        inspect.Parameter(
            option.name,
            inspect.Parameter.KEYWORD_ONLY,
            default=typer.Option(option.default, option.flag(), help=escape(option.help)),
            annotation=option.annotation,
        )
        for option in options
    ]
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


def step_command(step: Step) -> Callable[..., Planned]:
    """The command of `step`: it checks its options and gives the step planned, or a usage error naming it."""
    options = step_options(step.function)

    def command(ctx: typer.Context, as_column: str | None = None, **values: Any) -> Planned:
        try:
            arguments = {option.name: option.value(values[option.name]) for option in options}
            return Planned(step, step.prepare(arguments), as_column)
        except InvalidArguments as error:
            raise InvalidArguments(f"{step.name}: {error.message}", action=help_hint(step.name)) from None

    parameters = _parameters(step, options)
    command.__signature__ = inspect.Signature(parameters)  # ty: ignore[unresolved-attribute]
    command.__annotations__ = {parameter.name: parameter.annotation for parameter in parameters}
    command.__name__ = command.__qualname__ = step.name.replace("-", "_")
    command.__doc__ = _help(step, options)
    return output.guard(command)
