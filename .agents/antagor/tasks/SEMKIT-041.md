---
id: SEMKIT-041
title: 'synonym-candidates: RuWordNet and navec pulled as models'
status: in_progress
attempts: 0
blocked: true
blocked_reason: scope_held
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: human
worker: claude-code
type: feature
owns_paths:
- src/rb_semkit/core/word_vectors/
- src/rb_semkit/steps/word_vectors.py
- src/rb_semkit/core/vectors/
- CONTEXT.md
- pyproject.toml
- src/rb_semkit/commands/models.py
- src/rb_semkit/core/errors.py
- src/rb_semkit/data/vectors/models.toml
- src/rb_semkit/data/SKILL.md
- src/rb_semkit/steps/vectors.py
test_paths:
- tests/word_vectors/
- tests/conftest.py
- tests/snapshots/help/models-list.txt
- tests/snapshots/help/models-pull.txt
- tests/snapshots/help/models-remove.txt
- tests/snapshots/help/models.txt
- tests/snapshots/help/steps/word_vectors/synonym-candidates.txt
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
depends_on:
- SEMKIT-034
budget_usd: null
epic: E-006
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'synonym-candidates: кандидаты в синонимы из RuWordNet и navec, скачиваемых
  как модели.


  По каждому слову ядра (по леммам) — кандидаты из тезауруса и векторов слов для выбора
  Человеком; выбранные идут в --synonyms у dupes --kind meaning. Данные: semkit models
  pull ruwordnet / navec (ADR 0009). По умолчанию только кандидаты, встречающиеся
  в ядре; --all — все; --source; --top для navec. Отчёт: слово, кандидат, источник,
  оценка, есть в ядре; --as-synonyms — формат файла синонимов.


  Приёмка: диван → софа, кресло не синоним; --all; --as-synonyms читается dupes; без
  данных — команда pull, неверный --source — код 2; models list/remove для данных
  слов; тест качества на 100 парах (доли не ниже замеренных минус 0.05), без данных
  — пропуск.


  Вне: автоматический выбор синонимов, другие тезаурусы.'
---

synonym-candidates: per word of the core, synonym candidates from a thesaurus (RuWordNet) and word vectors (navec), for the Human to pick; the picked go to --synonyms of dupes --kind meaning. The word data are pulled like the encoders: semkit models pull ruwordnet and semkit models pull navec (ADR 0009: once, into the system cache, a fixed revision and a checksum; the step downloads nothing). The step works on lemmas; by default only candidates that occur in the core are given, --all gives every candidate; --source ruwordnet|navec|both (default both); --top limits the navec candidates per word. A report: word, candidate, source, score (1 for a thesaurus synonym, the cosine for navec), in core yes/no; stopwords and words with digits are skipped. The output format is the synonyms file format of the synonyms step (word and synonyms) with --as-synonyms, so a picked list goes straight to dupes --kind meaning --synonyms.

## Acceptance

- Given a core with «диван», «софа», «кресло» and both data pulled, When synonym-candidates runs, Then «диван» gets «софа» with its source and score, «кресло» is not a thesaurus synonym of «диван» [check: tests/word_vectors/test_synonym_candidates.py]
- Given --all, When the step runs, Then candidates not in the core are given with in core no; without --all they are left out [check: tests/word_vectors/test_synonym_candidates.py]
- Given --as-synonyms, When the step runs, Then the report is in the synonyms file format and dupes --kind meaning --synonyms reads it [check: tests/word_vectors/test_synonym_candidates.py]
- Given the data of a source not in the cache, When the step runs, Then nothing is downloaded and the error gives the ready semkit models pull command; --source nosuch is refused with exit 2 naming the allowed values [check: tests/word_vectors/test_synonym_candidates.py]
- Given semkit models pull ruwordnet and navec, When models list runs, Then both are shown with their size; models remove works for them as for the encoders [check: tests/word_vectors/test_models_words.py]
- Given the 100 labelled word pairs of E-005 and both data in the cache, When the quality test runs, Then the share of right proposals is at least the measured one minus 0.05 (RuWordNet 0.32, navec 0.18); without the data it is skipped with a message naming the pull command [check: tests/word_vectors/test_quality_words.py]

## How to test

Integration through the semkit CLI with small fake thesaurus and word-vector data registered by a fixture (as the test encoder of E-005); the quality test with the real cached data only.

## Basis

The model registry and the models command of E-005 (add the two word data to them); the synonyms file format of the synonyms step; the lemmatizer; the measures of the vectors plan.

## Read first

- `docs/plans/vectors.md`
- `docs/adr/0009-encoder-models-downloaded-once.md`
- `src/rb_semkit/core/corpus/synonyms.py`
- `CONTEXT.md`

## Out of scope

- choosing synonyms automatically (candidates only)
- other thesauri or languages
