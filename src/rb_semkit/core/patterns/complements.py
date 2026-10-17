"""Prepositional complements: a preposition and the words up to its noun («в москве», «для детей»); extract only.

`complement_end` is the rule where a complement ends; the word order of a phrase (fix_word_order) uses it too.
"""

from __future__ import annotations

import re
from collections.abc import Callable

import pandas as pd

from ..frame import map_unique
from ..morph.functions import BUNDLED
from ..morph.lemmatizer import NOUN, Lemmatizer
from ..normalize import norm_phrase
from ..text.base import Matcher, bundled_list, split_words, word_key

__all__ = ["complements"]

WINDOW = 5  # a complement holds the preposition and at most this many words after it
DECLINED = frozenset({NOUN, "a", "p"})  # a noun, an adjective, a participle
_LETTERS = re.compile(r"[^\W_]+")


def _parts(word: str) -> list[str]:
    """The parts of the word between punctuation, in lower case («диван-кровать,» → «диван», «кровать»)."""
    return [part.lower() for part in _LETTERS.findall(word)]


def _is_noun(word: str, lemmatizer: Lemmatizer) -> bool:
    return any(lemmatizer.pos(part) == NOUN for part in _parts(word))


def _is_oblique(word: str, lemmatizer: Lemmatizer) -> bool:
    """A noun, an adjective or a participle in an oblique case: not its lemma («дуба», «красного»)."""
    return any(
        lemmatizer.pos(part) in DECLINED and norm_phrase(lemmatizer.lemma(part)) != norm_phrase(part)
        for part in _parts(word)
    )


def complement_end(
    words: list[str], start: int, stops: Callable[[str], bool], lemmatizer: Lemmatizer = BUNDLED
) -> int | None:
    """The end of the complement of the preposition `words[start]`; None when no noun follows it.

    The complement goes up to the first noun among the next WINDOW words before a word that `stops` it, then on
    over the nouns and adjectives in an oblique case right after that noun, up to the last of those nouns: «из
    массива дуба», but «в москве» of «в москве недорого распродажа».
    """
    end = None
    for place in range(start + 1, min(start + 1 + WINDOW, len(words))):
        word = words[place]
        if stops(word) or (end is not None and not _is_oblique(word, lemmatizer)):
            break
        if _is_noun(word, lemmatizer):
            end = place + 1
    return end


class Complements(Matcher):
    def __init__(self) -> None:
        self._prepositions = frozenset(word_key(word) for word in bundled_list("complement_prepositions"))

    def _found(self, phrase: str) -> str:
        words = split_words(phrase)
        found = []
        start = 0
        while start < len(words):
            stop = start + 1
            if self._is_preposition(words[start]):
                stop = complement_end(words, start, self._is_preposition) or stop
                if stop > start + 1:
                    found.append(" ".join(words[start:stop]))
            start = stop
        return ", ".join(found)

    def _is_preposition(self, word: str) -> bool:
        return word_key(word) in self._prepositions

    def extract(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, self._found)


def complements() -> Complements:
    """Prepositional complements of a phrase, joined by ", "; extract only: «диван для детей с доставкой» →
    «для детей, с доставкой».

    A complement is a preposition of the bundled list complement_prepositions («для», «с», «в» and others; any case,
    ё as е) and the words after it up to the last noun among the next five words, before the next preposition. A preposition with no noun after it gives nothing.
    """
    return Complements()
