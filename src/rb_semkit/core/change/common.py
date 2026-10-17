"""What the change functions share: the run over a column, the bundled tables, the word case classes and checks."""

from __future__ import annotations

from collections.abc import Callable, Mapping

import pandas as pd

from .. import datastore
from ..errors import InvalidArguments
from ..frame import Frame, map_unique
from ..normalize import norm_phrase
from ..text.base import bundled_list, split_words, strip_edges

TRANSLIT = "change/translit.json"
WORD_ORDER = "change/word_order.json"


def changed(
    data: pd.Series | pd.DataFrame,
    change: Callable[[str], str],
    operation: str,
    column: str | None,
    inplace: bool,
) -> pd.Series | pd.DataFrame:
    """Each distinct phrase changed once, the result put back as the frame puts it (`<column>_<operation>`)."""
    frame = Frame(data, column, inplace)
    return frame.put(map_unique(frame.phrases, change), operation)


def each_word(change: Callable[[str], str]) -> Callable[[str], str]:
    """A change of a phrase that changes each of its words and joins them by one space."""
    return lambda phrase: " ".join(map(change, split_words(phrase)))


def pairs_table(name: str) -> list[list[str]]:
    """A table of [from, to] pairs of the package data, in the order they apply."""
    return datastore.table(TRANSLIT)[name]


def stopword_keys() -> frozenset[str]:
    return datastore.once("change/stopword_keys", lambda: frozenset(map(norm_phrase, bundled_list("stopwords"))))


def is_stopword(word: str) -> bool:
    return norm_phrase(word) in stopword_keys()


def split_edges(text: str) -> tuple[str, str, str]:
    """The punctuation before the text, the text, the punctuation after it: «(Диван),» → «(», «Диван», «),»; a text
    of punctuation only has no middle."""
    core = strip_edges(text)
    start = text.find(core)
    return text[:start], core, text[start + len(core) :]


def capitalised(text: str) -> str:
    """Lower case, then the first letter of each run of letters upper: «o'neil 5g» → «O'Neil 5G»."""
    return text.title()


def adjusted(text: str, like: str) -> str:
    """`text` in the case of the word `like`: lower, capitalised (the first letter upper), upper, or as it is."""
    if like == like.lower():
        return text.lower()
    if like == capitalised(like):
        return text[:1].upper() + text[1:]
    if like == like.upper():
        return text.upper()
    return text


def text_pairs(argument: str, pairs: Mapping[str, str]) -> list[tuple[str, str]]:
    """The (find, replacement) items of a non-empty mapping of texts; an empty text to find is refused."""
    if not isinstance(pairs, Mapping) or not pairs:
        raise InvalidArguments(
            f"{argument}={pairs!r}; allowed: a non-empty mapping of a text to find to its replacement."
        )
    for find, replacement in pairs.items():
        if not isinstance(find, str) or not isinstance(replacement, str):
            raise InvalidArguments(f"{argument}: {find!r} → {replacement!r}; allowed: texts on both sides.")
        if not find:
            raise InvalidArguments(f"{argument}: the empty text {find!r}; allowed: a non-empty text to find.")
    return list(pairs.items())


def one_word(argument: str, value: str) -> str:
    if not isinstance(value, str) or len(split_words(value)) != 1:
        raise InvalidArguments(f"{argument}={value!r}; allowed: one word.")
    return value
