---
id: SEMKIT-072
title: Standard section names in comments are the Standard's real headings
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
- src/rb_semkit/core/deps.py
- src/rb_semkit/core/errors.py
- src/rb_semkit/commands/auth.py
- pyproject.toml
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
translation: 'Исправить названия разделов Standard в комментариях после SEMKIT-071:
  Tools catalog/Dependencies/Install(DEPENDENCY_TOO_OLD) → Technology, Auth → Health,
  Tests — убрать.'
---

SEMKIT-071 replaced references with Standard section names, but some names do not exist. The Standard's sections are: Technology, Commands, Output, Errors, Health, Credentials, Install, Docs, CI, Release, Optional parts (https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator/src/branch/main/skills/cli-builder/reference/standard.md). Comments and docstrings only.

1. "the Standard, Tools catalog" (pyproject.toml, the external-dependencies comment; src/rb_semkit/core/deps.py, the ExternalDependency docstring) -> "the Standard, Technology".
2. "the Standard, Tests" (pyproject.toml, the help-snapshots comment) -> drop the reference.
3. "the Standard, Auth" (src/rb_semkit/commands/auth.py) -> "the Standard, Health".
4. "the Standard, Dependencies" (src/rb_semkit/core/deps.py, the module docstring) -> "the Standard, Technology".
5. "the Standard, Install" where it is about the DEPENDENCY_TOO_OLD install action (src/rb_semkit/core/deps.py, src/rb_semkit/core/errors.py) -> "the Standard, Technology".
6. `git grep -n "the Standard, " -- src tests scripts pyproject.toml` names only the sections listed above.

## Acceptance

- Given src, tests, scripts and pyproject.toml, When the grep of step 6 runs, Then every name it finds is one of the Standard's sections, and the gate ends with 'release: gate passed' [check: sh -c 'uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check']

## Out of scope

- Any text outside these references.
