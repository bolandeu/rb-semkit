---
id: SEMKIT-042
title: 'parse-html and headings: pages as HTML into columns and their heading structure'
status: in_review
attempts: 1
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
- src/rb_semkit/core/html/
- src/rb_semkit/steps/html.py
- src/rb_semkit/core/frame.py
- pyproject.toml
- src/rb_semkit/core/textstats/functions.py
- src/rb_semkit/data/SKILL.md
- src/rb_semkit/pipeline/state.py
- src/rb_semkit/steps/__init__.py
- uv.lock
- CHANGELOG.md
test_paths:
- tests/html/
- tests/conformance/test_cases.py
- tests/snapshots/help/steps/html/headings.txt
- tests/snapshots/help/steps/html/parse-html.txt
- tests/steps/fixtures/pages.csv
- tests/snapshots/describe.json
- tests/snapshots/help/read.txt
- tests/steps/areas.py
- tests/steps/test_steps.py
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-007
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'parse-html и headings: HTML страниц в колонки и структура заголовков.


  parse-html — шаг на колонке HTML: добавляет text (видимый текст без ссылок), links,
  all, main (основной контент без меню, шапки и подвала), title, description, h1;
  имена как у --pages. Скрипты, стили, скрытое не считаются; noindex, alt и title
  по умолчанию учитываются, --drop-noindex и --drop-attributes исключают; не HTML
  — пустые колонки, в сводке число таких строк. headings — отчёт: строка на заголовок
  по порядку (url, номер, уровень, текст). Обёртка над selectolax и trafilatura (замер
  в плане).


  Приёмка: страница «Импорт» — title, description, h1, main с разделами статьи без
  меню; страница MegaGroup — слов в пределах 1 % от 1683; ссылка уходит в links; noindex,
  комментарии noindex, alt — по умолчанию есть, флаги убирают; пустая ячейка и текст
  без тегов — пустые колонки, код 0; headings по порядку, номер с 1 по каждому url.


  Вне: скачивание и JS, summary, сравнения, coverage.'
---

The Human gives pages as HTML (one page: read page.html --whole; many: a table with url and html) and gets their parts as columns every text step takes, and their heading structure.

- parse-html: a change step on the working column of HTML. It adds: text (the visible text without the text of links), links (the text of links), all (both), main (the main content without menus, header and footer), title, description (the meta description), h1 (the first H1). The names match the --pages table of the vector steps (url, text, title, h1). Scripts, styles, noscript, templates and hidden elements are never counted. By default the text of <noindex> (the tag and the <!--noindex--> comments) and the alt and title attributes count; --drop-noindex and --drop-attributes leave them out. A cell that is not HTML or is empty gets empty columns, and the step summary counts such rows.
- headings: a report, one row per heading in page order: url (when the table has it), order, level (H1-H6), text.
- The parsing is a thin wrapper over ready libraries, measured in the plan: selectolax (lexbor) for the zones, meta tags, headings and noindex; trafilatura with favor_recall for main. Add them as dependencies of the package.
- A page built by JavaScript has no text in its HTML: the help says the Human gives the rendered HTML.

## Acceptance

- Given the test page of the plan (ost-term import), When parse-html runs, Then title, description and h1 «Таможенное оформление импорта» are filled, main holds the sections of the article («Документы для таможенного оформления импорта», «Частые вопросы о таможенном оформлении») and no menu items of the header or footer [check: tests/html/test_parse_html.py]
- Given the Miratext page of the plan (megagroup base shop), When parse-html then text-stats on all run, Then the word count is within 1 % of 1683 [check: tests/html/test_parse_html.py]
- Given a small page with a link «купить диван» inside a paragraph, When parse-html runs, Then links holds «купить диван», text holds the paragraph without it, all holds both [check: tests/html/test_parse_html.py]
- Given a page with <noindex>скрыто</noindex>, <!--noindex-->тоже<!--/noindex--> and <img alt="диван">, When parse-html runs, Then all holds the three words by default; with --drop-noindex the first two are gone; with --drop-attributes «диван» is gone [check: tests/html/test_parse_html.py]
- Given a table of three cells: a page, an empty cell and plain text without tags, When parse-html runs, Then the page is parsed, the other two get empty columns, the summary line names 2 rows without HTML, and the exit is 0 [check: tests/html/test_parse_html.py]
- Given the test page, When headings runs, Then the rows start with H1 «Таможенное оформление импорта», H2 «ОСТ-ТЕРМИНАЛ», H2 «Расположение таможенного поста и склада» in page order, with the order numbers 1, 2, 3 [check: tests/html/test_headings.py]
- Given a table with url and html of two pages, When headings runs, Then each row carries its url and the order restarts at 1 per page [check: tests/html/test_headings.py]

## How to test

Integration through the semkit CLI (the pipeline test runner): semkit read IN parse-html ... write OUT and semkit read IN headings write OUT. The two pages of the plan copied into the test fixtures; small pages written in the test modules.

## Basis

The step table (Step and STEPS of an area module), a change step that adds several columns (text-stats) and a report step (split-text); the measured choice of libraries in the plan.

## Read first

- `docs/plans/html-and-brief.md`
- `docs/plans/html-pages/ost-term-import.html`
- `src/rb_semkit/steps/textstats.py`
- `CONTEXT.md`

## Out of scope

- fetching pages or rendering JavaScript
- summary, the comparisons, coverage (other tasks)

## Feedback

### Blocked: scope_held (holders ['SEMKIT-034', 'SEMKIT-043'], paths ['pyproject.toml', 'src/rb_semkit/core/textstats/functions.py', 'src/rb_semkit/data/SKILL.md', 'src/rb_semkit/pipeline/state.py', 'src/rb_semkit/steps/__init__.py', 'tests/snapshots/describe.json', 'tests/snapshots/help/read.txt', 'tests/steps/areas.py', 'tests/steps/test_steps.py', 'uv.lock'])

### Attempt 1: file docstring

- update the docstring of src/rb_semkit/core/frame.py: +put_columns

### Attempt 1 (not counted): main moved and conflicts with the work

`main` changed since your work began, and merging it conflicts in:

- `src/rb_semkit/pipeline/state.py`
- `src/rb_semkit/steps/__init__.py`
- `uv.lock`

Merge it into your branch (`git merge main`), resolve each file keeping both behaviours, `git add` it and run the checks; do not commit: Antagor commits the merge with your work when the round ends (IDEA-201).

### Attempt 1 (not counted): main moved and conflicts with the work

`main` changed since your work began, and merging it conflicts in:

- `src/rb_semkit/data/SKILL.md`

Merge it into your branch (`git merge main`), resolve each file keeping both behaviours, `git add` it and run the checks; do not commit: Antagor commits the merge with your work when the round ends (IDEA-201).
