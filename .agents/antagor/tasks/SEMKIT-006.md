---
id: SEMKIT-006
title: 'Conformance: analysis functions and bundled data against the add-in VBA'
status: queue
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
- scripts/data_manifest.py
- scripts/bench.py
- scripts/build_data.toml
test_paths:
- tests/conformance/
docs: none
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on:
- SEMKIT-005
budget_usd: null
epic: E-001
spec_refs: []
checks:
- uv run pytest tests/conformance -q
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'Сверка ядра с VBA надстройки, вне шаблонов (их делает SEMKIT-005): дубли,
  n-граммы, биграммы, счётчики, леммы, словоформы, части речи. Каждый случай — строка
  «вход → VBA → semkit → правило ADR и почему»; тест падает на необъяснённом расхождении.
  Плюс все строки эталона semkit_reference.xlsx, проверка справочников на полноту
  против исходников VBA (манифест) и бюджет скорости. Код не правится: расхождение
  — xfail и сообщение Архитектору.'
---

Prove, case by case, how closely the library core repeats the add-in's VBA algorithms in the analysis area, where it differs and why, and that the bundled reference data is complete and fast. The text matchers are audited by SEMKIT-005; this task covers the rest of the core and the data.

## Case format (shared by every conformance test)

tests/conformance/cases/<function>.tsv, one row per case, columns: case_id, function (public sk name), call (the keyword arguments as JSON), input (one phrase, or several joined by ' | ' for a whole-column function), vba (what the VBA handler gives, traced from the reference below), expected (what semkit must give), rule (empty when expected == vba; otherwise the ADR 0005 rule), why (empty when expected == vba; otherwise one line: how the VBA did it and why semkit differs). tests/conformance/test_cases.py loads every TSV, runs the call through the public API and checks: the result equals expected; a row with expected != vba has a rule that is quoted in ADR 0005 and a non-empty why; a row with expected == vba has neither.

## Steps

1. Functions in scope: dupes (every kind and action), ngrams (words, lemmas, with and without stopwords, weights), bigrams, counts (every kind), lemmatize, wordforms, part_of_speech. For each: the VBA handler and lines (docs/vba/analysis.md, the dupes/n-gram docstrings of SEMKIT-003/004), and at least 5 cases: a plain one, the worked examples of the reference entry, and every quirk the entry lists (double spaces, case, ё, empty cells, punctuation, unknown words).
2. The reference workbook /Users/bolandau/Work/_sandbox/semtools/reference/semkit_reference.xlsx (sheet README names the handler of each sheet): copy every row of its 7 sheets into the case files with vba = the workbook value; expected follows ADR 0005.
3. Bundled data: scripts/data_manifest.py rebuilds tests/conformance/data_manifest.json from the VBA sources when they exist (/Users/bolandau/Work/_sandbox/semtools/reverse/downloads/spiski/*.xlsx for every marker list, /Users/bolandau/Work/_sandbox/semtools/reverse/data/lemms.tsv for the lemma dictionary, /Users/bolandau/Work/_sandbox/semtools/reverse/data/sheet_abc.tsv ranges and the VBA literals for stopwords, prepositions and suffix tables, as docs/vba/*.md name them): per bundled file its source, the source item count, the bundled item count and the items dropped with the reason. tests/conformance/test_data.py checks the bundled data against the manifest (counts, no unexplained drop), runs offline.
4. Speed: tests/conformance/test_speed.py runs each data-backed function (every marker list, stopwords, pos, lemmatize, wordforms) once on 10 000 synthetic phrases and fails above a budget of 2 s each and 0.5 s for the first load of a list; scripts/bench.py gets the same functions on the 1M set.
5. A row that fails against expected is not fixed in src: mark it xfail with the reason and report it in the inbox (finding: function, case_id, vba, expected, got, the code path you suspect). A VBA behaviour you think is a defect and ADR 0005 does not cover: ask in the inbox (question) with your recommendation.

## Acceptance

- Given the analysis functions dupes, ngrams, bigrams, counts, lemmatize, wordforms, part_of_speech, When tests/conformance/cases is listed, Then each has a case file with at least 5 rows, every row with vba, expected and, where they differ, rule and why [check: uv run pytest tests/conformance -q]
- Given the 7 sheets of the reference workbook, When the case files are read, Then every workbook row is a case with vba equal to the workbook value [check: uv run pytest tests/conformance -q]
- Given the bundled data files, When test_data runs, Then each file matches the manifest built from its VBA source and every dropped item has a reason [check: uv run pytest tests/conformance -q]
- Given 10 000 phrases, When each data-backed function runs, Then it finishes within its budget [check: uv run pytest tests/conformance -q]

## How to test

Public library seam (import rb_semkit as sk), parametrized over the TSV rows; the manifest test and the speed test run offline without the VBA sources.

## Basis

docs/vba/analysis.md (handlers, quirks, worked examples), ADR 0005 (allowed deviations, each with how the VBA did it and why), /Users/bolandau/Work/_sandbox/semtools/reference/semkit_reference.xlsx (VBA output on ~20 phrases per sheet), the VBA sources under /Users/bolandau/Work/_sandbox/semtools/reverse. Prior art: the dupes and n-gram docstrings and tests of SEMKIT-003/004, tests/matchers_vba of SEMKIT-005.

## Read first

- `docs/adr/0005-port-vba-fix-defects.md`
- `docs/vba/analysis.md`
- `CONTEXT.md`

## Out of scope

- Changes in src/: a failing case becomes an xfail and an inbox finding.
- The text matchers and markers (SEMKIT-005); declension, sentiment, clustering and the other v2 buttons.

## Feedback

### Blocked: scope_held (holders ['SEMKIT-005', 'SEMKIT-007'], paths ['docs/plan.md'])
