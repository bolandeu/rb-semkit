"""The text before or after the first or the last occurrence of a pattern."""

from __future__ import annotations

import re

import pandas as pd

from ...errors import InvalidArguments
from ...frame import map_unique
from ..base import Matcher, collapse

__all__ = ["around"]

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
    """The part of the phrase before or after the first or the last occurrence of a text.

    Remove and extract only.

    pattern: the text as typed, found anywhere, also inside a word («в» is found in «диван»); not a regular expression.
    after: the part after the occurrence; by default the part before it.
    last: the last occurrence; by default the first.
    include: the occurrence itself belongs to the part.

    remove finds the first occurrence in any case and the last one in the case written; extract matches the case
    written; ё = е. A phrase without the text has no part: remove leaves it, extract gives an empty cell.

    Example: {cli} read --text "купить диван в москве" remove-around " в " --after write -
    -> купить диван в
    Example: {cli} read --text "купить диван в москве" extract-around " в " --after write -
    -> москве

    ADR 0005: ё = е; no double spaces in the results, none at the edges.
    """
    return Around(pattern, after=after, include=include, last=last)
