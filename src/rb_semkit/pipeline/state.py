"""The state of a pipeline: the current table, the working column, and what each step did to them."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd
from pandas.api import types

from ..core.errors import InvalidArguments
from ..core.frame import Frame, text_columns
from ..steps import Change, Keep, Prepared, Report, Step


@dataclass(frozen=True)
class Planned:
    """A step of the command line with its options checked and its outcome to come."""

    step: Step
    run: Prepared
    as_column: str | None = None


@dataclass(frozen=True)
class Summary:
    """One step: the rows before and after it and the cells it changed."""

    step: str
    rows_before: int
    rows_after: int
    cells_changed: int

    def line(self) -> str:
        return f"{self.step}: {self.rows_before} → {self.rows_after} rows, {self.cells_changed} cells changed"

    def to_dict(self) -> dict:
        return asdict(self)


def _first_text_column(table: pd.DataFrame) -> str:
    found = text_columns(table)
    if not found:
        raise InvalidArguments(
            f"column: the table has no text column; allowed: a table with one ({list(table.columns)})."
        )
    return found[0]


class State:
    """The current table and its working column. With `journal`, every cell a step changes and every row it drops."""

    def __init__(self, table: pd.DataFrame, column: str | None, *, journal: bool = False) -> None:
        self.table = table
        if column is not None:
            Frame(table, column)  # a column that is not in the table, or holds no text, is refused here
        self.column = column if column is not None else _first_text_column(table)
        self.journal: list[dict] | None = [] if journal else None

    def apply(self, planned: Planned) -> Summary:
        before = len(self.table)
        changed = 0
        match planned.run(self.table, self.column):
            case Change(values):
                changed = self._change(planned, values)
            case Keep(rows):
                self._note(planned.step.name, self.column, self.table[self.column][~rows], None)
                self.table = self.table[rows.to_numpy()]
            case Report(table):
                self.table = table
                self.column = _first_text_column(table)
        return Summary(planned.step.name, before, len(self.table), changed)

    def _change(self, planned: Planned, values: pd.Series) -> int:
        """Put `values` into the target column; the cells changed: the marked ones of a bool column, else the new text."""
        suffix = planned.step.new_column
        target = planned.as_column or (f"{self.column}_{suffix}" if suffix else self.column)
        old = self.table[self.column]
        changed = values if types.is_bool_dtype(values) else values != old
        self._note(planned.step.name, target, old[changed], values[changed])
        table = self.table.copy(deep=False)
        if target in table.columns:
            table[target] = values
        else:
            table.insert(table.columns.get_loc(self.column) + 1, target, values)
        self.table = table
        return int(changed.sum())

    def _note(self, step: str, column: str, before: pd.Series, after: pd.Series | None) -> None:
        if self.journal is None:
            return
        for row, value in before.items():
            self.journal.append(
                {
                    "row": row,
                    "step": step,
                    "column": column,
                    "before": value,
                    "after": None if after is None else after[row],
                }
            )
