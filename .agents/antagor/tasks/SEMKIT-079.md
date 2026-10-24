---
id: SEMKIT-079
title: 'Tests: run pytest in parallel with pytest-xdist'
status: publish
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
- pyproject.toml
- uv.lock
- tests/
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
- uv run pytest
resident: null
tool: null
pr: null
---

## Goal
The gate's pytest step takes ~4.8 min, most of the ~8 min CI run. Run the tests in parallel with pytest-xdist to bring it down.

## What to do
- Add `pytest-xdist` to the `dev` dependency group; update `uv.lock`.
- Add `-n auto` to `[tool.pytest.ini_options] addopts` (the gate runs `uv run pytest`, so addopts is the only lever; the gate itself is the template's and stays as is).
- Coverage must still work and still apply `fail_under` across all workers (pytest-cov combines xdist workers itself).
- mutmut: keep it serial — add `-p no:xdist` (or `-n 0`) to `[tool.mutmut] pytest_add_cli_args`.
- Make every test pass in parallel, many times in a row: fix tests that share state (a fixed path, the cwd, env, a module-level cache, a written snapshot) so each one is independent. Fix the tests, not the product code; if a product-code change seems needed, stop and ask in the inbox.
- The gate's contract step runs `pytest tests/test_contracts.py -vv` on its own and reads "N cases from K consumers" from the output. Check that `rb-release check` still reports that line correctly with `-n auto` in addopts. If xdist breaks that report, ask in the inbox before working around it.

## Done when
- `uv run pytest` is green 3 runs in a row; give the wall time before and after in the result.
- `uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@v1.26.3#subdirectory=gate" rb-release check` is green and its contract line names the same case count as before.

## Basis
pytest-xdist (`-n auto`) with pytest-cov's built-in xdist support; existing fixtures `tmp_path` / `monkeypatch` for isolation.

## Out of scope
- Changing the gate or the CI workflow (template-owned).
- Product code under src/.
- The timed tests (marker `speed`): they stay out of the default run.

## Feedback

### Answer to question #1

> With -n auto in addopts, the gate's contract step prints '0 cases' instead of '4 cases from 3 consumers': its regex '::test_contract\[x\] PASSED' does not match xdist -vv lines '[gw0] [ 50%] PASSED tests/..::test_contract[x]' (rb-release check v1.26.3, scripts/release.py contract_summary). Also the gate's 'vulnerability audit' fails on setuptools 84.0.0 (GHSA-xmj3-9gf7-h52w), already in the lock at HEAD, not from this task.
> Question: How do we keep the contract line correct?
> Options:
> 1. Fix the gate parser upstream in cli-generator (accept xdist lines); until then the line shows 0 cases
> 2. Work around in tests/conftest.py: switch xdist off (numprocesses=0) when the run targets only tests/test_contracts.py
> 3. Accept '0 cases' in the contract line
> Recommended: Fix the gate parser upstream in cli-generator (accept xdist lines); until then the line shows 0 cases

Option 2: in tests/conftest.py switch xdist off (numprocesses=0) when the run targets only tests/test_contracts.py; the gate line must say '4 cases from 3 consumers'. I report the parser to cli-generator myself; do not wait for it. setuptools GHSA-xmj3-9gf7-h52w: if a fixed version exists, bump it in uv.lock (uv lock --upgrade-package setuptools); if none exists, say so in the result and go on.

### Blocked: needs_scope (entries [{'n': 1, 'text': "With -n auto in addopts, the gate's contract step prints '0 cases' instead of '4 cases from 3 consumers': its regex '::test_contract\\[x\\] PASSED' does not match xdist -vv lines '[gw0] [ 50%] PASSED te"}])
