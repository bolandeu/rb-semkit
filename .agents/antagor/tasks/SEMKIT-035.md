---
id: SEMKIT-035
title: 'dupes --kind meaning: duplicates by meaning with non-refining words, synonyms
  and the home city'
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
- src/rb_semkit/core/dupes/
- src/rb_semkit/steps/dupes.py
- src/rb_semkit/data/wordlists/meaning/
- src/rb_semkit/data/wordlists/manifest.toml
- scripts/build_parts/wordlists.py
- src/rb_semkit/core/lists/functions.py
test_paths:
- tests/dupes/
- tests/wordlists/
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
translation: 'dupes --kind meaning: дубли по смыслу с неуточняющими словами, синонимами
  и домашним городом.


  Дубль, если векторы близки по порогу и фразы различаются только неуточняющими словами
  (встроенный @meaning/neutral + список Человека через --neutral, по леммам), синонимами
  (--synonyms, файл формата шага synonyms), формой, порядком слов или домашним городом
  (--home). Уточнение (тип, размер, материал, комната, бренд, другой город) — другой
  интент, не дубль. Колонка сходства: оставленная фраза и косинус. --action как раньше.
  Старые виды не меняются.


  Приёмка: «купить диван недорого москва» ~ «диван купить в москве» с --home москва
  — дубль; «угловой»/«прямой» — нет; «москва»/«саратов» — нет, «диван»/«диван москва»
  — только с --home; софа ~ диван — только с --synonyms; слово из списка Человека
  — нейтрально; drop и mark_all; неизвестный список и --threshold -0.1 — код 2; старые
  виды без изменений; @meaning/neutral виден в semkit lists.


  Вне: синонимы слов (второй эпик), другие шаги по смыслу.'
---

The Human runs dupes --kind meaning on a core and gets duplicates by meaning (CONTEXT: Duplicate, Non-refining word, Intent): two phrases are duplicates when their vectors are close by --threshold (the default of the model) and the words that differ between them are only non-refining words, synonyms, another form of a word, another word order, or the home city. A refinement (type, mechanism, size, material, room, brand, used, another city) makes another intent, so «угловой диван» and «прямой диван» or «диван москва» and «диван саратов» are never duplicates, however close their vectors.

- The non-refining words are the bundled list @meaning/neutral (commercial words: недорого, дешево, распродажа, акция, от производителя, с доставкой, цена, цены, купить, заказать, интернет магазин, каталог, фото, ...), plus the Human list given by --neutral (a list name or a file, as other steps take lists); words are compared by lemma.
- --synonyms takes a file of word and synonyms (the format the synonyms step gives); a word and its synonym count as the same word.
- --home NAME names the home city: the city word is non-refining for that city only.
- The step adds a similarity column next to the dupes column: for a duplicate, the phrase kept (the first of its group, by the existing action rules) and the cosine to it; --action keeps its existing meaning (mark_except_first, mark_all, drop; drop keeps the first row of each group as for the other kinds).
- The existing kinds (exact, explicit, implicit, lemmas) do not change.
- It uses the base of the vectors (the model registry, the encoder, the index, --model and --threshold, the deterministic test encoder of the tests) and adds nothing to it.

## Acceptance

- Given the test encoder that puts «купить диван недорого москва» and «диван купить в москве» close, When dupes --kind meaning --home москва runs, Then the second is marked a duplicate of the first and the similarity column names the first and the cosine [check: tests/dupes/test_dupes_meaning.py]
- Given «угловой диван» and «прямой диван» with vectors closer than the threshold, When dupes --kind meaning runs, Then neither is marked, because угловой and прямой are not non-refining words [check: tests/dupes/test_dupes_meaning.py]
- Given «диван москва» and «диван саратов» close, When dupes --kind meaning --home москва runs, Then neither is marked; given «диван» and «диван москва», Then the second is a duplicate with --home москва and not without --home [check: tests/dupes/test_dupes_meaning.py]
- Given «софа угловая» and «угловой диван» close and a synonyms file with диван ~ софа, When dupes --kind meaning --synonyms runs, Then they are duplicates; without --synonyms they are not [check: tests/dupes/test_dupes_meaning.py]
- Given a Human list with the word «новинка», When dupes --kind meaning --neutral <list> runs, Then «диван новинка» and «диван» are duplicates, and the bundled words still count [check: tests/dupes/test_dupes_meaning.py]
- Given dupes --kind meaning --action drop, When the pipeline runs, Then only the first row of each group is kept; with mark_all every row of a group is marked [check: tests/dupes/test_dupes_meaning.py]
- Given --neutral naming a list that does not exist, When the step runs, Then it is refused with exit 2 naming the flag and the list; given --threshold -0.1, Then exit 2 names the step and the flag [check: tests/dupes/test_dupes_meaning.py]
- Given dupes --kind lemmas and the other existing kinds, When they run as before, Then their output does not change [check: tests/dupes/test_dupes.py]
- Given the bundled lists, When semkit lists shows them, Then @meaning/neutral is there with its Russian description [check: tests/wordlists/test_resolve.py]

## How to test

Integration through the semkit CLI (the pipeline test runner): semkit read IN dupes --kind meaning ... write OUT, with the deterministic test encoder of the base (fixed vectors for the phrases of each case). Small fixtures in the test module.

## Basis

The existing dupes kinds and their action rules; the lemmatizer for word comparison; the bundled word lists and their manifest; the reading of a synonyms file by the synonyms step; the base of the vectors task this depends on.

## Read first

- `src/rb_semkit/core/dupes/functions.py`
- `src/rb_semkit/steps/dupes.py`
- `docs/plans/vectors.md`
- `CONTEXT.md`

## Out of scope

- synonym candidates for words (the second vectors epic)
- cluster-meaning, off-topic, classify-queries, assign-pages
- changes to the existing dupes kinds
