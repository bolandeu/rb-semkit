"""N-grams and bigrams with counts, as the add-in counts them: one occurrence of a gram is one count.

A phrase becomes its words (case and ё folded, stopwords dropped on request, then lemmas on request); a shape turns
the words into grams; the grams of all phrases are counted, and summed by the weight of their phrase.
"""

from __future__ import annotations

from collections.abc import Callable
from itertools import chain, combinations

import numpy as np
import pandas as pd

from .. import datastore
from ..errors import InvalidArguments
from ..frame import Frame, map_unique
from ..morph import Lemmatizer
from ..morph.functions import BUNDLED
from ..normalize import norm_phrase
from ..text.base import split_words
from .weights import weights_of

LISTS = "lists/lists.json"
COLUMNS = ["ngram", "count"]


def _stopwords() -> frozenset[str]:
    return datastore.once(
        "analysis_stopwords", lambda: frozenset(norm_phrase(w) for w in datastore.table(LISTS)["stopwords"])
    )


def _checked_n(n: int) -> int:
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise InvalidArguments(f"n={n!r}; allowed: an integer of 1 or more.")
    return n


def _word_keys(phrases: pd.Series, *, lemmatizer: Lemmatizer | None, stopwords: bool) -> dict[str, str]:
    """Each distinct word of `phrases` as its key; "" for a word that drops out (a stopword, an empty key)."""
    dropped = frozenset() if stopwords else _stopwords()
    keys = {}
    for word in {word for phrase in phrases.unique() for word in split_words(phrase)}:
        key = norm_phrase(word)
        if key in dropped:
            key = ""
        elif key and lemmatizer is not None:
            key = lemmatizer.lemma(key)
        keys[word] = key
    return keys


def _runs(n: int) -> Callable[[list[str]], list[str]]:
    return lambda words: [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


def _pairs(words: list[str]) -> list[str]:
    return [f"{first}+{second}" for first, second in combinations(sorted(set(words)), 2)]


def _tally(
    data: pd.Series | pd.DataFrame,
    shape: Callable[[list[str]], list[str]],
    *,
    lemmatizer: Lemmatizer | None,
    stopwords: bool,
    weight: str | None,
    column: str | None,
) -> pd.DataFrame:
    frame = Frame(data, column)
    weights = weights_of(frame, weight)
    phrases = frame.phrases
    keys = _word_keys(phrases, lemmatizer=lemmatizer, stopwords=stopwords)
    grams = map_unique(phrases, lambda phrase: shape([keys[w] for w in split_words(phrase) if keys[w]])).tolist()
    table = pd.DataFrame({"ngram": list(chain.from_iterable(grams))})
    totals = {"count": ("ngram", "size")}
    if weights is not None:
        table["sum"] = np.repeat(weights.to_numpy(), [len(row) for row in grams])
        totals["sum"] = ("sum", "sum")
    counted = table.groupby("ngram", sort=False).agg(**totals).reset_index()
    return counted.sort_values(["count", "ngram"], ascending=[False, True]).reset_index(drop=True)


def ngrams(
    data: pd.Series | pd.DataFrame,
    n: int = 1,
    *,
    lemmas: bool = False,
    stopwords: bool = True,
    weight: str | None = None,
    lemmatizer: Lemmatizer = BUNDLED,
    column: str | None = None,
) -> pd.DataFrame:
    """Every run of `n` words over all phrases, counted: a table ngram, count (occurrences) and sum (with `weight`).

    Sorted by count, biggest first, then by ngram. Words are compared by case and ё.
    lemmas: count lemmas of the words («диваны» is «диван»), by `lemmatizer`.
    stopwords: False drops the stopwords before the runs are made (before the lemmas too).
    weight: a numeric column of the table; `sum` adds its value once per occurrence.
    """
    return _tally(
        data,
        _runs(_checked_n(n)),
        lemmatizer=lemmatizer if lemmas else None,
        stopwords=stopwords,
        weight=weight,
        column=column,
    )


def bigrams(
    data: pd.Series | pd.DataFrame,
    *,
    lemmas: bool = False,
    stopwords: bool = True,
    weight: str | None = None,
    lemmatizer: Lemmatizer = BUNDLED,
    column: str | None = None,
) -> pd.DataFrame:
    """Pairs of words of a phrase in any order, counted: «купить диван» and «диван купить» both give «диван+купить».

    Per phrase the words are sorted and a repeated word counts once. The table and its arguments are those of `ngrams`.
    """
    return _tally(
        data, _pairs, lemmatizer=lemmatizer if lemmas else None, stopwords=stopwords, weight=weight, column=column
    )
