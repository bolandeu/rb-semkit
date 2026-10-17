"""The step table: the library functions the pipeline runs, one entry per step (ADR 0008).

Each area keeps its entries in its own module of this package, as the list `STEPS`; `areas()` finds the modules, so
a new area needs no edit here. An entry names the step, the library function whose signature gives the options and
whose docstring gives the help, the kind of the step and how to prepare it from the options.

Kinds: change (writes the working column, or a new column), filter (keeps or drops rows), report (its table becomes
the current one). A prepared step takes the current table and the working column and gives its outcome: `Change`,
`Keep` or `Report`.
"""

from __future__ import annotations

import functools
import importlib
import inspect
import pkgutil
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

import pandas as pd

Kind = Literal["change", "filter", "report"]
# A docstring line that explains an argument of the function: «mode: …», «`action`: …».
ARGUMENT_LINE = re.compile(r"^`?(\w+)`?: ")


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
    """

    name: str
    function: Callable[..., Any]
    kind: Kind
    prepare: Callable[[dict[str, Any]], Prepared]
    note: str
    new_column: str | None = None

    def help(self) -> str:
        """The docstring of the function without its porting notes (paragraphs «ADR …»), then the note.

        The lines of a paragraph are joined, so the help wraps to the terminal; a line on an argument stays its own.
        """
        paragraphs = inspect.cleandoc(self.function.__doc__ or "").split("\n\n")
        kept = [_reflowed(text) for text in paragraphs if not text.startswith("ADR ")]
        return "\n\n".join([*kept, self.note])


def _reflowed(paragraph: str) -> str:
    lines: list[str] = []
    for line in paragraph.splitlines():
        if lines and not ARGUMENT_LINE.match(line):
            lines[-1] += f" {line.strip()}"
        else:
            lines.append(line.strip())
    return "\n".join(lines)


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
