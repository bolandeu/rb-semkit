---
id: SEMKIT-066
title: 'Antagor checks call the gate from rb-cli-core: the old release script is gone'
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
type: chore
owns_paths:
- .agents/antagor/antagor.toml
test_paths: []
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
- uv run rb-release check
resident: null
tool: null
pr: null
translation: В .agents/antagor/antagor.toml заменить проверку старым скриптом выпуска
  на uv run rb-release check (скрипт удалён в SEMKIT-065); гейт зелёный.
---

SEMKIT-065 removed the old release script, but `checks` in .agents/antagor/antagor.toml still call it. From a clean clone of v0.1.53 the gate fails two tests: tests/test_ci.py::test_project_files_name_the_gate_of_their_answer and tests/test_scripts.py::test_antagor_project_config.

1. In .agents/antagor/antagor.toml set checks = ["python3 scripts/check_command_docstrings.py", "uv run rb-release check"]. Change nothing else.
2. Run `uv run rb-release check`: it ends with "release: gate passed".

## Read first

- `.agents/antagor/antagor.toml`
- `tests/test_ci.py` — the failing test, read only
- `tests/test_scripts.py` — the failing test, read only
- `scripts/check_command_docstrings.py` — the first check, read only

## Acceptance

- Given .agents/antagor/antagor.toml, When the gate runs, Then its checks call 'uv run rb-release check' and the gate ends with 'release: gate passed' [check: uv run rb-release check]

## Out of scope

- Any other file: the template merge is done (SEMKIT-065).
