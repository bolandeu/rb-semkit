---
id: SEMKIT-069
title: 'Rename scenario to workflow: code, help, bundled folder and the project folder
  .rb_semkit/workflows/'
status: queue
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
- src/
- tests/
- README.md
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
translation: 'Переименовать «сценарий» в «workflow» по ADR 0011: код, справка, SKILL.md,
  README, встроенная папка data/workflows/, папка пользователя .rb_semkit/workflows/
  (старая scenarios/ ещё читается); команда остаётся semkit run NAME.'
---

ADR 0011 (the Human, 2026-10-20): the named, saved chain of semkit steps run by `semkit run NAME` is a workflow, not a scenario. The term in CONTEXT.md is already changed. Rename it everywhere in the product.

1. Code: modules, names, messages and docstrings: scenario -> workflow (src/rb_semkit/pipeline/scenarios.py, src/rb_semkit/core/scenarios/, src/rb_semkit/commands/run.py, src/rb_semkit/pipeline/group.py, src/rb_semkit/pipeline/run.py, src/rb_semkit/core/services.py).
2. Bundled folder: src/rb_semkit/data/scenarios/ -> src/rb_semkit/data/workflows/ (git mv; the wheel must still ship it).
3. The user's folder: .rb_semkit/workflows/. Keep reading the old .rb_semkit/scenarios/ too, so saved files do not break; a name in both: workflows/ wins. Say the old folder is read in one line of `run --help`.
4. Help, src/rb_semkit/data/SKILL.md and README.md: the word workflow. The command stays `semkit run NAME`.
5. Tests: tests/scenarios/ -> tests/workflows/; add a test that a file in the old .rb_semkit/scenarios/ still runs and that workflows/ wins over it. Refresh the help and describe snapshots (`--snapshot-update`), read the diff: only the word changes, and the new line about the old folder.
6. The gate ends with 'release: gate passed'.

## Acceptance

- Given a project folder with .rb_semkit/workflows/NAME.toml, When 'semkit run NAME' runs, Then it runs that workflow; and a file only in .rb_semkit/scenarios/ still runs [check: sh -c 'uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check']
- Given src/, tests/, README.md and SKILL.md, When searched for 'scenario' (any case), Then only the old-folder fallback and its test name it [check: sh -c 'uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check']

## Out of scope

- CHANGELOG.md history and docs/plans/: they record the past.
- CONTEXT.md and docs/adr/: the Architect has changed them.
- The command name `run`.

## Basis

Follow ADR 0011 and the Workflow entry of CONTEXT.md; keep the loader in src/rb_semkit/pipeline/scenarios.py and src/rb_semkit/core/scenarios/__init__.py, only renamed.

## Read first

- `docs/adr/0011-workflow-not-scenario.md`
- `CONTEXT.md`
- `src/rb_semkit/pipeline/scenarios.py`
- `src/rb_semkit/core/scenarios/__init__.py`
