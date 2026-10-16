# Changelog

All notable changes to this project are documented here. Versions follow
[SemVer](https://semver.org/) (while at `0.x`, a minor bump may break).

The changelog is written by `antagor publish`; don't edit it by hand.

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
