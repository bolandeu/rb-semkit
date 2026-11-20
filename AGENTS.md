# AGENTS.md

- The package Standard: https://github.com/bolandeu/python-package-gate/blob/main/skills/cli-builder/reference/standard.md (sections by name, for example «Install»).
- The gate before a commit: `gate check`, on this machine (Standard, CI). It is the only gate: no workflow runs it.

## Architect only

A worker does not need this section: Antagor cuts it from the worker's brief.

- Releases (until the Human cancels it): the Architect accepts tasks and runs `antagor publish` without asking, after its own check (the gate and a read of the changes since the last tag), and reports the release after. Then it updates the global install: `uv tool install --force "rb-semkit[vectors] @ git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/semkit.git@<tag>"`.
