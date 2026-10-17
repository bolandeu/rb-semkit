"""The thesaurus RuWordNet: the SQLite file of python-ruwordnet, read once into memory.

A sense is a word in a synset (a set of words of one meaning); the synonyms of a word are the other words of the
synsets it has. Words are keys as `norm_phrase` folds them (lower case, ё = е); a phrase of several words is left out.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from pathlib import Path

from ..normalize import norm_phrase
from ..vectors import cache, registry

NAME = "ruwordnet"


class Thesaurus:
    def __init__(self, senses: list[tuple[str, str]]) -> None:
        """senses: the synset and the lemma of each sense, in the order of the file."""
        self.synsets: dict[str, list[str]] = defaultdict(list)
        self.of_word: dict[str, list[str]] = defaultdict(list)
        for synset, lemma in senses:
            word = norm_phrase(lemma)
            if " " not in word:
                self.synsets[synset].append(word)
                self.of_word[word].append(synset)

    def synonyms(self, word: str) -> list[str]:
        """The other words of the synsets of `word`, each once, in the order of the file."""
        found = {other: None for synset in self.of_word.get(word, ()) for other in self.synsets[synset]}
        return [other for other in found if other != word]


def load(path: Path) -> Thesaurus:
    """The thesaurus in the SQLite file `path`."""
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as connection:
        return Thesaurus(connection.execute("SELECT synset_id, lemma FROM sense ORDER BY synset_id, id").fetchall())


def open_thesaurus(start: Path) -> Thesaurus:
    """RuWordNet as pulled into the cache of the project at or above `start` (ModelNotPulled, with the command that
    pulls it)."""
    pulled = cache.pulled_model(registry.model(NAME), start)
    return load(pulled.folder / next(iter(pulled.model.files)))
