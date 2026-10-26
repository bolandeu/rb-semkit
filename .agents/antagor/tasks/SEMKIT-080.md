---
id: SEMKIT-080
title: 'Template v1.27.3: update from v1.26.3'
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
- pyproject.toml
- uv.lock
- .copier-answers.yml
- .gitleaks.toml
- README.md
- CHANGELOG.md
- .gitignore
- .python-version
test_paths: []
docs:
- README.md
tools: []
worker_args: null
class: standard
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
translation: 'Обновить шаблон до v1.27.3 (с v1.26.3): Renovate PR #1 с маркерами конфликтов
  закрыт без слияния. Файлы Архитектора (.agents/, AGENTS.md, CODING_STANDARDS.md)
  уже на main. Конфликты — вручную, по кускам; docstring модулей — semkit.'
---

cli-generator template v1.27.3 (the Human asked, through the cli-generator agent): semkit moves from template v1.26.3 to v1.27.3. Renovate's PR #1 committed conflict markers and is closed without merging; do the update yourself. Follow SEMKIT-074 (the last template update) and the skill cli-generator:cli-builder, `reference/existing-package.md`, «A package from the template that wants updates».

1. Run copier first, before you change or stage anything (the worktree is clean; copier refuses a dirty tree):
   `uvx copier update --trust --defaults --conflict inline --vcs-ref v1.27.3 --data antagor_prefix=SEMKIT`
   Never drop `--trust`. The answers file says `SMK`, `.agents/antagor/antagor.toml` says `SEMKIT`: pass `SEMKIT` so the answer matches. If copier still refuses on a dirty tree, `git add -A` and run the staged script in its place, with the same arguments: `uvx --from copier python /Users/bolandau/.claude/skills/cli-generator/skills/cli-builder/scripts/copier_update_staged.py --trust --defaults --conflict inline --vcs-ref v1.27.3 --data antagor_prefix=SEMKIT`.
2. A dry run on main gave exit 0, no file deleted, inline conflicts (`<<<<<<< before updating`) in 21 files: tests/conftest.py, tests/test_scripts.py and src/rb_semkit/{__init__, _distribution, cli, commands/{__init__, auth, config, describe, doctor, init, run, skill}, core/{errors, models, services, version}, output/{__init__, human, json}}.py. Run `git status | grep '^ D'` after copier: restore every package file it deleted (`git checkout HEAD -- <file>`).
3. Resolve every conflict hunk by hunk. Keep semkit's commands, models, errors and settings; take the template's structure. Never one side wholesale (no `git checkout --theirs/--ours`, no copying the template file over). Most code conflicts are the module docstring only: keep semkit's docstring (Antagor refuses a module without one; `scripts/check_command_docstrings.py` checks the command docstrings). No `<<<<<<<`, `=======`, `>>>>>>>` may stay anywhere (`grep -rn '^<<<<<<<' .`). Delete every `.rej` file.
4. Keep:
   - the xdist workaround in tests/conftest.py (`pytest_configure`, SEMKIT-079): the gate's contract summary under xdist is not fixed in the template yet;
   - `-n auto ... -m 'not speed'` in pytest addopts and `gate_extras = ["vectors"]` in pyproject.toml; semkit's own `docs` command; semkit's CI trigger, `options: --init` and the ci-cache volume in `.gitea/workflows/ci.yml` (the dry run touched only the gate line there);
   - tests/test_scripts.py: take the template's check of `.agents/antagor/antagor.toml` (the gate left `checks`; `heavy = ["rb-release check"]` holds it), keep what in the file is semkit's own. A changed test goes into your report with its reason.
5. `.agents/antagor/antagor.toml`, `AGENTS.md` and `CODING_STANDARDS.md` are the Architect's and are already at the template side on main (commit bee7695). If copier changed or conflicted them, restore main's text: `git checkout HEAD -- .agents AGENTS.md CODING_STANDARDS.md`. README.md: the gate command at v1.27.3 by hand (copier never touches README).
6. `uv lock`; `uv run --extra vectors pytest --snapshot-update`; read the whole snapshot diff: only rendering changes, no Mac path (`/Users/...`). Then run the suite once with `GITHUB_ACTIONS=true FORCE_COLOR=1 PY_COLORS=1` set.
7. The gate, from the package root, until the last line is `release: gate passed` (it takes up to ~17 min; run it detached: `scripts/run_detached.sh gate <command>`, then `scripts/runs_status.sh gate`):
   `uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@v1.27.3#subdirectory=gate" rb-release check --keep-going`
   The gate line in `.gitea/workflows/ci.yml` must say v1.27.3 (copier writes it). A new template rule that semkit's code fails: fix the code, not the gate; if a rule looks wrong for semkit, ask in the inbox, do not work around it.
8. The report: `_commit` from `.copier-answers.yml`, the gate result, every test changed or removed (with the reason), and anything in this brief that was wrong or missing.

## Acceptance

- Given the updated repo, When the gate runs at the template tag, Then .copier-answers.yml has `_commit: v1.27.3`, no conflict marker or `.rej` file is left, CI runs the gate at v1.27.3, and the gate ends with 'release: gate passed' [check: sh -c 'uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git@$(sed -n "s/^_commit: //p" .copier-answers.yml)#subdirectory=gate" rb-release check']

## Basis

Follow SEMKIT-074 (the last template update): the same steps and the same things to keep.

## Read first

- `.copier-answers.yml`
- `tests/conftest.py`
- `.agents/antagor/antagor.toml` — read only: the Architect's, already at the template side

## Out of scope

- .agents/, AGENTS.md, CODING_STANDARDS.md: the Architect's, on main.
- requires-python, semkit's own commands and behaviour.
- The release: the Architect runs `antagor publish`.
