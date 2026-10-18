"""The looked-up units of a phrase: a segmentation of it into runs of words that do not overlap.

A run is a sense of several words of the thesaurus (found by lemmas); a word in no such sense is a unit by itself. A
stopword is no unit by itself, and stays inside a run when the sense holds it.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import NamedTuple

from ..analysis.frequency import bundled_stopwords
from ..normalize import norm_phrase
from ..text.base import split_words
from .thesaurus import Lemmas


class Token(NamedTuple):
    word: str  # as the phrase has it, in lower case
    lemma: str
    counts: bool  # whether the word can be a unit by itself: no stopword, no digit


class Unit(NamedTuple):
    text: str
    lemmas: Lemmas


def tokens(phrase: str, lemma_of: Callable[[str], str]) -> list[Token]:
    """The words of `phrase`, each with its lemma."""
    words = [word for word in map(norm_phrase, split_words(phrase)) if word]
    return [
        Token(word, lemma_of(word), word not in bundled_stopwords() and not any(char.isdigit() for char in word))
        for word in words
    ]


def segment(words: list[Token], phrases: frozenset[Lemmas], longest: int) -> list[Unit]:
    """The units of a phrase: of all the segmentations, the one with the most words inside the `phrases` (senses of
    several words) wins, then the one with fewer units, then the first from the left."""
    best: list[tuple[int, int, list[Unit]]] = [(0, 0, [])] * (len(words) + 1)
    for start in range(len(words) - 1, -1, -1):
        options = []
        for stop in range(min(len(words), start + longest), start + 1, -1):
            run = words[start:stop]
            if tuple(token.lemma for token in run) in phrases:
                covered, units, rest = best[stop]
                unit = Unit(" ".join(token.word for token in run), tuple(token.lemma for token in run))
                options.append((covered + len(run), units + 1, [unit, *rest]))
        covered, units, rest = best[start + 1]
        token = words[start]
        alone = [Unit(token.word, (token.lemma,))] if token.counts else []
        options.append((covered, units + len(alone), [*alone, *rest]))
        best[start] = max(options, key=lambda option: (option[0], -option[1]))
    return best[0][2]
