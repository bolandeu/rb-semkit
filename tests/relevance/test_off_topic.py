"""`off-topic` in a pipeline: every phrase of the core gets its distance from the centre of the core (or of the seed
phrases) and a yes/no flag; no row is dropped."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from ..pipeline.runner import jsonl, semkit

# the test encoder: a phrase is the sum of its words, so the last phrase shares only «диван» with the others.
SOFAS = ["купить диван", "диван купить", "купить угловой диван", "угловой диван", "диван недорого", "диван угловой"]
ODD = "скачать игру диван"
FREQ = [1, 1, 1, 1000, 1, 1, 1]


@pytest.fixture
def core_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "core.csv"
    pd.DataFrame({"phrase": [*SOFAS, ODD], "freq": FREQ}).to_csv(path, index=False)
    return path


def _rows(*arguments: str) -> list[dict]:
    result = semkit("read", *arguments, "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


def test_the_phrase_far_from_the_core_has_the_highest_score_and_the_flag_yes(core_csv: Path) -> None:
    rows = _rows(str(core_csv), "off-topic", "--threshold", "0.67")

    assert [row["phrase"] for row in rows] == [*SOFAS, ODD]
    assert max(rows, key=lambda row: row["off_topic_score"])["phrase"] == ODD
    assert [row["off_topic"] for row in rows] == ["no"] * 6 + ["yes"]
    assert all(0 <= row["off_topic_score"] <= 1 for row in rows)


def test_with_freq_a_frequent_phrase_pulls_the_centre_to_itself(core_csv: Path) -> None:
    plain = _rows(str(core_csv), "off-topic", "--threshold", "0.67")
    weighted = _rows(str(core_csv), "off-topic", "--threshold", "0.67", "--freq", "freq")

    assert plain[5]["phrase"] == weighted[5]["phrase"] == "диван угловой"  # a rare phrase near «угловой диван»
    assert weighted[5]["off_topic_score"] < plain[5]["off_topic_score"]
    assert weighted[3]["off_topic_score"] < plain[3]["off_topic_score"]


def test_with_seed_the_score_is_the_distance_from_the_seed_phrases(core_csv: Path) -> None:
    rows = _rows(str(core_csv), "off-topic", "--threshold", "0.67", "--seed", "скачать игру,игру скачать диван")

    assert min(rows, key=lambda row: row["off_topic_score"])["phrase"] == ODD
    assert [row["off_topic"] for row in rows] == ["yes"] * 6 + ["no"]


def test_a_freq_column_the_table_lacks_is_refused(core_csv: Path) -> None:
    result = semkit("read", str(core_csv), "off-topic", "--freq", "visits", "write", "-")

    assert result.exit_code == 2
    assert "--freq visits" in result.stderr
