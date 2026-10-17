"""The text core: the tokenizer, the Matcher protocol and the three verbs find / remove / extract (ADR 0004).

A phrase is split on any run of whitespace, so no word is empty and joined results never hold double spaces.
Words are compared by `norm_phrase` (case, ё→е); the output keeps the words as the phrase spells them.

Helpers shared by the matchers: `strip_edges` (a word without edge punctuation), `collapse` (single spaces, none
at the edges), `bundled_list` (a word list of the package data), and argument checks that raise InvalidArguments
naming the argument and the allowed values: `choice`, `whole_number` (N from 1), `word_list`, `compiled` (a regex).
"""

from __future__ import annotations

import re
from collections.abc import Iterable

import pandas as pd

from .. import datastore
from ..errors import InvalidArguments
from ..frame import Frame, map_unique
from ..normalize import norm_phrase

VERBS = ("find", "remove", "extract")
_EDGE_PUNCTUATION = re.compile(r"^[\W_]+|[\W_]+$")


def split_words(phrase: str) -> list[str]:
    return phrase.split()


def strip_edges(word: str) -> str:
    """The word without punctuation at its edges: «Диван,» → «Диван»."""
    return _EDGE_PUNCTUATION.sub("", word)


def word_key(word: str, *, ignore_punct: bool = False) -> str:
    """A word as compared: `norm_phrase`, and with `ignore_punct` without punctuation at its edges («Диван,» → диван)."""
    return norm_phrase(strip_edges(word) if ignore_punct else word)


def bundled_list(name: str) -> list[str]:
    """A word list of the package data by name: "stopwords", "prepositions", "toponym_prepositions_ru"…"""
    return datastore.table("text/lists.json")[name]


def collapse(text: str) -> str:
    """The text with every run of whitespace as one space, none at the edges."""
    return " ".join(text.split())


def choice(argument: str, value: str, allowed: tuple[str, ...]) -> str:
    """`value` when it is one of `allowed`, else InvalidArguments naming `argument` and the allowed values."""
    if value not in allowed:
        raise InvalidArguments(f"{argument}={value!r}; allowed: {', '.join(repr(item) for item in allowed)}.")
    return value


def compiled(argument: str, pattern: str) -> re.Pattern[str]:
    """The regular expression `pattern`, or InvalidArguments naming `argument` when it is not one."""
    try:
        return re.compile(pattern)
    except (re.error, TypeError) as error:
        raise InvalidArguments(f"{argument}={pattern!r}; allowed: a valid regular expression ({error}).") from None


def whole_number(argument: str, value: int) -> int:
    """`value` when it is an integer of 1 or more (N counts words or chars, from 1)."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise InvalidArguments(f"{argument}={value!r}; allowed: an integer of 1 or more.")
    return value


def word_list(argument: str, items: str | Iterable[str]) -> list[str]:
    """One word or a non-empty list of single words, as a list."""
    listed = [items] if isinstance(items, str) else list(items)
    if not listed or not all(isinstance(item, str) and len(split_words(item)) == 1 for item in listed):
        raise InvalidArguments(f"{argument}={listed!r}; allowed: one word or a non-empty list of single words.")
    return listed


class Matcher:
    """What a verb looks for in phrases. A matcher overrides the verbs it supports, each over a Series of phrases.

    find gives a bool mask, remove the cleaned text, extract the found part. A verb the matcher does not
    override raises InvalidArguments naming the ones it does.
    """

    def find(self, phrases: pd.Series) -> pd.Series:
        raise self._unsupported("find")

    def remove(self, phrases: pd.Series) -> pd.Series:
        raise self._unsupported("remove")

    def extract(self, phrases: pd.Series) -> pd.Series:
        raise self._unsupported("extract")

    def _unsupported(self, verb: str) -> InvalidArguments:
        supported = [name for name in VERBS if getattr(type(self), name) is not getattr(Matcher, name)]
        return InvalidArguments(f"{verb}: {type(self).__name__} does not support it; allowed: {', '.join(supported)}.")


class WordMatcher(Matcher):
    """A matcher of whole words: it marks the words of one phrase in `picks`; the three verbs follow from that."""

    def picks(self, words: list[str]) -> list[bool]:
        raise NotImplementedError

    def find(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, lambda phrase: any(self.picks(split_words(phrase)))).astype(bool)

    def remove(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, lambda phrase: self._join(phrase, keep=False))

    def extract(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, lambda phrase: self._join(phrase, keep=True))

    def _join(self, phrase: str, *, keep: bool) -> str:
        words = split_words(phrase)
        return " ".join(word for word, picked in zip(words, self.picks(words), strict=True) if picked is keep)


def _checked(matcher: Matcher) -> Matcher:
    if not isinstance(matcher, Matcher):
        raise InvalidArguments(f"matcher is a {type(matcher).__name__}; allowed: a matcher such as sk.words([...]).")
    return matcher


def _apply(
    verb: str, data: pd.Series | pd.DataFrame, matcher: Matcher, column: str | None, inplace: bool
) -> pd.Series | pd.DataFrame:
    frame = Frame(data, column, inplace)
    return frame.put(getattr(_checked(matcher), verb)(frame.phrases), verb)


def find(
    data: pd.Series | pd.DataFrame, matcher: Matcher, *, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """A bool mask: True where `matcher` finds something in the phrase."""
    return _apply("find", data, matcher, column, inplace)


def remove(
    data: pd.Series | pd.DataFrame, matcher: Matcher, *, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """The phrase without what `matcher` finds."""
    return _apply("remove", data, matcher, column, inplace)


def extract(
    data: pd.Series | pd.DataFrame, matcher: Matcher, *, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """Only what `matcher` finds in the phrase; an empty string where it finds nothing."""
    return _apply("extract", data, matcher, column, inplace)


class Pipe:
    """Verbs chained over one column: `sk.pipe(df, "phrase").remove(m1).remove(m2).phrases`."""

    def __init__(self, phrases: pd.Series) -> None:
        self.phrases = phrases

    def find(self, matcher: Matcher) -> pd.Series:
        return _checked(matcher).find(self.phrases)

    def remove(self, matcher: Matcher) -> Pipe:
        return Pipe(_checked(matcher).remove(self.phrases))

    def extract(self, matcher: Matcher) -> Pipe:
        return Pipe(_checked(matcher).extract(self.phrases))


def pipe(data: pd.Series | pd.DataFrame, column: str | None = None) -> Pipe:
    """Start a chain of verbs over a Series or a DataFrame column; the input is not changed."""
    return Pipe(Frame(data, column).phrases)
