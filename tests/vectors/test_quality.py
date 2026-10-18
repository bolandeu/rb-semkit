"""The default encoder on 200 labelled phrase pairs (same intent or not, checked by the Human): the cosine ranks the
pairs well, and the default threshold of the model is where the F1 of «same intent» is best. On the sofa core its
default cluster threshold keeps phrases of different intents in different clusters.

The test runs the real model from the cache; without it, it is skipped with the command that pulls it.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from rb_semkit.core.errors import CliError
from rb_semkit.core.vectors import encoder, registry
from rb_semkit.core.vectors.cluster import cluster_meaning

pytestmark = pytest.mark.real_encoder

PAIRS = Path(__file__).parent / "fixtures" / "phrase_pairs.tsv"
SOFA_CORE = Path(__file__).parents[1] / "e2e" / "fixtures" / "sofa_core.csv"
MODEL = "e5-small"


@pytest.fixture(scope="module")
def model_encoder() -> encoder.Encoder:
    """The encoder of the model from the cache."""
    try:
        return encoder.encoder_for(registry.model(MODEL), Path.cwd())
    except CliError as error:
        pytest.skip(f"{MODEL} is not in the cache ({error.code}): run 'semkit models pull {MODEL}'.")


@pytest.fixture(scope="module")
def similarities(model_encoder: encoder.Encoder) -> tuple[np.ndarray, np.ndarray]:
    """The cosine of each pair and its label (1: same intent)."""
    pairs = pd.read_csv(PAIRS, sep="\t", comment="#")
    encode = model_encoder.encode
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


def test_the_default_clusters_keep_intents_of_the_sofa_core_apart(model_encoder: encoder.Encoder) -> None:
    phrases = pd.read_csv(SOFA_CORE)["phrase"]
    threshold = registry.cluster_threshold(registry.model(MODEL), None)
    found = cluster_meaning(phrases, encoder=model_encoder, threshold=threshold)
    cluster = dict(zip(phrases, found["cluster"], strict=True))

    assert threshold == 0.975
    assert cluster["диван кровать купить в москве"] != cluster["диваны купить в москве"]  # joined at 0.97
