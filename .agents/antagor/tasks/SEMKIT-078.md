---
id: SEMKIT-078
title: 'Table steps: fill-down counts the filled cells; lookup leaves unmatched cells
  empty and names its FILE'
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
type: bugfix
owns_paths:
- src/rb_semkit/core/lookup/
- src/rb_semkit/steps/lookup.py
- src/rb_semkit/steps/rows.py
- src/rb_semkit/core/rows/
- src/rb_semkit/pipeline/state.py
- src/rb_semkit/steps/__init__.py
- tests/lookup/
- tests/rows/
- tests/snapshots/help/steps/lookup/
- tests/snapshots/describe/steps/lookup/
- tests/snapshots/help/steps/rows/
- tests/snapshots/describe/steps/rows/
- src/rb_semkit/data/SKILL.md
test_paths:
- tests/lookup/
- tests/rows/
docs: none
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
- python3 scripts/check_command_docstrings.py
- uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@v1.26.3#subdirectory=gate"
  rb-release check
resident: null
tool: null
pr: null
translation: 'Три дефекта табличных шагов E-008 с моей ручной проверки v0.1.65: (1)
  fill-down пишет «0 cells changed», хотя заполнил ячейки — должен считать заполненные;
  (2) lookup ставит несовпавшим строкам пустой текст "", из-за чего числовой столбец
  в JSONL смешивает числа и строки — должна быть пустая ячейка (null); (3) lookup
  при несуществующем файле пишет «Give --file», а файл — позиционный аргумент: сообщение
  должно называть FILE шага lookup.'
---

Three defects of the table steps of E-008, found by the Architect's manual check of v0.1.65.

1. fill-down reports «0 cells changed» (stderr and `cells_changed` in --json) though it filled cells. It must report the number of cells it filled. The other table steps (sample-rows, shuffle-rows, group-rows, split-rows, unpivot, lookup) change no cell of the input: their 0 stays.
2. lookup gives an unmatched row the empty text "" in each new column. In JSONL a number column then mixes numbers and texts ({"freq": 99} and {"freq": ""}). An unmatched cell must be an empty cell (null in JSON, an empty cell in CSV and xlsx), so a number column stays numbers.
3. lookup with a lookup table file that does not exist says «Give --file a file that exists», but the file is a positional argument, not an option --file. The message must name the argument as the command line takes it (the FILE of lookup). Other steps that read a second file by an option (compare-lists --against and others) keep their messages.

## Acceptance

- Given a column cluster with values диван, '', кресло, '', When fill-down --column cluster runs, Then the report says 2 cells changed (stderr «fill-down: 4 → 4 rows, 2 cells changed», --json cells_changed 2) [check: tests/rows/]
- Given a table of phrases (купить диван, кресло) and a lookup table (phrase, freq) with (купить диван, 99), When lookup FILE --on phrase runs and writes JSONL, Then the rows are {phrase: купить диван, freq: 99} and {phrase: кресло, freq: null}, and a CSV output has an empty cell for кресло [check: tests/lookup/]
- Given a lookup table file that does not exist, When lookup FILE runs, Then semkit refuses before writing, and the message names the FILE of lookup, not an option --file; compare-lists --against with a missing file keeps its message [check: tests/lookup/]

## How to test

Integration through the command line pipeline: semkit read TABLE.jsonl STEP ... write -, on small JSONL tables written by the test; --json for cells_changed

## Basis

The steps of E-008 (SEMKIT-075, SEMKIT-077): steps/rows.py, steps/lookup.py; the State in pipeline/state.py counts the cells a step changes

## Read first

- `src/rb_semkit/pipeline/state.py`
- `src/rb_semkit/steps/lookup.py`

## Out of scope

- The shape steps' counts (group-rows, split-rows, unpivot), the lookup note text, other steps' messages
