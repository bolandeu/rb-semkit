"""write --columns and --rename: choose, order and name the output columns."""

from __future__ import annotations

import json
from pathlib import Path

from .runner import CORE, jsonl, semkit


def test_columns_keep_the_chosen_ones_in_the_given_order(core_csv: Path) -> None:
    result = semkit("read", str(core_csv), "write", "-", "--columns", "freq,phrase")

    assert result.exit_code == 0, result.output
    rows = jsonl(result.stdout)
    assert [list(row) for row in rows] == [["freq", "phrase"]] * len(CORE)
    assert rows[0] == {"freq": 5, "phrase": "купить диван"}


def test_columns_repeat_and_take_a_comma_list(core_csv: Path) -> None:
    result = semkit("read", str(core_csv), "write", "-", "--columns", "freq", "--columns", "phrase")

    assert [list(row) for row in jsonl(result.stdout)] == [["freq", "phrase"]] * len(CORE)


def test_rename_sets_the_header_of_a_file(core_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"

    result = semkit("read", str(core_csv), "write", str(out), "--columns", "phrase,freq", "--rename", "freq=частота")

    assert result.exit_code == 0, result.output
    assert out.read_text(encoding="utf-8-sig").splitlines()[0] == "phrase,частота"


def test_rename_splits_on_the_first_equals_sign_and_swaps(core_csv: Path) -> None:
    result = semkit("read", str(core_csv), "write", "-", "--rename", "phrase=freq", "--rename", "freq=a=b")

    assert list(jsonl(result.stdout)[0]) == ["freq", "a=b"]


def test_an_unknown_column_is_refused_with_the_columns_there_are(core_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"

    result = semkit("--json", "read", str(core_csv), "write", str(out), "--columns", "nosuch")

    error = json.loads(result.stdout)["error"]
    assert result.exit_code == 2
    assert error["code"] == "INVALID_ARGUMENTS"
    assert "phrase, freq" in error["message"]
    assert not out.exists()


def test_a_rename_without_equals_sign_is_refused(core_csv: Path) -> None:
    result = semkit("--json", "read", str(core_csv), "write", "-", "--rename", "freq")

    assert result.exit_code == 2


def test_write_without_the_options_writes_every_column(core_csv: Path) -> None:
    result = semkit("read", str(core_csv), "write", "-")

    assert [list(row) for row in jsonl(result.stdout)] == [["phrase", "freq"]] * len(CORE)
