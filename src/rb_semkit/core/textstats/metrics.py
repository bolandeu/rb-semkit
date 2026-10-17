"""The measures of a list of lemmas: lexical diversity (MTLD) and the fit to Zipf's law."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

MTLD_THRESHOLD = 0.72
ZIPF_MIN_LEMMAS = 5


def _factors(lemmas: Sequence[str]) -> float:
    """Factors of one reading: a factor each time the running type/token ratio falls to the threshold or below."""
    factors, seen, tokens = 0.0, set(), 0
    for lemma in lemmas:
        seen.add(lemma)
        tokens += 1
        if len(seen) / tokens <= MTLD_THRESHOLD:
            factors, seen, tokens = factors + 1, set(), 0
    if tokens:
        factors += (1 - len(seen) / tokens) / (1 - MTLD_THRESHOLD)
    return factors


def mtld(lemmas: Sequence[str]) -> float:
    """McCarthy and Jarvis (2010): lemmas / the mean of the forward and backward factors, 2 decimals; 0 under 2 lemmas."""
    if len(lemmas) < 2:
        return 0.0
    mean = (_factors(lemmas) + _factors(lemmas[::-1])) / 2
    return round(len(lemmas) / mean, 2) if mean else 0.0


def zipf(counts: Sequence[int]) -> float:
    """R² x 100 of the regression of log count on log rank (rank 1 is the biggest count), 1 decimal.

    0 under 5 distinct lemmas, and when all counts are equal (no slope to explain).
    """
    if len(counts) < ZIPF_MIN_LEMMAS:
        return 0.0
    log_count = np.log(sorted(counts, reverse=True))
    log_rank = np.log(np.arange(1, len(counts) + 1))
    if np.ptp(log_count) == 0:
        return 0.0
    return round(float(np.corrcoef(log_rank, log_count)[0, 1] ** 2) * 100, 1)
