"""The markers matcher: bundled lists by name and user lists, in one pass, spelled as the list spells them."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

import pandas as pd

from ..errors import InvalidArguments
from ..frame import map_unique
from ..text.base import Matcher, bundled_list, choice, split_words, word_key
from ..text.matchers.phrases import Hit, PhraseList, choose
from .lists import bundled, names


class Markers(Matcher):
    def __init__(self, found_in: tuple[PhraseList, ...], prepositions: frozenset[str], sep: str) -> None:
        self._lists = found_in
        self._prepositions = prepositions
        self._sep = sep

    def _hits(self, words: list[str]) -> list[Hit]:
        hits = choose(hit for found_in in self._lists for hit in found_in.hits(words))
        taken = 0  # words before this one belong to an earlier hit
        grown = []
        for hit in hits:
            before = hit.start - 1
            if before >= taken and word_key(words[before], ignore_punct=True) in self._prepositions:
                hit = Hit(before, hit.stop, f"{words[before]} {hit.spelling}")
            grown.append(hit)
            taken = hit.stop
        return grown

    def find(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, lambda phrase: bool(self._hits(split_words(phrase)))).astype(bool)

    def remove(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, self._without)

    def extract(self, phrases: pd.Series) -> pd.Series:
        return map_unique(
            phrases, lambda phrase: self._sep.join(hit.spelling for hit in self._hits(split_words(phrase)))
        )

    def _without(self, phrase: str) -> str:
        words = split_words(phrase)
        gone = {index for hit in self._hits(words) for index in range(hit.start, hit.stop)}
        return " ".join(word for index, word in enumerate(words) if index not in gone)


def markers(
    lists: str | Iterable[str] = (),
    *,
    user: Mapping[str, Iterable[str]] | None = None,
    with_prepositions: bool = False,
    sep: str = ", ",
) -> Markers:
    """Items of marker lists found in a phrase, as whole words, in any case, ё as е; all lists in one pass.

    lists: names of the bundled lists (geo, mosmetro, districts, MO, citiesRu, questions, fun, DIY, edu, game, sale,
    rent, reviews, color, material, origin, cars, names). user: your own lists, `{"name": ["phrase", …]}`.
    extract gives the markers as the list spells them («Москве»), in phrase order, joined by `sep`.
    with_prepositions: a toponym preposition («в», «на», «in»…) before a marker goes with it, in remove and extract.
    """
    wanted = [lists] if isinstance(lists, str) else list(lists)
    chosen = [bundled(choice("lists", name, names())) for name in wanted]
    chosen += [PhraseList(f"user[{name!r}]", items) for name, items in (user or {}).items()]
    if not chosen:
        raise InvalidArguments(f"lists: none given; allowed: {', '.join(repr(name) for name in names())}, or user=.")
    prepositions = frozenset()
    if with_prepositions:
        prepositions = frozenset(
            word_key(word)
            for name in ("toponym_prepositions_ru", "toponym_prepositions_en")
            for word in bundled_list(name)
        )
    return Markers(tuple(chosen), prepositions, sep)
