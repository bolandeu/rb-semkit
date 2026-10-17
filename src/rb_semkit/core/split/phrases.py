"""split_text: a cell of prose becomes the phrases between its punctuation marks, one row per phrase.

A punctuation character (the class of `sk.chars("punctuation")`) separates phrases, with two exceptions that keep a
word whole: a hyphen or an apostrophe between two letters or digits («Wi-Fi», «кто-то», «it's»), and a point or comma
between two digits («2.5», «2,5»). Any other dot is a separator, so «т.д.» splits too; this is accepted.
"""

from __future__ import annotations

import re
from functools import cache

import pandas as pd

from ..frame import Frame, map_unique
from ..text.base import collapse
from ..text.matchers.chars import KINDS
from ..text.matchers.classes import DIGITS, cased


@cache
def _separator() -> re.Pattern[str]:
    """One punctuation character that is not inside a word."""
    kept = KINDS["punctuation"].body()
    word = cased() + DIGITS
    return re.compile(rf"(?!(?<=[{word}])['’-](?=[{word}])|(?<=[{DIGITS}])[.,](?=[{DIGITS}]))[^{kept}]")


def _phrases(cell: str) -> list[str]:
    return [phrase for phrase in map(collapse, _separator().split(cell)) if phrase]


def split_text(data: pd.Series | pd.DataFrame, *, column: str | None = None) -> pd.Series | pd.DataFrame:
    """Every cell cut into phrases at sentence ends and clause punctuation; one row per phrase, none for an empty cell.

    The punctuation is dropped, whitespace collapsed, case kept. A hyphen or apostrophe inside a word and a point or
    comma between digits stay. A Series gives a Series; a DataFrame with `column` gives a DataFrame whose rows are the
    phrases: `column` holds the phrase, the other columns repeat the source row. Each row keeps the index of its source.
    """
    frame = Frame(data, column)
    pieces = map_unique(frame.phrases, _phrases)
    if isinstance(data, pd.Series):
        return pieces.explode().dropna().rename(data.name)
    table = data.assign(**{str(column): pieces}).explode(str(column))
    return table.dropna(subset=[str(column)])
