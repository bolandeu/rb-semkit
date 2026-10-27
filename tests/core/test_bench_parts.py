"""scripts/bench.py runs every benchmark part it finds, each operation within the budgets of the bench."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "bench.py"
PART = '''"""A temporary area: the length of each phrase, and a word list it loads first."""

DATA_OPERATIONS = {"zarea_words": lambda phrases: phrases.str.split()}
OPERATIONS = {"zarea_lengths": lambda phrases: phrases.str.len()}
'''


def _bench(tmp_path: Path, *argv: str, part: str = PART) -> subprocess.CompletedProcess[str]:
    (tmp_path / "zarea.py").write_text(part, encoding="utf-8")
    return subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT), "--rows", "100", "--parts", str(tmp_path), *argv],
        capture_output=True,
        text=True,
        check=False,
    )


def _rows(output: str) -> dict[str, list[str]]:
    """The fields of each operation line of the bench output, by operation."""
    return {line.split()[0]: line.split()[1:] for line in output.splitlines()[1:]}


def test_the_operations_of_a_new_part_run_with_the_budgets(tmp_path: Path) -> None:
    result = _bench(tmp_path)

    assert result.returncode == 0, result.stderr
    rows = _rows(result.stdout)
    assert sorted(rows) == ["zarea_lengths", "zarea_words"]
    assert rows["zarea_lengths"][0] == "100"
    assert float(rows["zarea_lengths"][1]) == 0.0  # not data-backed: no load
    assert rows["zarea_words"][-1] == "ok"


def test_a_part_operation_over_its_budget_fails_naming_it(tmp_path: Path) -> None:
    result = _bench(tmp_path, "--ops", "zarea_lengths", "--limit", "0")

    assert result.returncode == 1
    assert _rows(result.stdout)["zarea_lengths"][-1] == "SLOW"
    assert "zarea_lengths" in result.stderr


def _timed_part(load: float, run: float) -> str:
    """A part whose operation sleeps `load` s on its first call (one phrase) and `run` s on the full call."""
    return (
        "import time\n"
        "def _op(phrases):\n"
        f"    time.sleep({load} if len(phrases) == 1 else {run})\n"
        "DATA_OPERATIONS = {'zarea_slow': _op}\n"
    )


def test_a_load_of_0_6_seconds_is_ok_with_the_default_load_limit(tmp_path: Path) -> None:
    result = _bench(tmp_path, part=_timed_part(load=0.6, run=0.1))

    assert result.returncode == 0, result.stderr
    assert _rows(result.stdout)["zarea_slow"][-1] == "ok"


def test_a_load_over_the_default_load_limit_is_slow(tmp_path: Path) -> None:
    result = _bench(tmp_path, part=_timed_part(load=2.5, run=0.1))

    assert result.returncode == 1
    assert _rows(result.stdout)["zarea_slow"][-1] == "SLOW"
