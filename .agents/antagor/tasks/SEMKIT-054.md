---
id: SEMKIT-054
title: 'Help standard and semkit docs: a deterministic human document of every command
  and step for InSpectra'
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
- docs/help-standard.md
- src/rb_semkit/commands/docs.py
- src/rb_semkit/cli.py
- src/rb_semkit/core/docs.py
- src/rb_semkit/steps/docs_hook.py
- src/rb_semkit/steps/__init__.py
- src/rb_semkit/data/SKILL.md
- tests/docs_cmd/
- tests/steps/test_help_standard.py
- tests/snapshots/
- tests/test_help.py
test_paths:
- tests/docs_cmd/
- tests/steps/test_help_standard.py
- tests/test_describe.py
docs:
- docs/help-standard.md
- src/rb_semkit/data/SKILL.md
tools: []
worker_args: null
class: hard
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
translation: 'Стандарт справки шага + команда semkit docs: детерминированно собирает
  из кода OpenCLI-файл для InSpectra (команды наверху, описание без строк опций, примеры
  отдельным полем с коротким результатом, значения по умолчанию и допустимые, у каждого
  шага вход read). HTML не делает — его собирает общая обёртка для всех CLI.'
---

The help in a browser (InSpectra over an OpenCLI file) is hard to read: semkit describe nests the commands under command (InSpectra reads them at the root, so it shows nothing without a jq rewrite); a step page is one paragraph that repeats each option's explanation; the example sits at the end of the text, not in the OpenCLI examples field; defaults and allowed values are not shown, and every option shows as repeatable (<TOP...>); a step page and its composer do not show the input of read (IN, --text, '-' for JSONL), so the generated command is «semkit read synonym-candidates» with no input. describe is a cross-tool contract (core/opencli.py header), so it stays as it is; the human document is a new command. The cli-generator template takes this task's output as its reference (IDEA-240) and will copy the generic module verbatim, so the generic part carries no semkit names.

1. A written standard of the help, docs/help-standard.md: a draft that later moves to cli-generator (skills/cli-builder/reference/help-standard.md) as it is, so its wording is neutral to the project: it speaks of a command (a step of semkit is a command), never of semkit, read or steps. The document is built from the code with no hand step (deterministic: the same code gives the same document byte for byte). The standard fixes:
 - summary: the first sentence of the docstring, one line, what the command gives;
 - description: the paragraphs after it, without the option lines and without the example lines;
 - an option line «name: text» goes to that option only;
 - default, allowed values (Literal/enum) and whether an option repeats come from the signature, never from the text; arity maximum 1 for an option that does not repeat;
 - the exact text of defaults and allowed values (OpenCLI 0.1 has no fields for them): the last line of the option description, «Default: 10. Allowed: ruwordnet, navec, both.»; «Default: …» only when there is a default, «Allowed: …» only when the values are fixed, the values joined by «, » in the signature order, each part ending with «.», one space between them; a flag shows «Default: off.»;
 - examples: a docstring line «Example: <command>», optionally followed by a line «-> <result>» (ASCII arrow); one to three per command. In the OpenCLI examples field each is one string: «<command>  # -> <result>» (two spaces before #), or «<command>» alone when there is no result line.
2. A generic module src/rb_semkit/core/docs.py, next to core/opencli.py, with no semkit names: walks the Click tree, builds the root-level shape (opencli, info, commands, options, arguments, examples), splits each docstring by the standard, takes defaults, allowed values and arity from the signature. It takes an optional hook that adds inherited arguments and options to the subcommands of a command.
3. The hook of semkit in its own module src/rb_semkit/steps/docs_hook.py: each read step carries the arguments and options of read (IN, --text, --column, --whole), so the composer builds «semkit read IN step …».
4. A command semkit docs: writes the document; --out FILE writes it to a file, else stdout. Rendering the HTML is not the CLI's job: the Human renders the file with InSpectra (Mac only) by a shell wrapper shared by all the CLIs.
5. A test of the standard (tests/steps/test_help_standard.py): for every step, summary present and one line, at least one Example, every option explained, no option line left in the description, the defaults line in the exact format; the steps that do not meet it yet are listed in one allowlist in the test with a comment. Running every example and checking its «->» result is SEMKIT-055, not this task.

## Acceptance

- Given semkit docs --out d.json, When it is read as JSON, Then commands, options, arguments and examples are at the root and the read steps are under read (the shape InSpectra reads; no inspectra in the tests: it is Mac-only) [check: tests/docs_cmd/]
- Given the synonym-candidates step, When semkit docs runs, Then its description has no option line and no Example line, its examples field holds its examples in the «command  # -> result» form, the --top description ends with «Default: 10.», the --source description ends with «Default: both. Allowed: ruwordnet, navec, both.», and --top has arity maximum 1 [check: tests/docs_cmd/]
- Given any read step in d.json, When it is read, Then it carries IN, --text, --column and --whole of read [check: tests/docs_cmd/]
- Given semkit docs run twice, When the files are compared, Then they are byte for byte the same [check: tests/docs_cmd/]
- Given core/docs.py, When it is searched, Then it names no semkit module, step or command (the hook is the only place that does) [check: tests/docs_cmd/]
- Given semkit describe, When it runs, Then its output is unchanged (snapshots) [check: tests/test_describe.py]
- Given every step, When the help standard test runs, Then each step meets the standard or is in the allowlist [check: tests/steps/test_help_standard.py]

## How to test

Integration through the semkit CLI runner: build the document, read it as JSON and check the fields; a unit test of core/docs.py on a small Typer app with no semkit code.

## Basis

core/opencli.py (the Click tree walk: reuse its reading, do not change its output); steps/__init__.py (doc_lines, argument_names: how the help splits a docstring today); the InSpectra viewer reads OpenCLI with the commands at the root.

## Read first

- `src/rb_semkit/core/opencli.py`
- `src/rb_semkit/steps/__init__.py`

## Out of scope

- Rewriting the docstrings of the steps to the standard, and running every example against its result (SEMKIT-055); any change of semkit describe; translating the help; rendering HTML.
