"""The library core against the add-in's VBA, case by case (`cases/<function>.tsv`, format in case_files.py).

Each case runs through the public API and must give `expected`. Where `expected` differs from `vba`, the case names
the ADR 0005 rule that allows it (several joined by «; », each quoted from the ADR) and says why; where they are the
same, it names neither. A case with a reason in `xfail` is a strict xfail: the library does not give `expected` yet.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from tests.matchers_vba.test_vba_refs import MATCHERS, supported_verbs

from .case_files import CASES_DIR, Case, all_cases, render, run

ADR_FILE = Path(__file__).resolve().parents[2] / "docs" / "adr" / "0005-port-vba-fix-defects.md"
ADR = ADR_FILE.read_text(encoding="utf-8")
RULE_SEP = "; "
MIN_CASES = 5
ANALYSIS_FUNCTIONS = ("dupes", "ngrams", "bigrams", "counts", "lemmatize", "wordforms", "part_of_speech")
CASES = all_cases()


def _param(case: Case) -> object:
    marks = [pytest.mark.xfail(reason=case.xfail, strict=True)] if case.xfail else []
    return pytest.param(case, id=case.case_id, marks=marks)


@pytest.mark.parametrize("case", [_param(case) for case in CASES])
def test_the_result_is_the_expected_one(case: Case) -> None:
    assert render(run(case)) == case.expected


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.case_id)
def test_a_deviation_from_the_vba_has_an_adr_rule_and_a_reason(case: Case) -> None:
    if case.expected == case.vba:
        assert (case.rule, case.why) == ("", "")
        return
    rules = case.rule.split(RULE_SEP)
    assert case.rule and all(rule in ADR for rule in rules), f"not quoted from ADR 0005: {case.rule!r}"
    assert case.why.strip()


def test_every_analysis_function_has_its_case_file_with_five_cases() -> None:
    counts = {name: sum(case.function == name for case in CASES) for name in ANALYSIS_FUNCTIONS}

    assert all((CASES_DIR / f"{name}.tsv").is_file() for name in ANALYSIS_FUNCTIONS)
    assert min(counts.values()) >= MIN_CASES, counts


def test_every_matcher_has_its_case_file_with_five_cases_per_verb() -> None:
    counts = Counter(case.function for case in CASES)
    functions = [f"{name}.{verb}" for name, matcher in MATCHERS.items() for verb in supported_verbs(matcher)]

    assert all((CASES_DIR / f"{name}.tsv").is_file() for name in MATCHERS)
    assert {function: counts[function] for function in functions if counts[function] < MIN_CASES} == {}


def test_case_ids_are_unique_and_a_case_stands_in_the_file_of_its_function() -> None:
    ids = [case.case_id for case in CASES]

    assert len(ids) == len(set(ids))
    assert all(case.file == f"{case.function.partition('.')[0]}.tsv" for case in CASES)
