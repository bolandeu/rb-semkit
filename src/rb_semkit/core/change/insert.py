"""`insert` text round a phrase or its words, `move_words` of a list to the start or the end of a phrase."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from ..errors import InvalidArguments
from ..text.base import choice, collapse, split_words, word_key, word_list
from .common import changed

__all__ = ["insert", "move_words"]

PLACES = ("start", "end")


def insert(
    data: pd.Series | pd.DataFrame,
    *,
    before: str = "",
    after: str = "",
    each_word: bool = False,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """`before` at the start and `after` at the end of the phrase, as given; an empty phrase gets them too.

    each_word: round each word of the phrase instead («купить диван» with after="," → «купить, диван,»); the words
    are joined by one space and an empty phrase stays empty.
    """
    if not (isinstance(before, str) and isinstance(after, str)):
        raise InvalidArguments(f"before, after: {before!r}, {after!r}; allowed: texts.")
    if not (before or after):
        raise InvalidArguments("before, after: neither given; allowed: a text in before, after or both.")
    if each_word:
        return changed(
            data,
            lambda phrase: collapse(" ".join(before + word + after for word in split_words(phrase))),
            "insert",
            column,
            inplace,
        )
    return changed(data, lambda phrase: before + phrase + after, "insert", column, inplace)


class WordMover:
    """Moves the words of a phrase equal to the items of a list (case and ё do not count) to its start or end, in the
    order and the spelling of the list; the first equal word moves, a repeated item takes the next one."""

    def __init__(self, items: list[str]) -> None:
        self._items = items
        self._places: dict[str, list[int]] = {}
        for place, item in enumerate(items):
            self._places.setdefault(word_key(item), []).append(place)

    def moved(self, words: list[str], to: str) -> list[str]:
        found: dict[str, list[int]] = {}
        for index, word in enumerate(words):
            found.setdefault(word_key(word), []).append(index)
        taken = sorted(  # the n-th item of a key takes the n-th word of it; either may run out first
            (place, index)
            for key, indexes in found.items()
            for place, index in zip(self._places.get(key, ()), indexes, strict=False)
        )
        gone = {index for _, index in taken}
        moved = [self._items[place] for place, _ in taken]
        kept = [word for index, word in enumerate(words) if index not in gone]
        return moved + kept if to == "start" else kept + moved


def move_words(
    data: pd.Series | pd.DataFrame,
    words: str | Iterable[str],
    *,
    to: str = "start",
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """The words of `words` found in the phrase moved to its start or end (`to`), in the order and the spelling of
    `words`: «диван угловой купить» with ["купить", "угловой"] → «купить угловой диван». Case and ё do not count;
    the first word equal to an item moves."""
    mover = WordMover(word_list("words", words))
    choice("to", to, PLACES)
    return changed(data, lambda phrase: " ".join(mover.moved(split_words(phrase), to)), "move_words", column, inplace)
