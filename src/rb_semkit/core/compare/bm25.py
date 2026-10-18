"""bm25: the Okapi BM25 score of each text for a query."""

from __future__ import annotations

import math
from functools import partial

import pandas as pd

from ..errors import InvalidArguments
from .shared import DECIMALS, TextCounts, checked_number, texts_of


def bm25(
    texts: pd.Series | pd.DataFrame | list[str],
    query: str,
    *,
    k1: float = 1.5,
    b: float = 0.75,
    column: str | None = None,
) -> pd.Series:
    """Okapi BM25 of each text for a query: one score per text, rounded to 4 decimals.

    Terms are the lemmas without stopwords, on both sides; a term repeated in the query counts once. A word without a
    lemma (a single letter, an abbreviation or a unit: «г», «руб», «см») is no term. The length of a text is its
    number of terms. idf = ln((N - df + 0.5) / (df + 0.5) + 1); N, df and the average
    length are taken over the given texts, so to rank my text among the competitors give all of them together.
    score = sum over the terms of idf x tf x (k1 + 1) / (tf + k1 x (1 - b + b x length / average length)).
    A text without a term of the query scores 0.
    texts: the texts, one per row.
    query: the query, a phrase.
    k1: how fast the score of a term saturates with its count (usually 1.2..2).
    b: how much the length of a text lowers the score, 0..1 (0: not at all).

    Example: {cli} read texts.csv bm25 "угловой диван" write -
    -> Диван угловой и кресло. Купить диван недорого., 0.8806; Кресло и диван, диван кожаный., 0.2784
    """
    if not isinstance(query, str):
        raise InvalidArguments(f"query is a {type(query).__name__}; allowed: a text (a str).")
    weight, saturation = checked_number(k1, "k1"), checked_number(b, "b", upper=1)
    index = texts.index if isinstance(texts, (pd.Series, pd.DataFrame)) else None
    counts_of = partial(TextCounts, n=1, lemmas=True, stopwords=False)
    terms = counts_of(query).counts.index
    counts = [counts_of(text).counts for text in texts_of(texts, column, "texts")]
    lengths = pd.Series([c.sum() for c in counts], dtype="float64")
    tf = pd.DataFrame([c.reindex(terms, fill_value=0) for c in counts]).reset_index(drop=True)
    df = (tf > 0).sum()
    idf = ((len(counts) - df + 0.5) / (df + 0.5) + 1).map(math.log)
    average = lengths.mean()
    norm = weight * (1 - saturation + saturation * lengths / average) if average else lengths
    scores = (tf.mul(weight + 1).div(tf.add(norm, axis=0)).fillna(0) * idf).sum(axis=1)
    return scores.round(DECIMALS).set_axis(index if index is not None else scores.index)
