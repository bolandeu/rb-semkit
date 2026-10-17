---
id: SEMKIT-027
title: 'Step help quality: real examples per step, each option''s own help, bullet
  lists kept; the agent guide uses the bundled lists'
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
- src/rb_semkit/pipeline/
- src/rb_semkit/steps/
- src/rb_semkit/data/SKILL.md
- README.md
- tests/snapshots/help/
test_paths:
- tests/pipeline/
- tests/steps/
- tests/test_help.py
- tests/snapshots/describe.json
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-026
budget_usd: null
epic: E-003
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**Качество справки шагов.** Пример у каждого шага — реальная команда
  (файл — имя файла, список — встроенный список, выбор — его значение), тест запускает
  каждый пример. Справка опции — только её текст (не протекает соседний аргумент).
  Списки в docstring остаются списками. --ai и README: минус-списки (фразы) — drop-phrases
  @minus/universal, отдельные слова — drop-words; пример со своей папкой списков (SEMKIT_LISTS)
  и semkit lists.'
---

The generated --help of the steps is what people and agents read; three defects of the generator and one gap of the guide.
1. Examples: the 'Example:' line fills a required option with a placeholder word, so 'coverage --against' shows 'coverage купить' and 'split-by-words good'. Each step's example must be a runnable command: a file option shows a file name (texts.csv, competitors.csv, serp.csv, freq.csv, pairs.csv), a list option shows a bundled list (@minus/universal, @stop/wordstat), a choice shows one of its values. A step-table entry may give its own example; the generator uses it first.
2. Option help: a docstring line that names several arguments ('core, column: …') or a sentence about another argument inside a line leaks into the previous option's help (coverage --mode, split-by-words --bad, markers --lists). Each option's help holds only its own text; a line naming several arguments gives each of them that text.
3. Bullet and numbered lists of a docstring stay lists in the help, not one reflowed paragraph.
4. The agent guide and README: the typical pipelines use the bundled lists and the right matcher for them: lists of phrases (minus/*) go to drop-phrases, single words to drop-words; add a pipeline with the Human's own list folder (SEMKIT_LISTS or the config lists = [paths]) and semkit lists to see the names.

## Acceptance

- Given every step, When its --help is read, Then its Example line is a command that a test runs on the fixtures without a usage error [check: tests/steps/]
- Given coverage --help and split-by-words --help, When read, Then --mode, --bad and --lists each hold only their own text [check: tests/test_help.py]
- Given a step whose docstring has a bullet list, When its --help is read, Then the bullets are on their own lines [check: tests/test_help.py]
- Given semkit --ai, When read, Then the clean-a-core pipeline uses drop-phrases @minus/universal, and a pipeline shows a user list folder with SEMKIT_LISTS; each example runs in the test [check: tests/steps/]

## How to test

The help snapshots (refreshed, the diff reviewed), a test that runs every step's Example line on fixtures, the existing SKILL.md pipeline test.

## Basis

Fix it in the generator (pipeline package) and, where a step needs it, by an explicit example or option help in its step-table entry; do not rewrite the library docstrings unless a line is wrong for Python users too. The help snapshots show every change.

## Read first

- `src/rb_semkit/steps/__init__.py`
- `src/rb_semkit/data/SKILL.md`

## Out of scope

- New steps or options; changes of the library behaviour.

## Feedback

### Attempt 1: file docstring

- update the docstring of src/rb_semkit/steps/__init__.py: +argument_names +doc_lines +parameter_names
