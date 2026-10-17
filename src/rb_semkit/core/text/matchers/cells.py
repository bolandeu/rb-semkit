"""Cells as units: by content, by occurrence among the cells, or empty. `remove` clears the found cells; empty ones go."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Literal, get_args

import pandas as pd

from ...errors import InvalidArguments
from ...frame import map_unique
from ...normalize import norm_phrase
from ..base import Matcher, bundled_list, choice, compiled, shown, split_words, word_key

__all__ = ["cells"]

CONTENT = ("contains", "starts", "ends")
CellKind = Literal["contains", "starts", "ends", "regex", "empty", "unique", "repeated", "first", "last"]
KINDS = get_args(CellKind)


def _text_test(kind: str, items: tuple[str, ...]) -> Callable[[str], bool]:
    if kind == "starts":
        return lambda phrase: norm_phrase(phrase).startswith(items)
    if kind == "ends":
        return lambda phrase: norm_phrase(phrase).endswith(items)
    return lambda phrase: any(item in norm_phrase(phrase) for item in items)


def _word_test(kind: str, words: frozenset[str]) -> Callable[[str], bool]:
    def test(phrase: str) -> bool:
        keys = [word_key(word) for word in split_words(phrase)]
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
        raise InvalidArguments(f"items: {shown(listed)}; allowed: a non-empty list of non-empty items.")
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
    def __init__(
        self, kind: CellKind, items: str | Iterable[str] | None, pattern: str | None, prepositions: bool
    ) -> None:
        self._kind = choice("kind", kind, KINDS)
        self._content: Callable[[str], object] | None = None
        if kind in CONTENT:
            self._content = _content_test(kind, items, prepositions)
        elif kind == "regex":
            self._content = _pattern_test(pattern)

    def find(self, phrases: pd.Series) -> pd.Series:
        blank = phrases == ""
        if self._kind == "empty":
            return blank
        if (content := self._content) is not None:
            return map_unique(phrases, lambda phrase: bool(content(phrase))).astype(bool)
        return self._occurrence(phrases, blank)

    def _occurrence(self, phrases: pd.Series, blank: pd.Series) -> pd.Series:
        """Cells compare in any case, ё as е, spaces as they are («диван » is no «диван»).

        Empty cells are never repeats of each other: each is the only one, the first and the last of its kind.
        """
        keys = phrases.str.lower().str.replace("ё", "е", regex=False)
        shared = keys.duplicated(keep=False) & ~blank
        if self._kind == "repeated":
            return shared
        if self._kind == "unique":
            return ~shared
        return ~(keys.duplicated(keep="first" if self._kind == "first" else "last") & ~blank)

    def remove(self, phrases: pd.Series) -> pd.Series:
        found = self.find(phrases)
        if self._kind == "empty":
            return phrases[~found]
        return phrases.where(~found, "")

    def extract(self, phrases: pd.Series) -> pd.Series:
        return phrases.where(self.find(phrases), "")


def cells(
    kind: CellKind,
    *,
    items: str | Iterable[str] | None = None,
    pattern: str | None = None,
    prepositions: bool = False,
) -> Cells:
    """A whole cell is found or not. remove clears a found cell (with "empty", it drops the rows); extract keeps the cell,
    or an empty cell if not found.

    kind: "contains", "starts", "ends" (with items: text parts, case and ё do not count; or with prepositions: the
    first, the last or any word is a bundled preposition, as written, «для,» is none); "regex" (with pattern); "empty"
    (no characters at all: a cell of spaces is not empty); by occurrence among the cells, in any case and ё as е:
    "unique" (once), "repeated" (more than once), "first", "last" occurrence. Empty cells are never repeats of each
    other.
    items: the text parts for "contains", "starts" and "ends".
    pattern: the regular expression for "regex".
    prepositions: for "contains", "starts" and "ends", look for a bundled preposition instead of items.

    ADR 0005: ё = е; empty cells are never duplicates; regex classes understand Cyrillic (Unicode); the fixed
    preposition list («по», no «g»); blank list items are refused.
    """
    return Cells(kind, items, pattern, prepositions)
