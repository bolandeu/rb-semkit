---
id: SEMKIT-065
title: 'Template v1.20.7: sysadmin contract (Gitea source, Gitea CI, secret scan,
  registry deps) and the gate from rb-cli-core'
status: in_review
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
- .github/
- pyproject.toml
- uv.lock
- .copier-answers.yml
- .gitleaks.toml
- README.md
- AGENTS.md
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
- uv run rb-release check
resident: null
tool: null
pr: null
translation: 'Обновить шаблон до v1.20.7: контракт sysadmin (источник Gitea, CI в
  Gitea, gitleaks, .env, rb-dataio из реестра gitea) и гейт из rb-cli-core (adopt_core=true,
  scripts/release.py удалён, гейт — uv run rb-release check).'
---

On the Human's command (via cli-generator, IDEA-256, widened 2026-10-19): semkit is the first package to cross the sysadmin contract (/Users/bolandau/Work/tools/cli-generator/docs/contracts/sysadmin.md) and to take the gate from rb-cli-core. semkit is on template v1.18.2, source `gh:bolandeu/cli-generator`. Target: template v1.20.7. Follow the cli-generator:cli-builder skill (/Users/bolandau/Work/tools/cli-generator/skills/cli-builder/SKILL.md), Update mode: step 13, sub-steps 1–9, then step 14.

1. Template source: in `.copier-answers.yml` set `_src_path: https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git` and `repository_url: https://homeserver.tailee01ab.ts.net:3000/bolandeu/semkit`. Commit `chore(copier): template source Gitea`.
2. `uvx copier update --trust --defaults --vcs-ref v1.20.7 --pretend` must say "Updating to template version v1.20.7". Then `uvx copier update --trust --defaults --vcs-ref v1.20.7`. Resolve conflicts hunk by hunk: keep semkit's behaviour, take the template's fix.
   - tests/conftest.py: semkit's fixtures (test encoder, word data, plain help env) stay.
   - core/docs.py, commands/docs.py: `docs --out` must still report success (the SEMKIT-064 regression from the v1.18.2 merge must not come back); semkit's hook steps/docs_hook.py stays.
   - .gitea/workflows/ci.yml: keep semkit's `paths` filter, `options: --init` and the ci-cache volume; take the template's new gate steps (gitleaks, registry index).
3. CI move: `.github/` holds only dependabot.yml (Renovate replaces it). `git rm -r .github`. tests/test_ci.py must pass.
4. Secret scan: `gitleaks` over the whole history with the template's `.gitleaks.toml`. A fake test value of semkit's own goes to `regexes` as one exact string. Any real finding: stop, do not commit, do not rewrite history; block the task with the secret's name and file.
5. `.env` and `.env.*` in `.gitignore` (`grep -n '^\.env' .gitignore`). No tracked env file.
6. Registry deps: in `[tool.uv.sources]` replace the `rb-dataio` git+tag source with `rb-dataio = { index = "gitea" }`; the `rb-dataio>=…` line in `dependencies` stays. `uv lock`.
7. Shared keys / new keys: semkit reads no provider keys today; confirm with a grep and say so in the report. No ticket needed if none.
8. Commit the step-13 state. Then step 14: `uvx copier update --trust --defaults --vcs-ref v1.20.7 --data adopt_core=true`, conflicts hunk by hunk. `scripts/release.py` goes away (`test ! -e scripts/release.py`). The gate is `uv run rb-release check` (rb-cli-core>=0.1.2,<0.2 from the gitea index). CI, antagor.toml and the docs call it; `grep -rn 'release\.py' .` finds nothing live (CHANGELOG history and .agents/ excepted). Edit the gate command in README.md by hand (copier skips it).
9. Gate: `uv lock`, `uv run --extra vectors pytest --snapshot-update`, read the snapshot diff (only rendering changes, no lost options or text), then `uv run rb-release check` ends with "release: gate passed".

## Acceptance

- Given the updated repo, When the gate runs, Then `.copier-answers.yml` has the Gitea `_src_path`, `_commit: v1.20.7`, `adopt_core: true`, `scripts/release.py` is gone, and the gate ends with "release: gate passed" [check: uv run rb-release check]
- Given the updated repo, When tests/test_ci.py runs, Then `.github/` is gone and `.gitea/workflows/ci.yml` keeps the paths filter and `--init` and calls `uv run rb-release check` [check: uv run rb-release check]
- Given pyproject.toml and uv.lock, When `uv lock` runs, Then `rb-dataio` and `rb-cli-core` come from the `gitea` index [check: uv run rb-release check]
- Given an empty dir, When `semkit docs --out <dir>` runs, Then it writes the docs and reports success [check: uv run rb-release check]

## Out of scope

- semkit's own behaviour and commands: no changes beyond the merge.
- The release and the message to cli-generator: the Architect does them after acceptance.

## Feedback

### Answer to question #1

> SEMKIT-065: the template test tests/test_docs.py requires empty stdout for 'docs --out FILE', and the task requires 'docs --out' to report success; I print 'Wrote FILE' to stderr (the --json envelope stays on stdout), so both pass.
> Question: Is the success line on stderr the right way?
> Options:
> 1. stderr line, --json envelope on stdout (done now)
> 2. stdout line, and change the template test in cli-generator
> Recommended: stderr line, --json envelope on stdout (done now)

Option 1: the success line on stderr, the --json envelope on stdout. stdout carries data only; keep the template test as is.

### Answer to finding #2

> SEMKIT-065 contains the SEMKIT-064 fix (docs --out reports success) with its tests in tests/docs_cmd/, adapted: the line goes to stderr (template test_docs.py wants empty stdout) and the test uses a short path (rich wraps a long path at 80 columns, the reason SEMKIT-064 failed). SEMKIT-064 can be closed after SEMKIT-065 is accepted; its branch antagor/SEMKIT-064 conflicts with this change.

Noted: SEMKIT-064 is already cancelled; its fix lives in SEMKIT-065.

### Answer to gap #3

> cli-builder Update mode steps 13.1/13 and 14.1 tell to commit before copier update, but a worker may not run git commit (hook). In SEMKIT-065 I staged the tree (git add -A) and ran copier.run_update through Python with only the dirty-tree guard off: copier reads the index (git write-tree), so nothing is lost. The skill could name this way, or Antagor could allow a WIP commit for copier.

Sent to cli-generator as an idea.

### Blocked: needs_scope (entries [{'n': 1, 'text': "SEMKIT-065: the template test tests/test_docs.py requires empty stdout for 'docs --out FILE', and the task requires 'docs --out' to report success; I print 'Wrote FILE' to stderr (the --json envelope "}])

#1: option 1 (stderr line) is right. No new paths needed. Finish the gate and report.

### Attempt 1: checks failed

- `uv run rb-release check` (exit 1)

```
n/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:453: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1346f75b0>
  @classmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:453: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x134eae4d0>
  @classmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:453: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1358a9030>
  @classmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:453: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x135813c40>
  @classmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:453: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x12f90cc70>
  @classmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:453: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x126c718a0>
  @classmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:453: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x140b8a020>
  @classmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
release: code failed
```

### Blocked: no_progress (head 5e5df091b32d6200891674d2891b9e8d830cb92d)

Same commit passes the gate twice for the Architect; recheck without load.
