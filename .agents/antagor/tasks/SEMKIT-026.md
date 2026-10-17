---
id: SEMKIT-026
title: Refresh the 11 step help snapshots that now list the word lists
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
type: chore
owns_paths:
- tests/snapshots/help/steps/change/
- tests/snapshots/help/steps/corpus/
- tests/snapshots/help/steps/markers/
test_paths:
- tests/test_help.py
docs: none
tools: []
worker_args: null
class: mechanical
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-003
spec_refs: []
checks:
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
---

SEMKIT-024 and SEMKIT-025 were built side by side: 025 made every step that takes items end its --help with the available word lists, and the 11 snapshots of 024's steps were taken without it. main fails test_help_snapshot for read-change-case, read-move-words, read-first-children, read-first-parents, read-nearest-parents, read-split-by-words, read-find-markers, read-remove-markers, read-extract-markers, read-keep-markers, read-drop-markers. Run uv run pytest tests/test_help.py --snapshot-update, check that each diff only adds the list of word lists at the end of the help, and commit the snapshots. No code change.

## Out of scope

- Any change of the help text itself (the generator, the docstrings): a separate task.
