---
id: SEMKIT-031
title: 'Text rules on a real page: one word splitter, split-text at sentences not
  dashes, no false typos, abbreviations no lemmas'
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
type: bugfix
owns_paths:
- src/rb_semkit/core/split
- src/rb_semkit/core/textstats
- src/rb_semkit/core/coverage
- src/rb_semkit/core/compare
- src/rb_semkit/core/analysis
- src/rb_semkit/core/corpus
- src/rb_semkit/core/text
- src/rb_semkit/data/text
- src/rb_semkit/data/corpus
- scripts/build_parts/text.py
- docs/vba/deviations/corpus.md
- docs/vba/deviations/text.md
- docs/vba/deviations/analysis.md
- docs/vba/conformance.md
- docs/vba/conformance/analysis.md
- docs/vba/conformance/corpus.md
- docs/vba/conformance/text.md
- src/rb_semkit/core/morph/lemmatizer.py
test_paths:
- tests/split
- tests/textstats
- tests/coverage
- tests/compare
- tests/analysis
- tests/corpus
- tests/matchers
- tests/conformance/cases/text
- tests/conformance/cases/corpus
- tests/conformance/cases/analysis
- tests/snapshots/describe.json
- tests/snapshots/help/steps/corpus/add-minus-words.txt
docs:
- docs/vba/deviations/corpus.md
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-004
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**Текстовые правила на реальной странице.** Одно разбиение на слова
  для split_text, text_stats, coverage, compare_grams, ngrams (числа с точками/дефисами
  — одно слово); split_text не режет по тире и по точке сокращения (г.), телефон и
  дата целы; coverage exact считает вхождение через тире/запятую; г, м, п, ул, руб
  — не леммы; ngrams без пунктуации на словах; опечатки не трогают верные формы ядра;
  add_minus_words — только уверенные синонимы; округление 4 знака; find-pos без двойных
  частей речи; remove-chars punctuation не рвёт 2.5 и 140х200.'
---

The end-to-end check (docs/plans/e2e-quality.md, items 12-19, 22, 26) on a real page (a customs warehouse site) and a real sofa core found the text functions split and count words differently, cut phrases where a sentence does not end, and the typo check rewrites correct phrases. Fix the library behaviour; Do not change the public docstrings: SEMKIT-033 updates them and the help snapshots after this task; when your fix changes a rule a docstring states, report it as an inbox finding (the function and the new rule). Behaviour only.

One word splitter: split_text, text_stats, coverage, compare_grams, compare_stats, ngrams and bm25 count the words of a text the same way: a number with inner points, commas or hyphens (31.03.2026, 541,67, 275-30-85, 2.5) is one word, a hyphenated word is one word. text_stats words and compare_grams / coverage densities of one text use the same word count.

split_text: a dash between words (Склад временного хранения — это место) does not cut a phrase; an abbreviation point (г. Краснознаменск, ул. Березовая, т. е.) does not end a sentence; a phone, a date, a decimal stay whole.

Coverage exact: an occurrence may cross a dash or a comma inside a sentence (хранения — это matches the phrase склад временного хранения это), not a sentence end.

Lemmas of the text metrics: single-letter words and the abbreviations г, м, п, д, т, ул, руб (with or without a point) are words but no lemmas for top, nausea, ttr, mtld, zipf and compare_grams.

ngrams of a raw text: punctuation at the edges of a word is not part of the gram (руб. and руб are one gram; ★ is no gram).

Typos: is_typo and typo_correction mark no word that is a known word form (москва, москве, угловые, недорогой, дешево, с диваном, для дивана) and change nothing in the 2000 phrases of the sofa core; a real misspelling (диавн, мосвка) is still marked and corrected.

Synonyms: add_minus_words adds only the sure synonyms by default; the unsure ones only when asked.

Rounding: coverage density and counts share are rounded to 4 decimals like compare_grams; compare_stats keeps integer metrics integers.

find-pos: a capitalised word is one part of speech (Быстро is not both adjective and adverb); лучше is no noun; покрывало is no verb.

remove-chars punctuation keeps a decimal and a size whole (2.5 м, 140х200 stay); the other punctuation still goes.

## Acceptance

- Given the text «Склад временного хранения — это место. Адрес: г. Краснознаменск, тел. 275-30-85, 31.03.2026.», When sk.split_text runs, Then «Склад временного хранения — это место» is one phrase, «г. Краснознаменск» is not cut, 275-30-85 and 31.03.2026 stay whole [check: tests/split]
- Given one page text, When text_stats, coverage and compare_grams run on it, Then text_stats words equals the word count behind the densities of coverage and compare_grams [check: tests/textstats]
- Given the text «Склад временного хранения — это место» and the core phrase «склад временного хранения это», When coverage exact runs, Then count is 1; Given «хранения. Это», Then count is 0 [check: tests/coverage]
- Given a text where «г.» stands 50 times and «таможенный» 10 times, When text_stats runs, Then top is таможенный and г is no lemma of nausea, ttr, mtld, zipf; compare_grams lists no gram г, м or п [check: tests/textstats]
- Given the raw text «цена 100 руб. и 200 руб, ★ отзывы», When ngrams runs, Then руб is one gram with count 2 and ★ is no gram [check: tests/analysis]
- Given купить диван в москве, угловые диваны, купить недорогой диван, купить диван дешево, кровать трансформер с диваном, матрас для дивана, When is_typo and typo_correction run, Then none is marked and none changes; Given купить диавн в мосвке, Then it is marked and corrected to купить диван в москве [check: tests/corpus]
- Given a synonyms table with a sure and an unsure synonym, When add_minus_words runs, Then only the sure one is added [check: tests/corpus]
- Given coverage and counts share results, When written, Then densities and shares have at most 4 decimals; compare_stats chars is an integer [check: tests/coverage]
- Given «диван раскладной Быстро в Москве», «какой диван лучше выбрать», «покрывало на диван», When find-pos runs, Then Быстро is either adjective or adverb (not both), лучше is no noun, покрывало is no verb [check: tests/matchers]
- Given «диван 2.5 м, 140х200!», When remove-chars punctuation runs, Then «диван 2.5 м 140х200» [check: tests/matchers]

