---
id: SEMKIT-052
title: 'nearest --to TEXT: the texts to match given on the command line instead of
  a file'
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
- src/rb_semkit/steps/nearest.py
- src/rb_semkit/core/nearest/
- src/rb_semkit/data/SKILL.md
- tests/snapshots/
- tests/nearest/
test_paths:
- tests/nearest/test_nearest.py
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
translation: 'nearest --to "фраза": образец прямо в команде вместо файла; вместе с
  read --text — сравнение фразы с фразой.'
---

nearest takes the texts to match only from a file (AGAINST / --against). To compare with one phrase the user makes a file of one row.

1. --to TEXT (repeatable): the texts to match, one per --to, in the order given; it is the against table with one column text and no url.
2. --to and AGAINST/--against together are refused with exit 2 naming both; neither is refused as now.
3. The report, --top, --threshold and --model work as with a file.
4. Step help with an example: semkit read phrases.csv nearest --to "растаможка авто" --threshold 0.85; the agent guide mentions it.

## Acceptance

- Given a table of phrases and --to 'растаможка авто', When nearest runs, Then the report is the same as with an against file of one row 'растаможка авто' [check: tests/nearest/test_nearest.py]
- Given --to 'a' --to 'b' and --top 2, When nearest runs, Then each row has matches among a and b, the nearest first [check: tests/nearest/test_nearest.py]
- Given --to and an against file together, When nearest runs, Then it is refused with exit 2 naming both [check: tests/nearest/test_nearest.py]

## How to test

Integration through the semkit CLI runner with the small test encoder the nearest tests use.

## Basis

steps/nearest.py (how AGAINST is read into a table).

## Out of scope

- read --text (SEMKIT-049); other steps with a file option.
