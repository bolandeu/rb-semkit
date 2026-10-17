---
id: SEMKIT-044
title: 'coverage --gap: phrases with inserted words'
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
type: feature
owns_paths:
- src/rb_semkit/core/coverage/
- src/rb_semkit/steps/coverage.py
test_paths:
- tests/coverage/
- tests/snapshots/help/steps/coverage/coverage.txt
- tests/snapshots/describe.json
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-007
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'coverage --gap: фразы со вставленными словами.


  --gap N — до N слов между соседними словами фразы в режимах exact и lemmas, порядок
  слов сохраняется; по умолчанию 0 — как раньше; в any_order не применяется (отказ);
  не переходит через конец предложения.


  Приёмка: «купить недорогие пластиковые окна» — 1 при --gap 1, 0 при --gap 0; «очень
  недорогие» — нужен --gap 2; lemmas + gap находит «купили недорогое пластиковое окно»;
  через точку — 0; --gap -1 и gap с any_order — код 2; тест скорости укладывается.


  Вне: именованные виды вхождения, цели по фразам.'
---

coverage finds a phrase with words inserted between its words: natural text writes «купить недорогие пластиковые окна» for the phrase «купить пластиковые окна». --gap N allows up to N words between each two neighbouring words of the phrase, in the exact and lemmas modes; the order of the phrase words stays. The default 0 gives the output of before. In any_order mode the phrase words are already anywhere in one piece of text, so --gap does not apply there and the help says so. A gap never crosses a sentence end, as the modes of before.

## Acceptance

- Given the text «Здесь можно купить недорогие пластиковые окна.» and the phrase «купить пластиковые окна», When coverage --gap 1 runs, Then count is 1; with --gap 0 count is 0 [check: tests/coverage/test_coverage.py]
- Given «купить очень недорогие пластиковые окна» and --gap 1, When coverage runs, Then count is 0; with --gap 2 count is 1 [check: tests/coverage/test_coverage.py]
- Given --mode lemmas --gap 1 and the text «купили недорогое пластиковое окно», When coverage runs on «купить пластиковые окна», Then count is 1 [check: tests/coverage/test_coverage.py]
- Given «купить. Пластиковые окна» and --gap 3, When coverage runs, Then count is 0 (the gap does not cross a sentence end) [check: tests/coverage/test_coverage.py]
- Given --gap -1, When coverage runs, Then it is refused with exit 2 naming the flag; given --gap 2 with --mode any_order, Then it is refused with exit 2 saying the gap does not apply to that mode [check: tests/coverage/test_coverage.py]
- Given the speed test of coverage, When it runs with --gap 2, Then it stays within its limit [check: tests/coverage/test_speed.py]

## How to test

Integration through the semkit CLI (the pipeline test runner) with texts in the test module; the existing speed test of coverage.

## Basis

The word index of coverage: a text is scanned once, phrases are looked up by their words; keep that, do not scan once per phrase.

## Read first

- `src/rb_semkit/core/coverage/report.py`
- `docs/plans/html-and-brief.md`

## Out of scope

- named kinds of occurrence, a column per kind, a stricter exact
- target counts per phrase

## Feedback

### Blocked: scope_held (holders ['SEMKIT-042'], paths ['tests/snapshots/describe.json'])
