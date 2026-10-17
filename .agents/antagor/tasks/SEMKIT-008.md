---
id: SEMKIT-008
title: 'Conformance: text matchers and markers in the shared case format, and the
  core report'
status: in_review
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
- tests/conformance/
- tests/matchers_vba/
- scripts/conformance_report.py
test_paths:
- tests/conformance/
docs:
- docs/vba/conformance.md
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on:
- SEMKIT-006
- SEMKIT-007
budget_usd: null
epic: E-001
spec_refs: []
checks:
- uv run pytest tests/conformance -q --no-cov
resident: null
tool: null
pr: null
translation: 'Сверка шаблонов и маркеров в общем формате «вход → VBA → semkit → правило
  и почему» (из тестов SEMKIT-005 и примеров справочника, ≥5 строк на шаблон и глагол)
  и итоговый отчёт docs/vba/conformance.md по всему ядру: по каждой функции обработчики
  VBA, сколько случаев как в VBA, отходы с причиной, xfail. Отчёт генерируется скриптом,
  тест ловит устаревший.'
---

SEMKIT-006 brings the conformance case format (tests/conformance/cases/<function>.tsv: case_id, function, call, input, vba, expected, rule, why) for the analysis functions. The text matchers and markers have their VBA cases in tests/matchers_vba/test_vba_cases.py (SEMKIT-005) as (phrase, matcher, verb, expected) without the VBA value, so where semkit follows the VBA and where it differs is not visible. This task moves them into the shared format and builds one report over the whole core.

1. For every matcher and markers: a case file in tests/conformance/cases/ with every row of tests/matchers_vba/test_vba_cases.py, plus the worked examples and quirks of its entries in docs/vba/matchers.md, at least 5 rows per matcher and verb; vba is the value the VBA handler gives (traced from the entry), expected is the semkit value; a row with expected != vba carries the ADR 0005 rule and the why line (how the VBA does it, why semkit differs). Remove tests/matchers_vba/test_vba_cases.py once every row is moved (test_vba_refs.py stays).
2. scripts/conformance_report.py writes docs/vba/conformance.md from all case files: per public function a section with its VBA handlers and lines, the counts (cases, as the VBA, deviations, xfail), then a table of the deviations (case, input, VBA, semkit, rule, why) and of the xfail rows; on top, one summary table over all functions. tests/conformance/test_report.py checks that docs/vba/conformance.md is what the script writes now (a stale report fails).
3. A case that fails is not fixed in src: xfail with the reason and an inbox finding (function, case_id, vba, expected, got).

## Acceptance

- Given every matcher of sk (chars, spaces, positions, around, regex, words, word_content, word_case, word_position, pos, repeats, stopwords, phrases, cells, markers), When tests/conformance/cases is listed, Then each has a case file with at least 5 rows per verb it supports, each with vba and expected, and rule and why where they differ [check: tests/conformance/test_cases.py]
- Given the case files of the whole core, When scripts/conformance_report.py runs, Then docs/vba/conformance.md lists every public function with its handlers, counts, deviations with rule and why, and xfail rows, and the committed file equals the output [check: tests/conformance/test_report.py]

## How to test

Public library seam (import rb_semkit as sk), parametrized over the TSV rows; the report test compares the committed file with the script output.

## Basis

docs/vba/matchers.md (handlers, quirks, worked examples per button), ADR 0005 (each deviation with how the VBA did it and why), tests/matchers_vba (SEMKIT-005 rows), tests/conformance (format and loader of SEMKIT-006).

## Read first

- `docs/adr/0005-port-vba-fix-defects.md`
- `docs/vba/matchers.md`

## Out of scope

- Changes in src/: a failing case becomes an xfail and an inbox finding.
- The analysis functions' cases (SEMKIT-006).
