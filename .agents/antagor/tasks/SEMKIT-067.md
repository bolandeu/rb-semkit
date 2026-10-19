---
id: SEMKIT-067
title: 'Timed tests leave the default test run: the gate does not fail under load'
status: in_progress
attempts: 0
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: human
worker: claude-code
type: chore
owns_paths:
- tests/
- pyproject.toml
- README.md
test_paths: []
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
- uv run rb-release check
resident: null
tool: null
pr: null
translation: Тесты с лимитом времени (perf_counter) пометить маркером speed и убрать
  из обычного прогона (addopts -m 'not speed'); бенчмарк — uv run pytest -m speed,
  команда в README; гейт не падает под нагрузкой.
---

SEMKIT-065 attempt 1: Antagor's gate run took 17 min under machine load and failed at pytest; the same commit passed twice in about 4 min. Tests with wall-clock limits fail when the machine is busy. Suspects: tests/pipeline/test_speed.py, tests/lists/test_lists.py::test_a_million_rows_run_in_seconds (< 30 s), tests/serp/test_speed.py, tests/coverage/test_speed.py, and other tests that assert on time.perf_counter.

1. Find every semkit test that asserts on elapsed time (grep perf_counter, monotonic, time.time in tests/). Name them in the report.
2. Mark each one `@pytest.mark.speed`.
3. Leave them out of the default run: add `-m 'not speed'` to addopts in pyproject.toml, so `uv run pytest` and the gate skip them.
4. The benchmark run stays possible: `uv run pytest -m speed` runs them. Put this one command in README.md, next to the gate command.
5. tests/test_detach.py comes from the cli-generator template: do not edit it. If its waits are the problem, add an inbox gap for cli-generator.
6. `uv run rb-release check` ends with 'release: gate passed'; `uv run pytest -m speed` passes on an idle machine.

## Acceptance

- Given the tests, When 'uv run pytest' or the gate runs, Then no test that asserts on elapsed time runs, and the gate ends with 'release: gate passed' [check: uv run rb-release check]

## Basis

Reuse the existing pytest marker `speed` (pyproject.toml [tool.pytest.ini_options] markers) and tests/pipeline/test_speed.py, which already uses it.

## Read first

- `tests/pipeline/test_speed.py`
- `tests/lists/test_lists.py`
- `tests/test_detach.py`

## Out of scope

- Speeding up the code itself.
- tests/test_detach.py and other template files.
