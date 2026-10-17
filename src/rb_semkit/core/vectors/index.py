"""The vector index: the nearest phrases of each phrase by the cosine of their vectors.

Up to the exact-search limit of the settings (about 300k phrases) every pair is compared; above it an HNSW graph
finds the neighbours, approximately. The graph is built on one thread, so the same vectors give the same index, and a
run gives the same neighbours as the run before it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from . import registry

IndexKind = Literal["exact", "hnsw"]


@dataclass(frozen=True)
class Neighbours:
    """The nearest phrases of each phrase, the nearest first, without the phrase itself.

    ids: one row per phrase, the rows of the neighbours, -1 where there are fewer; similarities: their cosines.
    """

    kind: IndexKind
    ids: np.ndarray
    similarities: np.ndarray


def index_kind(count: int) -> IndexKind:
    """The index for `count` phrases."""
    return "exact" if count <= registry.bundled().index.exact_limit else "hnsw"


def neighbours(vectors: np.ndarray) -> Neighbours:
    """The nearest phrases of each row of `vectors` (float32 rows of length 1), as many as the settings name."""
    import faiss

    settings = registry.bundled().index
    count, dimensions = vectors.shape
    kind = index_kind(count)
    if kind == "exact":
        index = faiss.IndexFlatIP(dimensions)
        index.add(vectors)
    else:
        index = faiss.IndexHNSWFlat(dimensions, settings.hnsw_links, faiss.METRIC_INNER_PRODUCT)
        index.hnsw.efConstruction = settings.hnsw_build
        index.hnsw.efSearch = settings.hnsw_search
        threads = faiss.omp_get_max_threads()
        faiss.omp_set_num_threads(1)  # one thread: the same graph every run
        try:
            index.add(vectors)
        finally:
            faiss.omp_set_num_threads(threads)
    similarities, ids = index.search(vectors, min(settings.neighbours + 1, count))
    return Neighbours(kind, *_without_self(ids, similarities))


def _without_self(ids: np.ndarray, similarities: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The neighbours without the row itself, wherever the search put it (an equal vector may come first); a row the
    search did not find among its own neighbours loses its farthest one."""
    count, found = ids.shape
    itself = ids == np.arange(count)[:, None]
    dropped = np.where(itself.any(axis=1), itself.argmax(axis=1), found - 1)
    kept = np.ones(ids.shape, dtype=bool)
    kept[np.arange(count), dropped] = False
    return ids[kept].reshape(count, found - 1), similarities[kept].reshape(count, found - 1)
