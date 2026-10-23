---
id: SEMKIT-075
title: Row steps fill-down, sample-rows, shuffle-rows, and the frame of the table
  steps
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
- src/rb_semkit/core/rows/
- src/rb_semkit/steps/rows.py
- tests/rows/
- tests/steps/areas/rows.py
- tests/steps/fixtures/rows/
- tests/snapshots/help/steps/rows/
- tests/snapshots/describe/steps/rows/
- tests/conformance/case_files.py
- src/rb_semkit/data/SKILL.md
test_paths:
- tests/rows/
- tests/steps/
- tests/conformance/
docs:
- src/rb_semkit/data/SKILL.md
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-008
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@v1.26.3#subdirectory=gate"
  rb-release check
resident: null
tool: null
pr: null
translation: 'Шаги fill-down (протяжка вниз пустых ячеек по --column, по умолчанию
  рабочий столбец), sample-rows (--n или --share, порядок сохраняется, --seed) и shuffle-rows
  (перемешивание, --seed) — новая область rows. Каркас эпика: все семь новых имён
  эпика сразу в NOT_CASED конформанса; три шага — в справке для агентов. Неверный
  ввод — отказ до записи с понятным сообщением.'
---

Three steps over the rows of the current table, and the frame the other table steps of the epic stand on.

- fill-down: in the columns named by --column (repeatable; by default the working column), a cell that is empty or holds only spaces takes the value of the nearest filled cell above it. Empty cells before the first filled cell stay empty. Other columns do not change.
- sample-rows: --n N keeps N rows, or --share S (0 < S <= 1) keeps that share of the rows, rounded to the nearest whole number. The rows keep their order. --seed makes the choice the same each run; without it each run chooses anew. --n larger than the table keeps every row.
- shuffle-rows: the same rows in a random order; --seed makes the order the same each run.

Each step is a public function of a new area of the library (rows), on a DataFrame, and a Step of the step table that wraps it, with help by the help standard (summary, examples, every option with its default). The working column stays the same after each step.

The frame for the epic: the conformance list of functions with no add-in case (NOT_CASED) gets all seven new names of the epic at once, as semkit's own table bricks: fill_down, sample_rows, shuffle_rows, group_rows, split_rows, unpivot, lookup. The agent guide gets the three steps of this task in its Table bricks section.

A wrong input is refused before any row is written, and the message names it: a --column the table does not have (with the columns there are), --n together with --share, neither of them, a negative --n, a --share outside (0, 1].

## Acceptance

- Given a column 'group' with values A, '', '  ', B, '' and an empty first cell above A, When fill-down --column group runs, Then it reads '', A, A, A, B, B [check: tests/rows/]
- Given 10 rows, When sample-rows --n 3 --seed 1 runs twice, Then both runs keep the same 3 rows in their table order; --share 0.25 keeps 3 rows (2.5 rounded); --n 20 keeps all 10 [check: tests/rows/]
- Given 10 rows, When shuffle-rows --seed 1 runs twice, Then both give the same order, the same 10 rows [check: tests/rows/]
- Given a wrong input (a --column the table does not have, --n with --share, neither, --n -1, --share 0 or 1.5), When the step runs, Then semkit exits with the usage error before writing, and the message names the wrong value and, for a column, the columns there are [check: tests/rows/]
- Given the conformance case files, When the conformance test runs, Then fill_down, sample_rows, shuffle_rows, group_rows, split_rows, unpivot and lookup are in NOT_CASED as semkit's own table bricks, and the step help snapshots of the three steps exist [check: tests/conformance/ tests/steps/]

## How to test

Integration through the command line pipeline: semkit read TABLE.jsonl STEP ... write -, on small JSONL tables written by the test (as tests/table/test_table_bricks.py); the step table tests through tests/steps/areas/rows.py with fixtures in tests/steps/fixtures/rows/

## Basis

Follow the table area: core/table (use_column, sort_rows) and steps/table.py (Step, Adapted, option, numbers_of); tests as tests/table/test_table_bricks.py

## Read first

- `src/rb_semkit/steps/table.py`
- `tests/table/test_table_bricks.py`
- `tests/steps/areas/table.py`

## Out of scope

- group-rows, split-rows, unpivot and lookup themselves: other tasks of the epic (only their names in NOT_CASED here)
- read/write changes, several input files
