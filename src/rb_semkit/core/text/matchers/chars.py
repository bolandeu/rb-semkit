"""Characters by type: latin, cyrillic, digits, letters and digits, punctuation, upper-case or Ukrainian letters."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Literal, NamedTuple, get_args

import pandas as pd

from ...frame import map_unique
from ..base import Matcher, choice, collapse
from . import classes

__all__ = ["chars"]


class Kind(NamedTuple):
    """A class of characters and what the verbs do with it.

    `body` is a regex class body, `negated` takes every character outside it. remove leaves `gap` for each run of
    the class. extract keeps the class and the whitespace with nothing between («Wi-Fi» → «WiFi») when `glued`,
    else the runs of the class joined by a space. With `numbers_whole`, a point or a comma between two digits is
    part of the number, not of the class («2.5», «541,67»).
    """

    body: Callable[[], str]
    negated: bool = False
    gap: str = ""
    glued: bool = False
    numbers_whole: bool = False


CharKind = Literal["latin", "cyrillic", "digits", "letters_digits", "punctuation", "upper", "ua"]
KINDS: dict[CharKind, Kind] = {
    "latin": Kind(lambda: classes.LATIN, glued=True),
    "cyrillic": Kind(lambda: classes.CYRILLIC, glued=True),
    "digits": Kind(lambda: classes.DIGITS, glued=True),
    "letters_digits": Kind(lambda: classes.cased() + classes.DIGITS),
    "punctuation": Kind(lambda: classes.cased() + classes.DIGITS + r"\s", negated=True, gap=" ", numbers_whole=True),
    "upper": Kind(classes.upper),
    "ua": Kind(lambda: "іїєґІЇЄҐ"),
}


class Chars(Matcher):
    def __init__(self, kind: CharKind) -> None:
        self._kind = KINDS[choice("kind", kind, get_args(CharKind))]
        body = self._kind.body()
        inside, outside = (f"[^{body}]", f"[{body}]") if self._kind.negated else (f"[{body}]", f"[^{body}]")
        if self._kind.numbers_whole:
            inside, outside = f"(?:(?!{classes.NUMBER_MARK}){inside})", f"(?:{outside}|{classes.NUMBER_MARK})"
        self._inside = re.compile(f"{inside}+")
        self._outside = re.compile(rf"[^{body}\s]+" if self._kind.glued else f"{outside}+")

    def find(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, lambda phrase: self._inside.search(phrase) is not None).astype(bool)

    def remove(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, lambda phrase: collapse(self._inside.sub(self._kind.gap, phrase)))

    def extract(self, phrases: pd.Series) -> pd.Series:
        gap = "" if self._kind.glued else " "
        return map_unique(phrases, lambda phrase: collapse(self._outside.sub(gap, phrase)))


def chars(kind: CharKind) -> Chars:
    """The characters of one type.

    kind: "latin" (A-Z a-z), "cyrillic" (А..ӿ and Ё: not the capitals Є І Ї), "digits" (0-9), "letters_digits"
    (letters that have a case, and 0-9), "punctuation" (every other character but whitespace: also «-», «№» and
    letters without a case; a point or a comma between two digits is none, so «2.5» and «541,67» stay), "upper"
    (upper-case letters), "ua" (the Ukrainian letters і ї є ґ).

    remove cuts the characters out; a punctuation character leaves a space («Диван-кровать» → «Диван кровать»).
    extract keeps latin, cyrillic and digits with the whitespace between them («120x200» → «120200»); for the other
    kinds it gives the runs joined by a space.

    Example: {cli} read --text "диван 120x200" --text "кресло" find-chars digits write -
    -> диван 120x200, true; кресло, false
    Example: {cli} read --text "диван 120x200" remove-chars digits write -
    -> диван x
    Example: {cli} read --text "диван 120x200" extract-chars digits write -
    -> 120200
    Example: {cli} read --text "диван 120x200" --text "кресло" keep-chars digits write -
    -> диван 120x200
    Example: {cli} read --text "диван 120x200" --text "кресло" drop-chars digits write -
    -> кресло

    ADR 0005: whitespace of any kind counts as a space; no double spaces in the results; ua is the letters і ї є ґ,
    not the add-in's 31-item list, whose endings catch Russian words («кровати»).
    """
    return Chars(kind)
