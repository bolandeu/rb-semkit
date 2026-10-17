"""The step table: the library functions the pipeline runs, one entry per step (ADR 0008).

Each area keeps its entries in its own module of this package, as the list `STEPS`; `areas()` finds the modules, so
a new area needs no edit here. An entry names the step, the library function whose signature gives the options and
whose docstring gives the help, the kind of the step and how to prepare it from the options.

Kinds: change (writes the working column, or a new column), filter (keeps or drops rows), report (its table becomes
the current one). A prepared step takes the current table and the working column and gives its outcome: `Change`,
`Keep` or `Report`.

Helpers for the area modules: `change_step` and `changing` make a change step of a function over phrases (`slug`
names it, `changing` checks its options on no phrases at all); `Adapted` shows a function to the command generator
with other arguments (`option` makes the parameter), for a table or a file in place of an argument; a file option is
read by `table_of` and turned into the argument by `as_table`, `pairs_of`, `scores_of` or `texts_of` (`first_text`
names the column of the texts); `joined` gives the working column as one text.

The help of a step is made from the docstring: `doc_lines` joins the lines of a paragraph but keeps the items of a list
and the explanations of arguments as lines of their own, `argument_names` gives the arguments such an explanation is
for, and `parameter_names` the arguments of a function (and of the function an `Adapted` one wraps).
"""

from __future__ import annotations

import functools
import importlib
import inspect
import pkgutil
import re
from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass
from types import FunctionType
from typing import Any, Literal

import pandas as pd

from ..core.errors import InvalidArguments
from ..core.frame import Frame, text_columns
from ..pipeline.tables import STDIO, Source

Kind = Literal["change", "filter", "report"]
# A docstring line that explains arguments of the function: «mode: …», «`action`: …», «core, column: …», «first / last: …».
ARGUMENT_NAMES = r"`?\w+`?(?:(?:, | / )`?\w+`?)*"
ARGUMENT_LINE = re.compile(rf"^(?P<names>{ARGUMENT_NAMES}): ")
# An explanation of another argument inside a line, after the end of a sentence: «… is bad. good: a phrase …».
INLINE_ARGUMENT = re.compile(rf"(?<=[.;]) (?P<names>{ARGUMENT_NAMES}): ")
LIST_ITEM = re.compile(r"^(?:[-*]|\d+[.)]) ")


@dataclass(frozen=True)
class Change:
    """The new values of a column, with the index of the table."""

    values: pd.Series


@dataclass(frozen=True)
class Keep:
    """True for each row of the table that stays."""

    rows: pd.Series


@dataclass(frozen=True)
class Report:
    """The table that replaces the current one."""

    table: pd.DataFrame


Outcome = Change | Keep | Report
Prepared = Callable[[pd.DataFrame, str], Outcome]


@dataclass(frozen=True)
class Step:
    """One entry of the step table.

    prepare: the options (by the names of the function's arguments) → the prepared step; it raises
    InvalidArguments for an option the function refuses, before any input is read.
    note: what the step does with the function, the last paragraph of the help.
    new_column: for a change, the suffix of the column it adds next to the working column (`<column>_find`);
    None rewrites the working column.
    source, example: the file the `Example:` line of the help reads, and the text after the step name in it; None
    gives the example from the required options (a file option shows a file, a list option a bundled list).
    """

    name: str
    function: Callable[..., Any]
    kind: Kind
    prepare: Callable[[dict[str, Any]], Prepared]
    note: str
    new_column: str | None = None
    source: str = "core.csv"
    example: str | None = None

    def help(self) -> str:
        """The docstring of the function without its porting notes (paragraphs «ADR …»), then the note.

        The lines of a paragraph are joined, so the help wraps to the terminal; a line on an argument and an item of a
        list stay their own.
        """
        paragraphs = inspect.cleandoc(self.function.__doc__ or "").split("\n\n")
        names = parameter_names(self.function)
        kept = ["\n".join(doc_lines(text, names)) for text in paragraphs if not text.startswith("ADR ")]
        return "\n\n".join([*kept, self.note])


def parameter_names(function: Callable[..., Any]) -> set[str]:
    """The arguments of a function and of the function it adapts."""
    return set(inspect.signature(function).parameters) | set(inspect.signature(inspect.unwrap(function)).parameters)


def doc_lines(paragraph: str, parameters: Collection[str]) -> list[str]:
    """The lines of a docstring paragraph as the help shows them.

    A line goes on the line before it, unless it starts an item of a list or the explanation of arguments; so does
    the explanation of an argument of `parameters` that follows the end of a sentence.
    """
    lines: list[str] = []
    for line in paragraph.splitlines():
        text = line.strip()
        if lines and not (ARGUMENT_LINE.match(text) or LIST_ITEM.match(text)):
            lines[-1] += f" {text}"
        else:
            lines.append(text)
    return [part for line in lines for part in _argument_parts(line, parameters)]


def argument_names(found: re.Match[str]) -> list[str]:
    """The names an explanation of arguments (ARGUMENT_LINE or INLINE_ARGUMENT) is for."""
    return [name.strip("`") for name in re.split(r", | / ", found["names"])]


def _argument_parts(line: str, parameters: Collection[str]) -> list[str]:
    parts, start = [], 0
    for found in INLINE_ARGUMENT.finditer(line):
        if all(name in parameters for name in argument_names(found)):
            parts.append(line[start : found.start()])
            start = found.start() + 1
    return [*parts, line[start:]]


