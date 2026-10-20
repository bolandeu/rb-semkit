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
---

x

## Read first

- `.gitattributes`

## Out of scope

- x
