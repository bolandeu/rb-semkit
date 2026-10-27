---
id: SEMKIT-089
title: 'Agent guide: the preposition limit of relate-phrases'
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
type: docs
owns_paths:
- src/rb_semkit/data/SKILL.md
- tests/snapshots/
test_paths: []
docs:
- src/rb_semkit/data/SKILL.md
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
- python3 scripts/check_command_docstrings.py
resident: null
tool: null
pr: null
translation: 'Описать в руководстве для агентов ограничение relate-phrases: предлоги
  отбрасываются, и пары вроде «диван с матрасом» / «матрас на диван» выходят same.
  Пример из 2 пар и что делает вызывающий.'
---

The agent guide (src/rb_semkit/data/SKILL.md, section «Relate phrases», «The limits») lists the dictionary gaps but not a limit found in the acceptance of E-009: prepositions are dropped, so two phrases with the same lemmas are `same` even when the preposition swaps the head noun. Found on the 200 labelled pairs (the test file in «Read first», SAME_BY_PREPOSITION): p136 «купить диван с ортопедическим матрасом» / «купить ортопедический матрас на диван», p174 «диван на ножках купить» / «ножки для дивана купить». 2 pairs of 200 come out `same`. A `same` phrase is glued without a SERP check, so the caller must look at such pairs.

Add to «The limits» two or three sentences: the limit, the two example pairs, and what the caller does (check by hand or by SERP a `same` pair whose preposition changes the head noun). Keep the style and the length of the section. Do not change any code or test.

## Read first

- `tests/relate/test_precision.py`

## Out of scope

- Any code or test. A rule that tells prepositions apart (a separate task if the marketer asks for it).
