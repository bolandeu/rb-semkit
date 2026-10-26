---
id: SEMKIT-087
title: 'relate-phrases: a link source knows every word of the table, so the order
  of the rows does not change a refinement'
status: in_review
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
- src/rb_semkit/core/relate/
- src/rb_semkit/steps/relate.py
- tests/relate/
- tests/snapshots/
test_paths:
- tests/relate/test_latin.py
- tests/relate/test_links_seam.py
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-082
budget_usd: null
epic: E-009
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
resident: null
tool: null
pr: null
translation: Источник latin знает только слова, о которых его уже спросили, поэтому
  результат зависит от порядка строк (веб/web). Источник должен знать все слова таблицы
  до первого поиска связей; порядок строк не должен менять уточнение.
---

The Latin link source gives a different result when the rows come in a different order, which breaks the rule of the epic that a refinement does not depend on the order of the rows. Found by hand on v0.1.69:

- rows «разработка веб», then «разработка web сайтов»: the second is a refinement of the first, reason `+сайт; web~веб (latin)` (right);
- rows «разработка web сайтов», then «разработка веб»: both are other, reasons `unlinked: сайт | ` (wrong: the first is a refinement of the second, with the same reason).

Cause: `_Latin` (core/relate/sources/latin.py) remembers only the words it was asked about (`_by_sound`, filled by `forms`), and `linked` answers from that memory. The phrases are processed in row order, so a word of a later row is not yet known when an earlier row looks for its candidates through the index (`_Table._hits` in core/relate/functions.py); with the dictionary source (SEMKIT-082) the runs of words are asked about only for phrases with two or more words, so a single word is not registered either.

Fix: a source must know all the words of the table before the first link is looked up, whatever the order of the rows. Extend the link interface (core/relate/sources/__init__.py) as needed, for example a step in which the reader gives every source every word of the table before the relations are found; the sources of SEMKIT-082 and SEMKIT-084 must keep working. A test source that answers only for the words it has seen must show the same result for any order of the rows. Do not change any class rule.

## Acceptance

- Given «разработка web сайтов» first and then «разработка веб», When the step runs, Then the first is a refinement of the second with reason +сайт; web~веб (latin), the same as when the rows come the other way round [check: tests/relate/test_latin.py]
- Given a test link source that answers only for the words it has seen, When the rows of a table come in any order, Then the refinements found are the same [check: tests/relate/test_links_seam.py]

## How to test

level: integration through the pipeline plus a unit test of the link seam; seam: semkit read TABLE.jsonl relate-phrases … write -; data: small JSONL tables, both orders of the same rows

## Basis

Follow the link interface of core/relate/sources/__init__.py and the Reader of core/relate/phrases.py; the fix goes to the interface or the reader, not to a special case in the Latin module only

## Read first

- `src/rb_semkit/core/relate/sources/latin.py`
- `src/rb_semkit/core/relate/phrases.py`
- `src/rb_semkit/core/relate/functions.py`

## Out of scope

- The class rules, the dictionary links, --synonyms, the speed of the step.
