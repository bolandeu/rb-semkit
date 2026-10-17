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
---

x

## Out of scope

- x
