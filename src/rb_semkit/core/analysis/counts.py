"""Counts of a semantic core: words and chars of a phrase, occurrences of a phrase, shares of a weight and ABC class."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..errors import InvalidArguments
from ..frame import Frame
from ..normalize import norm_phrase
from ..text.base import split_words
from .weights import weights_of

WHAT = ("words", "chars", "count", "number", "share", "share_of_total", "abc")
NEEDS_WEIGHT = ("share", "share_of_total", "abc")
# ABC classes: the upper bound of the cumulative share, and the class below it.
ABC_BOUNDS = ((0.8, "A"), (0.95, "B"))
ABC_REST = "C"


def _abc(share: float) -> str:
    return next((name for bound, name in ABC_BOUNDS if share <= bound), ABC_REST)


def _heaviest_first_shares(weights: pd.Series) -> pd.Series:
    """The cumulative share of the weight sum, from the heaviest row down, on the order of the input."""
    order = np.argsort(-weights.to_numpy(), kind="stable")
    cumulative = weights.to_numpy()[order].cumsum() / weights.sum()
    shares = np.empty(len(weights))
    shares[order] = cumulative
    return pd.Series(shares, index=weights.index)


def _weight_count(what: str, weights: pd.Series) -> pd.Series:
    total = weights.sum()
    if total == 0:
        return pd.Series(np.nan, index=weights.index)
    if what == "share":
        return weights.cumsum() / total
    if what == "share_of_total":
        return weights / total
    shares = _heaviest_first_shares(weights)
    return shares.map(_abc)


def counts(
    data: pd.Series | pd.DataFrame,
    what: str,
    *,
    weight: str | None = None,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """One count per phrase, as a Series or a new column `<column>_<what>`.

    what: "words" and "chars" — the words and the characters of the phrase; "count" — how many times the same
    phrase stands in the core; "number" — which occurrence of it this row is (1 for the first).
    Phrases are the same by case and ё (ADR 0005); an empty cell has no count (empty value).
    "share" — the cumulative share of the sum of `weight` (0..1) in row order; "share_of_total" — the
    value over the sum; both are empty when the sum is 0.
    "abc" — the class by the cumulative share from the heaviest phrase down: "A" up to 80 %, "B" up to
    95 %, "C" the rest. "share", "share_of_total" and "abc" need `weight`.
    """
    if what not in WHAT:
        raise InvalidArguments(f"what={what!r}; allowed: {', '.join(repr(item) for item in WHAT)}.")
    frame = Frame(data, column, inplace)
    phrases = frame.phrases
    weights = weights_of(frame, weight)
    if what in NEEDS_WEIGHT:
        if weights is None:
            raise InvalidArguments(f"what={what!r} needs weight; allowed: the name of a numeric column.")
        result = _weight_count(what, weights)
    else:
        result = _count(what, phrases.reset_index(drop=True))
    return frame.put(result.set_axis(phrases.index), what)


def _count(what: str, values: pd.Series) -> pd.Series:
    if what == "words":
        return values.map(lambda phrase: len(split_words(phrase)))
    if what == "chars":
        return values.str.len()
    keys = values.map(norm_phrase)
    groups = keys.groupby(keys)
    found = groups.transform("size") if what == "count" else groups.cumcount() + 1
    return found.astype("Int64").mask(keys == "")
