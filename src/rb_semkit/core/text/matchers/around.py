"""The text before or after the first or the last occurrence of a pattern."""

from __future__ import annotations

import re

import pandas as pd

from ...errors import InvalidArguments
from ...frame import map_unique
from ..base import Matcher, collapse

# ё = е (ADR 0005): each of the two letters matches both, in the case written
YO_YE = {"е": "[её]", "ё": "[её]", "Е": "[ЕЁ]", "Ё": "[ЕЁ]"}


def _occurrences(pattern: str, *, any_case: bool) -> re.Pattern[str]:
    """Every start of `pattern` as a substring, overlapping ones too; group 1 is the occurrence."""
    literal = "".join(YO_YE.get(char) or re.escape(char) for char in pattern)
    return re.compile(f"(?=({literal}))", re.IGNORECASE if any_case else 0)


class Around(Matcher):
    def __init__(self, pattern: str, *, after: bool, include: bool, last: bool) -> None:
        if not isinstance(pattern, str) or not pattern:
            raise InvalidArguments(f"pattern={pattern!r}; allowed: a non-empty text.")
        self._after = after
        self._include = include
        self._last = last
        # the add-in ignores case only in the remove buttons of the first occurrence
        self._removed = _occurrences(pattern, any_case=not last)
        self._extracted = _occurrences(pattern, any_case=False)

    def _part(self, phrase: str, occurrences: re.Pattern[str]) -> tuple[int, int] | None:
        """The (start, stop) of the part before or after the chosen occurrence; None when there is none."""
        found = list(occurrences.finditer(phrase))
        if not found:
            return None
        start, stop = found[-1 if self._last else 0].span(1)
        if self._after:
            return (start if self._include else stop, len(phrase))
        return (0, stop if self._include else start)

    def remove(self, phrases: pd.Series) -> pd.Series:
        def without(phrase: str) -> str:
            part = self._part(phrase, self._removed)
            return collapse(phrase if part is None else phrase[: part[0]] + phrase[part[1] :])

        return map_unique(phrases, without)

    def extract(self, phrases: pd.Series) -> pd.Series:
        def found(phrase: str) -> str:
            part = self._part(phrase, self._extracted)
            return "" if part is None else collapse(phrase[part[0] : part[1]])

        return map_unique(phrases, found)


def around(pattern: str, *, after: bool = False, include: bool = False, last: bool = False) -> Around:
    """The part of the phrase before (`after=False`) or after the first (`last=False`) or last occurrence of `pattern`.

    The pattern is text as typed, found anywhere, also inside a word («в» is found in «диван»). remove finds the
    first occurrence in any case and the last one in the case written; extract matches the case written. ё = е.
    `include=True` adds the occurrence itself to the part. A phrase without the pattern has no part: remove leaves
    it, extract gives ''. Remove and extract only.

    VBA (RibbonCallbacks.vba):
        remove: before the first `––·a` (line 2125) with include, `––·—` (line 2786) without; before the last `–—kk`
        (line 2923), `––··` (line 2389); after the first `––—–` (line 1791), `––—o` (line 2721); after the last
        `––—a` (line 2687), `––——` (line 2250).
        extract: before the first `–—–o` (line 2775) with include, `–—––` (line 1794) without (its bug fixed); after
        the last `–—o·` (line 2767), `–—–k` (line 1602) (its bug fixed); before the last, after the first: no VBA
        handler: derived from `–—–o` (line 2775) and `–—o·` (line 2767).
    ADR 0005: ё = е; no double spaces in the results, none at the edges.
    """
    return Around(pattern, after=after, include=include, last=last)
