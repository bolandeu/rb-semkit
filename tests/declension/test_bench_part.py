"""Everything that declines, on 1M synthetic phrases, within the budgets of scripts/bench.py (its defaults)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "bench.py"
ROWS = 1_000_000


def test_decline_on_a_million_phrases_fits_the_budget() -> None:
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT), "--rows", str(ROWS), "--ops", "decline"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    operation, rows, _load, _seconds, status = result.stdout.splitlines()[1].split()
    assert (operation, int(rows), status) == ("decline", ROWS, "ok")
