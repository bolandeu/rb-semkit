"""The library against the add-in's VBA, case by case (`cases/<area>/<function>.tsv`, format in case_files.py).

Each case runs through the public API and must give `expected`. Where `expected` differs from `vba`, the case names
the rule that allows it (several joined by «; », each quoted from ADR 0005 or from its area's deviations document) and
says why; where they are the same, it names neither. A case with a reason in `xfail` is a strict xfail: the library
does not give `expected` yet. Every public function of an area has its case file in the area's folder.
"""

from __future__ import annotations

import inspect
from collections import Counter

import pytest

import rb_semkit as sk

from .case_files import (
    CASES_DIR,
    NOT_CASED,
    VERBS,
    Case,
    all_cases,
    case_files,
    render,
    run,
)

MIN_CASES = 5
CASES = all_cases()


def _param(case: Case) -> object:
    marks = [pytest.mark.xfail(reason=case.xfail, strict=True)] if case.xfail else []
    return pytest.param(case, id=case.case_id, marks=marks)


def _public_functions() -> dict[str, str]:
    """Each public function of an area, by name: its area."""
    values = {name: getattr(sk, name) for name in dir(sk) if not name.startswith("_")}
    return {
        name: value.__module__.split(".")[2]
        for name, value in values.items()
        if inspect.isfunction(value) and value.__module__.startswith("rb_semkit.core.") and name not in NOT_CASED
    }


def _supported_verbs(matcher: sk.Matcher) -> list[str]:
    return [verb for verb in VERBS if getattr(type(matcher), verb) is not getattr(sk.Matcher, verb)]


@pytest.mark.parametrize("case", [_param(case) for case in CASES])
def test_the_result_is_the_expected_one(case: Case) -> None:
    assert render(run(case)) == case.expected


@pytest.mark.parametrize(("name", "area"), sorted(_public_functions().items()))
def test_every_public_function_has_its_case_file_in_its_area(name: str, area: str) -> None:
    assert (CASES_DIR / area / f"{name}.tsv").is_file()


def test_every_function_has_five_cases_and_a_matcher_five_per_verb_it_supports() -> None:
    counts = Counter(case.function for case in CASES)
    wanted = []
    for file in case_files():
        first = file.cases[0]
        if "." in first.function:
            matcher = getattr(sk, file.function)(**first.kwargs)
            wanted += [f"{file.function}.{verb}" for verb in _supported_verbs(matcher)]
        else:
            wanted.append(file.function)

    assert {function: counts[function] for function in wanted if counts[function] < MIN_CASES} == {}


def test_case_ids_are_unique_and_a_case_stands_in_the_file_of_its_function() -> None:
    ids = [case.case_id for case in CASES]

    assert len(ids) == len(set(ids))
    assert all(case.file == f"{case.area}/{case.function.partition('.')[0]}.tsv" for case in CASES)


def _row(case_id: str, vba: str, rule: str, why: str) -> str:
    return "\t".join((case_id, "chars.find", '{"kind": "latin"}', "диван IKEA", vba, "TRUE", rule, why, ""))
