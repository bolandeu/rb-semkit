---
id: SEMKIT-033
title: 'CLI that tells the truth: --as, errors, lemma matching of lists, help and
  guide in CLI terms, top-level commands; the e2e run on a real core in the gate'
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
type: bugfix
owns_paths:
- src/rb_semkit/pipeline
- src/rb_semkit/steps
- src/rb_semkit/commands
- src/rb_semkit/output
- src/rb_semkit/cli.py
- src/rb_semkit/data/SKILL.md
- src/rb_semkit/data/wordlists
- src/rb_semkit/core/wordlists
- src/rb_semkit/core/errors.py
- README.md
- scripts/build_parts/wordlists.toml
- src/rb_semkit/core
test_paths:
- tests/pipeline
- tests/steps
- tests/snapshots
- tests/test_cli.py
- tests/test_help.py
- tests/test_describe.py
- tests/wordlists
- tests/e2e
docs:
- README.md
- src/rb_semkit/data/SKILL.md
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on:
- SEMKIT-030
- SEMKIT-031
- SEMKIT-032
budget_usd: null
epic: E-004
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**CLI говорит правду + сквозная проверка в гейте.** Конвейер: --as по
  существующей колонке — отказ; шаг после --as работает с новой колонкой; remove-cells
  empty не падает; целые с пустой ячейкой остаются целыми; | head без ошибки; итоговая
  строка о записи. Ошибки: выход 2 до чтения, шаг и флаг CLI, действие в терминах
  CLI. Списки: сравнение по леммам; примеры и гайд не стирают коммерческое ядро; @markers/NAME;
  @CSV — первая колонка. Справка: у опций свои тексты и значения, в describe — значения
  и вид шага, без терминов Python, примеры работают; docstring''и — где правило поменяли
  030–032; --ai совпадает с CLI. Команды: --dry-run ничего не пишет, config set min_version
  обратимо, lists и --quiet правильно, единый --json. Сквозная проверка: 1000 фраз
  Букварикса и текст страницы, независимый пересчёт 10 прогонов в гейте.'
---

The end-to-end check (docs/plans/e2e-quality.md, items 20, 21, 27-50) found the CLI shell disagrees with itself and with its guide. Fix the CLI and the help; then check it end to end on real data.

Pipeline: --as NAME of an existing column is refused before the input is read, naming the column; a second find-* of the same column gets its own name, never overwrites; a step after --as works on the new column (the column --as made becomes the working one, the old stays); --as columns keep the order written; cells changed of --as counts the non-empty new values. remove-cells empty drops the rows with an empty cell (no crash). Reading keeps an integer column integer when it has an empty cell (xlsx, json, jsonl: 10 not 10.0) and a number column with a space-padded cell numbers; a number column picked as working column is text only for the step, numbers are written back as numbers. The output format, a txt target with several columns and the trace folder are checked before the input is read (exit 2). | head and any closed stdout end quietly (exit 0, no error line). In human mode read ends with one line: rows written and the target, or that it was a dry run. read with no arguments exits 2.

Errors: every refusal of the pipeline exits 2 before the input is read and names the step and the CLI flag (not the Python argument), with an action in CLI terms: a missing file of IN or of any file option (--against, --competitors, --freq, --pairs, --synonyms, @path), CSV on stdin ('-' is JSONL; pass the file path), a bad value of every enum option (coverage --mode, cluster-serp --method, compare-lists --op among them), a too big result (names --limit), a weight that is not a number (names the row and the value). A list error names only the bad items (at most 5) and the step to use instead (drop-phrases for multi-word items). An unknown @name lists the names that exist (the closest first). An empty input says the input is empty.

