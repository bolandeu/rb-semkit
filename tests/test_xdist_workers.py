"""`-n auto` runs at most three workers, and fewer when PYTEST_XDIST_AUTO_NUM_WORKERS asks for fewer."""

from __future__ import annotations

import pytest

pytest.importorskip("xdist")


def _workers(request: pytest.FixtureRequest) -> int:
    return request.config.hook.pytest_xdist_auto_num_workers(config=request.config)


def test_without_the_variable_the_workers_are_capped_at_three(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("PYTEST_XDIST_AUTO_NUM_WORKERS", raising=False)

    assert _workers(request) == 3


def test_a_variable_below_the_cap_wins(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTEST_XDIST_AUTO_NUM_WORKERS", "2")

    assert _workers(request) == 2


def test_a_variable_above_the_cap_does_not_lift_it(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PYTEST_XDIST_AUTO_NUM_WORKERS", "8")

    assert _workers(request) == 3
