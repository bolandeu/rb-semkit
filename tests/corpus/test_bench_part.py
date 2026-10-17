"""The benchmark part of the corpus area: clustering by the frequency dictionary of 1M phrases within the budget."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "bench.py"


def test_clustering_1m_phrases_by_the_frequency_dictionary_fits_the_budget_of_the_bench() -> None:
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT), "--rows", "1000000", "--ops", "cluster_by_frequency"],
        capture_output=True,
        text=True,
        check=False,
    )

    rows = {line.split()[0]: line.split()[1:] for line in result.stdout.splitlines()[1:]}
    assert result.returncode == 0, result.stdout + result.stderr
    assert rows["cluster_by_frequency"][0] == "1000000"
    assert rows["cluster_by_frequency"][-1] == "ok"
