---
id: SEMKIT-050
title: linear-combinations joins each combination into a phrase column; a step agree
  puts the words of a phrase in agreement
status: in_review
attempts: 1
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: architect
worker: claude-code
type: feature
owns_paths:
- src/rb_semkit/core/declension/
- src/rb_semkit/steps/declension.py
- src/rb_semkit/core/corpus/combinations.py
- src/rb_semkit/steps/corpus.py
- src/rb_semkit/steps/__init__.py
- src/rb_semkit/data/SKILL.md
- README.md
- tests/snapshots/
- tests/declension/
- tests/corpus/test_combinations.py
- tests/steps/
- src/rb_semkit/core/morph/lemmatizer.py
- src/rb_semkit/pipeline/state.py
test_paths:
- tests/declension/
- tests/corpus/test_combinations.py
- tests/conformance/areas/corpus.py
- tests/conformance/case_files.py
- tests/conformance/test_cases.py
docs:
- README.md
- src/rb_semkit/data/SKILL.md
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
- uv run --extra vectors pytest
resident: null
tool: null
pr: null
translation: linear-combinations склеивает сочетание в колонку phrase; новый шаг agree
  согласует слова по правилам соседних слов (глагол+сущ → вин., сущ+сущ → род., прил+сущ
  → род/число/падеж, предлог → падеж по таблице); несогласуемое остаётся с причиной
  в agree_note.
---

A core is often built by combining word variants (linear-combinations) and then filtering by meaning (nearest). Two gaps: the combination stays in separate columns, and the words do not agree («растаможить машина»).

1. linear-combinations also writes a column phrase: the items of each combination joined by one space, in the column order; it is the working column of the result.
2. A new step agree rewrites each phrase so that its words agree, by rules on neighbouring words (no syntax parser), using the existing declension core:
 - a verb then a noun group: the noun group in the accusative («растаможить машина» → «растаможить машину»), animacy as decline does;
 - a noun then a noun group without a preposition: the second group in the genitive («растаможка автомобиль» → «растаможка автомобиля»);
 - an adjective then a noun: the adjective takes the gender, number and case of the noun («легковой машина» → «легковая машина»);
 - a preposition then a noun group: the case of a small table of prepositions (из, для, без, до, от, у → genitive; к → dative; с: instrumental; в, на: accusative unless the phrase reads as a place, then prepositional — when unsure keep the word);
 - an indeclinable word (авто, такси) stays.
 A phrase whose words already agree stays as it is. A phrase where no rule applies, or a rule is ambiguous, stays as it is, and a column agree_note names the reason (empty when agreed). Pass --as NAME to write to a new column, as decline does.
3. Step help with real examples, the agent guide and README: the pipeline linear-combinations agree nearest.

## Acceptance

- Given columns a: растаможить, растаможка and b: машина, автомобиль, When linear-combinations runs, Then the column phrase holds «растаможить машина», «растаможить автомобиль», «растаможка машина», «растаможка автомобиль» [check: tests/corpus/test_combinations.py]
- Given «растаможить машина», When agree runs, Then it gives «растаможить машину» [check: tests/declension/]
- Given «растаможка автомобиль» and «таможенное оформление автомобиль», When agree runs, Then they give «растаможка автомобиля» and «таможенное оформление автомобиля» [check: tests/declension/]
- Given «легковой машина» and «купить рыжий кот», When agree runs, Then they give «легковая машина» and «купить рыжего кота» [check: tests/declension/]
- Given «растаможка авто из германия», When agree runs, Then it gives «растаможка авто из германии» [check: tests/declension/]
- Given «растаможка авто» and «купить диван», When agree runs, Then they stay and agree_note is empty [check: tests/declension/]
- Given a phrase no rule fits, When agree runs, Then it stays and agree_note names the reason [check: tests/declension/]

## How to test

Unit tests of the agreement rules on phrase pairs, and an integration run through the semkit CLI runner: linear-combinations then agree on a small combine table.

## Basis

core/declension (phrase.py, forms.py) and the decline step for case and animacy; core/corpus/combinations.py for linear-combinations.

## Read first

- `src/rb_semkit/core/declension/phrase.py`

## Out of scope

- A syntax parser; verb government other than the accusative (a dictionary of government); reordering words; changing the meaning-filter steps.

## Feedback

### Attempt 1: file docstring

- update the docstring of src/rb_semkit/core/declension/forms.py: +adjective_case
