---
id: SEMKIT-086
title: 'Bench tests: the load limit holds on the CI runner'
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
- scripts/bench.py
- tests/change/test_bench_part.py
- tests/corpus/test_bench_part.py
- tests/declension/test_bench_part.py
- tests/analysis/test_bench.py
- tests/core/test_bench_parts.py
- tests/pipeline/test_speed.py
- tests/conformance/test_speed.py
test_paths:
- tests/core/test_bench_parts.py
docs: none
tools: []
worker_args: null
class: mechanical
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-009
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
resident: null
tool: null
pr: null
translation: Лимит загрузки данных в тестах бенчмарка (0,5 с) срабатывает на CI-раннере
  впритык (0,506 с) и случайно валит гейт выпуска. Дать лимиту запас; лимит прогона
  120 с не меняется.
---

The 1M-phrase benchmark tests fail on the Gitea CI runner for the load limit, not for speed: tests/declension/test_bench_part.py failed in CI run 564 (main) and in run 588 (a release candidate) with `decline  1000000  load 0.506  seconds 26.86  SLOW`, `bench: over the limit of 120 s, load 0.5 s`. The run took 26.9 s of the 120 s allowed; only the first load of the data (0.506 s) was 6 ms over the 0.5 s limit. The same code passes on the Mac. The CI runner is shared and under load, so a limit this tight makes the release gate fail at random and costs a full CI round (8 to 30+ minutes) each time.

Make the load limit hold with a margin on the CI runner. The limit of the run (120 s) does not change. All the bench tests that run scripts/bench.py with its defaults are in scope: tests/change/test_bench_part.py, tests/corpus/test_bench_part.py, tests/declension/test_bench_part.py, and the others that call the script (find them with grep). Pick one place for the load limit (the default of scripts/bench.py, or one constant the tests pass as --load-limit) and keep the docstring of the script true.

## Acceptance

- Given an operation whose first load takes 0.6 s and whose run takes 30 s, When the bench runs with its defaults, Then the status is ok: the load limit has a margin over the 0.506 s that CI measured [check: tests/core/test_bench_parts.py]
- Given an operation whose run takes longer than 120 s, or whose load takes longer than the load limit, When the bench runs, Then it is SLOW and the exit code is 1 [check: tests/core/test_bench_parts.py]

## How to test

level: unit test of scripts/bench.py with a temporary part (as the existing tests of tests/core/test_bench_parts.py do) whose operation sleeps for the set times; seam: the exit code and the status column of the script; data: none

## Out of scope

- The 120 s limit of the run. The speed of any operation. Any other CI step.
