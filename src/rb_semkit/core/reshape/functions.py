"""`group_rows`, `split_rows` and `unpivot`: the rows of a group as one row, a cell cut into rows, columns as rows."""

from __future__ import annotations

import pandas as pd
from pandas.api import types

from ..errors import InvalidArguments
from ..table.functions import require_column

COUNT = "count"


def _empty(column: pd.Series) -> pd.Series:
    """True for each cell that is empty or holds only spaces."""
    return column.isna() | (column.astype(str).str.strip() == "")


def _require_sep(sep: str) -> None:
    if not sep:
        raise InvalidArguments("sep: is empty; allowed: one or more characters.")


def _require_named(by: list[str] | None, argument: str) -> list[str]:
    if not by:
        raise InvalidArguments(f"{argument}: not given; allowed: a column of the table, repeated for each next one.")
    return by


def group_rows(
    data: pd.DataFrame, *, column: str, by: list[str] | None = None, sep: str = ", ", sum: list[str] | None = None
) -> pd.DataFrame:
    """One row for each group of rows that hold the same cells in the columns of by.

    The groups come in the order of the first row of each. The row holds the group columns, the cells of the working
    column joined by sep (empty cells left out), count (the rows of the group) and the sum of each column of sum. The
    other columns are dropped. The sum columns hold numbers: «5,5» counts as 5.5. A column that is not in the table is
    refused, naming the columns there are.

    by: the column to group by; repeat it for each next column.
    sep: the text between the joined phrases.
    sum: the column of numbers to add up in each group; repeat it for each next column.

    Example: {cli} read reshape/clusters.csv group-rows --by cluster --sum freq write -
    -> диван, купить диван, диван недорого, 2, 15; кресло, кресло, 1, 3
    """
    keys, added = _require_named(by, "by"), sum or []
    _require_sep(sep)
    _require_group_columns(data, column, keys, added)
    phrases = data[column].where(~_empty(data[column]), None)
    grouped = data.assign(**{column: phrases}).groupby(keys, sort=False, dropna=False)
    columns = {
        column: (column, lambda cells: sep.join(cells.dropna().astype(str))),
        COUNT: (column, "size"),
        **{name: (name, "sum") for name in added},
    }
    return grouped.agg(**columns).reset_index()


def _require_group_columns(data: pd.DataFrame, column: str, keys: list[str], added: list[str]) -> None:
    """The columns of by and sum are in the table, the sum ones hold numbers, none is a column of the result."""
    for argument, names in (("by", keys), ("sum", added)):
        for name in names:
            require_column(data, argument, name)
    require_column(data, "column", column)
    for name in keys + added:
        if name in (column, COUNT):
            raise InvalidArguments(
                f"by, sum: {name!r} is a column of the result already; allowed: any other column than the working"
                f" column and {COUNT!r}."
            )
    for name in added:
        if not types.is_numeric_dtype(data[name]):
            raise InvalidArguments(f"sum: {name!r} does not hold numbers.")


def split_rows(data: pd.DataFrame, *, column: str, sep: str = ",") -> pd.DataFrame:
    """One row for each part of the cells of the working column, cut by sep.

    The spaces at the edges of a part are trimmed, an empty part makes no row. The other columns are copied to each new
    row. A cell with no sep stays one row, an empty cell stays one row with an empty cell. A column that is not in the
    table is refused, naming the columns there are.

    sep: the text that cuts a cell.

    Example: {cli} read reshape/cells.csv split-rows --sep ";" write -
    -> диван, 7; софа, 7; кресло, 3
    """
    _require_sep(sep)
    require_column(data, "column", column)
    cells = data[column]
    cut = cells.astype(str).str.contains(sep, regex=False) & ~_empty(cells)
    trimmed = cells.astype(str).str.split(sep, regex=False).map(lambda texts: [t.strip() for t in texts if t.strip()])
    pieces = trimmed.where(cut, pd.Series([[cell] for cell in cells], index=cells.index, dtype=object))
    kept = pieces.map(bool).astype(bool)  # a cell cut into empty parts only makes no row
    return data.assign(**{column: pieces})[kept].explode(column).reset_index(drop=True)


def unpivot(
    data: pd.DataFrame, *, keep: list[str] | None = None, name_column: str = "column", value_column: str = "value"
) -> pd.DataFrame:
    """The kept columns stay; every other column turns into rows.

    Each kept row gives one row for each other column: the kept cells, the name of the column in name_column and its
    cell in value_column, in the order of the columns. A column that is not in the table is refused, naming the columns
    there are; so is keep with every column, and a name_column or value_column that a kept column has already.

    keep: the column to keep; repeat it for each next column.
    name_column: the column that holds the name of the unpivoted column.
    value_column: the column that holds the cell of the unpivoted column.

    Example: {cli} read reshape/regions.csv unpivot --keep phrase write -
    -> диван, msk, 10; диван, spb, 4
    """
    kept = _require_named(keep, "keep")
    for name in kept:
        require_column(data, "keep", name)
    if set(kept) == set(data.columns):
        raise InvalidArguments(
            f"keep: names every column of the table; allowed: fewer than the {len(data.columns)} there are."
        )
    for argument, name in (("name_column", name_column), ("value_column", value_column)):
        if name in kept:
            raise InvalidArguments(
                f"{argument}: {name!r} is a kept column already; allowed: a name no kept column has."
            )
    if name_column == value_column:
        raise InvalidArguments(f"value_column: {value_column!r} is the name_column too; allowed: another name.")
    long = data.reset_index(drop=True).melt(
        id_vars=kept, var_name=name_column, value_name=value_column, ignore_index=False
    )
    return long.sort_index(kind="stable").reset_index(drop=True)
