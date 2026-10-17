---
id: SEMKIT-034
title: 'Vectors base: models pull/list/remove, the encoder, the index and cluster-meaning
  end to end'
status: publish
attempts: 2
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
- src/rb_semkit/core/vectors/
- src/rb_semkit/commands/models.py
- src/rb_semkit/steps/vectors.py
- src/rb_semkit/data/SKILL.md
- tests/conftest.py
- pyproject.toml
- src/rb_semkit/core/errors.py
- src/rb_semkit/core/models.py
- src/rb_semkit/core/version.py
- src/rb_semkit/data/vectors/models.toml
- src/rb_semkit/pipeline/state.py
- src/rb_semkit/steps/__init__.py
- uv.lock
test_paths:
- tests/vectors/
- tests/snapshots/describe.json
- tests/snapshots/help/models-list.txt
- tests/snapshots/help/models-pull.txt
- tests/snapshots/help/models-remove.txt
- tests/snapshots/help/models.txt
- tests/snapshots/help/read.txt
- tests/snapshots/help/steps/vectors/cluster-meaning.txt
- tests/steps/areas.py
- tests/steps/test_steps.py
docs:
- src/rb_semkit/data/SKILL.md
tools: []
worker_args: null
class: hard
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
translation: 'Основа векторов: models pull/list/remove, encoder, индекс и cluster-meaning
  от входа до результата.


  Тонкий сквозной путь эпика и общая основа шагов по смыслу: extra rb-semkit[vectors];
  semkit models pull/list/remove в кэш системы (ADR 0009); реестр моделей (e5-small
  по умолчанию, bge-m3, potion, hf:<id>; ревизия и сумма); интерфейс encoder; индекс
  (точный до ~300 тыс., HNSW выше, детерминированно); общие --model и --threshold,
  ошибки и пороги по умолчанию; тестовый детерминированный encoder; 200 размеченных
  пар — фикстура и тест качества (без модели — пропуск); ONNX вместо torch при совпадении
  векторов; порог кластеров подобрать на ядре «диван», образец кластеров — в отчёт;
  раздел в справке.


  Приёмка: pull с проверкой суммы, повтор ничего не качает; неудачный pull без обрывков;
  два pull сразу — одна копия; remove и отказ для нескачанного; неизвестный --model
  и --threshold 1.5 — код 2; нет модели — ошибка с командой pull; без extra — ошибка
  с командой установки, другие шаги работают; cluster-meaning: близкие вместе, одиночка
  — кластер из одной, имя по частоте или центру, повтор даёт то же; HNSW выше предела,
  видно в сводке; тест качества ROC AUC ≥ 0.93.


  Вне: dupes по смыслу, off-topic, classify-queries, assign-pages, синонимы слов,
  GPU.'
---

The thin end-to-end path of the vectors epic and the base every step by meaning shares. With the optional extra rb-semkit[vectors] installed, the Human pulls a model once (semkit models pull e5-small) into the system cache (ADR 0009), sees it in semkit models list, removes it with semkit models remove, and runs cluster-meaning in a pipeline: every phrase gets a cluster and a cluster name.

- The model registry maps short names (e5-small default, bge-m3, potion) to a Hugging Face id, a fixed revision and a checksum, and takes hf:<id> for any model.
- The encoder interface turns phrases into normalized float32 vectors in batches, with the prefix the model needs («query: » for e5).
- The vector index is exact up to about 300k phrases and HNSW above, deterministic.
- The shared options --model and --threshold, the errors (no extra, no model, unknown model, threshold out of range) and the default thresholds per model live here, so the other steps by meaning only add their logic.
- The test suite registers a small deterministic test encoder in place of the real models (an autouse fixture), so pipeline tests and step examples run without a download.
- The 200 labelled phrase pairs and the 100 word pairs (the labels folder next to the vectors plan, checked by the Human) go into the tests as a fixture; a quality test runs the real default model from the cache and is skipped, with a message, without it.
- Use ONNX runtime instead of torch when its vectors match torch (cos above 0.999 on the sofa core of the e2e fixtures): measure and state the result in the task report.
- Tune the default cluster threshold on the sofa core and put a sample of its clusters in the task report for the Human.
- A section of the guide tells how to install the extra, pull a model and run a step by meaning.

## Acceptance

