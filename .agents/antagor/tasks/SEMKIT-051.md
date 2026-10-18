---
id: SEMKIT-051
title: 'synonym-candidates: synonyms of any number of words, both ways (a word, a
  phrase), from the thesaurus'
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
- src/rb_semkit/core/word_vectors/
- src/rb_semkit/steps/word_vectors.py
- src/rb_semkit/data/SKILL.md
- tests/snapshots/
- tests/word_vectors/
test_paths:
- tests/word_vectors/test_synonym_candidates.py
- tests/conftest.py
- tests/steps/fixtures/customs.csv
docs:
- src/rb_semkit/data/SKILL.md
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: null
spec_refs: []
checks:
- uv run --extra vectors pytest
resident: null
tool: null
pr: null
translation: 'synonym-candidates: синоним не зависит от числа слов — слово ↔ фраза
  ↔ фраза (растаможка = таможенное оформление = таможенное оформление товаров), по
  умолчанию, без опции.'
---

RuWordNet holds senses of one word and of several words in the same synset: the synset of «растаможка» has растаможивание, растаможить, растамаживать, таможенное оформление, таможенная очистка, таможенное обслуживание, таможенная процедура, таможенное оформление товаров, оформить на таможне. A synonym is a synonym whatever the number of its words: a word may have a phrase as a synonym, a phrase a word, a phrase a phrase. synonym-candidates now skips candidates of several words and looks up single words only, so «таможенное оформление» never shows.

1. The thesaurus candidates are of any number of words, by default (no option): in lower case as the sense names, score 1, source ruwordnet. The vectors (navec) stay one word, as now.
2. The looked-up units of a phrase are a segmentation of it into runs that do not overlap:
 - a stopword is never a unit by itself; it stays inside a run when the sense holds it («оформить на таможне»), compared by lemmas with the sense lemma column;
 - of all the segmentations, the one with the most words inside senses of several words wins; on a tie, the one with fewer units (longer senses); on a tie still, the first from the left;
 - a word in no such sense is a unit by itself (when it is no stopword);
 - a word inside a found sense gets no candidates of its own («оформление» of «таможенное оформление» does not get «дизайн»).
 A run row has that run as word. The whole phrase is one unit only when it is a sense itself. «таможенное оформление грузов из индии» (with no sense «таможенное оформление грузов» in the data) gives the units «таможенное оформление», «грузов», «индии».
3. Each candidate once per unit: the same name with ё/е or a duplicate sense counts once; the unit itself is not its own candidate.
4. in_core of a candidate of several words: true when the candidate occurs in a phrase of the core as a run of words, by lemmas.
5. --as-slots: the result as a table of slots for linear-combinations: one column per unit of the phrase, in their order, named slot_1, slot_2…; the first row holds the units themselves, the rows under them their candidates (each column as long as its list, the rest empty). Stopwords give no slot. It needs a core of one phrase; more phrases are refused with exit 2. --as-slots and --as-synonyms together are refused with exit 2.
6. Step help (an example with a phrase synonym) and the agent guide.

## Acceptance

- Given the core «растаможка авто», When synonym-candidates --all --source ruwordnet runs, Then the candidates of растаможка include «таможенное оформление» and «таможенная очистка» [check: tests/word_vectors/test_synonym_candidates.py]
- Given the core «таможенное оформление авто», When synonym-candidates --all runs, Then there are rows with word «таможенное оформление» and candidate «растаможка» [check: tests/word_vectors/test_synonym_candidates.py]
- Given the core «таможенное оформление товаров», When synonym-candidates --all runs, Then the unit «таможенное оформление товаров» has the candidate «растаможка» [check: tests/word_vectors/test_synonym_candidates.py]
- Given the core «растаможка авто» and «таможенное оформление машины», When synonym-candidates runs without --all, Then «таможенное оформление» is a candidate of растаможка with in_core true [check: tests/word_vectors/test_synonym_candidates.py]
- Given the core «таможенное оформление транспортного средства» (a run in another case), When synonym-candidates --all runs, Then the unit «таможенное оформление» has the candidate «растаможка» and the unit «транспортного средства» has the candidates of the sense «транспортное средство» (средство передвижения, транспорт) [check: tests/word_vectors/test_synonym_candidates.py]
- Given the core «растаможка авто» (not a sense of the thesaurus as a whole), When synonym-candidates --all runs, Then no row has word «растаможка авто»: a candidate always replaces only the unit of its row, never the whole phrase [check: tests/word_vectors/test_synonym_candidates.py]
- Given the core «таможенное оформление грузов из индии», When synonym-candidates --all runs, Then the units are exactly «таможенное оформление», «грузов», «индии»; no row has word «оформление», «таможенное» or «из» [check: tests/word_vectors/test_synonym_candidates.py]
- Given a fixture where both «a b» and «b c» are senses and the core «a b c», When the step runs, Then the units are «a b» and «c» (the first from the left on a tie) [check: tests/word_vectors/test_synonym_candidates.py]
- Given the core «оформить на таможне» (a sense with a stopword inside), When the step runs, Then it is one unit [check: tests/word_vectors/test_synonym_candidates.py]
- Given the core «таможенное оформление грузов из индии», When synonym-candidates --all --as-slots runs, Then the columns are slot_1, slot_2, slot_3; the first row is «таможенное оформление», «грузов», «индии»; slot_1 holds «растаможка» below; there is no slot for «из» [check: tests/word_vectors/test_synonym_candidates.py]
- Given --as-slots on a core of two phrases, When the step runs, Then it is refused with exit 2 [check: tests/word_vectors/test_synonym_candidates.py]
- Given the --as-slots output, When linear-combinations runs on it, Then each combination takes one item of each slot and the first combination is the units of the phrase [check: tests/word_vectors/test_synonym_candidates.py]
- Given a synset with the same name twice (растамаживать in two senses), When the step runs, Then the candidate is listed once for the unit [check: tests/word_vectors/test_synonym_candidates.py]
- Given --as-synonyms, When the step runs, Then the file holds the one-word candidates of the one-word units only, as now, since the steps with --synonyms compare word by word; the help says so [check: tests/word_vectors/test_synonym_candidates.py]

## How to test

Integration through the semkit CLI runner with the RuWordNet fixture the word-vector tests use (add the senses of the examples to the fixture); the real data test as the existing real-data tests do.

## Basis

core/word_vectors/thesaurus.py (the synset lookup) and candidates.py; the sense table has name and lemma columns.

## Read first

- `src/rb_semkit/core/word_vectors/thesaurus.py`

## Out of scope

- Other synonym sources (YARN, Wiktionary, dictionaries); vectors of phrases; hypernyms or related relations; an option to turn the phrase candidates off; synonyms of several words in the steps with --synonyms (dupes, ad-groups).
