---
id: SEMKIT-057
title: 'semkit run NAME: named scenarios of semkit''s own steps, bundled or in the
  project, with parameters and help'
status: in_review
attempts: 2
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
- src/rb_semkit/core/services.py
- src/rb_semkit/output/__init__.py
- CHANGELOG.md
test_paths:
- tests/scenarios/
- tests/test_cli.py
- tests/test_describe.py
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

1. A scenario file NAME.toml: description (one line), the parameters (name, default, help; every parameter has a default, so a scenario runs with the input alone; a parameter without a default is refused when the file is loaded, exit 2 naming the file and the parameter), and steps: the chain as read takes it, one step per line, with {name} placeholders; {text} is the input phrase. Bundled scenarios ship in the package (data/scenarios); the project folder .rb_semkit/scenarios/ adds more, and one of the same name overrides the bundled one.
2. semkit run NAME [IN | --text TEXT…] [--set name=value…] [write OUT]: the input as read takes it (IN, --text, '-'); each --set fills a parameter (an unknown one is refused with exit 2); besides the declared parameters, any option of any step of the scenario can be set as --set STEP.OPTION=VALUE (nearest.model=e5-small, synonym-candidates.top=20): it replaces the option's value in that step, or adds the option when the step has none; a step that is not in the scenario, or an option the step does not take, is refused with exit 2 naming the steps and their options. Then the steps run as one read pipeline. The input may be one phrase or many (a file, several --text, '-'): a scenario with per_phrase = true runs its whole chain once for each input row, {text} being that row's phrase, and joins the results into one table with a first column input (the phrase the row comes from), in the input order, each part sorted as its steps sort; a scenario without it runs the chain once over the whole table. One row and many rows give the same result for the same phrase, and the same columns: the column input is there for one phrase too, so the output has one shape whatever the input. Without write, a table on the terminal, as read does.
3. semkit run --help lists the scenarios with their descriptions; semkit run NAME --help shows its description, parameters with defaults and its steps. semkit docs (SEMKIT-054) lists each scenario under run.
4. A scenario whose step or option does not exist is refused when it is loaded, with exit 2 naming the file and the line.
5. The first bundled scenario, intent-synonyms: phrase synonyms of one intent. All the variations, the input phrase itself among them (the first row of the slots), multiplied, agreed, scored by meaning against the input, sorted by similarity from the highest. per_phrase = true. Parameters threshold (0: every variation stays; 0.85 cuts below), model (bge-m3), source (ruwordnet). Steps: synonym-candidates --all --source {source} --as-slots; linear-combinations; agree; nearest --to {text} --threshold {threshold} --model {model}; use-column match; drop-cells empty; sort-rows --by similarity --desc.
6. run is no longer hidden; the agent guide and README show run intent-synonyms --text "растаможка авто".

## Acceptance

- Given run intent-synonyms --text 'растаможка авто' with the test encoder and thesaurus fixture, When it runs, Then the result equals the same chain written out in read, and every row has a match [check: tests/scenarios/]
- Given --set threshold=0.9, When it runs, Then the nearest step takes 0.9 [check: tests/scenarios/]
- Given run intent-synonyms without --set, When it runs, Then every combination of the slots is in the result, the input phrase among them, sorted by similarity from the highest [check: tests/scenarios/]
- Given --set nearest.model=e5-small and --set synonym-candidates.top=20, When it runs, Then those steps take those values; --set nosuchstep.x=1 and --set nearest.nosuch=1 are refused with exit 2 naming the steps and their options [check: tests/scenarios/]
- Given run intent-synonyms --text 'растаможка авто' with no --set, When it runs, Then it runs with the defaults of every parameter, and run intent-synonyms --help shows each default [check: tests/scenarios/]
- Given a scenario file with a parameter without a default, When it is loaded, Then it is refused with exit 2 naming the file and the parameter [check: tests/scenarios/]
- Given run intent-synonyms --text 'растаможка авто' --text 'таможенное оформление импорта' (or a file of these two rows), When it runs, Then the table has a first column input, the rows of the first phrase then those of the second, each part sorted by similarity from the highest, and the part of each phrase equals the result of running it alone [check: tests/scenarios/]
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

## Feedback

### Attempt 1: file docstring

- update the docstring of src/rb_semkit/pipeline/group.py: +planned +reported

### Attempt 2: the Architect's verdict

The review found blockers; close each:

- [blocker] C1/C11 CONTEXT.md: the glossary entry **Pipeline** says "never a built-in scenario" and `_Avoid_: scenario, recipe`. The diff names the new object "scenario" in code, help, README, SKILL.md and the TOML files. The glossary was not changed in the diff. Add a **Scenario** term and drop the Avoid line (or choose another word), and write an ADR or note on the change (C2: see the memory/ADR rule on composite steps). The term and the glossary must agree.

Minor remarks of the review: optional, if they do not widen the task:

- [minor] C5 core/scenarios/__init__.py `_step_lines`: the line number of a step is found by "first line at or after `steps =` that contains the step text". A step text that is a substring of an earlier line (e.g. a comment) gives a wrong line in the error. It is a heuristic, not a parse.
- [minor] C5 commands/run.py: `_command` copies a base command and sets attributes with `# ty: ignore`; it works but is fragile against Typer/Click changes.
- [minor] [missing] CHANGELOG.md has no entry for SEMKIT-057, while other tasks (SEMKIT-054, -060) have one — «6. run is no longer hidden; the agent guide and README show run intent-synonyms …» (the Architect may add it).

### Architect's note

The review blocker (glossary) is closed by the Architect in main, commit 3869130: CONTEXT.md now has the Scenario term, ADR 0010 records the decision. Do not edit CONTEXT.md or docs/adr. Merge main, keep the word scenario. Add the CHANGELOG.md entry for run NAME / intent-synonyms. The two minor remarks are optional.

### Attempt 2 (not counted): main moved and conflicts with the work

`main` changed since your work began, and merging it conflicts in:

- `CHANGELOG.md`

Merge it into your branch (`git merge main`), resolve each file keeping both behaviours, `git add` it and run the checks; do not commit: Antagor commits the merge with your work when the round ends (IDEA-201).
