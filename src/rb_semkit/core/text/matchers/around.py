"""The text before or after the first or the last occurrence of a pattern."""

from __future__ import annotations

import re

from ...errors import InvalidArguments
from ..base import Matcher
from .spans import SpanMatcher

YO_YE = "её"


def _whole_words(pattern: str) -> re.Pattern[str]:
    """The pattern as written, as whole words, in any case, ё and е alike."""
    literal = "".join(f"[{YO_YE}]" if char in YO_YE else re.escape(char) for char in pattern.lower())
    return re.compile(rf"(?<!\w){literal}(?!\w)", re.IGNORECASE)


class Around(SpanMatcher):
    find = Matcher.find

    def __init__(self, pattern: str, *, after: bool, include: bool, last: bool) -> None:
        if not isinstance(pattern, str) or not pattern.strip():
            raise InvalidArguments(f"pattern={pattern!r}; allowed: a non-empty word or words.")
        self._pattern = _whole_words(pattern.strip())
        self._after = after
        self._include = include
        self._last = last

    def spans(self, phrase: str) -> list[tuple[int, int]]:
        hits = list(self._pattern.finditer(phrase))
        if not hits:
            return []
        hit = hits[-1 if self._last else 0]
        if self._after:
            return [(hit.start() if self._include else hit.end(), len(phrase))]
        return [(0, hit.end() if self._include else hit.start())]


def around(pattern: str, *, after: bool = False, include: bool = False, last: bool = False) -> Around:
    """The part of the phrase before (`after=False`) or after the first (`last=False`) or last occurrence of `pattern`.

    The pattern is a word or words as written, found as whole words, in any case, ё as е. `include=True` adds the
    occurrence itself to the part. A phrase without the pattern has no part: remove leaves it, extract gives ''.
    Remove and extract only.
    """
    return Around(pattern, after=after, include=include, last=last)
