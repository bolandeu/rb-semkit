---
id: SEMKIT-015
title: 'N-grams and bigrams: a docs column, the number of texts (cells) that hold
  the gram'
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
type: feature
owns_paths:
- src/rb_semkit/core/analysis/frequency.py
- src/rb_semkit/core/analysis/__init__.py
- tests/conformance/areas/analysis.py
test_paths:
- tests/analysis/
- tests/conformance/case_files.py
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
translation: '**Колонка docs в n-граммах и биграммах.** Кроме count (сколько раз встретилось)
  — docs: в скольких текстах (ячейках) есть грамма. 10 статей конкурентов по одной
  в строке → split_text → ngrams: видно, какие слова и биграммы есть у 7 из 10. Сверка
  с надстройкой по count и sum не меняется.'
---

To compare a text with competitor texts, a gram needs two numbers: how often it occurs (count) and in how many texts (rows, cells) it occurs. Add the column docs to the tables of sk.ngrams and sk.bigrams, right after count: the number of distinct index values of the input whose phrases hold the gram at least once. With a one-phrase-per-row core it is the number of phrases with the gram. With phrases cut from texts by sk.split_text (it keeps the source index, so the index repeats) it is the number of texts. Sorting stays by count, then ngram. The conformance comparison with the add-in keeps checking count and sum only; docs is a semkit addition (say so in the docstring; no ADR: the add-in has no such column).

Also add the column forms when lemmas=True: the word forms met for the gram's lemmas, most frequent first, joined by ', ' (for a unigram «диван» — «диваны, диван, дивана»; for a longer gram the forms of each position joined by ' ' per occurrence variant is too much: give the distinct original spellings of the whole gram instead, most frequent first, at most 5). Without lemmas there is no forms column.

## Acceptance

- Given ['диваны диван', 'диваны'], When sk.ngrams(data, 1, lemmas=True) runs, Then the row диван has forms 'диваны, диван' [check: tests/analysis/]

- Given the Series ['диван кровать диван', 'диван'], When sk.ngrams(data, 1) runs, Then диван has count 3 and docs 2 [check: tests/analysis/]
- Given a Series with the index [0, 0, 1] (phrases cut from 2 texts) and диван in all three, When sk.ngrams runs, Then диван has docs 2 [check: tests/analysis/]
- Given the conformance cases of ngrams and bigrams, When the full gate runs, Then they pass unchanged [check: tests/analysis/]

## How to test

Unit tests in tests/analysis/ over small Series; the existing 1M bench must stay within its limit.

## Basis

_tally in frequency.py already maps each phrase to its grams; docs is the number of distinct source rows whose grams hold the gram (a gram repeated in one row counts once). Keep count and sum as they are: the conformance cases compare them with the add-in.

## Read first

- `src/rb_semkit/core/analysis/frequency.py`
- `tests/conformance/areas/analysis.py`

## Out of scope

- A comparison command (mine vs competitors): the CLI pipeline composes it.
- TF-IDF or other weights.
