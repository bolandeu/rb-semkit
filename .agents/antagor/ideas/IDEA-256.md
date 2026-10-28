---
id: IDEA-256
title: 'Template v1.20.3: Gitea source, Gitea CI, secret scan, registry deps (first
  package for the Renovate check)'
created: '2026-10-19T07:01:21+00:00'
source_project: cli-generator
source_path: /Users/bolandau/Work/tools/cli-generator
status: taken
for_path: /Users/bolandau/Work/tools/semkit
triage:
  serves: []
  risks: []
  why: 'Human''s command via cli-generator: semkit is the first package on the sysadmin
    contract template (Gitea source, CI, gitleaks, registry deps)'
  score: 8.0
  route: task
  at: '2026-10-19T13:34:50+00:00'
task: SEMKIT-065
taken_project: semkit
---

From cli-generator, on the Human's command (2026-10-19): semkit is the first package to move to template v1.20.3. Follow cli-builder SKILL.md, Update mode, step 13 (switch _src_path to https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git, copier update --trust --defaults, keep your .gitea CI or take the template one, gitleaks, .env, registry deps, shared keys via legacy_env, gate). Release through antagor publish. When the tag is out, tell cli-generator: sysadmin then runs Renovate to check that a copier-update PR appears for the next template tag. Contract: /Users/bolandau/Work/tools/cli-generator/docs/contracts/sysadmin.md.
