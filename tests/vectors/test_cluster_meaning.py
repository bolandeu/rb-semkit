"""`cluster-meaning` in a pipeline: every phrase gets a cluster, its name and its similarity to the name; the shared
options --model and --threshold and their errors."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from ..pipeline.runner import jsonl, semkit
from .conftest import LocalSource

# a1 a2 a3 share their words, b has none of them (the test encoder: a phrase is the sum of its words).
PHRASES = ["купить диван", "диван купить", "купить диван недорого", "ремонт телефона"]
FREQ = [10, 5, 40, 3]


@pytest.fixture
def phrases_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "phrases.csv"
    pd.DataFrame({"phrase": PHRASES, "freq": FREQ}).to_csv(path, index=False)
    return path


def _rows(*arguments: str) -> list[dict]:
    result = semkit(*arguments, "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


def test_close_phrases_share_a_cluster_and_a_far_one_is_a_cluster_of_one(phrases_csv: Path) -> None:
    rows = _rows("read", str(phrases_csv), "cluster-meaning", "--threshold", "0.7")

    assert [row["phrase"] for row in rows] == PHRASES
    assert [row["cluster"] for row in rows] == [1, 1, 1, 2]
    assert [row["cluster_name"] for row in rows] == ["купить диван"] * 3 + ["ремонт телефона"]
    assert rows[3]["similarity"] == 1.0


def test_with_freq_the_cluster_is_named_by_its_most_frequent_phrase(phrases_csv: Path) -> None:
    rows = _rows("read", str(phrases_csv), "cluster-meaning", "--threshold", "0.7", "--freq", "freq")

    assert [row["cluster_name"] for row in rows] == ["купить диван недорого"] * 3 + ["ремонт телефона"]
    assert rows[2]["similarity"] == 1.0
    assert [row["freq"] for row in rows] == FREQ


def test_two_runs_give_the_same_columns(phrases_csv: Path) -> None:
    arguments = ("read", str(phrases_csv), "cluster-meaning", "--threshold", "0.7")

    assert _rows(*arguments) == _rows(*arguments)


def test_a_high_threshold_leaves_only_the_same_words_together(phrases_csv: Path) -> None:
    rows = _rows("read", str(phrases_csv), "cluster-meaning", "--threshold", "0.99")

    assert [row["cluster"] for row in rows] == [1, 1, 2, 3]


def test_a_freq_column_the_table_lacks_is_refused(phrases_csv: Path) -> None:
    result = semkit("read", str(phrases_csv), "cluster-meaning", "--freq", "visits", "write", "-")

    assert result.exit_code == 2
    assert "--freq visits" in result.stderr


def _error(*arguments: str) -> tuple[int, dict]:
    result = semkit("--json", *arguments, "write", "out.csv")
    return result.exit_code, json.loads(result.stdout)["error"]


def test_an_unknown_model_names_the_short_names_and_the_hub_form(phrases_csv: Path) -> None:
    code, error = _error("read", str(phrases_csv), "cluster-meaning", "--model", "nosuch")

    assert code == 2
    text = error["message"] + error.get("action", "")
    assert all(name in text for name in ("nosuch", "e5-small", "bge-m3", "potion", "hf:<id>"))


@pytest.mark.parametrize("threshold", ["1.5", "-0.1"])
def test_a_threshold_out_of_range_names_the_step_and_the_flag(phrases_csv: Path, threshold: str) -> None:
    code, error = _error("read", str(phrases_csv), "cluster-meaning", "--threshold", threshold)

    assert code == 2
    assert error["message"].startswith("cluster-meaning: ")
    assert "--threshold" in error["message"]


def test_a_hub_model_needs_a_threshold(phrases_csv: Path) -> None:
    code, error = _error("read", str(phrases_csv), "cluster-meaning", "--model", "hf:org/model")

    assert code == 2
    assert "--threshold" in error["message"]


@pytest.mark.real_encoder
def test_a_model_not_in_the_cache_downloads_nothing_and_gives_the_pull_command(
    phrases_csv: Path, hub: LocalSource, models_dir: Path
) -> None:
    code, error = _error("read", str(phrases_csv), "cluster-meaning")

    assert code != 0
    assert error["code"] == "MODEL_NOT_PULLED"
    assert "semkit models pull e5-small" in error["action"]
    assert hub.downloads == []
    assert not models_dir.exists()
