---
id: SEMKIT-061
title: 'CI green on the homeserver runner: tests render help without CI colour and
  width; container --init for test_detach'
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
type: bugfix
owns_paths:
- tests/conftest.py
- .gitea/workflows/ci.yml
test_paths:
- tests/
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
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'Зелёный CI на homeserver: в тестах убрать влияние CI на цвет и ширину
  справки (autouse в conftest), в ci.yml container --init для test_detach.'
---

CI on the homeserver runner is red on v0.1.49 (jobs 277, 278): pytest has 164 failed, 5574 passed. The same gate is green on the Mac. The sysadmin found two causes.

1. Help renders differently in CI: 161 snapshots in tests/test_help.py, tests/scenarios/test_run.py::test_run_help_lists_the_scenarios_with_their_descriptions, and 1 test in tests/steps/test_steps.py. Gitea Actions sets CI=true and GITHUB_ACTIONS=true. Rich then forces a colour terminal with its own width (ANSI codes `\x1b[1m`, other line breaks). tests/test_help.py already passes HELP_ENV (COLUMNS=100, NO_COLOR=1, TERM=dumb), but not every test uses it, and the CI variables still win. Fix it once in tests/conftest.py with an autouse fixture: set NO_COLOR=1, TERM=dumb, COLUMNS=100, and delete FORCE_COLOR, CI, GITHUB_ACTIONS, TTY_COMPATIBLE and TTY_INTERACTIVE. Then the tests render the same in any environment. Check it locally: `CI=true GITHUB_ACTIONS=true FORCE_COLOR=1 uv run --extra vectors pytest` must be green.
2. tests/test_detach.py::test_killed_outright: the killed child stays in the process table as a zombie, because the job container has no init (PID 1 is not an init). Add `options: --init` to `container:` in .gitea/workflows/ci.yml.

## Read first

- `tests/test_help.py` — HELP_ENV, the width the snapshots use

## Out of scope

- The help text and the snapshots themselves: they stay as they are.

## Acceptance

- Given CI=true GITHUB_ACTIONS=true FORCE_COLOR=1 in the environment, When uv run --extra vectors pytest runs, Then it is green [check: uv run --extra vectors pytest]

## How to test

Run the whole suite with the CI variables set, as in the body; and with none set.

## Basis

tests/test_help.py HELP_ENV; the sysadmin's diagnosis of jobs 277 and 278.
