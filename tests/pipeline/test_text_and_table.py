"""`read --text` (phrases from the command line) and a pipeline without write (a table in the terminal, else JSONL)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from rich.console import Console

from rb_semkit.output import human

from .runner import jsonl, semkit


@pytest.fixture
def terminal(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stdout as a terminal: the table is drawn into the captured output."""
    monkeypatch.setattr(human, "console", Console(force_terminal=True, width=100, color_system=None))


def test_a_pipeline_without_write_prints_the_table_in_a_terminal(terminal: None) -> None:
    result = semkit("read", "--text", "растаможка авто", "--text", "купить диван", "ngrams", "-n", "1")

    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    assert [cell.strip() for cell in lines[1].strip("┃│ ").split("┃")] == ["ngram", "count", "docs"]
    body = [line for line in lines if "│" in line]
    assert [[cell.strip() for cell in line.strip("│ ").split("│")] for line in body] == [
        ["растаможка", "1", "1"],
        ["авто", "1", "1"],
        ["купить", "1", "1"],
        ["диван", "1", "1"],
    ]


def test_text_is_the_same_table_as_a_file_with_a_column_phrase(tmp_path: Path) -> None:
    result = semkit("read", "--text", "a b", "--text", "c", "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [{"phrase": "a b"}, {"phrase": "c"}]


def test_in_and_text_together_are_refused_with_exit_2(core_csv: Path) -> None:
    result = semkit("--json", "read", str(core_csv), "--text", "a", "write", "-")

    assert result.exit_code == 2
    message = json.loads(result.stdout)["error"]["message"]
    assert "IN" in message and "--text" in message


@pytest.mark.parametrize("flag", [["--json"], []])
def test_a_pipeline_without_write_gives_jsonl_with_json_or_outside_a_terminal(flag: list[str]) -> None:
    result = semkit(*flag, "read", "--text", "a b", "dupes", "--kind", "exact", "--action", "drop")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout)[0]["phrase"] == "a b"


def test_a_pipeline_with_write_out_works_as_before(tmp_path: Path, terminal: None) -> None:
    out = tmp_path / "out.csv"

    result = semkit("read", "--text", "a b", "write", str(out))

    assert result.exit_code == 0, result.output
    assert result.stdout == f"Wrote 1 rows to {out}.\n"
    assert out.read_text(encoding="utf-8").splitlines() == ["phrase", "a b"]
