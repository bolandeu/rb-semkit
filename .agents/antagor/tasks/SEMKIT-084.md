---
id: SEMKIT-084
title: 'relate-phrases --synonyms: groups of synonyms of the caller, items of several
  words'
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
- src/rb_semkit/core/relate/sources/own_links.py
- tests/relate/test_own_links.py
- tests/snapshots/
test_paths:
- tests/relate/test_own_links.py
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-081
budget_usd: null
epic: E-009
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
resident: null
tool: null
pr: null
translation: 'Свои связи для relate-phrases: --synonyms FILE с группами синонимов,
  элемент может быть из нескольких слов (стиральная машина | стиралка | стиральная
  машинка). Две формы файла: столбец synonyms с разделителем | или столбцы word и
  synonyms, как у dupes. Без цепочек между группами. Списка связей в пакете нет.'
---

Add the links of the caller to relate-phrases: `--synonyms FILE` with groups of synonyms, where an item may be several words. Windmill makes the file per run (the LLM grouping and the right column of Wordstat); nothing of it is bundled.

- The link source «synonyms», one new module in the package of sources that SEMKIT-081 made (found by itself; do not edit the step module or any other shared file). It adds the option `--synonyms` through the options of a source.
- The file is a table read like the other steps read their tables. Two shapes: (A) a column `synonyms`, one group per row, the items split by `|` (an item may be several words): `стиральная машина | стиралка | стиральная машинка`, `ремонт | починка | ремонтировать | починить`. (B) the columns `word` and `synonyms` of `dupes --synonyms` (the synonyms split by spaces): a group of the word and its synonyms. A file with neither shape is refused with a message that names the missing column; an unreadable file is refused with its path; a group of one item is ignored.
- Items are compared by lemmas, as runs of words. An item of several words is a run the cut of a phrase knows (the source gives it as a run), so «стиральная машина» in a phrase is one unit that links to «стиралка».
- The items of one group are linked to each other. No chain across groups: if a ~ b in one group and b ~ c in another, a and c are not linked. A word in two groups links through both. `reason` names it: `починить~ремонт (synonyms)`.
- The help of the step documents the option and the two shapes with an example; the help snapshot is updated.

## Acceptance

- Given a file of groups (shape A) «ремонт | починка | ремонтировать | починить», When «ремонт стиральных машин» comes first and then «починить стиральную машину», Then the second is a variation with reason починить~ремонт (synonyms) [check: tests/relate/test_own_links.py]
- Given the group «стиральная машина | стиралка | стиральная машинка», When «ремонт стиральных машин» comes first and then «ремонт стиралки» and «ремонт стиральной машинки», Then both are variations: the item of several words is matched as a run [check: tests/relate/test_own_links.py]
- Given the same groups as a table with the columns word and synonyms (shape B), When the step runs, Then the result is the same for the words it holds [check: tests/relate/test_own_links.py]
- Given the groups a ~ b and b ~ c in two rows, When «a x» comes first and then «c x», Then the second is other; Given a word in two groups, Then it links through both [check: tests/relate/test_own_links.py]
- Given a file with neither shape, an unreadable file and a group of one item, When the step runs, Then the first two are refused with a message that names the missing column or the path, and the third is ignored [check: tests/relate/test_own_links.py]

## How to test

level: integration through the pipeline plus unit tests of the reader; seam: semkit read TABLE.jsonl relate-phrases --synonyms FILE … write -; data: small files written in the test (tmp_path)

## Basis

Follow how dupes reads its --synonyms table (src/rb_semkit/steps/dupes.py: refining_options, as_table, table_of) and the interface of the link sources that SEMKIT-081 made; one new module, found by itself

## Read first

- `docs/plans/relate-phrases.md`
- `src/rb_semkit/steps/dupes.py`
- `tests/conftest.py`

## Out of scope

- A bundled list of links. A change of the --synonyms of dupes, ad-groups or synonym-candidates, or of their files. Making groups (Windmill does it).
