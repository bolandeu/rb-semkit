"""Phrases from a list, found as whole words by an Aho-Corasick automaton, the longest from each word; the engine of
`markers` too."""

from __future__ import annotations

from collections.abc import Iterable
from typing import NamedTuple

import ahocorasick  # ty: ignore[unresolved-import]  # a compiled extension without type stubs
import pandas as pd

from ...errors import InvalidArguments
from ...frame import map_unique
from ..base import WordMatcher, collapse, split_words, word_key


class Hit(NamedTuple):
    """Words `start` up to `stop` of a phrase hold a listed phrase, as the list spells it."""

    start: int
    stop: int
    spelling: str


class PhraseList:
    """Phrases compared word by word as written (case and ё do not count, punctuation does: «москве,» is no «москве»).

    The automaton runs over words, not letters. The phrases that start with a word keep the list order.
    """

    def __init__(self, argument: str, items: Iterable[str]) -> None:
        listed = [items] if isinstance(items, str) else list(items)
        spellings: dict[str, str] = {}
        for item in listed:
            if isinstance(item, str) and item.split():
                spellings.setdefault(" ".join(word_key(word) for word in item.split()), collapse(item))
        if not spellings:
            raise InvalidArguments(f"{argument}={listed[:3]!r}; allowed: a non-empty list of phrases.")
        self._spellings = spellings
        self._starting: dict[str, list[str]] = {}
        self._automaton = ahocorasick.Automaton()
        for key in spellings:
            self._starting.setdefault(key.split(" ", 1)[0], []).append(key)
            self._automaton.add_word(f" {key} ", key)
        self._automaton.make_automaton()

    def hits(self, words: list[str]) -> list[Hit]:
        """Every listed phrase in the words, overlapping ones too."""
        text = f" {' '.join(word_key(word) for word in words)} "
        hits = []
        for end, key in self._automaton.iter(text):
            start = text.count(" ", 0, end - len(key) - 1)  # the spaces before the leading space of the match
            hits.append(Hit(start, start + key.count(" ") + 1, self._spellings[key]))
        return hits

    def starting_at(self, words: list[str], index: int) -> list[Hit]:
        """The listed phrases that stand at word `index`, in list order."""
        keys = [word_key(word) for word in words[index:]]
        return [
            Hit(index, index + len(key.split(" ")), self._spellings[key])
            for key in self._starting.get(keys[0], ())
            if keys[: key.count(" ") + 1] == key.split(" ")
        ]


def longest(hits: Iterable[Hit]) -> Hit:
    """The hit of the most words, then of the most characters; the first of equals (list order)."""
    return max(hits, key=lambda hit: (hit.stop - hit.start, len(hit.spelling)))


def choose(hits: Iterable[Hit]) -> list[Hit]:
    """For each word, the `longest` hit that starts there, left to right; the words of a chosen hit start no other."""
    starting: dict[int, list[Hit]] = {}
    for hit in hits:
        starting.setdefault(hit.start, []).append(hit)
    chosen: list[Hit] = []
    for start in sorted(starting):
        if not chosen or start >= chosen[-1].stop:
            chosen.append(longest(starting[start]))
    return chosen


class Phrases(WordMatcher):
    def __init__(self, items: Iterable[str]) -> None:
        self._list = PhraseList("items", items)

    def picks(self, words: list[str]) -> list[bool]:
        picked = [False] * len(words)
        for hit in choose(self._list.hits(words)):
            picked[hit.start : hit.stop] = [True] * (hit.stop - hit.start)
        return picked

    def extract(self, phrases: pd.Series) -> pd.Series:
        return map_unique(
            phrases, lambda phrase: ", ".join(hit.spelling for hit in choose(self._list.hits(split_words(phrase))))
        )


def phrases(items: Iterable[str]) -> Phrases:
    """Phrases of a list, found as whole words («угловой диван» is not in «угловойдиван» or «угловой диван,»).

    Words compare in any case, ё as е; punctuation glued to a word counts. find, remove and extract take the same
    phrases, as `sk.markers(user=...)` does: left to right, for each word the longest phrase that starts there (in
    words, then in characters; a tie keeps the list order), and the words of a taken phrase start no other. remove
    keeps the case of the other words; extract gives the phrases as the list spells them, joined by ', '.

    VBA (RibbonCallbacks.vba):
        find: `—k—k` (line 2218) with `–la` (lines 645–646).
        remove: `aok–` (line 2733) with `DeletePhrases` (lines 3452–3470).
        extract: `–a–a` (line 1736) with `la—` (lines 647–648).
    ADR 0005: ё = е; split on any whitespace; no double spaces; remove keeps the case (`DeletePhrases` lower-cases);
    extract joins by ', ', not "\\"; extract takes the longest phrase («нижний новгород»), `la—` the first in list
    order found anywhere in the phrase («нижний»), and gives a word inside a found phrase its own marker too.
    """
    return Phrases(items)
