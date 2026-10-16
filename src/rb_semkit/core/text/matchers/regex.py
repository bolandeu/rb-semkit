"""A regular expression: the first match or all of them; or the phrases that do NOT match."""

from __future__ import annotations

import pandas as pd

from ...frame import map_unique
from ..base import collapse, compiled
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

    def remove(self, phrases: pd.Series) -> pd.Series:
        if self._invert:
            return super().remove(phrases)
        return map_unique(phrases, lambda phrase: collapse(self._pattern.sub("", phrase)))


def regex(pattern: str, *, all_matches: bool = False, invert: bool = False) -> Regex:
    """What the regular expression `pattern` matches in a phrase, case-sensitive, searched anywhere.

    find: the pattern matches. remove: every match is cut out. extract: the first match, or with `all_matches=True`
    every match, joined by a space.
    invert: the phrase is the found part when the pattern does NOT match it: find gives True, extract the phrase,
    remove '' for such phrases (a phrase that matches stays as it is).

    VBA (RibbonCallbacks.vba):
        find: `—koa` (line 2089).
        remove: `aoka` (line 2363); invert: no VBA handler: derived from `aok·` (line 1820).
        extract: `–a—–` (line 2712), all_matches `–a——` (lines 2877–2878), joined by a space (the VBA asks for the
        separator); invert: no VBA handler: derived from `aok·` (line 1820).
    ADR 0005: no double spaces in the results.
    """
    return Regex(pattern, all_matches=all_matches, invert=invert)
