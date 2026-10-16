"""The add-in's character classes and word tests (docs/vba/matchers.md S4), shared by the matchers.

VBA compares with `Option Compare Binary`, so `[A-Za-z]` and `[0-9]` are ASCII. A letter is «cased» when its upper and
lower case differ (`UCase(c) <> LCase(c)`): latin, cyrillic, greek…, not CJK or Arabic; VBA strings are UTF-16, so
only the Basic Multilingual Plane counts. Each class is a regex class body, to put inside `[…]` or `[^…]`.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from functools import cache

LATIN = "A-Za-z"
DIGITS = "0-9"
# `—–o` (line 2147): А..ӿ and Ё; not Ѐ..Џ, so the capitals Є І Ї are not cyrillic, their small letters are
CYRILLIC = "А-ӿЁ"
# `[А-Яа-я]` of the Like masks (`ala`, line 1770): Ё and ё are not in it
RU_LETTERS = "А-я"
_LAST_BMP = 0xFFFF
_SURROGATES = range(0xD800, 0xE000)

_HAS_LATIN = re.compile(f"[{LATIN}]")
_HAS_DIGIT = re.compile(f"[{DIGITS}]")
_HAS_CYRILLIC = re.compile(f"[{CYRILLIC}]")
_DIGIT_OR_RU = re.compile(f"[{DIGITS}{RU_LETTERS}]")
# `IsNumeric` (line 2360) as the add-in runs it: a sign, a decimal comma or point, an exponent, a currency sign,
# a negative in brackets, a hex or octal literal: «1,5», «1e3», «-5», «(5)», «$5», «&H10».
_NUMBER = r"\$?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:e[+-]?\d+)?"
_NUMERIC = re.compile(rf"[+-]?{_NUMBER}|\({_NUMBER}\)|&h[0-9a-f]+|&o?[0-7]+", re.IGNORECASE)


def _class_of(test: Callable[[str], bool]) -> str:
    """A regex class body of every BMP character that passes `test`, as ranges."""
    ranges: list[list[int]] = []
    for code in range(_LAST_BMP + 1):
        if code in _SURROGATES or not test(chr(code)):
            continue
        if ranges and ranges[-1][1] == code - 1:
            ranges[-1][1] = code
        else:
            ranges.append([code, code])
    return "".join(
        re.escape(chr(first)) + (f"-{re.escape(chr(last))}" if last > first else "") for first, last in ranges
    )


@cache
def cased() -> str:
    """The letters whose upper and lower case differ."""
    return _class_of(lambda char: char.upper() != char.lower())


@cache
def upper() -> str:
    """The letters that differ from their lower case (`ooa`, line 2655)."""
    return _class_of(lambda char: char != char.lower())


@cache
def _has_cased() -> re.Pattern[str]:
    return re.compile(f"[{cased()}]")


def has_latin(word: str) -> bool:
    """`a–—` (line 2153): an ASCII latin letter."""
    return _HAS_LATIN.search(word) is not None


def has_digit(word: str) -> bool:
    """`·kk` (line 1619): an ASCII digit."""
    return _HAS_DIGIT.search(word) is not None


def has_cyrillic(word: str) -> bool:
    """`—–o` (line 2147): a cyrillic letter of `CYRILLIC`."""
    return _HAS_CYRILLIC.search(word) is not None


def has_cased(word: str) -> bool:
    """A letter whose upper and lower case differ (`UCase(x) <> LCase(x)`)."""
    return _has_cased().search(word) is not None


def only_latin(word: str) -> bool:
    """`ala` (line 1770): a latin letter and no digit and no `[А-Яа-я]`; punctuation is allowed («Wi-Fi»)."""
    return has_latin(word) and _DIGIT_OR_RU.search(word) is None


def is_numeric(word: str) -> bool:
    """`··—` (line 2360): the word is a number for VBA `IsNumeric` («2», «1,5», «-5», «1e3»)."""
    return _NUMERIC.fullmatch(word) is not None
