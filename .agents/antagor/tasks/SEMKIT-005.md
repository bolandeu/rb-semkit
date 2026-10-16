---
id: SEMKIT-005
title: Port the text matchers and markers from the add-in VBA
status: in_progress
attempts: 0
blocked: true
blocked_reason: needs_scope
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: human
worker: claude-code
type: feature
owns_paths:
- src/rb_semkit/core/text/matchers/
- src/rb_semkit/core/markers/
- src/rb_semkit/core/morph/lemmatizer.py
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
1. Find the matcher's buttons in docs/vba/matchers.md (index table: menu path → handler → section) and read their entries: algorithm, quirks, ADR 0005 deviation, worked examples. Open RibbonCallbacks.vba only to settle a point the entry leaves open.
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

Reference of the VBA algorithms, traced from the handlers (the source of truth for this task): docs/vba/matchers.md — 255 buttons of find/remove/extract, shared sections S1–S12, quirks and ADR 0005 deviations per button; it also lists the buttons that are broken in the add-in (no handler or a run-time error) — port those from the nearest working handler it names. Raw VBA, only for a point the reference leaves open: /Users/bolandau/Work/_sandbox/semtools/reverse/vba/RibbonCallbacks.vba; ribbon map: /Users/bolandau/Work/_sandbox/semtools/reverse/ribbon_full.txt; marker lists: /Users/bolandau/Work/_sandbox/semtools/reverse/downloads/spiski/. Prior art of a VBA-faithful port: the dupes, n-gram and bigram rules (SEMKIT-003, SEMKIT-004) traced from handlers —kka, ako—, akoa, ako·, ak—, –·ao. ADR 0005 lists the allowed deviations.

## Read first

- docs/vba/matchers.md (the entries of the matcher being ported; the index first)
- docs/adr/0005-port-vba-fix-defects.md
- CONTEXT.md

## Out of scope

- dupes, n-grams, bigrams, counts, lemmatizer (already ported).
- New matchers beyond v1; the CLI.

## Feedback

### Answer to question #1

> around() finds the pattern as whole words in any case; the VBA buttons (docs/vba/matchers.md R1 and X1, `––·a` … `–—–k`) find it as a plain substring as typed, case-insensitive only in the first-occurrence Remove buttons; SEMKIT-002 acceptance 2 (remove around('в', after=True, include=True) on '  купить  диван  в  москве ' gives 'купить диван') and tests/matchers/test_extract.py hold only with whole words: as a substring the first 'в' is inside 'диван', and the result is 'купить ди'.
> Question: How does around() find its pattern?
> Options:
> 1. VBA: a substring as typed; Remove with the first occurrence ignores case, Remove with the last occurrence and every Extract match case (ё = е); update the SEMKIT-002 acceptance and the tests
> 2. Keep whole words in any case (ё = е), named in the docstring as a deviation from the VBA
> Recommended: VBA: a substring as typed; Remove with the first occurrence ignores case, Remove with the last occurrence and every Extract match case (ё = е); update the SEMKIT-002 acceptance and the tests

Option 1 (VBA, per ADR 0005): a substring as typed; Remove with the first occurrence ignores case, Remove with the last occurrence and every Extract match case (ё = е). Update the SEMKIT-002 acceptance line and the tests to the VBA results.

### Answer to question #2

> The VBA runs VBScript RegExp, where \w, \d, \s and \b are ASCII (docs/vba/matchers.md S8: port with re.ASCII); the existing test tests/matchers/test_remove.py expects sk.remove with sk.regex(r'\bв\b') to cut the Cyrillic word 'в' from 'купить диван в москве', and that needs Unicode \b.
> Question: Do sk.regex and sk.cells('regex') use ASCII or Unicode character classes?
> Options:
> 1. ASCII (re.ASCII), as VBScript; change the test to a pattern without \b
> 2. Unicode (the Python default), a deviation from the VBA for Cyrillic text; keep the test
> Recommended: Unicode (the Python default), a deviation from the VBA for Cyrillic text; keep the test

Option 2 (the Human, 2026-10-17): Unicode character classes, a deviation recorded in ADR 0005 (commit on main); name it in the docstring; keep the test.

### Answer to question #3

> The VBA has one NOT-match button, remove `aok·` (docs/vba/matchers.md R1, its bug fixed): it keeps only the matches, joined with no separator ('диван 120x200' with \d+ gives '120200'); the existing test test_regex_not_match_removes_whole_phrases_that_do_not_match expects remove with regex(r'\d', invert=True) on ['a1', 'abc'] to give ['a1', ''], and find and extract with invert have no VBA handler.
> Question: What does regex(invert=True) do?
> Options:
> 1. VBA: the found part is all text the pattern does not match: remove keeps only the matches joined with no separator ('a1' gives '1'), extract gives the text outside the matches, find is True where such text exists; update the test
> 2. Keep: a phrase is found as a whole when the pattern does not match it (find True, extract the phrase, remove '')
> Recommended: VBA: the found part is all text the pattern does not match: remove keeps only the matches joined with no separator ('a1' gives '1'), extract gives the text outside the matches, find is True where such text exists; update the test

Option 1 (VBA, per ADR 0005): the found part is the text the pattern does not match; remove keeps only the matches joined with no separator; extract gives the text outside the matches; find is True where such text exists. Update the test.
