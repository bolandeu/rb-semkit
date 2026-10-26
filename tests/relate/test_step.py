"""The step relate-phrases: --to, the refusals of the input, --dry-run and --json."""

from __future__ import annotations

import json
from pathlib import Path

from ..pipeline.runner import jsonl, semkit
from .runner import relate, table


def test_to_compares_every_row_only_with_that_phrase(tmp_path: Path) -> None:
    found = relate(tmp_path, ["угловой диван", "кресло", "диван", "купить угловой диван"], "--to", "диван")

    assert found["угловой диван"] == ("refinement", "диван", "угловой диван", "+угловой")
    assert found["кресло"] == ("other", "", "кресло", "unlinked: кресло | диван")
    assert found["диван"][:2] == ("same", "диван")
    assert found["купить угловой диван"][:2] == ("refinement", "диван")


def test_to_without_words_is_refused(tmp_path: Path) -> None:
    result = semkit("read", str(table(tmp_path, ["диван"])), "relate-phrases", "--to", "в", "write", "-")

    assert result.exit_code == 2
    assert "to: 'в' has no words" in result.output


def test_a_column_the_table_lacks_is_refused_by_its_name(tmp_path: Path) -> None:
    result = semkit("read", str(table(tmp_path, ["диван"])), "--column", "query", "relate-phrases", "write", "-")

    assert result.exit_code == 2
    assert "--column query: the input has no such column" in result.output


def test_an_empty_table_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "empty.jsonl"
    path.write_text("")

    result = semkit("read", str(path), "relate-phrases", "write", "-")

    assert result.exit_code == 2
    assert "the input is empty" in result.output


def test_dry_run_with_json_writes_nothing_and_counts_the_step(tmp_path: Path) -> None:
    out = tmp_path / "out.jsonl"

    result = semkit("--json", "--dry-run", "read", str(table(tmp_path, ["диван", "угловой диван"])), "relate-phrases",
                    "write", str(out))  # fmt: skip

    assert result.exit_code == 0, result.output
    envelope = json.loads(result.stdout)
    assert envelope["ok"] is True and envelope["written"] is False
    assert [step["step"] for step in envelope["steps"]] == ["relate-phrases"]
    assert not out.exists()


def test_json_gives_the_rows_with_the_four_columns_after_the_phrase(tmp_path: Path) -> None:
    result = semkit("--json", "read", str(table(tmp_path, ["диван", "угловой диван"])), "relate-phrases", "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [
        {"phrase": "диван", "class": "other", "of": "", "group": "диван", "reason": "base of: угловой диван"},
        {"phrase": "угловой диван", "class": "refinement", "of": "диван", "group": "диван", "reason": "+угловой"},
    ]
