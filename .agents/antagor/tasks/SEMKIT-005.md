---
id: SEMKIT-005
title: Port the text matchers and markers from the add-in VBA
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
type: feature
owns_paths:
- src/rb_semkit/core/text/matchers/
- src/rb_semkit/core/markers/
test_paths:
- tests/matchers_vba/
- tests/matchers/
- tests/markers/
docs: none
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on:
- SEMKIT-002
budget_usd: null
epic: E-001
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'Перенести шаблоны текста и маркеры из VBA надстройки. SEMKIT-002 написана
  по примерам приёмки, а не перенесена из надстройки. Задача: для каждого шаблона
  найти обработчик VBA, сравнить с кодом на конкретных фразах, привести код к VBA
  (отступления — только из ADR 0005), указать обработчик в docstring, на каждое изменение
  — тест. Расхождение VBA с приёмкой — вопрос Архитектору.'
---

The text matchers and markers were written to the acceptance examples, not ported from the add-in. The Human requires the add-in's algorithms (ADR 0005). This task audits every matcher against its VBA handler and makes the code follow the VBA.

For each matcher (chars, spaces, positions, around, regex, word_content, word_case, word_position, pos, repeats, stopwords, phrases, cells, markers) and each verb it supports:
1. Find the ribbon button in ribbon_full.txt (the `-> handler` name) and read the handler in RibbonCallbacks.vba (obfuscated names; helper functions and forms in the same folder).
2. Compare the handler with the current code on concrete phrases: what counts as a word, a latin/cyrillic/UA char, punctuation, a position, which occurrence 'around' takes and whether it includes the pattern, how word lists match (all/any, start/end), how repeats and cells are decided, how the toponym list is matched and which preposition is taken with it.
3. Make the code follow the VBA. Deviate only where ADR 0005 says so: ё = е, stopwords case-insensitive, split on any whitespace, no double spaces in results, markers spelled as the list and joined by ', '.
4. Put the handler name(s) and the VBA line range in each matcher's docstring, with one line on any ADR 0005 deviation.
5. For every behaviour that changed, add a test with the phrase that showed the difference.

A difference between the VBA and an existing acceptance line or test: ask in the inbox (question), do not choose and do not edit the existing test.

## Acceptance

- Given each matcher of the module, When its docstring is read, Then it names the VBA handler and line range it ports, or says «no VBA handler: derived from <handler>» [check: tests/matchers_vba/test_vba_refs.py]
- Given the VBA handler of each matcher run by hand on the audit phrases, When the same phrases go through sk.find/remove/extract, Then the results match except the ADR 0005 deviations; each case is a test row (phrase, matcher, verb, expected) [check: tests/matchers_vba/test_vba_cases.py]
- Given a report of the audit, When the task is done, Then docs-free summary in the task result lists per matcher: handler, «matched» or «fixed: <what>» [check: tests/matchers_vba/test_vba_cases.py]

## How to test

Public library seam (import rb_semkit as sk): a table of (phrase, matcher, verb, expected) cases derived from the VBA handlers, at least 3 per matcher, including the edge cases where the old code differed.

## Basis

VBA: /Users/bolandau/Work/_sandbox/semtools/reverse/vba/RibbonCallbacks.vba; ribbon map: /Users/bolandau/Work/_sandbox/semtools/reverse/ribbon_full.txt; marker lists: /Users/bolandau/Work/_sandbox/semtools/reverse/downloads/spiski/. Prior art of a VBA-faithful port: the dupes, n-gram and bigram rules (SEMKIT-003, SEMKIT-004) traced from handlers —kka, ako—, akoa, ako·, ak—, –·ao. ADR 0005 lists the allowed deviations.

## Read first

- docs/adr/0005-port-vba-fix-defects.md
- CONTEXT.md

## Out of scope

- dupes, n-grams, bigrams, counts, lemmatizer (already ported).
- New matchers beyond v1; the CLI.
