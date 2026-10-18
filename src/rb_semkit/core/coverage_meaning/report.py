"""coverage_meaning: for each core phrase, the best paragraph of a text by meaning, and whether it covers the phrase."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..relevance.page import PageEncoder
from ..relevance.vectors import DIGITS
from ..relevance.vectors import nearest as nearest_targets

YES, NO = "yes", "no"


def coverage_meaning(
    phrases: pd.Series,
    paragraphs: pd.DataFrame,
    *,
    encoder: PageEncoder,
    threshold: float,
    clusters: pd.Series | None = None,
) -> pd.DataFrame:
    """For each core phrase, the paragraph nearest it by meaning, and whether the text covers the phrase.

    paragraphs: the paragraphs of the text (a report of `split-paragraphs`: url, number, paragraph).
    threshold: the similarity from 0 to 1 from which a paragraph covers a phrase.
    clusters: the cluster of each phrase, by the index of `phrases`; a cluster is covered when any of its phrases is.

    The report has a row for each phrase, in its order and with its index: url and number (of the paragraph), the
    paragraph, similarity (4 places) and covered (yes or no); with clusters also cluster_covered. A phrase with no
    words, or a text with no paragraphs, gives an empty paragraph, no similarity and covered no.
    """
    vectors, has_words = encoder.encode(phrases)
    best, similarity = _best(vectors, paragraphs, encoder)
    matched = (best >= 0) & has_words
    picked = paragraphs.reset_index(drop=True).reindex(np.where(matched, best, -1))
    covered = pd.Series(matched & (similarity >= threshold), index=phrases.index)
    report = pd.DataFrame(
        {
            "url": picked["url"].fillna("").to_numpy(),
            "number": picked["number"].astype("Int64").to_numpy(),
            "paragraph": picked["paragraph"].fillna("").to_numpy(),
            "similarity": np.where(matched, similarity.astype(float).round(DIGITS), np.nan),
            "covered": np.where(covered, YES, NO),
        },
        index=phrases.index,
    )
    if clusters is not None:
        report["cluster_covered"] = np.where(covered.groupby(clusters).transform("any").fillna(covered), YES, NO)
    return report


def _best(vectors: np.ndarray, paragraphs: pd.DataFrame, encoder: PageEncoder) -> tuple[np.ndarray, np.ndarray]:
    """The row of the paragraph nearest each vector (-1 for none) and its similarity."""
    if paragraphs.empty:
        return np.full(len(vectors), -1), np.zeros(len(vectors), dtype=np.float32)
    targets, _ = encoder.encode(paragraphs["paragraph"])
    ids, similarities = nearest_targets(vectors, targets, 1)
    return ids[:, 0], similarities[:, 0]
