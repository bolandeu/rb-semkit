---
id: SEMKIT-049
title: 'read --text: phrases from the command line; a pipeline without write prints
  a table'
status: queue
attempts: 0
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: architect
worker: claude-code
type: feature
owns_paths:
- src/rb_semkit/commands/read.py
- src/rb_semkit/pipeline/
- src/rb_semkit/output/
- src/rb_semkit/data/SKILL.md
- README.md
- tests/snapshots/
- tests/pipeline/
test_paths:
- tests/pipeline/
docs:
- README.md
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
- uv run pytest
resident: null
tool: null
pr: null
translation: 'read --text: фразы прямо в команде; конвейер без write печатает таблицу
  в терминал (с --json или в пайп — JSONL).'
---

Quick tests of a step need a file today: read takes IN (a file, or '-' for JSONL on stdin), and write - gives JSONL only.

1. read --text TEXT (repeatable) makes the input table from the command line: one column phrase, one row per --text, in the order given. IN is then left out; IN and --text together are refused with exit 2.
2. A pipeline that ends without write prints the result as a table in the terminal (the human output of the CLI, every column, every row). With --json, or when stdout is not a terminal, it writes JSONL to stdout as write - does. write - stays as it is.
3. The read help, the agent guide (SKILL.md) and README show the short form: semkit read --text "растаможка авто" synonym-candidates --all

## Acceptance

- Given read --text 'растаможка авто' --text 'купить диван', When ngrams -n 1 runs without write, Then the terminal shows a table with the columns of the ngrams report [check: tests/pipeline/]
- Given read --text 'a b' with a write -, When it runs, Then the output is the same JSONL as for a file with a column phrase holding 'a b' [check: tests/pipeline/]
- Given read core.csv --text 'a', When it runs, Then it is refused with exit 2 and a message naming IN and --text [check: tests/pipeline/]
- Given a pipeline without write and --json (or stdout not a terminal), When it runs, Then stdout is JSONL of the result [check: tests/pipeline/]
- Given a pipeline with write out.csv, When it runs, Then it works as before [check: tests/pipeline/]

## How to test

Integration through the semkit CLI runner of the pipeline tests; the table checked by its header and rows in the captured output; help snapshots refreshed.

## Basis

commands/read.py and pipeline/tables.py (the '-' reader and the write step); output/human.py for the table.

## Out of scope

- Paging or truncating long tables; reading phrases from a plain-text stdin; any change of a step.
