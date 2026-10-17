"""What the three comparisons share: the checked inputs, the counts of a text and the verdict against a median."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from ..analysis.frequency import ngrams
from ..errors import InvalidArguments
from ..frame import Frame
from ..normalize import norm_phrase
from ..split import split_text
from ..text.base import split_words
from ..text.words import has_lemma

DECIMALS = 4


def checked_number(value: object, name: str, *, upper: float = math.inf) -> float:
    """`value` as a number from 0 to `upper`; anything else raises InvalidArguments naming `name`."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= upper:
        limit = "0 or more" if upper == math.inf else f"from 0 to {upper:g}"
        raise InvalidArguments(f"{name}={value!r}; allowed: a number {limit}.")
    return float(value)


def checked_text(mine: object) -> str:
    if not isinstance(mine, str):
        raise InvalidArguments(f"mine is a {type(mine).__name__}; allowed: a text (a str, a cell of a table).")
    return mine


def texts_of(data: pd.Series | pd.DataFrame | list[str] | tuple[str, ...], column: str | None, name: str) -> list[str]:
    """The texts one per row, in order; a list is a Series of texts. No text at all raises InvalidArguments."""
    series = pd.Series(list(data), dtype=object) if isinstance(data, (list, tuple)) else data
    if len(series) == 0:
        raise InvalidArguments(f"{name}: no texts; allowed: one text or more.")
    return Frame(series, column).phrases.tolist()


def _lemma_words(phrase: str) -> str:
    return " ".join(word for word in split_words(phrase) if has_lemma(norm_phrase(word)))


class TextCounts:
    """The grams of one text with their counts, and its words (stopwords included), as the n-grams count them.

    With `lemmas`, a word without a lemma («г», «руб»: `text.words.has_lemma`) is a word of the text but in no gram.
    """

    def __init__(self, text: str, *, n: int, lemmas: bool, stopwords: bool) -> None:
        phrases = split_text(pd.Series([text], dtype=object))
        self.words = sum(len(split_words(phrase)) for phrase in phrases)
        if lemmas:
            phrases = phrases.map(_lemma_words)
            phrases = phrases[phrases != ""]
        if phrases.empty:
            self.counts = pd.Series(dtype="int64")
        else:
            table = ngrams(phrases, n, lemmas=lemmas, stopwords=stopwords)
            self.counts = table.set_index("ngram")["count"]

    @property
    def density(self) -> pd.Series:
        """The count of each gram / the words of the text; 0 for a text without words."""
        return self.counts / self.words if self.words else self.counts.astype("float64")


def verdicts(mine: pd.Series, median: pd.Series, tolerance: float) -> pd.Series:
    """'below', 'within' or 'above': `mine` against median x (1 ± tolerance); a median of 0 is within only for 0."""
    zero = median == 0
    return pd.Series(
        np.select(
            [zero & (mine == 0), zero, mine < median * (1 - tolerance), mine > median * (1 + tolerance)],
            ["within", "above", "below", "above"],
            default="within",
        ),
        index=mine.index,
    )
