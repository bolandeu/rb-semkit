---
id: SEMKIT-059
title: 'write --columns and --rename: choose, order and rename the output columns
  (dataio v0.1.26)'
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
- pyproject.toml
- uv.lock
- src/rb_semkit/pipeline/tables.py
- src/rb_semkit/pipeline/
- src/rb_semkit/commands/read.py
- src/rb_semkit/data/SKILL.md
- README.md
- tests/pipeline/
- tests/snapshots/
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
- uv run --extra vectors pytest
resident: null
tool: null
pr: null
translation: 'write --columns/--rename: выбрать, упорядочить и переименовать колонки
  вывода через dataio v0.1.26; пин dataio поднять до v0.1.26.'
---

dataio v0.1.26 (IDEA-241) writes a chosen set of columns, in a chosen order, under chosen names: write() takes columns (a list of source names, kept in this order) and rename (a mapping old -> new), the selection first, then the rename; an unknown name, a rename of a missing or dropped column, or a clash is INVALID_ARGUMENTS (exit 2) listing the columns there are; a swap a<->b is allowed. The output field names of semkit are the column names its steps make, so agents and Windmill want to set them at write time.

1. The dataio pin moves to v0.1.26 (the git tag of [tool.uv.sources] and the lower bound rb-dataio>=0.1.26,<0.2); uv.lock refreshed.
2. write OUT takes --columns NAME,NAME (comma list, repeatable) and --rename OLD=NEW (repeatable, split on the first '='), passed to dataio as they are; the errors of dataio come out as semkit errors with their exit 2 and message.
3. The same choice for the output without write (the terminal table, or JSONL to a pipe): not in this task; write - takes the options.
4. Help of write with an example, the agent guide and README: … nearest --to Q write - --columns phrase,similarity --rename similarity=сходство.

## Acceptance

- Given a nearest report, When write - --columns phrase,similarity runs, Then each JSONL object has exactly the keys phrase and similarity in that order [check: tests/pipeline/]
- Given --rename similarity=сходство, When write out.csv runs, Then the header is phrase,сходство [check: tests/pipeline/]
- Given --columns nosuch, When write runs, Then it is refused with exit 2 listing the columns there are [check: tests/pipeline/]
- Given write without these options, When it runs, Then the output is as before [check: tests/pipeline/]

## How to test

Integration through the semkit CLI runner on small JSONL tables.

## Basis

pipeline/tables.py (the write step and its call of dataio.write); the dataio v0.1.26 API (columns, rename).

## Out of scope

- Column choice for the output without write; renaming inside the pipeline (a step).
