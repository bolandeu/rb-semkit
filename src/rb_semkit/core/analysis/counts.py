"""Counts of a semantic core: words and chars of a phrase, occurrences of a phrase, share of a weight and ABC class."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..errors import InvalidArguments
from ..frame import Frame
from ..text.base import split_words
from .weights import weights_of

WHAT = ("words", "chars", "count", "number", "share", "abc")
NEEDS_WEIGHT = ("share", "abc")
# ABC classes: the upper bound of the cumulative share, and the class below it.
ABC_BOUNDS = ((0.8, "A"), (0.95, "B"))
ABC_REST = "C"


def _abc(share: float) -> str:
    return next((name for bound, name in ABC_BOUNDS if share <= bound), ABC_REST)


def _shares(weights: pd.Series) -> pd.Series:
    """The cumulative share of the weight sum, from the heaviest row down, on the order of the input."""
    order = np.argsort(-weights.to_numpy(), kind="stable")
    cumulative = weights.to_numpy()[order].cumsum() / weights.sum()
    shares = np.empty(len(weights))
    shares[order] = cumulative
    return pd.Series(shares, index=weights.index)


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
    phrase stands in the core; "number" — which occurrence of it this row is (1 for the first);
    "share" — the cumulative share of the sum of `weight` (0..1), from the heaviest phrase down;
    "abc" — the class by that share: "A" up to 80 %, "B" up to 95 %, "C" the rest. "share" and "abc" need `weight`.
    """
    if what not in WHAT:
        raise InvalidArguments(f"what={what!r}; allowed: {', '.join(repr(item) for item in WHAT)}.")
    frame = Frame(data, column, inplace)
    phrases = frame.phrases
    weights = weights_of(frame, weight)
    if what in NEEDS_WEIGHT:
        if weights is None:
            raise InvalidArguments(f"what={what!r} needs weight; allowed: the name of a numeric column.")
        shares = _shares(weights)
        result = shares if what == "share" else shares.map(_abc)
    else:
        result = _count(what, phrases.reset_index(drop=True))
    return frame.put(result.set_axis(phrases.index), what)


def _count(what: str, values: pd.Series) -> pd.Series:
    if what == "words":
        return values.map(lambda phrase: len(split_words(phrase)))
    if what == "chars":
        return values.str.len()
    if what == "count":
        return values.groupby(values).transform("size")
    return values.groupby(values).cumcount() + 1
