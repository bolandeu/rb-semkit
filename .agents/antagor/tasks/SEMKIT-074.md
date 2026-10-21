---
id: SEMKIT-074
title: 'Template v1.26.3: package docs keep no retelling of Antagor''s process'
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
docs:
- AGENTS.md
- CODING_STANDARDS.md
- README.md
tools: []
worker_args: null
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
translation: Обновить шаблон до v1.26.3 и убрать из AGENTS.md, CODING_STANDARDS.md
  и README пересказ процесса Antagor (тикеты, кто выпускает, как собирается CHANGELOG,
  границы hand fix). AGENTS.md — по скелету шаблона; в «Architect only» — одно правило
  о выпусках Архитектором. Смысл правил пакета не меняется.
---

cli-generator (2026-10-21, a request of the Human): package docs keep no retelling of Antagor's process. Antagor's rules come from the installed Antagor (its skills and the worker's brief); a retelling goes stale, and AGENTS.md goes into every worker's brief, where it conflicts with the current rules. Template v1.26.3 does the same, so semkit moves from template v1.25.8 to v1.26.3 and then cleans what the template does not own.

1. Stage the tree (`git add -A`) and run copier with the dirty-tree guard off, as before (a worker may not commit). Then `uvx copier update --trust --defaults --vcs-ref v1.26.3`. Resolve conflicts hunk by hunk: keep semkit's behaviour, take the template's text. Keep what SEMKIT-073 kept: semkit's CI trigger (push on main and antagor/publish-*, no paths filter), `options: --init` and the ci-cache volume; semkit's own `docs` command; `-m 'not speed'` in pytest addopts and `gate_extras = ["vectors"]`.
2. AGENTS.md: the template's skeleton (template/AGENTS.md.jinja at v1.26.3), in English: the pointer line with `antagor board`; CONTEXT.md, docs/adr/, CODING_STANDARDS.md, ".agents/antagor/ (tasks and epics)", the skill antagor-method; the Standard link; the gate command at v1.26.3. Drop the hand-fix line. Under "## Architect only" put exactly this one rule of the Human (its meaning stays):
   "Releases (until the Human cancels it): the Architect accepts tasks and runs `antagor publish` without asking, after its own check (the gate and a read of the changes since the last tag), and reports the release after. Then it updates the global install: `uv tool install --force "rb-semkit[vectors] @ git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/semkit.git@<tag>"`."
3. CODING_STANDARDS.md: drop the hand-fix rule (Antagor's own) and, in «Версии и релизы», who runs a release and how publish builds CHANGELOG.md. Keep the package's facts: a release is a tag; never edit CHANGELOG.md, never push or tag by hand, never force-push or `commit --amend`. Where the text names Antagor's unit of work, say «задача»/«эпик», not «тикет»/«сценарий».
4. README.md, «Release» and the install text: drop "Work goes through Antagor tickets", who runs a release, `antagor publish --bump` and how it builds CHANGELOG.md and deploys. Keep: the version is the git tag (`vX.Y.Z`), `pyproject.toml` has no `version =`, nobody tags or pushes by hand, install only a release tag, never a branch. The gate command in README at the template tag.
5. No rule of the package changes its meaning; only Antagor's process leaves the docs.
6. `uv lock` if the template asks; `uv run --extra vectors pytest --snapshot-update`, read the diff: only rendering changes. The gate (the command below) ends with 'release: gate passed'.

## Acceptance

- Given the updated repo, When the gate runs at the template tag, Then .copier-answers.yml has _commit: v1.26.3, AGENTS.md follows the template skeleton with one rule under '## Architect only', AGENTS.md, CODING_STANDARDS.md and README.md name no ticket, scenario, hand-fix boundary or the way publish builds the changelog, and the gate ends with 'release: gate passed' [check: sh -c 'uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check']

## Basis

Follow SEMKIT-073 (the last template update): the same steps and the same things to keep.

## Read first

- `.copier-answers.yml`
- `AGENTS.md`
- `CODING_STANDARDS.md`

## Out of scope

- requires-python, semkit's own commands and behaviour.
- .agents/: the Architect's (its gate line moves to v1.26.3 on main).
