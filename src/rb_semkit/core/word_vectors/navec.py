"""The word vectors navec: the pack of natasha (a tar of vocab.bin, the words, and pq.bin, their vectors in product
quantization: each vector is the parts of its code in a table of centroids).

The vectors are opened a block at a time, so the 500 000 words never stand in memory as numbers at once.
"""

from __future__ import annotations

import gzip
import tarfile
from pathlib import Path
from typing import IO

import numpy as np

from ..vectors import cache, registry
from ..vectors.encoder import normalized

NAME = "navec"
VOCAB, PQ = "vocab.bin", "pq.bin"
SPECIAL = ("<unk>", "<pad>")
UINT32 = 4


class WordVectors:
    def __init__(self, words: list[str], indexes: np.ndarray, codes: np.ndarray) -> None:
        """words: the vocabulary. indexes: the centroid of each part of each word. codes: the centroids of each part."""
        self.words, self.indexes, self.codes = words, indexes, codes
        self.rows = {word: row for row, word in enumerate(words)}
        self.parts = np.arange(codes.shape[0])

    def __contains__(self, word: str) -> bool:
        return word in self.rows

    def _vectors(self, rows: np.ndarray) -> np.ndarray:
        """The vectors of length 1 of the words in `rows`."""
        return normalized(self.codes[self.parts, self.indexes[rows]].reshape(len(rows), -1))

    def neighbours(
        self, words: list[str], among: frozenset[str] | None, count: int
    ) -> dict[str, list[tuple[str, float]]]:
        """For each word of `words` in the vocabulary, its `count` nearest words of `among` (the whole vocabulary
        when None) with the cosine, the nearest first, itself and the special tokens left out."""
        queries = [word for word in words if word in self]
        asked = np.array([self.rows[word] for word in queries], dtype=np.int64)
        candidates = self._candidates(among)
        found = self._search(self._vectors(asked), asked, candidates, count) if len(asked) else []
        return {
            word: [(self.words[row], score) for score, row in zip(scores, rows, strict=True) if score > -np.inf]
            for word, (scores, rows) in zip(queries, found, strict=True)
        }

    def _candidates(self, among: frozenset[str] | None) -> np.ndarray:
        """The rows of the words `among` (the whole vocabulary when None) without the special tokens."""
        if among is None:
            rows = np.arange(len(self.words))
        else:
            rows = np.array(sorted(self.rows[word] for word in among if word in self), dtype=np.int64)
        return rows[~np.isin(rows, [self.rows[word] for word in SPECIAL if word in self])]

    def _search(
        self, queries: np.ndarray, asked: np.ndarray, candidates: np.ndarray, count: int
    ) -> list[tuple[np.ndarray, np.ndarray]]:
        """The best `count` candidates of each query: their cosines and rows, the best first."""
        best_scores = np.full((0, len(queries)), -np.inf, dtype=np.float32)
        best_rows = np.zeros((0, len(queries)), dtype=np.int64)
        block = registry.bundled().words.block
        for start in range(0, len(candidates), block):
            rows = candidates[start : start + block]
            scores = self._vectors(rows) @ queries.T
            scores[rows[:, None] == asked[None, :]] = -np.inf
            best_scores = np.vstack([best_scores, scores])
            best_rows = np.vstack([best_rows, np.broadcast_to(rows[:, None], scores.shape)])
            if len(best_scores) > count:
                kept = np.argpartition(-best_scores, count - 1, axis=0)[:count]
                best_scores = np.take_along_axis(best_scores, kept, axis=0)
                best_rows = np.take_along_axis(best_rows, kept, axis=0)
        return [_sorted(best_scores[:, query], best_rows[:, query]) for query in range(len(queries))]


def _sorted(scores: np.ndarray, rows: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The scores from the best, a tie by the row."""
    order = np.lexsort((rows, -scores))
    return scores[order], rows[order]


def _member(pack: tarfile.TarFile, name: str) -> IO[bytes]:
    """The file `name` of the pack."""
    found = pack.extractfile(name)
    if found is None:
        raise ValueError(f"{pack.name}: {name} is no file")  # a pack the checksum passed holds it
    return found


def load(path: Path) -> WordVectors:
    """The word vectors in the pack `path`."""
    with tarfile.open(path) as pack:
        with gzip.GzipFile(fileobj=_member(pack, VOCAB)) as vocab:
            size = int(np.frombuffer(vocab.read(UINT32), np.uint32)[0])
            vocab.read(UINT32 * size)  # the counts of the words
            words = vocab.read().decode("utf-8").splitlines()
        quantized = _member(pack, PQ)
        vectors, _, parts, centroids = (int(number) for number in np.frombuffer(quantized.read(4 * UINT32), np.uint32))
        indexes = np.frombuffer(quantized.read(vectors * parts), np.uint8).reshape(vectors, parts)
        codes = np.frombuffer(quantized.read(), np.float32).reshape(parts, centroids, -1)
    return WordVectors(words, indexes, codes)


def open_word_vectors(start: Path) -> WordVectors:
    """navec as pulled into the cache of the project at or above `start` (ModelNotPulled, with the command that pulls
    it)."""
    pulled = cache.pulled_model(registry.model(NAME), start)
    return load(pulled.folder / next(iter(pulled.model.files)))
