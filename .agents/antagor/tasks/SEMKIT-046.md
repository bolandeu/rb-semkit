---
id: SEMKIT-046
title: Test snapshots and step lists split by step, so tasks that add steps do not
  wait for each other
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
type: chore
owns_paths:
- tests/test_describe.py
- tests/test_help.py
- tests/snapshots/
- tests/steps/areas.py
- tests/steps/test_steps.py
- tests/conftest.py
test_paths:
- tests/test_describe.py
- tests/test_help.py
- tests/steps/
docs: none
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
---

Every new step or option changes shared test files: the one snapshot tests/snapshots/describe.json, the shared help snapshots such as tests/snapshots/help/read.txt (it lists the steps) and the step list tests/steps/areas.py. So parallel tasks that add steps wait for each other (scope_held). Split them so a task that adds or changes a step touches only files of its own step or area: describe output stored per command (one file per command or step, like the help snapshots), and the step lists that tests check kept per area. The contract checks stay as strong as now: the whole describe document is still valid against the OpenCLI schema and matches the real CLI.

## Acceptance

- Given the current CLI, When the describe test runs, Then it compares the describe document command by command against one snapshot file per command, and the files hold together exactly what tests/snapshots/describe.json holds now [check: tests/test_describe.py]
- Given a new step is added in one area, When its snapshots are refreshed, Then the changed snapshot and list files are only those of that step or its area, not a file shared by all steps [check: tests/test_describe.py]
- Given a snapshot file of a command that no longer exists, When the tests run, Then they fail naming that file [check: tests/test_describe.py]

## How to test

The existing contract and help tests (pytest, syrupy) over the real Typer app; no new fixtures.

## Basis

IDEA-238; tests/test_describe.py, tests/test_help.py, tests/steps/areas.py, tests/steps/test_steps.py.

## Out of scope

- the describe output itself and the CLI
