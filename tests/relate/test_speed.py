"""relate-phrases speed: the 1000 phrases of the sofa core run in at most 10 seconds on the development machine, with
the real thesaurus read before the clock starts. Left out of the gate (marker speed); run it on an idle machine."""

from __future__ import annotations

import csv
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from rb_semkit.core.errors import CliError
from rb_semkit.core.word_vectors import thesaurus

from ..e2e.recount import FIXTURES
from .runner import rows

pytestmark = [pytest.mark.speed, pytest.mark.real_encoder]

SOFA = FIXTURES / "sofa_core.csv"
SECONDS = 10


@pytest.fixture(autouse=True)
def _real_thesaurus_once(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """The thesaurus from the cache, read before the clock starts; skips when it is not pulled."""
    try:
        loaded = thesaurus.open_thesaurus(Path.cwd())
    except CliError as error:
        pytest.skip(f"ruwordnet is not in the cache ({error.code}): run 'semkit models pull ruwordnet'.")
    monkeypatch.setattr(thesaurus, "open_thesaurus", lambda start: loaded)
    yield


def test_the_sofa_core_runs_in_seconds(tmp_path: Path) -> None:
    with SOFA.open(newline="", encoding="utf-8") as file:
        phrases = [row["phrase"] for row in csv.DictReader(file)]
    rows(tmp_path, phrases[:10])  # the lemmatizer and the lists are read before the clock starts

    start = time.perf_counter()
    found = rows(tmp_path, phrases)
    seconds = time.perf_counter() - start

    assert len(phrases) == 1000
    assert len(found) == 1000
    assert seconds <= SECONDS, f"{seconds:.1f} s"
