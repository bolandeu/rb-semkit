---
id: SEMKIT-007
title: 'Markers and phrase lists: extract the longest match'
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
type: feature
owns_paths:
- src/rb_semkit/core/markers/
- src/rb_semkit/core/text/matchers/phrases.py
test_paths:
- tests/markers/
- tests/matchers/
- tests/matchers_vba/
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
- uv run pytest tests/markers tests/matchers tests/matchers_vba -q
resident: null
tool: null
pr: null
translation: 'Маркеры и списки фраз: извлекать самое длинное совпадение («как сделать»,
  а не «как»), при равной длине — порядок списка; find/remove на тех же участках.
  Отход от VBA la— записан в ADR 0005.'
---

The marker extraction follows the VBA `la—` (docs/vba/matchers.md S10): for each word that starts a list item it takes the first item, in list order, that the phrase holds, so a short item hides a longer one: questions on 'как сделать диван своими руками' gives 'как', not 'как сделать'. ADR 0005 now asks for the longest match.

1. For each word that starts one or more items, take the longest item (in words, then in characters) that the phrase holds from that word; a tie keeps the list order.
2. Matched words are consumed: a later word inside a taken item does not start another one.
3. The same rule for sk.markers (every list, with_prepositions too) and sk.phrases extract; find and remove give the same spans.
4. Update the docstrings (the ADR 0005 line) and the rows of tests/matchers_vba that change, with the VBA value in a comment.

## Acceptance

- Given the questions list and 'как сделать диван своими руками', When sk.extract with sk.markers('questions'), Then the result is 'как сделать' [check: tests/markers/test_longest.py]
- Given sk.phrases(['нижний', 'нижний новгород']) and 'купить диван нижний новгород', When extract, Then 'нижний новгород'; When remove, Then 'купить диван' [check: tests/markers/test_longest.py]
- Given two items of equal length from one word, When extract, Then the one earlier in the list [check: tests/markers/test_longest.py]

## How to test

Public library seam (import rb_semkit as sk): pytest cases in tests/markers/test_longest.py with the bundled lists.

## Basis

docs/vba/matchers.md S10 (la—, DeletePhrases), ADR 0005, the SEMKIT-005 code of core/markers/matcher.py and phrases.py.

## Read first

- `docs/adr/0005-port-vba-fix-defects.md`
- `docs/vba/matchers.md`

## Out of scope

- Other matchers; the marker lists themselves.
