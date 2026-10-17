---
id: SEMKIT-028
title: CLI read keeps numeric columns numeric; only the text columns are text
status: done
attempts: 0
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: architect
worker: claude-code
type: bugfix
owns_paths:
- src/rb_semkit/pipeline/tables.py
- src/rb_semkit/pipeline/state.py
- docs/plan.md
- src/rb_semkit/data/SKILL.md
- src/rb_semkit/steps/__init__.py
- src/rb_semkit/steps/analysis.py
test_paths:
- tests/pipeline/
- tests/steps/test_steps.py
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: null
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**CLI: числа остаются числами.** Сейчас read читает всё как текст, и
  freq 100 выходит строкой "100"; колонки частот и весов — текст для шагов, которые
  их суммируют или сортируют. Читать с типами dataio; рабочая колонка всегда текст
  (''2024'' остаётся ''2024'', пусто — ''''); остальные колонки — свои типы; числа
  пишутся числами во всех форматах.'
---

semkit read now reads every column as text (as_text=True), so freq 100 comes out as "100" in JSONL and a weight or frequency column is text for the steps that sum or sort by it (ngrams --weight, cluster-serp --freq, the corpus steps with a frequency). Read with the types dataio infers; the working column is always text (a phrase '2024' stays '2024', NaN becomes ''); other columns keep their types; numbers are written as numbers in JSONL, csv, xlsx and parquet. --whole and stdin JSONL follow the same rule.

## Acceptance

- Given core.csv with phrase,freq rows 'диван,100', When semkit read core.csv write - runs, Then the row is {"phrase": "диван", "freq": 100} [check: tests/pipeline/]
- Given a phrase column holding '2024' and an empty cell, When read, Then the working column holds '2024' and '' as text [check: tests/pipeline/]
- Given core.csv with freq, When semkit read core.csv ngrams --weight freq write - runs, Then the sum column adds the numbers [check: tests/pipeline/]
- Given a table read and written to xlsx and parquet, When read back, Then freq is a number column [check: tests/pipeline/]

## How to test

CLI tests through CliRunner over csv, xlsx, parquet and JSONL fixtures.

## Basis

rb_dataio.read infers types by default (plan §3: '5' → Int64, dates → datetime); the library needs text only in the working column and the other text columns. Read with the inferred types, then make the text columns text: the working column (and a column a step names as text) becomes str with NaN as '', so a phrase like '5' stays the phrase '5'.

## Read first

- `src/rb_semkit/pipeline/tables.py`
- `docs/plan.md`

## Out of scope

- Changing the library's input rules (fillna and text checks in Frame).

## Feedback

### Answer to finding #1

> tests/test_scripts.py::test_antagor_project_config fails independent of SEMKIT-028: antagor config now lists 'scratch/' next to 'state/', 'receipts/'; the test expects only the two.

Taken into SEMKIT-029; 028 is published together with 029 so main stays green.
