"""The change area's benchmark part: translit and ЧПУ of 1M phrases each within the budgets of scripts/bench.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "bench.py"
OPERATIONS = ("translit_en", "translit_ru", "chpu")


def test_translit_and_chpu_of_a_million_phrases_fit_the_budget() -> None:
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT), "--rows", "1000000", "--ops", ",".join(OPERATIONS)],
        capture_output=True,
        text=True,
        check=False,
    )

    rows = {line.split()[0]: line.split()[1:] for line in result.stdout.splitlines()[1:]}
    assert result.returncode == 0, result.stdout + result.stderr
    assert {name: rows[name][0] for name in OPERATIONS} == dict.fromkeys(OPERATIONS, "1000000")
    assert [rows[name][-1] for name in OPERATIONS] == ["ok"] * len(OPERATIONS)