Lists: the words and phrases steps get an option to compare by lemmas (the library's lemmatizer of the matchers); the guide's clean-a-core pipeline and the help examples use lists that fit a commercial core (no list that holds купить drops a commercial core; @minus/universal without купить, or the example uses a fitting list); find-markers --lists takes @markers/NAME and a user's marker file; @FILE of a CSV reads its first column without the header; cluster-serp --freq takes the frequency column by name (an option for it); weights «5,5» and «1 000» are numbers.

Help and guide: every option has its own text and its accepted values (in --help and in describe --json as accepted values); describe --json gives each step its kind; positional names are the user's (KIND, not positional_kind); no Python terms in the step help (Series, DataFrame, sk., InvalidArguments, norm_phrase, True/False/None, ADR, the add-in), no explanation of an argument the CLI has no option for; a paragraph does not leak into the next option; examples run and do something on the shipped data (remove-around with a literal, remove-edges with characters, combinations with --limit or a small list, split-by-words with --good, parents with a phrase list). Update the library docstrings where the behaviour of SEMKIT-030..032 changed a rule they state (decline accusative, coverage across a dash). The guide (--ai) matches the CLI: --quiet (no -q), the --json envelope as it is, exit 3 without auth login, text-stats a change step, how columns are read, --json before the steps, its pipelines on files a user has. Help text is not hard-wrapped mid-sentence.

Top-level commands: global --dry-run writes nothing for config set, skill install, lists add / rm, init (or the command refuses it); config set lowers cli.min_version and the version gate applies to every command alike; config set lists [paths] and a bad value exit 2 with the accepted format; init and its help name the same folder; a relative SEMKIT_LISTS resolves against the current folder, SEMKIT_LISTS wins over config lists, lists add --to a folder outside the search path warns; lists show @NAME takes the @ and an unknown name exits 2; --quiet keeps the result and hides only extra lines; doctor unhealthy exits non-zero; run is hidden or does something; --json envelopes have one shape for every command and do not escape Cyrillic; --trace refuses an existing file without --overwrite and its row is 1-based like the file.

E2E run in the gate: fixtures of a real core (the first 1000 Bukvarix phrases for «купить диван») and a real page text with its core (svh); a test recomputes the ten runs of the check independently (no semkit code in the recount) and compares: n-grams 1-3 with weight, drop-words / drop-phrases by a list (and by lemmas), dupes by lemmas, cluster-serp soft and hard rules, coverage exact, text-stats chars and words, the round trip of every format with numbers and an empty cell, the declension and lemma words of SEMKIT-030 through the CLI.

## Acceptance

- Given core.csv with phrase,freq, When semkit read core.csv chpu --as freq write - runs, Then it exits 2 before reading, naming the column freq; When lemmatize --as key sort-words runs, Then sort-words changes key and phrase stays [check: tests/pipeline]
- Given a table with an empty phrase cell, When remove-cells empty runs, Then the row is dropped and exit is 0 [check: tests/pipeline]
- Given jsonl and xlsx with freq 10, 2 and an empty cell, When read and written to jsonl, Then freq is 10 and 2, not 10.0 [check: tests/pipeline]
- Given semkit read core.csv write - piped into head -1, When head exits, Then semkit exits 0 with nothing on stderr [check: tests/pipeline]
- Given a missing --against file, CSV on stdin, coverage --mode fuzzy, cluster-serp --method foo, compare-lists --op foo, permutations over 2000 phrases, When the pipeline starts, Then each exits 2 before reading the input, names the step and the flag, and its action names a CLI flag (no format=, sep=, encoding=) [check: tests/pipeline]
- Given drop-words @minus/cheap, When the pipeline starts, Then the error names at most 5 multi-word items and drop-phrases; Given @nope, Then the error lists existing names [check: tests/pipeline]
- Given core.csv with «купить дешевые диваны» and «диван со скидкой», When drop-phrases @minus/cheap runs with matching by lemmas, Then both rows are dropped [check: tests/steps]
- Given the guide's clean-a-core pipeline on the e2e sofa core, When it runs, Then it keeps more than half of the rows [check: tests/steps]
- Given every step, When its --help and describe --json are read, Then every enum option lists its values, every option has its own text, no step text holds Series, DataFrame, sk., InvalidArguments, norm_phrase, ADR or a Python literal, and every Example runs on the shipped data and changes or reports something [check: tests/steps]
- Given semkit --ai, When a test checks it against the CLI, Then every flag, envelope field, exit code and command it names exists and its pipelines run [check: tests/steps]
- Given semkit --dry-run config set name x, When it runs, Then config.toml is unchanged; Given config set cli.min_version 0.2.0 then 0.1.0, Then the second succeeds; Given config set lists '["/abs"]', Then it is set [check: tests/test_cli.py]
- Given --quiet lists show minus/free, When it runs, Then the items are printed; Given lists show @minus/cheap, Then the list is shown; Given an unknown name, Then exit 2 [check: tests/test_cli.py]
- Given the e2e fixtures, When the gate runs, Then the independent recount of the ten runs agrees with semkit [check: tests/e2e]

## How to test

CLI through CliRunner (tests/pipeline, tests/steps, tests/test_cli.py); help and describe snapshots refreshed; tests/e2e with fixtures in its own folder and a recount in plain Python

## Basis

ADR 0008 (pipeline of steps, help from the docstring); the step table of src/rb_semkit/steps; docs/plans/e2e-quality.md for every item and the ten runs

## Read first

- `docs/plans/e2e-quality.md`
- `docs/adr/0008-cli-pipeline-of-chained-steps.md`
- `src/rb_semkit/steps/__init__.py`
- `src/rb_semkit/pipeline/tables.py`

## Out of scope

- The behaviour of library functions (SEMKIT-030..032); only their docstrings
- dataio's xlsx writer speed (IDEA-231)
- Fetching texts or SERPs
