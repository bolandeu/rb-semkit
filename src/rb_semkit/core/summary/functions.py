"""summary: one row of statistics per numeric column of a table."""

from __future__ import annotations

import pandas as pd

from ..compare.shared import DECIMALS, wholes_kept
from ..errors import InvalidArguments

COLUMNS = ["column", "count", "mean", "median", "min", "max"]
NUMBERS = COLUMNS[2:]


def summary(data: pd.DataFrame) -> pd.DataFrame:
    """The count, mean, median, min and max of each numeric column of a table: a row per column.

    The columns: column, the name; count, the cells with a number; mean, median, min, max. Numbers are rounded to 4
    decimals, as the comparisons round; a column of whole numbers gives whole numbers where they are whole. A column
    of text and a column of true / false are left out. A table without a numeric column is refused.
    parse-html, then text-stats, then summary gives the table «all pages: mean, median».

    Example: {cli} read freq.csv summary write -
    -> freq, 3, 7.6667, 8, 5, 10
    """
    if not isinstance(data, pd.DataFrame):
        raise InvalidArguments(f"data is a {type(data).__name__}; allowed: a table (a DataFrame).")
    numbers = data.select_dtypes("number")
    if numbers.columns.empty:
        raise InvalidArguments("data: the table has no numeric column; allowed: a table with a column of numbers.")
    table = pd.DataFrame(
        {
            "column": numbers.columns.astype(str),
            "count": numbers.count().to_numpy(),
            "mean": numbers.mean().round(DECIMALS).to_numpy(),
            "median": numbers.median().round(DECIMALS).to_numpy(),
            "min": numbers.min().round(DECIMALS).to_numpy(),
            "max": numbers.max().round(DECIMALS).to_numpy(),
        },
        columns=COLUMNS,
    )
    counted = numbers.dtypes.map(pd.api.types.is_integer_dtype).to_numpy()
    return table.assign(**wholes_kept(table[NUMBERS], counted))
