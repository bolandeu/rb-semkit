---
id: SEMKIT-051
title: 'synonym-candidates --phrases: thesaurus candidates of several words, and lookups
  of several-word senses'
status: ideas
attempts: 0
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: null
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
- uv run pytest
resident: null
tool: null
pr: null
translation: 'synonym-candidates --phrases: синонимы-словосочетания из RuWordNet (таможенное
  оформление, таможенная очистка…) и поиск по словосочетаниям ядра.'
---

RuWordNet holds several-word senses in the same synset as single words: the synset of «растаможка» has растаможивание, растаможить, растамаживать, таможенное оформление, таможенная очистка, таможенное обслуживание, таможенная процедура, оформить на таможне. synonym-candidates skips candidates of several words, so the user never sees the phrase synonyms.

1. --phrases (off by default, so the output without it stays as now): the thesaurus also gives candidates of several words, in lower case as the sense names, score 1, source ruwordnet. The vectors (navec) stay one word.
2. With --phrases, a run of words of the core that is a sense of the thesaurus (2-4 words, compared by lemmas) is looked up too: its row has that run as word. A core «таможенное оформление авто» gives the candidates of «таможенное оформление» as well as of each word.
3. Each candidate once per word: the same name with ё/е or a duplicate sense counts once.
4. Step help (an example with --phrases) and the agent guide.

## Acceptance

- Given the core «растаможка авто», When synonym-candidates --all --phrases --source ruwordnet runs, Then the candidates of растаможка include «таможенное оформление» and «таможенная очистка» [check: tests/word_vectors/test_synonym_candidates.py]
- Given the core «таможенное оформление авто», When synonym-candidates --all --phrases runs, Then there are rows with word «таможенное оформление» and candidate «растаможка» [check: tests/word_vectors/test_synonym_candidates.py]
- Given the same core without --phrases, When the step runs, Then the output is as before (no candidate of several words) [check: tests/word_vectors/test_synonym_candidates.py]
- Given a synset with the same name twice (растамаживать in two senses), When the step runs, Then the candidate is listed once for the word [check: tests/word_vectors/test_synonym_candidates.py]

## How to test

Integration through the semkit CLI runner with the RuWordNet fixture the word-vector tests use (skip when the data is not pulled, as those tests do).

## Basis

core/word_vectors/thesaurus.py (the synset lookup) and candidates.py; the sense table has name and lemma columns.

## Read first

- `src/rb_semkit/core/word_vectors/thesaurus.py`

## Out of scope

- Other synonym sources (YARN, Wiktionary, dictionaries); vectors of phrases; hypernyms or related relations.
