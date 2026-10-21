---
id: SEMKIT-073
title: 'Template v1.25.8: the gate with the CI colour fix on Python 3.11'
status: publish
attempts: 1
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
translation: 'Обновить шаблон до v1.25.8: гейт с исправлением цвета в CI на Python
  3.11 (из-за него красный CI выпуска). requires-python не меняется; .agents/ не трогать
  — строку гейта Архитектор уже поменял.'
---

cli-generator (2026-10-21): the gate of template v1.25.8 runs on Python >=3.11 and fixes 'standard: commands' on CI (Rich colour under GITHUB_ACTIONS). semkit's release candidates are red on Gitea CI with the v1.23.1 gate. The gate tag is the template tag (`_commit` in .copier-answers.yml), so semkit moves from template v1.23.1 to v1.25.8. requires-python stays ">=3.11".

1. Stage the tree (`git add -A`) and run copier with the dirty-tree guard off, as before (a worker may not commit). Then `uvx copier update --trust --defaults --vcs-ref v1.25.8`. Resolve conflicts hunk by hunk: keep semkit's behaviour, take the template's fix. An older package keeps all its parts on update (the optional parts are copier questions now).
   - .gitea/workflows/ci.yml: take the template's gate step at v1.25.8, but keep semkit's trigger (push on branches main and antagor/publish-*, no paths filter), `options: --init` and the ci-cache volume.
   - The `docs` command left the template; semkit keeps its own `docs` command, core/docs.py and steps/docs_hook.py.
   - pyproject.toml: keep `-m 'not speed'` in pytest addopts and `gate_extras = ["vectors"]`.
   - The gate line in .agents/antagor/antagor.toml is already at v1.25.8 on main: do not touch .agents/.
2. `uv lock` if the template asks; `uv run --extra vectors pytest --snapshot-update`, read the diff: only rendering changes.
3. The gate (the command below) ends with 'release: gate passed'. If a Standard rule looks wrong for semkit, ask in the inbox, do not work around it.

## Read first

- `.copier-answers.yml`
- `.agents/antagor/antagor.toml` — read only: its gate line is already at v1.25.8

## Acceptance

- Given the updated repo, When the gate runs at the template tag, Then .copier-answers.yml has `_commit: v1.25.8`, CI runs the gate at v1.25.8, and the gate ends with 'release: gate passed' [check: sh -c 'uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check']

## Out of scope

- requires-python, semkit's own commands and behaviour.
- .agents/: the Architect's.

## Basis

Follow SEMKIT-068 (the last template update): the same steps and the same things to keep.

## Feedback

### Attempt 1: file docstring

- update the docstring of src/rb_semkit/commands/describe.py: +register
- update the docstring of src/rb_semkit/commands/skill.py: +register
- update the docstring of src/rb_semkit/core/version.py: +optional_module
