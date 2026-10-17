---
id: SEMKIT-022
title: Public word-keys helper of the analysis area; dir(rb_semkit) lists only the
  public names
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
type: chore
owns_paths:
- src/rb_semkit/core/analysis/frequency.py
- src/rb_semkit/core/analysis/__init__.py
- src/rb_semkit/__init__.py
- src/rb_semkit/core/corpus/
test_paths:
- tests/core/test_public_names.py
- tests/analysis/
docs: none
tools: []
worker_args: null
class: mechanical
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-002
spec_refs: []
checks:
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**Мелочи после E-002.** Хелпер _word_keys, которым пользуется область
  corpus, сделать непубличным-но-открытым word_keys; dir(sk) показывает только публичные
  имена, без ast, Path, functools и т. п.'
---

Two small fixes. (1) The corpus area imports the private helper _word_keys of src/rb_semkit/core/analysis/frequency.py (word -> key, lemma, stopword flag). Rename it to word_keys (no leading underscore, a docstring saying other areas use it, like bundled_stopwords there) and update every import in src/rb_semkit/core/corpus/. It is not a public name of the package: do not put it in __all__ of the analysis area. (2) dir(rb_semkit) lists the module's own imports (Any, Path, annotations, ast, functools, importlib) next to the public names: __dir__ in src/rb_semkit/__init__.py returns globals() too. Make it return the public names only (the discovered names and InvalidArguments), sorted.

## Acceptance

- Given import rb_semkit as sk, When dir(sk) runs, Then it holds no name of ast, functools, importlib, Path, Any or annotations, and it holds every discovered public name [check: tests/core/test_public_names.py]
- Given the source tree, When grepped, Then no module outside analysis imports a name with a leading underscore from rb_semkit.core.analysis [check: tests/core/test_public_names.py]

## How to test

Unit tests in tests/core/test_public_names.py; the existing analysis and corpus tests must pass unchanged.

## Read first

- `src/rb_semkit/core/analysis/frequency.py`
- `src/rb_semkit/__init__.py`

## Out of scope

- Any change of behaviour of ngrams, bigrams or the corpus functions.
