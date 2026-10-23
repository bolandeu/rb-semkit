---
id: SEMKIT-077
title: 'Step lookup: columns of a lookup table by a key phrase'
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
- src/rb_semkit/core/lookup/
- src/rb_semkit/steps/lookup.py
- tests/lookup/
- tests/steps/areas/lookup.py
- tests/steps/fixtures/lookup/
- tests/snapshots/help/steps/lookup/
- tests/snapshots/describe/steps/lookup/
- src/rb_semkit/data/SKILL.md
- src/rb_semkit/pipeline/state.py
- src/rb_semkit/steps/__init__.py
test_paths:
- tests/lookup/
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
- SEMKIT-076
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
translation: 'Шаг lookup: столбцы справочной таблицы по ключевой фразе, в памяти,
  своим кодом (ADR 0012). --on KEY или main=lookup; --kind как у дублей (exact по
  умолчанию, implicit находит «Диван купить»); первое совпадение, число повторяющихся
  ключей в отчёте; без совпадения — пустые ячейки или --matched-only; --take сужает
  столбцы; совпадающее имя получает _lookup. Новая область lookup, справка для агентов
  с типовой цепочкой. Неверный ввод — отказ до записи.'
---

The step lookup adds the columns of a lookup table to the current table, row by row, by a key phrase (ADR 0012: the join is semkit's own code, in memory; CONTEXT.md, Lookup table).

- lookup FILE --on KEY: FILE is read as read reads a table (an address of dataio: a sheet, a Google spreadsheet). KEY is the key column, or main=lookup when the lookup table calls it differently; by default the working column of the table and the first text column of the lookup table.
- --kind: how two keys are the same, as the duplicate kinds of dupes: exact (default), explicit, implicit and the others dupes has. With implicit, «купить диван» finds «Диван купить».
- Each row gets the other columns of the lookup table (--take COLUMN, repeatable, narrows them) from the first row of the lookup table whose key matches. A key that repeats in the lookup table: the first row wins, and the step's report (stderr and --json) says how many keys repeat.
- A row with no match keeps empty cells in the new columns; --matched-only drops it. The rows keep their order and their number (never more rows than before).
- A lookup column whose name the table already has gets the suffix _lookup. The working column stays the same.

The step is a public function of a new area of the library (lookup), on two DataFrames, and a Step of the step table that wraps it, with help by the help standard. The agent guide gets the step in its Table bricks section, with one typical pipeline that runs (frequencies from another export joined by phrase).

A wrong input is refused before any row is written, and the message names it: a FILE that cannot be read, a key column missing in the table or in the lookup table (with the columns there are), a --take column the lookup table does not have, an unknown --kind.

## Acceptance

- Given a table of phrases (купить диван, кресло, стол) and a lookup table (phrase, freq, url) with (купить диван, 10, /d), (кресло, 3, /k), When lookup FILE --on phrase runs, Then the rows get freq and url: (купить диван, 10, /d), (кресло, 3, /k), (стол, '', ''), in the same order; with --matched-only стол is dropped; --take freq adds only freq [check: tests/lookup/]
- Given 'купить диван' in the table and 'Диван купить' in the lookup table, When lookup runs with --kind implicit, Then they match; with the default exact they do not [check: tests/lookup/]
- Given a lookup table where 'кресло' stands twice with freq 3 and 4, When lookup runs, Then кресло gets 3, the row count stays the same, and the report says 1 key repeats [check: tests/lookup/]
- Given a table with a column freq and a lookup table with freq, When lookup runs, Then the new column is freq_lookup; --on phrase=query matches the table's phrase with the lookup table's query [check: tests/lookup/]
- Given a wrong input (a FILE that does not exist, a key column missing in either table, --take with a column the lookup table does not have, --kind nonsense), When the step runs, Then semkit refuses before writing and the message names the wrong value and, for a column, the columns there are [check: tests/lookup/]
- Given the agent guide, When its typical pipelines run, Then the one with lookup writes the rows the guide shows [check: tests/steps/]

## How to test

Integration through the command line pipeline: semkit read TABLE.jsonl lookup LOOKUP.jsonl ... write -, on small JSONL tables written by the test; the step table tests through tests/steps/areas/lookup.py with fixtures in tests/steps/fixtures/lookup/

## Basis

Read the lookup table as compare-lists reads its second list (table_of, first_text in steps/listtools.py); compare keys with the dupes area's key_function for the kind; follow the rows area of SEMKIT-075 for the step and its tests

## Read first

- `src/rb_semkit/steps/listtools.py`
- `src/rb_semkit/core/dupes/functions.py`
- `docs/adr/0012-lookup-step-joins-in-semkit.md`

## Out of scope

- dataio: no change there (ADR 0012)
- fuzzy lookup by letters, several matches per row
- NOT_CASED: SEMKIT-075 already lists the name
