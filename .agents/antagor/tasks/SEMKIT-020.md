---
id: SEMKIT-020
title: 'List tools: compare two lists (both, either, only first, only second) by a
  duplicate kind; strip characters at word edges'
status: queue
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
- src/rb_semkit/core/lists/
- src/rb_semkit/core/text/matchers/edges.py
- src/rb_semkit/core/dupes/functions.py
test_paths:
- tests/lists/
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-002
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**Списки: сравнение двух и обрезка символов по краям слов.** sk.compare_lists(первый,
  второй, op=both|either|first|second, kind=exact|explicit|implicit|lemmas) — пересечение,
  объединение, только в первом, только во втором; «одна и та же фраза» — как в sk.dupes
  (с перестановками, по леммам). sk.edges(start, end) — убирает символы в начале и
  конце слов: операторы Директа + ! [ ] и знаки вроде ? . (как «убрать символы в начале/конце
  слова» у Букварикса).'
---

Two small steps the usual keyword-list tools have and semkit lacks as one call. (1) sk.compare_lists(first, second, *, op='both', kind='exact', lemmatizer=None, column=None, second_column=None) -> Series of phrases: op 'both' — phrases of first that are also in second; 'either' — first then second, each phrase once; 'first' — only in first; 'second' — only in second. «The same phrase» is the key of sk.dupes for kind (exact; explicit: case, ё, spaces; implicit: any word order; lemmas). The result keeps the spelling of its first occurrence and the order of the input; a phrase repeated in one list comes once. Empty cells are never phrases. (2) sk.edges(start='', end='') -> a matcher, remove only: cuts the given characters from the start and from the end of each word (any run of them), e.g. sk.remove(x, sk.edges(start='+-!["', end='?!.]"')) turns '+купить !диван? [москва]' into 'купить диван москва'; the characters inside a word stay ('wi-fi'); a word that was only those characters disappears; no double spaces, none at the edges. Both are semkit additions, not from the add-in: no conformance case.

## Acceptance

- Given first ['Купить диван', 'кресло', 'стол'] and second ['диван купить', 'стул'], When sk.compare_lists(first, second, op='both', kind='implicit'), Then ['Купить диван']; When op='first', Then ['кресло', 'стол']; When op='second', Then ['стул']; When op='either', Then ['Купить диван', 'кресло', 'стол', 'стул'] [check: tests/lists/]
- Given first ['купить диваны'] and second ['купить диван'], When op='both', kind='lemmas', Then ['купить диваны']; When kind='exact', Then [] [check: tests/lists/]
- Given '+купить !диван? [москва] wi-fi -', When sk.remove(x, sk.edges(start='+-![', end='?!.]')), Then 'купить диван москва wi-fi' [check: tests/lists/]
- Given a wrong op or kind, When called, Then sk.InvalidArguments names it and the allowed values [check: tests/lists/]

## How to test

Unit tests in tests/lists/ over small Series and DataFrames; 1M rows for compare_lists in seconds (marked like the other speed tests).

## Basis

Comparison reuses the keys of sk.dupes (kinds exact, explicit, implicit, lemmas; it already takes against=): one notion of «the same phrase» in the whole package. The edge matcher follows the Matcher pattern of spaces.py (remove only) and declares its name in __all__ of its module.

## Read first

- `src/rb_semkit/core/dupes/functions.py`
- `src/rb_semkit/core/text/matchers/spaces.py`
- `src/rb_semkit/core/text/base.py`

## Out of scope

- Lower case, ё → е in the text, empty rows, duplicates, combinations: other steps already do them (the change block, sk.cells('empty'), sk.dupes, the combinations of SEMKIT-013).
- More than two lists at once: chain the calls.

## Feedback

### Attempt 1: file docstring

- update the docstring of src/rb_semkit/core/dupes/functions.py: +key_function
