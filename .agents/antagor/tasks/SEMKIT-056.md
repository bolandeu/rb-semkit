---
id: SEMKIT-056
title: 'Table bricks: use-column switches the working column, sort-rows orders the
  rows by a column'
status: publish
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
- src/rb_semkit/core/table/
- src/rb_semkit/steps/table.py
- src/rb_semkit/pipeline/
- src/rb_semkit/steps/__init__.py
- src/rb_semkit/data/SKILL.md
- tests/table/
- tests/snapshots/
test_paths:
- tests/table/
- tests/steps/areas/table.py
- tests/steps/fixtures/matches.csv
- tests/conformance/case_files.py
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
translation: 'Кирпичики таблицы: use-column NAME — сменить рабочую колонку (чтобы
  drop-cells empty убрал строки без совпадения), sort-rows --by COLUMN [--desc] —
  сортировка строк.'
---

The first scenario (the plan of vectors, phrase synonyms of one intent) needs jq for two things no step does: keep the rows nearest matched (it keeps an empty match for a row below the threshold) and order the rows by similarity. Two generic steps, chain-agnostic:

1. use-column NAME: the column NAME becomes the working column of the next steps; the table does not change. A missing column is refused with exit 2 naming the columns there are. Then drop-cells empty drops the rows with an empty match: nearest … use-column match drop-cells empty.
2. sort-rows --by COLUMN [--desc]: the rows in the order of the column, numbers as numbers, texts in the order of sort-words (ё after е), stable (equal rows keep their order), empty cells last; --by repeatable (the first wins, the next break ties). A missing column is refused with exit 2.
3. Step help with real examples; the agent guide shows nearest … use-column match drop-cells empty sort-rows --by similarity --desc.

## Acceptance

- Given a nearest report with rows below the threshold, When use-column match drop-cells empty runs, Then only the matched rows stay and the working column is match [check: tests/table/]
- Given a table with similarity 0.9, 0.95, empty, 0.8, When sort-rows --by similarity --desc runs, Then the order is 0.95, 0.9, 0.8, empty [check: tests/table/]
- Given equal values, When sort-rows runs, Then the rows keep their order; with --by a --by b the second breaks ties [check: tests/table/]
- Given use-column or sort-rows --by with a missing column, When it runs, Then it is refused with exit 2 naming the columns there are [check: tests/table/]

## How to test

Integration through the semkit CLI runner on small JSONL tables.

## Basis

steps/__init__.py (the step kinds) and pipeline/state.py (the working column).

## Read first

- `docs/plans/vectors.md`

## Out of scope

- semkit run and saved scenarios (the next task); filters by a numeric threshold.

## Feedback

### Answer to question #1

> SEMKIT-056 says texts sort in the order of sort-words (ё after е), but sort-words orders by character codes (ё after я).
> Question: Which text order does sort-rows use?
> Options:
> 1. ё after е
> 2. character codes, as sort-words
> Recommended: ё after е

Option 1: ё after е (Russian alphabet order: е, ё, ж). The task text wrongly tied it to sort-words; sort-words stays as it is. Say the order in the sort-rows help.

### Blocked: needs_scope (entries [{'n': 1, 'text': 'SEMKIT-056 says texts sort in the order of sort-words (ё after е), but sort-words orders by character codes (ё after я).\nQuestion: Which text order does sort-rows use?\nOptions:\n1. ё after е\n2. charact'}])

### Attempt 1: checks failed

- `uv run --extra vectors pytest` (exit 1)

```
y                    46      7    85%   60-61, 65, 72-73, 93-94
src/rb_semkit/core/word_vectors/navec.py         69      1    99%   91
src/rb_semkit/core/wordlists/folders.py          36      1    97%   51
src/rb_semkit/output/__init__.py                122      9    93%   99, 143, 187, 211-214, 257-258
src/rb_semkit/output/human.py                    27      1    96%   31
src/rb_semkit/pipeline/commands.py              192      4    98%   135-136, 169, 185
src/rb_semkit/pipeline/state.py                 135      4    97%   56, 103, 141, 157
src/rb_semkit/pipeline/tables.py                147      8    95%   57, 72, 122, 137, 139, 141, 172, 213
src/rb_semkit/steps/__init__.py                 182      3    98%   191, 252, 274
src/rb_semkit/steps/markers.py                   31      2    94%   36, 42
src/rb_semkit/steps/serp.py                      25      5    80%   23, 28-34
src/rb_semkit/steps/text.py                      70      1    99%   88
---------------------------------------------------------------------------
TOTAL                                          7042    201    97%

131 files skipped due to complete coverage.
Required test coverage of 90.0% reached. Total coverage: 97.15%
--------------------------- snapshot report summary ----------------------------
323 snapshots passed.
=========================== short test summary info ============================
FAILED tests/conformance/test_cases.py::test_every_public_function_has_its_case_file_in_its_area[sort_rows-table]
FAILED tests/conformance/test_cases.py::test_every_public_function_has_its_case_file_in_its_area[use_column-table]
=========== 2 failed, 5647 passed, 26 warnings in 155.98s (0:02:35) ============
/Users/bolandau/Work/tools/semkit.worktrees/SEMKIT-056/.venv/lib/python3.14/site-packages/_pytest/unraisableexception.py:33: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x134a70d60>
  gc.collect()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
```
