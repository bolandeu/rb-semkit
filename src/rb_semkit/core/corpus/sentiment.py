"""Sentiment of phrases by your own dictionary of scored words."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from numbers import Real
from typing import Literal

import pandas as pd

from ..errors import InvalidArguments
from ..frame import Frame, map_unique
from ..normalize import norm_phrase
from ..text.base import choice, split_words

__all__ = ["sentiment"]

Statistic = Literal["mean", "min", "max"]
STATISTICS: dict[Statistic, Callable[[list[float]], float]] = {
    "mean": lambda found: sum(found) / len(found),
    "min": min,
    "max": max,
}


def _scores(scores: Mapping[str, float]) -> dict[str, float]:
    """The scores by word key; the first of two words with one key wins."""
    keyed: dict[str, float] = {}
    for word, score in dict(scores).items():
        if not isinstance(word, str) or len(split_words(word)) != 1:
            raise InvalidArguments(f"scores: the word {word!r}; allowed: one word per item.")
        if isinstance(score, bool) or not isinstance(score, Real):
            raise InvalidArguments(f"scores: {word!r} has {score!r}; allowed: a number.")
        keyed.setdefault(norm_phrase(word), float(score))
    return keyed


def sentiment(
    data: pd.Series | pd.DataFrame,
    scores: Mapping[str, float],
    *,
    what: Statistic = "mean",
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """The score of each phrase by the scored words it holds: their mean, min or max.

    scores: a dictionary word → number («отличный» 5, «плохой» -3); words match in any case and with ё = е, and a word
    repeated in the phrase counts each time.
    what: "mean", "min" or "max" of the scores of the words. A phrase with no scored word gets an empty value.

    Example: {cli} read --text "отличный диван" --text "плохой диван" --text "диван" sentiment dictionary.csv write -
    -> отличный диван, 5.0; плохой диван, -3.0; диван,
    """
    statistic = STATISTICS[choice("what", what, tuple(STATISTICS))]
    keyed = _scores(scores)

    def score(phrase: str) -> float:
        found = [keyed[key] for key in map(norm_phrase, split_words(phrase)) if key in keyed]
        return statistic(found) if found else math.nan

    frame = Frame(data, column, inplace)
    return frame.put(map_unique(frame.phrases, score).astype(float), "sentiment")
