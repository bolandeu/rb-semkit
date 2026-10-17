"""Words by case: lower, Capital, CAPS (find and extract)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal, get_args

from ..base import Matcher, WordMatcher, choice
from . import classes

__all__ = ["word_case"]

# The word as it is written, punctuation included; a word with no cased letter has no case («2024», «—»).
Case = Literal["lower", "Capital", "CAPS"]
CASES: dict[Case, Callable[[str], bool]] = {
    "lower": lambda word: word == word.lower(),
    "Capital": lambda word: word == word.title(),  # Excel PROPER: a capital after every non-letter («Из-За»)
    "CAPS": lambda word: word == word.upper(),
}


class WordCase(WordMatcher):
    remove = Matcher.remove

    def __init__(self, kind: Case) -> None:
        self._test = CASES[choice("kind", kind, get_args(Case))]

    def picks(self, words: list[str]) -> list[bool]:
        return [classes.has_cased(word) and self._test(word) for word in words]


def word_case(kind: Case) -> WordCase:
    """Words by the case of their letters (find and extract only); digits and punctuation do not count.

    kind: "lower" (no capital letter: «x5»); "Capital" (each run of letters starts with a capital, the rest small:
    «Москве», not «iPhone» or «Из-за»); "CAPS" (no small letter: «BMW», «В»).

    ADR 0005: split on any whitespace.
    """
    return WordCase(kind)
