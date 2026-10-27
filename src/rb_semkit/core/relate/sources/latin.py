"""The link source «latin»: a word in Latin letters and a word in Cyrillic letters that sound the same are linked.

A Latin word is read in Cyrillic by the table translit en→ru of the change area. Two words sound the same when the
reading of the Latin one equals the Cyrillic one after the same folding: lower case, ё as е, щ as ш (bosch reads
«бощ», and it equals «бош»). A word with digits, a word of other letters and a Cyrillic word have no reading. The
reading is also the other form of the Latin word, so the lookups of the other sources try it.
"""

from __future__ import annotations

import functools
import re
from collections import defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import pandas as pd

from ...change.chars import translit
from ...word_vectors.thesaurus import Lemmas
from . import Links, SourceOption

_LATIN = re.compile(r"[a-z]+")
_CYRILLIC = re.compile(r"[а-яё]+")
_FOLD = str.maketrans({"ё": "е", "щ": "ш"})


@functools.cache
def _reading(word: str) -> str | None:
    """The word in Cyrillic letters, or None when it is not a word of Latin letters only."""
    if not _LATIN.fullmatch(word):
        return None
    return str(translit(pd.Series([word]), to="ru").iloc[0])


def _sound(word: str) -> str | None:
    """What the word sounds like, as a Cyrillic word folded; None for a word with no sound of this source."""
    reading = _reading(word)
    if reading is None and _CYRILLIC.fullmatch(word):
        reading = word
    return None if reading is None else reading.translate(_FOLD)


def _single(unit: Lemmas, other: Lemmas) -> tuple[str, str] | None:
    """The Latin word and the Cyrillic word of two units of one word each, in this order, or None."""
    if len(unit) != 1 or len(other) != 1:
        return None
    for latin, cyrillic in (unit[0], other[0]), (other[0], unit[0]):
        if _reading(latin) is not None and _CYRILLIC.fullmatch(cyrillic):
            return latin, cyrillic
    return None


class _Latin(Links):
    """The links of the words by sound. It remembers the words of the table (`learn`), because the other script of a
    word is known only by them."""

    def __init__(self) -> None:
        self._by_sound: defaultdict[str, set[str]] = defaultdict(set)

    def learn(self, words: Iterable[str]) -> None:
        for word in words:
            if (sound := _sound(word)) is not None:
                self._by_sound[sound].add(word)

    def forms(self, word: str) -> Iterable[str]:
        reading = _reading(word)
        return [] if reading is None else [reading]

    def link(self, unit: Lemmas, other: Lemmas) -> str | None:
        found = _single(unit, other)
        if found is None or _sound(found[0]) != _sound(found[1]):
            return None
        return f"{found[0]}~{found[1]} (latin)"

    def linked(self, unit: Lemmas) -> Iterable[Lemmas]:
        if len(unit) != 1 or (sound := _sound(unit[0])) is None:
            return ()
        return [(word,) for word in self._by_sound[sound] if self.link(unit, (word,))]


class Latin:
    options: tuple[SourceOption, ...] = ()

    def prepare(self, options: Mapping[str, Any], project: Path) -> Links:
        return _Latin()


SOURCES = [Latin()]
