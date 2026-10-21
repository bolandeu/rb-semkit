---
id: SEMKIT-071
title: Comments, docstrings, README and help name no cli-generator internal file and
  no numbered Standard section
status: publish
attempts: 0
blocked: true
blocked_reason: idea_wait
phase: null
tests_hash: null
publish_stage: gate
created_by: architect
approved_by: human
worker: claude-code
type: chore
owns_paths:
- src/
- tests/
- scripts/check_command_docstrings.py
- README.md
- pyproject.toml
- .gitleaks.toml
test_paths: []
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
- 'sh -c ''uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed
  -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check'''
resident: null
tool: null
pr: null
translation: 'Убрать из комментариев, docstring, README и справки ссылки на внутренние
  файлы cli-generator (architecture.md, conventions.md, help-standard.md) и номера
  разделов Standard (§N): правило словами или раздел Standard по имени. Поведение
  не меняется.'
---

From cli-generator (the Human asked for it, 2026-10-21): semkit is a product with its own docs and docs/adr; text in it must not point at cli-generator's own development. Change comments, docstrings, README and help text only; no behaviour change.

1. Find: `git grep -n -E 'architecture\.md|conventions\.md|help-standard\.md|cli-generator plugin|[Ss]tandard §' -- src tests scripts README.md pyproject.toml .gitleaks.toml`. Today about 20 files, among them .gitleaks.toml, README.md (the lines that send the reader to cli-generator's architecture file and to the cli-generator plugin's README), pyproject.toml, scripts/check_command_docstrings.py, and files under src/rb_semkit/ and tests/.
2. Replace each reference with the rule in plain words, or with the Standard's section by its name (for example "the Standard, Help"), or drop it when it adds nothing. semkit's own help standard for its steps stays semkit's: call it "the help standard", not by a cli-generator file name.
3. Keep: the Standard link and the gate command in AGENTS.md, CODING_STANDARDS.md, CI and README; the `[tool.cli-generator]` settings key; `contact: "cli-generator"` in the tools-catalog contract under tests/contracts/; semkit's own references (to its plan, its VBA notes and its ADRs, with their § numbers).
4. If a help text changes, refresh the snapshots (`--snapshot-update`) and read the diff: only the reference text.
5. The gate ends with 'release: gate passed'; the grep of step 1 finds nothing.

## Read first

- `AGENTS.md` — the Standard link and the gate command, read only
- `CODING_STANDARDS.md` — read only

## Acceptance

- Given src, tests, scripts, README.md, pyproject.toml and .gitleaks.toml, When the grep of step 1 runs, Then it finds nothing, and the gate ends with 'release: gate passed' [check: sh -c 'uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check']

## Out of scope

- Behaviour, option names, exit codes.
- docs/, CHANGELOG.md, AGENTS.md, CODING_STANDARDS.md, .agents/: history and the Architect's files.

## Basis

Template v1.25.2 of cli-generator removed the same references from the template; follow its wording where semkit's file came from the template.
