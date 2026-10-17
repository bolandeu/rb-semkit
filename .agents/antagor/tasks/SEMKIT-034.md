---
id: SEMKIT-034
title: x
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
- src/x
test_paths:
- tests/vectors/
docs: none
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-005
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
---

y

## Acceptance

- Given a, When b, Then c [check: tests/vectors/test_models.py]

## How to test

z

## Basis

b

## Read first

- `docs/plans/vectors.md`
- `docs/adr/0009-encoder-models-downloaded-once.md`
- `src/rb_semkit/steps/dupes.py`
- `src/rb_semkit/commands/lists.py`
- `CONTEXT.md`

## Out of scope

- w
