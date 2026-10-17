"""What the pipeline refuses before it reads the input, and how it ends when stdout closes early."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from .runner import semkit, semkit_process


def _error(*args: str, input: str | None = None) -> tuple[int, dict]:
    result = semkit("--json", *args, input=input)
    return result.exit_code, json.loads(result.stdout)["error"]


def test_read_with_no_arguments_is_a_usage_error() -> None:
    code, error = _error("read")

    assert code == 2
    assert error["message"].startswith("read: IN not given;")
    assert "read --help" in error["action"]


def test_a_missing_in_is_refused_with_exit_2(tmp_path: Path) -> None:
    code, error = _error("read", str(tmp_path / "nope.csv"), "remove-words", "купить", "write", "-")

    assert code == 2
    assert error["message"] == f"read: IN {tmp_path / 'nope.csv'} does not exist."
    assert "format=" not in error["action"]


def test_an_out_of_an_unknown_format_is_refused_before_the_input_is_read(tmp_path: Path) -> None:
    code, error = _error("read", str(tmp_path / "nope.csv"), "write", str(tmp_path / "out.foo"))

    assert code == 2
    assert error["message"].startswith("write: OUT ")
    assert ".xlsx" in error["action"]


def test_a_txt_out_with_several_columns_is_refused_with_exit_2_and_out_stays(core_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.txt"

    code, error = _error("read", str(core_csv), "write", str(out))

    assert code == 2
    assert error["message"] == f"write: OUT {out} holds one column, the table has 2."
    assert not out.exists()
    assert sorted(path.name for path in tmp_path.iterdir()) == ["core.csv"]


def test_a_trace_in_a_folder_that_does_not_exist_is_refused_before_the_input_is_read(tmp_path: Path) -> None:
    trace = tmp_path / "no" / "t.jsonl"

    code, error = _error("read", str(tmp_path / "nope.csv"), "--trace", str(trace), "write", "-")

    assert code == 2
    assert error["message"].startswith("read: --trace ")


def test_an_existing_trace_is_refused_without_overwrite(core_csv: Path, tmp_path: Path) -> None:
    trace = tmp_path / "t.jsonl"
    trace.write_text("old\n", encoding="utf-8")

    code, error = _error("read", str(core_csv), "--trace", str(trace), "write", "-")

    assert code == 2
    assert error["code"] == "OUTPUT_EXISTS"
    assert "--overwrite" in error["action"]
    assert trace.read_text(encoding="utf-8") == "old\n"


def test_an_existing_trace_is_replaced_with_overwrite(core_csv: Path, tmp_path: Path) -> None:
    trace = tmp_path / "t.jsonl"
    trace.write_text("old\n", encoding="utf-8")

    result = semkit("read", str(core_csv), "--trace", str(trace), "remove-words", "купить", "write", "-", "--overwrite")

    assert result.exit_code == 0, result.output
    assert json.loads(trace.read_text(encoding="utf-8").splitlines()[0])["row"] == 1


def test_csv_on_stdin_is_refused_naming_jsonl_and_the_file_path() -> None:
    code, error = _error("read", "-", "write", "-", input="phrase,freq\nдиван,1\n")

    assert code == 2
    assert "JSONL" in error["message"]
    assert "path" in error["action"]
    assert not any(hint in error["action"] for hint in ("format=", "sep=", "encoding="))


def test_an_empty_input_says_it_is_empty(tmp_path: Path) -> None:
    source = tmp_path / "empty.csv"
    source.write_text("", encoding="utf-8")

    code, error = _error("read", str(source), "write", "-")

    assert code == 2
    assert "empty" in error["message"]


def test_a_header_without_rows_runs_and_writes_no_rows(tmp_path: Path) -> None:
    source = tmp_path / "header.csv"
    pd.DataFrame({"phrase": []}).to_csv(source, index=False)

    result = semkit("read", str(source), "remove-words", "купить", "write", "-")

    assert result.exit_code == 0, result.output


@pytest.mark.parametrize("arguments", [[], ["remove-words", "купить"]], ids=["read", "step"])
def test_a_closed_stdout_ends_quietly_with_exit_0(tmp_path: Path, arguments: list[str]) -> None:
    source = tmp_path / "core.csv"
    pd.DataFrame({"phrase": [f"купить диван {number}" for number in range(20000)]}).to_csv(source, index=False)
    semkit_cli = subprocess.Popen(  # noqa: S603
        [sys.executable, "-m", "rb_semkit.cli", "read", str(source), *arguments, "write", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert semkit_cli.stdout is not None and semkit_cli.stderr is not None
    semkit_cli.stdout.readline()
    semkit_cli.stdout.close()  # what `| head -1` does

    code = semkit_cli.wait(timeout=60)

    assert code == 0
    assert b"Error" not in semkit_cli.stderr.read()


def test_human_mode_ends_with_the_rows_written_and_the_target(core_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"

    result = semkit("read", str(core_csv), "write", str(out))

    assert result.stdout == f"Wrote 5 rows to {out}.\n"


def test_a_dry_run_says_it_wrote_nothing(core_csv: Path, tmp_path: Path) -> None:
    result = semkit("read", str(core_csv), "--dry-run", "write", str(tmp_path / "out.csv"))

    assert result.stdout == "Dry run: 5 rows, nothing written.\n"


def test_stdin_jsonl_still_reads(tmp_path: Path) -> None:
    result = semkit_process("read", "-", "write", "-", input='{"phrase": "диван"}\n')

    assert result.returncode == 0, result.stderr
