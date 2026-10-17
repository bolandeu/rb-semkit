"""The markers matcher: bundled lists by name and user lists, in one pass, spelled as the list spells them."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

import pandas as pd

from ..errors import InvalidArguments
from ..frame import map_unique
from ..text.base import Matcher, bundled_list, choice, split_words, word_key
from ..text.matchers.phrases import Hit, PhraseList, choose, longest
from .lists import bundled, names


class Markers(Matcher):
    def __init__(self, found_in: tuple[PhraseList, ...], prepositions: frozenset[str], sep: str) -> None:
        self._lists = found_in
        self._prepositions = prepositions
        self._sep = sep

    def _pairs(self, words: list[str]) -> list[Hit]:
        """Each toponym preposition with the longest list item right after it."""
        pairs: list[Hit] = []
        for index, word in enumerate(words[:-1]):
            if (pairs and index < pairs[-1].stop) or word_key(word) not in self._prepositions:
                continue
            items = [hit for found_in in self._lists for hit in found_in.starting_at(words, index + 1)]
            if items:
                item = longest(items)
                pairs.append(Hit(index, item.stop, f"{word} {item.spelling}"))
        return pairs

    def _hits(self, words: list[str]) -> list[Hit]:
        if self._prepositions:
            return self._pairs(words)
        return choose(hit for found_in in self._lists for hit in found_in.hits(words))

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
    A word glued to punctuation is not matched («москве,»).
    find, remove and extract take the same markers: left to right, for each word the longest item that starts there
    (in words, then in characters; a tie keeps the list order: the lists in the given order, user lists last), and
    the words of a taken item start no other («Нижний Новгород», not «Нижний Новгород, Новгород»).
    extract gives them as the list spells them («Москве»; «как сделать», not «как»), in word order, joined by `sep`.
    remove keeps the case of the other words.
    with_prepositions: only the markers right after a toponym preposition («в», «во», «на», «по», «из», «до», «г»,
    «и»; as written, «в,» is none) count, and the preposition goes with them; a marker without one stays. A
    preposition takes the longest item right after it, as above. remove cuts the pair, extract gives it («в Москве»),
    find is True where such a pair stands.

    ADR 0005: ё = е; split on any whitespace; no double spaces; markers as the list spells them, joined by ', ';
    remove keeps the case of the phrase; with prepositions, the preposition and one list item go as a whole, not only
    the next word («отели в хересе де ла фронтере» → «отели»); extract takes the longest item from a word («как
    сделать», not «как») and only items that start at a word, so a word inside a found item gives no marker of its
    own («Нижний Новгород», not «Новгород» too).
    """
    wanted = [lists] if isinstance(lists, str) else list(lists)
    chosen = [bundled(choice("lists", name, names())) for name in wanted]
    chosen += [PhraseList(f"user[{name!r}]", items) for name, items in (user or {}).items()]
    if not chosen:
        raise InvalidArguments(f"lists: none given; allowed: {', '.join(repr(name) for name in names())}, or user=.")
    prepositions = frozenset()
    if with_prepositions:
        prepositions = frozenset(word_key(word) for word in bundled_list("toponym_prepositions_ru"))
    return Markers(tuple(chosen), prepositions, sep)
