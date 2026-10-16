"""Words by case: lower, Capital, CAPS (find and extract)."""

from __future__ import annotations

from collections.abc import Callable

from ..base import Matcher, WordMatcher, choice, strip_edges


def _letters(word: str) -> str:
    return "".join(char for char in strip_edges(word) if char.isalpha())


def _is_lower(letters: str) -> bool:
    return bool(letters) and letters.islower()


def _is_capital(letters: str) -> bool:
    return bool(letters) and letters[0].isupper() and not any(char.isupper() for char in letters[1:])


def _is_caps(letters: str) -> bool:
    return len(letters) > 1 and letters.isupper()


CASES: dict[str, Callable[[str], bool]] = {"lower": _is_lower, "Capital": _is_capital, "CAPS": _is_caps}


class WordCase(WordMatcher):
    remove = Matcher.remove

    def __init__(self, kind: str) -> None:
        self._test = CASES[choice("kind", kind, tuple(CASES))]

    def picks(self, words: list[str]) -> list[bool]:
        return [self._test(_letters(word)) for word in words]


def word_case(kind: str) -> WordCase:
    """Words by the case of their letters (find and extract only).

    kind: "lower" (all letters lower: «x5»); "Capital" (the first letter upper, the rest not: «Москве», not «iPhone»);
    "CAPS" (two or more letters, all upper: «BMW»). Digits and punctuation do not count.
    """
    return WordCase(kind)
