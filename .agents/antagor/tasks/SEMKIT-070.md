---
id: SEMKIT-070
title: 'Help and describe snapshots are generated files: tests/snapshots/** linguist-generated'
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
- .gitattributes
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
- 'sh -c ''uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed
  -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check'''
resident: null
tool: null
pr: null
translation: 'Пометить снимки справки tests/snapshots/** как linguist-generated в
  .gitattributes (правило Человека 20.10): обновление шаблона больше не упирается
  в max_files.'
---

The Human's rule (2026-10-20): generated files go to .gitattributes as linguist-generated, so Antagor counts them by file. tests/snapshots/ holds 326 files written by `pytest --snapshot-update`; a template update that refreshes the help of the 145 pipeline steps goes over max_files = 150.

1. Add one line to .gitattributes: `tests/snapshots/** linguist-generated`, with a short comment above it in the style of the file (written by pytest --snapshot-update, read in review as a diff).
2. The gate ends with 'release: gate passed'.

## Read first

- `.gitattributes`
- `tests/snapshots/help/run.txt` — one of the snapshots, read only

## Acceptance

- Given .gitattributes, When git check-attr linguist-generated runs on tests/snapshots/help/run.txt, Then it says set, and the gate ends with 'release: gate passed' [check: sh -c 'uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check']

## Out of scope

- The snapshots themselves.
