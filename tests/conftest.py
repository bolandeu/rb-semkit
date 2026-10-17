"""Shared fixtures: a test sees only the word lists it sets up, never the ones of the machine it runs on."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _no_machine_word_lists(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SEMKIT_LISTS", raising=False)
