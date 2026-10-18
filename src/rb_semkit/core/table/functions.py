"""`use_column` and `sort_rows`: the working column of the next steps, and the order of the rows."""

from __future__ import annotations

import numpy as np
import pandas as pd
from pandas.api import types

from ..errors import InvalidArguments


def _require(table: pd.DataFrame, argument: str, name: str) -> None:
    if name not in table.columns:
        listed = ", ".join(repr(column) for column in table.columns) or "none"
        raise InvalidArguments(f"{argument}: {name!r} is not in the table; allowed: {listed}.")


def use_column(data: pd.DataFrame, name: str) -> pd.DataFrame:
    """The column that the next steps work on; the table does not change.

    A column that is not in the table is refused, naming the columns there are.

    name: the column to work on.

    Example: {cli} read matches.csv use-column match drop-cells empty write -
    -> купить диван, диван купить, 0.95; стол, столик, 0.9
    """
    _require(data, "name", name)
    return data


def _keys(column: pd.Series) -> list[pd.Series]:
    """What a column is ordered by, the main key first: numbers as they are; texts by the lower case with «ё» as «е»,
    then as written, so «ё» comes after «е»."""
    if types.is_numeric_dtype(column):
        return [column]
    texts = column.astype(object).where(column.notna(), "").astype(str)
    return [texts.str.lower().str.replace("ё", "е"), texts]


def _ranks(column: pd.Series, *, desc: bool) -> list[np.ndarray]:
    """The rank of each cell by each key of the column; the rank of an empty cell is after all others."""
    empty = column.isna() | (column.astype(str) == "")
    found = []
    for key in _keys(column):
        rank = key.mask(empty).rank(method="dense").astype("float64")
        found.append((-rank if desc else rank).fillna(np.inf).to_numpy())
    return found


def sort_rows(data: pd.DataFrame, *, by: list[str] | None = None, desc: bool = False) -> pd.DataFrame:
    """The rows in the order of a column, numbers as numbers, texts as `sort-words` orders words (ё after е).

    Equal rows keep their order, empty cells come last (also with desc). With several columns the first wins and
    each next one breaks the ties. A column that is not in the table is refused, naming the columns there are.

    by: the column to order by; repeat it for each next column.
    desc: the biggest first, the texts from the end.

    Example: {cli} read freq.csv sort-rows --by freq write -
    -> кресло, 5; купить диван, 8; диван купить, 10
    Example: {cli} read freq.csv sort-rows --by freq --desc write -
    -> диван купить, 10; купить диван, 8; кресло, 5
    """
    if not by:
        raise InvalidArguments("by: not given; allowed: a column of the table, repeated for each next one.")
    for name in by:
        _require(data, "by", name)
    keys = [rank for name in by for rank in _ranks(data[name], desc=desc)]
    return data.iloc[np.lexsort(keys[::-1])]
