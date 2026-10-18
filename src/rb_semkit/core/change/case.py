"""`change_case`: the case of whole phrases, of sentences, of some words of a phrase."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from typing import Literal, NamedTuple, get_args

import pandas as pd

from .. import datastore
from ..errors import InvalidArguments
from ..markers.lists import phrases
from ..normalize import norm_phrase
from ..text.base import bundled_list, choice, split_words, word_key, word_list
from ..text.matchers.phrases import PhraseList, choose
from .common import capitalised, changed, each_word, split_edges

__all__ = ["change_case"]

Kind = Literal[
    "lower", "upper", "title", "sentence", "sentence_lower", "latin_title", "latin_upper",
    "list_title", "list_upper", "toponyms", "abbreviations",
]  # fmt: skip
KINDS = get_args(Kind)
LIST_KINDS = ("list_title", "list_upper")
TOPONYMS = "geo"
HYPHEN = "-"
# A sentence starts the text or follows «.», «!» or «?»; spaces may stand before its first letter or digit.
_SENTENCE_START = re.compile(r"(?:^|[.!?])\s*(\w)")
_LATIN_WORD_START = re.compile(r"(?<!\S)[a-z]")
_LATIN = re.compile(r"[A-Za-z]")
# Letters of a word that looks like an abbreviation: all consonants («hp», «спб»), or 3 vowels and more («ооо»).
CONSONANTS = frozenset("bcdfghjklmnpqrstvwxzбвгджзйклмнпрстфхцчшщъь")
VOWELS = frozenset("aeiouyаеёиоуыэюя")
ABBREVIATION_LENGTH = range(2, 6)
VOWEL_ABBREVIATION_LENGTH = 3


def _sentences(change: Callable[[str], str]) -> Callable[[str], str]:
    return lambda phrase: _SENTENCE_START.sub(lambda found: found[0][:-1] + change(found[1]), phrase)


def _latin_upper(word: str) -> str:
    return word.upper() if _LATIN.search(word) else word


def _listed(words: Iterable[str], change: Callable[[str], str]) -> Callable[[str], str]:
    keys = frozenset(map(norm_phrase, word_list("words", words)))
    return each_word(lambda word: change(word) if word_key(word) in keys else word)


class _Part(NamedTuple):
    """A word of a name, or a piece of a hyphenated word, with the punctuation around it and what joins it to the next."""

    prefix: str
    text: str
    suffix: str
    joiner: str


def _geo() -> PhraseList:
    """The bundled place names with a hyphen read as a space: «Ростов на Дону» is also «ростов-на-дону»."""
    return datastore.once(
        "change/geo_names",
        lambda: PhraseList(TOPONYMS, [name.replace(HYPHEN, " ") for name in phrases(TOPONYMS)]),
    )


def _parts(phrase: str) -> list[_Part]:
    parts: list[_Part] = []
    for word in split_words(phrase):
        prefix, core, suffix = split_edges(word)
        pieces = core.split(HYPHEN) if core and "" not in core.split(HYPHEN) else [core or word]
        last = len(pieces) - 1
        parts += [
            _Part(prefix if not index else "", piece, suffix if index == last else "", " " if index == last else HYPHEN)
            for index, piece in enumerate(pieces)
        ]
    return parts


def _toponyms(phrase: str) -> str:
    parts = _parts(phrase)
    for hit in reversed(choose(_geo().hits([part.text for part in parts]))):
        names = hit.spelling.split(" ")
        if len(names) == hit.stop - hit.start:
            parts[hit.start : hit.stop] = [
                part._replace(text=name) for part, name in zip(parts[hit.start : hit.stop], names, strict=True)
            ]
    return "".join(f"{part.prefix}{part.text}{part.suffix}{part.joiner}" for part in parts)[:-1]


def _looks_like_abbreviation(word: str) -> bool:
    """2 to 5 chars of one class: consonants, or vowels (3 or more); a first char of no class counts as a consonant,
    the other chars of no class do not count."""
    if len(word) not in ABBREVIATION_LENGTH:
        return False
    lower = word.lower()
    vowels = lower[0] in VOWELS
    if any((char in VOWELS) != vowels for char in lower[1:] if char in VOWELS or char in CONSONANTS):
        return False
    return not vowels or len(word) >= VOWEL_ABBREVIATION_LENGTH


def _abbreviations() -> Callable[[str], str]:
    spellings = {norm_phrase(item): item for item in bundled_list("abbreviations")}

    def change(word: str) -> str:
        word = word.upper() if _looks_like_abbreviation(word) else word
        return spellings.get(norm_phrase(word), word)

    return each_word(change)


def _change(kind: str, words: Iterable[str] | None) -> Callable[[str], str]:
    if kind in LIST_KINDS:
        if words is None:
            raise InvalidArguments(f"words: not given; allowed: one word or a non-empty list of single words ({kind}).")
        return _listed(words, capitalised if kind == "list_title" else str.upper)
    if words is not None:
        raise InvalidArguments(f"words are only for a list kind; allowed: kind {' or '.join(LIST_KINDS)}.")
    simple: dict[str, Callable[[str], str]] = {
        "lower": str.lower,
        "upper": str.upper,
        "title": capitalised,
        "sentence": _sentences(str.upper),
        "sentence_lower": _sentences(str.lower),
        "latin_title": lambda phrase: _LATIN_WORD_START.sub(lambda found: found[0].upper(), phrase),
        "latin_upper": each_word(_latin_upper),
        "toponyms": _toponyms,
    }
    return simple[kind] if kind in simple else _abbreviations()


def change_case(
    data: pd.Series | pd.DataFrame,
    kind: Kind,
    *,
    words: Iterable[str] | None = None,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """The phrase in another case.

    The word kinds split the phrase on any whitespace and join the words by one space.

    kind: the case to give:
    - "lower", "upper": the whole phrase;
    - "title": every word capitalised, the rest lower; a letter after a digit or a sign starts a word too
      («иван-петров 5g» → «Иван-Петров 5G»);
    - "sentence", "sentence_lower": the first letter of the text and of each sentence (after «.», «!», «?» and
      spaces) upper or lower; the other letters stay;
    - "latin_title": a word that starts with a small latin letter gets it capital («iphone» → «Iphone»);
    - "latin_upper": a word with a latin letter in upper case whole («wi-fi-роутер» → «WI-FI-РОУТЕР»);
    - "list_title", "list_upper": the words of `words` capitalised or upper (case and ё do not count);
    - "toponyms": the place names of the bundled geo list as the list spells them («нижний новгород» →
      «Нижний Новгород»), the longest name from each word; punctuation at the edges of a word is ignored and kept
      («в москве,» → «в Москве,»), and a hyphen splits a word («ростов-на-дону» → «Ростов-на-Дону»);
    - "abbreviations": a word of 2 to 5 consonants, or 3 to 5 vowels, upper («hp», «ооо»), then each word of the
      bundled abbreviations as the list spells it («спб» → «СПб», «usb» → «USB», «СМ» → «см»).
    words: the words for "list_title" and "list_upper".

    Example: {cli} read --text "купить диван" --text "диван ИКЕА" change-case title write -
    -> Купить Диван; Диван Икеа
    Example: {cli} read --text "купить диван в москве" change-case list_upper --words диван write -
    -> купить ДИВАН в москве
    """
    choice("kind", kind, KINDS)
    return changed(data, _change(kind, words), "change_case", column, inplace)
