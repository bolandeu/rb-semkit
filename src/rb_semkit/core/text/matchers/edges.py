"""Edges: the given characters cut from the start and from the end of each word."""

from __future__ import annotations

import pandas as pd

from ...errors import InvalidArguments
from ...frame import map_unique
from ..base import Matcher, split_words

__all__ = ["edges"]


def _characters(argument: str, value: str) -> str:
    if not isinstance(value, str):
        raise InvalidArguments(f"{argument}={value!r}; allowed: a string of characters.")
    return value


class Edges(Matcher):
    def __init__(self, start: str, end: str) -> None:
        self._start = _characters("start", start)
        self._end = _characters("end", end)

    def _clean(self, phrase: str) -> str:
        words = (word.lstrip(self._start).rstrip(self._end) for word in split_words(phrase))
        return " ".join(word for word in words if word)

    def remove(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, self._clean)


def edges(start: str = "", end: str = "") -> Edges:
    """The characters to cut from the edges of each word (remove only).

    start: characters cut from the start of a word, any run of them; end: the same at its end. Characters inside a
    word stay («wi-fi»); a word of only those characters disappears. The result has single spaces, none at the edges.
    """
    return Edges(start, end)
