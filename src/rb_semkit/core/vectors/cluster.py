"""cluster_meaning: phrases grouped by the similarity of their phrase vectors, with no SERP.

`frequencies` gives the frequency of each distinct phrase; `ad_groups` reuses it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import index
from .encoder import Encoder, normalized

DIGITS = 4


def cluster_meaning(
    data: pd.Series, *, encoder: Encoder, threshold: float, freq: pd.Series | None = None
) -> pd.DataFrame:
    """Clusters of phrases by meaning: phrases of close vectors share a cluster; every phrase gets one.

    threshold: the similarity from 0 to 1 a phrase needs to the phrase that starts a cluster to join it.
    freq: the frequency of each phrase, by the index of `data`; the cluster is named after its most frequent phrase.
    Without it, after the phrase nearest the centre of the cluster (the mean of its vectors).

    The phrase with the most neighbours (phrases at the threshold or above) starts the first cluster and takes its
    neighbours; of the phrases left, the one with the most neighbours starts the next, and so on; a tie goes to the
    first row. A phrase without neighbours is a cluster of one. Equal phrases are one phrase. The clusters are numbered
    in the order of their first rows. The columns: cluster, cluster_name and similarity (of the phrase to the name of
    its cluster, 4 places); an empty cell gets none. The table tells the index it searched in `attrs["index"]`.
    """
    texts = data.fillna("").astype(str)
    phrases = pd.Index(pd.unique(texts[texts != ""]))
    vectors = np.ascontiguousarray(encoder.encode(list(phrases)), dtype=np.float32)
    labels, kind = _clusters(vectors, threshold) if len(phrases) else (np.zeros(0, dtype=np.int64), index.index_kind(0))
    names = _names(vectors, labels, None if freq is None else frequencies(texts, freq, phrases))
    rows = phrases.get_indexer(texts)
    found = rows >= 0
    name_rows = names[labels[rows[found]]]
    similarity = (vectors[rows[found]] * vectors[name_rows]).sum(axis=1).astype(float).round(DIGITS)
    table = pd.DataFrame(
        {
            "cluster": pd.Series(pd.NA, index=data.index, dtype="Int64"),
            "cluster_name": pd.Series("", index=data.index, dtype=object),
            "similarity": pd.Series(np.nan, index=data.index, dtype=float),
        }
    )
    table.loc[found, "cluster"] = labels[rows[found]] + 1
    table.loc[found, "cluster_name"] = phrases[name_rows].to_numpy()
    table.loc[found, "similarity"] = similarity
    table.attrs["index"] = kind
    return table


def _clusters(vectors: np.ndarray, threshold: float) -> tuple[np.ndarray, index.IndexKind]:
    """The cluster of each phrase (0 for the cluster of the first row), and the index searched."""
    found = index.neighbours(vectors)
    close = (found.ids >= 0) & (found.similarities >= threshold)
    starts = np.full(len(vectors), -1, dtype=np.int64)  # the row that starts the cluster of each phrase
    for row in np.argsort(-close.sum(axis=1), kind="stable"):
        if starts[row] < 0:
            starts[row] = row
            members = found.ids[row][close[row]]
            starts[members[starts[members] < 0]] = row
    first_rows = pd.Series(np.arange(len(vectors))).groupby(starts).min().sort_values()
    numbers = pd.Series(np.arange(len(first_rows)), index=first_rows.index)
    return numbers[starts].to_numpy(), found.kind


def frequencies(texts: pd.Series, freq: pd.Series, phrases: pd.Index) -> np.ndarray:
    """The frequency of each phrase: the sum over its rows."""
    given = pd.to_numeric(freq.reindex(texts.index), errors="coerce").fillna(0)
    return given.groupby(texts.to_numpy()).sum().reindex(phrases).to_numpy()


def _names(vectors: np.ndarray, labels: np.ndarray, frequencies: np.ndarray | None) -> np.ndarray:
    """The row of the phrase that names each cluster: the most frequent, else the nearest the centre; a tie, the first."""
    scores = frequencies
    if scores is None:
        centres = np.zeros((labels.max(initial=-1) + 1, vectors.shape[1]), dtype=np.float32)
        np.add.at(centres, labels, vectors)
        scores = (vectors * normalized(centres)[labels]).sum(axis=1)
    return pd.Series(scores).groupby(labels).idxmax().to_numpy()
