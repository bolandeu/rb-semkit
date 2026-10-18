---
id: SEMKIT-051
title: 'synonym-candidates: synonyms of any number of words, both ways (a word, a
  phrase), from the thesaurus'
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
- src/rb_semkit/core/word_vectors/
- src/rb_semkit/steps/word_vectors.py
- src/rb_semkit/data/SKILL.md
- tests/snapshots/
- tests/word_vectors/
test_paths:
- tests/word_vectors/test_synonym_candidates.py
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
2. The looked-up units of a phrase are its words and every run of its words that is a sense of the thesaurus, of any length, compared by lemmas (the sense lemma column). A run row has that run as word. A core «таможенное оформление товаров авто» gives the candidates of «таможенное оформление товаров», of «таможенное оформление», and of each word.
3. Each candidate once per unit: the same name with ё/е or a duplicate sense counts once; the unit itself is not its own candidate.
4. in_core of a candidate of several words: true when the candidate occurs in a phrase of the core as a run of words, by lemmas.
5. Step help (an example with a phrase synonym) and the agent guide.

## Acceptance

- Given the core «растаможка авто», When synonym-candidates --all --source ruwordnet runs, Then the candidates of растаможка include «таможенное оформление» and «таможенная очистка» [check: tests/word_vectors/test_synonym_candidates.py]
- Given the core «таможенное оформление авто», When synonym-candidates --all runs, Then there are rows with word «таможенное оформление» and candidate «растаможка» [check: tests/word_vectors/test_synonym_candidates.py]
- Given the core «таможенное оформление товаров», When synonym-candidates --all runs, Then the unit «таможенное оформление товаров» has the candidate «растаможка» [check: tests/word_vectors/test_synonym_candidates.py]
- Given the core «растаможка авто» and «таможенное оформление машины», When synonym-candidates runs without --all, Then «таможенное оформление» is a candidate of растаможка with in_core true [check: tests/word_vectors/test_synonym_candidates.py]
- Given a synset with the same name twice (растамаживать in two senses), When the step runs, Then the candidate is listed once for the unit [check: tests/word_vectors/test_synonym_candidates.py]
- Given --as-synonyms, When the step runs, Then a candidate of several words stays whole in the synonyms cell, so the file reads back by the steps with --synonyms (their separator chosen so that a phrase is not split) [check: tests/word_vectors/test_synonym_candidates.py]

## How to test

Integration through the semkit CLI runner with the RuWordNet fixture the word-vector tests use (add the senses of the examples to the fixture); the real data test as the existing real-data tests do.

## Basis

core/word_vectors/thesaurus.py (the synset lookup) and candidates.py; the sense table has name and lemma columns; the reader of --synonyms files for item 6.

## Read first

- `src/rb_semkit/core/word_vectors/thesaurus.py`

## Out of scope

- Other synonym sources (YARN, Wiktionary, dictionaries); vectors of phrases; hypernyms or related relations; an option to turn the phrase candidates off.
