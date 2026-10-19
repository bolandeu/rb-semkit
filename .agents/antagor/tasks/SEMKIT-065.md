---
id: SEMKIT-065
title: 'Template v1.20.3: Gitea source, Gitea CI, secret scan, registry deps (first
  package for the Renovate check)'
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
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
---

On the Human's command (via cli-generator, IDEA-256): semkit is the first package to cross the sysadmin contract (/Users/bolandau/Work/tools/cli-generator/docs/contracts/sysadmin.md). semkit is on template v1.18.2, source `gh:bolandeu/cli-generator`. Follow the cli-generator:cli-builder skill, Update mode, step 13, sub-steps 1–9. Do not do step 14 (adopt_core stays false).

1. Template source: in `.copier-answers.yml` set `_src_path: https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git` and `repository_url: https://homeserver.tailee01ab.ts.net:3000/bolandeu/semkit`. Commit `chore(copier): template source Gitea`.
2. `uvx copier update --trust --defaults --pretend` must say "Updating to template version …" (the latest tag, v1.20.3 or newer). Then `uvx copier update --trust --defaults`. Resolve conflicts hunk by hunk: keep semkit's behaviour, take the template's fix.
   - tests/conftest.py: semkit's fixtures (test encoder, word data, plain help env) stay.
   - core/docs.py, commands/docs.py: `docs --out` must still report success (the SEMKIT-064 regression from the v1.18.2 merge must not come back); semkit's hook steps/docs_hook.py stays.
   - .gitea/workflows/ci.yml: keep semkit's `paths` filter, `options: --init` and the ci-cache volume; take the template's new gate steps (gitleaks, registry index).
3. CI move: `.github/` holds only dependabot.yml (Renovate replaces it). `git rm -r .github`. tests/test_ci.py must pass.
4. Secret scan: `gitleaks` over the whole history with the template's `.gitleaks.toml`. A fake test value of semkit's own goes to `regexes` as one exact string. Any real finding: stop, do not commit, do not rewrite history; block the task with the secret's name and file.
5. `.env` and `.env.*` in `.gitignore` (`grep -n '^\.env' .gitignore`). No tracked env file.
6. Registry deps: in `[tool.uv.sources]` replace the `rb-dataio` git+tag source with `rb-dataio = { index = "gitea" }`; the `rb-dataio>=…` line in `dependencies` stays. `uv lock`.
7. Shared keys / new keys: semkit reads no provider keys today; confirm with a grep and say so in the report. No ticket needed if none.
8. Gate: `uv run --extra vectors pytest --snapshot-update`, read the snapshot diff (only rendering changes, no lost options or text), then `uv run scripts/release.py --check` green.

## Acceptance

- `.copier-answers.yml` has the Gitea `_src_path` and `_commit` v1.20.3 or newer. [check: uv run scripts/release.py --check]
- `.github/` is gone; `.gitea/workflows/ci.yml` keeps the paths filter and `--init`. [check: uv run scripts/release.py --check]
- `rb-dataio` comes from the `gitea` index in pyproject.toml and uv.lock. [check: uv run scripts/release.py --check]
- `semkit docs --out <dir>` reports success. [check: uv run scripts/release.py --check]

## Out of scope

- Step 14 of Update mode: the gate from rb-cli-core (adopt_core).
- The release and the message to cli-generator: the Architect does them after acceptance.
