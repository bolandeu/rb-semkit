"""A core of 10 000 phrases over a text of 100 000 words runs in seconds."""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest

import rb_semkit as sk

LIMIT_SECONDS = 20


@pytest.mark.speed
def test_ten_thousand_phrases_over_a_hundred_thousand_words() -> None:
    rng = np.random.default_rng(1)
    vocabulary = [f"слово{i}" for i in range(3000)]
    text = " ".join(rng.choice(vocabulary, 100_000))
    core = pd.Series([" ".join(rng.choice(vocabulary, rng.integers(1, 4))) for _ in range(10_000)])

    started = time.perf_counter()
    table = sk.coverage(core, pd.Series([text]), mode="any_order")

    assert time.perf_counter() - started < LIMIT_SECONDS
    assert len(table) == core.nunique()


@pytest.mark.speed
def test_a_gap_of_two_over_a_hundred_thousand_words() -> None:
    rng = np.random.default_rng(2)
    vocabulary = [f"слово{i}" for i in range(3000)]
    text = " ".join(rng.choice(vocabulary, 100_000))
    core = pd.Series([" ".join(rng.choice(vocabulary, rng.integers(1, 4))) for _ in range(10_000)])

    started = time.perf_counter()
    table = sk.coverage(core, pd.Series([text]), gap=2)

    assert time.perf_counter() - started < LIMIT_SECONDS
    assert len(table) == core.nunique()
