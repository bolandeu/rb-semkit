"""N-grams and bigrams with counts, as the add-in counts them: one occurrence of a gram is one count.

A phrase becomes its words (those of `text.words`: no punctuation at the edges of a word; case and ё folded, stopwords
dropped on request, then lemmas on request); a shape turns the words into grams; the grams of all phrases are counted,
and summed by the weight of their phrase.

`bundled_stopwords` gives the stopword list of these steps to other areas (text_stats uses it for water and nausea);
`word_keys` gives them the word -> key step (the corpus area uses it).
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
from ..text.base import bundled_list, split_words
from ..text.words import text_words
from .weights import weights_of

MAX_FORMS = 5  # the spellings of a gram longer than one word


def bundled_stopwords() -> frozenset[str]:
    """The bundled stopwords, folded as `norm_phrase` folds a word."""
    return datastore.once("analysis_stopwords", lambda: frozenset(norm_phrase(w) for w in bundled_list("stopwords")))


def checked_n(n: int) -> int:
    """The gram size `n`, or InvalidArguments; other areas use it, like `bundled_stopwords`."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise InvalidArguments(f"n={n!r}; allowed: an integer of 1 or more.")
    return n


Token = tuple[str, bool, str]  # the key of a word, whether it counts (False: a stopword to drop), its spelling
Gram = tuple[str, str]  # the gram, and the spelling of its words


def word_keys(phrases: pd.Series, *, lemmatizer: Lemmatizer | None, stopwords: bool) -> dict[str, Token]:
    """Each distinct word of `phrases` as its key (other areas use it, like `bundled_stopwords`); a stopword to drop (`stopwords=False`) is not lemmatized."""
    dropped = frozenset() if stopwords else bundled_stopwords()
    keys = {}
    for word in {word for phrase in phrases.unique() for word in split_words(phrase)}:
        key = norm_phrase(word)
        counts = bool(key) and key not in dropped
        keys[word] = (lemmatizer.lemma(key) if counts and lemmatizer is not None else key, counts, key)
    return keys


def _runs(n: int) -> Callable[[list[Token]], list[Gram]]:
    """Runs of `n` counting words; the dropped stopwords between them stay inside the gram."""

    def shape(tokens: list[Token]) -> list[Gram]:
        counting = [i for i, (_, counts, _) in enumerate(tokens) if counts]
        runs = (tokens[counting[i] : counting[i + n - 1] + 1] for i in range(len(counting) - n + 1))
        return [
            (" ".join(key for key, _, _ in run if key), " ".join(form for key, _, form in run if key)) for run in runs
        ]

    return shape


def _pairs(tokens: list[Token]) -> list[Gram]:
    words = sorted({key: form for key, counts, form in tokens if counts}.items())
    return [
        (f"{first}+{second}", f"{form_first}+{form_second}")
        for (first, form_first), (second, form_second) in combinations(words, 2)
    ]


def _docs(table: pd.DataFrame) -> pd.Series:
    """For each gram the number of distinct source rows that hold it."""
    return table[["ngram", "row"]].drop_duplicates().groupby("ngram", sort=False).size()


def _forms(table: pd.DataFrame, limit: int | None) -> pd.Series:
    """For each gram its spellings, most frequent first, joined by ', '; `limit` of them at most."""
    spellings = table.groupby(["ngram", "form"], sort=False).agg(met=("form", "size")).reset_index()
    spellings = spellings.sort_values(["ngram", "met", "form"], ascending=[True, False, True])
    if limit is not None:
        spellings = spellings.groupby("ngram", sort=False).head(limit)
    return spellings.groupby("ngram", sort=False)["form"].agg(", ".join)


def _tally(
    data: pd.Series | pd.DataFrame,
    shape: Callable[[list[Token]], list[Gram]],
    *,
    lemmatizer: Lemmatizer | None,
    stopwords: bool,
    weight: str | None,
    column: str | None,
    forms_limit: int | None,
) -> pd.DataFrame:
    frame = Frame(data, column)
    weights = weights_of(frame, weight)
    phrases = map_unique(frame.phrases, lambda phrase: " ".join(text_words(phrase)))
    keys = word_keys(phrases, lemmatizer=lemmatizer, stopwords=stopwords)
    grams = map_unique(phrases, lambda phrase: shape([keys[word] for word in split_words(phrase)])).tolist()
    lengths = [len(row) for row in grams]
    flat = list(chain.from_iterable(grams))
    table = pd.DataFrame(
        {
            "ngram": [gram for gram, _ in flat],
            "form": [form for _, form in flat],
            "row": np.repeat(pd.factorize(phrases.index)[0], lengths),
        }
    )
    totals = {"count": ("ngram", "size")}
    if weights is not None:
        table["sum"] = np.repeat(weights.to_numpy(), lengths)
        totals["sum"] = ("sum", "sum")
    counted = table.groupby("ngram", sort=False).agg(**totals).reset_index()
    counted.insert(2, "docs", counted["ngram"].map(_docs(table)).astype("int64"))
    if lemmatizer is not None:
        counted["forms"] = counted["ngram"].map(_forms(table, forms_limit))
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
    """Every run of `n` words over all phrases, counted: a table ngram, count, docs, sum and forms.

    count: occurrences. docs: in how many distinct index values (texts, when `sk.split_text` cut the phrases) the gram
    occurs at least once; the add-in has no such column, it is a semkit addition, so the conformance cases compare
    count and sum only. sum: with `weight`. forms: with `lemmas`, the word forms met for the gram, most frequent first,
    joined by ', ' («диваны, диван»); for a gram of several words its distinct spellings, at most 5.

    Sorted by count, biggest first, then by ngram. Words are compared by case and ё.
    lemmas: count lemmas of the words («диваны» is «диван»), by `lemmatizer`.
    stopwords: False makes the runs of words that are no stopwords; a stopword between two of them stays inside the
    gram («купить диван в москве» gives «купить диван» and «диван в москве»), as «Биграмм без учета стоп-слов»;
    stopwords are found in any case (ADR 0005).
    weight: a numeric column of the table; `sum` adds its value once per occurrence.
    """
    return _tally(
        data,
        _runs(checked_n(n)),
        lemmatizer=lemmatizer if lemmas else None,
        stopwords=stopwords,
        weight=weight,
        column=column,
        forms_limit=None if n == 1 else MAX_FORMS,
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
        data,
        _pairs,
        lemmatizer=lemmatizer if lemmas else None,
        stopwords=stopwords,
        weight=weight,
        column=column,
        forms_limit=MAX_FORMS,
    )
