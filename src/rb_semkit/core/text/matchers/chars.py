"""Characters by type: runs of latin, cyrillic, digits, letters and digits, punctuation, upper-case or Ukrainian letters."""

from __future__ import annotations

import re

from ..base import choice
from .spans import SpanMatcher

PATTERNS = {
    "latin": "[A-Za-z]+",
    "cyrillic": "[Ѐ-ӿ]+",
    "digits": "[0-9]+",
    "letters_digits": r"[^\W_]+",
    "punctuation": r"(?:[^\w\s]|_)+",
    "upper": "[A-ZА-ЯЁІЇЄҐ]+",
    "ua": "[іїєґІЇЄҐ]+",
}


class Chars(SpanMatcher):
    def __init__(self, kind: str) -> None:
        self._pattern = re.compile(PATTERNS[choice("kind", kind, tuple(PATTERNS))])

    def spans(self, phrase: str) -> list[tuple[int, int]]:
        return [match.span() for match in self._pattern.finditer(phrase)]


def chars(kind: str) -> Chars:
    """The characters of one type; a run of them is one found part (extract joins the runs by a space).

    kind: "latin", "cyrillic", "digits", "letters_digits", "punctuation", "upper" (upper-case latin and cyrillic
    letters), "ua" (the Ukrainian letters і ї є ґ).
    """
    return Chars(kind)
