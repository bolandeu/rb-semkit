---
id: SEMKIT-065
title: 'Template v1.20.7: sysadmin contract (Gitea source, Gitea CI, secret scan,
  registry deps) and the gate from rb-cli-core'
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
- .github/
- pyproject.toml
- uv.lock
- .copier-answers.yml
- .gitleaks.toml
- README.md
- AGENTS.md
- CHANGELOG.md
- .gitignore
- .python-version
- changelog.d/
- CODING_STANDARDS.md
- antagor.toml
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
- uv run rb-release check
resident: null
tool: null
pr: null
translation: 'Обновить шаблон до v1.20.7: контракт sysadmin (источник Gitea, CI в
  Gitea, gitleaks, .env, rb-dataio из реестра gitea) и гейт из rb-cli-core (adopt_core=true,
  scripts/release.py удалён, гейт — uv run rb-release check).'
---

On the Human's command (via cli-generator, IDEA-256, widened 2026-10-19): semkit is the first package to cross the sysadmin contract (/Users/bolandau/Work/tools/cli-generator/docs/contracts/sysadmin.md) and to take the gate from rb-cli-core. semkit is on template v1.18.2, source `gh:bolandeu/cli-generator`. Target: template v1.20.7. Follow the cli-generator:cli-builder skill (/Users/bolandau/Work/tools/cli-generator/skills/cli-builder/SKILL.md), Update mode: step 13, sub-steps 1–9, then step 14.

1. Template source: in `.copier-answers.yml` set `_src_path: https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git` and `repository_url: https://homeserver.tailee01ab.ts.net:3000/bolandeu/semkit`. Commit `chore(copier): template source Gitea`.
2. `uvx copier update --trust --defaults --vcs-ref v1.20.7 --pretend` must say "Updating to template version v1.20.7". Then `uvx copier update --trust --defaults --vcs-ref v1.20.7`. Resolve conflicts hunk by hunk: keep semkit's behaviour, take the template's fix.
   - tests/conftest.py: semkit's fixtures (test encoder, word data, plain help env) stay.
   - core/docs.py, commands/docs.py: `docs --out` must still report success (the SEMKIT-064 regression from the v1.18.2 merge must not come back); semkit's hook steps/docs_hook.py stays.
   - .gitea/workflows/ci.yml: keep semkit's `paths` filter, `options: --init` and the ci-cache volume; take the template's new gate steps (gitleaks, registry index).
3. CI move: `.github/` holds only dependabot.yml (Renovate replaces it). `git rm -r .github`. tests/test_ci.py must pass.
4. Secret scan: `gitleaks` over the whole history with the template's `.gitleaks.toml`. A fake test value of semkit's own goes to `regexes` as one exact string. Any real finding: stop, do not commit, do not rewrite history; block the task with the secret's name and file.
5. `.env` and `.env.*` in `.gitignore` (`grep -n '^\.env' .gitignore`). No tracked env file.
6. Registry deps: in `[tool.uv.sources]` replace the `rb-dataio` git+tag source with `rb-dataio = { index = "gitea" }`; the `rb-dataio>=…` line in `dependencies` stays. `uv lock`.
7. Shared keys / new keys: semkit reads no provider keys today; confirm with a grep and say so in the report. No ticket needed if none.
8. Commit the step-13 state. Then step 14: `uvx copier update --trust --defaults --vcs-ref v1.20.7 --data adopt_core=true`, conflicts hunk by hunk. `scripts/release.py` goes away (`test ! -e scripts/release.py`). The gate is `uv run rb-release check` (rb-cli-core>=0.1.2,<0.2 from the gitea index). CI, antagor.toml and the docs call it; `grep -rn 'release\.py' .` finds nothing live (CHANGELOG history and .agents/ excepted). Edit the gate command in README.md by hand (copier skips it).
9. Gate: `uv lock`, `uv run --extra vectors pytest --snapshot-update`, read the snapshot diff (only rendering changes, no lost options or text), then `uv run rb-release check` ends with "release: gate passed".

## Acceptance

- `.copier-answers.yml` has the Gitea `_src_path`, `_commit: v1.20.7` and `adopt_core: true`; `scripts/release.py` is gone. [check: uv run rb-release check]
- `.github/` is gone; `.gitea/workflows/ci.yml` keeps the paths filter and `--init` and calls `uv run rb-release check`. [check: uv run rb-release check]
- `rb-dataio` and `rb-cli-core` come from the `gitea` index in pyproject.toml and uv.lock. [check: uv run rb-release check]
- `semkit docs --out <dir>` reports success. [check: uv run rb-release check]

## Out of scope

- semkit's own behaviour and commands: no changes beyond the merge.
- The release and the message to cli-generator: the Architect does them after acceptance.
