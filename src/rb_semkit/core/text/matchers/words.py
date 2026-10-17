"""Whole words: one word or a list; all or any of them; anywhere, at the start or at the end of the phrase."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from ...normalize import norm_phrase
from ..base import WordMatcher, choice, word_key, word_list

if TYPE_CHECKING:
    from ...morph import Lemmatizer

__all__ = ["words"]

MODES = ("any", "all")
PLACES = ("anywhere", "start", "end")


class Words(WordMatcher):
    def __init__(
        self,
        items: str | Iterable[str],
        *,
        mode: str = "any",
        where: str = "anywhere",
        ignore_punct: bool = False,
        lemmatizer: Lemmatizer | None = None,
    ) -> None:
        listed = word_list("words", items)
        self._mode = choice("mode", mode, MODES)
        self._where = choice("where", where, PLACES)
        self._ignore_punct = ignore_punct
        self._lemmatizer = lemmatizer
        self._keys = frozenset(self._key(item) for item in listed)

    def _key(self, word: str) -> str:
        key = word_key(word, ignore_punct=self._ignore_punct)
        if self._lemmatizer is None or not key:
            return key
        return norm_phrase(self._lemmatizer.lemma(key))

    def _places(self, count: int) -> range:
        if self._where == "start":
            return range(min(count, 1))
        if self._where == "end":
            return range(max(count - 1, 0), count)
        return range(count)

    def picks(self, words: list[str]) -> list[bool]:
        places = self._places(len(words))
        keys = {index: self._key(words[index]) for index in places}
        if self._mode == "all" and not self._keys <= set(keys.values()):
            return [False] * len(words)
        return [index in keys and keys[index] in self._keys for index in range(len(words))]


def words(
    items: str | Iterable[str],
    *,
    mode: str = "any",
    where: str = "anywhere",
    ignore_punct: bool = False,
    lemmatizer: Lemmatizer | None = None,
) -> Words:
    """Whole words of a phrase equal to `items`, compared by case and ё (`norm_phrase`).

    mode: "any" — any of the words; "all" — only phrases holding every one of them.
    where: "anywhere", "start" (the first word only) or "end" (the last word only).
    ignore_punct: punctuation at the edges of a word does not count («диван,» is «диван»).
    lemmatizer: compare lemmas («диваны» is «диван»); None compares the words as they are.

    ADR 0005: ё = е; split on any whitespace; blank list items are refused.
    """
    return Words(items, mode=mode, where=where, ignore_punct=ignore_punct, lemmatizer=lemmatizer)
