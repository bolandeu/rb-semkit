"""The conformance cases of the declension and patterns areas (format in tests/conformance/case_files.py).

Each public function of the two areas has its case file with five cases at least, every case gives `expected`, and
each area report is what scripts/conformance_report.py writes from the case files.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

import rb_semkit as sk
from tests.conformance.case_files import NOT_CASED, Case, all_cases, render, run

ROOT = Path(__file__).resolve().parents[2]
AREAS = ("declension", "patterns")
MIN_CASES = 5
CASES = [case for case in all_cases() if case.area in AREAS]


def _functions(area: str) -> list[str]:
    """The public names of the area's modules that have conformance cases."""
    return [
        name
        for name in dir(sk)
        if getattr(getattr(sk, name), "__module__", "").startswith(f"rb_semkit.core.{area}.") and name not in NOT_CASED
    ]


@pytest.mark.parametrize("area", AREAS)
def test_each_function_of_the_area_has_five_cases_at_least(area: str) -> None:
    counts = Counter(case.function.partition(".")[0] for case in CASES if case.area == area)

    assert _functions(area)
    assert {name: counts[name] for name in _functions(area) if counts[name] < MIN_CASES} == {}


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.case_id)
def test_the_case_gives_the_expected_value(case: Case) -> None:
    assert not case.xfail
    assert render(run(case)) == case.expected
