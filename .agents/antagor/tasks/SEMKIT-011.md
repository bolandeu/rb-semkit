---
id: SEMKIT-011
title: 'Change block: every text change of the add-in (case, insert, replace, translit,
  ЧПУ, match types, UTM, hashes, word order, phonetic)'
status: publish
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

### Attempt 1: the Architect's verdict

The review found blockers; close each:

- [blocker] C11 tests/core/test_build_data.py: `BUILT_FILES` (line ~19) lists the built files of morph, text and declension, but not `change/translit.json` and `change/word_order.json`. The byte-identity test (`test_two_runs_are_byte_identical_and_match_the_package`) therefore never checks the change data against a rebuild. The file is in the owned paths, but the diff left it as it was (the feedback says the edit was blocked by `scope_held`, holder SEMKIT-012). The Architect must release the scope or add the two lines.
- [blocker] C11 tests/markers/test_build_markers.py:120: the task rewrote `test_gitattributes_marks_all_built_data_as_generated` to compare `.gitattributes` with every `scripts/build_parts/*.py`. After the merge of main, `build_parts/declension.py` exists and `.gitattributes` has no `src/rb_semkit/data/declension/**` line. I ran `uv run pytest -q`: 1 failed, 2554 passed; the failed test is this one («Extra items in the right set: 'src/rb_semkit/data/declension/**'»). The suite is red at the merge commit. Fix: add the declension line to `.gitattributes` (SEMKIT-012 data; needs the scope), or keep the old fixed set plus `change`.
- [blocker] [wrong] The built data of the area is not under the byte-identity check of the build, so «the area's data manifest» can drift from the files without a red test — «The tables these functions use (…) are built into the package data of the area in a fast format, with the area's data manifest.» (same cause as the first Standards blocker.)

Minor remarks of the review: optional, if they do not widen the task:

- [minor] C3 src/rb_semkit/core/change/replace.py: `_class_case` repeats the idea of `common.adjusted` (text in the case class of another text). The two differ only a little (upper first, capitalised only by the first letter). One helper with a flag would be enough.
- [minor] C7 src/rb_semkit/core/change/word_order.py: `COMPLEMENT_WORDS = 5`, `FORMS` endings and `NOT_ADJECTIVES` are literals in code. `COMPLEMENT_WORDS` is a limit a user may want to change. It is documented in the docstring, so the Architect may accept it.
- [minor] .gitattributes (joined outside the slice): the `change/**` line is needed. The build part writes `data/change/`, so `linguist-generated` is right. The line changes only how files are counted, not the behaviour.
- [minor] docs/plan.md (joined outside the slice): the edit is needed (D12/D16 now built in the area, "later" removed). The new line is longer than the neighbours; style only.
- [minor] [extra] `change_case` has `sentence_lower`; `fix_word_order` has `lemmatizer=` and `complements=`; `insert` has `each_word`. The task names none of them. They come from the add-in or from ADR 0003/0005, and the deviations document explains them — «insert text before / after each word, at the start / end of the phrase». Accept.
- [minor] [wrong] The task lists the match type «exact». `match_type` has no kind of that name (`kind='exact'` is refused in `tests/change/test_errors.py`). The nearest are "fixed_forms" («!A») and "quoted_fixed_order" («"[!A]"»). The docstring should say which kind is the exact match — «match types: broad «+A», «!A», phrase «[A]» and «"A"», exact, anti-semantic».

### Answer to finding #1

> tests/core/test_build_data.py BUILT_FILES and the compact-JSON check do not list change/translit.json and change/word_order.json. SEMKIT-011 left them out because SEMKIT-012 holds the file. The manifest test there already compares change.json with the build. Add the two files when the file is free.

Taken into SEMKIT-021.
