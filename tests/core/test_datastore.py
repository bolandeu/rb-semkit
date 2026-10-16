"""The bundled data loads lazily, once, when many threads ask for it at once."""

from __future__ import annotations

import threading
import time
from collections import Counter
from pathlib import Path

import pandas as pd
import pytest

import rb_semkit as sk
from rb_semkit.core import datastore


def test_eight_threads_on_first_use_load_the_data_once(monkeypatch: pytest.MonkeyPatch) -> None:
    opened: Counter[str] = Counter()
    open_trie = datastore._open_trie

    def slow_counting_open(path: Path):
        opened[path.name] += 1
        time.sleep(0.05)  # widen the window in which a second loader could start
        return open_trie(path)

    monkeypatch.setattr(datastore, "_loaded", {})  # first use in this process
    monkeypatch.setattr(datastore, "_open_trie", slow_counting_open)
    start = threading.Barrier(8)
    results: list[list[str]] = []

    def lemmatize() -> None:
        lemmatizer = sk.SemtoolsLemmatizer()
        start.wait()
        results.append(sk.lemmatize(pd.Series(["москве", "купила"]), lemmatizer=lemmatizer).tolist())

    threads = [threading.Thread(target=lemmatize) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert results == [["москва", "купить"]] * 8
    assert opened == Counter({"lemmas.marisa": 1})
