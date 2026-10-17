"""The CLI part of the benchmark, within its budget: 1M phrases in parquet through 5 cleaning steps, and 100k rows
written to xlsx in a few seconds (dataio v0.1.23 writes xlsx in linear time)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "bench.py"
PIPELINE_ROWS = "1000000"
XLSX_ROWS = "100000"
XLSX_SECONDS = "5"  # «within a few seconds» of the task (SEMKIT-033)


def _bench_line(capsys: pytest.CaptureFixture[str], operation: str, *arguments: str) -> tuple[int, list[str]]:
    """The exit code of the bench over one operation and the fields of its line."""
    spec = importlib.util.spec_from_file_location("bench", SCRIPT)
    assert spec is not None and spec.loader is not None
    bench = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bench)

    code = bench.main(["--ops", operation, *arguments])

    line = next(line for line in capsys.readouterr().out.splitlines() if line.startswith(operation))
    return code, line.split()


@pytest.mark.speed
def test_the_pipeline_part_of_the_bench_runs_within_its_budget(capsys: pytest.CaptureFixture[str]) -> None:
    code, fields = _bench_line(capsys, "pipeline", "--rows", PIPELINE_ROWS)

    assert code == 0, fields
    assert fields[1] == PIPELINE_ROWS


@pytest.mark.speed
def test_100k_rows_are_written_to_xlsx_within_a_few_seconds(capsys: pytest.CaptureFixture[str]) -> None:
    code, fields = _bench_line(capsys, "write-xlsx", "--rows", XLSX_ROWS, "--limit", XLSX_SECONDS)

    assert code == 0, fields
    assert fields[1] == XLSX_ROWS
