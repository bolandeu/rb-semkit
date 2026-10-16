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

    VBA (RibbonCallbacks.vba):
        remove: before the first `––·a` (line 2125) with include, `––·—` (line 2786) without; before the last `–—kk`
        (line 2923), `––··` (line 2389); after the first `––—–` (line 1791), `––—o` (line 2721); after the last
        `––—a` (line 2687), `––——` (line 2250).
        extract: before the first `–—–o` (line 2775) with include, `–—––` (line 1794) without (its bug fixed); after
        the last `–—o·` (line 2767), `–—–k` (line 1602) (its bug fixed); before the last, after the first: no VBA
        handler: derived from `–—–o` (line 2775) and `–—o·` (line 2767).
        The VBA finds the pattern as a substring as typed, in any case only in the remove buttons of the first
        occurrence; here it is found as whole words in any case.
    ADR 0005: ё = е; no double spaces in the results, none at the edges.
    """
    return Around(pattern, after=after, include=include, last=last)
