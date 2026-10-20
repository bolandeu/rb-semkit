---
id: SEMKIT-068
title: 'Template v1.23.0: the gate through uvx from cli-generator, rb-cli-core gone'
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
- src/
- tests/
- scripts/
- .gitea/
- pyproject.toml
- uv.lock
- .copier-answers.yml
- .gitleaks.toml
- README.md
- CHANGELOG.md
- .gitignore
- .python-version
- CODING_STANDARDS.md
- AGENTS.md
- .agents/antagor/antagor.toml
test_paths: []
docs: none
tools: []
worker_args: null
decision: false
visual: null
depends_on: []
budget_usd: null
epic: null
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run rb-release check
resident: null
tool: null
pr: null
---

From cli-generator (the Human said to send it), 2026-10-20: move semkit to template v1.23.0; the gate is uvx --from git+…/cli-generator.git@<template tag>#subdirectory=gate rb-release check; adopt_core, rb-cli-core and release.py are gone; the gate checks the Standard's mandatory rules (standard.md). Release, then send the version to cli-generator.

(from IDEA-294)
