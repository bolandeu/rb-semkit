"""The vectors the relevance functions share: each cell of a column as a phrase vector, and the nearest rows."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..vectors.encoder import Encoder

DIGITS = 4


def encoded(encoder: Encoder, texts: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """The vector of each cell (a row of zeros for an empty cell), and whether the cell holds a phrase."""
    cells = texts.fillna("").astype(str)
    unique = pd.Index(pd.unique(cells[cells != ""]))
    found = cells.to_numpy() != ""
    vectors = np.zeros((len(cells), 0), dtype=np.float32)
    if len(unique):
        by_phrase = np.ascontiguousarray(encoder.encode(list(unique)), dtype=np.float32)
        vectors = np.zeros((len(cells), by_phrase.shape[1]), dtype=np.float32)
        vectors[found] = by_phrase[unique.get_indexer(cells[found])]
    return vectors, found


def nearest(vectors: np.ndarray, targets: np.ndarray, count: int) -> tuple[np.ndarray, np.ndarray]:
    """The rows of `targets` nearest each row of `vectors` by the cosine, the nearest first, and their similarities.

    A row beyond the number of targets is -1, its similarity 0.
    """
    import faiss

    index = faiss.IndexFlatIP(targets.shape[1])
    index.add(targets)
    similarities, ids = index.search(vectors, count)
    return ids, np.where(ids >= 0, similarities, 0).astype(np.float32)
