---
id: SEMKIT-036
title: 'off-topic, classify-queries, assign-pages: phrases against the core, a query
  report and the site pages by meaning'
status: in_review
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
- src/rb_semkit/core/relevance/
- src/rb_semkit/steps/relevance.py
- tests/steps/fixtures/pages.csv
- README.md
- src/rb_semkit/steps/vectors.py
test_paths:
- tests/relevance/
- tests/steps/test_examples.py
- tests/snapshots/help/steps/relevance/assign-pages.txt
- tests/snapshots/help/steps/relevance/classify-queries.txt
- tests/snapshots/help/steps/relevance/off-topic.txt
- tests/snapshots/describe.json
- tests/snapshots/help/read.txt
- tests/steps/areas.py
- tests/steps/test_steps.py
- tests/steps/fixtures/page_texts.csv
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-034
budget_usd: null
epic: E-005
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'off-topic, classify-queries, assign-pages: фразы против ядра, отчёта
  о запросах и страниц сайта по смыслу.


  Три шага добавляют колонки и не удаляют строки. off-topic: оценка 0–1 удалённости
  от центра ядра (с весом --freq) или от центра --seed и флаг по порогу. classify-queries:
  отчёт о запросах против ядра --against — ближайшая фраза, сходство, цель да/нет.
  assign-pages: ядро против таблицы --pages (url, text) — лучшая страница и сходство,
  вторая и сходство. Основу векторов не меняют.


  Приёмка: чужая фраза — наибольшая оценка и флаг; --freq смещает центр; --seed меняет
  центр; classify даёт ближайшую фразу и цель да/нет, строки на месте; несуществующий
  --against — код 2; assign-pages ставит угловой диван на страницу угловых, вторая
  — прямые; нет url или text — код 2, одна страница — вторая пустая; примеры шагов
  работают на фикстурах.


  Вне: дубли и кластеры по смыслу, второй эпик (каннибализация, пробелы, абзацы),
  сбор текстов страниц.'
---

Three steps that place each phrase against a reference by meaning. Each adds columns and never drops a row; the Human decides by sorting and filtering on the columns.

- off-topic: every phrase of the core gets a 0–1 score of its distance from the centre of the core (the mean of the phrase vectors weighted by frequency with --freq, plain without it), or from the centre of --seed phrases (a list name or a file) when given, and a yes/no flag by --threshold.
- classify-queries: the working table is a search query report; --against names the core (a table read as read does, its phrase column by the usual column rules). Every query gets the nearest core phrase, the similarity and target yes/no by --threshold.
- assign-pages: the working table is the core; --pages names a table with the columns url and text (the text of the page: its title, H1 and body as the Human prepared them). Every phrase gets the best page, its similarity, the second page and its similarity.
- All three use the base of the vectors (the model registry, the encoder, the index, --model and --threshold with the default of the model, the deterministic test encoder of the tests) and add nothing to it. A page text longer than the model input is cut by the encoder as the base does, and the help says so.

## Acceptance

- Given a core of sofa phrases and «скачать игру диван» far from them by the test encoder, When off-topic runs, Then that phrase has the highest score and the flag yes, the sofa phrases have the flag no, and no row is dropped [check: tests/relevance/test_off_topic.py]
- Given --freq, When off-topic runs, Then the centre is weighted by frequency: a frequent phrase pulls the centre, so a rare phrase near it scores lower than without --freq [check: tests/relevance/test_off_topic.py]
- Given --seed with two phrases, When off-topic runs, Then the score is the distance from the centre of the seed phrases, not of the core [check: tests/relevance/test_off_topic.py]
- Given a report of three queries and --against a core where «угловой диван купить» is nearest to the first query, When classify-queries runs, Then the first query gets that phrase, the similarity and target yes; a query below the threshold gets target no; all three rows stay [check: tests/relevance/test_classify_queries.py]
- Given --against a file that does not exist, When classify-queries runs, Then it is refused with exit 2 naming the flag and the path [check: tests/relevance/test_classify_queries.py]
- Given a core and --pages with two pages (угловые диваны, прямые диваны), When assign-pages runs, Then «угловой диван» gets the corner page first and the straight page second, each with its similarity [check: tests/relevance/test_assign_pages.py]
- Given --pages without a url or a text column, When assign-pages runs, Then it is refused with exit 2 naming the missing column; given a pages table of one page, Then the second page and its similarity are empty [check: tests/relevance/test_assign_pages.py]
- Given the step help of each of the three, When the examples of the step table run on the step fixtures, Then each does something [check: tests/steps/test_examples.py]

## How to test

Integration through the semkit CLI (the pipeline test runner): semkit read IN STEP ... write OUT, with the deterministic test encoder of the base (fixed vectors for the phrases of each case). Small fixtures in the test modules; a pages table among the step fixtures for the step example.

## Basis

The step table (Step and STEPS of an area module) and the report steps of the compare area for an option that names another table; the base of the vectors task this depends on.

## Read first

- `src/rb_semkit/steps/compare.py`
- `docs/plans/vectors.md`
- `CONTEXT.md`

## Out of scope

- dupes --kind meaning, cluster-meaning (other tasks)
- competing pages, gaps, paragraphs of texts (the second vectors epic)
- fetching page texts from the web

## Feedback

### Blocked: scope_held (holders ['SEMKIT-035', 'SEMKIT-043', 'SEMKIT-045'], paths ['README.md', 'src/rb_semkit/steps/vectors.py', 'tests/snapshots/describe.json', 'tests/snapshots/help/read.txt', 'tests/steps/areas.py', 'tests/steps/test_steps.py'])

SEMKIT-035, SEMKIT-043, SEMKIT-045 finished; your kept work on README.md, src/rb_semkit/steps/vectors.py, tests/snapshots/describe.json, tests/snapshots/help/read.txt, tests/steps/areas.py, tests/steps/test_steps.py is back in the worktree; main is merged into your branch where it merges clean

`main` changed since your work began, and merging it conflicts in:

- `src/rb_semkit/steps/vectors.py`
- `tests/steps/fixtures/pages.csv`

Merge it into your branch (`git merge main`), resolve each file keeping both behaviours, `git add` it and run the checks; do not commit: Antagor commits the merge with your work when the round ends (IDEA-201).
