"""The page vector: the vector of a text of any length, for the steps that compare texts (nearest, assign-pages).

A text longer than the input of the model is cut into pieces of a near-equal number of words that the model takes
whole, and its vector is the mean of the vectors of its pieces; a short text is one piece, as it is. When the table of
the texts has the columns title and h1, their vectors are added with the weights of the settings file
`data/vectors/page.toml`.
"""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .. import datastore
from ..vectors.encoder import Encoder, normalized
from .vectors import encoded

SETTINGS = "vectors/page.toml"
TEXT = "text"
HEADINGS = ("title", "h1")


@dataclass(frozen=True)
class PageSettings:
    tokens_per_word: float
    weights: Mapping[str, float]  # of the text and of each heading


def settings() -> PageSettings:
    """The settings of the page vector, read once."""
    return datastore.once(
        SETTINGS,
        lambda: PageSettings(**tomllib.loads((datastore.DATA_DIR / SETTINGS).read_text(encoding="utf-8"))),
    )


@dataclass(frozen=True)
class PageEncoder:
    """The encoder of texts of any length; `max_tokens` is the input of its model."""

    encoder: Encoder
    max_tokens: int

    def encode(self, texts: pd.Series, table: pd.DataFrame | None = None) -> tuple[np.ndarray, np.ndarray]:
        """The page vector of each text, and whether the text (or its title or h1) has words.

        table: the table of the texts; its columns title and h1, other than the column of the texts, weigh more.
        """
        weights = settings().weights
        parts = [_parts(texts, self._piece_words(), weights[TEXT])]
        for name in HEADINGS:
            if table is not None and name in table.columns and name != texts.name:
                parts.append(_parts(table[name], self._piece_words(), weights[name]))
        found = pd.concat(parts, ignore_index=True)
        vectors, _ = encoded(self.encoder, found[TEXT])
        sums = np.zeros((len(texts), vectors.shape[1]), dtype=np.float32)
        rows = found["row"].to_numpy(dtype=np.int64)
        np.add.at(sums, rows, vectors * found["weight"].to_numpy(dtype=np.float32)[:, None])
        has_words = np.zeros(len(texts), dtype=bool)
        has_words[rows] = True
        return normalized(sums), has_words

    def _piece_words(self) -> int:
        """The most words of a piece the model takes whole."""
        return max(1, int(self.max_tokens / settings().tokens_per_word))


def _parts(cells: pd.Series, size: int, weight: float) -> pd.DataFrame:
    """The pieces of each cell: the row of the cell, the weight of the piece (`weight` shared by the pieces of the
    cell) and its text; an empty cell has none."""
    rows, weights, pieces = [], [], []
    for row, text in enumerate(cells.fillna("").astype(str)):
        found = _pieces(text, size)
        if found:
            rows += [row] * len(found)
            weights += [weight / len(found)] * len(found)
            pieces += found
    return pd.DataFrame({"row": rows, "weight": weights, TEXT: pd.Series(pieces, dtype=object)})


def _pieces(text: str, size: int) -> list[str]:
    """The text as it is when it has up to `size` words; else its words in the fewest pieces of up to `size` words,
    of a near-equal number of words."""
    words = text.split()
    if len(words) <= size:
        return [text] if words else []
    count = -(-len(words) // size)
    return [" ".join(piece) for piece in np.array_split(np.array(words, dtype=object), count)]
