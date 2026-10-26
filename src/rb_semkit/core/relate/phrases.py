"""A phrase of relate-phrases as its units, and the links between units that the sources give.

A word is its lemma (case and ё folded); a preposition, a conjunction or a particle is dropped, except the question
words and the words to keep; a word with digits stays as it is. The units are the cut of the words into runs that a
source knows, as `synonym-candidates` cuts them; every other word is a unit by itself. When two such runs overlap,
the phrase keeps every cut, and a comparison takes the one that explains the most words.
"""

from __future__ import annotations

import functools
import itertools
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from ..morph import Lemmatizer
from ..normalize import norm_phrase
from ..text.base import split_words
from ..word_vectors.thesaurus import Lemmas
from ..word_vectors.units import Token, Unit, cuts
from .sources import Links

DROPPED = frozenset({"prep", "conj", "prt"})  # the parts of speech of the lemmatizer that a phrase drops


@dataclass(frozen=True)
class Phrase:
    """A row of the table: its place (`row`; -1 for the phrase of --to), its cell and its cuts into units, the cut of
    `synonym-candidates` first."""

    row: int
    text: str
    cuts: tuple[tuple[Unit, ...], ...]

    @property
    def units(self) -> tuple[Unit, ...]:
        """The units of its first cut."""
        return self.cuts[0]

    @functools.cached_property
    def lemmas(self) -> Lemmas:
        """The lemmas of its units in any order: a phrase of the same lemmas is the same phrase."""
        return tuple(sorted(lemma for unit in self.units for lemma in unit.lemmas))

    @functools.cached_property
    def keys(self) -> frozenset[Lemmas]:
        """The units of all its cuts."""
        return frozenset(unit.lemmas for cut in self.cuts for unit in cut)

    def within(self, reach: frozenset[Lemmas]) -> bool:
        """Whether every unit of one of its cuts is in `reach`."""
        return any(all(unit.lemmas in reach for unit in cut) for cut in self.cuts)

    def before(self, other: Phrase) -> bool:
        """Whether a relation of `other` may point to it: fewer units, or as many and an earlier row."""
        return (len(self.units), self.row) < (len(other.units), other.row)


class Reader:
    """Reads the phrases into units and asks the sources for the links of the units; each lookup is done once."""

    def __init__(self, links: Sequence[Links], keep: Iterable[str], lemmatizer: Lemmatizer) -> None:
        self._links = links
        self._keep = frozenset(map(norm_phrase, keep))
        self._lemmatizer = lemmatizer
        self._longest = max((source.longest for source in links), default=1)
        self._token = functools.cache(self._token_of)
        self._forms = functools.cache(self._forms_of)
        self.link = functools.cache(self._link)
        self.linked = functools.cache(self._linked)

    def learn(self, texts: Iterable[str]) -> None:
        """Gives every source the lemmas of all the words of the table, before the first lookup."""
        words = {self._token(word).lemma for text in texts for word in map(norm_phrase, split_words(text)) if word}
        for source in self._links:
            source.learn(words)

    def phrase(self, row: int, text: str) -> Phrase:
        words = [self._token(word) for word in map(norm_phrase, split_words(text)) if word]
        runs = frozenset(
            run
            for size in range(2, self._longest + 1)
            for start in range(len(words) - size + 1)
            if self._known(run := tuple(token.lemma for token in words[start : start + size]))
        )
        return Phrase(row, text, tuple(map(tuple, cuts(words, runs, self._longest))))

    def _token_of(self, word: str) -> Token:
        if any(char.isdigit() for char in word):
            return Token(word, word, True)
        lemma = norm_phrase(self._lemmatizer.lemma(word))
        kept = word in self._keep or lemma in self._keep
        return Token(word, lemma, kept or self._lemmatizer.pos(word) not in DROPPED)

    def _known(self, run: Lemmas) -> bool:
        return any(source.knows(form) for form in self._forms(run) for source in self._links)

    def _forms_of(self, unit: Lemmas) -> tuple[Lemmas, ...]:
        """The unit and its other forms: each word in its forms that the sources give."""
        words = [[word, *(form for source in self._links for form in source.forms(word))] for word in unit]
        return tuple(itertools.product(*words))

    def _link(self, unit: Lemmas, other: Lemmas) -> str | None:
        """The reason of the first source that links the two units, in any of their forms."""
        pairs = itertools.product(self._forms(unit), self._forms(other))
        return next(
            (reason for first, second in pairs for source in self._links if (reason := source.link(first, second))),
            None,
        )

    def _linked(self, unit: Lemmas) -> frozenset[Lemmas]:
        """The unit and the units linked to it, in any of its forms."""
        return frozenset({unit}).union(*(source.linked(form) for form in self._forms(unit) for source in self._links))
