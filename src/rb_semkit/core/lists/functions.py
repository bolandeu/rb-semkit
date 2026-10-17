"""`compare_lists`: the phrases of two lists that are in both, in either, or in only one of them.

«The same phrase» is the key of `dupes` for the kind. An empty phrase has no key, so it is never a phrase of the result.
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from ..dupes.functions import DupeKind, key_function
from ..errors import InvalidArguments
from ..frame import Frame, map_unique
from ..morph.lemmatizer import Lemmatizer

OPS = ("both", "either", "first", "second")


def _keyed(phrases: pd.Series, key_of: Callable[[str], str]) -> pd.DataFrame:
    """The non-empty phrases with their keys, the first phrase of each key only, in the input order."""
    keys = map_unique(phrases, key_of)
    table = pd.DataFrame({"phrase": phrases.to_numpy(), "key": keys.to_numpy()})
    return table[table["key"] != ""].drop_duplicates("key")


def compare_lists(
    first: pd.Series | pd.DataFrame,
    second: pd.Series | pd.DataFrame,
    *,
    op: str = "both",
    kind: DupeKind = "exact",
    lemmatizer: Lemmatizer | None = None,
    column: str | None = None,
    second_column: str | None = None,
) -> pd.Series:
    """The phrases of two lists by `op`: both (of `first` that are in `second`), either (`first`, then `second`),
    first (only in `first`), second (only in `second`).

    The same phrase is the same key of `dupes` for `kind`. A phrase keeps the spelling of its first occurrence and
    comes once; the order is the input order. Empty cells are never phrases.
    """
    if op not in OPS:
        raise InvalidArguments(f"op: {op!r} is not an operation; allowed: {', '.join(OPS)}.")
    key_of = key_function(kind, lemmatizer)
    left = _keyed(Frame(first, column).phrases, key_of)
    right = _keyed(Frame(second, second_column, argument="second_column").phrases, key_of)
    if op == "both":
        result = left[left["key"].isin(right["key"])]
    elif op == "first":
        result = left[~left["key"].isin(right["key"])]
    elif op == "second":
        result = right[~right["key"].isin(left["key"])]
    else:
        result = pd.concat([left, right]).drop_duplicates("key")
    return pd.Series(result["phrase"].to_numpy(), dtype=object)
