"""1M phrases in parquet through 5 cleaning steps of the CLI, within the budget of the benchmark."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "bench.py"
ROWS = "1000000"


@pytest.mark.speed
def test_the_pipeline_part_of_the_bench_runs_within_its_budget(capsys: pytest.CaptureFixture[str]) -> None:
    spec = importlib.util.spec_from_file_location("bench", SCRIPT)
    assert spec is not None and spec.loader is not None
    bench = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bench)

    code = bench.main(["--rows", ROWS, "--ops", "pipeline"])

    line = next(line for line in capsys.readouterr().out.splitlines() if line.startswith("pipeline"))
    assert code == 0, line
    assert line.split()[1] == ROWS
