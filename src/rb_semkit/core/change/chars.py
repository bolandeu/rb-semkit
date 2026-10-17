"""Changes char by char: quotes to «ёлочки», translit both ways, ЧПУ, the keyboard layout, similar chars cyr↔lat."""

from __future__ import annotations

import re
from collections.abc import Callable

import pandas as pd

from .. import datastore
from ..text.base import choice
from .common import changed, pairs_table

__all__ = ["chpu", "guillemets", "similar_chars", "switch_layout", "translit"]

LANGUAGES = ("en", "ru")
QUOTE = '"'
OPENING, CLOSING = "«", "»"
_WORD = re.compile(r"\S+")
_NOT_SLUG = re.compile(r"[^a-z0-9]+")
SLUG_SEP = "-"


def guillemets(
    data: pd.Series | pd.DataFrame, *, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """Straight double quotes as «ёлочки», opening and closing in turn: «диван "Честер" купить» → «диван «Честер»
    купить». A phrase with quotes loses the spaces at its edges."""

    def change(phrase: str) -> str:
        if QUOTE not in phrase:
            return phrase
        parts = phrase.split(QUOTE)
        marks = [OPENING if index % 2 == 0 else CLOSING for index in range(len(parts) - 1)]
        return "".join(part + mark for part, mark in zip(parts, [*marks, ""], strict=True)).strip(" ")

    return changed(data, change, "guillemets", column, inplace)


def _to_latin_table() -> dict[int, str]:
    table = {}
    for cyrillic, latin in pairs_table("translit_ru_en"):
        table[ord(cyrillic)] = latin
        table[ord(cyrillic.upper())] = latin.capitalize()
    return table


def _to_latin(phrase: str) -> str:
    table = datastore.once("change/to_latin", _to_latin_table)
    if phrase == phrase.lower():
        return phrase.translate(table)
    return _WORD.sub(lambda word: _latin_word(word[0], table), phrase)


def _latin_word(word: str, table: dict[int, str]) -> str:
    latin = word.translate(table)
    return latin.upper() if sum(char.isupper() for char in word) > 1 and word == word.upper() else latin


def _to_cyrillic(phrase: str) -> str:
    for latin, cyrillic in pairs_table("translit_en_ru"):
        phrase = phrase.replace(latin, cyrillic)
    return phrase


def translit(
    data: pd.Series | pd.DataFrame, *, to: str, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """Letters of one alphabet written in the other: to="en" — «Щука жёлтая» → «Schuka zheltaya», a word in capitals
    stays in capitals («ЖУК» → «ZHUK»); to="ru" — by letter groups, «Yandex» → «Яндекс», «Jeep» → «Джееп»,
    «ob'em» → «обэм». The other chars stay."""
    choice("to", to, LANGUAGES)
    return changed(data, _to_latin if to == "en" else _to_cyrillic, "translit", column, inplace)


def _slug_table() -> dict[int, str]:
    return {ord(char): value.lower() for char, value in pairs_table("chpu")}


def chpu(
    data: pd.Series | pd.DataFrame, *, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """The phrase as a ЧПУ (a human-readable URL part): latin letters and digits in lower case, cyrillic in translit,
    accented letters as plain ones; the spaces and signs between words become one «-», none at the edges:
    «Диван-кровать 2 м!» → «divan-krovat-2-m», «Щётка  ёж» → «schetka-ezh»."""
    table = datastore.once("change/chpu", _slug_table)

    def change(phrase: str) -> str:
        return _NOT_SLUG.sub(SLUG_SEP, phrase.translate(table)).strip(SLUG_SEP)

    return changed(data, change, "chpu", column, inplace)


def _layout_table(to: str) -> dict[int, str]:
    """Each key of one layout to the same key of the other; a key whose capital is itself (a sign) maps once."""
    table: dict[int, str] = {}
    for english, russian in pairs_table("layout"):
        source, target = (english, russian) if to == "ru" else (russian, english)
        table[ord(source)] = target
        if source.upper() != source:
            table[ord(source.upper())] = target.upper()
    return table


def _translated(name: str, build: Callable[[], dict[int, str]]) -> Callable[[str], str]:
    table = datastore.once(name, build)
    return lambda phrase: phrase.translate(table)


def switch_layout(
    data: pd.Series | pd.DataFrame, *, to: str, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """Text typed in the wrong keyboard layout, retyped on the same keys of the other: to="ru" — «ghbdtn, vbh» →
    «приветб мир», «z» → «я»; to="en" — «привет» → «ghbdtn», a capital on a sign key gives its shifted sign
    («Б» → «<», «Ё» → «~»)."""
    choice("to", to, LANGUAGES)
    return changed(
        data, _translated(f"change/layout_{to}", lambda: _layout_table(to)), "switch_layout", column, inplace
    )


def _similar_table(to: str) -> dict[int, str]:
    pairs = pairs_table("similar_chars")
    return {ord(source): target for source, target in (pairs if to == "en" else [pair[::-1] for pair in pairs])}


def similar_chars(
    data: pd.Series | pd.DataFrame, *, to: str, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """The letters that look alike in both alphabets (а a, В B, Н H, р p, с c, у y, х x…) in the alphabet `to`:
    to="en" — «Москва» → «Mockвa»; to="ru" — «CTO» → «СТО». The other letters stay."""
    choice("to", to, LANGUAGES)
    return changed(
        data, _translated(f"change/similar_{to}", lambda: _similar_table(to)), "similar_chars", column, inplace
    )
