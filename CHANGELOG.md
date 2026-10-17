# Changelog

All notable changes to this project are documented here. Versions follow
[SemVer](https://semver.org/) (while at `0.x`, a minor bump may break).

The changelog is written by `antagor publish`; don't edit it by hand.

## v0.1.9 — 2026-10-17

### E-002 — semkit: the rest of the library — change, declension, analysis and the later functions

import rb_semkit gives every function of the add-in's menus except Mystem: each follows the VBA algorithm, the broken ones work as intended, and the conformance report lists for each function where it follows the VBA, where it differs and why.
Time: 1h since the epic was approved

- Core phrases in a text: count, texts and density of each core phrase, exact, by lemmas or in any word order (SEMKIT-016)

## v0.1.8 — 2026-10-17

### E-002 — semkit: the rest of the library — change, declension, analysis and the later functions

import rb_semkit gives every function of the add-in's menus except Mystem: each follows the VBA algorithm, the broken ones work as intended, and the conformance report lists for each function where it follows the VBA, where it differs and why.
Time: 1h since the epic was approved

- Morphology block: declension of nouns, adjectives and full names, irrelevant words, the pymorphy fallback, ready patterns and prepositional complements (SEMKIT-012)
- Text to phrases: split each cell at sentence and clause punctuation into phrase rows (SEMKIT-014)
- N-grams and bigrams: a docs column, the number of texts (cells) that hold the gram (SEMKIT-015)

## v0.1.7 — 2026-10-17

### E-002 — semkit: the rest of the library — change, declension, analysis and the later functions

import rb_semkit gives every function of the add-in's menus except Mystem: each follows the VBA algorithm, the broken ones work as intended, and the conformance report lists for each function where it follows the VBA, where it differs and why.
Time: 0.5h since the epic was approved

- Frame for parallel areas: discovered public names, data build parts, per-area conformance and benchmark; product text without the VBA (SEMKIT-010)

## v0.1.6 — 2026-10-17

### E-001 — semkit v1: phrase-processing library

import rb_semkit gives Python functions over a pandas Series or table column: find/remove/extract by matchers (chars, words, regex, phrases, markers, stopwords, POS), duplicates of 4 kinds, n-grams and bigrams with counts, lemmas, POS and wordforms on the bundled !SEMTools dictionary. 1M phrases are processed in minutes. The comparison with the add-in on reference examples is a separate task after this epic.
Time: 12.6h since the epic was approved

- Conformance: text matchers and markers in the shared case format, and the core report (SEMKIT-008)

## v0.1.5 — 2026-10-17

### E-001 — semkit v1: phrase-processing library

import rb_semkit gives Python functions over a pandas Series or table column: find/remove/extract by matchers (chars, words, regex, phrases, markers, stopwords, POS), duplicates of 4 kinds, n-grams and bigrams with counts, lemmas, POS and wordforms on the bundled !SEMTools dictionary. 1M phrases are processed in minutes. The comparison with the add-in on reference examples is a separate task after this epic.
Time: 12.3h since the epic was approved

- Analysis functions: follow the VBA where the conformance cases differ (SEMKIT-009)

## v0.1.4 — 2026-10-17

### E-001 — semkit v1: phrase-processing library

import rb_semkit gives Python functions over a pandas Series or table column: find/remove/extract by matchers (chars, words, regex, phrases, markers, stopwords, POS), duplicates of 4 kinds, n-grams and bigrams with counts, lemmas, POS and wordforms on the bundled !SEMTools dictionary. 1M phrases are processed in minutes. The comparison with the add-in on reference examples is a separate task after this epic.
Time: 12.2h since the epic was approved

- Conformance: analysis functions and bundled data against the add-in VBA (SEMKIT-006)
- Markers and phrase lists: extract the longest match (SEMKIT-007)

## v0.1.3 — 2026-10-17

### E-001 — semkit v1: phrase-processing library

import rb_semkit gives Python functions over a pandas Series or table column: find/remove/extract by matchers (chars, words, regex, phrases, markers, stopwords, POS), duplicates of 4 kinds, n-grams and bigrams with counts, lemmas, POS and wordforms on the bundled !SEMTools dictionary. 1M phrases are processed in minutes. The comparison with the add-in on reference examples is a separate task after this epic.
Time: 11.9h since the epic was approved

- Port the text matchers and markers from the add-in VBA (SEMKIT-005)

## v0.1.2 — 2026-10-16

### E-001 — semkit v1: phrase-processing library

import rb_semkit gives Python functions over a pandas Series or table column: find/remove/extract by matchers (chars, words, regex, phrases, markers, stopwords, POS), duplicates of 4 kinds, n-grams and bigrams with counts, lemmas, POS and wordforms on the bundled !SEMTools dictionary. 1M phrases are processed in minutes. The comparison with the add-in on reference examples is a separate task after this epic.
Time: 1.9h since the epic was approved

- Text matchers and marker lists: every v1 find/remove/extract (SEMKIT-002)
- Duplicates of 4 kinds (SEMKIT-003)
- N-grams, bigrams, counts and the 1M benchmark (SEMKIT-004)

## v0.1.1 — 2026-10-16

### E-001 — semkit v1: phrase-processing library

import rb_semkit gives Python functions over a pandas Series or table column: find/remove/extract by matchers (chars, words, regex, phrases, markers, stopwords, POS), duplicates of 4 kinds, n-grams and bigrams with counts, lemmas, POS and wordforms on the bundled !SEMTools dictionary. 1M phrases are processed in minutes. The comparison with the add-in on reference examples is a separate task after this epic.
Time: 1.3h since the epic was approved

- Core: bundled dictionary, lemmatizer and the find/remove/extract frame (SEMKIT-001)
