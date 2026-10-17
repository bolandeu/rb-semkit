---
id: SEMKIT-019
title: 'Compare a text with competitor texts: gram density against the competitors''
  median, metrics against their median, BM25'
status: in_review
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
- src/rb_semkit/core/compare/
- docs/vba/conformance.md
- docs/vba/conformance/compare.md
test_paths:
- tests/compare/
- tests/conformance/areas/compare.py
- tests/conformance/cases/compare/bm25.tsv
- tests/conformance/cases/compare/compare_grams.tsv
- tests/conformance/cases/compare/compare_stats.tsv
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-014
- SEMKIT-015
- SEMKIT-017
budget_usd: null
epic: E-002
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**Сравнение текста с конкурентами (ТЗ по топу).** На вход — мой текст
  и тексты конкурентов как данные; semkit ничего не качает. compare_grams: по каждой
  лемме/n-грамме — у скольких конкурентов есть, медиана/мин/макс плотности (отсутствие
  = 0, чтобы медиана не завышалась), моя плотность и вердикт ниже/в норме/выше (±30
  % от медианы). compare_stats: мои метрики text_stats против медианы топа. bm25:
  релевантность каждого текста запросу с учётом редкости слов в корпусе — моё место
  среди конкурентов.'
---

The brief of a text by the top: how my text differs from the competitors' texts. semkit never fetches anything: the texts come in as data (other CLI services download and clean pages). Three functions; mine is one text (a str, or a Series or DataFrame cell), competitors are texts one per row (Series, or DataFrame with column=). (1) sk.compare_grams(mine, competitors, *, n=1, lemmas=True, stopwords=False, tolerance=0.3) -> DataFrame, one row per gram met in any competitor: ngram, docs (competitors that hold it), docs_share (docs / competitors, 0..1), median, min, max (the density of the gram in each competitor text = count of the gram / words of that text; a competitor without the gram counts as 0, so the median is not inflated), mine (its density in my text), verdict ('below', 'within', 'above': mine against median x (1 ± tolerance); when the median is 0, 'within' if mine is 0, else 'above'). Sorted by median, biggest first, then ngram. (2) sk.compare_stats(mine, competitors, *, tolerance=0.3) -> DataFrame, one row per numeric metric of sk.text_stats: metric, mine, median, min, max, delta (mine - median), verdict as above. (3) sk.bm25(texts, query, *, k1=1.5, b=0.75) -> Series of scores with the index of texts: Okapi BM25 of each text for the query, lemmas without stopwords on both sides; idf = ln((N - df + 0.5) / (df + 0.5) + 1), df and the average length over the given texts; to rank my text among the competitors pass all of them together. Round densities and scores to 4 decimals. No fixed norms (no «переспам» thresholds): the only norm is the competitors' median.

## Acceptance

- Given mine 'диван диван кресло' and the competitors ['диван стол', 'стол стул', 'диван диван диван стол'], When sk.compare_grams(mine, competitors) runs, Then диван has docs 2, median 0.5 (densities 0.5, 0, 0.75), mine 0.6667 and verdict above (over 0.5 x 1.3) [check: tests/compare/]
- Given those texts, When compare_grams runs, Then стол has docs 3, mine 0 and verdict below; кресло is absent (no competitor has it) [check: tests/compare/]
- Given those texts, When sk.compare_stats runs, Then the rows are the numeric metrics of sk.text_stats with mine, median, delta and verdict [check: tests/compare/]
- Given three texts and the query 'диван', When sk.bm25 runs, Then a text without диван scores 0 and the text with the most диван per length scores highest; the values match a hand computation [check: tests/compare/]
- Given an empty competitors list, a negative tolerance or n < 1, When called, Then sk.InvalidArguments names the argument [check: tests/compare/]

## How to test

Unit tests in tests/compare/ with hand-computed densities and BM25; one timing test (marked like the other speed tests): 1 text against 20 competitors of 5 000 words.

## Basis

Build on sk.split_text (SEMKIT-014), sk.ngrams with its docs column (SEMKIT-015) and sk.text_stats (SEMKIT-017); compare words as they do (case and ё folded, lemmas through the Lemmatizer protocol, the bundled stopwords). Declare the public names in __all__ of the new area.

## Read first

- `src/rb_semkit/core/analysis/frequency.py`
- `src/rb_semkit/core/frame.py`

## Out of scope

- Downloading or cleaning pages, HTML zones, titles and headings: other CLI services hand semkit plain texts.
- Embeddings and semantic similarity.
- Fixed SEO norms (nausea over 7 is spam and the like).