class Adapted:
    """A library function as the step table sees it, when its arguments have no command-line form of their own.

    `parameters` changes the signature: a name mapped to None is taken off (the step fills it from the current table),
    one mapped to a Parameter is replaced by it (a file option instead of a table), a name that is new is added at the
    end. `docs` are lines on the new arguments («name: text»), added to the docstring for the help of their options.
    """

    def __init__(self, function: FunctionType, parameters: Mapping[str, inspect.Parameter | None], *docs: str) -> None:
        signature = inspect.signature(function)
        kept = [parameters.get(name, parameter) for name, parameter in signature.parameters.items()]
        added = [parameter for name, parameter in parameters.items() if parameter and name not in signature.parameters]
        self.__wrapped__ = function
        self.__globals__ = getattr(function, "__globals__", {})  # the names the annotations are resolved in
        self.__name__ = function.__name__
        self.__module__ = function.__module__
        self.__doc__ = "\n\n".join([inspect.cleandoc(function.__doc__ or ""), "\n".join(docs)])
        self.__signature__ = signature.replace(parameters=[*(p for p in kept if p), *added])

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.__wrapped__(*args, **kwargs)


def option(name: str, annotation: Any = str, default: Any = inspect.Parameter.empty) -> inspect.Parameter:
    """A keyword-only parameter for `Adapted`."""
    return inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY, default=default, annotation=annotation)


def slug(function: FunctionType) -> str:
    """The name of the step of a function: its name with hyphens."""
    return function.__name__.replace("_", "-")


def table_of(path: str, option_name: str) -> pd.DataFrame:
    """The table in the file `path`, read as `read` does (types inferred, text columns text); '-' is the pipeline's input, so refused."""
    if path == STDIO:
        raise InvalidArguments(f"{option_name}: '-' is not allowed here; allowed: a file.")
    return Source(path).read()


def first_text(table: pd.DataFrame, option_name: str) -> str:
    """The first text column of a table read from a file."""
    found = text_columns(table)
    if not found:
        raise InvalidArguments(f"{option_name}: the file has no text column; allowed: a file with one.")
    return found[0]


def texts_of(table: pd.DataFrame, option_name: str) -> pd.Series:
    """The first text column of a table read from a file, as the texts."""
    return table[first_text(table, option_name)]


def as_table(table: pd.DataFrame, option_name: str) -> pd.DataFrame:
    """The table read from a file as it is."""
    return table


def pairs_of(table: pd.DataFrame, option_name: str) -> dict[str, str]:
    """The first column of a table read from a file mapped to its second."""
    if len(table.columns) < 2:
        raise InvalidArguments(f"{option_name}: the file has {len(table.columns)} column; allowed: two columns.")
    return dict(zip(table.iloc[:, 0], table.iloc[:, 1], strict=True))


def scores_of(table: pd.DataFrame, option_name: str) -> dict[str, float]:
    """The first column of a table read from a file mapped to the numbers of its second."""
    try:
        return {word: float(score) for word, score in pairs_of(table, option_name).items()}
    except ValueError:
        raise InvalidArguments(f"{option_name}: the second column holds text that is not a number.") from None


def joined(table: pd.DataFrame, column: str) -> str:
    """The cells of the working column as one text, one per line: «my text» for a step that compares texts."""
    return "\n".join(Frame(table, column).phrases)


def changing(
    function: Callable[..., Any], **files: tuple[str, Callable[[pd.DataFrame, str], Any]]
) -> Callable[[dict], Prepared]:
    """The `prepare` of a function that gives the new values of the working column.

    `files` names the arguments that the step takes from a file: the option that holds the file, and the callable that
    turns the table in it into the argument. The options are checked as the function checks them, on no phrases at all.
    """

    def prepare(options: dict) -> Prepared:
        given = {name: value for name, value in options.items() if name not in dict(files.values())}
        for argument, (name, read) in files.items():
            given[argument] = read(table_of(options[name], name), name)
        function(pd.Series([], dtype=object), **given)
        return lambda table, column: Change(function(Frame(table, column).phrases, **given))

    return prepare


CHANGE_NOTE = "The step rewrites the working column; with --as NAME it writes the result to a new column NAME."


def change_step(
    function: FunctionType, *, new_column: str | None = None, source: str = "core.csv", example: str | None = None
) -> Step:
    """The change step of a function that takes phrases and gives phrases (or one value per phrase)."""
    note = CHANGE_NOTE if new_column is None else f"The step writes its result to a new column <column>_{new_column}."
    return Step(slug(function), function, "change", changing(function), note, new_column, source, example)


@functools.cache
def areas() -> dict[str, tuple[Step, ...]]:
    """The steps of each area, by the name of its module, sorted by name."""
    found = {}
    for module in sorted(info.name for info in pkgutil.iter_modules(__path__)):
        found[module] = tuple(importlib.import_module(f"{__name__}.{module}").STEPS)
    return found


def ai_section() -> str:
    """The steps for an agent: each with its kind and the first line of its help, by area."""
    lines = [
        "## Pipeline steps",
        "",
        "`semkit read IN [--column C] [--whole] STEP… write OUT`; `semkit read IN STEP --help` shows a step.",
    ]
    for area, steps in areas().items():
        lines += ["", f"### {area}", ""]
        lines += [f"- `{step.name}` ({step.kind}): {step.help().splitlines()[0]}" for step in steps]
    return "\n".join(lines) + "\n"
