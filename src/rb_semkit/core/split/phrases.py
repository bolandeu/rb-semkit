"""split_text: a cell of prose becomes the phrases between its punctuation marks, one row per phrase.

The words are those of `text.words` (a hyphen or an apostrophe inside a word, a point or a comma inside a number stay);
a phrase ends at the punctuation between two words but a dash («хранения — это») and the point of an abbreviation
(«г. Краснознаменск»), as `text.words.ends_phrase` says.
"""

from __future__ import annotations

import pandas as pd

from ..frame import Frame, map_unique
from ..text.words import ends_phrase, pieces


def _phrases(cell: str) -> list[str]:
    return [" ".join(words) for words in pieces(cell, ends_phrase)]


def split_text(data: pd.Series | pd.DataFrame, *, column: str | None = None) -> pd.Series | pd.DataFrame:
    """Every cell cut into phrases at sentence ends and clause punctuation; one row per phrase, none for an empty cell.

    The punctuation is dropped, whitespace collapsed, case kept. A hyphen or apostrophe inside a word and a point or
    comma between digits stay. A Series gives a Series; a DataFrame with `column` gives a DataFrame whose rows are the
    phrases: `column` holds the phrase, the other columns repeat the source row. Each row keeps the index of its source.
    """
    frame = Frame(data, column)
    pieces_of = map_unique(frame.phrases, _phrases)
    if isinstance(data, pd.Series):
        return pieces_of.explode().dropna().rename(data.name)
    table = data.assign(**{str(column): pieces_of}).explode(str(column))
    return table.dropna(subset=[str(column)])
