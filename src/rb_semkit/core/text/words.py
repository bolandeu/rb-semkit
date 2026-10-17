"""The words of a text: one rule for split_text, text_stats, coverage, the comparisons and the n-grams.

A word is a run of letters that have a case and digits. A hyphen or an apostrophe between two of them and a point or a
comma between two digits stay inside it: «кресло-кровать», «it's», «31.03.2026», «541,67», «275-30-85». Any other
character is no part of a word, so «руб.» is the word «руб» and «★» is none.

`pieces` cuts a text at the marks between its words, by a rule of what cuts: `ends_phrase` (split_text) cuts at any
punctuation but a dash between words; `ends_sentence` (coverage) only at a sentence end. A point after an abbreviation
of `data/text/words.toml` («г. Краснознаменск», «т. е.») is no mark of either.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Callable
from functools import cache

from .. import datastore
from ..errors import InvalidArguments
from ..normalize import norm_phrase
from .matchers.classes import DIGITS, NUMBER_MARK, cased

SETTINGS = "text/words.toml"
DASHES = "-‐‑‒–—―"
SENTENCE_ENDS = ".!?…"
ABBREVIATION_POINT = "."

Cut = Callable[[str, str], bool]  # the marks between two words, the word before them -> they end a piece


@cache
def _word() -> re.Pattern[str]:
    char = f"[{cased()}{DIGITS}]"
    return re.compile(rf"{char}+(?:(?:['’-]|{NUMBER_MARK}){char}+)*")


def _settings() -> dict[str, frozenset[str]]:
    path = datastore.DATA_DIR / SETTINGS
    values = tomllib.loads(path.read_text(encoding="utf-8"))
    missing = [name for name in ("abbreviations", "units") if name not in values]
    if missing:
        raise InvalidArguments(f"{path}: no settings {missing!r}; allowed: a file with abbreviations and units.")
    return {name: frozenset(map(norm_phrase, values[name])) for name in ("abbreviations", "units")}


def _setting(name: str) -> frozenset[str]:
    return datastore.once(SETTINGS, _settings)[name]


def text_words(text: str) -> list[str]:
    """The words of a text, in order."""
    return _word().findall(text)


def has_lemma(key: str) -> bool:
    """False for a word (as `norm_phrase` folds it) that is a word but no lemma of the text metrics: a single letter,
    an abbreviation or a unit of `data/text/words.toml`."""
    single_letter = len(key) == 1 and not key.isdigit()
    return not (single_letter or key in _setting("abbreviations") or key in _setting("units"))


def _marks(between: str, before: str) -> str:
    """The marks between two words without the whitespace and without the point of an abbreviation before them."""
    marks = "".join(between.split())
    if marks.startswith(ABBREVIATION_POINT) and norm_phrase(before) in _setting("abbreviations"):
        return marks[1:]
    return marks


def ends_phrase(between: str, before: str) -> bool:
    """Punctuation between two words that is not a dash and not the point of an abbreviation."""
    return any(mark not in DASHES for mark in _marks(between, before))


def ends_sentence(between: str, before: str) -> bool:
    """A point, «!», «?» or «…» between two words that is not the point of an abbreviation."""
    return any(mark in SENTENCE_ENDS for mark in _marks(between, before))


def pieces(text: str, cuts: Cut) -> list[list[str]]:
    """The words of a text in pieces: a new piece starts where `cuts` says the marks before a word end one."""
    found: list[list[str]] = []
    piece: list[str] = []
    end = 0
    for match in _word().finditer(text):
        if piece and cuts(text[end : match.start()], piece[-1]):
            found.append(piece)
            piece = []
        piece.append(match.group())
        end = match.end()
    if piece:
        found.append(piece)
    return found
