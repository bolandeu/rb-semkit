---
id: SEMKIT-049
title: 'read --text: phrases from the command line; a pipeline without write prints
  a table'
status: in_review
attempts: 2
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: architect
worker: claude-code
type: feature
owns_paths:
- src/rb_semkit/commands/read.py
- src/rb_semkit/pipeline/
- src/rb_semkit/output/
- src/rb_semkit/data/SKILL.md
- README.md
- tests/snapshots/
- tests/pipeline/
- src/rb_semkit/cli.py
- tests/test_cli.py
- tests/test_help.py
- tests/steps/test_guide.py
test_paths:
- tests/pipeline/
docs:
- README.md
- src/rb_semkit/data/SKILL.md
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: null
spec_refs: []
checks:
- uv run pytest
resident: null
tool: null
pr: null
translation: 'read --text: фразы прямо в команде; конвейер без write печатает таблицу
  в терминал (с --json или в пайп — JSONL).'
---

Quick tests of a step need a file today: read takes IN (a file, or '-' for JSONL on stdin), and write - gives JSONL only.

1. read --text TEXT (repeatable) makes the input table from the command line: one column phrase, one row per --text, in the order given. IN is then left out; IN and --text together are refused with exit 2.
2. A pipeline that ends without write prints the result as a table in the terminal (the human output of the CLI, every column, every row). With --json, or when stdout is not a terminal, it writes JSONL to stdout as write - does. write - stays as it is.
3. The read help, the agent guide (SKILL.md) and README show the short form: semkit read --text "растаможка авто" synonym-candidates --all

## Acceptance

- Given read --text 'растаможка авто' --text 'купить диван', When ngrams -n 1 runs without write, Then the terminal shows a table with the columns of the ngrams report [check: tests/pipeline/]
- Given read --text 'a b' with a write -, When it runs, Then the output is the same JSONL as for a file with a column phrase holding 'a b' [check: tests/pipeline/]
- Given read core.csv --text 'a', When it runs, Then it is refused with exit 2 and a message naming IN and --text [check: tests/pipeline/]
- Given a pipeline without write and --json (or stdout not a terminal), When it runs, Then stdout is JSONL of the result [check: tests/pipeline/]
- Given a pipeline with write out.csv, When it runs, Then it works as before [check: tests/pipeline/]

## How to test

Integration through the semkit CLI runner of the pipeline tests; the table checked by its header and rows in the captured output; help snapshots refreshed.

## Basis

commands/read.py and pipeline/tables.py (the '-' reader and the write step); output/human.py for the table.

## Out of scope

- Paging or truncating long tables; reading phrases from a plain-text stdin; any change of a step.

## Feedback

### Attempt 1: file docstring

- add a docstring to src/rb_semkit/output/human.py: what it holds and why

### Attempt 2: checks failed

- `uv run pytest` (exit 1)

```
ts/word_vectors/test_models_words.py::test_a_pull_puts_the_data_into_the_cache_and_list_shows_it_with_its_size[ruwordnet-ruwordnet-2021.db]
FAILED tests/word_vectors/test_models_words.py::test_a_pull_puts_the_data_into_the_cache_and_list_shows_it_with_its_size[navec-navec_test.tar]
FAILED tests/word_vectors/test_models_words.py::test_a_second_pull_downloads_nothing
FAILED tests/word_vectors/test_models_words.py::test_a_file_whose_checksum_differs_leaves_nothing
FAILED tests/word_vectors/test_models_words.py::test_remove_takes_the_data_out_of_the_cache_and_the_list
FAILED tests/word_vectors/test_synonym_candidates.py::test_data_not_in_the_cache_downloads_nothing_and_gives_the_pull_command
ERROR tests/word_vectors/test_synonym_candidates.py::test_a_word_gets_its_synonym_with_the_source_and_the_score_and_not_a_related_word
ERROR tests/word_vectors/test_synonym_candidates.py::test_the_words_are_the_lemmas_of_the_core_without_stopwords_and_numbers
ERROR tests/word_vectors/test_synonym_candidates.py::test_without_all_the_candidates_not_in_the_core_are_left_out
ERROR tests/word_vectors/test_synonym_candidates.py::test_all_gives_the_candidates_not_in_the_core_marked_so_and_each_lemma_once
ERROR tests/word_vectors/test_synonym_candidates.py::test_top_limits_the_candidates_of_the_word_vectors
ERROR tests/word_vectors/test_synonym_candidates.py::test_a_source_leaves_the_other_one_out
ERROR tests/word_vectors/test_synonym_candidates.py::test_as_synonyms_gives_the_file_of_synonyms_that_a_step_with_synonyms_reads
ERROR tests/word_vectors/test_synonym_candidates.py::test_a_top_below_one_is_refused
======= 56 failed, 5176 passed, 3 skipped, 8 errors in 256.08s (0:04:16) =======
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:455: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x12bee8130>
  result = tuple_new(cls, iterable)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
```
