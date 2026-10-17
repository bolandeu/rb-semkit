"""Stopwords: the bundled list and a user list; remove only."""

from __future__ import annotations

from collections.abc import Iterable

from ...normalize import norm_phrase
from ..base import Matcher, WordMatcher, bundled_list, word_key, word_list

__all__ = ["stopwords"]


class Stopwords(WordMatcher):
    find = Matcher.find
    extract = Matcher.extract

    def __init__(self, extra: Iterable[str] | None) -> None:
        listed = bundled_list("stopwords") + (word_list("extra", extra) if extra is not None else [])
        self._keys = frozenset(norm_phrase(word) for word in listed)

    def picks(self, words: list[str]) -> list[bool]:
        return [word_key(word) in self._keys for word in words]


def stopwords(extra: Iterable[str] | None = None) -> Stopwords:
    """The function words with no search intent (prepositions, conjunctions, particles); remove only.

    A word is compared as written: «и,» with its comma is no stopword. Case and ё do not count.
    extra: your own words, taken together with the bundled list.

    ADR 0005: stopwords in any case; ё = е; split on any whitespace; no double spaces; the junk word «g» dropped.
    """
    return Stopwords(extra)
