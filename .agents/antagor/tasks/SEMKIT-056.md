---
id: SEMKIT-056
title: 'Table bricks: use-column switches the working column, sort-rows orders the
  rows by a column'
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
type: feature
owns_paths:
- src/rb_semkit/core/table/
- src/rb_semkit/steps/table.py
- src/rb_semkit/pipeline/
- src/rb_semkit/steps/__init__.py
- src/rb_semkit/data/SKILL.md
- tests/table/
- tests/snapshots/
test_paths:
- tests/table/
docs:
- src/rb_semkit/data/SKILL.md
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
- uv run --extra vectors pytest
resident: null
tool: null
pr: null
translation: 'Кирпичики таблицы: use-column NAME — сменить рабочую колонку (чтобы
  drop-cells empty убрал строки без совпадения), sort-rows --by COLUMN [--desc] —
  сортировка строк.'
---

The first scenario (the plan of vectors, phrase synonyms of one intent) needs jq for two things no step does: keep the rows nearest matched (it keeps an empty match for a row below the threshold) and order the rows by similarity. Two generic steps, chain-agnostic:

1. use-column NAME: the column NAME becomes the working column of the next steps; the table does not change. A missing column is refused with exit 2 naming the columns there are. Then drop-cells empty drops the rows with an empty match: nearest … use-column match drop-cells empty.
2. sort-rows --by COLUMN [--desc]: the rows in the order of the column, numbers as numbers, texts in the order of sort-words (ё after е), stable (equal rows keep their order), empty cells last; --by repeatable (the first wins, the next break ties). A missing column is refused with exit 2.
3. Step help with real examples; the agent guide shows nearest … use-column match drop-cells empty sort-rows --by similarity --desc.

## Acceptance

- Given a nearest report with rows below the threshold, When use-column match drop-cells empty runs, Then only the matched rows stay and the working column is match [check: tests/table/]
- Given a table with similarity 0.9, 0.95, empty, 0.8, When sort-rows --by similarity --desc runs, Then the order is 0.95, 0.9, 0.8, empty [check: tests/table/]
- Given equal values, When sort-rows runs, Then the rows keep their order; with --by a --by b the second breaks ties [check: tests/table/]
- Given use-column or sort-rows --by with a missing column, When it runs, Then it is refused with exit 2 naming the columns there are [check: tests/table/]

## How to test

Integration through the semkit CLI runner on small JSONL tables.

## Basis

steps/__init__.py (the step kinds) and pipeline/state.py (the working column).

## Read first

- `docs/plans/vectors.md`

## Out of scope

- semkit run and saved scenarios (the next task); filters by a numeric threshold.
