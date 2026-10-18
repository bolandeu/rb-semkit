"""A regular expression: the first match or all of them; or, inverted, the text the pattern does NOT match."""

from __future__ import annotations

import pandas as pd

from ...frame import map_unique
from ..base import Matcher, collapse, compiled

__all__ = ["regex"]


class Regex(Matcher):
    def __init__(self, pattern: str, *, all_matches: bool, invert: bool) -> None:
        self._pattern = compiled("pattern", pattern)
        self._all = all_matches
        self._invert = invert

    def _matches(self, phrase: str) -> list[str]:
        return [match.group() for match in self._pattern.finditer(phrase)]

    def _outside(self, phrase: str) -> str:
        """The text outside every match."""
        return collapse(self._pattern.sub("", phrase))

    def _found(self, phrase: str) -> str:
        if self._invert:
            return self._outside(phrase)
        matches = self._matches(phrase)
        return collapse(" ".join(matches if self._all else matches[:1]))

    def find(self, phrases: pd.Series) -> pd.Series:
        if self._invert:
            return map_unique(phrases, lambda phrase: self._outside(phrase) != "").astype(bool)
        return map_unique(phrases, lambda phrase: self._pattern.search(phrase) is not None).astype(bool)

    def remove(self, phrases: pd.Series) -> pd.Series:
        if self._invert:
            return map_unique(phrases, lambda phrase: collapse("".join(self._matches(phrase))))
        return map_unique(phrases, self._outside)

    def extract(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, self._found)


def regex(pattern: str, *, all_matches: bool = False, invert: bool = False) -> Regex:
    """What a regular expression matches in a phrase, case-sensitive, searched anywhere.

    pattern: the regular expression; \\w, \\b and \\d take Cyrillic letters too.
    all_matches: extract gives every match, joined by a space; by default the first.
    invert: the found part is the text the pattern does not match: remove keeps only the matches, joined with nothing
    between («диван 120x200» with \\d+ → «120200»); extract gives the text outside the matches («диван x»); find marks
    the phrases where such text is left.

    find marks the phrases where the pattern matches; remove cuts out every match; extract gives the first match.

    Example: {cli} read --text "диван 120x200" --text "кресло" find-regex "\\d+" write -
    -> диван 120x200, true; кресло, false
    Example: {cli} read --text "диван 120x200" remove-regex "\\d+x\\d+" write -
    -> диван
    Example: {cli} read --text "диван 120x200" extract-regex "\\d+x\\d+" write -
    -> 120x200
    Example: {cli} read --text "диван 120x200" --text "кресло" keep-regex "\\d+" write -
    -> диван 120x200
    Example: {cli} read --text "диван 120x200" --text "кресло" drop-regex "\\d+" write -
    -> кресло

    ADR 0005: \\w, \\b and \\d understand Cyrillic (Unicode); no double spaces in the results.
    """
    return Regex(pattern, all_matches=all_matches, invert=invert)
