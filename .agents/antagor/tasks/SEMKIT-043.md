---
id: SEMKIT-043
title: summary, the mean in the comparisons, recommended occurrences, --no-digits
  and --exclude
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
- src/rb_semkit/core/compare/
- src/rb_semkit/core/textstats/
- src/rb_semkit/core/summary/
- src/rb_semkit/steps/compare.py
- src/rb_semkit/steps/textstats.py
- src/rb_semkit/steps/summary.py
test_paths:
- tests/compare/
- tests/textstats/
- tests/summary/
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-007
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'summary, среднее в сравнениях, рекомендуемые вхождения, --no-digits
  и --exclude.


  summary — отчёт по любой таблице: на каждую числовую колонку count, mean, median,
  min, max. compare-stats и compare-grams — колонка среднего, --norm mean|median для
  вердикта (по умолчанию медиана, как раньше). compare-grams — --words N: need = норма
  плотности × N, have, add (минус — убрать), med_count (медиана вхождений), --per-text
  — плотность по каждой странице. --no-digits и --exclude LIST в text-stats, compare-stats,
  compare-grams: слова с цифрами или из списка не считаются нигде, как будто их нет.


  Приёмка: summary 100/200/600 → mean 300, median 200; без чисел — код 2; --norm mean
  меняет вердикт; need 10, have 4, add 6 и с --words 1000 — 20/16; med_count 3; колонки
  по url; --no-digits — 3 слова, --exclude года — 4; без новых опций вывод прежний
  плюс колонка среднего.


  Вне: parse-html, headings, coverage, ТЗ.'
---

Measures over a list of pages and one page against the list: the mean beside the median, the recommended number of occurrences for a text size, and leaving numbers or a word list out of the measures.

- summary: a report over any table: one row per numeric column with column, count, mean, median, min, max (rounded as the compare steps round). parse-html → text-stats → summary gives the table «all URLs: mean, median».
- compare-stats and compare-grams: a mean column beside the median; --norm mean|median picks the norm of the verdict (default median: the output of before plus the mean column; the tolerance applies to the chosen norm).
- compare-grams, the recommended occurrences: --words N (default: the words of my text) gives need = round(norm density x N), have (the occurrences in my text), add = need - have (negative: remove); and med_count, the median number of occurrences in the competitors. --per-text adds a density column per competitor text, named by its url column when the competitors table has one, else text_1, text_2 ...
- --no-digits and --exclude LIST (a list as other steps take lists: items, @FILE, @NAME) in text-stats, compare-stats and compare-grams: words with a digit, or the listed words (compared case- and ё-folded, as written, not by lemma), are left out of every count as if absent from the text, the word total included.

## Acceptance

- Given a table with columns words (100, 200, 600) and title (text), When summary runs, Then there is one row: words, count 3, mean 300, median 200, min 100, max 600; a table without numeric columns is refused with exit 2 naming the reason [check: tests/summary/test_summary.py]
- Given my text and three competitors with word counts 100, 200, 600, When compare-stats --norm mean runs, Then the row words has median 200, mean 300 and the verdict against 300; without --norm the verdict is against 200 as before [check: tests/compare/test_compare.py]
- Given a gram with densities 0.01, 0.02, 0.03 in the competitors and my text of 500 words holding it 4 times, When compare-grams --norm mean runs, Then need is 10, have 4, add 6; with --words 1000, need is 20 and add 16 [check: tests/compare/test_compare.py]
- Given a gram met 2, 3 and 10 times in the competitors, When compare-grams runs, Then med_count is 3 [check: tests/compare/test_compare.py]
- Given a competitors table with a url column, When compare-grams --per-text runs, Then there is a density column per competitor named by its url [check: tests/compare/test_compare.py]
- Given the text «диван 2026 года за 15000 рублей», When text-stats --no-digits runs, Then words is 3 (the two numbers left out); When --exclude года runs, Then words is 4 and «года» is in no count [check: tests/textstats/test_text_stats.py]
- Given --no-digits on compare-grams, When it runs, Then no gram holds a word with a digit [check: tests/compare/test_compare.py]
- Given the compare steps without the new options, When they run on the fixtures of before, Then the columns of before are unchanged (the mean column is added) [check: tests/compare/test_compare.py]

## How to test

Integration through the semkit CLI (the pipeline test runner) on small texts and tables written in the test modules.

## Basis

The compare area (its shared norm, rounding and verdicts), the text-stats words and counts; the option of a list as other steps take it.

## Read first

- `src/rb_semkit/core/compare/shared.py`
- `src/rb_semkit/core/compare/grams.py`
- `src/rb_semkit/core/textstats/functions.py`
- `docs/plans/html-and-brief.md`

## Out of scope

- parse-html, headings, coverage (other tasks)
- the copywriter brief and target counts per phrase