- Given the vectors extra and an empty cache, When semkit models pull e5-small runs, Then the model is in the cache (or models.dir) at its fixed revision with the checksum checked, models list shows it pulled with its size, and a second pull says it is already there and downloads nothing [check: tests/vectors/test_models.py]
- Given a pull that fails (the download raises midway, or the checksum differs), When it ends, Then no partial model is in the cache, the exit is non-zero and the message names the cause and the command to retry [check: tests/vectors/test_models.py]
- Given two pulls of the same model at once, When both end, Then the cache holds one valid copy [check: tests/vectors/test_models.py]
- Given a pulled model, When semkit models remove NAME runs, Then it is gone from the cache and from models list; remove of a name not pulled is refused with exit 2 and the list of pulled models [check: tests/vectors/test_models.py]
- Given --model nosuch, When cluster-meaning runs, Then exit 2 names the short names e5-small, bge-m3, potion and the form hf:<id>; given --threshold 1.5, Then exit 2 names the step and the flag [check: tests/vectors/test_cluster_meaning.py]
- Given the model of a step not in the cache, When the pipeline runs, Then nothing is downloaded and the error gives the ready command semkit models pull NAME [check: tests/vectors/test_cluster_meaning.py]
- Given semkit without the vectors extra (its imports unavailable), When cluster-meaning or semkit models runs, Then the error names the install command of the extra, and a pipeline of other steps runs as before [check: tests/vectors/test_extra.py]
- Given the test encoder and phrases a1 a2 a3 close to each other and b far from them, When cluster-meaning --threshold runs, Then a1 a2 a3 share one cluster, b is a cluster of one, the cluster name is the most frequent phrase with --freq and the phrase nearest the centre without it; two runs give the same columns [check: tests/vectors/test_cluster_meaning.py]
- Given more phrases than the exact-search limit (the limit lowered in the test), When a step by meaning runs, Then it uses HNSW, the step summary names the index, and two runs give the same result [check: tests/vectors/test_index.py]
- Given the 200 labelled phrase pairs and e5-small in the cache, When the quality test runs, Then the ROC AUC of the cosine against the label is at least 0.93 and the default threshold of e5-small is within 0.01 of its best-F1 threshold; without the model the test is skipped with a message naming the pull command [check: tests/vectors/test_quality.py]

## How to test

Integration through the semkit CLI (the pipeline test runner): semkit models and semkit read IN cluster-meaning write OUT, with the deterministic test encoder; downloads are faked by a local source in tmp_path, the cache set by models.dir. The quality test goes through the encoder interface with the real cached model only.

## Basis

The step table (the steps package: Step and STEPS of an area module); the command group pattern of the lists command; the errors of core errors and their exit codes; platformdirs for the cache (ADR 0009); the measured choices of the vectors plan.

## Read first

- `docs/plans/vectors.md`
- `docs/adr/0009-encoder-models-downloaded-once.md`
- `docs/plans/vectors-labels/phrase_pairs.tsv`
- `src/rb_semkit/steps/dupes.py`
- `CONTEXT.md`

## Out of scope

- dupes --kind meaning, off-topic, classify-queries, assign-pages (other tasks of the epic)
- word synonyms and the second vectors epic
- GPU

## Feedback

### Attempt 1: file docstring

- update the docstring of src/rb_semkit/core/errors.py: +ModelNotPulled +PullFailed +VectorsNotInstalled
- add a docstring to src/rb_semkit/core/version.py: what it holds and why

### Attempt 2: the Architect's verdict

The review found blockers; close each:

- [blocker] C11 src/rb_semkit/data/SKILL.md:42: The `--json` envelope changed. A step summary now has an optional `note` (`state.Summary.to_dict`, `Columns.note`). Line 42 still says `steps` holds one `{"step", "rows_before", "rows_after", "cells_changed"}` per step. README.md lines 82-84 (`"steps"` in the envelope) were also not checked. The new section further down in SKILL.md names `note`, so the file now states the shape in two places and the two differ. Update the old line to show the optional `note`.

Minor remarks of the review: optional, if they do not widen the task:

- [minor] C3 src/rb_semkit/data/SKILL.md: The install command hard-codes the repository URL `https://github.com/bolandeu/rb-semkit.git`. `core/version.py` (`repository_url`) says that no module repeats a value that pyproject.toml holds. The URL is now in two places.
- [minor] C5 src/rb_semkit/steps/vectors.py: `by_meaning` opens the encoder with `Path.cwd()`. The pipeline context already has the project path (`commands/models.py` uses `ctx.obj["project"]`). A step run with `-C` or a project option may look for `models.dir` in the wrong folder.
- [minor] C5 src/rb_semkit/core/vectors/cache.py (`_place`): In the stale-copy branch, `folder.rename(stale)` followed by `temporary.rename(folder)` is not atomic. A third pull in that window can fail with an OS error, which becomes `PullFailed`. The two-pull acceptance case passes, so this is only a rare edge.
- [minor] C6 tests/vectors/fixtures/word_pairs.tsv: No test reads this file (grep over src, tests and docs). The task asks for the 100 word pairs "as a fixture", so it is not wrong. It is unused data until the word-synonym task.
- [minor] [missing] The task report (not the diff) must hold the ONNX-versus-torch cos result and the sample of sofa-core clusters. I did not find them in the diff, only the claims in `models.toml` comments ("cos above 0.999", "checked on the clusters of the sofa core"). The Architect should confirm they are in the worker's report — «Use ONNX runtime instead of torch when its vectors match torch (cos above 0.999 on the sofa core of the e2e fixtures): measure and state the result in the task report.» and «put a sample of its clusters in the task report for the Human.»
- [minor] [extra] `models remove --dry-run` and the `hf:<id>` listing of hub models were not named as acceptance points. `--dry-run` follows the project rule for irreversible actions and `hf:<id>` is in the task text, so I do not count them as scope creep.
- [minor] [wrong] `similarity` column and `attrs["index"]` of the cluster table are not in the task («every phrase gets a cluster and a cluster name»). The extra column is documented in the help, the guide and the tests, so it is small and visible — «every phrase gets a cluster and a cluster name».
