---
id: SEMKIT-053
title: 'decline: a noun already in the genitive inside a group is declined again (продукции
  → продукций)'
status: queue
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
- src/rb_semkit/core/declension/
- tests/declension/
test_paths:
- tests/declension/
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-050
budget_usd: null
epic: null
spec_refs: []
checks:
- uv run --extra vectors pytest
resident: null
tool: null
pr: null
translation: 'decline: существительное, уже стоящее в родительном после главного,
  склоняется повторно (продукции → продукций, федерации → федераций).'
---

decline genitive on noun groups whose second noun is already in the genitive declines that noun again, as a nominative plural: «импорт продукции» → «импорта продукций», «ввоз на территорию российской федерации» → «ввоза на территорию российской федераций». The help says a word already in another case stays; a noun right after the head noun in the genitive (its complement) must stay as it is.

The head noun and its adjectives decline; a dependent noun group in the genitive after the head stays.

## Acceptance

- Given «импорт продукции», When decline genitive runs, Then it gives «импорта продукции» [check: tests/declension/]
- Given «ввоз на территорию российской федерации», When decline genitive runs, Then it gives «ввоза на территорию российской федерации» [check: tests/declension/]
- Given «импорт товаров» and «таможенное оформление товаров», When decline genitive runs, Then they give «импорта товаров» and «таможенного оформления товаров» [check: tests/declension/]
- Given «красный диван», When decline genitive runs, Then it gives «красного дивана» as before [check: tests/declension/]

## How to test

Unit tests of the phrase declension and one run through the semkit CLI runner.

## Basis

core/declension/phrase.py: how a noun that is not the first is chosen to decline; the ambiguity of продукции (gen sg / nom pl).

## Out of scope

- The agree step (SEMKIT-050); other cases than the found ones.
