"""20 000 phrases of 10 URLs each cluster in seconds, either way."""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest

import rb_semkit as sk

LIMIT_SECONDS = 20


@pytest.mark.speed
@pytest.mark.parametrize("method", ["soft", "hard"])
def test_twenty_thousand_phrases(method: str) -> None:
    rng = np.random.default_rng(1)
    phrases = np.repeat([f"фраза {i}" for i in range(20_000)], 10)
    serp = pd.DataFrame(
        {
            "phrase": phrases,
            "position": np.tile(np.arange(1, 11), 20_000),
            "url": [f"https://site{n}.ru/p" for n in rng.integers(0, 60_000, 200_000)],
        }
    )

    started = time.perf_counter()
    table = sk.cluster_serp(serp, method=method)

    assert time.perf_counter() - started < LIMIT_SECONDS
    assert len(table) == 20_000
