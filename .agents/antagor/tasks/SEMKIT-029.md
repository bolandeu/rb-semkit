---
id: SEMKIT-029
title: 'Project config test: .agents/antagor/.gitignore holds state/ and receipts/;
  Antagor may add its own lines'
status: queue
attempts: 0
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: architect
worker: claude-code
type: chore
owns_paths:
- tests/test_scripts.py
test_paths:
- tests/test_scripts.py
docs: none
tools: []
worker_args: null
class: mechanical
decision: false
visual: null
depends_on: []
budget_usd: null
epic: null
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**Тест конфига Antagor.** Тест ждёт в .agents/antagor/.gitignore ровно
  state/ и receipts/, а обновление Antagor добавило scratch/ — гейт красный. Проверять,
  что state/ и receipts/ есть; свои строки Antagor добавлять может.'
---

tests/test_scripts.py::test_antagor_project_config asserts .agents/antagor/.gitignore is exactly ['state/', 'receipts/']. The Antagor upgrade added 'scratch/', so the gate is red on main. Assert that state/ and receipts/ are among the lines and let Antagor add its own, as the same test does for the publish keys.

## Read first

- `tests/test_scripts.py`
- `.agents/antagor/.gitignore` — read only, Antagor writes it

## Out of scope

- Any change to other tests.
