"""The steps over the rows of the table: fill-down fills empty cells, sample-rows keeps some rows, shuffle-rows mixes them."""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

import pandas as pd

from ..core.rows.functions import fill_down, sample_rows, shuffle_rows
from . import LONG, REPEATED, Adapted, Prepared, Step, View, option


def _prepare_fill_down(options: dict) -> Prepared:
    named = options["column"]

    def run(table: pd.DataFrame, column: str) -> View:
        names = named or [column]
        fill_down(table.iloc[:0], column=names)  # a missing column is refused before the cells are read
        filled = fill_down(table, column=names)
        changed = sum(int((filled[name].astype(str) != table[name].astype(str)).sum()) for name in names)
        return View(filled, column, cells_changed=changed)

    return run


def _prepare_rows(function: Callable[..., pd.DataFrame]) -> Callable[[dict], Prepared]:
    """The `prepare` of a step that keeps or reorders rows: the options are checked on no rows at all."""

    def prepare(options: dict) -> Prepared:
        function(pd.DataFrame(), **options)
        return lambda table, column: View(function(table, **options), column)

    return prepare


STEPS = [
    Step(
        "fill-down",
        Adapted(fill_down, {"column": option("column", Annotated[list[str] | None, REPEATED], None)}),
        "filter",
        _prepare_fill_down,
        "The step changes the cells of the named columns only. Without --column it fills the working column,"
        " which stays the same.",
    ),
    Step(
        "sample-rows",
        Adapted(sample_rows, {"n": option("n", Annotated[int | None, LONG], None)}),
        "filter",
        _prepare_rows(sample_rows),
        "The step changes no cell. The working column stays the same.",
    ),
    Step(
        "shuffle-rows",
        shuffle_rows,
        "filter",
        _prepare_rows(shuffle_rows),
        "The step changes no cell. The working column stays the same.",
    ),
]
