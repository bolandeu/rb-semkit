"""`lookup`: the columns of a lookup table added to a table, row by row, by a key phrase."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..dupes.functions import DupeKind, key_function
from ..errors import InvalidArguments
from ..frame import map_unique, text_columns
from ..table.functions import require_column

SUFFIX = "_lookup"
REPEATED_KEYS = "repeated_keys"  # the name in `attrs` of the result: how many keys repeat in the lookup table


def _key_columns(data: pd.DataFrame, other: pd.DataFrame, on: str | None) -> tuple[str, str]:
    """The key column of the table and the one of the lookup table: `on` is KEY or MAIN=LOOKUP; without it, the first
    text column of each."""
    if on is None:
        found = text_columns(data), text_columns(other)
        if not all(found):
            raise InvalidArguments("on: not given and a table has no text column; allowed: KEY or MAIN=LOOKUP.")
        return found[0][0], found[1][0]
    main, _, lookup_name = on.partition("=")
    return main, lookup_name or main


def _require_in_lookup(other: pd.DataFrame, argument: str, name: str) -> None:
    try:
        require_column(other, argument, name)
    except InvalidArguments as refusal:
        raise InvalidArguments(str(refusal).replace("is not in the table", "is not in the lookup table")) from None


def _keys(column: pd.Series, kind: DupeKind) -> pd.Series:
    """The key of each cell by the kind; an empty cell has the empty key, which matches nothing."""
    phrases = column.astype(object).where(column.notna(), "").astype(str)
    return map_unique(phrases, key_function(kind, None))


def _first_rows(keys: pd.Series) -> pd.Series:
    """The position in the lookup table of the first row of each filled key."""
    return pd.Series(np.arange(len(keys)), index=keys.to_numpy())[keys.to_numpy() != ""].groupby(level=0).first()


def lookup(
    data: pd.DataFrame,
    other: pd.DataFrame,
    *,
    on: str | None = None,
    kind: DupeKind = "exact",
    take: list[str] | None = None,
    matched_only: bool = False,
) -> pd.DataFrame:
    """The table with the columns of the lookup table added, row by row, by a key phrase.

    A row takes the cells of the first row of the lookup table whose key is the same by the kind. A row with no match
    keeps empty cells; with matched_only it is dropped. The rows keep their order. A lookup column whose name the table
    has gets the suffix _lookup. The attribute repeated_keys of the result counts the keys that stand in the lookup
    table more than once. A column that is not in a table is refused, naming the columns there are.

    on: the key column, or MAIN=LOOKUP when the lookup table calls it differently; without it, the first text column of each table.
    kind: how two keys are the same: exact (the same text), explicit (the same in any case, with ё as е and any spaces),
    implicit (the same words in another order) or lemmas (the same lemmas in any order).
    take: the column of the lookup table to add; repeat it for each next column; without it, every other column.
    matched_only: drop the rows that have no match.

    Example: {cli} read phrases.csv lookup lookup/urls.csv --take url --matched-only write -
    -> купить диван, /buy-divan; кресло, /kreslo
    """
    main, key_column = _key_columns(data, other, on)
    require_column(data, "on", main)
    _require_in_lookup(other, "on", key_column)
    names = [name for name in other.columns if name != key_column] if take is None else take
    for name in names:
        _require_in_lookup(other, "take", name)
    keys = _keys(other[key_column], kind)
    first = _first_rows(keys)
    positions = _keys(data[main], kind).map(first)
    matched = positions.notna().to_numpy()
    rows = positions.fillna(0).astype(int).to_numpy()
    added = {}
    for name in names:
        cells = other[name].iloc[rows] if len(other) else pd.Series([""] * len(data), dtype=object)
        cells = cells.set_axis(data.index)
        added[name + SUFFIX if name in data.columns else name] = (
            cells if matched.all() else cells.astype(object).where(matched, "")
        )
    joined = data.assign(**added)
    joined.attrs[REPEATED_KEYS] = int((keys[keys != ""].value_counts() > 1).sum())
    return joined[matched] if matched_only else joined
