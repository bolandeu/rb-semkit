---
id: SEMKIT-033
title: 'CLI that tells the truth: --as, errors, lemma matching of lists, help and
  guide in CLI terms, top-level commands; the e2e run on a real core in the gate'
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
- tests/pipeline
- tests/steps
- tests/snapshots
- tests/test_cli.py
- tests/test_help.py
- tests/test_describe.py
- tests/wordlists
- src/rb_semkit/data/morph
- scripts/build_parts/morph.py
- docs/vba/deviations/morph.md
- pyproject.toml
- scripts/build_parts/morph.toml
- scripts/build_parts/wordlists.py
- uv.lock
- scripts/bench_parts/cli.py
test_paths:
- tests/pipeline
- tests/steps
- tests/snapshots
- tests/test_cli.py
- tests/test_help.py
- tests/test_describe.py
- tests/wordlists
- tests/e2e
- tests/change/test_errors.py
- tests/conformance/data_manifest/morph.json
- tests/conformance/data_manifest/wordlists.json
- tests/core/test_frame.py
- tests/core/test_morph.py
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

Pipeline: --as NAME of an existing column is refused before the input is read, naming the column; a second find-* of the same column gets its own name, never overwrites; a step after --as works on the new column (the column --as made becomes the working one, the old stays); --as columns keep the order written; cells changed of --as counts the non-empty new values. remove-cells empty drops the rows with an empty cell (no crash). Reading keeps a number column with a space-padded cell numbers (the int column with an empty cell comes from dataio v0.1.23); a number column picked as working column is text only for the step, numbers are written back as numbers. The output format, a txt target with several columns and the trace folder are checked before the input is read (exit 2). | head and any closed stdout end quietly (exit 0, no error line). In human mode read ends with one line: rows written and the target, or that it was a dry run. read with no arguments exits 2.

Errors: every refusal of the pipeline exits 2 before the input is read and names the step and the CLI flag (not the Python argument), with an action in CLI terms: a missing file of IN or of any file option (--against, --competitors, --freq, --pairs, --synonyms, @path), CSV on stdin ('-' is JSONL; pass the file path), a bad value of every enum option (coverage --mode, cluster-serp --method, compare-lists --op among them), a too big result (names --limit), a weight that is not a number (names the row and the value). A list error names only the bad items (at most 5) and the step to use instead (drop-phrases for multi-word items). An unknown @name lists the names that exist (the closest first). An empty input says the input is empty.

