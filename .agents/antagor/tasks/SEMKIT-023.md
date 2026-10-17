---
id: SEMKIT-023
title: 'CLI pipeline core: read, chained steps, write; the step table and its generator;
  the text, dupes and n-gram steps'
status: queue
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
- docs/plan.md
- src/rb_semkit/commands/read.py
- src/rb_semkit/core/dupes/functions.py
- src/rb_semkit/core/errors.py
- src/rb_semkit/core/frame.py
- src/rb_semkit/core/lists/functions.py
- src/rb_semkit/core/markers/lists.py
- src/rb_semkit/core/text/base.py
- src/rb_semkit/core/text/matchers/cells.py
- src/rb_semkit/core/text/matchers/chars.py
- src/rb_semkit/core/text/matchers/pos.py
- src/rb_semkit/core/text/matchers/repeats.py
- src/rb_semkit/core/text/matchers/spaces.py
- src/rb_semkit/core/text/matchers/word_case.py
- src/rb_semkit/core/text/matchers/word_content.py
- src/rb_semkit/core/text/matchers/words.py
test_paths:
- tests/pipeline/
- tests/snapshots/describe.json
- tests/snapshots/help/read-write.txt
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

## Feedback

### Answer to question #1

> SEMKIT-023 acceptance asks the --json error envelope to carry code, message and hint; the project envelope (output.emit_error, SKILL.md 'Errors') carries code, message and action, and SKILL.md is out of this task.
> Question: Which key carries the recovery text of a pipeline usage error?
> Options:
> 1. Keep action, as every other command; read 'hint' in the acceptance as action
> 2. Add a hint key next to action for pipeline errors only
> 3. Rename action to hint everywhere (breaking change of the envelope)
> Recommended: Keep action, as every other command; read 'hint' in the acceptance as action

Option 1: keep action, as every other command; read 'hint' in the acceptance as action.

### Answer to question #2

> The E-003 goal writes 'drop-words @minus/universal remove-chars punctuation' (required arguments positional); SEMKIT-023 acceptance writes 'remove-words --items купить' and 'drop-words --items @stop.txt' (options). I implement options now (the task).
> Question: How does a step take a required argument of the library function?
> Options:
> 1. Both: as the option --NAME, or positional when it is the first required argument
> 2. Option only (--items, --kind), as the task acceptance
> 3. Positional only, as the epic goal
> Recommended: Both: as the option --NAME, or positional when it is the first required argument

Option 1: both. The first required argument is positional and also accepted as --NAME; the rest are options. The epic goal line is the target form (drop-words @minus/universal, remove-chars punctuation).

### Answer to finding #3

> ADR 0001 says rb_dataio comes as the extra [io]; SEMKIT-023 made it a required dependency (task Basis), pinned to the homeserver repo https://homeserver.tailee01ab.ts.net:3000/bolandeu/dataio.git (the GitHub URL in docs/plan.md §3 does not exist). docs/plan.md §3.2 is updated; the ADR wording is the Architect's.

Accepted: required dependency, the homeserver URL. ADR 0001 is updated on main.

### Answer to finding #4

> Typer 0.27 ships its own Click without chained groups; src/rb_semkit/pipeline/group.py chains the steps itself and imports typer._click (Command, Context, UsageError) and typer.core.TyperGroup, which are Typer internals. A Typer upgrade can break the pipeline group; tests/pipeline catches it.

Accepted with a guard: bound typer to the current minor in pyproject (>=0.27,<0.28) so an upgrade is a deliberate change; keep the pipeline tests as the tripwire.

### Blocked: needs_scope (entries [{'n': 1, 'text': "SEMKIT-023 acceptance asks the --json error envelope to carry code, message and hint; the project envelope (output.emit_error, SKILL.md 'Errors') carries code, message and action, and SKILL.md is out "}, {'n': 2, 'text': "The E-003 goal writes 'drop-words @minus/universal remove-chars punctuation' (required arguments positional); SEMKIT-023 acceptance writes 'remove-words --items купить' and 'drop-words --items @stop.t"}])

Answers in inbox #1-#4: keep action; both positional first argument and --NAME; dataio required (ADR 0001 updated); pin typer to the current minor.

### Attempt 1: file docstring

- add a docstring to src/rb_semkit/cli.py: what it holds and why
- add a docstring to src/rb_semkit/commands/read.py: what it holds and why
- add a docstring to src/rb_semkit/core/errors.py: what it holds and why
- update the docstring of src/rb_semkit/core/frame.py: +text_columns
- update the docstring of src/rb_semkit/core/markers/lists.py: +phrases
- update the docstring of src/rb_semkit/core/text/base.py: +verbs

### Attempt 2: the Architect's verdict

The review found blockers; close each:

- [blocker] C6 .agents/antagor/scratch/report.md: the worker's attempt report is committed (commits 67e3522, 2d8c5b0, 8ef9aaf). It is a stray file; it is not in `.agents/antagor/.gitignore`. Remove it from the tree.
- [blocker] [wrong] `read --whole` loses the blank lines of the text. `read_lines` uses dataio `txt` reading, which skips blank lines. I ran `semkit read w.txt --whole write -` on the file `a`, blank line, `b`: the cell is `a\nb`, not `a\n\nb\n`. A paragraph break is lost, and so is the structure of an article — «read --whole reads a text file as one cell (column text)»; «Then the table has one cell with the whole text».

Minor remarks of the review: optional, if they do not widen the task:

- [minor] C5 src/rb_semkit/pipeline/run.py: `--trace` is written after OUT. If the trace write fails, OUT is already replaced and the command reports an error. Write the trace first, or document the order.
- [minor] C4 src/rb_semkit/core/lists/functions.py: `compare_lists` gets the `DupeKind` type. The change is small and keeps one list of kinds (C3), but this function is not a step of this task. The Architect may accept it.
- [minor] C1 src/rb_semkit/pipeline/commands.py: the name `POSITIONAL = "positional_"` is a parameter prefix, not a positional marker. `POSITIONAL_PREFIX` says what it holds.
- [minor] [wrong] The `--json` error envelope keeps the key `action`, not `hint`. This follows the Architect's answer to question #1 (option 1), so it is not a defect. SKILL.md still has no word on it; that file is out of scope. Noted only.
- [minor] [extra] `--trace` also records the dropped rows of a filter step (`after` is null). The task says «a row-level JSONL journal (row, step, column, before, after)». This fits the journal, so I do not count it.
- [minor] [missing] The speed test passes, but the bench part has no number of its own: it uses the global `--limit` of 120 s. The task says «within the library budget plus read and write». Name the budget of the pipeline part, or state that the global limit is the budget.
