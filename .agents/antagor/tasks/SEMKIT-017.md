---
id: SEMKIT-017
title: 'Text metrics per text: characters, words, unique lemmas, water, classic and
  academic nausea, the top lemma'
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
- src/rb_semkit/core/textstats/
test_paths:
- tests/textstats/
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
translation: '**Метрики текста.** sk.text_stats: по каждому тексту (ячейке) — символы,
  символы без пробелов, слова, уникальные леммы, вода (доля стоп-слов), классическая
  тошнота (корень из числа самой частой леммы без стоп-слов), академическая (её доля),
  самая частая лемма. Определения свои и записаны точно в справке; под цифры Адвего
  не подгоняем.'
---

The usual SEO metrics of a text, the same numbers each run, over thousands of texts at once. Add sk.text_stats(data, *, lemmatizer=BUNDLED, column=None) -> DataFrame with the input index, one row per text (a cell is a text; an empty cell gives zeros): chars (all characters), chars_no_spaces, words, unique (distinct lemmas), water (share of stopwords among the words, 0..1), nausea_classic (square root of the count of the most frequent lemma that is no stopword, 2 decimals), nausea_academic (that count / words, 0..1), top (that lemma; a tie takes the first in the text). These are semkit's own definitions: write them in the docstring exactly as computed, so a reader can reproduce them (other services define water and nausea differently; do not chase any one of them). With a DataFrame and column= the metric columns are added after the column, as the other steps add theirs (see the Frame conventions in README «Output»).

## Acceptance

- Given the text 'Диван купить. Диван и диваны в Москве!', When sk.text_stats runs, Then words is 7, top is диван, nausea_classic is 1.73 (sqrt 3), nausea_academic is 3/7 and water is the share of и and в (2/7) [check: tests/textstats/]
- Given None, NaN or '' cells, When text_stats runs, Then those rows are zeros and top is '' [check: tests/textstats/]
- Given a DataFrame with column='text', When text_stats runs, Then the metric columns follow text and the other columns stay [check: tests/textstats/]

## How to test

Unit tests in tests/textstats/ with hand-counted small texts; one timing test (marked like the other speed tests) for 1 000 texts of 2 000 words.

## Basis

Words of a text: drop the punctuation of sk.chars('punctuation') (reuse its definition; keep in-word hyphens as one word, as split_text does), split on whitespace, fold case and ё (norm_phrase). Stopwords: the bundled list the n-grams use. Lemmas: the Lemmatizer protocol, default the bundled one. Declare the public name in __all__ of the new area.

## Read first

- `src/rb_semkit/core/analysis/frequency.py`
- `src/rb_semkit/core/text/matchers/chars.py`
- `src/rb_semkit/core/morph/__init__.py`

## Out of scope

- Readability indexes, spelling (SEMKIT-013 does typos), comparison with the core (SEMKIT-016).
- Matching the numbers of a particular service (Advego, Text.ru).
