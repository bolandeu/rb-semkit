"""Each data-backed function on 10 000 synthetic phrases: within 2 s, and within 0.5 s for the first load of its data.

scripts/bench.py runs them in a fresh process, so the first load is not hidden by a list another test loaded already.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "bench.py"
ROWS = 10_000
RUN_BUDGET = 2.0
LOAD_BUDGET = 0.5


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("bench", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bench = _load()
OPERATIONS = [name for name, operation in bench.operations(bench.DEFAULT_PARTS).items() if operation.data_backed]


@pytest.fixture(scope="module")
def timings() -> dict[str, tuple[float, float]]:
    """Seconds of the first load and of the run, by operation, from one run of the bench."""
    argv = ["--rows", str(ROWS), "--ops", ",".join(OPERATIONS), "--limit", str(RUN_BUDGET)]
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT), *argv, "--load-limit", str(LOAD_BUDGET)],
        capture_output=True,
        text=True,
        check=False,
    )
    rows = [line.split() for line in result.stdout.splitlines()[1:]]
    return {row[0]: (float(row[2]), float(row[3])) for row in rows if row[0] in OPERATIONS}


@pytest.mark.parametrize("operation", OPERATIONS)
def test_a_data_backed_function_runs_within_its_budget(operation: str, timings: dict[str, tuple[float, float]]) -> None:
    load, seconds = timings[operation]

    assert load <= LOAD_BUDGET, f"first load {load:.3f} s"
    assert seconds <= RUN_BUDGET, f"{ROWS} phrases in {seconds:.2f} s"
