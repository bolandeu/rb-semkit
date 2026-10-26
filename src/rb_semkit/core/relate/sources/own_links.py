"""The link source «synonyms»: the groups of synonyms of the caller, given per run in `--synonyms FILE`.

The items of one group are linked to each other, and to no item of another group. An item of several words is a run of
words, one unit of a phrase.
"""

from __future__ import annotations

import itertools
from collections import defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import pandas as pd

from ...errors import InvalidArguments
from ...morph.functions import BUNDLED
from ...normalize import norm_phrase
from ...text.base import split_words
from ...word_vectors.thesaurus import Lemmas
from . import Links, SourceOption

OPTION = "synonyms"
ITEM_SEPARATOR = "|"
DOC = (
    "synonyms: a file of the groups of synonyms of the topic, read like `read` does; the items of a group are linked to"
    " each other (no chain across groups) and are compared by lemmas. Two shapes: a column synonyms, one group per row,"
    " the items split by | and an item may be several words (стиральная машина | стиралка | стиральная машинка); or the"
    " columns word and synonyms of `dupes --synonyms`, a word and its synonyms split by spaces. A group of one item is"
    " ignored. Example: --synonyms groups.csv, a file with the column synonyms and the row ремонт | починка | починить."
)


class OwnLinks(Links):
    """The links of the groups: two units are linked when a group holds both."""

    def __init__(self, groups: Iterable[Iterable[Lemmas]]) -> None:
        self._of: dict[Lemmas, list[frozenset[Lemmas]]] = defaultdict(list)
        for group in map(frozenset, groups):
            for item in group if len(group) > 1 else ():
                self._of[item].append(group)
        self.longest = max((len(item) for item in self._of), default=1)

    def knows(self, run: Lemmas) -> bool:
        return len(run) > 1 and run in self._of

    def link(self, unit: Lemmas, other: Lemmas) -> str | None:
        if unit == other or not any(other in group for group in self._of.get(unit, ())):
            return None
        first, second = sorted([unit, other])
        return f"{' '.join(first)}~{' '.join(second)} (synonyms)"

    def linked(self, unit: Lemmas) -> Iterable[Lemmas]:
        return set(itertools.chain.from_iterable(self._of.get(unit, ()))) - {unit}


def _lemmas(item: str) -> Lemmas:
    return tuple(norm_phrase(BUNDLED.lemma(word)) for word in split_words(norm_phrase(item)))


def groups_of(table: pd.DataFrame) -> list[list[Lemmas]]:
    """The groups of a table of one of the two shapes; each is a list of the items as lemmas."""
    if OPTION not in table.columns:
        raise InvalidArguments(
            f"--{OPTION}: no column {OPTION!r}; allowed: a table with the column {OPTION!r} (the items of a group split"
            f" by {ITEM_SEPARATOR}) or with the columns 'word' and {OPTION!r}."
        )
    cells = table[OPTION].fillna("").astype(str)
    if "word" in table.columns:
        words = table["word"].fillna("").astype(str)
        rows = [[word, *listed.split()] for word, listed in zip(words, cells, strict=True)]
    else:
        rows = [cell.split(ITEM_SEPARATOR) for cell in cells]
    return [[item for text in row if (item := _lemmas(text))] for row in rows]


class Synonyms:
    """The source: the option --synonyms."""

    options = (SourceOption(OPTION, str | None, DOC),)

    def prepare(self, options: Mapping[str, Any], project: Path) -> Links | None:
        path = options.get(OPTION)
        if path is None:
            return None
        from ....steps import table_of  # the file is read as the steps read their tables

        return OwnLinks(groups_of(table_of(path, OPTION)))


SOURCES = [Synonyms()]
