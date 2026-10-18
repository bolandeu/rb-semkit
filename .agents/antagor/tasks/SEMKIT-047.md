---
id: SEMKIT-047
title: 'A separate default threshold for clusters by meaning: 0.975 for e5-small,
  the pair threshold stays 0.97'
status: queue
attempts: 1
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
- src/rb_semkit/data/vectors/models.toml
- src/rb_semkit/core/vectors/
- src/rb_semkit/steps/vectors.py
- src/rb_semkit/steps/coverage_meaning.py
- src/rb_semkit/steps/adgroups.py
- src/rb_semkit/core/adgroups/functions.py
- src/rb_semkit/commands/models.py
- docs/plans/vectors.md
- tests/snapshots/
- tests/conftest.py
- src/rb_semkit/data/SKILL.md
test_paths:
- tests/vectors/
docs:
- docs/plans/vectors.md
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

The model threshold in models.toml is one number for two jobs: two phrases of one intent (pairs: dupes meaning, nearest) and the clusters of cluster-meaning. For e5-small 0.97 is the best F1 on the labelled pairs, but on the clusters of the sofa core it joins phrases of different intent («диван кровать» with «купить диван»). At 0.975 the sofa core gives 539 clusters, the largest 33, with no such mix; 0.98 splits one intent apart. Add a separate default for clusters: cluster_threshold of a model, 0.975 for e5-small; a model without it uses its threshold. cluster-meaning (and the steps that cluster by meaning) take cluster_threshold when --threshold is not given; the pair steps keep threshold 0.97. The help of the cluster steps says which default they use.

## Acceptance

- Given the sofa core fixture and e5-small, When cluster-meaning runs without --threshold, Then it uses 0.975 and «диван кровать» and «купить диван» are in different clusters [check: tests/vectors/test_quality.py]
- Given e5-small, When dupes --kind meaning or nearest runs without --threshold, Then the threshold is 0.97 as before [check: tests/vectors/]
- Given a model with no cluster_threshold (bge-m3, hf:<id> with a threshold given), When cluster-meaning runs, Then it uses the model threshold [check: tests/vectors/]
- Given --threshold 0.9, When cluster-meaning runs, Then 0.9 is used [check: tests/vectors/]

## How to test

Unit tests of the registry; the quality test on the sofa core with the real e5-small where the existing quality tests run it.

## Basis

docs/plans/vectors.md (thresholds); my check of 0.97 / 0.975 / 0.98 on the sofa core.

## Read first

- `src/rb_semkit/data/vectors/models.toml`
- `src/rb_semkit/core/vectors/registry.py`

## Out of scope

- the pair threshold of any model

## Feedback

### Attempt 1: checks failed

- `uv run pytest` (exit 1)

```
hare/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:453: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x12ced0c70>
  @classmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:453: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x12dd6c8b0>
  @classmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:453: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x129bc84f0>
  @classmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:453: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x12ca96890>
  @classmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:453: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x12c6c64d0>
  @classmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/.local/share/uv/python/cpython-3.14.3-macos-aarch64-none/lib/python3.14/collections/__init__.py:453: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x12deb9210>
  @classmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/bolandau/Work/tools/semkit.worktrees/SEMKIT-047/.venv/lib/python3.14/site-packages/_pytest/unraisableexception.py:33: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1301f6a70>
  gc.collect()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
```
