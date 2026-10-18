---
id: SEMKIT-040
title: 'ad-groups: small ad groups of one intent'
status: publish
attempts: 1
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
- src/rb_semkit/core/adgroups/
- src/rb_semkit/steps/adgroups.py
- src/rb_semkit/steps/dupes.py
- src/rb_semkit/core/vectors/cluster.py
- src/rb_semkit/data/SKILL.md
- src/rb_semkit/steps/vectors.py
test_paths:
- tests/adgroups/
- tests/conformance/test_cases.py
- tests/snapshots/help/steps/adgroups/ad-groups.txt
- tests/snapshots/describe.json
- tests/snapshots/help/read.txt
- tests/steps/areas.py
- tests/steps/test_steps.py
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-035
budget_usd: null
epic: E-006
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'ad-groups: мелкие рекламные группы одного интента.


  Фразы — дубли по смыслу друг друга (правило dupes --kind meaning) — в одной группе
  (транзитивно); --max-size N делит большие по вектору, детерминированно; имя группы
  — самая частотная (--freq) или первая. Опции dupes meaning работают так же. Строки
  не удаляются.


  Приёмка: три коммерческих варианта вместе, «угловой диван» отдельно; --max-size
  3 делит 7 фраз, повтор — то же; имя по частоте; --max-size 0 — код 2; --home москва:
  «диван москва» с «диван», «диван саратов» — нет.


  Вне: соответствие объявлений, посадочные (это assign-pages), изменения dupes.'
---

ad-groups: small ad groups of one intent from a core. Phrases that are duplicates by meaning of each other (the rule of dupes --kind meaning: close vectors and only non-refining words, synonyms, word forms, word order or the home city differ) share a group, taken transitively. --max-size N splits a larger group into parts of at most N by vector (nearest phrases together, deterministic). The group name is its most frequent phrase with --freq, else its first phrase. The options of dupes --kind meaning (--neutral, --synonyms, --home, --model, --threshold) work the same. Every phrase gets its group number and group name; no row is dropped.

## Acceptance

- Given «купить диван недорого», «диван купить», «недорогой диван купить» and «угловой диван», When ad-groups runs with the test encoder putting them close, Then the first three share a group and «угловой диван» is another group [check: tests/adgroups/test_adgroups.py]
- Given a group of 7 phrases and --max-size 3, When ad-groups runs, Then it is split into groups of at most 3, and two runs give the same groups [check: tests/adgroups/test_adgroups.py]
- Given --freq, When ad-groups runs, Then the group name is its most frequent phrase [check: tests/adgroups/test_adgroups.py]
- Given --max-size 0, When ad-groups runs, Then it is refused with exit 2 naming the flag [check: tests/adgroups/test_adgroups.py]
- Given --home москва, When ad-groups runs, Then «диван москва» and «диван» share a group and «диван саратов» does not [check: tests/adgroups/test_adgroups.py]

## How to test

Integration through the semkit CLI (the pipeline test runner) with the deterministic test encoder of E-005.

## Basis

Reuse the pair rule of dupes --kind meaning (do not copy it); the base of E-005.

## Read first

- `src/rb_semkit/core/dupes/functions.py`
- `docs/plans/vectors.md`
- `CONTEXT.md`

## Out of scope

- ad fit and landing pages (scenarios of the vectors plan; landing pages are assign-pages)
- changes to dupes

## Feedback

### Blocked: scope_held (holders ['SEMKIT-036', 'SEMKIT-041'], paths ['src/rb_semkit/core/vectors/cluster.py', 'src/rb_semkit/data/SKILL.md', 'src/rb_semkit/steps/vectors.py', 'tests/snapshots/describe.json', 'tests/snapshots/help/read.txt', 'tests/steps/areas.py', 'tests/steps/test_steps.py'])

SEMKIT-036, SEMKIT-041 finished; your kept work on src/rb_semkit/core/vectors/cluster.py, src/rb_semkit/data/SKILL.md, src/rb_semkit/steps/vectors.py, tests/snapshots/describe.json, tests/snapshots/help/read.txt, tests/steps/areas.py, tests/steps/test_steps.py is back in the worktree; main is merged into your branch where it merges clean

`main` changed since your work began, and merging it conflicts in:

- `src/rb_semkit/steps/vectors.py`
- `tests/steps/areas.py`
- `tests/steps/test_steps.py`

Merge it into your branch (`git merge main`), resolve each file keeping both behaviours, `git add` it and run the checks; do not commit: Antagor commits the merge with your work when the round ends (IDEA-201).

### Attempt 1: file docstring

- update the docstring of src/rb_semkit/core/vectors/cluster.py: +frequencies
- update the docstring of src/rb_semkit/steps/dupes.py: +refining_options
