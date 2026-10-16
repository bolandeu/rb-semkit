---
id: SEMKIT-004
title: N-grams, bigrams, counts and the 1M benchmark
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
- src/rb_semkit/core/analysis/
- scripts/bench.py
test_paths:
- tests/analysis/
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
translation: 'n-граммы, биграммы, счётчики и замер на 1 млн фраз: sk.ngrams (слова
  или леммы, со стоп-словами или без, счёт и сумма веса), sk.bigrams без учёта порядка,
  sk.counts (слова, символы, вхождения, доля суммы, ABC). Скрипт замера: синтетические
  фразы, время дублей, n-грамм и лемм, ненулевой выход при превышении лимита.'
---

Frequency analysis of a semantic core and the 1M-phrase benchmark.

- sk.ngrams(data, n=1, lemmas=False, stopwords=True, weight=None, column=...): every run of n words (n = 1..N) over all phrases → a DataFrame with columns ngram, count (occurrences, as the add-in counts: «диван диван угловой» adds 2 to «диван»), sum (of the weight column per occurrence, when given), sorted by count desc then ngram. lemmas=True counts lemmas (bundled lemmatizer unless one is given); stopwords=False drops stopwords first.
- sk.bigrams(data, lemmas=False, stopwords=True, weight=None): as the add-in: per phrase lower-case the words, sort them, drop repeated words, then every pair i<j written as «w1+w2» («диван+купить» for both «купить диван» and «диван купить»); stopwords are kept by default, stopwords=False drops them first; same table shape and sort.
- sk.counts(data, what=...): per phrase: words, chars; per occurrence: occurrence count, occurrence number; share of sum (cumulative) and ABC class (A ≤ 80 %, B ≤ 95 %, C rest) by a weight column. Returns a Series / new column like other functions.
- A benchmark script: generates N synthetic phrases from the bundled dictionary (fixed seed) and times dupes (all kinds), ngrams (words, lemmas), lemmatize; prints a table and exits non-zero when an operation takes over a limit (default 120 s). --rows, --ops, --limit, --input options. With --input CSV (columns phrase, freq_msk_exact: a real core exported from Bukvarix) the phrases come from that file; when --rows is larger than the file, its phrases are repeated with a word shuffled so dupes still have work. An operation whose module is not present yet is reported as skipped.

## Acceptance

- Given pd.Series(['купить диван', 'диван угловой', 'купить стол']), When sk.ngrams(s, n=1) runs, Then it gives ngram/count rows диван 2, купить 2, стол 1, угловой 1 in that order [check: tests/analysis/test_ngrams.py]
- Given the same Series with weights [10, 5, 1] and n=2, When sk.ngrams(df, n=2, weight='freq', column='phrase') runs, Then rows are 'диван угловой' 1 5, 'купить диван' 1 10, 'купить стол' 1 1 [check: tests/analysis/test_ngrams.py]
- Given pd.Series(['купить диваны', 'диван купила']), When sk.ngrams(s, lemmas=True) runs, Then 'диван' 2 and 'купить' 2 [check: tests/analysis/test_ngrams.py]
- Given pd.Series(['диван в москве', 'москве диван']), When sk.bigrams(s) runs, Then rows 'диван+москве' 2, 'в+диван' 1, 'в+москве' 1; with stopwords=False only 'диван+москве' 2 [check: tests/analysis/test_bigrams.py]
- Given pd.Series(['диван диван угловой']), When sk.ngrams(s, n=1) runs, Then 'диван' 2, 'угловой' 1 [check: tests/analysis/test_ngrams.py] [check: tests/analysis/test_bigrams.py]
- Given weights [70, 20, 10], When sk.counts(..., what='abc') runs, Then classes A, B, C; what='words' on 'купить диван в москве' gives 4 [check: tests/analysis/test_counts.py]
- Given n=0, an unknown what, or a weight column that is not numeric, When called, Then InvalidArguments names the argument and the allowed values [check: tests/analysis/test_errors.py]
- Given a CSV with 3 phrases and --input it --rows 10 --ops ngrams, When the benchmark runs, Then it reports 10 rows built from the file's phrases and exits 0 [check: tests/analysis/test_bench.py]
- Given the benchmark with --rows 1000 --ops ngrams,lemmatize, When it runs, Then it prints one line per operation with rows and seconds and exits 0; with --limit 0 it exits non-zero naming the slow operation [check: tests/analysis/test_bench.py]

## How to test

Public library seam (import rb_semkit as sk) with small Series and DataFrames; the Lemmatizer protocol with a fake for lemmas=True; the benchmark script run in-process with small --rows.

## Basis

Reuse the core task's frame, tokenizer, stopword list loader and bundled lemmatizer. Plan §1.6 (v1 lines).

## Read first

- CONTEXT.md
- docs/plan.md

## Out of scope

- Permutations, parents/children, basis phrases, clustering, split by good/bad words (v2); typos; CLI.
