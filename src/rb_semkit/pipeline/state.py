"""The state of a pipeline: the current table, the working column, and what each step did to them.

A step sees the working column as text; a number column stays numbers in the table, and the values a step writes back
to it are numbers again when every one of them is a number. A column --as makes becomes the working column; a new
column of a step (`<column>_find`) that the table has already gets a number (`<column>_find_2`).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import cast

import pandas as pd
from pandas.api import types

from ..core.errors import InvalidArguments
from ..core.frame import text_columns
from ..steps import Change, Columns, Keep, Prepared, Report, Step
from .tables import as_text, numbers


@dataclass(frozen=True)
class Planned:
    """A step of the command line with its options checked and its outcome to come."""

    step: Step
    run: Prepared
    as_column: str | None = None


@dataclass(frozen=True)
class Summary:
    """One step: the rows before and after it, the cells it changed, and what else the step tells (`note`)."""

    step: str
    rows_before: int
    rows_after: int
    cells_changed: int
    note: str | None = None

    def line(self) -> str:
        line = f"{self.step}: {self.rows_before} → {self.rows_after} rows, {self.cells_changed} cells changed"
        return line if self.note is None else f"{line}; {self.note}"

    def to_dict(self) -> dict:
        """The summary as --json gives it; `note` only when the step tells one."""
        return {name: value for name, value in asdict(self).items() if name != "note" or value is not None}


def _working_column(table: pd.DataFrame) -> str:
    """The first text column, else the first column: a number column is text for the steps."""
    found = text_columns(table) or list(table.columns)
    if not found:
        raise InvalidArguments("read: the input is empty.", action="Name a table with a header and rows.")
    return found[0]


def _column_taken(planned: Planned) -> InvalidArguments:
    name = planned.as_column
    return InvalidArguments(
        f"{planned.step.name}: --as {name}: the table has a column {name} already.",
        action=f"Give --as a name the table does not have, or rename the column {name} in the input.",
    )


def check_as(steps: Iterable[Planned], columns: Iterable[str]) -> None:
    """Refuse --as NAME of a column of the input or of an earlier --as, up to the first report (its columns are new)."""
    known = set(columns)
    for planned in steps:
        if planned.step.kind == "report":
            return
        if planned.as_column is not None:
            if planned.as_column in known:
                raise _column_taken(planned)
            known.add(planned.as_column)


def _free_name(table: pd.DataFrame, name: str) -> str:
    """`name`, or `name_2`, `name_3`… when the table has it."""
    found, number = name, 1
    while found in table.columns:
        number += 1
        found = f"{name}_{number}"
    return found


def _cells_changed(values: pd.Series, old: pd.Series | None) -> pd.Series:
    """The cells a change counts: the marked ones of a bool column; else against the old values, or the non-empty ones."""
    if types.is_bool_dtype(values):
        return values
    if old is None:
        return values.notna() & (values.astype(str) != "")
    return values != old


class State:
    """The current table and its working column. With `journal`, every cell a step changes and every row it drops."""

    def __init__(self, table: pd.DataFrame, column: str | None, *, journal: bool = False) -> None:
        if column is not None and column not in table.columns:
            raise InvalidArguments(
                f"read: --column {column}: the input has no such column.",
                action=f"Name one of its columns: {', '.join(map(str, table.columns)) or 'none'}.",
            )
        self.table = table
        self.column = column if column is not None else _working_column(table)
        self.journal: list[dict] | None = [] if journal else None
        self._last_added: dict[str, str] = {}  # the column added last next to a column: the next one goes after it

    def apply(self, planned: Planned) -> Summary:
        before = len(self.table)
        changed = 0
        note = None
        match planned.run(self._as_steps_see_it(), self.column):
            case Change(values):
                if len(values) < len(self.table):  # a change that also drops rows: remove-cells empty
                    self._keep(planned.step.name, self.table.index.isin(values.index))
                changed = self._change(planned, values)
            case Columns(table, note, renamed):
                if renamed is not None:
                    self._rename(renamed)
                changed = sum(self._add(planned.step.name, str(name), values) for name, values in table.items())
            case Keep(rows):
                self._keep(planned.step.name, rows.to_numpy())
            case Report(table):
                self.table = table
                self.column = _working_column(table)
        return Summary(planned.step.name, before, len(self.table), changed, note)

    def _rename(self, name: str) -> None:
        """The working column under `name`; the columns added after it stay after it."""
        self.table = self.table.rename(columns={self.column: name})
        if self.column in self._last_added:
            self._last_added[name] = self._last_added.pop(self.column)
        self.column = name

    def _as_steps_see_it(self) -> pd.DataFrame:
        """The table with the working column as text."""
        if self.column in text_columns(self.table):
            return self.table
        return self.table.assign(**{self.column: as_text(self.table[self.column])})

    def _keep(self, step: str, rows) -> None:
        self._note(step, self.column, self.table[self.column][~rows], None)
        self.table = self.table[rows]

    def _target(self, planned: Planned) -> str:
        if planned.as_column is not None:
            if planned.as_column in self.table.columns:
                raise _column_taken(planned)
            return planned.as_column
        suffix = planned.step.new_column
        return _free_name(self.table, f"{self.column}_{suffix}") if suffix else self.column

    def _change(self, planned: Planned, values: pd.Series) -> int:
        """Put `values` into the target column; a column --as made becomes the working one."""
        target = self._target(planned)
        old = self.table[self.column]
        changed = _cells_changed(values, as_text(old) if target == self.column else None)
        self._note(planned.step.name, target, old[changed], values[changed])
        if target == self.column:
            self.table = self.table.assign(**{target: numbers(values) if types.is_numeric_dtype(old) else values})
        else:
            self._insert(target, values)
        if planned.as_column is not None:
            self.column = target
        return int(changed.sum())

    def _add(self, step: str, name: str, values: pd.Series) -> int:
        """Add a column of a step's `Columns` after the working column: `name`, or `name_2` when the table has it."""
        target = _free_name(self.table, str(name))
        changed = _cells_changed(values, None)
        self._note(step, target, self.table[self.column][changed], values[changed])
        self._insert(target, values)
        return int(changed.sum())

    def _insert(self, target: str, values: pd.Series) -> None:
        """A new column right after the working column and the columns added after it before."""
        table = self.table.copy(deep=False)
        after = self._last_added.get(self.column, self.column)
        table.insert(table.columns.get_loc(after if after in table.columns else self.column) + 1, target, values)
        self._last_added[self.column] = target
        self.table = table

    def _note(self, step: str, column: str, before: pd.Series, after: pd.Series | None) -> None:
        if self.journal is None:
            return
        for row, value in before.items():
            self.journal.append(
                {
                    "row": cast(int, row) + 1,  # the row of the input file, 1 for the first one under the header
                    "step": step,
                    "column": column,
                    "before": value,
                    "after": None if after is None else after[row],
                }
            )
