"""Cells as units: by content, by occurrence among the cells, or empty. `remove` drops the rows, it does not edit them."""

from __future__ import annotations

from collections.abc import Callable, Iterable

import pandas as pd

from ...errors import InvalidArguments
from ...frame import map_unique
from ...normalize import norm_phrase
from ..base import Matcher, bundled_list, choice, compiled, split_words, word_key

CONTENT = ("contains", "starts", "ends")
KINDS = (*CONTENT, "regex", "empty", "unique", "repeated", "first", "last")


def _text_test(kind: str, items: tuple[str, ...]) -> Callable[[str], bool]:
    if kind == "starts":
        return lambda phrase: norm_phrase(phrase).startswith(items)
    if kind == "ends":
        return lambda phrase: norm_phrase(phrase).endswith(items)
    return lambda phrase: any(item in norm_phrase(phrase) for item in items)


def _word_test(kind: str, words: frozenset[str]) -> Callable[[str], bool]:
    def test(phrase: str) -> bool:
        keys = [word_key(word, ignore_punct=True) for word in split_words(phrase)]
        if not keys:
            return False
        if kind == "starts":
            return keys[0] in words
        if kind == "ends":
            return keys[-1] in words
        return any(key in words for key in keys)

    return test


def _item_keys(items: str | Iterable[str]) -> tuple[str, ...]:
    listed = [items] if isinstance(items, str) else list(items)
    if not listed or not all(isinstance(item, str) and item.strip() for item in listed):
        raise InvalidArguments(f"items={listed!r}; allowed: a non-empty list of non-empty strings.")
    return tuple(norm_phrase(item) for item in listed)


def _content_test(kind: str, items: str | Iterable[str] | None, prepositions: bool) -> Callable[[str], object]:
    if prepositions == (items is not None):
        raise InvalidArguments(
            f"items: {'both given' if prepositions else 'not given'} for kind={kind!r}; "
            "allowed: a non-empty list of strings, or prepositions=True, not both."
        )
    if items is None:
        return _word_test(kind, frozenset(word_key(word) for word in bundled_list("prepositions")))
    return _text_test(kind, _item_keys(items))


def _pattern_test(pattern: str | None) -> Callable[[str], object]:
    if pattern is None:
        raise InvalidArguments("pattern: not given for kind='regex'; allowed: a regular expression.")
    return compiled("pattern", pattern).search


class Cells(Matcher):
    def __init__(self, kind: str, items: str | Iterable[str] | None, pattern: str | None, prepositions: bool) -> None:
        self._kind = choice("kind", kind, KINDS)
        self._content: Callable[[str], object] | None = None
        if kind in CONTENT:
            self._content = _content_test(kind, items, prepositions)
        elif kind == "regex":
            self._content = _pattern_test(pattern)

    def find(self, phrases: pd.Series) -> pd.Series:
        blank = phrases.str.strip() == ""
        if self._kind == "empty":
            return blank
        if (content := self._content) is not None:
            return map_unique(phrases, lambda phrase: bool(content(phrase))).astype(bool)
        return self._occurrence(phrases, blank)

    def _occurrence(self, phrases: pd.Series, blank: pd.Series) -> pd.Series:
        """Empty cells are never repeats of each other: each is the only one, the first and the last of its kind."""
        shared = phrases.duplicated(keep=False) & ~blank
        if self._kind == "repeated":
            return shared
        if self._kind == "unique":
            return ~shared
        return ~(phrases.duplicated(keep="first" if self._kind == "first" else "last") & ~blank)

    def remove(self, phrases: pd.Series) -> pd.Series:
        return phrases[~self.find(phrases)]

    def extract(self, phrases: pd.Series) -> pd.Series:
        return phrases.where(self.find(phrases), "")


def cells(
    kind: str,
    *,
    items: str | Iterable[str] | None = None,
    pattern: str | None = None,
    prepositions: bool = False,
) -> Cells:
    """A whole cell is found or not. remove drops the rows that are found; extract keeps the cell, or '' if not found.

    kind: "contains", "starts", "ends" (with `items`: text parts, case and ё do not count; or with
    `prepositions=True`: the bundled prepositions, as whole words); "regex" (with `pattern`); "empty" (blank);
    by occurrence among the cells: "unique" (once), "repeated" (more than once), "first", "last" occurrence.
    Empty cells are never repeats of each other.
    """
    return Cells(kind, items, pattern, prepositions)
