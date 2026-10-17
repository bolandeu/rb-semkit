"""What the comparisons share: the checked inputs, the counts of a text, the norm and the verdict against it."""

from __future__ import annotations

import math
from typing import Literal

import numpy as np
import pandas as pd

from ..analysis.frequency import ngrams
from ..errors import InvalidArguments
from ..frame import Frame
from ..normalize import norm_phrase
from ..split import split_text
from ..text.base import split_words
from ..text.words import has_lemma
from ..textstats.skip import Skip

DECIMALS = 4
Norm = Literal["mean", "median"]
NORMS = ("mean", "median")
NO_SKIP = Skip()


def checked_number(value: object, name: str, *, upper: float = math.inf) -> float:
    """`value` as a number from 0 to `upper`; anything else raises InvalidArguments naming `name`."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= upper:
        limit = "0 or more" if upper == math.inf else f"from 0 to {upper:g}"
        raise InvalidArguments(f"{name}={value!r}; allowed: a number {limit}.")
    return float(value)


def checked_norm(norm: object) -> Norm:
    """`norm` when it is «mean» or «median»; anything else raises InvalidArguments naming `norm`."""
    if norm not in NORMS:
        raise InvalidArguments(f"norm={norm!r}; allowed: 'mean' or 'median'.")
    return norm  # ty: ignore[invalid-return-type]


def whole(value: float) -> int | float:
    return int(value) if float(value).is_integer() else float(value)


def wholes_kept(numbers: pd.DataFrame, counted: np.ndarray) -> pd.DataFrame:
    """`numbers` with the rows marked in `counted` as integers where they are whole (a mean or a median may be a half)."""
    kept = numbers.astype(object)
    kept.loc[counted] = kept.loc[counted].map(whole)
    return kept


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
    The words of `skip` are in no gram and no count, the words total included.
    """

    def __init__(self, text: str, *, n: int, lemmas: bool, stopwords: bool, skip: Skip = NO_SKIP) -> None:
        phrases = split_text(pd.Series([text], dtype=object))
        if skip.active:
            phrases = phrases.map(lambda phrase: " ".join(skip.kept(split_words(phrase))))
            phrases = phrases[phrases != ""]
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


def verdicts(mine: pd.Series, norm: pd.Series, tolerance: float) -> pd.Series:
    """'below', 'within' or 'above': `mine` against norm x (1 ± tolerance); a norm of 0 is within only for 0."""
    zero = norm == 0
    return pd.Series(
        np.select(
            [zero & (mine == 0), zero, mine < norm * (1 - tolerance), mine > norm * (1 + tolerance)],
            ["within", "above", "below", "above"],
            default="within",
        ),
        index=mine.index,
    )
