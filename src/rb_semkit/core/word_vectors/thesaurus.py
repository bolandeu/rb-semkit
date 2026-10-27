"""The thesaurus RuWordNet: the SQLite file of python-ruwordnet, read once into memory.

A sense is a word or a phrase in a synset (a set of senses of one meaning); the synonyms of a sense are the other
senses of the synsets it has. A POS-synonymy pair links two synsets of one meaning in different parts of speech
(создание ~ создать). A sense is found by its lemmas, as the column `lemma` holds them (lower case, ё = е);
it shows as its name in lower case. The words of the lemmas are lemmatized again, as the words of the core are, as
the column and the lemmatizer may differ (оформить, оформлять).
"""

from __future__ import annotations

import functools
import sqlite3
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple

from ..morph import Lemmatizer
from ..morph.functions import BUNDLED
from ..normalize import norm_phrase
from ..vectors import cache, registry

NAME = "ruwordnet"
Lemmas = tuple[str, ...]


class Sense(NamedTuple):
    name: str
    lemmas: Lemmas


class Thesaurus:
    def __init__(
        self,
        senses: list[tuple[str, str, str]],
        lemmatizer: Lemmatizer = BUNDLED,
        pos_synonyms: Iterable[tuple[str, str]] = (),
    ) -> None:
        """senses: the synset, the name and the lemma of each sense, in the order of the file.
        pos_synonyms: the POS-synonymy pairs of synsets, in either direction."""
        lemma_of = functools.cache(lambda word: norm_phrase(lemmatizer.lemma(word)))
        self.synsets: dict[str, list[Sense]] = defaultdict(list)
        self.of_lemmas: dict[Lemmas, list[str]] = defaultdict(list)
        for synset, name, lemma in senses:
            lemmas = tuple(lemma_of(word) for word in norm_phrase(lemma).split())
            self.synsets[synset].append(Sense(name.lower(), lemmas))
            self.of_lemmas[lemmas].append(synset)
        self.phrases = frozenset(lemmas for lemmas in self.of_lemmas if len(lemmas) > 1)
        self.longest = max(map(len, self.phrases), default=1)
        self.pos_synonyms: dict[str, set[str]] = defaultdict(set)
        for left, right in pos_synonyms:
            self.pos_synonyms[left].add(right)
            self.pos_synonyms[right].add(left)

    def synonyms(self, lemmas: Lemmas) -> list[Sense]:
        """The other senses of the synsets of `lemmas`, one for each name, in the order of the file."""
        found = {
            norm_phrase(sense.name): sense
            for synset in self.of_lemmas.get(lemmas, ())
            for sense in self.synsets[synset]
            if sense.lemmas != lemmas
        }
        return list(found.values())


def load(path: Path) -> Thesaurus:
    """The thesaurus in the SQLite file `path`."""
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as connection:
        return Thesaurus(
            connection.execute("SELECT synset_id, name, lemma FROM sense ORDER BY synset_id, id").fetchall(),
            pos_synonyms=connection.execute("SELECT left_id, right_id FROM pos_synonymy_relation").fetchall(),
        )


def open_thesaurus(start: Path) -> Thesaurus:
    """RuWordNet as pulled into the cache of the project at or above `start` (ModelNotPulled, with the command that
    pulls it)."""
    pulled = cache.pulled_model(registry.model(NAME), start)
    return load(pulled.folder / next(iter(pulled.model.files)))
