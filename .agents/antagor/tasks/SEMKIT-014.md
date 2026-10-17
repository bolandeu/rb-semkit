---
id: SEMKIT-014
title: 'Text to phrases: split each cell at sentence and clause punctuation into phrase
  rows'
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
- src/rb_semkit/core/split/
test_paths:
- tests/split/
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-010
budget_usd: null
epic: E-002
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**Текст → фразы.** Текст — это таблица из одной ячейки. Новый шаг sk.split_text
  режет каждую ячейку на фразы по концам предложений и знакам препинания внутри них,
  убирает знаки; одна строка становится несколькими. После него частотный словарь,
  биграммы, стоп-слова и леммы работают на обычном тексте (статья, отзывы) без склеек
  через точку. Wi-Fi, 2,5 и подобное не режутся. Чтение файла — в эпике CLI.'
---


A text is a table of one cell. Add sk.split_text(data, column=None): each cell is cut into phrases at sentence ends (. ! ? …) and at clause punctuation (, ; : dashes as separators, brackets, quotes « » " ' ), the punctuation is dropped, whitespace is collapsed, empty pieces are dropped; one input row becomes as many rows as it has phrases. Then every existing step works on prose: sk.ngrams(sk.split_text(text), 2, stopwords=False) is a bigram dictionary of an article without grams across a sentence end. Series in -> Series out, each phrase keeps the index of its source row (pandas explode). DataFrame with column= -> a DataFrame whose rows are the phrases: the column holds the phrase, the other columns repeat the source row, the index repeats the source index. Keep the case of the text. Keep inside a word: a hyphen (Wi-Fi, кто-то), an apostrophe, a decimal point or comma between digits (2.5, 2,5), a dot inside a number or an abbreviation is a separator only where a sentence ends (decide simply and document: 'т.д.' may split, that is acceptable). The function is not from the add-in: no conformance case, no VBA reference.

## Acceptance

- Given the Series ['Купить диван в Москве. Диван, кровать и кресло!'], When sk.split_text runs, Then the result is ['Купить диван в Москве', 'Диван', 'кровать и кресло'] with index [0, 0, 0] [check: tests/split/]
- Given that text, When sk.ngrams(sk.split_text(text), 2) runs, Then no gram holds punctuation and no gram crosses a sentence end ('москве диван' is absent) [check: tests/split/]
- Given a DataFrame with columns phrase and freq and two rows, When sk.split_text(df, column='phrase') runs, Then each phrase row repeats its source freq and index [check: tests/split/]
- Given 'Wi-Fi роутер за 2,5 тысячи', When split, Then it stays one phrase [check: tests/split/]
- Given None, NaN, '' or '...' cells, When split, Then they give no rows; a wrong column raises sk.InvalidArguments naming it [check: tests/split/]

## How to test

Unit tests over pandas Series and DataFrame in tests/split/; a 1M-row timing is not needed (one pass of a compiled regex).

## Basis

Reuse the input handling of the other areas (Series, or DataFrame with column=; NaN/None are empty strings) and the error type sk.InvalidArguments. The new area declares its public name in __all__; the root finds it (no edit of rb_semkit/__init__.py). Punctuation is the class of sk.chars("punctuation") (src/rb_semkit/core/text/matchers/chars.py), so both steps mean the same characters; reuse its definition, do not write a second list. The difference from sk.remove(x, sk.chars("punctuation")) + sk.spaces("extra"): those clean a cell in place and glue sentences («в Москве. Диван» → «в Москве Диван»); split_text first cuts at the boundaries, then cleans each piece, keeping the in-word exceptions above.

## Read first

- `src/rb_semkit/__init__.py`
- `src/rb_semkit/core/analysis/frequency.py`
- `src/rb_semkit/core/text/base.py`
- `src/rb_semkit/core/text/matchers/chars.py`

## Out of scope

- Reading a text file or stdin (the CLI epic, through dataio).
- Sentence splitting by a model or a library (razdel, nltk): a regex is enough for n-grams.
- Lowercasing, stopwords, lemmas: the following steps do them.
