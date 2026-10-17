---
id: SEMKIT-011
title: 'Change block: every text change of the add-in (case, insert, replace, translit,
  ЧПУ, match types, UTM, hashes, word order, phonetic)'
status: in_review
attempts: 0
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
- src/rb_semkit/core/change/
- src/rb_semkit/data/change/
- scripts/build_parts/change.py
- scripts/bench_parts/change.py
- tests/conformance/cases/change/
- tests/conformance/areas/change.py
- tests/conformance/data_manifest/change.json
- .gitattributes
- docs/plan.md
test_paths:
- tests/change/
- tests/markers/test_build_markers.py
- tests/core/test_build_data.py
docs:
- docs/vba/deviations/change.md
- docs/vba/conformance/change.md
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
translation: 'Блок «Изменить»: все изменения текста надстройки функциями над колонкой
  — регистр, вставка, перенос и замена, разбивка, разворот, сортировка, ёлочки, транслит,
  ЧПУ, раскладка, похожие символы, фонетика, типы соответствия, минус-слова, UTM,
  хеши, порядок слов. Решения Р3–Р5; таблицы — в данные пакета в быстром формате;
  отходы — в документе области; сверка ≥5 строк на функцию.'
---

The change block of the library: every text change of the add-in, as Python functions on a phrase column (the v1 frame: a Series or a DataFrame column in, a new column or inplace out). The algorithms come from docs/vba/change.md, improved where Python does better or the add-in is broken.

Functions (one area «change»):
- case: every word capitalised, sentence case, words with latin letters, words from a list (capitalised / upper), toponyms capitalised, abbreviations upper (BMW, RGB);
- insert text before / after each word, at the start / end of the phrase;
- move a word to the start / end; replace word → word and list → list (keep the case, or take the new one); mass replace by substring, whole phrase or regex;
- split text from digits; reverse the characters or the word order; sort the words A–Z;
- quotes → «ёлочки»; translit ru→en and en→ru; ЧПУ translit; keyboard layout switch; similar characters cyr↔lat;
- phonetic en→ru («Dreamline» → «Дримлайн»);
- match types: broad «+A», «!A», phrase «[A]» and «"A"», exact, anti-semantic; drop the modifiers on stopwords; drop the minus-words;
- UTM: remove the utm tags from a URL, extract a utm value;
- hashes md5 / sha256;
- word order fix (BK*), with the user's main word when given.

Decisions already made (record each deviation from the add-in in the area deviations document, with how the add-in did it and why):
- ЧПУ: lower case; spaces and punctuation between words become one «-»; no «-» at the edges and no double «-».
- UTM: the «utm_» prefix in any case; extract returns the value only, URL-decoded; removal keeps a valid «?» and «&».
- Word order fix: the user's main word when given (the add-in drops it by mistake); otherwise as the add-in decides.
- The add-in's broken literals (for example the keyboard layout string where «z» never becomes «я») are fixed.

The tables these functions use (translit, ЧПУ, layout, similar chars, phonetic) are built into the package data of the area in a fast format, with the area's data manifest. Docstrings describe the behaviour in user terms, never the VBA (ADR 0006).

## Acceptance

- Given «Диван-кровать 2 м!», When chpu runs, Then «divan-krovat-2-m»; given «Щётка  ёж», Then «schetka-ezh» [check: tests/change/test_translit.py]
- Given «https://site.ru/?UTM_Source=ya&utm_medium=cpc&id=5#top», When the utm tags are removed, Then «https://site.ru/?id=5#top»; When utm source is extracted from «?utm_source=%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81», Then «Яндекс» [check: tests/change/test_utm.py]
- Given «купить диван в москве», When the broad match modifier runs, Then «+купить +диван в +москве» with no modifier on the stopword, as the area deviations document says [check: tests/change/test_match_types.py]
- Given «ghbdtn vbh» and «z», When the layout switches en→ru, Then «привет мир» and «я» [check: tests/change/test_layout.py]
- Given each function of the area, When the area's conformance cases run, Then each has a case file with at least 5 rows (the add-in's value, semkit's value, rule and why where they differ), all pass, and the area report equals the script output [check: tests/change/test_conformance.py]
- Given a wrong input (no column, an unknown case kind, an empty replace list, a bad regex), When called, Then InvalidArguments names the argument and the allowed values, nothing changes [check: tests/change/test_errors.py]
- Given 1M phrases, When translit and chpu run, Then each fits its benchmark budget [check: tests/change/test_bench_part.py]

## How to test

Public library seam (import rb_semkit as sk), pytest per function group plus the conformance case files of the area.

## Basis

docs/vba/change.md (every button: handler, algorithm, quirks, examples); the v1 frame (frame.py, map_unique) and the per-area parts of SEMKIT-010; ADR 0005, ADR 0006.

## Read first

- `docs/vba/change.md`
- `docs/adr/0005-port-vba-fix-defects.md`
- `docs/adr/0006-vba-is-a-porting-source.md`
- `CONTEXT.md`

## Out of scope

- Declension, analysis and text matchers (other area tasks).
- Excel-only actions (colours, bold).

## Feedback

### Blocked: scope_held (holders ['SEMKIT-012'], paths ['tests/core/test_build_data.py'])
