"""The vector index of the steps by meaning: exact search up to the limit, HNSW above it; deterministic both ways."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pandas as pd
import pytest

from rb_semkit.core.vectors import registry

from ..pipeline.runner import jsonl, semkit

PHRASES = [
    "купить диван", "диван купить", "купить диван недорого", "купить угловой диван", "угловой диван",
    "ремонт телефона", "ремонт телефонов", "телефон ремонт", "чехол для телефона",
]  # fmt: skip


@pytest.fixture
def phrases_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "phrases.csv"
    pd.DataFrame({"phrase": PHRASES}).to_csv(path, index=False)
    return path


def _exact_limit(monkeypatch: pytest.MonkeyPatch, limit: int) -> None:
    bundled = registry.bundled()
    lowered = dataclasses.replace(bundled, index=dataclasses.replace(bundled.index, exact_limit=limit))
    monkeypatch.setattr(registry, "bundled", lambda: lowered)


def _run(phrases_csv: Path, out: str) -> tuple[dict, list[dict]]:
    result = semkit("--json", "read", str(phrases_csv), "cluster-meaning", "--threshold", "0.7", "write", out)
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)["steps"][0], jsonl(Path(out).read_text(encoding="utf-8"))


def test_up_to_the_limit_the_search_is_exact_and_the_summary_says_so(phrases_csv: Path) -> None:
    summary, _ = _run(phrases_csv, "out.jsonl")

    assert summary["note"] == "index: exact"


def test_above_the_limit_the_search_is_hnsw_and_two_runs_agree(
    phrases_csv: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, exact = _run(phrases_csv, "exact.jsonl")
    _exact_limit(monkeypatch, 3)

    summary, first = _run(phrases_csv, "first.jsonl")
    _, second = _run(phrases_csv, "second.jsonl")

    assert summary["note"] == "index: hnsw"
    assert first == second
    assert first == exact  # a small table: HNSW finds every neighbour the exact search finds


def test_the_summary_line_names_the_index(phrases_csv: Path) -> None:
    result = semkit("read", str(phrases_csv), "cluster-meaning", "--threshold", "0.7", "write", "out.csv")

    assert result.exit_code == 0, result.output
    assert "cluster-meaning: 9 → 9 rows, 27 cells changed; index: exact" in result.stderr.splitlines()
