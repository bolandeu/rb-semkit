---
id: SEMKIT-037
title: Help and docstrings say «the bundled dictionary», not the add-in name
status: in_progress
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
- src/rb_semkit/core/corpus/typos.py
- src/rb_semkit/core/morph/lemmatizer.py
- src/rb_semkit/core/morph/functions.py
- src/rb_semkit/core/text/matchers/pos.py
test_paths:
- tests/core/test_no_vba_in_docs.py
docs: none
tools: []
worker_args: null
class: mechanical
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-005
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'Справка и docstring говорят «встроенный словарь», а не имя надстройки.


  Справка is-typo и другие docstring (опечатки, лемматизатор, коды частей речи, матчер
  частей речи) называют «!SEMTools dictionary». По ADR 0006 продукт не называет надстройку:
  писать «встроенный словарь». Проверка docstring, которая уже ловит упоминания VBA,
  должна ловить и «SEMTools».


  Вне: манифест списков слов (колонка источника и имя списка stop/semtools — публичный
  контракт), материалы переноса.'
---

The help of is-typo (semkit read IN is-typo --help) says «a wordform the !SEMTools dictionary or pymorphy3 knows», and other docstrings that reach the help or --ai name the add-in the same way (the typos of the corpus, the lemmatizer, the part-of-speech codes, the part-of-speech matcher). Product text must not name the add-in (ADR 0006): say «the bundled dictionary». The check of docstrings that already refuses VBA references must refuse «SEMTools» too, so it does not come back.

## Acceptance

- Given semkit read IN is-typo --help, When the Human reads it, Then it says «the bundled dictionary» and no «SEMTools» [check: tests/core/test_no_vba_in_docs.py]
- Given every docstring of the package, When the docs check runs, Then none holds «SEMTools» or «!SEMTools», and the check has an example that it finds them [check: tests/core/test_no_vba_in_docs.py]

## How to test

Unit: the existing docstring check of the package with «SEMTools» added to its pattern, and its example list.

## Out of scope

- the word list manifest (its source column and the list name stop/semtools): a list name is a public contract, renaming it is another decision
- conformance case files and docs/vba, where the add-in is named on purpose
