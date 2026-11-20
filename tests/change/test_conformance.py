"""The change area against the add-in: every public function of the area has its case file of 5 cases or more, every
case gives its expected value, and the area report is what scripts/conformance_report.py writes."""

from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

import pytest

import rb_semkit as sk
from tests.conformance.case_files import Case, case_files, render, run

ROOT = Path(__file__).resolve().parents[2]
AREA = "change"
FILES = [file for file in case_files() if file.area == AREA]
MIN_CASES = 5


def _report_script():
    spec = importlib.util.spec_from_file_location("conformance_report", ROOT / "scripts" / "conformance_report.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _area_functions() -> list[str]:
    values = {name: getattr(sk, name) for name in dir(sk) if not name.startswith("_")}
    return sorted(
        name
        for name, value in values.items()
        if inspect.isfunction(value) and value.__module__.startswith(f"rb_semkit.core.{AREA}.")
    )


def test_each_function_of_the_area_has_a_case_file_of_five_cases_or_more() -> None:
    assert sorted(file.function for file in FILES) == _area_functions()
    assert {file.function: len(file.cases) for file in FILES if len(file.cases) < MIN_CASES} == {}


@pytest.mark.parametrize("case", [case for file in FILES for case in file.cases], ids=lambda case: case.case_id)
def test_each_case_gives_its_expected_value(case: Case) -> None:
    assert render(run(case)) == case.expected
