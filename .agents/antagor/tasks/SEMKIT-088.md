---
id: SEMKIT-088
title: 'Tests: cap xdist workers and load the real models once'
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
- tests/conftest.py
- tests/vectors/
- tests/word_vectors/
- tests/relate/test_thesaurus_relations.py
test_paths:
- tests/vectors/test_extra.py
- tests/test_xdist_workers.py
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-009
spec_refs: []
checks: manual
resident: null
tool: null
pr: null
translation: 'Тесты съедают память: на 16 ГБ Mac три гейта разом (по 10 воркеров xdist,
  у каждого свои реальные модели ~2,4 ГБ) положили систему. Ограничить воркеры до
  3, все тесты с реальными моделями — в одну группу xdist, модели грузить один раз;
  замерить пик памяти до и после.'
---

The full test run takes too much memory. On 2026-10-26 about 20:03-20:07 MSK three gates ran at once on the 16 GB Mac (three tasks in review) and macOS killed processes and had to be power-reset (Jetsam reports: the largest python3.14 process 9.2 GB RSS, 31 python processes ~12.9 GB together). Causes found in the code:

- `addopts = "-n auto"` in pyproject.toml: 10 xdist workers on this machine, three runs at once = ~30 python processes.
- The tests marked `real_encoder` (tests/vectors/test_extra.py, test_quality.py, test_cluster_meaning.py, tests/word_vectors/test_quality_words.py, test_synonym_candidates.py, tests/relate/test_thesaurus_relations.py) open the real models of ~/Library/Caches/semkit (~2.4 GB), and every xdist worker that gets one of them loads its own copy.

Do:
1. Cap xdist in addopts: a fixed number of workers (3; not `auto`), and `--dist loadgroup`.
2. Put every test that opens the real models into ONE xdist group (`pytest.mark.xdist_group("real_models")`, set in one place: the collection hook of tests/conftest.py, by the `real_encoder` marker), so only one worker holds the models.
3. Load each real model once per worker and share it: the real encoder, the thesaurus and the word vectors that those tests open must come from a session-scoped cache, not be opened again by every test or module.
4. Measure the peak memory of the full run before and after: sum the RSS of the pytest process tree, sampled every second (a small script in the scratchpad, not in the repo), and write both numbers (GB) in the task result. The run is `uv run pytest` as the gate runs it.

The CI gate uses the same addopts; its time may grow a little, that is accepted. Do not change what any test checks.

## How to test

level: the full suite, as the gate runs it; seam: pytest only; data: the real models of the cache; measure the peak RSS of the process tree before and after

## Basis

Follow the existing real_encoder marker and the autouse fixtures of tests/conftest.py; pytest-xdist loadgroup

## Read first

- `tests/conftest.py`
- `pyproject.toml`

## Out of scope

- What any test asserts. The speed (marker speed) tests. The Antagor config. The CI workflow file.
