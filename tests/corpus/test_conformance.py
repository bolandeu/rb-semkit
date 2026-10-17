"""The corpus area against the add-in: every public function has its case file of at least 5 cases, every case gives
its expected value, and the committed area report is what scripts/conformance_report.py writes.

The cases run here by area; tests/conformance/ runs them with every other area and checks the quoted rules.
"""

from __future__ import annotations

import inspect
import subprocess
import sys
from pathlib import Path

import pytest

import rb_semkit as sk
from tests.conformance.case_files import CASES_DIR, Case, all_cases, render, run

AREA = "corpus"
ROOT = Path(__file__).resolve().parents[2]
MIN_CASES = 5
CASES = [case for case in all_cases() if case.area == AREA]


def _functions() -> list[str]:
    return sorted(
        name
        for name in dir(sk)
        if not name.startswith("_")
        and inspect.isfunction(value := getattr(sk, name))
        and value.__module__.startswith(f"rb_semkit.core.{AREA}.")
    )


@pytest.mark.parametrize("name", _functions())
def test_each_function_of_the_area_has_a_case_file_of_at_least_five_cases(name: str) -> None:
    assert (CASES_DIR / AREA / f"{name}.tsv").is_file()
    assert sum(case.function == name for case in CASES) >= MIN_CASES


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.case_id)
def test_each_case_gives_its_expected_value(case: Case) -> None:
    assert not case.xfail
    assert render(run(case)) == case.expected


def test_the_area_report_is_what_the_script_writes(tmp_path: Path) -> None:
    script = ROOT / "scripts" / "conformance_report.py"
    result = subprocess.run([sys.executable, str(script), "--out", str(tmp_path)], capture_output=True, check=False)  # noqa: S603

    assert result.returncode == 0, result.stderr
    written = (tmp_path / "conformance" / f"{AREA}.md").read_text(encoding="utf-8")
    assert (ROOT / "docs" / "vba" / "conformance" / f"{AREA}.md").read_text(encoding="utf-8") == written
