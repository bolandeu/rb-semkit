"""Match types of the search engines' ads: operators on a phrase (`match_type`), modifiers taken off the stopwords
(`drop_modifiers`) and the minus-words dropped (`drop_minus_words`).

A minus-word is a word that starts with «-» and has more after it («-бесплатно»); a lone «-» is a dash. A word with
an operator is one that starts with «+», «!» or «-».
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from ..text.base import choice, split_words
from .common import changed, each_word, is_stopword

__all__ = ["drop_minus_words", "drop_modifiers", "match_type"]

KINDS = (
    *("broad", "broad_modifier", "plus_every_word", "stopword_modifier", "fixed_forms"),
    *("quoted_fixed_forms", "quoted_fixed_order", "brackets", "quotes", "antisemantic"),
)
MODIFIERS = ("+", "!")
OPERATORS = ("+", "!", "-")
BROAD_STRIPPED = str.maketrans("", "", '+![]"')
# The kinds that wrap the words of the phrase: the opening and the closing marks, and the operator of each word.
WRAPS = {
    "quoted_fixed_forms": ('"', '"', "!"),
    "quoted_fixed_order": ('"[', ']"', "!"),
    "brackets": ("[", "]", ""),
    "quotes": ('"', '"', ""),
}


def _is_minus_word(word: str) -> bool:
    return len(word) > 1 and word[0] == "-"


def _with_operator(word: str, operator: str) -> str:
    return word if word.startswith(OPERATORS) else operator + word


def _without_stopword_modifier(word: str) -> str:
    return word[1:] if len(word) > 1 and word.startswith(MODIFIERS) and is_stopword(word[1:]) else word


def _wrapped(opening: str, closing: str, operator: str) -> Callable[[str], str]:
    def change(phrase: str) -> str:
        words = split_words(phrase)
        minus = [word for word in words if _is_minus_word(word)]
        kept = [_with_operator(word, operator) if operator else word for word in words if not _is_minus_word(word)]
        return " ".join([f"{opening}{' '.join(kept)}{closing}"] * bool(kept) + minus)

    return change


def _change(kind: str, modifier: str) -> Callable[[str], str]:
    if kind in WRAPS:
        return _wrapped(*WRAPS[kind])
    plus = each_word(lambda word: _with_operator(word, "+"))
    kinds: dict[str, Callable[[str], str]] = {
        "broad": lambda phrase: phrase.translate(BROAD_STRIPPED),
        "plus_every_word": plus,
        "broad_modifier": lambda phrase: each_word(_without_stopword_modifier)(plus(phrase)),
        "stopword_modifier": each_word(lambda word: modifier + word if is_stopword(word) else word),
        "fixed_forms": each_word(lambda word: _with_operator(word, "!")),
        "antisemantic": each_word(
            lambda word: word if is_stopword(word) or word.startswith(OPERATORS) else f"[{word}]"
        ),
    }
    return kinds[kind]


def match_type(
    data: pd.Series | pd.DataFrame,
    kind: str,
    *,
    modifier: str = "+",
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """The phrase with the operators of a match type, by `kind`:

    - "broad": «A в Б», every «+», «!», «[», «]» and «"» taken out;
    - "plus_every_word": «+A +в +Б»; "broad_modifier": «+A в +Б», the stopwords plain;
    - "stopword_modifier": «A +в Б», `modifier` ("+" or "!") on the stopwords only;
    - "fixed_forms": «!A !в !Б»; "quoted_fixed_forms": «"!A !в !Б"»; "quoted_fixed_order": «"[!A !в !Б]"»;
    - "brackets": «[A в Б]»; "quotes": «"A в Б"»;
    - the exact match is "quotes", "quoted_fixed_forms" and "quoted_fixed_order" for Yandex, "brackets" for
      Google; the phrase match is "brackets" for Yandex, "quotes" for Google;
    - "antisemantic": «[A] в [Б]», each word but the stopwords in brackets.

    A word that has an operator keeps it, and no other is added; the minus-words keep their place, and the kinds that
    wrap the phrase put them after it («"купить диван" -бесплатно»). Stopwords are found in any case. An empty phrase
    stays empty; the words are joined by one space ("broad" keeps the spaces as they are).
    """
    choice("kind", kind, KINDS)
    choice("modifier", modifier, MODIFIERS)
    return changed(data, _change(kind, modifier), "match_type", column, inplace)


def drop_modifiers(
    data: pd.Series | pd.DataFrame, *, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """The «+» or «!» of each stopword taken off, in any case: «+купить +в !москве +для дачи» → «+купить в !москве
    для дачи». The words are joined by one space."""
    return changed(data, each_word(_without_stopword_modifier), "drop_modifiers", column, inplace)


def drop_minus_words(
    data: pd.Series | pd.DataFrame, *, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """The phrase without its minus-words: «купить диван -бесплатно -скачать» → «купить диван». A lone «-» between
    words is a dash and stays («диван - кровать»). The words are joined by one space."""
    return changed(
        data,
        lambda phrase: " ".join(word for word in split_words(phrase) if not _is_minus_word(word)),
        "drop_minus_words",
        column,
        inplace,
    )
