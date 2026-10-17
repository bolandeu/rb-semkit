---
id: SEMKIT-023
title: 'CLI pipeline core: read, chained steps, write; the step table and its generator;
  the text, dupes and n-gram steps'
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
- src/rb_semkit/cli.py
- src/rb_semkit/pipeline/
- src/rb_semkit/steps/__init__.py
- src/rb_semkit/steps/text.py
- src/rb_semkit/steps/dupes.py
- src/rb_semkit/steps/analysis.py
- src/rb_semkit/core/opencli.py
- src/rb_semkit/commands/describe.py
- pyproject.toml
- scripts/bench_parts/cli.py
- tests/test_help.py
- tests/test_cli.py
- tests/test_contracts.py
- tests/test_describe.py
- tests/contracts/
- tests/snapshots/help/read.txt
- tests/snapshots/help/steps/text/
- tests/snapshots/help/steps/dupes/
- tests/snapshots/help/steps/analysis/
test_paths:
- tests/pipeline/
docs: none
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-003
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**Ядро CLI: read, цепочка шагов, write; таблица шагов и генератор; шаги
  поиска/удаления/извлечения, дублей и n-грамм.** semkit read IN шаги… write OUT (Click
  chain), порядок записи. Состояние конвейера: текущая таблица, рабочая колонка; шаги-правки
  на месте (--as — новая колонка), фильтры (keep-*/drop-*), отчёты (их таблица становится
  текущей). Генератор шагов из сигнатур и docstring; каждая область держит свои записи
  в своём модуле — следующие задачи добавляют области без правки ядра. Списки в аргументах:
  @путь, «a,b», @имя (через хук резолвера; пока — встроенные стоп-слова и маркеры).
  Сводка в stderr, --trace, --quiet, --dry-run, отказ без --overwrite, запись целиком
  или никак, ошибки до чтения входа. Авторегистрация команд, хук ai_section для --ai,
  describe со шагами, снапшоты справки по папкам областей. Бенчмарк 1M строк через
  5 шагов.'
---

The thin end-to-end path of the CLI (ADR 0008), with the frame every other step plugs into.
1. Pipeline: semkit read IN [--column C] [--whole] STEP… write OUT [--overwrite]. A chained group (Click chain) whose first command is read and last is write; any number of steps between, run in the order written. read/write go through rb_dataio; '-' is stdin/stdout JSONL; read --whole reads a text file as one cell (column text); --column picks the working column, by default the first text column.
2. Pipeline state: the current table, the working column, the summaries. Step kinds: change (rewrites the working column in place; --as NAME writes a new column instead), filter (keeps or drops rows), report (its result table becomes the current table; the working column becomes its first text column).
3. Step table and generator: one table maps public functions to steps; the generator builds a Click command per entry from the signature (keyword arguments become options with their defaults and Literal choices, bools become flags) and the docstring (the help). Each area keeps its entries in its own module under the steps package; the generator discovers the modules, so a later task adds an area without editing the core. In this task: the text matchers as steps <verb>-<matcher> for find/remove/extract (find adds a bool column NAME_find), plus keep-<matcher> and drop-<matcher> (filter); dupes (with --action drop as a filter); ngrams and bigrams (report).
4. List arguments: an argument that takes items accepts @path (a file, one item per line, UTF-8, BOM and CRLF stripped), a comma list in quotes, or @name. @name resolves through a resolver hook: when the module rb_semkit.core.wordlists exists and has resolve(name) and names(), use it; otherwise only the bundled stopwords and the marker lists by their names. An unknown name is refused with the names that exist.
5. Output and errors: after each step one stderr line (step, rows before → after, cells changed); --trace FILE writes a row-level JSONL journal (row, step, column, before, after); --quiet drops the stderr lines; --dry-run runs all steps and writes nothing; OUT that exists is refused without --overwrite, and the file is written to a temp file and renamed (whole or not at all). A wrong step, option or value is refused before the input is read (exit code of a usage error, the message names the step, the option and the allowed values; with --json the error envelope with code, message, hint). Nothing but the result goes to stdout.
6. Discovery hooks for later tasks: cli.py registers every module of the commands package that exposes a Typer app or a command, so a new command module needs no edit of cli.py; --ai prints the bundled SKILL.md followed by the sections that modules expose through an ai_section() hook (the steps and, later, the lists).
7. describe --json lists every step with its options; help snapshots of the steps live in tests/snapshots/help/steps/<area>/ (one folder per step area), so later tasks own their own snapshot folders.
8. Speed: a bench part runs read parquet → 5 cleaning steps → write parquet over 1M phrases within the library budget plus read and write.

## Acceptance

- Given core.csv with a phrase column, When semkit read core.csv remove-words --items 'купить' dupes --kind lemmas --action drop write out.csv runs, Then out.csv has the phrases without «купить» and without lemma duplicates, in the input order [check: tests/pipeline/]
- Given a JSONL stdin, When semkit read - drop-words --items @stop.txt ngrams -n 2 write - runs, Then stdout is JSONL rows ngram, count, docs and stderr has one summary line per step [check: tests/pipeline/]
- Given a change step with --as clean, When it runs, Then the column clean is added and phrase keeps its old values; without --as phrase is rewritten [check: tests/pipeline/]
- Given out.csv exists, When the pipeline would write it without --overwrite, Then exit code is non-zero, the message names --overwrite and out.csv is unchanged; given a step that fails mid-way, Then out.csv is unchanged [check: tests/pipeline/]
- Given --dry-run, When the pipeline runs, Then the summary is printed and no file is written [check: tests/pipeline/]
- Given remove-words --mode nope, When the pipeline starts, Then it is refused before reading the input, naming the step remove-words, the option --mode and the allowed values; with --json the error is a JSON envelope with code, message and hint [check: tests/pipeline/]
- Given --trace t.jsonl, When a remove step changes 2 cells, Then t.jsonl has 2 rows with row, step, column, before, after [check: tests/pipeline/]
- Given read --whole article.txt split... , When the input is a text file, Then the table has one cell with the whole text [check: tests/pipeline/]
- Given @minus.txt with a BOM and CRLF, @stopwords and 'a,b', When used as items, Then each gives the expected items; @nope is refused with the names that exist [check: tests/pipeline/]
- Given semkit describe --json, When read, Then it lists read, write and every step of this task with its options; every step has a help snapshot under its area folder [check: tests/pipeline/]
- Given 1M phrases in parquet, When the bench part runs 5 cleaning steps, Then it ends within its budget [check: tests/pipeline/]

## How to test

CLI level: typer CliRunner and a subprocess for stdin/stdout, tmp files in csv, jsonl and parquet; the help snapshots; one marked speed test.

## Basis

Follow the cli-builder frame that is already here (output.guard, --json envelopes, AI-readable errors, describe as OpenCLI, help snapshots). Read and write through rb_dataio (plan §3: as_text=True, fillna, JSONL on pipes) — it becomes a required dependency of the package. Steps are generated from the library: the step table names the function, its kind and the arguments that need a CLI form; the help is the function's docstring.

## Read first

- `docs/adr/0008-cli-pipeline-of-chained-steps.md`
- `src/rb_semkit/cli.py`
- `src/rb_semkit/commands/describe.py`
- `docs/plan.md`

## Out of scope

- Steps of the other areas (change, declension, morph, corpus, coverage, textstats, compare, serp, split, markers, list tools): the steps task.
- User list folders, the list manifest, the Bukvarix lists, semkit lists: the word-list task.
- The text of SKILL.md and README: the steps task.
