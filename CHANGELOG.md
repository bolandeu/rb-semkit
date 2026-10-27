# Changelog

All notable changes to this project are documented here. Versions follow
[SemVer](https://semver.org/) (while at `0.x`, a minor bump may break).

The changelog is written by `antagor publish`; don't edit it by hand.

## v0.2.0 — 2026-10-27

### E-009 — relate-phrases: the class of each phrase of a topic (same, variation, refinement, other)

One step, relate-phrases, gives each phrase of a topic its class (same, variation, refinement or other), the phrase it belongs to (of), the first phrase of its group (group) and the reason (the rule and the word link), by dictionaries and lemmas only: no network, no vectors, no LLM at run time. About 1000 phrases run in seconds. The caller sorts the phrases (by frequency) and checks the variations and the other phrases by SERP.
Time: 15.5h since the epic was approved

- relate-phrases acceptance: the table end to end, precision on 200 pairs, speed, documents (SEMKIT-085)
- Tests: cap xdist workers and load the real models once (SEMKIT-088)

## v0.1.70 — 2026-10-27

### E-009 — relate-phrases: the class of each phrase of a topic (same, variation, refinement, other)

One step, relate-phrases, gives each phrase of a topic its class (same, variation, refinement or other), the phrase it belongs to (of), the first phrase of its group (group) and the reason (the rule and the word link), by dictionaries and lemmas only: no network, no vectors, no LLM at run time. About 1000 phrases run in seconds. The caller sorts the phrases (by frequency) and checks the variations and the other phrases by SERP.
Time: 13.9h since the epic was approved

- relate-phrases dictionary links: synsets, POS-synonymy and runs of words as units (SEMKIT-082)
- Bench tests: the load limit holds on the CI runner (SEMKIT-086)
- relate-phrases: a link source knows every word of the table, so the order of the rows does not change a refinement (SEMKIT-087)

## v0.1.69 — 2026-10-26

### E-009 — relate-phrases: the class of each phrase of a topic (same, variation, refinement, other)

One step, relate-phrases, gives each phrase of a topic its class (same, variation, refinement or other), the phrase it belongs to (of), the first phrase of its group (group) and the reason (the rule and the word link), by dictionaries and lemmas only: no network, no vectors, no LLM at run time. About 1000 phrases run in seconds. The caller sorts the phrases (by frequency) and checks the variations and the other phrases by SERP.
Time: 1.5h since the epic was approved

- relate-phrases core: classes, of, group and reason over lemmas, the step, the link seam (SEMKIT-081)
- relate-phrases Latin reading: web = веб, bosch = бош (SEMKIT-083)
- relate-phrases --synonyms: groups of synonyms of the caller, items of several words (SEMKIT-084)

## v0.1.68 — 2026-10-26

### Outside epics

- Template v1.27.3: update from v1.26.3 (SEMKIT-080)

## v0.1.67 — 2026-10-24

### Outside epics

- Tests: run pytest in parallel with pytest-xdist (SEMKIT-079)

## v0.1.66 — 2026-10-23

### Outside epics

- Table steps: fill-down counts the filled cells; lookup leaves unmatched cells empty and names its FILE (SEMKIT-078)

## v0.1.65 — 2026-10-23

### E-008 — Table steps of the pipeline: group, split, lookup, fill down, sample, shuffle, unpivot

One semkit pipeline does these table operations in memory, as steps: group-rows, split-rows, lookup, fill-down, sample-rows, shuffle-rows, unpivot. Each is an atomic step with its help and examples, and each is a public function of the library.
Time: 1h since the epic was approved

- Step lookup: columns of a lookup table by a key phrase (SEMKIT-077)

## v0.1.64 — 2026-10-23

### E-008 — Table steps of the pipeline: group, split, lookup, fill down, sample, shuffle, unpivot

One semkit pipeline does these table operations in memory, as steps: group-rows, split-rows, lookup, fill-down, sample-rows, shuffle-rows, unpivot. Each is an atomic step with its help and examples, and each is a public function of the library.
Time: 0.7h since the epic was approved

- Shape steps group-rows, split-rows, unpivot (SEMKIT-076)

## v0.1.63 — 2026-10-23

### E-008 — Table steps of the pipeline: group, split, lookup, fill down, sample, shuffle, unpivot

One semkit pipeline does these table operations in memory, as steps: group-rows, split-rows, lookup, fill-down, sample-rows, shuffle-rows, unpivot. Each is an atomic step with its help and examples, and each is a public function of the library.
Time: 0.4h since the epic was approved

- Row steps fill-down, sample-rows, shuffle-rows, and the frame of the table steps (SEMKIT-075)

## v0.1.62 — 2026-10-21

### Outside epics

- Template v1.26.3: package docs keep no retelling of Antagor's process (SEMKIT-074)

## v0.1.61 — 2026-10-21

### Outside epics

- Comments, docstrings, README and help name no cli-generator internal file and no numbered Standard section (SEMKIT-071)

## v0.1.60 — 2026-10-21

### Outside epics

- Template v1.25.8: the gate with the CI colour fix on Python 3.11 (SEMKIT-073)

## v0.1.59 — 2026-10-21

### Outside epics

- Help and describe snapshots are generated files: tests/snapshots/** linguist-generated (SEMKIT-070)

## v0.1.58 — 2026-10-20

### Outside epics

- Rename scenario to workflow: code, help, bundled folder and the project folder .rb_semkit/workflows/ (SEMKIT-069)

## v0.1.57 — 2026-10-20

### Main

- chore(antagor): checks call the gate through uvx at template v1.23.1


## v0.1.56 — 2026-10-20

### Outside epics

- Template update to the newest tag (v1.23.1+): the gate through uvx from cli-generator, rb-cli-core gone (SEMKIT-068)

## v0.1.55 — 2026-10-19

### Outside epics

- Timed tests leave the default test run: the gate does not fail under load (SEMKIT-067)

## v0.1.54 — 2026-10-19

### Main

- Reapply "chore(antagor): checks call the gate from rb-cli-core (release.py is gone)"
- Revert "chore(antagor): checks call the gate from rb-cli-core (release.py is gone)"
- chore(antagor): checks call the gate from rb-cli-core (release.py is gone)


## v0.1.53 — 2026-10-19

### Outside epics

- Template v1.20.7: sysadmin contract (Gitea source, Gitea CI, secret scan, registry deps) and the gate from rb-cli-core (SEMKIT-065)

## v0.1.52 — 2026-10-18

### Outside epics

- Template update: copier update to cli-generator v1.18.2, help snapshots refreshed, gate green (SEMKIT-063)

## v0.1.51 — 2026-10-18

### Outside epics

- write: a refused --columns/--rename gets its own action line, not the 'folder is writable' one (SEMKIT-062)

## v0.1.50 — 2026-10-18

### Outside epics

- CI green on the homeserver runner: tests render help without CI colour and width; container --init for test_detach (SEMKIT-061)

## v0.1.49 — 2026-10-18

### Outside epics

- write --columns and --rename: choose, order and rename the output columns (dataio v0.1.26) (SEMKIT-059)

## v0.1.48 — 2026-10-18

### Outside epics

- semkit run NAME: named scenarios of semkit's own steps, bundled or in the project, with parameters and help (SEMKIT-057)

## v0.1.47 — 2026-10-18

### Outside epics

- semkit docs: examples without the command path, inherited options only (InSpectra rules of the template) (SEMKIT-058)

## v0.1.46 — 2026-10-18

### Outside epics

- CI on the homeserver runner: .gitea/workflows/ci.yml runs the release gate; ruff format fix in tests/conftest.py (SEMKIT-060)

## v0.1.45 — 2026-10-18

### Outside epics

- Table bricks: use-column switches the working column, sort-rows orders the rows by a column (SEMKIT-056)

## v0.1.44 — 2026-10-18

### Outside epics

- Every step's docstring to the help standard: one-line summary, option lines, short examples with results (SEMKIT-055)

## v0.1.43 — 2026-10-18

### Outside epics

- Help standard and semkit docs: a deterministic human document of every command and step for InSpectra (SEMKIT-054)

## v0.1.42 — 2026-10-18

### Outside epics

- nearest --to TEXT: the texts to match given on the command line instead of a file (SEMKIT-052)

## v0.1.41 — 2026-10-18

### Outside epics

- synonym-candidates: synonyms of any number of words, both ways (a word, a phrase), from the thesaurus (SEMKIT-051)

## v0.1.40 — 2026-10-18

### Outside epics

- decline: a noun already in the genitive inside a group is declined again (продукции → продукций) (SEMKIT-053)

## v0.1.39 — 2026-10-18

### Outside epics

- linear-combinations joins each combination into a phrase column; a step agree puts the words of a phrase in agreement (SEMKIT-050)

## v0.1.38 — 2026-10-18

### Outside epics

- read --text: phrases from the command line; a pipeline without write prints a table (SEMKIT-049)

## v0.1.37 — 2026-10-18

### Outside epics

- parse-html keeps the zone names when the HTML column is text; the steps over pages take the column text by default (SEMKIT-048)

## v0.1.36 — 2026-10-18

### Outside epics

- A separate default threshold for clusters by meaning: 0.975 for e5-small, the pair threshold stays 0.97 (SEMKIT-047)

## v0.1.35 — 2026-10-18

### Outside epics

- Test snapshots and step lists split by step, so tasks that add steps do not wait for each other (SEMKIT-046)

## v0.1.34 — 2026-10-18

### E-006 — Vectors: primitives by meaning for SEO, texts and ads

semkit has the atomic commands nearest, split-paragraphs, coverage-meaning, ad-groups and synonym-candidates; long texts are compared by a page vector. The scenarios built from them (core gaps, competing pages, internal links, ad fit, competitor topics) are recorded in the vectors plan for later.
Time: 2.3h since the epic was approved

- coverage-meaning: core phrases a text covers by meaning (SEMKIT-039)

## v0.1.33 — 2026-10-18

### E-006 — Vectors: primitives by meaning for SEO, texts and ads

semkit has the atomic commands nearest, split-paragraphs, coverage-meaning, ad-groups and synonym-candidates; long texts are compared by a page vector. The scenarios built from them (core gaps, competing pages, internal links, ad fit, competitor topics) are recorded in the vectors plan for later.
Time: 2.1h since the epic was approved

- nearest, the page vector and split-paragraphs (SEMKIT-038)

## v0.1.32 — 2026-10-18

### E-006 — Vectors: primitives by meaning for SEO, texts and ads

semkit has the atomic commands nearest, split-paragraphs, coverage-meaning, ad-groups and synonym-candidates; long texts are compared by a page vector. The scenarios built from them (core gaps, competing pages, internal links, ad fit, competitor topics) are recorded in the vectors plan for later.
Time: 2h since the epic was approved

- ad-groups: small ad groups of one intent (SEMKIT-040)

## v0.1.31 — 2026-10-18

### E-006 — Vectors: primitives by meaning for SEO, texts and ads

semkit has the atomic commands nearest, split-paragraphs, coverage-meaning, ad-groups and synonym-candidates; long texts are compared by a page vector. The scenarios built from them (core gaps, competing pages, internal links, ad fit, competitor topics) are recorded in the vectors plan for later.
Time: 1.8h since the epic was approved

- synonym-candidates: RuWordNet and navec pulled as models (SEMKIT-041)

## v0.1.30 — 2026-10-18

### E-005 — Vectors: the base and the steps by meaning

With the vectors extra installed and a model pulled once (semkit models pull), the Human runs dupes --kind meaning, cluster-meaning, off-topic, classify-queries and assign-pages in a pipeline and gets candidate columns with a similarity; nothing is dropped by these steps; a checked-in quality test on 200 labelled phrase pairs shows the default model and threshold separate same and different intents.
Time: 1.7h since the epic was approved

- off-topic, classify-queries, assign-pages: phrases against the core, a query report and the site pages by meaning (SEMKIT-036)

## v0.1.29 — 2026-10-18

### E-005 — Vectors: the base and the steps by meaning

With the vectors extra installed and a model pulled once (semkit models pull), the Human runs dupes --kind meaning, cluster-meaning, off-topic, classify-queries and assign-pages in a pipeline and gets candidate columns with a similarity; nothing is dropped by these steps; a checked-in quality test on 200 labelled phrase pairs shows the default model and threshold separate same and different intents.
Time: 1.5h since the epic was approved

- dupes --kind meaning: duplicates by meaning with non-refining words, synonyms and the home city (SEMKIT-035)

## v0.1.28 — 2026-10-18

### E-007 — HTML input and page measures: parse-html, headings, summary, the mean, recommended occurrences

semkit read pages.jsonl parse-html gives each page its zones (text, links, all, main), title, description and h1 as columns that every text step takes; headings gives the H1-H6 structure; summary gives the mean, median, min and max of any table; compare-stats and compare-grams compare a page with the mean or the median of a list and give the recommended occurrences for a text size; coverage finds phrases with inserted words; numbers and a word list can be left out of the measures.
Time: 0.8h since the epic was approved

- parse-html and headings: pages as HTML into columns and their heading structure (SEMKIT-042)

## v0.1.27 — 2026-10-18

### E-005 — Vectors: the base and the steps by meaning

With the vectors extra installed and a model pulled once (semkit models pull), the Human runs dupes --kind meaning, cluster-meaning, off-topic, classify-queries and assign-pages in a pipeline and gets candidate columns with a similarity; nothing is dropped by these steps; a checked-in quality test on 200 labelled phrase pairs shows the default model and threshold separate same and different intents.
Time: 1.3h since the epic was approved

- Pipeline steps use the project of the CLI, not the current folder (SEMKIT-045)

### E-007 — HTML input and page measures: parse-html, headings, summary, the mean, recommended occurrences

semkit read pages.jsonl parse-html gives each page its zones (text, links, all, main), title, description and h1 as columns that every text step takes; headings gives the H1-H6 structure; summary gives the mean, median, min and max of any table; compare-stats and compare-grams compare a page with the mean or the median of a list and give the recommended occurrences for a text size; coverage finds phrases with inserted words; numbers and a word list can be left out of the measures.
Time: 0.7h since the epic was approved

- coverage --gap: phrases with inserted words (SEMKIT-044)

## v0.1.26 — 2026-10-18

### E-007 — HTML input and page measures: parse-html, headings, summary, the mean, recommended occurrences

semkit read pages.jsonl parse-html gives each page its zones (text, links, all, main), title, description and h1 as columns that every text step takes; headings gives the H1-H6 structure; summary gives the mean, median, min and max of any table; compare-stats and compare-grams compare a page with the mean or the median of a list and give the recommended occurrences for a text size; coverage finds phrases with inserted words; numbers and a word list can be left out of the measures.
Time: 0.5h since the epic was approved

- summary, the mean in the comparisons, recommended occurrences, --no-digits and --exclude (SEMKIT-043)

## v0.1.25 — 2026-10-18

### E-005 — Vectors: the base and the steps by meaning

With the vectors extra installed and a model pulled once (semkit models pull), the Human runs dupes --kind meaning, cluster-meaning, off-topic, classify-queries and assign-pages in a pipeline and gets candidate columns with a similarity; nothing is dropped by these steps; a checked-in quality test on 200 labelled phrase pairs shows the default model and threshold separate same and different intents.
Time: 0.9h since the epic was approved

- Vectors base: models pull/list/remove, the encoder, the index and cluster-meaning end to end (SEMKIT-034)

## v0.1.24 — 2026-10-18

### E-005 — Vectors: the base and the steps by meaning

With the vectors extra installed and a model pulled once (semkit models pull), the Human runs dupes --kind meaning, cluster-meaning, off-topic, classify-queries and assign-pages in a pipeline and gets candidate columns with a similarity; nothing is dropped by these steps; a checked-in quality test on 200 labelled phrase pairs shows the default model and threshold separate same and different intents.
Time: 0.3h since the epic was approved

- Help and docstrings say «the bundled dictionary», not the add-in name (SEMKIT-037)

## v0.1.23 — 2026-10-17

### E-004 — semkit on a real core: correct morphology and text rules, a CLI that tells the truth

Every finding of docs/plans/e2e-quality.md is fixed, decided in an ADR or the help, or recorded as not taken; a checked-in end-to-end run on a real core and a real text recounts the results independently and is part of the gate.
Time: 2.8h since the epic was approved

- CLI that tells the truth: --as, errors, lemma matching of lists, help and guide in CLI terms, top-level commands; the e2e run on a real core in the gate (SEMKIT-033)

## v0.1.22 — 2026-10-17

### E-004 — semkit on a real core: correct morphology and text rules, a CLI that tells the truth

Every finding of docs/plans/e2e-quality.md is fixed, decided in an ADR or the help, or recorded as not taken; a checked-in end-to-end run on a real core and a real text recounts the results independently and is part of the gate.
Time: 1.1h since the epic was approved

- Change functions on real phrases: match types with operators, a reversible translit, toponyms, phonetic, replace-words, UTM (SEMKIT-032)

## v0.1.21 — 2026-10-17

### E-004 — semkit on a real core: correct morphology and text rules, a CLI that tells the truth

Every finding of docs/plans/e2e-quality.md is fixed, decided in an ADR or the help, or recorded as not taken; a checked-in end-to-end run on a real core and a real text recounts the results independently and is part of the gate.
Time: 0.9h since the epic was approved

- Morphology on a real core: correct lemmas, the accusative, plurals, compounds, adjectives, full names, word forms (SEMKIT-030)
- Text rules on a real page: one word splitter, split-text at sentences not dashes, no false typos, abbreviations no lemmas (SEMKIT-031)

## v0.1.20 — 2026-10-17

### Outside epics

- CLI read keeps numeric columns numeric; only the text columns are text (SEMKIT-028)
- Project config test: .agents/antagor/.gitignore holds state/ and receipts/; Antagor may add its own lines (SEMKIT-029)

## v0.1.19 — 2026-10-17

### E-003 — semkit CLI: one command line is a pipeline of steps over the whole library; named word lists

semkit read core.xlsx drop-words @minus/universal remove-chars punctuation dupes --kind lemmas --action drop ngrams -n 2 write out.csv works; every library function is a step with its own --help; semkit lists shows every list (bundled, the Human's folders, the project) and a step that takes a list shows them in its help; an agent gets the same through --json, describe and --ai.
Time: 1.4h since the epic was approved

- Step help quality: real examples per step, each option's own help, bullet lists kept; the agent guide uses the bundled lists (SEMKIT-027)

## v0.1.18 — 2026-10-17

### E-003 — semkit CLI: one command line is a pipeline of steps over the whole library; named word lists

semkit read core.xlsx drop-words @minus/universal remove-chars punctuation dupes --kind lemmas --action drop ngrams -n 2 write out.csv works; every library function is a step with its own --help; semkit lists shows every list (bundled, the Human's folders, the project) and a step that takes a list shows them in its help; an agent gets the same through --json, describe and --ai.
Time: 1.1h since the epic was approved

- Refresh the 11 step help snapshots that now list the word lists (SEMKIT-026)

## v0.1.17 — 2026-10-17

### E-003 — semkit CLI: one command line is a pipeline of steps over the whole library; named word lists

semkit read core.xlsx drop-words @minus/universal remove-chars punctuation dupes --kind lemmas --action drop ngrams -n 2 write out.csv works; every library function is a step with its own --help; semkit lists shows every list (bundled, the Human's folders, the project) and a step that takes a list shows them in its help; an agent gets the same through --json, describe and --ai.
Time: 1h since the epic was approved

- CLI steps for every other area of the library; the agent guide (--ai) and README with typical pipelines (SEMKIT-024)
- Word lists: bundled Bukvarix and add-in lists with a manifest, the Human's folders by any path, semkit lists, sk.word_list (SEMKIT-025)

## v0.1.16 — 2026-10-17

### E-003 — semkit CLI: one command line is a pipeline of steps over the whole library; named word lists

semkit read core.xlsx drop-words @minus/universal remove-chars punctuation dupes --kind lemmas --action drop ngrams -n 2 write out.csv works; every library function is a step with its own --help; semkit lists shows every list (bundled, the Human's folders, the project) and a step that takes a list shows them in its help; an agent gets the same through --json, describe and --ai.
Time: 0.8h since the epic was approved

- CLI pipeline core: read, chained steps, write; the step table and its generator; the text, dupes and n-gram steps (SEMKIT-023)

## v0.1.15 — 2026-10-17

### E-002 — semkit: the rest of the library — change, declension, analysis and the later functions

import rb_semkit gives every function of the add-in's menus except Mystem: each follows the VBA algorithm, the broken ones work as intended, and the conformance report lists for each function where it follows the VBA, where it differs and why.
Time: 1.5h since the epic was approved

- Public word-keys helper of the analysis area; dir(rb_semkit) lists only the public names (SEMKIT-022)

## v0.1.14 — 2026-10-17

### E-002 — semkit: the rest of the library — change, declension, analysis and the later functions

import rb_semkit gives every function of the add-in's menus except Mystem: each follows the VBA algorithm, the broken ones work as intended, and the conformance report lists for each function where it follows the VBA, where it differs and why.
Time: 1.4h since the epic was approved

- Conformance: no cases for semkit's own functions; drop the text_stats cases that copy expected into vba (SEMKIT-021)

## v0.1.13 — 2026-10-17

### E-002 — semkit: the rest of the library — change, declension, analysis and the later functions

import rb_semkit gives every function of the add-in's menus except Mystem: each follows the VBA algorithm, the broken ones work as intended, and the conformance report lists for each function where it follows the VBA, where it differs and why.
Time: 1.4h since the epic was approved

- Analysis block: combinations, parents and basis phrases, good/bad split, clustering, synonyms to minus-words, typos, sentiment (SEMKIT-013)

## v0.1.12 — 2026-10-17

### E-002 — semkit: the rest of the library — change, declension, analysis and the later functions

import rb_semkit gives every function of the add-in's menus except Mystem: each follows the VBA algorithm, the broken ones work as intended, and the conformance report lists for each function where it follows the VBA, where it differs and why.
Time: 1.3h since the epic was approved

- Change block: every text change of the add-in (case, insert, replace, translit, ЧПУ, match types, UTM, hashes, word order, phonetic) (SEMKIT-011)
- List tools: compare two lists (both, either, only first, only second) by a duplicate kind; strip characters at word edges (SEMKIT-020)

## v0.1.11 — 2026-10-17

### E-002 — semkit: the rest of the library — change, declension, analysis and the later functions

import rb_semkit gives every function of the add-in's menus except Mystem: each follows the VBA algorithm, the broken ones work as intended, and the conformance report lists for each function where it follows the VBA, where it differs and why.
Time: 1.1h since the epic was approved

- Clustering by a given SERP table: soft and hard, by the number of common URLs in the top (SEMKIT-018)
- Compare a text with competitor texts: gram density against the competitors' median, metrics against their median, BM25 (SEMKIT-019)

## v0.1.10 — 2026-10-17

### E-002 — semkit: the rest of the library — change, declension, analysis and the later functions

import rb_semkit gives every function of the add-in's menus except Mystem: each follows the VBA algorithm, the broken ones work as intended, and the conformance report lists for each function where it follows the VBA, where it differs and why.
Time: 1.1h since the epic was approved

- Text metrics per text: characters, words, unique lemmas, water, classic and academic nausea, the top lemma (SEMKIT-017)

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
