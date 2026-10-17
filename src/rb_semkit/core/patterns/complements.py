"""Prepositional complements: a preposition and the words up to its noun («в москве», «для детей»); extract only."""

from __future__ import annotations

import re

import pandas as pd

from ..frame import map_unique
from ..morph.functions import BUNDLED
from ..text.base import Matcher, bundled_list, split_words, word_key

__all__ = ["complements"]

WINDOW = 5  # a complement holds the preposition and at most this many words after it
_LETTERS = re.compile(r"[^\W_]+")


def _is_noun(word: str) -> bool:
    """A part of the word between punctuation is a noun («диван-кровать,»)."""
    return any(BUNDLED.pos(part.lower()) == "n" for part in _LETTERS.findall(word))


class Complements(Matcher):
    def __init__(self) -> None:
        self._prepositions = frozenset(word_key(word) for word in bundled_list("complement_prepositions"))

    def _found(self, phrase: str) -> str:
        words = split_words(phrase)
        found = []
        start = 0
        while start < len(words):
            stop = start + 1
            if word_key(words[start]) in self._prepositions:
                stop = self._noun_end(words, start) or stop
                if stop > start + 1:
                    found.append(" ".join(words[start:stop]))
            start = stop
        return ", ".join(found)

    def _noun_end(self, words: list[str], start: int) -> int | None:
        """The end of the last noun among the next WINDOW words before another preposition; None without one."""
        end = None
        for place in range(start + 1, min(start + 1 + WINDOW, len(words))):
            if word_key(words[place]) in self._prepositions:
                break
            if _is_noun(words[place]):
                end = place + 1
        return end

    def extract(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, self._found)


def complements() -> Complements:
    """Prepositional complements of a phrase, joined by ", "; extract only: «диван для детей с доставкой» →
    «для детей, с доставкой».

    A complement is a preposition («для», «с», «в», «из», «на», «к», «со», «о», «во», «у», «по», «под», «от», «после»,
    «за», «над»; any case, ё as е) and the words after it up to the last noun among the next five words, before the
    next preposition. A preposition with no noun after it gives nothing.
    """
    return Complements()
