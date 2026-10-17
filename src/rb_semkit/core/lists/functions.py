"""`compare_lists`: the phrases of two lists that are in both, in either, or in only one of them.

«The same phrase» is the key of `dupes` for the kind. An empty phrase has no key, so it is never a phrase of the result.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal, get_args

import pandas as pd

from ..dupes.functions import DupeKind, key_function
from ..errors import InvalidArguments
from ..frame import Frame, map_unique
from ..morph.lemmatizer import Lemmatizer

Op = Literal["both", "either", "first", "second"]
OPS = get_args(Op)


def _keyed(phrases: pd.Series, key_of: Callable[[str], str]) -> pd.DataFrame:
    """The non-empty phrases with their keys, the first phrase of each key only, in the input order."""
    keys = map_unique(phrases, key_of)
    table = pd.DataFrame({"phrase": phrases.to_numpy(), "key": keys.to_numpy()})
    return table[table["key"] != ""].drop_duplicates("key")


def compare_lists(
    first: pd.Series | pd.DataFrame,
    second: pd.Series | pd.DataFrame,
    *,
    op: Op = "both",
    kind: DupeKind = "exact",
    lemmatizer: Lemmatizer | None = None,
    column: str | None = None,
    second_column: str | None = None,
) -> pd.Series:
    """The phrases of two lists, by an operation.

    op: both (the phrases of the first list that are in the second), either (the first list, then the second), first
    (only in the first list), second (only in the second).
    kind: when two phrases are the same, as for dupes: exact, explicit, implicit or lemmas.
    first: the first list.
    second: the second list.
    second_column: the column of the phrases of the second list.
    lemmatizer: what gives the lemmas.

    A phrase keeps the spelling of its first occurrence and comes once; the order is the input order. Empty cells are
    never phrases.
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