## How to test

Unit through the library (import rb_semkit as sk); conformance cases of text, corpus and analysis where the function has cases (semkit's own functions stay out of the cases, NOT_CASED)

## Basis

ADR 0005 for ported functions; semkit's own functions (split_text, text_stats, coverage, compare_grams) follow their docstrings; the typo provider of core/corpus

## Read first

- `docs/plans/e2e-quality.md`
- `docs/adr/0005-port-vba-fix-defects.md`
- `tests/conformance/case_files.py`

## Out of scope

- Morphology (lemmas, declension): SEMKIT-030
- The step help, its snapshots, the docstrings and the guide: SEMKIT-033
- A new spelling service

## Feedback

### Answer to question #1

> find-pos: the bundled !SEMTools dictionary codes лучше as a noun and покрывало as a verb (pymorphy3: comparative adjective, noun); the codes come from the lemmatizer (morph, SEMKIT-030), and a general 'pymorphy3 wins' rule breaks 15 of 29 disagreeing words of the sofa core (белые, угловой, дорогой become nouns).
> Question: Where do the wrong part-of-speech codes of лучше and покрывало get fixed?
> Options:
> 1. SEMKIT-030 adds them to its correction of the dictionary data (code and lemma per word); find-pos follows without own code; SEMKIT-031 does the capital rule only
> 2. SEMKIT-031 adds a small code correction table read by the pos matcher only (data/text)
> 3. SEMKIT-031 edits the morph dictionary data now, before SEMKIT-030
> Recommended: SEMKIT-030 adds them to its correction of the dictionary data (code and lemma per word); find-pos follows without own code; SEMKIT-031 does the capital rule only

Option 1: the codes of лучше and покрывало are fixed in the dictionary correction of SEMKIT-030's mechanism; as 030 is already running, SEMKIT-033 adds the two entries after it. SEMKIT-031 does the capital rule only; drop the лучше / покрывало part of its find-pos acceptance (the Быстро part stays).

### Answer to finding #2

> SEMKIT-031 changed rules that public docstrings state (for SEMKIT-033): (1) sk.split_text: a dash between words (— – -) and the point of an abbreviation of data/text/words.toml (г. ул. т. е. тел. руб.) do not cut a phrase; both are dropped (module doc said «т.д.» splits). (2) sk.text_stats: no lemma for top/nausea/ttr/mtld/zipf = every single-letter word + abbreviations and units of data/text/words.toml (рублей, см, мм, мл, кг; шт, кв, стр, ул, руб are abbreviations); words count numbers with inner . , - as one word and keep an apostrophe inside a word. (3) sk.coverage: exact and lemmas cross any punctuation inside a sentence (dash, comma), never a sentence end (. ! ? …, not an abbreviation point); any_order stays inside one split_text phrase; density rounded to 4 decimals. (4) sk.compare_grams / sk.bm25: with lemmas, a word without a lemma (single letter, abbreviation, unit) is in no gram but counts in the words of a text. (5) sk.compare_stats: integer metrics (chars, chars_no_spaces, words, unique) stay integers where whole; the docstring says 'rounded to 4 decimals'. (6) sk.ngrams / sk.bigrams: words are those of split_text (punctuation at word edges is dropped, ★ is no gram, 31.03.2026 one word). (7) sk.counts share / share_of_total: rounded to 4 decimals. (8) sk.CoreSpelling / is_typo / typo_correction: a stopword or a wordform the !SEMTools dictionary or pymorphy3 knows is never a typo; a correction starts with the same letter as the word. (9) sk.add_minus_words: new argument unsure=False (CLI --unsure, help now 'See the description above.'): only rows with sure True are added unless unsure; a table without the column sure is all sure; a sure cell read from a file as text (True/TRUE/ИСТИНА/1) counts. (10) sk.pos: a capitalised word is looked up in lower case (the docstring says «Быстро» is an adjective as in the add-in). (11) sk.chars('punctuation'): a point or comma between two digits is no punctuation (2.5, 541,67 stay).

Goes into SEMKIT-033's body (the docstring rules changed by 031) before 033 starts.

### Blocked: needs_scope (entries [{'n': 1, 'text': 'find-pos: the bundled !SEMTools dictionary codes лучше as a noun and покрывало as a verb (pymorphy3: comparative adjective, noun); the codes come from the lemmatizer (morph, SEMKIT-030), and a general'}])

No scope for src/rb_semkit/core/morph/lemmatizer.py: it is SEMKIT-030's. Drop that change (inbox #1: the лучше / покрывало codes go to SEMKIT-033 through 030's dictionary correction). Keep the capital rule in the pos matcher; drop the лучше / покрывало part of the find-pos acceptance, keep Быстро.
