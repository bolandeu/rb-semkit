---
id: SEMKIT-054
title: 'Help standard and semkit docs: a deterministic human document of every command
  and step for InSpectra'
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
type: feature
owns_paths:
- docs/help-standard.md
- src/rb_semkit/commands/docs.py
- src/rb_semkit/cli.py
- src/rb_semkit/core/docs/
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

The help in a browser (InSpectra over an OpenCLI file) is hard to read: semkit describe nests the commands under command (InSpectra reads them at the root, so it shows nothing without a jq rewrite); a step page is one paragraph that repeats each option's explanation; the example sits at the end of the text, not in the OpenCLI examples field; defaults and allowed values are not shown, and every option shows as repeatable (<TOP...>); a step page and its composer do not show the input of read (IN, --text, '-' for JSONL), so the generated command is «semkit read synonym-candidates» with no input. describe is a cross-tool contract (core/opencli.py header), so it stays as it is; the human document is a new command.

1. A written standard of the step help, docs/help-standard.md, made so that the document is built from the code with no hand step (deterministic: the same code gives the same document byte for byte):
 - summary: the first sentence of the docstring, one line, what the step gives («Synonym candidates for the units of the core…»);
 - description: the paragraphs after it, without the option lines and without the Example lines;
 - option lines «name: text» go to that option only;
 - default, allowed values (Literal/enum) and whether an option repeats come from the signature, never from the text;
 - Example lines (one or more): «Example: <command>», optionally followed by «→ <short result>» on the next line («→ растаможка автомобиля»); they go to the examples field;
 - the input of read is shown on every step: IN (a file of any format), --text TEXT (repeatable), '-' (JSONL on stdin), and write OUT optional (without it a table on the terminal).
2. A command semkit docs: writes the human document, an OpenCLI file with the commands at the root (opencli, info, commands, options, arguments, examples), step descriptions and examples split as the standard says, defaults and allowed values in the option descriptions, arity maximum 1 for an option that does not repeat, and each read step carrying the arguments and options of read (IN, --text, --column, --whole) so the composer builds «semkit read IN step …». --out FILE writes it to a file, else stdout. Rendering the HTML is not semkit's job: the Human renders the file with InSpectra by a shell wrapper shared by all the CLIs.
3. A test of the standard (tests/steps/test_help_standard.py): for every step, summary present and one line, at least one Example, every option explained, no option line left in the description; the steps that do not meet it yet are listed in one allowlist in the test with a comment, so that SEMKIT task 2 of this pair empties it. Running semkit docs twice gives the same bytes.

## Acceptance

- Given semkit docs --out d.json, When InSpectra renders d.json, Then the commands and the read steps are listed (no empty page) [check: tests/docs_cmd/]
- Given the synonym-candidates step, When semkit docs runs, Then its description has no option line and no Example line, its examples field holds the example, --top shows default 10, --source shows ruwordnet|navec|both, and --top has arity maximum 1 [check: tests/docs_cmd/]
- Given any read step in d.json, When it is read, Then it carries IN, --text, --column and --whole of read [check: tests/docs_cmd/]
- Given semkit docs run twice, When the files are compared, Then they are byte for byte the same [check: tests/docs_cmd/]
- Given semkit describe, When it runs, Then its output is unchanged (snapshots) [check: tests/test_describe.py]
- Given every step, When the help standard test runs, Then each step meets the standard or is in the allowlist [check: tests/steps/test_help_standard.py]

## How to test

Integration through the semkit CLI runner: build the document, read it as JSON and check the fields; no inspectra in the tests.

## Basis

core/opencli.py (the Click tree walk, reuse it, do not change its output); steps/__init__.py (doc_lines, argument_names: how the help splits a docstring today); the InSpectra viewer reads OpenCLI with the commands at the root.

## Read first

- `src/rb_semkit/core/opencli.py`
- `src/rb_semkit/steps/__init__.py`

## Out of scope

- Rewriting the docstrings of the steps to the standard (the next task); any change of semkit describe; translating the help.
