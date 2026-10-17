"""classify_queries: each query of a search query report against the phrases of the core."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..errors import InvalidArguments
from ..vectors.encoder import Encoder
from .vectors import DIGITS, encoded, nearest


def classify_queries(data: pd.Series, *, against: pd.Series, encoder: Encoder, threshold: float) -> pd.DataFrame:
    """The nearest phrase of the core for each query of a search query report, by meaning.

    threshold: the similarity from 0 to 1 a query needs to its nearest phrase to be a target.
    against: the phrases of the core.

    The columns: nearest_phrase (the first of two equally near), similarity (4 places) and target (yes when the
    similarity is at the threshold or above, else no); an empty cell gets none. No row is dropped.
    """
    phrases = pd.Series(pd.unique(against.fillna("").astype(str).loc[lambda cells: cells != ""]), dtype=object)
    if phrases.empty:
        raise InvalidArguments("against: the core has no phrases.", action="Give a table with a column of phrases.")
    vectors, found = encoded(encoder, data)
    core, _ = encoded(encoder, phrases)
    ids, similarities = nearest(vectors, core, 1)
    similarity = similarities[:, 0].astype(float)
    table = pd.DataFrame(
        {
            "nearest_phrase": pd.Series(np.where(found, phrases.to_numpy()[ids[:, 0]], "")),
            "similarity": pd.Series(np.where(found, similarity.round(DIGITS), np.nan)),
            "target": pd.Series(np.where(found, np.where(similarity >= threshold, "yes", "no"), "")),
        }
    )
    return table.set_axis(data.index)
