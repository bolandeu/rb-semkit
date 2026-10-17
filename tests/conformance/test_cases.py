"""The library against the add-in's VBA, case by case (`cases/<area>/<function>.tsv`, format in case_files.py).

Each case runs through the public API and must give `expected`. Where `expected` differs from `vba`, the case names
the rule that allows it (several joined by «; », each quoted from ADR 0005 or from its area's deviations document) and
says why; where they are the same, it names neither. A case with a reason in `xfail` is a strict xfail: the library
does not give `expected` yet. Every public function of an area has its case file in the area's folder.
"""

from __future__ import annotations

import inspect
from collections import Counter
from pathlib import Path

import pytest

import rb_semkit as sk

from .case_files import CASE_COLUMNS, CASES_DIR, Case, all_cases, case_files, render, run, unquoted_rules

MIN_CASES = 5
VERBS = ("find", "remove", "extract")
# A function that is not from the add-in has no conformance case: the report compares semkit with the add-in, and a case
# without a VBA column to compare would count as «the VBA». Such a function is tested in its own area tests.
NOT_CASED = {
    *VERBS,  # the verbs and the pipe run in the cases of every matcher
    "pipe",
    "split_text",
    "coverage",
    "cluster_serp",  # takes a SERP table and replaces the add-in's method (ADR 0005)
    "text_stats",
    "compare_grams",
    "compare_stats",
    "bm25",
    "compare_lists",
    "edges",
    "parse_html",
    "headings",
    "word_list",  # semkit's own: the word lists, not a function of the add-in
}
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


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.case_id)
def test_a_deviation_from_the_vba_has_a_quoted_rule_and_a_reason(case: Case) -> None:
    if case.expected == case.vba:
        assert (case.rule, case.why) == ("", "")
        return
    assert unquoted_rules(case) == [], "not quoted from ADR 0005 or the area's deviations document"
    assert case.why.strip()


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


def test_a_case_file_in_a_new_area_folder_runs_and_quotes_its_area_deviations(tmp_path: Path) -> None:
    (tmp_path / "cases" / "zarea").mkdir(parents=True)
    rows = [_row("zarea-same", "TRUE", "", ""), _row("zarea-fixed", "FALSE", "латиница находится", "a test rule")]
    text = "\n".join(["# zarea. A temporary area.", "\t".join(CASE_COLUMNS), *rows]) + "\n"
    (tmp_path / "cases" / "zarea" / "chars.tsv").write_text(text, encoding="utf-8")
    (tmp_path / "deviations").mkdir()
    (tmp_path / "deviations" / "zarea.md").write_text("# zarea\n\nВ zarea латиница находится.\n", encoding="utf-8")

    same, fixed = all_cases(tmp_path / "cases")

    assert (same.area, same.file) == ("zarea", "zarea/chars.tsv")
    assert [render(run(case)) for case in (same, fixed)] == ["TRUE", "TRUE"]
    assert unquoted_rules(fixed, tmp_path / "deviations") == []
    assert unquoted_rules(fixed, tmp_path / "nowhere") == ["латиница находится"]
