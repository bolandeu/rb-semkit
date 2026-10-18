---
id: SEMKIT-038
title: nearest, the page vector and split-paragraphs
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
- src/rb_semkit/core/nearest/
- src/rb_semkit/steps/nearest.py
- src/rb_semkit/core/relevance/
- src/rb_semkit/data/text/paragraphs.toml
- src/rb_semkit/data/vectors/page.toml
- src/rb_semkit/steps/__init__.py
- src/rb_semkit/steps/compare.py
- src/rb_semkit/steps/relevance.py
- src/rb_semkit/steps/vectors.py
test_paths:
- tests/nearest/
- tests/snapshots/help/steps/nearest/nearest.txt
- tests/snapshots/help/steps/nearest/split-paragraphs.txt
- tests/snapshots/help/steps/relevance/assign-pages.txt
- tests/snapshots/describe.json
- tests/snapshots/help/read.txt
- tests/steps/areas.py
- tests/steps/test_steps.py
docs: none
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on:
- SEMKIT-034
- SEMKIT-036
budget_usd: null
epic: E-006
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'nearest, вектор страницы и split-paragraphs.


  Каркас эпика: nearest — для каждой строки top-N строк таблицы --against с рангом
  и сходством (длинный отчёт, url совпадения); --threshold отсекает слабые, строка
  без совпадений остаётся с пустым совпадением. Вектор страницы: длинный текст режется
  на куски, векторы усредняются, title и h1 весят больше; его используют nearest и
  assign-pages (для коротких текстов вывод assign-pages не меняется). split-paragraphs:
  текст или таблица url+text → строка на абзац (url, номер, абзац); абзац — блок между
  пустыми строками, строка-заголовок — отдельный абзац.


  Приёмка: --top 3 даёт 9 строк для 3 фраз; порог оставляет пустое совпадение; --top
  0 и нет файла — код 2; вес title виден; assign-pages на коротких текстах не меняется;
  пример абзацев; нумерация с 1 по каждому url.


  Вне: coverage-meaning, ad-groups, synonym-candidates, сценарии.'
---

The frame of the epic: matching any two tables by meaning, the page vector for long texts, and the paragraph unit.

- nearest: for each row of the working table, the top --top (default 1) rows of --against (a table read as read reads it; its text column by the usual column rules, or --against-column) with rank and similarity, in a long report: the working phrase, the match, its rank, the similarity, and the url of the match when the against table has one. --threshold (optional) leaves out matches below it; a row with no match left keeps one row with empty match.
- Page vector: a text longer than the model input is cut into pieces the model takes whole; the piece vectors are averaged; when the table has title and h1 columns, their vectors are added with more weight (state the weights in the help). nearest and assign-pages both use it; assign-pages output does not change for short texts.
- split-paragraphs: a text file, or a table of url and text, into a report of one row per paragraph: url (empty for a file), number from 1, paragraph. A paragraph is a block between empty lines; a heading line (a short line without an end mark, followed by text) is a paragraph of its own. Spaces at the ends are trimmed; an empty text gives no rows.
- All use the base of E-005 (registry, encoder, index, --model, --threshold, the deterministic test encoder) and add nothing to it.

## Acceptance

- Given a core of 3 phrases and --against a table of 5 texts, When nearest --top 3 runs, Then the report has 9 rows, ranks 1-3 per phrase in order of similarity, and the url column of the matches [check: tests/nearest/test_nearest.py]
- Given --threshold 0.9 and a phrase whose matches are all below it, When nearest runs, Then that phrase has one row with an empty match [check: tests/nearest/test_nearest.py]
- Given --top 0, or --against a file that does not exist, When nearest runs, Then it is refused with exit 2 naming the flag (and the path) [check: tests/nearest/test_nearest.py]
- Given a text longer than the model input, When its vector is made, Then it is the weighted mean of its piece vectors; with title and h1 columns their weight shows (a page whose title matches the phrase ranks above a page that has it only deep in the text) [check: tests/nearest/test_page_vector.py]
- Given short page texts, When assign-pages runs before and after, Then its output is the same [check: tests/nearest/test_page_vector.py]
- Given «Диваны\n\nУгловые диваны бывают...\nЕщё строка.\n\n\nПрямые диваны...», When split-paragraphs runs, Then the rows are 1 «Диваны», 2 «Угловые диваны бывают... Ещё строка.» (the lines of a block joined by a space), 3 «Прямые диваны...» [check: tests/nearest/test_split_paragraphs.py]
- Given a table of two urls and texts, When split-paragraphs runs, Then the numbering starts at 1 for each url; an empty text gives no rows [check: tests/nearest/test_split_paragraphs.py]

## How to test

Integration through the semkit CLI (the pipeline test runner) with the deterministic test encoder of E-005; small tables in the test modules.

## Basis

The step table and the report steps; the option of a step that names another table (classify-queries --against of E-005); the encoder and index of E-005; the text splitting of the text area for line and sentence ends.

## Read first

- `docs/plans/vectors.md`
- `src/rb_semkit/steps/compare.py`
- `src/rb_semkit/core/text/words.py`
- `CONTEXT.md`

## Out of scope

- coverage-meaning, ad-groups, synonym-candidates (other tasks)
- the scenarios of the vectors plan (gaps, competing pages, links)
- fetching page texts

## Feedback

### Blocked: scope_held (holders ['SEMKIT-040', 'SEMKIT-041'], paths ['src/rb_semkit/steps/vectors.py', 'tests/snapshots/describe.json', 'tests/snapshots/help/read.txt', 'tests/steps/areas.py', 'tests/steps/test_steps.py'])

SEMKIT-040, SEMKIT-041 finished; your kept work on src/rb_semkit/steps/vectors.py, tests/snapshots/describe.json, tests/snapshots/help/read.txt, tests/steps/areas.py, tests/steps/test_steps.py is back in the worktree; main is merged into your branch where it merges clean
