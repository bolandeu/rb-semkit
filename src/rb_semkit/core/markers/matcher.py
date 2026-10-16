"""The markers matcher: bundled lists by name and user lists, in one pass, spelled as the list spells them."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping

import pandas as pd

from ..errors import InvalidArguments
from ..frame import map_unique
from ..text.base import Matcher, bundled_list, choice, split_words, word_key
from ..text.matchers.phrases import Hit, PhraseList, choose
from .lists import bundled, names


def _longest(items: list[Hit]) -> Hit:
    return max(items, key=lambda hit: len(hit.spelling))  # the first of equals


def _first(items: list[Hit]) -> Hit:
    return items[0]


class Markers(Matcher):
    def __init__(self, found_in: tuple[PhraseList, ...], prepositions: frozenset[str], sep: str) -> None:
        self._lists = found_in
        self._prepositions = prepositions
        self._sep = sep

    def _pairs(self, words: list[str], pick: Callable[[list[Hit]], Hit]) -> list[Hit]:
        """Each toponym preposition with the list item that `pick` takes of those right after it (`udalit…`, `k—––`)."""
        pairs: list[Hit] = []
        for index, word in enumerate(words[:-1]):
            if (pairs and index < pairs[-1].stop) or word_key(word) not in self._prepositions:
                continue
            items = [hit for found_in in self._lists for hit in found_in.starting_at(words, index + 1)]
            if items:
                item = pick(items)
                pairs.append(Hit(index, item.stop, f"{word} {item.spelling}"))
        return pairs

    def _hits(self, words: list[str]) -> list[Hit]:
        if self._prepositions:
            return self._pairs(words, _longest)
        return choose(hit for found_in in self._lists for hit in found_in.hits(words))

    def _markers(self, words: list[str]) -> list[str]:
        if self._prepositions:
            return [pair.spelling for pair in self._pairs(words, _first)]
        found = [marker for found_in in self._lists for marker in found_in.markers(words)]
        return [spelling for _, spelling in sorted(found, key=lambda marker: marker[0])]  # stable: list order kept

    def find(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, lambda phrase: bool(self._hits(split_words(phrase)))).astype(bool)

    def remove(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, self._without)

    def extract(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, lambda phrase: self._sep.join(self._markers(split_words(phrase))))

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
    extract gives, for each word that starts a list item found in the phrase, the first such item in list order, as
    the list spells it («Москве»; «как», not «как сделать», when «как» comes first): in word order, joined by `sep`;
    a word inside a found item gives its own marker too («Нижний Новгород, Новгород»).
    remove cuts the longest item first, left to right, and keeps the case of the other words.
    with_prepositions: only the markers right after a toponym preposition («в», «во», «на», «по», «из», «до», «г»,
    «и»; as written, «в,» is none) count, and the preposition goes with them; a marker without one stays. remove cuts
    the pair with the longest item (in characters), extract gives «в Москве» with the first item in list order, find
    is True where such a pair stands.

    VBA (RibbonCallbacks.vba):
        find: `—k——` (line 2520) geo, `—k—6` (line 2047) mosmetro, `—k—7` (line 2048) districts, `—k—8` (line 2049)
        MO, `—k—9` (line 2050) citiesRu, `—k—o` (line 2040) questions, `—k—3` (line 2044) fun, `—k—4` (line 2045)
        DIY, `—k—01` (line 2052) edu, `—k—02` (line 2053) game, `—k—l` (line 2042) sale, `—k—00` (line 2041) rent,
        `—k—2` (line 2043) reviews, `—k—0` (line 2051) color, `—k—03` (line 2054) material, `—k—04` (line 2055)
        origin, `—k—5` (line 2046) cars, `—k—05` (line 2056) names, `RbnFind` (line 3172) several lists; each with
        `–la` (lines 645–646).
        remove: `a·–a` (line 2204) geo, `a·a6` (line 2030) and the other `a·a*` buttons, `RbnDelete` (line 3173)
        several lists; each with `DeletePhrases` (lines 3452–3470); geo with prepositions `a·—a` (line 2967) with
        `udalit_toponimy_s_pryedlogami` (lines 1194–1197), its one-item quirk fixed.
        extract: `–a·a` (line 2823) geo, `——aa4` (line 2014) and the other `——aa*` buttons, `–a—o` (line 2409)
        questions (its later steps, which cut word repeats and sale phrases and lower-case the result, are not
        taken), `RbnExtract` (line 3174) several lists; each with `la—` (lines 647–648); geo with prepositions `–·kk`
        (line 2674) with `k—––` (lines 1198–1199).
        user lists: no VBA handler: derived from `—k—k` (line 2218), `aok–` (line 2733) and `–a–a` (line 1736).
        prepositions on lists other than geo, and find with prepositions: no VBA handler: derived from
        `udalit_toponimy_s_pryedlogami` (lines 1194–1197).
    ADR 0005: ё = е; split on any whitespace; no double spaces; markers as the list spells them, joined by ', ';
    remove keeps the case (`DeletePhrases` lower-cases); with prepositions, a key of one list item cuts that whole
    item, not only the next word («отели в хересе де ла фронтере» → «отели», VBA: «отели де ла фронтере»).
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
