---
id: SEMKIT-055
title: 'Every step''s docstring to the help standard: one-line summary, option lines,
  short examples with results'
status: in_review
attempts: 0
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: human
worker: claude-code
type: docs
owns_paths:
- src/rb_semkit/core/
- src/rb_semkit/steps/
- tests/snapshots/
- tests/steps/test_help_standard.py
- tests/steps/test_examples.py
- src/rb_semkit/pipeline/commands.py
test_paths:
- tests/steps/test_help_standard.py
- tests/steps/test_examples.py
- tests/docs_cmd/test_docs_cmd.py
- tests/steps/fixtures/one_page.csv
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-054
budget_usd: null
epic: null
spec_refs: []
checks:
- uv run --extra vectors pytest
resident: null
tool: null
pr: null
translation: 'Привести docstring каждого шага к стандарту SEMKIT-054: одна строка
  — что даёт шаг, строки опций, 1–3 коротких примера с результатом на русских фразах;
  поведение не меняется; список исключений теста опустеет.'
---

SEMKIT-054 writes docs/help-standard.md and a test with an allowlist of the steps that do not meet it. This task brings every step to it and empties the allowlist.

For each step's docstring (the library function or the Adapted wrapper): a first sentence that says in one line what the step gives; the paragraphs of what it does, plain and short; one «name: text» line per option; one to three Example lines of a real short command, each followed by a «-> result» line (ASCII arrow, the format of docs/help-standard.md) with a short result on Russian SEO phrases («купить диван» → …). The meaning of a step and its options do not change; only the text.

## Acceptance

- Given the help standard test, When it runs, Then the allowlist is empty and every step passes [check: tests/steps/test_help_standard.py]
- Given every Example of every step, When the examples test runs them, Then each runs and its result matches its «->» line; the runner that checks the result is built here (SEMKIT-054 leaves it out) [check: tests/steps/test_examples.py]
- Given semkit docs, When it runs, Then no step description repeats an option line [check: tests/steps/test_help_standard.py]

## How to test

The help standard test and the example runner over every step; help snapshots refreshed.

## Basis

docs/help-standard.md and tests/steps/test_help_standard.py of SEMKIT-054; the existing Example lines and tests/steps/test_examples.py.

## Out of scope

- Any change of behaviour, option names or defaults; translating the help; README and the agent guide.
