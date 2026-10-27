---
id: SEMKIT-090
title: 'relate-phrases: a refinement even when a multi-word unit takes a word of the
  base phrase'
status: done
attempts: 0
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: architect
worker: claude-code
type: bugfix
owns_paths:
- src/rb_semkit/core/relate/
- src/rb_semkit/core/word_vectors/units.py
- src/rb_semkit/core/word_vectors/candidates.py
- src/rb_semkit/steps/relate.py
- tests/relate/
- tests/word_vectors/
- tests/snapshots/
- docs/plans/relate-phrases.md
test_paths:
- tests/relate/test_refinement_units.py
- tests/relate/test_acceptance.py
- tests/relate/test_precision.py
docs: none
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: null
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
resident: null
tool: null
pr: null
translation: 'T330: relate-phrases даёт other фразе, которая по словам — уточнение,
  когда словарь склеил слова (мастер по ремонту, кузов автомобиля) или слова основной
  фразы не рядом. Нужно: четыре пары маркетера тестом (сначала красный), слово-в-слово
  разрез тоже кандидат; таблица приёмки и 200 пар без потерь.'
---

relate-phrases gives `other` to a phrase that is a refinement by words, when the thesaurus reads a part of the phrase as a multi-word unit. The marketer's production runs of v0.2.0 (request T330, card S329) show four pairs. C is the phrase, H is the base:

| C | H | now | wanted |
|---|---|---|---|
| мастер по ремонту стиральных машин | ремонт стиральных машин | other | refinement (the unit «мастер по ремонту» takes the word «ремонт» of H) |
| мастер по ремонту машинок стиральных на дому | ремонт стиральных машин | other | refinement (same unit; «машинок стиральных» is in another order; машинка ~ машина) |
| растаможка кузова автомобиля | растаможка авто | other | refinement (the unit «кузов автомобиля» takes «автомобиль»; авто ~ автомобиль) |
| ремонт стиральных и посудомоечных машин | ремонт стиральных машин | other | refinement (the words of H are not adjacent in C: «посудомоечная машина» is one unit there) |

Rule (the user, S319: a refinement is decided by words): C is a refinement of H when every unit of H pairs with a word or a unit of C (equal or linked) and C has words left over.

Cause (found by reading the code): `cuts()` (core/word_vectors/units.py) gives only the segmentations that leave no known run out, so a phrase never has the cut into single words when a known run fits somewhere in it; `best_pairing()` (core/relate/pairing.py) can then only pair the cuts it has, and the unit «мастер по ремонту» hides the word «ремонт». Do not trust this cause without a test: write the four pairs as a failing test first, then fix.

Do:
1. The four pairs as tests, red first. Use the test thesaurus fixture of tests/relate/conftest.py with the senses of the real thesaurus for these words, and one test with the real thesaurus (marked real_encoder, skipped when it is not pulled).
2. Make the word-level cut (every word a unit, the cut of lemmas) a candidate of the pairing, for the decision of a refinement. Keep the choice «the pairing that explains the most words».
3. Same and variation must not get easier: no pair of another intent may become same or variation. The 200 labelled pairs (tests/relate/test_precision.py) stay as they are, and the table of the acceptance (tests/relate/test_acceptance.py) gives the same classes, `of` and `reason`.
4. Speed stays: 1000 phrases of the sofa core in seconds (tests/relate/test_speed.py, marker speed; run it once on an idle machine and report the time).

## Acceptance

- Given «ремонт стиральных машин» first and then «мастер по ремонту стиральных машин» and «мастер по ремонту машинок стиральных на дому», When the step runs, Then both are refinement of the first with reason +мастер… for the words left over [check: tests/relate/test_refinement_units.py]
- Given «растаможка авто» first and then «растаможка кузова автомобиля», When the step runs, Then the second is a refinement of the first [check: tests/relate/test_refinement_units.py]
- Given «ремонт стиральных машин» first and then «ремонт стиральных и посудомоечных машин», When the step runs, Then the second is a refinement of the first, also in the reverse order of the rows [check: tests/relate/test_refinement_units.py]
- Given the table of the acceptance and the 200 labelled pairs, When the step runs, Then the classes, of and reason of the table are the same as before and no pair of another intent comes out same or variation beyond the known four rows [check: tests/relate/test_acceptance.py]

## How to test

level: integration through the pipeline; seam: semkit read TABLE.jsonl relate-phrases … write -; data: small JSONL tables with the test thesaurus of tests/relate/conftest.py, plus one real-thesaurus test (skipped when not pulled); red first

## Basis

Follow cuts() of core/word_vectors/units.py and best_pairing() of core/relate/pairing.py; the pairs and the table already tested in tests/relate/test_acceptance.py and test_precision.py

## Read first

- `src/rb_semkit/core/word_vectors/units.py`
- `src/rb_semkit/core/relate/pairing.py`
- `src/rb_semkit/core/relate/functions.py`
- `tests/relate/conftest.py`

## Out of scope

- Prepositions (same for «диван с матрасом» / «матрас на диван»): a separate idea. Any change of the dictionary, --synonyms or the Latin reading. Any new step or option.
