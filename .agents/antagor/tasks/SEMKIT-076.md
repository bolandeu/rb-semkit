---
id: SEMKIT-076
title: Shape steps group-rows, split-rows, unpivot
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
- src/rb_semkit/core/reshape/
- src/rb_semkit/steps/reshape.py
- tests/reshape/
- tests/steps/areas/reshape.py
- tests/steps/fixtures/reshape/
- tests/snapshots/help/steps/reshape/
- tests/snapshots/describe/steps/reshape/
- src/rb_semkit/data/SKILL.md
test_paths:
- tests/reshape/
- tests/steps/
docs:
- src/rb_semkit/data/SKILL.md
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-075
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
translation: 'Шаги group-rows (свёртка: строка на группу по --by, фразы через --sep
  «, », count, --sum суммирует числа), split-rows (строка размножается по --sep «,»,
  края обрезаются, пустые части не дают строк) и unpivot (--keep остаются, остальные
  столбцы — в строки column/value, имена меняются опциями) — новая область reshape.
  Справка для агентов — с типовой цепочкой «кластер одной строкой». Неверный ввод
  — отказ до записи.'
---

Three steps that change the shape of the current table.

- group-rows --by COLUMN (repeatable): one row per group, in the order of the first row of each group; the group columns, the phrases of the working column of the group joined by --sep (default ", ", empty cells left out), and count (the rows of the group). Each column named by --sum (repeatable) holds the sum of its numbers in the group («5,5» counts as 5.5). Other columns are dropped. The working column after the step is the joined phrases.
- split-rows: a cell of the working column cut by --sep (default ","): one row per part, spaces at the edges of each part trimmed, an empty part makes no row, the other columns copied to each new row. A cell with no separator stays one row; an empty cell stays one row with an empty cell.
- unpivot --keep COLUMN (repeatable): the kept columns stay; every other column turns into rows: one row per kept row and unpivoted column, with the column name in a column named by --name-column (default column) and the cell in --value-column (default value). The working column after the step is the value column.

Each step is a public function of a new area of the library (reshape), on a DataFrame, and a Step of the step table that wraps it, with help by the help standard. The agent guide gets the three steps in its Table bricks section, with one typical pipeline that runs (a cluster as one row: cluster-by-frequency, then group-rows).

A wrong input is refused before any row is written, and the message names it: a column of --by, --sum or --keep the table does not have (with the columns there are), a --sum column with a text that is not a number (naming the row), an empty --sep, --keep with every column of the table, a --name-column or --value-column the kept columns already have.

## Acceptance

- Given rows (cluster, phrase, freq) = (диван, купить диван, 10), (диван, диван недорого, 5), (кресло, кресло, 3), When group-rows --by cluster --sum freq runs, Then two rows: (диван, 'купить диван, диван недорого', count 2, freq 15) and (кресло, 'кресло', 1, 3), and no other column [check: tests/reshape/]
- Given a cell 'диван, софа ,' and a column freq 7, When split-rows runs, Then two rows ('диван', 7) and ('софа', 7); with --sep ';' a cell 'а;б' gives 'а' and 'б'; a cell without the separator stays one row [check: tests/reshape/]
- Given columns phrase, msk, spb with the row (диван, 10, 4), When unpivot --keep phrase runs, Then rows (диван, msk, 10) and (диван, spb, 4) in columns phrase, column, value; --name-column region --value-column freq renames the two [check: tests/reshape/]
- Given a wrong input (a --by, --sum or --keep column the table does not have, a --sum cell 'много', --sep '', --keep with every column, --value-column phrase while phrase is kept), When the step runs, Then semkit exits with the usage error before writing and the message names the wrong value and, for a column, the columns there are [check: tests/reshape/]
- Given the agent guide, When its typical pipelines run, Then the one with group-rows writes the rows the guide shows [check: tests/steps/]

## How to test

Integration through the command line pipeline: semkit read TABLE.jsonl STEP ... write -, on small JSONL tables written by the test; the step table tests through tests/steps/areas/reshape.py with fixtures in tests/steps/fixtures/reshape/

## Basis

Follow the rows area of SEMKIT-075 and the table area (core/table, steps/table.py); numbers_of for --sum

## Read first

- `src/rb_semkit/steps/table.py`
- `tests/table/test_table_bricks.py`

## Out of scope

- fill-down, sample-rows, shuffle-rows, lookup: other tasks of the epic
- NOT_CASED: SEMKIT-075 already lists the names
