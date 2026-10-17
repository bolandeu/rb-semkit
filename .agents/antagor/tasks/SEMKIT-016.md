---
id: SEMKIT-016
title: 'Core phrases in a text: count, texts and density of each core phrase, exact,
  by lemmas or in any word order'
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
type: feature
owns_paths:
- src/rb_semkit/core/coverage/
- src/rb_semkit/core/frame.py
test_paths:
- tests/coverage/
- tests/conformance/test_cases.py
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-014
budget_usd: null
epic: E-002
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**Вхождения ядра в текст.** sk.coverage(ядро, тексты, mode=...): для
  каждой фразы ядра — count (сколько раз в текстах), docs (в скольких текстах), density
  (плотность). Фразы с нулём остаются в таблице — это и есть недостающие ключи. Режимы:
  exact (как написано), lemmas (по леммам: «купить диваны» находит «купила диван»),
  any_order (леммы в одном отрезке текста в любом порядке). Через точку и запятую
  фраза не ищется.'
---

The SEO check of a text against its core. Add sk.coverage(core, texts, *, mode='exact', lemmatizer=BUNDLED, column=None, text_column=None) -> DataFrame. core: the core phrases (Series, or DataFrame with column=); texts: the texts, one per row (Series, or DataFrame with text_column=). The table has one row per distinct core phrase, in the core order: phrase, count (occurrences in all texts), docs (texts that hold it at least once), density (count x words of the phrase / words of all texts, as a share 0..1). first (the number of the word of the first text where the phrase first starts, 1-based, counting all words of that text; empty when count is 0: the earlier, the stronger the signal). A phrase with count 0 stays in the table: the missing phrases are the point. mode: 'exact' — the words of the phrase in a row, as written (case and ё folded); 'lemmas' — the same with lemmas of both sides («купить диваны» finds «купила диван»); 'any_order' — the lemmas of the phrase all inside one piece of text (one split_text phrase), in any order. Occurrences of one core phrase do not overlap; each core phrase is counted on its own (a longer phrase does not hide a shorter one). Speed: a core of 10 000 phrases over a text of 100 000 words in seconds (index the text pieces by word, do not scan the text per phrase).

## Acceptance

- Given the core ['кровать'] and the text 'Диван. Купить кровать', When coverage runs, Then first is 3 [check: tests/coverage/]

- Given the core ['купить диван', 'диван кровать', 'кресло'] and the text 'Купить диваны в Москве. Диван, кровать!', When sk.coverage(core, text, mode='lemmas') runs, Then купить диван has count 1, диван кровать has count 0 (a comma between) and кресло has count 0 [check: tests/coverage/]
- Given the core ['диван купить'] and that text, When mode='any_order', Then count is 1; When mode='exact', Then count is 0 [check: tests/coverage/]
- Given two texts and a phrase found twice in the first and once in the second, When coverage runs, Then count is 3, docs is 2 and density is count x words / all words [check: tests/coverage/]
- Given a wrong mode or a missing column, When coverage runs, Then sk.InvalidArguments names the argument and the allowed values [check: tests/coverage/]

## How to test

Unit tests in tests/coverage/ over small Series and DataFrames; one timing test (marked like the other speed tests) for 10 000 phrases x 100 000 words.

## Basis

Cut the texts with sk.split_text (SEMKIT-014), so a phrase never matches across a sentence end or punctuation. Compare words as the other areas do (norm_phrase: case folded, ё = е); lemmas through the Lemmatizer protocol (default the bundled one, lemmatizer= to change it). Declare the public name in __all__ of the new area.

## Read first

- `src/rb_semkit/core/text/matchers/phrases.py`
- `src/rb_semkit/core/analysis/frequency.py`
- `src/rb_semkit/core/morph/__init__.py`

## Out of scope

- Text metrics (nausea, water): SEMKIT-017.
- Reading files; the CLI command.
- Partial matches (a part of the phrase found) and recommendations of how many times to add a phrase.
