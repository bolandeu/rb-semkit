---
id: SEMKIT-068
title: 'Template v1.23.0: the gate through uvx from cli-generator, rb-cli-core gone'
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
- .agents/antagor/antagor.toml
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
- uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@v1.23.0#subdirectory=gate"
  rb-release check
resident: null
tool: null
pr: null
translation: 'Обновить шаблон до v1.23.0: гейт через uvx из cli-generator (тег шаблона),
  убрать rb-cli-core и uv run rb-release; гейт проверяет обязательные правила Standard
  — красные шаги чинить в semkit, спорное правило — вопросом.'
---

From cli-generator (the Human said to send it), 2026-10-20: move semkit from template v1.20.7 (adopt_core=true, the gate from the rb-cli-core library) to template v1.23.0. In v1.23.0 the gate lives in cli-generator/gate and runs through uvx at the template tag:

`uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@v1.23.0#subdirectory=gate" rb-release check`

The `adopt_core` answer and the dev dependency `rb-cli-core` are gone. The gate also checks the Standard's mandatory rules (commands, json, errors, health, docs, ci); a failure names a section of skills/cli-builder/reference/standard.md in cli-generator. Do NOT follow the Update mode of the cli-builder skill: it still talks about the old release script and adopt_core. Follow these steps.

1. Clean tree. Commit before copier is not allowed for a worker: stage the tree (`git add -A`) and run copier with the dirty-tree guard off, as in SEMKIT-065. Then `uvx copier update --trust --defaults --vcs-ref v1.23.0`. Resolve conflicts hunk by hunk: keep semkit's behaviour, take the template's fix.
   - Take the template's .gitea/workflows/ci.yml, but keep semkit's `paths` filter, `options: --init` and the ci-cache volume.
   - Take the template's gate command in .agents/antagor/antagor.toml (`checks`) and in AGENTS.md. Keep the other keys of antagor.toml as main has them.
   - tests/conftest.py: semkit's fixtures stay. core/docs.py, commands/docs.py: `docs --out` still reports success on stderr; steps/docs_hook.py stays.
   - pyproject.toml: keep `-m 'not speed'` in pytest addopts (SEMKIT-067) and `gate_extras = ["vectors"]`.
2. Remove `rb-cli-core` from the dev group and from `[tool.uv.sources]`, and every place that runs `rb-release` through `uv run` (README.md, AGENTS.md, CODING_STANDARDS.md, CI, tests). `adopt_core` leaves .copier-answers.yml. Then `uv lock`.
3. `uv run --extra vectors pytest --snapshot-update`; read the snapshot diff: only rendering changes, no lost options or text.
4. Run the gate command above until it ends with `release: gate passed`. Fix every red step in semkit code. If a Standard rule looks wrong for semkit, do not work around it: add an inbox question naming the rule, the section of standard.md and why, and go on with the rest.

## Read first

- `.copier-answers.yml`
- `.agents/antagor/antagor.toml`

## Acceptance

- Given the updated repo, When the gate runs through uvx at v1.23.0, Then it ends with "release: gate passed" [check: uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@v1.23.0#subdirectory=gate" rb-release check]
- Given pyproject.toml, uv.lock, CI, AGENTS.md, README.md and .agents/antagor/antagor.toml, When searched for rb-cli-core and `uv run rb-release`, Then nothing is found, and `_commit: v1.23.0` is in .copier-answers.yml without `adopt_core` [check: uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@v1.23.0#subdirectory=gate" rb-release check]

## Out of scope

- The timed tests (marker speed): they stay out of the default run.
- The release and the message to cli-generator: the Architect does them after acceptance.
