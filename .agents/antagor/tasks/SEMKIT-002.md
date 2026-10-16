---
id: SEMKIT-002
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
- x
test_paths:
- tests/x/
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-001
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
---

## Acceptance

- Given a, When b, Then c [check: tests/x/t.py]

## How to test

x

## Basis

x

## Read first

- `docs/adr/0004-matcher-and-three-verbs.md`
- `CONTEXT.md`
- `docs/plan.md`

## Out of scope

- x
