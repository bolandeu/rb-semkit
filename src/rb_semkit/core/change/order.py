"""The order inside a phrase: text split from digits, chars or words reversed, words sorted."""

from __future__ import annotations

import re
from typing import Literal, get_args

import pandas as pd

from ..errors import InvalidArguments
from ..text.base import choice, split_words
from .common import changed

__all__ = ["reverse", "sort_words", "split_digits"]

What = Literal["chars", "words"]
WHAT = get_args(What)
# Between a digit and a letter or a sign glued to it, either way round; a size «140х200» (latin or cyrillic x) is
# matched whole, after the edge in front of it, so it has no edge inside.
_DIGIT_EDGE = re.compile(r"(?<=\d)(?=[^\d\s])|(?<=[^\d\s])(?=\d)|(?P<size>\d+(?:[xх]\d+)+)", re.IGNORECASE)


def split_digits(
    data: pd.Series | pd.DataFrame, *, sep: str = " ", column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """A separator between digits and the text glued to them: «iphone13pro» → «iphone 13 pro». Digits and text already
    apart stay as they are; a size N×M (the x latin or cyrillic, in any case) stays whole («диван140х200» → «диван
    140х200»).

    sep: the separator; with "|" «a1b22» → «a|1|b|22».
    """
    if not isinstance(sep, str):
        raise InvalidArguments(f"sep={sep!r}; allowed: a text.")
    return changed(
        data,
        lambda phrase: _DIGIT_EDGE.sub(lambda found: found["size"] or sep, phrase),
        "split_digits",
        column,
        inplace,
    )


def reverse(
    data: pd.Series | pd.DataFrame, *, what: What = "chars", column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """The phrase backwards.

    what: "chars" — its characters («абв 12» → «21 вба»); "words" — its words, joined by one space («купить диван
    москва» → «москва диван купить»).
    """
    choice("what", what, WHAT)
    if what == "chars":
        return changed(data, lambda phrase: phrase[::-1], "reverse", column, inplace)
    return changed(data, lambda phrase: " ".join(reversed(split_words(phrase))), "reverse", column, inplace)


def sort_words(
    data: pd.Series | pd.DataFrame, *, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """The words of the phrase sorted by their character codes, joined by one space: digits, then latin capitals,
    latin small letters, cyrillic capitals, cyrillic small letters; «Ё» before «А» and «ё» after «я»."""
    return changed(data, lambda phrase: " ".join(sorted(split_words(phrase))), "sort_words", column, inplace)
