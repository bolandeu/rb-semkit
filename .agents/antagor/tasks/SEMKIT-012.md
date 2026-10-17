---
id: SEMKIT-012
title: 'Morphology block: declension of nouns, adjectives and full names, irrelevant
  words, the pymorphy fallback, ready patterns and prepositional complements'
status: queue
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
- src/rb_semkit/core/declension/
- src/rb_semkit/core/patterns/
- src/rb_semkit/core/morph/lemmatizer.py
- src/rb_semkit/core/morph/functions.py
- src/rb_semkit/data/declension/
- scripts/build_parts/declension.py
- scripts/bench_parts/declension.py
- tests/conformance/cases/declension/
- tests/conformance/cases/patterns/
- tests/conformance/areas/declension.py
- tests/conformance/data_manifest/declension.json
- README.md
- scripts/build_data.toml
- scripts/build_parts/morph.py
test_paths:
- tests/declension/
- tests/patterns/
- tests/core/test_build_data.py
docs:
- docs/vba/deviations/declension.md
- docs/vba/deviations/patterns.md
- docs/vba/conformance/declension.md
- docs/vba/conformance/patterns.md
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on:
- SEMKIT-010
budget_usd: null
epic: E-002
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'Блок морфологии и шаблонов: склонение сущ. (12 форм), прил. (16), ФИО
  (5 падежей) и «всё что склоняется» на таблицах надстройки в данных пакета; нерелевантные
  слова без изменения входа; fallback pymorphy3 в лемматизаторе по параметру; готовые
  шаблоны (домены, e-mail, телефоны, даты), предлоги в конце фраз, предложные дополнения.
  Сломанное в надстройке — как задумано, отходы в документах областей.'
---

Declension, the morphology-based minus-words and the remaining text patterns, as Python functions on a phrase column (the v1 frame). The algorithms come from docs/vba/analysis.md (§2, §3, §9, §12) and docs/vba/matchers.md, and work as intended where the add-in is broken.

Areas «declension» and «patterns»:
- decline nouns (12 forms), adjectives (16 forms, every gender and the plural), full names (5 cases), and «everything that declines» in a phrase; on the add-in's tables bundled into the package data in a fast format, with the area's data manifest;
- irrelevant words: for a main word, the candidates that stand before a case preposition and a form of the main word, with their counts and examples; the input column is never changed;
- the lemmatizer gets an opt-in fallback: lemmatize(..., fallback='pymorphy') gives the pymorphy3 lemma to a word missing from the bundled dictionary; by default nothing changes;
- text patterns: ready patterns (domains, e-mails, RU phones, dates DDMMYYYY / YYYYMMDD) for find/remove/extract; phrase-end prepositions and buy markers (remove, until the last word is clean); prepositional complements («в москве», «для детей») for extract.

The add-in's defects are fixed (record each in the area deviations document, with how the add-in did it and why): the consonant fallback of nouns (the add-in gives «ди» for «диван»), the part-of-speech skip in «everything that declines» (the add-in declines verbs: «купити»), the full-name accusative (the add-in gives the dative), the apostrophe in names in -ий, neuter adjectives in the oblique cases, the irrelevant-words search changing the input, the phrase-end preposition list (Latin «o» in «пo», the junk «g»). Docstrings describe the behaviour in user terms, never the VBA (ADR 0006).

## Acceptance

- Given «диван», «парк», «книга», When declined to the genitive singular, Then «дивана», «парка», «книги»; given «диван», Then the genitive plural is «диванов» [check: tests/declension/test_nouns.py]
- Given «купить красный диван», When everything that declines goes to the genitive, Then «купить красного дивана» (the verb stays) [check: tests/declension/test_phrase.py]
- Given «красный», When declined, Then the masculine genitive «красного», the feminine accusative «красную», the neuter genitive «красного», the plural genitive «красных» [check: tests/declension/test_adjectives.py]
- Given «Иванов Сергей Петрович» and «Петрова Анна Ивановна», When declined, Then the genitive «Иванова Сергея Петровича» and the accusative «Петрову Анну Ивановну»; given «Толстой Дмитрий Ильич», Then the genitive has no apostrophe: «Толстого Дмитрия Ильича»; a value that is not three words gives InvalidArguments naming the argument [check: tests/declension/test_full_names.py]
- Given the phrases «чехол для телефона», «чехол на телефон» and the main word «телефон», When irrelevant words run, Then the table has «чехол» with 2 uses and its examples, and the input column is unchanged [check: tests/declension/test_irrelevant.py]
- Given a word missing from the bundled dictionary, When lemmatize runs with fallback='pymorphy', Then it gets the pymorphy3 lemma; without the fallback it stays as it is; an unknown fallback name gives InvalidArguments [check: tests/declension/test_pymorphy_fallback.py]
- Given «пишите на info@site.ru до 01022024», When the e-mail and date patterns extract, Then «info@site.ru» and «01022024»; given «диван в и», When the phrase-end prepositions are removed, Then «диван»; given «диван для детей с доставкой», When the complements extract, Then «для детей, с доставкой» [check: tests/patterns/test_patterns.py]
- Given each function of the two areas, When their conformance cases run, Then each has a case file with at least 5 rows and all pass, and the area reports equal the script output [check: tests/declension/test_conformance.py]
- Given 1M phrases, When everything that declines runs, Then it fits its benchmark budget [check: tests/declension/test_bench_part.py]

## How to test

Public library seam (import rb_semkit as sk), pytest per function group plus the conformance case files of the two areas.

## Basis

docs/vba/analysis.md §1.5, §2, §3, §9, §12 and docs/vba/matchers.md (phrase-end prepositions, complements); the v1 lemmatizer and the matcher frame; the per-area parts of SEMKIT-010; ADR 0005, ADR 0006.

## Read first

- `docs/vba/analysis.md`
- `docs/vba/matchers.md`
- `docs/adr/0005-port-vba-fix-defects.md`
- `docs/adr/0006-vba-is-a-porting-source.md`

## Out of scope

- The change block and the analysis block (other area tasks).
- Changing the bundled lemma dictionary.

## Feedback

### Answer to finding #1

> SEMKIT-012, lemmatize fallback: the epic E-002 says «by default the word stays as it is, as in the add-in», but the v1 default (ADR 0003) already asks pymorphy3 for a word its dictionary knows («лайфхаками» → «лайфхак», case lemmatize-unknown-pymorphy). The task says «by default nothing changes», so I kept the v1 default; fallback='pymorphy' adds the pymorphy3 guess for a word unknown to both dictionaries («тиктокерами» → «тиктокер»). If the default must be the add-in's (the word as it is), that is a change of ADR 0003 and of the morph cases: a separate task.

Keep the v1 default (ADR 0003: pymorphy3 for a word the bundled dictionary does not know) — better lemmas than the add-in's word-as-is; fallback='pymorphy' as you did. The epic line «the word stays as it is» is outdated by ADR 0003; no separate task.

### Attempt 1: file docstring

- update the docstring of src/rb_semkit/core/morph/functions.py: +word_by_word
