"""`phonetic`: English words written in Russian as they sound, by the bundled tables of whole words, word ends, word
starts and letter groups."""

from __future__ import annotations

from typing import NamedTuple

import pandas as pd

from .. import datastore
from ..text.base import split_words
from .common import adjusted, changed, pairs_table

__all__ = ["phonetic"]

LENGTHS = (5, 4, 3, 2)


class Tables(NamedTuple):
    words: dict[str, str]
    suffixes: dict[int, dict[str, str]]
    prefixes: dict[int, dict[str, str]]
    groups: dict[int, list[list[str]]]  # by length, in the order they apply; 1 is the single letters


def _lookup(name: str) -> dict[str, str]:
    return {english: russian for english, russian in pairs_table(name)}


def _tables() -> Tables:
    return Tables(
        _lookup("phonetic_words"),
        {length: _lookup(f"phonetic_suffixes_{length}") for length in LENGTHS},
        {length: _lookup(f"phonetic_prefixes_{length}") for length in LENGTHS},
        {length: pairs_table(f"phonetic_any_{length}") for length in (*LENGTHS, 1)},
    )


def _replaced(text: str, groups: list[list[str]]) -> str:
    for english, russian in groups:
        text = text.replace(english, russian)
    return text


def _russian(word: str, tables: Tables) -> str:
    """A lower-case word: a whole word of the table; else for 5 to 2 letters the longest word end and word start
    of the tables (one of each at most, while the word is that long), then the letter groups of that length."""
    if word in tables.words:
        return tables.words[word]
    text = word
    suffix_done = prefix_done = False
    for length in LENGTHS:
        if len(word) >= length:
            suffix = tables.suffixes[length].get(text[-length:])
            if not suffix_done and suffix is not None:
                text, suffix_done = text[:-length] + suffix, True
            prefix = tables.prefixes[length].get(text[:length])
            if not prefix_done and prefix is not None:
                text, prefix_done = prefix + text[length:], True
        text = _replaced(text, tables.groups[length])
    return _replaced(text, tables.groups[1])


def phonetic(
    data: pd.Series | pd.DataFrame, *, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """Each word read as English and written in Russian.

    «Dreamline» → «Дримлайн», «iphone» → «айфон», «google» → «гугл». A word keeps its case: lower, capitalised or
    upper («XIAOMI» → «СЯОМИ»); a word of mixed case comes out lower. The words are joined by one space.

    Example: {cli} read --text "Dreamline" --text "iphone" phonetic write -
    -> Дримлайн; айфон
    """
    tables = datastore.once("change/phonetic", _tables)

    def change(phrase: str) -> str:
        return " ".join(adjusted(_russian(word.lower(), tables), word) for word in split_words(phrase))

    return changed(data, change, "phonetic", column, inplace)
