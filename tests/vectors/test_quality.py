"""The default encoder on 200 labelled phrase pairs (same intent or not, checked by the Human): the cosine ranks the
pairs well, and the default threshold of the model is where the F1 of «same intent» is best.

The test runs the real model from the cache; without it, it is skipped with the command that pulls it.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from rb_semkit.core.errors import CliError
from rb_semkit.core.vectors import encoder, registry

pytestmark = pytest.mark.real_encoder

PAIRS = Path(__file__).parent / "fixtures" / "phrase_pairs.tsv"
MODEL = "e5-small"


@pytest.fixture(scope="module")
def similarities() -> tuple[np.ndarray, np.ndarray]:
    """The cosine of each pair and its label (1: same intent)."""
    try:
        encode = encoder.encoder_for(registry.model(MODEL), Path.cwd()).encode
    except CliError as error:
        pytest.skip(f"{MODEL} is not in the cache ({error.code}): run 'semkit models pull {MODEL}'.")
    pairs = pd.read_csv(PAIRS, sep="\t", comment="#")
    first, second = encode(pairs["phrase_a"].tolist()), encode(pairs["phrase_b"].tolist())
    return (first * second).sum(axis=1), pairs["label"].to_numpy()


def _roc_auc(scores: np.ndarray, labels: np.ndarray) -> float:
    """The share of (same, different) pairs of pairs that the cosine orders right; a tie counts a half."""
    same, different = scores[labels == 1][:, None], scores[labels == 0][None, :]
    return float(((same > different).sum() + 0.5 * (same == different).sum()) / (same.size * different.size))


def _f1(found: np.ndarray, labels: np.ndarray) -> float:
    right = (found & (labels == 1)).sum()
    return 2 * right / (found.sum() + (labels == 1).sum())


def test_the_cosine_separates_same_and_different_intents(similarities: tuple[np.ndarray, np.ndarray]) -> None:
    scores, labels = similarities

    assert _roc_auc(scores, labels) >= 0.93


def test_the_default_threshold_is_the_best_f1_threshold(similarities: tuple[np.ndarray, np.ndarray]) -> None:
    scores, labels = similarities
    best = max(np.unique(scores), key=lambda threshold: _f1(scores >= threshold, labels))

    assert abs(registry.model(MODEL).threshold - best) <= 0.01
