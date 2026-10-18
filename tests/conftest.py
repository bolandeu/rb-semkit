"""Shared fixtures: a test sees only the word lists it sets up, never the ones of the machine it runs on; the steps by
meaning get a small deterministic encoder in place of the real models, and the step by words a small thesaurus and
small word vectors, so no test downloads or loads a real one.

A test marked `real_encoder` gets the models as semkit opens them: the vectors extra, the cache, the model files.
"""

from __future__ import annotations

import zlib
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pytest

from rb_semkit.core.vectors import encoder
from rb_semkit.core.vectors.registry import Model
from rb_semkit.core.word_vectors.navec import WordVectors
from rb_semkit.core.word_vectors.thesaurus import Thesaurus
from rb_semkit.steps import word_vectors

WORD_DIMENSIONS = 64


class WordEncoder:
    """The test encoder: a phrase is the sum of its words, each word a fixed random vector (seeded by the word).

    Phrases of the same words get the same vector, phrases that share words close ones, phrases of other words far
    ones; the same phrase gives the same vector in every run.
    """

    def encode(self, phrases: Sequence[str]) -> np.ndarray:
        vectors = np.zeros((len(phrases), WORD_DIMENSIONS), dtype=np.float32)
        for row, phrase in enumerate(phrases):
            for word in phrase.lower().split():
                vectors[row] += np.random.default_rng(zlib.crc32(word.encode())).standard_normal(WORD_DIMENSIONS)
        lengths = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.where(lengths == 0, 1, lengths)


@pytest.fixture(autouse=True)
def _no_machine_word_lists(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SEMKIT_LISTS", raising=False)


@pytest.fixture(autouse=True)
def _test_encoder(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    if request.node.get_closest_marker("real_encoder"):
        return

    def opened(model: Model, start: Path) -> WordEncoder:
        return WordEncoder()

    monkeypatch.setattr(encoder, "encoder_for", opened)


@pytest.fixture(autouse=True)
def _test_word_data(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """A thesaurus where диван and чехол are synonyms, and so are растаможка and таможенное оформление, and word vectors where they are close."""
    if request.node.get_closest_marker("real_encoder"):
        return
    words = ["<unk>", "<pad>", "диван", "чехол"]
    codes = np.array([[[0, 0], [0, 0], [1, 0], [0.8, 0.6]]], dtype=np.float32)
    vectors = WordVectors(words, np.arange(len(words), dtype=np.uint8).reshape(-1, 1), codes)
    monkeypatch.setattr(word_vectors, "open_thesaurus", lambda start: Thesaurus(
            [
                ("1", "ДИВАН", "ДИВАН"),
                ("1", "ЧЕХОЛ", "ЧЕХОЛ"),
                ("2", "РАСТАМОЖКА", "РАСТАМОЖКА"),
                ("2", "ТАМОЖЕННОЕ ОФОРМЛЕНИЕ", "ТАМОЖЕННЫЙ ОФОРМЛЕНИЕ"),
            ]
        ))
    monkeypatch.setattr(word_vectors, "open_word_vectors", lambda start: vectors)
