---
id: SEMKIT-024
title: CLI steps for every other area of the library; the agent guide (--ai) and README
  with typical pipelines
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
- src/rb_semkit/steps/change.py
- src/rb_semkit/steps/declension.py
- src/rb_semkit/steps/morph.py
- src/rb_semkit/steps/corpus.py
- src/rb_semkit/steps/coverage.py
- src/rb_semkit/steps/textstats.py
- src/rb_semkit/steps/compare.py
- src/rb_semkit/steps/serp.py
- src/rb_semkit/steps/split.py
- src/rb_semkit/steps/markers.py
- src/rb_semkit/steps/listtools.py
- src/rb_semkit/data/SKILL.md
- tests/snapshots/help/steps/change/
- tests/snapshots/help/steps/declension/
- tests/snapshots/help/steps/morph/
- tests/snapshots/help/steps/corpus/
- tests/snapshots/help/steps/coverage/
- tests/snapshots/help/steps/textstats/
- tests/snapshots/help/steps/compare/
- tests/snapshots/help/steps/serp/
- tests/snapshots/help/steps/split/
- tests/snapshots/help/steps/markers/
- tests/snapshots/help/steps/listtools/
test_paths:
- tests/steps/
docs:
- README.md
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-023
budget_usd: null
epic: E-003
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**Шаги CLI для всех остальных областей; справка для агента (--ai) и
  README.** Каждая публичная функция становится шагом: изменение текста, склонение,
  морфология, анализ ядра, split-text, coverage, text-stats, compare-grams/stats,
  bm25, cluster-serp, маркеры, compare-lists, edges. Второй вход — опцией-файлом (--against,
  --competitors, --freq, --dictionary). Тест падает, если новая функция библиотеки
  не стала шагом. SKILL.md для --ai: форма конвейера, виды шагов, флаги, синтаксис
  списков и типовые конвейеры (чистка ядра, частотный словарь статьи, сравнение с
  конкурентами, вхождения ядра, кластеры по выдаче, сравнение списков) — каждый пример
  проверяется тестом. README — короткий раздел CLI.'
---

Every public function of rb_semkit that the core task did not cover becomes a step, so the whole library runs from one command line.
1. Steps by area: change (case, insert, move, replace, split digits, reverse, sort words, quotes, translit, chpu, layout, similar chars, match types, UTM, hashes, word order, phonetic), declension (decline, nouns, adjectives, full names, irrelevant words, ready patterns, complements, phrase end), morph (lemmatize, part of speech, wordforms), corpus (combinations, parents, children, basis phrases, good/bad split, clustering by frequency, synonyms to minus-words, typos, sentiment), split_text, coverage, text_stats, compare_grams, compare_stats, bm25, cluster_serp, markers (find/remove/extract-markers and keep/drop-markers), compare_lists and edges. Kinds: a function that rewrites a phrase is a change step; one that returns a new table is a report step; markers and edges follow the matcher steps of the core.
2. Arguments that are a second input take a file option: --against FILE (coverage texts, compare_lists second list), --competitors FILE (compare_grams, compare_stats), --freq FILE (cluster_serp), --dictionary FILE (sentiment); the file is read like read does (any dataio format, '-' not allowed here). Items and lists take @name, @path or a comma list as in the core.
3. A test walks the public names of rb_semkit and fails when a function is neither a step nor in an explicit list of names that are not steps (Lemmatizer, Matcher, InvalidArguments, pipe, word_list and the like): a function added to the library later must get its step table entry.
4. The agent guide: rewrite the bundled SKILL.md (printed by --ai) for this CLI: the pipeline form, the step kinds, --column, --as, --whole, --trace, --dry-run, --overwrite, the list syntax (@name, @path, 'a,b'), and typical pipelines with their exact command lines: clean a core (drop minus-words, remove punctuation and extra spaces, dupes by lemmas); the frequency dictionary of an article (read --whole, split_text, ngrams by lemmas); a text against competitors (compare-grams --competitors); core phrases in a text (coverage); SERP clusters (cluster-serp); compare two lists. Each example is run by a test.
5. README: a short CLI section with the same typical pipelines (not a copy of the help).

## Acceptance

- Given the public names of rb_semkit, When the step test walks them, Then every function is a step or in the explicit not-a-step list [check: tests/steps/]
- Given core.csv, When semkit read core.csv chpu --as url write - runs, Then the url column holds «divan-krovat-2-m» for «Диван-кровать 2 м!» [check: tests/steps/]
- Given article.txt, When semkit read --whole article.txt split-text ngrams -n 1 --lemmas write - runs, Then stdout holds the lemmas with count, docs and forms [check: tests/steps/]
- Given mine.txt and competitors.csv, When semkit read --whole mine.txt compare-grams --competitors competitors.csv write - runs, Then the rows have ngram, docs, median, mine and verdict [check: tests/steps/]
- Given serp.csv (phrase, position, url), When semkit read serp.csv cluster-serp --method hard --common 3 write - runs, Then each phrase has cluster and center [check: tests/steps/]
- Given the typical pipelines of SKILL.md, When the test runs each command line on its fixture, Then each exits 0 and gives the output the guide shows [check: tests/steps/]
- Given a step of this task with a wrong value (decline --case падеж), When the pipeline starts, Then it is refused naming the step, the option and the allowed values [check: tests/steps/]

## How to test

CLI level through CliRunner over small fixtures in tests/steps/fixtures/; help snapshots per area folder; the step-coverage test over the public names.

## Basis

Add one step-table module per area in the steps package, as the core task did for text, dupes and analysis; the generator and the pipeline state come from the core and are not changed here. A function whose arguments need a CLI form the generator cannot derive (a second table, a SERP table, a frequency table, a dictionary) takes a file option read through the same reader as read (any dataio format).

## Read first

- `docs/adr/0008-cli-pipeline-of-chained-steps.md`
- `README.md`

## Out of scope

- The pipeline core, the generator, read/write: SEMKIT-023.
- User list folders, the list manifest, semkit lists: the word-list task.
