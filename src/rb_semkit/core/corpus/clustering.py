"""Clustering of a semantic core by the frequency dictionary of its words."""

from __future__ import annotations

from collections import Counter

import pandas as pd

from ..analysis.frequency import word_keys
from ..frame import Frame
from ..text.base import split_words, whole_number

__all__ = ["cluster_by_frequency"]


def cluster_by_frequency(
    data: pd.Series | pd.DataFrame,
    *,
    threshold: int,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """The cluster of each phrase: its words that stand in at least a number of phrases of the core.

    threshold: the fewest phrases a word must stand in to name a cluster.

    A word counts once per phrase; words are compared in any case and with ё as е; stopwords are left out. The cluster
    lists its words in lower case, the most frequent first, then alphabetically, so «купить диван» and «диван купить»
    make one cluster. A phrase with no such word gets an empty cell.

    Example: {cli} read --text "купить диван" --text "диван купить" --text "купить кресло" cluster-by-frequency 2 write -
    -> купить диван, купить диван; диван купить, купить диван; купить кресло, купить
    """
    whole_number("threshold", threshold)
    frame = Frame(data, column, inplace)
    phrases = frame.phrases
    keys = word_keys(phrases, lemmatizer=None, stopwords=False)
    spelling: dict[str, str] = {}  # each key as its word first stands in the core, in lower case
    word_sets = {}
    for phrase in phrases.unique():
        counted = [(keys[word][0], word) for word in split_words(phrase) if keys[word][1]]
        for key, word in counted:
            spelling.setdefault(key, word.lower())
        word_sets[phrase] = frozenset(key for key, _ in counted)
    frequency: Counter[str] = Counter()
    for phrase, rows in phrases.value_counts(sort=False).items():
        frequency.update(dict.fromkeys(word_sets[phrase], rows))

    def cluster(words: frozenset[str]) -> str:
        kept = sorted((key for key in words if frequency[key] >= threshold), key=lambda key: (-frequency[key], key))
        return " ".join(spelling[key] for key in kept)

    return frame.put(phrases.map({phrase: cluster(words) for phrase, words in word_sets.items()}), "cluster")
