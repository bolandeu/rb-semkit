"""The link source dictionary: RuWordNet links two units of one synset, or of two synsets of a POS-synonymy pair.

A unit is found by its lemmas; a run of words also hyphenated or glued («веб сайт» → веб-сайт, вебсайт). A word of
several senses links through any of them. A link is one step: a link of a link is no link. The derivation pairs of
the file are never read: they join too much (купить ~ покупатель).
"""

from __future__ import annotations

import functools
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from ...word_vectors import thesaurus
from ...word_vectors.thesaurus import Lemmas, Thesaurus
from . import Links, SourceOption

SYNSET, POS_SYNONYMY = "synset", "pos_synonymy"  # the names of the two links in a reason


class Dictionary(Links):
    """The links of a thesaurus; the reason names each unit by the name of its sense."""

    def __init__(self, found: Thesaurus) -> None:
        self._thesaurus = found
        self.longest = found.longest
        self._meanings = functools.cache(self._meanings_of)

    def knows(self, run: Lemmas) -> bool:
        return bool(self._meanings(run))

    def link(self, unit: Lemmas, other: Lemmas) -> str | None:
        meanings, others = self._meanings(unit), self._meanings(other)
        for synset, name in meanings.items():
            if synset in others:
                return f"{name}~{others[synset]} ({SYNSET})"
        for synset, name in meanings.items():
            paired = self._thesaurus.pos_synonyms.get(synset, set())
            if (found := next((each for each in others if each in paired), None)) is not None:
                return f"{name}~{others[found]} ({POS_SYNONYMY})"
        return None

    def linked(self, unit: Lemmas) -> Iterable[Lemmas]:
        synsets = [
            each for synset in self._meanings(unit) for each in (synset, *self._thesaurus.pos_synonyms.get(synset, ()))
        ]
        senses = [sense for synset in synsets for sense in self._thesaurus.synsets[synset]]
        return {form for sense in senses for form in (sense.lemmas, _split(sense.lemmas))}

    def _meanings_of(self, unit: Lemmas) -> dict[str, str]:
        """The synsets of the senses of the unit, each with the name of its sense, in the order of the file."""
        found: dict[str, str] = {}
        for spelled in _spellings(unit):
            for synset in self._thesaurus.of_lemmas.get(spelled, ()):
                senses = self._thesaurus.synsets[synset]
                found.setdefault(synset, next(sense.name for sense in senses if sense.lemmas == spelled))
        return found


def _spellings(unit: Lemmas) -> list[Lemmas]:
    """The unit by its lemmas, and a run of words also hyphenated and glued."""
    return [unit] if len(unit) == 1 else [unit, ("-".join(unit),), ("".join(unit),)]


def _split(lemmas: Lemmas) -> Lemmas:
    """The lemmas of a sense with each hyphenated word split into its parts: as a phrase of separate words has it."""
    return tuple(part for lemma in lemmas for part in lemma.split("-"))


class DictionarySource:
    """RuWordNet, always on: it adds no option, and refuses when the thesaurus is not pulled."""

    options: tuple[SourceOption, ...] = ()

    def prepare(self, options: Mapping[str, Any], project: Path) -> Links:
        return Dictionary(thesaurus.open_thesaurus(project))


SOURCES = [DictionarySource()]
