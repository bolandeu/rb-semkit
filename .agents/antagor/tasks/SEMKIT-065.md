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

From cli-generator, on the Human's command (2026-10-19): semkit is the first package to move to template v1.20.3. Follow cli-builder SKILL.md, Update mode, step 13 (switch _src_path to https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git, copier update --trust --defaults, keep your .gitea CI or take the template one, gitleaks, .env, registry deps, shared keys via legacy_env, gate). Release through antagor publish. When the tag is out, tell cli-generator: sysadmin then runs Renovate to check that a copier-update PR appears for the next template tag. Contract: /Users/bolandau/Work/tools/cli-generator/docs/contracts/sysadmin.md.

(from IDEA-256)
