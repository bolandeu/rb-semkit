---
id: SEMKIT-048
title: parse-html keeps the zone names when the HTML column is text; the steps over
  pages take the column text by default
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
- src/rb_semkit/core/html/
- src/rb_semkit/steps/html.py
- src/rb_semkit/steps/__init__.py
- src/rb_semkit/steps/nearest.py
- src/rb_semkit/steps/compare.py
- src/rb_semkit/steps/coverage_meaning.py
- tests/snapshots/
test_paths:
- tests/html/
- tests/steps/
- tests/vectors/
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-046
budget_usd: null
epic: null
spec_refs: []
checks:
- uv run pytest
resident: null
tool: null
pr: null
---

Two fixes of the column names that pages tables use.

1. One page read with read page.html --whole holds its HTML in the column text. parse-html then cannot give its text zone that name: the zone goes to text_2 and text keeps the raw HTML (the test page of the plan: text 17046 words, all 3073). The zone columns must keep their names, which match the --pages table of the vector steps: the HTML column is renamed html when its name is one of the zone names (text, links, all, main, title, description, h1). When a column html already exists too, the step refuses with exit 2 and a message naming both columns.

2. nearest --against and compare-grams --competitors take by default the first text column that is no url column (steps.texts_column). On a table of parse-html (html, url, text, ..., title, h1) or of url,title,h1,text that is html or title, not text; the user has to give --against-column text. The default becomes: the column named text when there is one, else as now.

## Acceptance

- Given read docs/plans/html-pages/ost-term-import.html --whole, When parse-html runs, Then text is the visible text without link text (fewer words than all), there is no text_2, and the HTML is in the column html [check: tests/html/test_parse_html.py]
- Given a table whose HTML column is named main, When parse-html runs, Then main is the main content and the HTML is in the column html [check: tests/html/test_parse_html.py]
- Given a table with an HTML column text and a column html as well, When parse-html runs, Then it is refused with exit 2 naming both columns [check: tests/html/test_parse_html.py]
- Given a table with the HTML column named html, When parse-html runs, Then the output is as before [check: tests/html/test_parse_html.py]
- Given a competitors file with columns url,title,h1,text, When compare-grams --competitors runs without a column option, Then it compares against the column text [check: tests/steps/]
- Given an --against file of parse-html output, When nearest runs without --against-column, Then it uses the column text [check: tests/steps/]
- Given a file with no column named text, When these steps run, Then the column is chosen as before [check: tests/steps/]

## How to test

Integration through the semkit CLI (the pipeline test runner) with the fixtures of the html and step tests; nearest with the small test encoder the vector tests use.

## Basis

parse-html and its tests; steps.texts_column and its callers (nearest, compare, coverage_meaning).

## Read first

- `src/rb_semkit/steps/html.py`
- `src/rb_semkit/steps/__init__.py`
- `docs/plans/html-and-brief.md`
- `docs/plans/html-pages/ost-term-import.html` — the test page (read only; copy it into the html fixtures if a test needs it)

## Out of scope

- other columns or options of parse-html
