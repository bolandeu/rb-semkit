---
id: SEMKIT-059
title: 'write --columns and --rename: choose, order and rename the output columns
  (dataio v0.1.26)'
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
type: feature
owns_paths:
- pyproject.toml
- uv.lock
- src/rb_semkit/pipeline/
- src/rb_semkit/commands/read.py
- src/rb_semkit/data/SKILL.md
- README.md
- tests/pipeline/
- tests/snapshots/
- .gitea/workflows/ci.yml
- .python-version
- .gitignore
- CHANGELOG.md
test_paths:
- tests/pipeline/
- tests/docs_cmd/test_core_docs.py
docs:
- README.md
- src/rb_semkit/data/SKILL.md
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
- uv run --extra vectors pytest
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'write --columns/--rename: выбрать, упорядочить и переименовать колонки
  вывода через dataio v0.1.26; пин dataio поднять до v0.1.26.'
---

dataio v0.1.26 (IDEA-241) writes a chosen set of columns, in a chosen order, under chosen names: write() takes columns (a list of source names, kept in this order) and rename (a mapping old -> new), the selection first, then the rename; an unknown name, a rename of a missing or dropped column, or a clash is INVALID_ARGUMENTS (exit 2) listing the columns there are; a swap a<->b is allowed. The output field names of semkit are the column names its steps make, so agents and Windmill want to set them at write time.

1. The dataio pin moves to v0.1.26 (the git tag of [tool.uv.sources] and the lower bound rb-dataio>=0.1.26,<0.2); uv.lock refreshed.
2. write OUT takes --columns NAME,NAME (comma list, repeatable) and --rename OLD=NEW (repeatable, split on the first '='), passed to dataio as they are; the errors of dataio come out as semkit errors with their exit 2 and message.
3. The same choice for the output without write (the terminal table, or JSONL to a pipe): not in this task; write - takes the options.
4. Help of write with an example, the agent guide and README: … nearest --to Q write - --columns phrase,similarity --rename similarity=сходство.
5. The release gate is red on main at `ty check`: src/rb_semkit/pipeline/tables.py:143 and :156 pass str | None to rb_dataio.read. Fix them here (the same file), so `uv run scripts/release.py --check` is green; CI on the homeserver runs that gate.
6. .gitea/workflows/ci.yml runs on code changes only: `push` and `pull_request` get `paths: [src/**, tests/**, scripts/**, pyproject.toml, uv.lock, .gitea/workflows/**]`; `workflow_dispatch` stays (a manual run). A commit with `[skip ci]` skips it (Gitea's own rule, nothing to add).
7. One Python for the Mac and CI: add `.python-version` with `3.14` (uv on the runner installs it into the shared cache). The ty errors of item 5 show on 3.13 (CI took the only cached Python) and not on 3.14: narrow `self.address` to str before rb_dataio.read anyway, the None case is a real gap.
8. CHANGELOG.md holds a stray hand-written `## Unreleased` block with a duplicate SEMKIT-057 line (below v0.1.48): delete that block. Do not add entries yourself: `antagor publish` writes the changelog.

## Acceptance

- Given a nearest report, When write - --columns phrase,similarity runs, Then each JSONL object has exactly the keys phrase and similarity in that order [check: tests/pipeline/]
- Given --rename similarity=сходство, When write out.csv runs, Then the header is phrase,сходство [check: tests/pipeline/]
- Given --columns nosuch, When write runs, Then it is refused with exit 2 listing the columns there are [check: tests/pipeline/]
- Given write without these options, When it runs, Then the output is as before [check: tests/pipeline/]

## How to test

Integration through the semkit CLI runner on small JSONL tables.

## Basis

pipeline/tables.py (the write step and its call of dataio.write); the dataio v0.1.26 API (columns, rename).

## Out of scope

- Column choice for the output without write; renaming inside the pipeline (a step).

## Read first

- `scripts/release.py` — the gate: ty check runs there

## Feedback

### Blocked: environment_broken (checks ['uv run --extra vectors pytest'])

### Attempt 0 (not counted): main moved and conflicts with the work

`main` changed since your work began, and merging it conflicts in:

- `CHANGELOG.md`

Merge it into your branch (`git merge main`), resolve each file keeping both behaviours, `git add` it and run the checks; do not commit: Antagor commits the merge with your work when the round ends (IDEA-201).
