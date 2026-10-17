---
id: SEMKIT-030
title: 'Morphology on a real core: correct lemmas, the accusative, plurals, compounds,
  adjectives, full names, word forms'
status: in_review
attempts: 2
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
- src/rb_semkit/core/morph
- src/rb_semkit/core/declension
- src/rb_semkit/core/patterns
- src/rb_semkit/data/morph
- src/rb_semkit/data/declension
- scripts/build_parts/morph.py
- scripts/build_parts/declension.py
- docs/adr/0003-morphology-engines.md
- docs/vba/deviations/declension.md
- docs/vba/deviations/patterns.md
- docs/vba/deviations/morph.md
- docs/vba/conformance/change.md
- docs/vba/conformance/declension.md
- docs/vba/conformance/morph.md
- docs/vba/conformance/patterns.md
- docs/vba/deviations/change.md
- scripts/build_parts/declension.toml
- scripts/build_parts/morph.toml
- src/rb_semkit/core/change/word_order.py
- src/rb_semkit/steps/morph.py
test_paths:
- tests/declension
- tests/patterns
- tests/core/test_morph.py
- tests/core/test_wordforms_vba.py
- tests/conformance/cases/morph
- tests/conformance/cases/declension
- tests/conformance/cases/patterns
- tests/conformance/cases/change/fix_word_order.tsv
- tests/conformance/data_manifest/declension.json
- tests/conformance/data_manifest/morph.json
- tests/core/test_build_data.py
- tests/steps/test_steps.py
docs:
- docs/adr/0003-morphology-engines.md
- docs/vba/deviations/declension.md
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-004
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**Морфология на реальном ядре.** Исправить леммы (кафе, мини, ширина,
  временного…), винительный неодушевлённых (купить кожаный диван), склонение множественного
  числа (угловых диванов), составных (дивана-кровати), прилагательных (большой скидки,
  синее, третья), существительных во мн. (стулья, люди), ФИО (Белых не склоняется,
  Глинки, Королёвой, Романа), словоформы без входного слова, код части речи для неизвестного
  слова, дополнения без лишних слов. Каждое слово — кейс сверки; правило лемм — в
  ADR 0003. Справку и снимки не трогать.'
---

The end-to-end check (docs/plans/e2e-quality.md, items 1-11) found the morphology gives wrong Russian on a real sofa core and a customs core. Fix the library behaviour so the words below come out right; each fixed word is a conformance case of its area (expected = the correct form, the add-in's value in vba, the rule and why per ADR 0005). Do not change the docstrings of the public sk functions (the step help is made from them): SEMKIT-033 updates them and the help snapshots after this task; when your fix changes a rule a docstring states, report it as an inbox finding (the function and the new rule). Module (file) docstrings are not frozen: keep each one naming what its file holds, new helpers too (the project's file docstring check). Behaviour only.

Lemmatizer: the bundled dictionary answers first and gives wrong lemmas that pymorphy3 gets right. Correct them (a correction of the dictionary data or a rule for when pymorphy3 wins; record the rule in ADR 0003): кафе, купе, мини, ширина, шириной, спину, экокожа, подростка, аскона, ножках, петушках, донецке, вещей, временного (склад временного хранения), рус; раскладывающийся / раскладывается keep their own lemmas; a lemma has no ё where the word has none (вперед).

Declension of phrases: accusative of an inanimate noun is its nominative and the adjective agrees (купить кожаный диван, угловой диван, красный диван); an animate one keeps the genitive form (купить кота); a plural phrase declines in the plural (угловые диваны → угловых диванов, дизайнерские диваны → дизайнерскими диванами); the first part of a hyphenated noun compound declines (диван-кровать → дивана-кровати, диваном-кроватью); a feminine adjective in -ая after ш ж ч щ к г х (большая скидка → большой скидки); an adjective with не- (нераскладной диван → нераскладном диване). decline-adjective: синий neuter синее, третий feminine третья, plural accusative третьи, лисий plural лисьи. decline-noun plural: стул → стулья, человек → люди / людей; мебель has no plural. Full names: Белых and Черных stay, Глинка → Глинки, Королёва → Королёвой, accusative Абрамовича Романа Аркадьевича, instrumental Абрамовичем; a row that is not three words stays as it is and the run goes on.

Word forms: the input word is not repeated (as the help says); an unknown word or a phrase gives an empty result, not an error about a text column. Part of speech: an unknown word gets a code (not an empty one, no double spaces). Complements: extract-complements stops at the complement (в москве недорого распродажа → в москве; от производителя распродажа → от производителя), fix-word-order follows. remove-phrase-end buy_markers leaves no hanging preposition (диван с доставкой купить дешево → диван с доставкой).

ADR 0003: the declension has no modes auto / table / pymorphy in the code. Correct the ADR to the rule as it is after this task: the add-in tables decline; pymorphy3 gives the animacy of the accusative and declines a hyphenated noun; no modes.

More table defects of the same kind as «третий» (one line each in the declension build): «второй» feminine nominative «вторая», masculine accusative «второй» (inanimate), plural accusative «вторые»; «голубой» and «рябой» dative «голубому» / «рябому», plural genitive «голубых» / «рябых».

## Acceptance