Lists: the words and phrases steps get an option to compare by lemmas (the library's lemmatizer of the matchers); the guide's clean-a-core pipeline and the help examples use lists that fit a commercial core (no list that holds купить drops a commercial core; @minus/universal without купить, or the example uses a fitting list); find-markers --lists takes @markers/NAME and a user's marker file; @FILE of a CSV reads its first column without the header; cluster-serp --freq takes the frequency column by name (an option for it); weights «5,5» and «1 000» are numbers.

Help and guide: every option has its own text and its accepted values (in --help and in describe --json as accepted values); describe --json gives each step its kind; positional names are the user's (KIND, not positional_kind); no Python terms in the step help (Series, DataFrame, sk., InvalidArguments, norm_phrase, True/False/None, ADR, the add-in), no explanation of an argument the CLI has no option for; a paragraph does not leak into the next option; examples run and do something on the shipped data (remove-around with a literal, remove-edges with characters, combinations with --limit or a small list, split-by-words with --good, parents with a phrase list). Update the library docstrings where the behaviour of SEMKIT-030..032 changed a rule they state (decline accusative, coverage across a dash). The guide (--ai) matches the CLI: --quiet (no -q), the --json envelope as it is, exit 3 without auth login, text-stats a change step, how columns are read, --json before the steps, its pipelines on files a user has. Help text is not hard-wrapped mid-sentence.

Top-level commands: global --dry-run writes nothing for config set, skill install, lists add / rm, init (or the command refuses it); config set lowers cli.min_version and the version gate applies to every command alike; config set lists [paths] and a bad value exit 2 with the accepted format; init and its help name the same folder; a relative SEMKIT_LISTS resolves against the current folder, SEMKIT_LISTS wins over config lists, lists add --to a folder outside the search path warns; lists show @NAME takes the @ and an unknown name exits 2; --quiet keeps the result and hides only extra lines; doctor unhealthy exits non-zero; run is hidden or does something; --json envelopes have one shape for every command and do not escape Cyrillic; --trace refuses an existing file without --overwrite and its row is 1-based like the file.

E2E run in the gate: fixtures of a real core (the first 1000 Bukvarix phrases for «купить диван») and a real page text with its core (svh); a test recomputes the ten runs of the check independently (no semkit code in the recount) and compares: n-grams 1-3 with weight, drop-words / drop-phrases by a list (and by lemmas), dupes by lemmas, cluster-serp soft and hard rules, coverage exact, text-stats chars and words, the round trip of every format with numbers and an empty cell, the declension and lemma words of SEMKIT-030 through the CLI.

Carried over from the core tasks.

Part of speech: the bundled dictionary codes лучше as a noun and покрывало as a verb; add both (лучше: comparative adjective / adverb; покрывало: noun) to the dictionary correction SEMKIT-030 made (its data and its build), so find-pos follows with no code of its own.

Docstring rules changed by the core tasks (write each into the docstring of the function and refresh the help snapshots):

- SEMKIT-031: (1) sk.split_text: a dash between words (— – -) and the point of an abbreviation of data/text/words.toml (г. ул. т. е. тел. руб.) do not cut a phrase; both are dropped (module doc said «т.д.» splits). (2) sk.text_stats: no lemma for top/nausea/ttr/mtld/zipf = every single-letter word + abbreviations and units of data/text/words.toml (рублей, см, мм, мл, кг; шт, кв, стр, ул, руб are abbreviations); words count numbers with inner . , - as one word and keep an apostrophe inside a word. (3) sk.coverage: exact and lemmas cross any punctuation inside a sentence (dash, comma), never a sentence end (. ! ? …, not an abbreviation point); any_order stays inside one split_text phrase; density rounded to 4 decimals. (4) sk.compare_grams / sk.bm25: with lemmas, a word without a lemma (single letter, abbreviation, unit) is in no gram but counts in the words of a text. (5) sk.compare_stats: integer metrics (chars, chars_no_spaces, words, unique) stay integers where whole; the docstring says 'rounded to 4 decimals'. (6) sk.ngrams / sk.bigrams: words are those of split_text (punctuation at word edges is dropped, ★ is no gram, 31.03.2026 one word). (7) sk.counts share / share_of_total: rounded to 4 decimals. (8) sk.CoreSpelling / is_typo / typo_correction: a stopword or a wordform the !SEMTools dictionary or pymorphy3 knows is never a typo; a correction starts with the same letter as the word. (9) sk.add_minus_words: new argument unsure=False (CLI --unsure, help now 'See the description above.'): only rows with sure True are added unless unsure; a table without the column sure is all sure; a sure cell read from a file as text (True/TRUE/ИСТИНА/1) counts. (10) sk.pos: a capitalised word is looked up in lower case (the docstring says «Быстро» is an adjective as in the add-in). (11) sk.chars('punctuation'): a point or comma between two digits is no punctuation (2.5, 541,67 stay).
- SEMKIT-032: (1) match_type: a phrase with quotes/brackets is not wrapped again; operator goes inside the existing quote/bracket pair; brackets/quotes/quoted_* replace the old wrap; antisemantic drops the old wrap. (2) translit to='ru': a word in capitals reads by small-letter groups and stays in capitals (ZHUK→ЖУК); new groups shch, ts, yy; 'y' after a/u before no vowel is й; ь and ъ (and е/ё) cannot reverse. (3) change_case toponyms: punctuation at word edges is ignored and kept; a hyphen splits a word so «ростов-на-дону»→«Ростов-на-Дону». (4) phonetic: whole-word table has 'ikea'→'икеа'. (5) replace_words: punctuation at the edges of the found words is kept around the replacement; an empty replacement removes the words with that punctuation. (6) extract_utm: only the part before '#' is searched. (7) split_digits: a size NxM (x latin/cyrillic, any case) stays whole. (8) switch_layout: signs of the Russian layout map to English keys and back: . = /, ',' = ?, : = ^, ; = $, ? = &, " = @, № = #, / = |.
- SEMKIT-030: (1) decline_noun: the accusative is no longer from the tables only; an inanimate noun takes its nominative («диван» → «диван»), an animate one its genitive («кот» → «кота»), a singular in -а/-я the table form («книгу»); a hyphenated noun declines whole by pymorphy3 («диваном-кроватью»). The docstring still says «диван» → «дивана». (2) decline: a nominative plural phrase declines in the plural («угловые диваны» → «угловых диванов»); a feminine, neuter or plural adjective declines from its lemma («большая скидка» → «большой скидки»); the accusative agrees by animacy («купить кожаный диван», «рыжего кота»). (3) decline_full_name: a value that is not three words stays as it is (no InvalidArguments); surnames in -ых/-их stay; a man's surname in -а/-я declines («Глинки»). (4) part_of_speech and SemtoolsLemmatizer: a word with no part of speech gets the code «unkn», not «»; a не- noun of the dictionary whose rest is an adjective is «a». (5) complements and fix_word_order step 1: a complement ends at its first noun and the oblique nouns and adjectives right after it, not at the last noun among the next five. (6) phrase_end buy_markers: a marker right after a preposition stays («диван с доставкой купить» → «диван с доставкой»).


dataio: pin rb-dataio to tag v0.1.23. It writes xlsx in linear time (DATAIO-024; add a benchmark that writes 100k rows to xlsx within a few seconds) and reads an int column with an empty cell from json, jsonl and xlsx as Int64 (DATAIO-025), so semkit's read needs no workaround for it: the e2e round trip checks it.


## Acceptance

- Given «лучше» and «покрывало на диван», When find-pos runs, Then лучше is no noun and покрывало is no verb [check: tests/steps]
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

## Feedback

### Blocked: timeout (detail ,"terminal_id":"term_65e0d8dd52c242c0","terminal_title":"◑ Antagor handoff prompt.md","terminal_title_stripped":"Antagor handoff prompt.md","workspace_id":"w1N"},"type":"agent_info"}}

--- screen ---
de == 0, f"{arguments}: {result.output}" 41 + summary = json.loads(result.stdout)["steps"][-1] 42 + did = { … 5 more lines (ctrl+o to expand) ⏺ Bash(uv run pytest tests/steps/test_examples.py -q --no-cov -p no:randomly 2>&1 | grep -E "^E +AssertionError" | head -30; cat tests/steps/fixtures/core.csv) ⎿ Running… ✢ Perambulating… (1h 0m 7s · ↓ 158.2k tokens · thought for 1s) ⎿ Tip: Use /clear to start fresh when switching topics and free up context ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── ❯ ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── ⏵⏵ bypass permissions on (shift+tab to cycle) · esc to interrupt · ← 3 agents)

Timeout hit mid-work, not a dead end. Continue from your worktree as it stands (66 changed files are kept): finish the tests/steps/test_examples.py fixes, then run the task checks and the full test suite once. Do not restart from scratch.

### Attempt 1: file docstring

- add a docstring to src/rb_semkit/commands/auth.py: what it holds and why
- add a docstring to src/rb_semkit/commands/config.py: what it holds and why
- add a docstring to src/rb_semkit/commands/describe.py: what it holds and why
- add a docstring to src/rb_semkit/commands/doctor.py: what it holds and why
- add a docstring to src/rb_semkit/commands/init.py: what it holds and why
- add a docstring to src/rb_semkit/commands/run.py: what it holds and why
- add a docstring to src/rb_semkit/commands/skill.py: what it holds and why
- update the docstring of src/rb_semkit/core/errors.py: +ConfigInvalid +Unhealthy
- update the docstring of src/rb_semkit/core/services.py: +check_project_compat
- add a docstring to src/rb_semkit/output/__init__.py: what it holds and why
- add a docstring to src/rb_semkit/output/json.py: what it holds and why
- update the docstring of src/rb_semkit/steps/text.py: +ByLemmas +MatcherFactory

### Attempt 2: the Architect's verdict

The review found blockers; close each:

- [blocker] [missing] No benchmark that writes 100k rows to xlsx. A search of `tests/` and `scripts/` for xlsx and 100000 finds only the 1M-row parquet speed test and the round-trip test. — «add a benchmark that writes 100k rows to xlsx within a few seconds»

Minor remarks of the review: optional, if they do not widen the task:

- [minor] C11 docs/plan.md: line 175 still says the dataio contract was "checked against dataio v0.1.21", while pyproject.toml now pins v0.1.23. It is a dated note, so it may stay; the Architect decides.
- [minor] C4 tests/e2e/fixtures: three fixture files of 1001 lines each (sofa_core, serp, svh_core) are in the diff. They are needed by the task's e2e run; no remark besides size.
- [minor] [wrong] The `Feedback` block asked the worker to add file docstrings (commands/*.py, output/*.py, steps/text.py, core/errors.py, core/services.py). `commands/run.py` has one; the reviewer did not check the other files one by one. Not an acceptance point.
