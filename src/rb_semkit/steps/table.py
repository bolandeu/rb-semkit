"""The steps that work on the table as a whole: use-column switches the working column, sort-rows orders the rows."""

from __future__ import annotations

from typing import Annotated

import pandas as pd

from ..core.errors import InvalidArguments
from ..core.table.functions import sort_rows, use_column
from . import REPEATED, Adapted, Prepared, Step, View, numbers_of, option


def _prepare_use_column(options: dict) -> Prepared:
    name = options["name"]
    return lambda table, column: View(use_column(table, name), name)


def _as_numbers(table: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """The table with each column of `by` that holds number text as numbers («5,5» is 5.5); texts stay texts."""
    converted = {}
    for name in by:
        try:
            converted[name] = numbers_of(table[name], name)
        except (InvalidArguments, KeyError):
            continue
    return table.assign(**converted)


def _prepare_sort_rows(options: dict) -> Prepared:
    by, desc = options["by"], options["desc"]

    def run(table: pd.DataFrame, column: str) -> View:
        sort_rows(table.iloc[:0], by=by, desc=desc)  # a missing column is refused before the cells are read
        order = sort_rows(_as_numbers(table, by), by=by, desc=desc).index
        return View(table.loc[order], column)

    return run


STEPS = [
    Step(
        "use-column",
        use_column,
        "filter",
        _prepare_use_column,
        "The step changes no cell and no row: the column NAME is the working column of the next steps."
        " With drop-cells empty after it, the rows with an empty cell in NAME are dropped.",
    ),
    Step(
        "sort-rows",
        Adapted(sort_rows, {"by": option("by", Annotated[list[str] | None, REPEATED], None)}),
        "filter",
        _prepare_sort_rows,
        "The step changes no cell. The working column stays the same.",
    ),
]
