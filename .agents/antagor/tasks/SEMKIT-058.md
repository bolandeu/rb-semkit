---
id: SEMKIT-058
title: 'semkit docs: examples without the command path, inherited options only (InSpectra
  rules of the template)'
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
type: bugfix
owns_paths:
- src/rb_semkit/core/docs.py
- src/rb_semkit/steps/docs_hook.py
- docs/help-standard.md
- tests/docs_cmd/
- tests/snapshots/
- src/rb_semkit/commands/docs.py
test_paths:
- tests/docs_cmd/
- tests/steps/test_examples.py
- tests/steps/test_help_standard.py
docs:
- docs/help-standard.md
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
resident: null
tool: null
pr: null
translation: 'semkit docs по правилам InSpectra из шаблона: в примерах только то,
  что после пути команды; наследуются только опции (recursive у родителя), позиционные
  — никогда; вход read остаётся у read, у каждого шага первая строка «Input: semkit
  read IN|--text TEXT|- <step> …».'
---

InSpectra (checked by cli-generator on 0.0.164) always prefixes an example with '<program> <command path>', and OpenCLI cannot put a positional argument before a subcommand. The cli-generator template takes these rules (IDEA-240); semkit's docs output follows them now.

1. Examples (core/docs.py): an OpenCLI example holds only what follows '<program> <command path>': «--top 5  # -> <result>». The docstring Example line keeps the full command (the example runner runs it); docs strips the prefix, and refuses (a failing check of the standard, and semkit docs exits 1 naming the command and the example) an example that does not start with it.
2. Inheritance (core/docs.py): a hook may inherit options only, never positional arguments; inherited options are marked recursive on the parent, not copied into each subcommand.
3. semkit's hook (steps/docs_hook.py): the input of read stays on read only (IN, and --text, --column, --whole as read's options, not recursive, since read takes them before the first step). A read step's example in the docstring is a full command «semkit read <input> <step> …»; the hook strips «semkit read <input> <step>» (the input part is IN, '-', or read's options with their values) so the examples field holds the step's options only. Each read step's description begins with one line «Input: semkit read IN|--text TEXT|- <step> [options] [write OUT]», so the full form is on every step page; read's own description holds full examples with input.
4. docs/help-standard.md says both rules (examples without the command path; options only inherited, recursive on the parent, no positional inheritance), neutral to the project.

## Acceptance

- Given the docstring example «semkit read customs.csv synonym-candidates --all --source ruwordnet», When semkit docs runs, Then the examples field of synonym-candidates holds «--all --source ruwordnet» [check: tests/docs_cmd/]
- Given an example with --text input «semkit read --text 'растаможка авто' synonym-candidates --all», When semkit docs runs, Then the examples field holds «--all» [check: tests/docs_cmd/]
- Given an example of a command that does not start with its command path, When semkit docs runs, Then it exits 1 naming the command and the example [check: tests/docs_cmd/]
- Given any read step, When semkit docs runs, Then it carries no IN argument and no copies of read's options, and its description begins with the Input line [check: tests/docs_cmd/]
- Given core/docs.py with a hook that adds an option to subcommands, When docs runs on a small Typer app, Then the option is recursive on the parent and is not copied into the subcommands [check: tests/docs_cmd/]

## How to test

Integration through the semkit CLI runner and a unit test of core/docs.py on a small Typer app with no semkit code.

## Basis

core/docs.py and steps/docs_hook.py of SEMKIT-054; the decision of cli-generator on IDEA-240.

## Out of scope

- The step docstrings themselves (SEMKIT-055 keeps full commands in Example lines); a new --in option of read; rendering HTML.

## Feedback

### Attempt 1: checks failed

- `uv run --extra vectors pytest` (exit 1)

```
9-72, 79, 82-88, 97, 100, 103
src/rb_semkit/core/version.py                    46      7    85%   60-61, 65, 72-73, 93-94
src/rb_semkit/core/word_vectors/navec.py         69      1    99%   91
src/rb_semkit/core/wordlists/folders.py          36      1    97%   51
src/rb_semkit/output/__init__.py                122      9    93%   99, 143, 187, 211-214, 257-258
src/rb_semkit/output/human.py                    27      1    96%   31
src/rb_semkit/pipeline/commands.py              192      4    98%   135-136, 169, 185
src/rb_semkit/pipeline/state.py                 132      4    97%   56, 103, 138, 154
src/rb_semkit/pipeline/tables.py                147      8    95%   57, 72, 122, 137, 139, 141, 172, 213
src/rb_semkit/steps/__init__.py                 178      3    98%   183, 244, 266
src/rb_semkit/steps/docs_hook.py                 35      1    97%   43
src/rb_semkit/steps/markers.py                   31      2    94%   36, 42
src/rb_semkit/steps/serp.py                      25      5    80%   23, 28-34
src/rb_semkit/steps/text.py                      70      1    99%   88
---------------------------------------------------------------------------
TOTAL                                          7031    201    97%

128 files skipped due to complete coverage.
Required test coverage of 90.0% reached. Total coverage: 97.14%
--------------------------- snapshot report summary ----------------------------
1 snapshot failed. 318 snapshots passed.
=========================== short test summary info ============================
FAILED tests/test_describe.py::test_command_snapshot[docs] - assert [+ receiv...
=========== 1 failed, 5842 passed, 26 warnings in 204.31s (0:03:24) ============
/Users/bolandau/Work/tools/semkit.worktrees/SEMKIT-058/.venv/lib/python3.14/site-packages/_pytest/unraisableexception.py:33: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x138a65120>
  gc.collect()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
```
