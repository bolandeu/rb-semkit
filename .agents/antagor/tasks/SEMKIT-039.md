---
id: SEMKIT-039
title: 'coverage-meaning: core phrases a text covers by meaning'
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
type: feature
owns_paths:
- src/rb_semkit/core/coverage_meaning/
- src/rb_semkit/steps/coverage_meaning.py
test_paths:
- tests/coverage_meaning/
- tests/snapshots/describe.json
- tests/snapshots/help/read.txt
- tests/snapshots/help/steps/coverage_meaning/coverage-meaning.txt
- tests/steps/areas.py
- tests/steps/test_steps.py
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-038
budget_usd: null
epic: E-006
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'coverage-meaning: какие фразы ядра текст покрывает по смыслу.


  Рядом с покрытием по словам. Ядро против --text (файл или таблица url+text), разбитого
  на абзацы: каждой фразе — лучший абзац (url, номер, текст), сходство, покрыта да/нет
  по порогу; с --cluster — покрыт ли кластер (если покрыта любая его фраза). Строки
  не удаляются.


  Приёмка: угловой диван — абзац 2, покрыт; диван кровать — нет; кластер покрыт, если
  покрыта одна фраза; поиск по нескольким url; нет файла или колонки — код 2; пустой
  текст — всё не покрыто.


  Вне: изменения покрытия по словам, сценарии.'
---

coverage-meaning: which core phrases a text covers by meaning, beside the word coverage. The working table is the core; --text names a text file, or a table of url and text, cut into paragraphs by the paragraph unit of split-paragraphs. Every phrase gets its best paragraph (url, number, the paragraph), the similarity and covered yes/no by --threshold. With --cluster naming a cluster column (as cluster-meaning gives it), every phrase also gets covered yes/no of its cluster: a cluster is covered when any of its phrases is. No row is dropped.

## Acceptance

- Given a core with «угловой диван» and «диван кровать» and a text whose second paragraph is about corner sofas, When coverage-meaning runs, Then «угловой диван» gets paragraph 2, its similarity and covered yes; «диван кровать» gets covered no [check: tests/coverage_meaning/test_coverage_meaning.py]
- Given --cluster with a cluster of three phrases of which one is covered, When coverage-meaning runs, Then all three get cluster covered yes [check: tests/coverage_meaning/test_coverage_meaning.py]
- Given a table of two urls and texts, When coverage-meaning runs, Then the best paragraph is searched across both and its url is given [check: tests/coverage_meaning/test_coverage_meaning.py]
- Given --text that does not exist, or --cluster naming a column that is not there, When the step runs, Then it is refused with exit 2 naming the flag [check: tests/coverage_meaning/test_coverage_meaning.py]
- Given an empty text, When coverage-meaning runs, Then every phrase gets covered no and an empty paragraph [check: tests/coverage_meaning/test_coverage_meaning.py]

## How to test

Integration through the semkit CLI (the pipeline test runner) with the deterministic test encoder of E-005; small texts in the test module.

## Basis

The word coverage step for the shape of its options and its text input; the paragraph unit and nearest of the frame task; the base of E-005.

## Read first

- `src/rb_semkit/steps/coverage.py`
- `docs/plans/vectors.md`
- `CONTEXT.md`

## Out of scope

- changes to the word coverage
- off-topic paragraphs and competitor topics (scenarios of the vectors plan)
