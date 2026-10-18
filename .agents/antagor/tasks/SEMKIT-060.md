---
id: SEMKIT-060
title: 'CI on the homeserver runner: .gitea/workflows/ci.yml runs the release gate;
  ruff format fix in tests/conftest.py'
status: queue
attempts: 0
blocked: true
blocked_reason: aborted
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: architect
worker: claude-code
type: chore
owns_paths:
- .gitea/workflows/ci.yml
- tests/conftest.py
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
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'CI на раннере homeserver: .gitea/workflows/ci.yml гоняет release.py
  --check; поправить форматирование tests/conftest.py (гейт падает на main).'
---

The homeserver Gitea runner (label docker, shared cache volume ci-cache) is ready for semkit (sysadmin, the Human's yes 2026-10-18). Gitea repos are public in the tailnet, so rb-dataio installs with no token.

1. Add .gitea/workflows/ci.yml exactly as the draft below (GitHub ignores .gitea; no .github/workflows).
2. Run `uv run ruff format tests/conftest.py`: line ~66 (monkeypatch.setattr ... open_thesaurus) is not formatted, and the gate fails on main at ruff format --check.
3. Run `uv run scripts/release.py --check` locally: green.

Draft:

```
name: ci
on: [push, pull_request, workflow_dispatch]
jobs:
  gate:
    runs-on: docker
    container:
      image: node:22-bookworm
      volumes:
        - ci-cache:/cache
    env:
      UV_CACHE_DIR: /cache/uv
      XDG_CACHE_HOME: /cache/xdg
      UV_PYTHON_INSTALL_DIR: /cache/python
      UV_LINK_MODE: copy
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # release.py needs tags
      - name: uv
        run: |
          mkdir -p /cache/bin
          [ -x /cache/bin/uv ] || curl -LsSf --max-time 300 https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/cache/bin UV_NO_MODIFY_PATH=1 sh
          echo /cache/bin >> "$GITHUB_PATH"
      - run: uv run scripts/release.py --check
```

## Out of scope

- GitHub workflows; the first CI run and its tuning (3.5 GB memory per job, model downloads): the Architect watches the run after the push.

## Read first

- `scripts/release.py` — the gate the CI runs
