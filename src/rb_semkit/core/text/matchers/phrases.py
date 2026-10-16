"""Phrases from a list, found as whole words by an Aho-Corasick automaton; the engine of `markers` too."""

from __future__ import annotations

from collections.abc import Iterable
from typing import NamedTuple

import ahocorasick  # ty: ignore[unresolved-import]  # a compiled extension without type stubs

from ...errors import InvalidArguments
from ..base import WordMatcher, collapse, word_key


class Hit(NamedTuple):
    """Words `start` up to `stop` of a phrase hold a listed phrase, as the list spells it."""

    start: int
    stop: int
    spelling: str


def _key(word: str) -> str:
    return word_key(word, ignore_punct=True) or word_key(word)


class PhraseList:
    """Phrases compared by case, ё and punctuation at the edges of words. The automaton runs over words, not letters."""

    def __init__(self, argument: str, items: Iterable[str]) -> None:
        listed = [items] if isinstance(items, str) else list(items)
        spellings: dict[str, str] = {}
        for item in listed:
            if isinstance(item, str) and item.split():
                spellings.setdefault(" ".join(_key(word) for word in item.split()), collapse(item))
        if not spellings:
            raise InvalidArguments(f"{argument}={listed[:3]!r}; allowed: a non-empty list of phrases.")
        self._spellings = spellings
        self._automaton = ahocorasick.Automaton()
        for key in spellings:
            self._automaton.add_word(f" {key} ", key)
        self._automaton.make_automaton()

    def hits(self, words: list[str]) -> list[Hit]:
        """Every listed phrase in the words, overlapping ones too."""
        text = f" {' '.join(_key(word) for word in words)} "
        found = []
        for end, key in self._automaton.iter(text):
            start = text.count(" ", 0, end - len(key) - 1)  # the spaces before the leading space of the match
            found.append(Hit(start, start + key.count(" ") + 1, self._spellings[key]))
        return found


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


def phrases(items: Iterable[str]) -> Phrases:
    """Phrases of a list, found as whole words («угловой диван» is not in «угловойдиван»), in any case, ё as е.

    Several at one place: the leftmost, then the longest. extract gives the found words as the phrase spells them.
    """
    return Phrases(items)
