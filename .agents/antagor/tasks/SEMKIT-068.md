---
id: SEMKIT-068
title: 'Template update to the newest tag (v1.23.1+): the gate through uvx from cli-generator,
  rb-cli-core gone'
status: publish
attempts: 1
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
- 'sh -c ''uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed
  -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check'''
resident: null
tool: null
pr: null
translation: 'Обновить шаблон до v1.23.0: гейт через uvx из cli-generator (тег шаблона),
  убрать rb-cli-core и uv run rb-release; гейт проверяет обязательные правила Standard
  — красные шаги чинить в semkit, спорное правило — вопросом.'
---

From cli-generator (the Human said to send it), 2026-10-20: move semkit from template v1.20.7 (adopt_core=true, the gate from the rb-cli-core library) to the newest cli-generator template tag (v1.23.1 or newer: the first tag with CG-045, where the gate counts --json from the root help). In it the gate lives in cli-generator/gate and runs through uvx at the template tag:

`uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@<the tag in .copier-answers.yml _commit>#subdirectory=gate" rb-release check`

The `adopt_core` answer and the dev dependency `rb-cli-core` are gone. The gate also checks the Standard's mandatory rules (commands, json, errors, health, docs, ci); a failure names a section of skills/cli-builder/reference/standard.md in cli-generator. Do NOT follow the Update mode of the cli-builder skill: it still talks about the old release script and adopt_core. Follow these steps.

1. Clean tree. Commit before copier is not allowed for a worker: stage the tree (`git add -A`) and run copier with the dirty-tree guard off, as in SEMKIT-065. Then `uvx copier update --trust --defaults --vcs-ref <that tag>` (find it: `git ls-remote --tags https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git`). Resolve conflicts hunk by hunk: keep semkit's behaviour, take the template's fix.
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

- Given the updated repo, When the gate runs through uvx at the template tag, Then it ends with "release: gate passed" [check: sh -c 'uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check']
- Given pyproject.toml, uv.lock, CI, AGENTS.md, README.md and .agents/antagor/antagor.toml, When searched for rb-cli-core and `uv run rb-release`, Then nothing is found, and the new tag is `_commit` in .copier-answers.yml without `adopt_core` [check: sh -c 'uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check']

## Out of scope

- The timed tests (marker speed): they stay out of the default run.
- The release and the message to cli-generator: the Architect does them after acceptance.

## Feedback

### Answer to question #1

> The v1.23.0 gate fails 'standard: json' (Standard, section Output) and 'standard: errors' (section Errors) on the 145 pipeline steps under 'semkit read': the gate lists them as commands, but a step is a part of one pipeline command, and --json is a global option before the steps ('semkit --json read IN STEP'), so a step's --help has no --json and 'semkit read STEP --json --x' reports 'No such option: --json' without the envelope. Every other gate step passes (osv audit checked by hand: no issues).
> Question: How do we make the gate pass for the pipeline steps?
> Options:
> 1. cli-generator changes the gate: rules json and errors skip the subcommands of a chained group (Click chain=True), or probe the group itself ('semkit read --json')
> 2. semkit adds --json to every step's options (a copy of the global flag) and turns a usage error after any --json into the error envelope
> 3. the Standard gets a declared exception (a pyproject key) for the pipeline steps of semkit
> Recommended: cli-generator changes the gate: rules json and errors skip the subcommands of a chained group (Click chain=True), or probe the group itself ('semkit read --json')

Option 1: cli-generator changes the gate (IDEA-297): --json from the root's help counts; errors probe 'semkit --json read STEP --unknown'. semkit changes nothing for these rules. When the task returns, update to the new template tag (the Architect names it).

### Blocked: idea_wait (idea IDEA-297, idea_state IDEA-297 is new, was needs_scope, note needs the gate fix and template tag from cli-generator)

CG-045 is released: template tag v1.23.1. Update with --vcs-ref v1.23.1; the gate now counts the root's --json and probes 'semkit --json read STEP --unknown', so the pipeline steps need no change.

### Attempt 1: file docstring

- update the docstring of src/rb_semkit/output/__init__.py: +RootGroup
