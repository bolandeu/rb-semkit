---
id: SEMKIT-045
title: Pipeline steps use the project of the CLI, not the current folder
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
type: bugfix
owns_paths:
- src/rb_semkit/pipeline/
- src/rb_semkit/commands/read.py
- src/rb_semkit/steps/vectors.py
- src/rb_semkit/core/wordlists/folders.py
test_paths:
- tests/pipeline/test_project_folder.py
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-005
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'Шаги конвейера берут проект из CLI, а не текущую папку.


  Сейчас шаги ищут models.dir и списки проекта (@niche/…, папки из конфига) от текущей
  папки; при запуске с опцией проекта — не там. Шаги должны получать ту же папку проекта,
  что и команды. Относительная папка списков в конфиге — от корня проекта.


  Приёмка: models.dir проекта находится из другой текущей папки; @niche/minus проекта
  находится; относительная папка списков — от проекта; без опции — как раньше.


  Вне: новые опции, шаги векторов эпиков.'
---

A pipeline run for a project given by the project option of the CLI (not the current folder) must use that project: today the steps start from the current folder, so the steps by meaning look for models.dir of the config, and the list steps look for the project word lists (@niche/... and the folders listed in the config), in the wrong place. The commands already take the project from the CLI context (models, lists, config); the pipeline steps must get the same folder. A folder of lists written as a relative path in the config is relative to the project root, not to the current folder.

## Acceptance

- Given a project in folder P with models.dir set in its config to a folder holding a model, and the current folder elsewhere, When semkit with the project option P runs read IN cluster-meaning write OUT, Then the model of models.dir is used and nothing says the model is missing [check: tests/pipeline/test_project_folder.py]
- Given a project in folder P with its own list @niche/minus, and the current folder elsewhere, When semkit with the project option P runs read IN drop-words @niche/minus write OUT, Then the list of P is used [check: tests/pipeline/test_project_folder.py]
- Given a lists folder written as a relative path in the config of P, When a list step runs from another current folder with the project option P, Then the folder is found relative to P [check: tests/pipeline/test_project_folder.py]
- Given no project option, When the pipeline runs inside a project folder, Then the behaviour of before holds [check: tests/pipeline/test_project_folder.py]

## How to test

Integration through the semkit CLI (the pipeline test runner) with two temporary folders (the project and another current folder) and the deterministic test encoder.

## Basis

How the commands take the project from the CLI context (models, lists, config); the word list folder lookup; the encoder lookup of the vectors base.

## Read first

- `src/rb_semkit/commands/models.py`
- `src/rb_semkit/core/wordlists/folders.py`
- `src/rb_semkit/steps/vectors.py`

## Out of scope

- new options; the vector steps of the epics
