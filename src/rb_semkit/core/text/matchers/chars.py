"""Characters by type: latin, cyrillic, digits, letters and digits, punctuation, upper-case or Ukrainian letters."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import NamedTuple

import pandas as pd

from ...frame import map_unique
from ..base import Matcher, choice, collapse
from . import classes


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

    VBA (RibbonCallbacks.vba):
        find: `—·k—` (line 1824) latin, `—·k–` (line 2088) cyrillic, `—·ka` (line 1652) digits, `—kko` (line 2874)
        letters_digits, `—·ok` (line 2756) upper; punctuation: no VBA handler: derived from `aok—` (line 2404).
        remove: `ak·—` (line 1856) latin, `ak–·` (line 1867) cyrillic, `aokk` (line 1924) digits, `aok—` (line 2404)
        punctuation; letters_digits, upper: no VBA handler: derived from `aok—` (line 2404).
        extract: `–ako` (line 2441) latin, `–—–a` (line 2350) cyrillic, `–·ko` (line 2594) digits, `aok—`
        (line 2404) letters_digits; punctuation, upper: no VBA handler: derived from `aok—` (line 2404).
        ua, every verb: no VBA handler: derived from `—·k·` (line 1786), the letters only (its `fua` test, line 1343,
        also looks for Ukrainian endings and words).
    ADR 0005: whitespace of any kind counts as a space; no double spaces in the results.
    """
    return Chars(kind)
