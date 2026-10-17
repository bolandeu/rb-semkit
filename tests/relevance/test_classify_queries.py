"""`classify-queries` in a pipeline: every query of a search query report gets the nearest phrase of the core, the
similarity and target yes/no; no row is dropped."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from ..pipeline.runner import jsonl, semkit

CORE = ["угловой диван купить", "купить диван", "диван недорого"]
QUERIES = ["диван угловой купить", "ремонт телефона", "диван купить"]


@pytest.fixture
def files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    monkeypatch.chdir(tmp_path)
    report, core = tmp_path / "queries.csv", tmp_path / "core.csv"
    pd.DataFrame({"query": QUERIES, "clicks": [7, 5, 3]}).to_csv(report, index=False)
    pd.DataFrame({"phrase": CORE, "freq": [10, 20, 30]}).to_csv(core, index=False)
    return report, core


def test_a_query_gets_its_nearest_core_phrase_the_similarity_and_the_target(files: tuple[Path, Path]) -> None:
    report, core = files

    result = semkit("read", str(report), "classify-queries", "--against", str(core), "--threshold", "0.8", "write", "-")

    assert result.exit_code == 0, result.output
    rows = jsonl(result.stdout)
    assert [row["query"] for row in rows] == QUERIES
    assert [row["clicks"] for row in rows] == [7, 5, 3]
    assert rows[0]["nearest_phrase"] == "угловой диван купить"
    assert rows[0]["similarity"] == 1.0
    assert [row["target"] for row in rows] == ["yes", "no", "yes"]
    assert rows[1]["similarity"] < 0.8


def test_an_against_file_that_does_not_exist_is_refused(files: tuple[Path, Path]) -> None:
    report, _ = files

    result = semkit("read", str(report), "classify-queries", "--against", "nosuch.csv", "write", "-")

    assert result.exit_code == 2
    assert "--against nosuch.csv" in result.stderr