- Given второй (feminine nominative, masculine accusative, plural accusative), голубой and рябой (dative, plural genitive), When decline-adjective runs, Then вторая, второй, вторые, голубому, рябому, голубых, рябых [check: tests/conformance/cases/declension]
- Given the words кафе, купе, мини, ширина, шириной, спину, экокожа, подростка, аскона, ножках, петушках, донецке, вещей, временного, рус, вперед, When sk.lemmatize runs, Then the lemmas are кафе, купе, мини, ширина, ширина, спина, экокожа, подросток, аскона, ножка, петушки, донецк, вещь, временный, рус, вперед [check: tests/conformance/cases/morph]
- Given раскладывающийся and раскладывается, When lemmatized, Then each keeps its own lemma (раскладывающийся, раскладываться) [check: tests/conformance/cases/morph]
- Given купить кожаный диван, угловой диван, купить кота, When sk.decline runs to the accusative, Then купить кожаный диван, угловой диван, купить кота [check: tests/conformance/cases/declension]
- Given угловые диваны and дизайнерские диваны, When declined to the genitive and the instrumental, Then угловых диванов, угловыми диванами, дизайнерских диванов, дизайнерскими диванами [check: tests/conformance/cases/declension]
- Given диван-кровать угловой, большая скидка, нераскладной диван, When declined to the genitive and the prepositional, Then дивана-кровати углового, большой скидки, нераскладного дивана, and диване-кровати угловом, большой скидке, нераскладном диване [check: tests/conformance/cases/declension]
- Given синий (neuter nominative), третий (feminine nominative, plural accusative), лисий (plural nominative), стул and человек (plural nominative), When decline-adjective / decline-noun run, Then синее, третья, третьи, лисьи, стулья, люди [check: tests/conformance/cases/declension]
- Given Белых Никита Юрьевич, Глинка Михаил Иванович, Королёва Наталья Кузьминична, Абрамович Роман Аркадьевич, Мамедов Эльчин Гусейн оглы, When sk.decline_full_name runs (genitive, accusative, instrumental), Then Белых Никиты Юрьевича, Глинки Михаила Ивановича, Королёвой Натальи Кузьминичны, Абрамовича Романа Аркадьевича, Абрамовичем Романом Аркадьевичем, and the five-word name stays as it is without an error [check: tests/declension]
- Given the word диван and the unknown word тиктокер, When sk.wordforms runs, Then диван is not among its forms and тиктокер gives an empty result [check: tests/core/test_wordforms_vba.py]
- Given диван клик кляк купить, When part of speech runs, Then every word has a code and the result has no double spaces [check: tests/conformance/cases/morph]
- Given купить диван в москве недорого распродажа and диван от производителя распродажа, When extract-complements runs, Then в москве and от производителя; Given диван с доставкой купить дешево, When remove-phrase-end buy_markers runs, Then диван с доставкой [check: tests/conformance/cases/patterns]

## How to test

Unit through the library (import rb_semkit as sk) and the conformance case files of morph, declension and patterns; the e2e words of docs/plans/e2e-quality.md as the data

## Basis

ADR 0003 (dictionary, pymorphy3, tables), ADR 0005 (follow the add-in, fix explicit defects, record the deviation); the conformance case format of tests/conformance/case_files.py

## Read first

- `docs/plans/e2e-quality.md`
- `docs/adr/0003-morphology-engines.md`
- `docs/adr/0005-port-vba-fix-defects.md`
- `tests/conformance/case_files.py`

## Out of scope

- A new morphology engine (mystem, a model)
- The step help, its snapshots, the docstrings and the guide: SEMKIT-033

## Feedback

### Attempt 1: file docstring

- update the docstring of src/rb_semkit/core/morph/lemmatizer.py: +noun_parse
- update the docstring of src/rb_semkit/core/patterns/complements.py: +complement_end

### Answer to finding #1

> SEMKIT-030 changed rules that public docstrings state (for SEMKIT-033): (1) decline_noun: the accusative is no longer from the tables only; an inanimate noun takes its nominative («диван» → «диван»), an animate one its genitive («кот» → «кота»), a singular in -а/-я the table form («книгу»); a hyphenated noun declines whole by pymorphy3 («диваном-кроватью»). The docstring still says «диван» → «дивана». (2) decline: a nominative plural phrase declines in the plural («угловые диваны» → «угловых диванов»); a feminine, neuter or plural adjective declines from its lemma («большая скидка» → «большой скидки»); the accusative agrees by animacy («купить кожаный диван», «рыжего кота»). (3) decline_full_name: a value that is not three words stays as it is (no InvalidArguments); surnames in -ых/-их stay; a man's surname in -а/-я declines («Глинки»). (4) part_of_speech and SemtoolsLemmatizer: a word with no part of speech gets the code «unkn», not «»; a не- noun of the dictionary whose rest is an adjective is «a». (5) complements and fix_word_order step 1: a complement ends at its first noun and the oblique nouns and adjectives right after it, not at the last noun among the next five. (6) phrase_end buy_markers: a marker right after a preposition stays («диван с доставкой купить» → «диван с доставкой»).

Goes into SEMKIT-033's body.

### Answer to finding #2

> ADR 0003 says declension has the modes auto / table / pymorphy (auto: pymorphy3 when it knows the word). The code has no such mode: decline, decline_noun and decline_adjective use the add-in tables only; SEMKIT-030 added pymorphy3 only for animacy and hyphenated nouns. Decide: implement the modes, or correct ADR 0003.

Correct ADR 0003 to the code: tables decline, pymorphy3 for animacy and hyphenated nouns, no modes; in this task's body now.

### Answer to finding #3

> Declension tables (sheet abc, adjective_exceptions) have more defects of the kind SEMKIT-030 fixed for «третий», not taken (out of the task): «второй» feminine nominative «вторые» and animate accusatives «второго» / «вторых»; «голубой» and «рябой» dative «голубого» / «рябого» and plural genitive «голубыъ» / «рябыъ». A fix is a line each in scripts/build_parts/declension.toml.

Taken into this task: one line each, acceptance added.
