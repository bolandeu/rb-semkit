"""The steps that change the shape of the table: group-rows, split-rows, unpivot."""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

import pandas as pd

from ..core.reshape.functions import group_rows, split_rows, unpivot
from . import REPEATED, Adapted, Prepared, Step, View, numbers_of, option

PLACEHOLDER = "working column"


def _probed(function: Callable[..., pd.DataFrame], names: list[str], **options) -> None:
    """Check the options on a table with no rows and the columns `names` (and a working column)."""
    table = pd.DataFrame({name: pd.Series(dtype=float) for name in [*names, PLACEHOLDER]})
    function(table, **options)


def _prepare_group_rows(options: dict) -> Prepared:
    by, sums = options["by"] or [], options["sum"] or []
    _probed(lambda table, **given: group_rows(table, column=PLACEHOLDER, **given), [*by, *sums], **options)

    def run(table: pd.DataFrame, column: str) -> View:
        numbers = {name: numbers_of(table[name], f"--sum {name}") for name in sums if name in table.columns}
        return View(group_rows(table.assign(**numbers), column=column, **options), column)

    return run


def _prepare_split_rows(options: dict) -> Prepared:
    _probed(lambda table, **given: split_rows(table, column=PLACEHOLDER, **given), [], **options)
    return lambda table, column: View(split_rows(table, column=column, **options), column)


def _prepare_unpivot(options: dict) -> Prepared:
    _probed(unpivot, options["keep"] or [], **options)
    return lambda table, column: View(unpivot(table, **options), options["value_column"])


STEPS = [
    Step(
        "group-rows",
        Adapted(
            group_rows,
            {
                "column": None,
                "by": option("by", Annotated[list[str] | None, REPEATED], None),
                "sum": option("sum", Annotated[list[str] | None, REPEATED], None),
            },
        ),
        "filter",
        _prepare_group_rows,
        "The step drops the other columns. The working column stays the same: it holds the joined phrases.",
    ),
    Step(
        "split-rows",
        Adapted(split_rows, {"column": None}),
        "filter",
        _prepare_split_rows,
        "The step changes no other column. The working column stays the same.",
    ),
    Step(
        "unpivot",
        Adapted(unpivot, {"keep": option("keep", Annotated[list[str] | None, REPEATED], None)}),
        "filter",
        _prepare_unpivot,
        "The step makes the value column the working column.",
    ),
]
