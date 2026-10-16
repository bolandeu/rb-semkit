---
id: SEMKIT-003
title: Duplicates of 4 kinds
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
- src/rb_semkit/core/dupes/
test_paths:
- tests/dupes/
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-001
budget_usd: null
epic: E-001
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'Дубли 4 видов: sk.dupes — точные, явные (после нормализации), неявные
  (другой порядок слов), по словоформам (леммы). Действия: пометить кроме первого,
  пометить все, удалить кроме первого; сравнение с другой колонкой (against). Пустые
  фразы — не дубли. Работа по уникальным ключам для 1 млн фраз.'
---

Duplicates of a semantic core, on the frame of the core task: sk.dupes(data, kind=..., action=..., against=None, lemmatizer=None, column=...).

Kinds: exact (equal strings); explicit (equal after the shared normalization: case, ё→е, spaces); implicit (equal multiset of normalized words, other word order); lemmas (equal multiset of lemmas: implicit by wordforms; uses the bundled lemmatizer when none is given). Actions: mark_except_first (bool, the first of each group False), mark_all (every member of a group with 2+ phrases True), drop (keep the first, drop the rest; index of kept rows unchanged). against: another Series or column; then a phrase is a duplicate when its key is in the other one, by the same kinds. Empty phrases are never duplicates of each other. Works on unique keys and maps back, for 1M phrases.

## Acceptance

- Given pd.Series(['купить диван', 'Купить  диван', 'диван купить', 'купить диваны', 'стол']), When sk.dupes with kind exact, explicit, implicit, lemmas and action mark_except_first runs, Then it gives [F,F,F,F,F], [F,T,F,F,F], [F,T,T,F,F], [F,T,T,T,F] [check: tests/dupes/test_dupes.py]
- Given the same Series and kind implicit, When action mark_all and drop run, Then mark_all gives [T,T,T,F,F] and drop returns the rows 0, 3, 4 with their index [check: tests/dupes/test_dupes.py]
- Given a DataFrame column 'phrase' and against=pd.Series(['диван купить']), When sk.dupes(df, kind='implicit', action='mark_all', against=..., column='phrase') runs, Then column 'phrase_dupes' marks the rows 0, 1, 2 and 'phrase' is unchanged [check: tests/dupes/test_dupes.py]
- Given pd.Series(['ёлка купить', 'елка купить']), When kind explicit runs, Then the second is a duplicate (ё = е) [check: tests/dupes/test_dupes.py]
- Given ['', None, ''], When any kind runs, Then no row is marked (empty phrases are never duplicates) [check: tests/dupes/test_dupes.py]
- Given kind='nope' or action='nope', When called, Then InvalidArguments lists the allowed kinds or actions and nothing is changed [check: tests/dupes/test_dupes.py]
- Given a fake lemmatizer mapping 'диваны' → 'диван', When kind lemmas runs with it, Then it uses the fake only [check: tests/dupes/test_dupes.py]

## How to test

Public library seam (import rb_semkit as sk) with small Series and DataFrames; the Lemmatizer protocol with a fake.

## Basis

Reuse the core task's frame (input/output, NaN, column=, InvalidArguments), tokenizer, norm_phrase and the bundled lemmatizer. Plan §1.3; the Duplicate term in the glossary.

## Read first

- CONTEXT.md
- docs/plan.md

## Out of scope

- Fuzzy or typo duplicates (Levenshtein: later); word repeats inside one phrase (the matchers block); CLI.
