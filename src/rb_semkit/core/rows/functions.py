"""`fill_down`, `sample_rows` and `shuffle_rows`: the rows of a table filled from above, a sample of them, their random order."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from ..errors import InvalidArguments
from ..table.functions import require_column


def _empty(column: pd.Series) -> pd.Series:
    """True for each cell that is empty or holds only spaces."""
    return column.isna() | (column.astype(str).str.strip() == "")


def fill_down(data: pd.DataFrame, *, column: list[str] | None = None) -> pd.DataFrame:
    """The table where, in each named column, an empty cell takes the value of the nearest filled cell above it.

    A cell that holds only spaces is empty too. Empty cells before the first filled cell stay as they are. The other
    columns do not change. A column that is not in the table is refused, naming the columns there are.

    column: the column to fill; repeat it for each next column.

    Example: {cli} read rows/groups.csv fill-down --column group write -
    -> , 0; A, 1; A, 2; A, 3; B, 4; B, 5
    """
    if not column:
        raise InvalidArguments("column: not given; allowed: a column of the table, repeated for each next one.")
    for name in column:
        require_column(data, "column", name)
    filled = {}
    for name in column:
        values = data[name]
        above = values.mask(_empty(values)).ffill()
        filled[name] = above.where(above.notna(), values)
    return data.assign(**filled)


def _kept(size: int, n: int | None, share: float | None) -> int:
    """How many of `size` rows stay, by `n` or by `share` (rounded to the nearest whole number, a half up)."""
    if (n is None) == (share is None):
        raise InvalidArguments("n, share: give one of them, not both and not neither.")
    if n is not None:
        if n < 0:
            raise InvalidArguments(f"n: {n} is negative; allowed: 0 or more.")
        return min(n, size)
    if share is None or not 0 < share <= 1:
        raise InvalidArguments(f"share: {share} is out of range; allowed: above 0 up to 1.")
    return math.floor(size * share + 0.5)


def sample_rows(
    data: pd.DataFrame, *, n: int | None = None, share: float | None = None, seed: int | None = None
) -> pd.DataFrame:
    """N rows of the table, or a share of them, chosen at random; the rows keep their order.

    A share is rounded to the nearest whole number of rows. An n larger than the table keeps every row. The same seed
    chooses the same rows each run; without a seed each run chooses anew. Give n or share, one of them.

    n: how many rows to keep.
    share: the share of the rows to keep, above 0 up to 1.
    seed: a whole number that makes the choice the same each run.

    Example: {cli} read freq.csv sample-rows --n 2 --seed 1 write -
    -> диван купить, 10; купить диван, 8
    """
    count = _kept(len(data), n, share)
    chosen = np.random.default_rng(seed).choice(len(data), size=count, replace=False)
    return data.iloc[np.sort(chosen)]


def shuffle_rows(data: pd.DataFrame, *, seed: int | None = None) -> pd.DataFrame:
    """The same rows in a random order.

    The same seed gives the same order each run; without a seed each run orders anew.

    seed: a whole number that makes the order the same each run.

    Example: {cli} read freq.csv shuffle-rows --seed 3 write -
    -> кресло, 5; купить диван, 8; диван купить, 10
    """
    return data.iloc[np.random.default_rng(seed).permutation(len(data))]
