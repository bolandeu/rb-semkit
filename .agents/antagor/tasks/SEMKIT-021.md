---
id: SEMKIT-021
title: 'Conformance: no cases for semkit''s own functions; drop the text_stats cases
  that copy expected into vba'
status: done
attempts: 0
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: human
worker: claude-code
type: chore
owns_paths:
- tests/conformance/cases/textstats/
- tests/conformance/cases/compare/
- tests/conformance/areas/textstats.py
- tests/conformance/areas/compare.py
- tests/conformance/test_cases.py
- docs/vba/conformance/textstats.md
- docs/vba/conformance/compare.md
- scripts/conformance_report.py
- tests/core/test_build_data.py
test_paths:
- tests/conformance/
- tests/core/test_build_data.py
docs:
- docs/vba/conformance.md
tools: []
worker_args: null
class: mechanical
decision: false
visual: null
depends_on:
- SEMKIT-020
- SEMKIT-011
budget_usd: null
epic: E-002
spec_refs: []
checks:
- uv run scripts/release.py --check
- uv run scripts/conformance_report.py --check
resident: null
tool: null
pr: null
translation: '**Сверка: без псевдо-случаев для своих функций.** text_stats нет в надстройке,
  а её случаи сверки копируют ожидаемое в колонку VBA — отчёт врёт про 10 совпадений.
  Убрать их, добавить text_stats в исключения рядом со split_text и coverage, записать
  правило: своя функция — без сверки, тесты только в своей области.'
---

The conformance report compares semkit with the add-in. text_stats, compare_grams, compare_stats and bm25 are not from the add-in, yet their case files copy expected into the vba column, so the report counts cases «as the VBA» that compare nothing. Remove tests/conformance/cases/textstats/, tests/conformance/cases/compare/, tests/conformance/areas/textstats.py, tests/conformance/areas/compare.py and the area pages docs/vba/conformance/textstats.md and docs/vba/conformance/compare.md (if present); add text_stats, compare_grams, compare_stats, bm25, compare_lists and edges to NOT_CASED in tests/conformance/test_cases.py with split_text, coverage and cluster_serp (semkit's own functions); regenerate docs/vba/conformance.md. Make the rule explicit where NOT_CASED is defined: a function that is not from the add-in has no conformance case; it is tested in its own area tests. If the report script needs an area list, it must not require an area for an own function.

Also: tests/conformance/test_cases.py::test_every_public_function_has_its_case_file_in_its_area must pass for the functions in NOT_CASED (SEMKIT-020 left it red for compare_lists and edges). And list change/translit.json and change/word_order.json in BUILT_FILES and the compact-JSON check of tests/core/test_build_data.py (SEMKIT-011 could not: the file was held).

## Acceptance

- Given the build test, When it runs, Then BUILT_FILES holds change/translit.json and change/word_order.json [check: tests/core/test_build_data.py]

- Given the conformance cases, When the gate runs, Then no case file exists for text_stats or the compare area, NOT_CASED holds split_text, coverage, cluster_serp, text_stats, compare_grams, compare_stats, bm25, compare_lists and edges, the gate is green, and docs/vba/conformance.md has no textstats or compare row [check: tests/conformance/]

## How to test

The existing conformance tests and conformance_report.py --check.

## Read first

- `tests/conformance/test_cases.py`
- `tests/conformance/case_files.py`

## Out of scope

- The tests in tests/textstats/ and tests/compare/ stay as they are.
