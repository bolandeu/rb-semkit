---
id: SEMKIT-062
title: 'write: a refused --columns/--rename gets its own action line, not the ''folder
  is writable'' one'
status: done
attempts: 0
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: human
worker: claude-code
type: bugfix
owns_paths:
- src/rb_semkit/pipeline/tables.py
- tests/pipeline/
test_paths:
- tests/pipeline/
docs: none
tools: []
worker_args: null
class: mechanical
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
translation: 'write: при отказе dataio по --columns/--rename подсказка про колонки,
  а не «проверьте права на папку OUT».'
---

`write OUT --columns nosuch` exits 2 with dataio's message (good), but the next line says "Check that the folder of OUT is writable and OUT is not open in another program." That is WRITE_ACTION (src/rb_semkit/pipeline/tables.py), the action for a failed write, and it is wrong for a refused argument.

1. When dataio refuses an argument (`INVALID_ARGUMENTS`, the REFUSED code) during write, the action line says: "Give --columns and --rename the names of the columns the message lists." WRITE_ACTION stays for every other write error.
2. A test in tests/pipeline/ for both cases.

## Read first

- `src/rb_semkit/pipeline/tables.py` — `_dataio`, WRITE_ACTION

## Out of scope

- The messages of dataio themselves; the read errors.

## Acceptance

- Given write - --columns nosuch, When it runs, Then it exits 2 and the action line names --columns and --rename, not the folder of OUT [check: tests/pipeline/]
- Given a write to a folder that does not exist, When it runs, Then the action line still says to check the folder of OUT [check: tests/pipeline/]

## How to test

Integration through the semkit CLI runner on a one-row table.

## Basis

pipeline/tables.py _dataio and REFUSED (SEMKIT-059).
