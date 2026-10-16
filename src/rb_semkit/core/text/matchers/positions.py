"""Characters by position: the first or the last N."""

from __future__ import annotations

from ..base import Matcher, whole_number
from .spans import SpanMatcher


class Positions(SpanMatcher):
    find = Matcher.find

    def __init__(self, count: int, *, last: bool = False) -> None:
        self._count = whole_number("count", count)
        self._last = last

    def spans(self, phrase: str) -> list[tuple[int, int]]:
        size = len(phrase)
        return [(max(size - self._count, 0), size)] if self._last else [(0, min(self._count, size))]


def positions(count: int, *, last: bool = False) -> Positions:
    """The first `count` characters of a phrase, or the last ones with `last=True` (remove and extract)."""
    return Positions(count, last=last)
