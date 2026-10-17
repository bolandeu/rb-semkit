---
id: SEMKIT-021
title: 'Conformance: no cases for semkit''s own functions; drop the text_stats cases
  that copy expected into vba'
status: ideas
attempts: 0
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: null
worker: claude-code
type: chore
owns_paths:
- tests/conformance/cases/textstats/
- tests/conformance/areas/textstats.py
- tests/conformance/test_cases.py
- docs/vba/conformance/textstats.md
- scripts/conformance_report.py
test_paths:
- tests/conformance/
docs:
- docs/vba/conformance.md
tools: []
worker_args: null
class: mechanical
decision: false
visual: null
depends_on: []
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

The conformance report compares semkit with the add-in. text_stats is not from the add-in, yet its case file copies expected into the vba column, so the report counts 10 cases «as the VBA» that compare nothing. Remove tests/conformance/cases/textstats/, tests/conformance/areas/textstats.py and docs/vba/conformance/textstats.md; add text_stats to NOT_CASED in tests/conformance/test_cases.py with split_text and coverage (semkit's own functions); regenerate docs/vba/conformance.md. Make the rule explicit where NOT_CASED is defined: a function that is not from the add-in has no conformance case; it is tested in its own area tests. If the report script needs an area list, it must not require an area for an own function.

## Acceptance

- Given the conformance cases, When the gate runs, Then no case file exists for text_stats, NOT_CASED holds split_text, coverage and text_stats, and docs/vba/conformance.md has no textstats row [check: tests/conformance/]

## How to test

The existing conformance tests and conformance_report.py --check.

## Read first

- `tests/conformance/test_cases.py`
- `tests/conformance/case_files.py`

## Out of scope

- The tests of text_stats in tests/textstats/ stay as they are.
