"""`ad-groups` in a pipeline: phrases that are duplicates by meaning of each other share a group, taken transitively;
--max-size splits a larger group by vector (the test encoder: a phrase is the sum of its words, so phrases that share
words are close)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..pipeline.runner import jsonl, semkit

CLOSE = "0.1"  # the phrases of these cases share a word or more; a refinement must not count however close they are
SEVEN = [
    "диван",
    "диван недорого",
    "недорого диван",
    "диван купить",
    "купить диван",
    "купить диван недорого",
    "диван недорого купить",
]


def _run(tmp_path: Path, phrases: list[str], *options: str, freq: list[int] | None = None) -> list[dict]:
    path = tmp_path / "phrases.csv"
    pd.DataFrame({"phrase": phrases, "freq": freq or range(len(phrases))}).to_csv(path, index=False)
    result = semkit("read", str(path), "ad-groups", *options, "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


def _groups(rows: list[dict]) -> list[int]:
    return [row["ad_group"] for row in rows]


def test_duplicates_by_meaning_share_a_group_and_a_refinement_is_another_group(tmp_path: Path) -> None:
    phrases = ["купить диван недорого", "диван купить", "недорогой диван купить", "угловой диван"]

    rows = _run(tmp_path, phrases, "--threshold", "0.4")

    assert [row["phrase"] for row in rows] == phrases
    assert _groups(rows) == [1, 1, 1, 2]
    assert [row["ad_group_name"] for row in rows] == ["купить диван недорого"] * 3 + ["угловой диван"]


def test_a_group_is_split_by_max_size_and_two_runs_give_the_same_groups(tmp_path: Path) -> None:
    rows = _run(tmp_path, SEVEN, "--threshold", CLOSE, "--max-size", "3")

    sizes = pd.Series(_groups(rows)).value_counts()
    assert len(sizes) == 3
    assert sizes.max() <= 3
    assert _run(tmp_path, SEVEN, "--threshold", CLOSE, "--max-size", "3") == rows


def test_without_max_size_a_group_stays_whole(tmp_path: Path) -> None:
    assert _groups(_run(tmp_path, SEVEN, "--threshold", CLOSE)) == [1] * 7


def test_with_freq_the_group_is_named_by_its_most_frequent_phrase(tmp_path: Path) -> None:
    phrases = ["купить диван", "диван купить", "угловой диван"]

    rows = _run(tmp_path, phrases, "--threshold", CLOSE, "--freq", "freq", freq=[10, 50, 5])

    assert [row["ad_group_name"] for row in rows] == ["диван купить", "диван купить", "угловой диван"]


def test_max_size_below_one_is_refused_naming_the_flag(tmp_path: Path) -> None:
    path = tmp_path / "phrases.csv"
    pd.DataFrame({"phrase": ["диван"]}).to_csv(path, index=False)

    result = semkit("read", str(path), "ad-groups", "--max-size", "0", "write", "-")

    assert result.exit_code == 2
    assert "--max-size" in result.output


def test_the_home_city_is_not_a_refinement_and_another_city_is(tmp_path: Path) -> None:
    rows = _run(tmp_path, ["диван москва", "диван", "диван саратов"], "--home", "москва", "--threshold", CLOSE)

    assert _groups(rows) == [1, 1, 2]
