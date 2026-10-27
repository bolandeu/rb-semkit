---
id: SEMKIT-085
title: 'relate-phrases acceptance: the table end to end, precision on 200 pairs, speed,
  documents'
status: in_review
attempts: 1
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
- src/rb_semkit/core/relate/
- src/rb_semkit/steps/relate.py
- src/rb_semkit/data/SKILL.md
- README.md
- tests/relate/
- tests/snapshots/
test_paths:
- tests/relate/test_acceptance.py
- tests/relate/test_precision.py
- tests/relate/test_speed.py
docs:
- README.md
- src/rb_semkit/data/SKILL.md
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-081
- SEMKIT-082
- SEMKIT-083
- SEMKIT-084
- SEMKIT-087
budget_usd: null
epic: E-009
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
resident: null
tool: null
pr: null
translation: 'Приёмка эпика: таблица из плана целиком через конвейер (тезаурус из
  реальных связей слов + тестовый --synonyms), стык латиницы и словаря (web сайт →
  веб-сайт), точность на 200 размеченных парах (реальный тезаурус, исключения — в
  отчёт), скорость 1000 фраз за секунды (marker speed), README и справка для агентов.'
---

Close the epic with the checks of the whole step: the acceptance table of the plan end to end, the precision on the labelled pairs, the speed, and the user documents. All link sources exist now (the lemmas, the dictionary, the Latin reading, the caller's groups); this task joins them where they meet and fixes what the checks find.

- The acceptance table: every row of section 4 of the plan (docs/plans/relate-phrases.md) as a test through the pipeline, with a test thesaurus made of the real senses and relations of the words of the table (section 2 of the plan lists the links checked by hand), and a test `--synonyms` file for «починить стиральную машину». The same table runs against the real thesaurus in a test that needs it (marker `real_encoder`, left out when the model is not pulled).
- The join of the Latin reading and the dictionary: «разработка web сайтов» at «разработка сайтов» is a variation (the reading «веб сайт» finds the run веб-сайт, which is one synset with сайт). If the run lookup of the dictionary does not use the other forms of a word yet, make it so.
- Precision: the 200 labelled phrase pairs of tests/vectors/fixtures/phrase_pairs.tsv run through the step (real thesaurus, marker as above): no pair labelled as another intent may come out same or variation. For each pair that does, put the phrases, the link and the reason in the report. Fix a bug of the code. A link that is the dictionary's own polysemy (a word of two senses) is reported, not worked around, and the fixture is never edited.
- Speed: the 1000 phrases of the sofa core (tests/e2e/test_ten_runs.py names the file) run in seconds, in a test with the marker `speed` (left out of the gate): at most 10 seconds on the development machine, without the load of the thesaurus. If it is slower, fix the index.
- Documents: the step in README.md (an example) and in the bundled agent guide, with the classes, the columns, `--synonyms` and its two shapes, and the limits (dictionary gaps are `other`: сделать ≁ создать, починить ≁ ремонт; the caller's links fill them).

## Acceptance

- Given the table of section 4 of the plan, When each row runs through the pipeline with the test thesaurus and the test --synonyms file, Then every row gets the class, of, group and reason that the table gives [check: tests/relate/test_acceptance.py]
- Given «разработка сайтов» first and then «разработка web сайтов», When the step runs, Then the second is a variation: the Latin reading finds the run веб-сайт in the dictionary [check: tests/relate/test_acceptance.py]
- Given the 200 labelled pairs and the real thesaurus, When they run through the step, Then no pair labelled as another intent comes out same or variation, or each exception is in the report with its link [check: tests/relate/test_precision.py]
- Given the 1000 phrases of the sofa core, When the step runs, Then it ends in at most 10 seconds without the load of the thesaurus [check: tests/relate/test_speed.py]
- Given the README and the bundled agent guide, When a reader looks for relate-phrases, Then both describe the classes, the columns, --synonyms with its two shapes and the limits, with an example that runs [check: tests/relate/test_acceptance.py]

## How to test

level: integration through the pipeline; seam: semkit read TABLE.jsonl relate-phrases … write -; data: the plan's table in a test file, a small test thesaurus, the labelled pairs fixture, the sofa core; the precision and the real-table tests need the pulled thesaurus (marker real_encoder), the speed test the marker speed

## Basis

Follow the tests of SEMKIT-081 to SEMKIT-084 and the examples of the existing steps in README.md; no new rule here: a failing check is a bug of an earlier task, fixed in the code

## Read first

- `docs/plans/relate-phrases.md`
- `tests/vectors/fixtures/phrase_pairs.tsv`
- `tests/e2e/test_ten_runs.py`
- `README.md`

## Out of scope

- New classes, new link sources, vectors, a bundled list of links, SERP. A change of the labelled pairs. The glossary CONTEXT.md and the docs/adr: the Architect's.

## Feedback

### Attempt 1: the project's full check failed after the merge

The project's full check fails with this task merged into main, and passes without it: your change broke something elsewhere. Merge main into your branch and fix it within the task, or say what is outside it with `antagor inbox add`.

- `the project's CI (https://homeserver.tailee01ab.ts.net:3000/api/v1/repos/bolandeu/semkit/commits/{commit}/status)`

```
CI status: failure
ci / gate (push): failure — Failing after 17s https://homeserver.tailee01ab.ts.net:3000/bolandeu/semkit/actions/runs/643/jobs/831
```
