---
id: SEMKIT-057
title: 'semkit run NAME: named scenarios of semkit''s own steps, bundled or in the
  project, with parameters and help'
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
- src/rb_semkit/commands/run.py
- src/rb_semkit/cli.py
- src/rb_semkit/core/scenarios/
- src/rb_semkit/data/scenarios/
- src/rb_semkit/pipeline/
- src/rb_semkit/core/docs/
- src/rb_semkit/data/SKILL.md
- README.md
- tests/scenarios/
- tests/snapshots/
- tests/test_help.py
test_paths:
- tests/scenarios/
docs:
- README.md
- src/rb_semkit/data/SKILL.md
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on:
- SEMKIT-056
- SEMKIT-054
budget_usd: null
epic: null
spec_refs: []
checks:
- uv run --extra vectors pytest
resident: null
tool: null
pr: null
translation: 'semkit run NAME: именованные сценарии только из шагов semkit (встроенные
  и из папки проекта), параметры --set, справка run --help / run NAME --help и в semkit
  docs; первый встроенный — intent-synonyms.'
---

A scenario is a named chain of semkit's own steps, kept so that a frequent chain runs by its name. It holds steps of semkit only; a flow that calls other tools is built outside.

1. A scenario file NAME.toml: description (one line), the parameters (name, default, help), and steps: the chain as read takes it, one step per line, with {name} placeholders; {text} is the input phrase. Bundled scenarios ship in the package (data/scenarios); the project folder .rb_semkit/scenarios/ adds more, and one of the same name overrides the bundled one.
2. semkit run NAME [IN | --text TEXT…] [--set name=value…] [write OUT]: the input as read takes it (IN, --text, '-'); each --set fills a parameter (an unknown one or a missing required one is refused with exit 2); then the steps run as one read pipeline. Without write, a table on the terminal, as read does.
3. semkit run --help lists the scenarios with their descriptions; semkit run NAME --help shows its description, parameters with defaults and its steps. semkit docs (SEMKIT-054) lists each scenario under run.
4. A scenario whose step or option does not exist is refused when it is loaded, with exit 2 naming the file and the line.
5. The first bundled scenario, intent-synonyms: phrase synonyms of one intent. Parameters threshold (0.85), model (bge-m3), source (ruwordnet). Steps: synonym-candidates --all --source {source} --as-slots; linear-combinations; agree; nearest --to {text} --threshold {threshold} --model {model}; use-column match; drop-cells empty; sort-rows --by similarity --desc.
6. run is no longer hidden; the agent guide and README show run intent-synonyms --text "растаможка авто".

## Acceptance

- Given run intent-synonyms --text 'растаможка авто' with the test encoder and thesaurus fixture, When it runs, Then the result equals the same chain written out in read, and every row has a match [check: tests/scenarios/]
- Given --set threshold=0.9, When it runs, Then the nearest step takes 0.9 [check: tests/scenarios/]
- Given --set nosuch=1, When it runs, Then it is refused with exit 2 naming the parameters there are [check: tests/scenarios/]
- Given a project scenario intent-synonyms.toml, When run intent-synonyms runs in that project, Then the project one is used [check: tests/scenarios/]
- Given a scenario with an unknown step, When run lists or runs it, Then it is refused with exit 2 naming the file and the line [check: tests/scenarios/]
- Given run --help and run intent-synonyms --help, When they run, Then the first lists intent-synonyms with its description and the second shows its parameters with defaults and its steps [check: tests/scenarios/]

## How to test

Integration through the semkit CLI runner with the test encoder and the thesaurus fixture of the vector tests; a project folder made in a tmp path.

## Basis

commands/read.py and pipeline/ (how a chain of steps is parsed and run: reuse it, the scenario is the same chain); commands/run.py (the placeholder to replace); the project folder of SEMKIT-045.

## Out of scope

- Calling other tools from a scenario; conditions or loops in a scenario; editing scenarios from the CLI.

## Read first

- `docs/plans/vectors.md`
