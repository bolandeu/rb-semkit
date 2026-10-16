"""Phrases from a list, found as whole words by an Aho-Corasick automaton; the engine of `markers` too."""

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

    def _found(self, words: list[str]) -> tuple[str, list[tuple[int, str]]]:
        text = f" {' '.join(word_key(word) for word in words)} "
        return text, list(self._automaton.iter(text))

    def hits(self, words: list[str]) -> list[Hit]:
        """Every listed phrase in the words, overlapping ones too."""
        text, found = self._found(words)
        hits = []
        for end, key in found:
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

    def markers(self, words: list[str]) -> list[tuple[int, str]]:
        """The add-in's markers of the words (`la—`): (word index, the phrase as the list spells it), repeats kept.

        For each word, the first phrase in list order that starts with it and stands anywhere in the words; so a
        word inside a found phrase gives its own marker too («Нижний Новгород», «Новгород»).
        """
        _, found = self._found(words)
        present = {key for _, key in found}
        markers = []
        for index, word in enumerate(words):
            key = next((key for key in self._starting.get(word_key(word), ()) if key in present), None)
            if key is not None:
                markers.append((index, self._spellings[key]))
        return markers


def choose(hits: Iterable[Hit]) -> list[Hit]:
    """From overlapping hits, the leftmost, and of those the longest; the others are dropped."""
    chosen: list[Hit] = []
    for hit in sorted(hits, key=lambda hit: (hit.start, hit.start - hit.stop)):
        if not chosen or hit.start >= chosen[-1].stop:
            chosen.append(hit)
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
            phrases, lambda phrase: ", ".join(spelling for _, spelling in self._list.markers(split_words(phrase)))
        )


def phrases(items: Iterable[str]) -> Phrases:
    """Phrases of a list, found as whole words («угловой диван» is not in «угловойдиван» or «угловой диван,»).

    Words compare in any case, ё as е; punctuation glued to a word counts. remove cuts the longest phrase first,
    left to right, and keeps the case of the other words. extract gives the markers as `sk.markers(user=...)` does:
    for each word that starts a found item, the first such item in list order, as the list spells it, joined by ', '.

    VBA (RibbonCallbacks.vba):
        find: `—k—k` (line 2218) with `–la` (lines 645–646).
        remove: `aok–` (line 2733) with `DeletePhrases` (lines 3452–3470).
        extract: `–a–a` (line 1736) with `la—` (lines 647–648).
    ADR 0005: ё = е; split on any whitespace; no double spaces; remove keeps the case (`DeletePhrases` lower-cases);
    extract joins by ', ', not "\\".
    """
    return Phrases(items)
