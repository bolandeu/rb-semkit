"""Characters by type: latin, cyrillic, digits, letters and digits, punctuation, upper-case or Ukrainian letters."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import NamedTuple

import pandas as pd

from ...frame import map_unique
from ..base import Matcher, choice, collapse
from . import classes

__all__ = ["chars"]


class Kind(NamedTuple):
    """A class of characters and what the verbs do with it.

    `body` is a regex class body, `negated` takes every character outside it. remove leaves `gap` for each run of
    the class. extract keeps the class and the whitespace with nothing between («Wi-Fi» → «WiFi») when `glued`,
    else the runs of the class joined by a space.
    """

    body: Callable[[], str]
    negated: bool = False
    gap: str = ""
    glued: bool = False


KINDS = {
    "latin": Kind(lambda: classes.LATIN, glued=True),
    "cyrillic": Kind(lambda: classes.CYRILLIC, glued=True),
    "digits": Kind(lambda: classes.DIGITS, glued=True),
    "letters_digits": Kind(lambda: classes.cased() + classes.DIGITS),
    "punctuation": Kind(lambda: classes.cased() + classes.DIGITS + r"\s", negated=True, gap=" "),
    "upper": Kind(classes.upper),
    "ua": Kind(lambda: "іїєґІЇЄҐ"),
}


class Chars(Matcher):
    def __init__(self, kind: str) -> None:
        self._kind = KINDS[choice("kind", kind, tuple(KINDS))]
        body = self._kind.body()
        inside, outside = (f"[^{body}]", f"[{body}]") if self._kind.negated else (f"[{body}]", f"[^{body}]")
        self._inside = re.compile(f"{inside}+")
        self._outside = re.compile(rf"[^{body}\s]+" if self._kind.glued else f"{outside}+")

    def find(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, lambda phrase: self._inside.search(phrase) is not None).astype(bool)

    def remove(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, lambda phrase: collapse(self._inside.sub(self._kind.gap, phrase)))

    def extract(self, phrases: pd.Series) -> pd.Series:
        gap = "" if self._kind.glued else " "
        return map_unique(phrases, lambda phrase: collapse(self._outside.sub(gap, phrase)))


def chars(kind: str) -> Chars:
    """The characters of one type.

    kind: "latin" (A-Z a-z), "cyrillic" (А..ӿ and Ё: not the capitals Є І Ї), "digits" (0-9), "letters_digits"
    (letters that have a case, and 0-9), "punctuation" (every other character but whitespace: also «-», «№» and
    letters without a case), "upper" (upper-case letters), "ua" (the Ukrainian letters і ї є ґ).
    remove cuts the characters out; a punctuation character leaves a space («Диван-кровать» → «Диван кровать»).
    extract keeps latin, cyrillic and digits with the whitespace between them («120x200» → «120200»); for the other
    kinds it gives the runs joined by a space.

    ADR 0005: whitespace of any kind counts as a space; no double spaces in the results; ua is the letters і ї є ґ,
    not the add-in's 31-item list, whose endings catch Russian words («кровати»).
    """
    return Chars(kind)
