---
id: SEMKIT-063
title: 'Template update: copier update to cli-generator v1.18.2, help snapshots refreshed,
  gate green'
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
- src/
- tests/
- scripts/
- .gitea/
- .github/
- pyproject.toml
- uv.lock
- .copier-answers.yml
- README.md
- CHANGELOG.md
- .gitignore
- .python-version
- changelog.d/
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
- uv run --extra vectors pytest
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: Обновить шаблон cli-generator с v1.15.0 до v1.18.2 (copier update), разрешить
  конфликты, обновить снимки справки, гейт зелёный.
---

cli-generator v1.18.2 is out: the template's tests pass in Gitea Actions (help snapshots with GITHUB_ACTIONS=true; detach sees a zombie as finished; tests/conftest.py is always there). semkit is on v1.15.0 (.copier-answers.yml).

1. `copier update --trust --vcs-ref v1.18.2 --defaults`. Follow the Update mode of the cli-generator:cli-builder skill.
2. Resolve each conflict keeping semkit's behaviour and taking the template's fix. Likely conflicts:
   - tests/conftest.py: semkit's own fixtures (test encoder, word data, plain help env from SEMKIT-061) stay; merge the template's parts.
   - core/docs.py and commands/docs.py: semkit's version (SEMKIT-054/058) was the reference for the template's docs command (CG-016). Take the template's version when it does the same; keep semkit's hook (steps/docs_hook.py).
   - .gitea/workflows/ci.yml: keep semkit's paths filter and `options: --init`.
3. `uv run --extra vectors pytest --snapshot-update`; review the snapshot diff: only rendering changes, no lost options or text.
4. `uv run scripts/release.py --check` green.

## Read first

- `.copier-answers.yml` — the current template version

## Out of scope

- New features from the template that need a decision of the Architect: report them in the inbox instead.

## Basis

The cli-builder skill, Update mode; cli-generator v1.18.2 release notes.
