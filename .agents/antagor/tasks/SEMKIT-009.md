---
id: SEMKIT-009
title: 'Analysis functions: follow the VBA where the conformance cases differ'
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
type: bugfix
owns_paths:
- src/rb_semkit/core/analysis/counts.py
- src/rb_semkit/core/analysis/frequency.py
- src/rb_semkit/core/morph/functions.py
- src/rb_semkit/core/morph/lemmatizer.py
- tests/conformance/cases/
test_paths:
- tests/analysis/
- tests/core/
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-006
budget_usd: null
epic: E-001
spec_refs: []
checks:
- uv run pytest tests/analysis tests/core tests/conformance -q
resident: null
tool: null
pr: null
translation: 'Функции анализа по VBA там, где сверка SEMKIT-006 нашла расхождения:
  счётчики без учёта регистра, ё=е, пустые без счёта; доля накопительным итогом в
  порядке строк и новая «доля от суммы»; биграммы без стоп-слов оставляют стоп-слово
  внутри; словоформы по алфавиту и через лемму для словоформы.'
---

The conformance cases of SEMKIT-006 (tests/conformance/cases, xfail rows reported in its inbox #1–#5) show five places where the analysis functions differ from the VBA without an ADR 0005 reason. Make the code follow the VBA, with the ADR 0005 deviations, and turn those xfail rows into passing ones.

1. counts(what='count' / 'number'): key a phrase as the VBA does (`––k—` L1875, `–kko` L2166: UCase), plus ADR 0005: ё = е; an empty cell gets no count (empty value), not a group of its own.
2. counts(what='share'): the cumulative share in row order, as «Накопительным итогом» `–koo` (L2489); add the kind 'share_of_total' = value / SUM, as «Долю от суммы» `–kok` (L1607). A sum of 0 gives empty values, not an error.
3. ngrams(n=2, stopwords=False): as «Биграмм без учета стоп-слов» `—k··` (L2781) → `ka–a` (L1005): a stopword between two words stays inside the gram ('купить диван в москве' gives 'купить диван' and 'диван в москве'); ADR 0005: stopwords in any case.
4. wordforms(): the forms of the lemma in alphabetical order (the dictionary order `––aa` L380 writes), no duplicates.
5. wordforms() of a word that is not a lemma: lemmatize it first, then give the forms of that lemma (`––aa`: aaa(LCase(word))); the input word is not repeated (ADR 0005).
6. Docstrings: the handler and lines, and the ADR 0005 line where it applies. In tests/conformance/cases drop the xfail of the rows this fixes; do not change their vba or expected.

## Acceptance

- Given 'диван | Диван | стол', When counts(what='count'), Then '2 | 2 | 1'; given 'ёж | еж', Then '2 | 2'; given 'диван |  | ', Then '1 |  | ' [check: tests/analysis/test_counts_vba.py]
- Given weights 20, 50, 30 in that row order, When counts(what='share'), Then 0.2, 0.7, 1; When counts(what='share_of_total'), Then 0.2, 0.5, 0.3 [check: tests/analysis/test_counts_vba.py]
- Given 'купить диван в москве', When ngrams(n=2, stopwords=False), Then the grams are 'купить диван' and 'диван в москве' [check: tests/analysis/test_ngrams_vba.py]
- Given 'диваны', When wordforms, Then the forms of 'диван' in alphabetical order, each once [check: tests/core/test_wordforms_vba.py]
- Given the conformance cases, When they run, Then the rows of SEMKIT-006 inbox #1–#5 pass without xfail [check: uv run pytest tests/analysis tests/core tests/conformance -q]

## How to test

Public library seam (import rb_semkit as sk): pytest cases above, plus the conformance TSV rows.

## Basis

docs/vba/analysis.md §1.4, §2, §4 and docs/vba/matchers.md for the stopword bigrams; ADR 0005; the SEMKIT-006 inbox findings #1–#5 with their case ids.

## Read first

- `docs/adr/0005-port-vba-fix-defects.md`
- `docs/vba/analysis.md`

## Out of scope

- Other analysis functions; the case values (vba, expected) of SEMKIT-006.
