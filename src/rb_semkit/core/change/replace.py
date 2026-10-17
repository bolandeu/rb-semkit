"""`replace_words`: whole words and phrases by a list; `replace_text`: by a text inside, the whole phrase or a regex."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping

import pandas as pd

from ..errors import InvalidArguments
from ..normalize import norm_phrase
from ..text.base import choice, compiled, split_words
from .common import adjusted, capitalised, changed, text_pairs

__all__ = ["replace_text", "replace_words"]

CASES = ("new", "keep")
BY = ("substring", "phrase", "regex")
_YO = "[её]"


def _by_length(pairs: list[tuple[str, str]]) -> dict[int, dict[str, str]]:
    """The replacements by the number of words of what they replace, longest first; the first of equal keys wins."""
    found: dict[int, dict[str, str]] = {}
    for find, replacement in pairs:
        key = norm_phrase(find)
        found.setdefault(len(key.split(" ")), {}).setdefault(key, replacement)
    return dict(sorted(found.items(), reverse=True))


def _replaced_words(words: list[str], length: int, table: dict[str, str], keep_case: bool) -> list[str]:
    """Each run of `length` words found in `table`, left to right, replaced by its words."""
    result: list[str] = []
    index = 0
    while index < len(words):
        replacement = table.get(norm_phrase(" ".join(words[index : index + length])))
        if replacement is None:
            result.append(words[index])
            index += 1
            continue
        result += split_words(adjusted(replacement, words[index]) if keep_case else replacement)
        index += length
    return result


def replace_words(
    data: pd.Series | pd.DataFrame,
    pairs: Mapping[str, str],
    *,
    case: str = "new",
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Whole words and phrases of the phrase replaced by `pairs` (what to find → its replacement); case and ё do not
    count. Longer phrases go first: {"стиральная машинка": "стиральная машина", "машинка": "машина"}. An empty
    replacement deletes the words.

    case: "new" — the replacement as given; "keep" — in the case of the first word it replaces (lower, capitalised,
    upper; a word of mixed case keeps the replacement as given).
    """
    by_length = _by_length(text_pairs("pairs", pairs))
    keep_case = choice("case", case, CASES) == "keep"

    def change(phrase: str) -> str:
        words = split_words(phrase)
        for length, table in by_length.items():
            words = _replaced_words(words, length, table, keep_case)
        return " ".join(words)

    return changed(data, change, "replace_words", column, inplace)


def _class_case(text: str, like: str) -> str:
    """`text` upper when `like` is upper (digits and an empty text too), capitalised when `like` is, else lower."""
    if like == like.upper():
        return text.upper()
    return capitalised(text) if like == capitalised(like) else text.lower()


def _substring(pairs: list[tuple[str, str]]) -> Callable[[str], str]:
    patterns = [
        (re.compile("".join(_YO if char in "её" else re.escape(char) for char in find.lower()), re.IGNORECASE), to)
        for find, to in pairs
    ]

    def change(phrase: str) -> str:
        for pattern, replacement in patterns:
            phrase = pattern.sub(lambda _found, replacement=replacement: replacement, phrase)
        return phrase

    return change


def _phrase(pairs: list[tuple[str, str]]) -> Callable[[str], str]:
    table: dict[str, str] = {}
    for find, replacement in pairs:
        table.setdefault(norm_phrase(find), replacement)

    def change(phrase: str) -> str:
        replacement = table.get(norm_phrase(phrase))
        return phrase if replacement is None else _class_case(replacement, phrase)

    return change


def _regex(pairs: list[tuple[str, str]], first_only: bool) -> Callable[[str], str]:
    patterns = [(compiled("pairs", find), replacement) for find, replacement in pairs]
    for pattern, replacement in patterns:
        try:
            pattern.sub(replacement, "")
        except re.error as error:
            raise InvalidArguments(f"pairs: {replacement!r}; allowed: a valid replacement ({error}).") from None

    def change(phrase: str) -> str:
        for pattern, replacement in patterns if phrase else ():
            phrase = pattern.sub(replacement, phrase, count=int(first_only))
        return phrase

    return change


def replace_text(
    data: pd.Series | pd.DataFrame,
    pairs: Mapping[str, str],
    *,
    by: str = "substring",
    first_only: bool = False,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """The phrase changed by `pairs`, one after the other (a later pair works on the result of the earlier ones):

    - by="substring": every occurrence of the text, in any case and ё as е, becomes the replacement as given;
    - by="phrase": a phrase equal to the text (case, ё and extra spaces do not count) becomes the replacement in the
      case of the phrase: lower, capitalised or upper («МОСКВА» → «САНКТ-ПЕТЕРБУРГ»);
    - by="regex": each match of the pattern (cyrillic letters are word chars) becomes the replacement, with `\\1` and
      `\\g<name>` for the groups; first_only: only the first match.
    """
    listed = text_pairs("pairs", pairs)
    choice("by", by, BY)
    if first_only and by != "regex":
        raise InvalidArguments(f"first_only is only for a regex; allowed: by='regex', not by={by!r}.")
    change = _regex(listed, first_only) if by == "regex" else (_substring if by == "substring" else _phrase)(listed)
    return changed(data, change, "replace_text", column, inplace)
