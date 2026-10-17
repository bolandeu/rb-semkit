"""What the pipeline refuses, and what it leaves on disk when it does."""

from __future__ import annotations

import json
from pathlib import Path

from .runner import jsonl, semkit


def test_an_existing_out_is_refused_without_overwrite(core_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    out.write_text("old\n", encoding="utf-8")

    result = semkit("read", str(core_csv), "remove-words", "--items", "купить", "write", str(out))

    assert result.exit_code != 0
    assert "--overwrite" in result.stderr
    assert out.read_text(encoding="utf-8") == "old\n"


def test_overwrite_replaces_an_existing_out(core_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.jsonl"
    out.write_text("old\n", encoding="utf-8")

    result = semkit("read", str(core_csv), "keep-words", "--items", "угловые", "write", str(out), "--overwrite")

    assert result.exit_code == 0, result.output
    assert jsonl(out.read_text(encoding="utf-8")) == [{"phrase": "угловые диваны", "freq": "2"}]
    assert sorted(path.name for path in tmp_path.iterdir()) == ["core.csv", "out.jsonl"]


def test_a_step_that_fails_mid_way_leaves_out_unchanged(core_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    out.write_text("old\n", encoding="utf-8")

    result = semkit(
        "read", str(core_csv), "remove-words", "--items", "купить", "ngrams", "--weight", "nope",
        "write", str(out), "--overwrite",
    )  # fmt: skip

    assert result.exit_code != 0
    assert "nope" in result.stderr
    assert out.read_text(encoding="utf-8") == "old\n"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["core.csv", "out.csv"]


def test_dry_run_prints_the_summary_and_writes_nothing(core_csv: Path, tmp_path: Path) -> None:
    out, trace = tmp_path / "out.csv", tmp_path / "t.jsonl"

    result = semkit(
        "read", str(core_csv), "--dry-run", "--trace", str(trace), "remove-words", "--items", "купить",
        "write", str(out),
    )  # fmt: skip

    assert result.exit_code == 0, result.output
    assert result.stderr.splitlines()[0].startswith("remove-words: 5 → 5 rows, 2 cells changed")
    assert not out.exists()
    assert not trace.exists()


def test_a_wrong_value_is_refused_before_the_input_is_read(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"

    result = semkit("read", str(missing), "remove-words", "--items", "x", "--mode", "nope", "write", "-")

    assert result.exit_code == 2
    assert "remove-words" in result.stderr
    assert "--mode" in result.stderr
    assert "'any'" in result.stderr and "'all'" in result.stderr
    assert "missing.csv" not in result.stderr


def test_a_wrong_value_with_json_is_an_error_envelope(tmp_path: Path) -> None:
    result = semkit("--json", "read", str(tmp_path / "missing.csv"), "remove-words", "--mode", "nope", "write", "-")

    payload = json.loads(result.stdout)
    assert result.exit_code == 2
    assert payload["ok"] is False
    assert payload["error"]["code"] == "INVALID_ARGUMENTS"
    assert "remove-words" in payload["error"]["message"] and "--mode" in payload["error"]["message"]
    assert "remove-words --help" in payload["error"]["action"]


def test_an_unknown_step_is_refused_naming_it(tmp_path: Path) -> None:
    result = semkit("--json", "read", str(tmp_path / "missing.csv"), "remove-wordz", "write", "-")

    payload = json.loads(result.stdout)
    assert result.exit_code == 2
    assert "remove-wordz" in payload["error"]["message"]


def test_a_pipeline_must_end_with_write(core_csv: Path) -> None:
    result = semkit("--json", "read", str(core_csv), "remove-words", "--items", "купить")

    payload = json.loads(result.stdout)
    assert result.exit_code == 2
    assert "write" in payload["error"]["message"]


def test_a_matcher_argument_the_library_refuses_is_refused_before_reading(tmp_path: Path) -> None:
    result = semkit("--json", "read", str(tmp_path / "missing.csv"), "remove-word-position", "write", "-")

    payload = json.loads(result.stdout)
    assert result.exit_code == 2
    assert payload["error"]["message"].startswith("remove-word-position: ")


def test_a_missing_input_is_an_error_after_the_steps_are_checked(tmp_path: Path) -> None:
    result = semkit("--json", "read", str(tmp_path / "missing.csv"), "remove-words", "--items", "x", "write", "-")

    payload = json.loads(result.stdout)
    assert result.exit_code != 0
    assert payload["error"]["code"] == "SOURCE_NOT_FOUND"


def test_trace_writes_one_row_per_changed_cell(core_csv: Path, tmp_path: Path) -> None:
    trace = tmp_path / "t.jsonl"

    result = semkit(
        "read", str(core_csv), "--trace", str(trace), "remove-words", "--items", "купить", "write", "-",
    )  # fmt: skip

    assert result.exit_code == 0, result.output
    assert jsonl(trace.read_text(encoding="utf-8")) == [
        {"row": 0, "step": "remove-words", "column": "phrase", "before": "купить диван", "after": "диван"},
        {
            "row": 2,
            "step": "remove-words",
            "column": "phrase",
            "before": "купить угловой диван",
            "after": "угловой диван",
        },
    ]


def test_quiet_drops_the_summary_lines(core_csv: Path, tmp_path: Path) -> None:
    result = semkit("read", str(core_csv), "--quiet", "remove-words", "--items", "купить", "write", "-")

    assert result.exit_code == 0, result.output
    assert result.stderr == ""
    assert len(jsonl(result.stdout)) == 5
