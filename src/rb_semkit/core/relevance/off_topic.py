"""off_topic: the distance of each phrase of a core from the centre of the core, or of seed phrases."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from ..errors import InvalidArguments
from ..vectors.encoder import Encoder, normalized
from .vectors import DIGITS, encoded


def off_topic(
    data: pd.Series,
    *,
    encoder: Encoder,
    threshold: float,
    freq: pd.Series | None = None,
    seed: Iterable[str] | None = None,
) -> pd.DataFrame:
    """The distance of each phrase of the core from the centre of the core, by meaning.

    threshold: the similarity from 0 to 1 a phrase needs to the centre to be on topic.
    freq: the frequency of each phrase, by the index of `data`; the centre weighs each phrase by it.
    seed: phrases that give the centre in place of the core.

    The centre is the mean of the phrase vectors of the core, each weighed by its frequency with freq and by 1 without
    it; with seed, the mean of the phrase vectors of the seed phrases. The columns: off_topic_score (1 minus the
    similarity of the phrase to the centre, from 0 to 1, 4 places) and off_topic (yes when the similarity is below the
    threshold, else no); an empty cell gets none. No row is dropped.

    Example: {cli} read --text "купить диван" off-topic write -
    -> купить диван, 0.0, no
    """
    vectors, found = encoded(encoder, data)
    if seed is None:
        weights = np.ones(len(data)) if freq is None else pd.to_numeric(freq, errors="coerce").fillna(0).to_numpy()
        centre = _centre(vectors[found], weights[found], "the frequencies of the phrases")
    else:
        seed_vectors, _ = encoded(encoder, pd.Series(list(seed), dtype=object))
        centre = _centre(seed_vectors, np.ones(len(seed_vectors)), "the seed phrases")
    similarity = (vectors @ centre).astype(float)
    table = pd.DataFrame(
        {
            "off_topic_score": pd.Series(np.where(found, np.clip(1 - similarity, 0, 1).round(DIGITS), np.nan)),
            "off_topic": pd.Series(np.where(found, np.where(similarity < threshold, "yes", "no"), "")),
        }
    )
    return table.set_axis(data.index)


def _centre(vectors: np.ndarray, weights: np.ndarray, what: str) -> np.ndarray:
    """The mean of the vectors weighed by `weights`, as a vector of length 1."""
    if not len(vectors) or weights.sum() <= 0:
        raise InvalidArguments(f"off-topic: {what} give no centre.", action="Name phrases with a frequency above 0.")
    return normalized(np.average(vectors, axis=0, weights=weights)[None])[0]
