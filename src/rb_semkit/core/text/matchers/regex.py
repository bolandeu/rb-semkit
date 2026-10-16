"""A regular expression: the first match or all of them; or the phrases that do NOT match."""

from __future__ import annotations

from ..base import compiled
from .spans import SpanMatcher


class Regex(SpanMatcher):
    def __init__(self, pattern: str, *, all_matches: bool, invert: bool) -> None:
        self._pattern = compiled("pattern", pattern)
        self._all = all_matches
        self._invert = invert

    def spans(self, phrase: str) -> list[tuple[int, int]]:
        matches = [match.span() for match in self._pattern.finditer(phrase)]
        if self._invert:
            return [] if matches else [(0, len(phrase))]
        return matches if self._all else matches[:1]


def regex(pattern: str, *, all_matches: bool = False, invert: bool = False) -> Regex:
    """What the regular expression `pattern` matches in a phrase: the first match, or every match.

    invert: the phrase is the found part when the pattern does NOT match it: find gives True, extract the phrase,
    remove '' for such phrases (a phrase that matches stays as it is).
    """
    return Regex(pattern, all_matches=all_matches, invert=invert)
