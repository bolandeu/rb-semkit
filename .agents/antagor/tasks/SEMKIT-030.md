---
id: SEMKIT-030
title: 'Morphology on a real core: correct lemmas, the accusative, plurals, compounds,
  adjectives, full names, word forms'
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
test_paths:
- tests/declension
- tests/patterns
- tests/core/test_morph.py
- tests/core/test_wordforms_vba.py
- tests/conformance/cases/morph
- tests/conformance/cases/declension
- tests/conformance/cases/patterns
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

The end-to-end check (docs/plans/e2e-quality.md, items 1-11) found the morphology gives wrong Russian on a real sofa core and a customs core. Fix the library behaviour so the words below come out right; each fixed word is a conformance case of its area (expected = the correct form, the add-in's value in vba, the rule and why per ADR 0005). Do not change the public docstrings: SEMKIT-033 updates them and the help snapshots after this task; when your fix changes a rule a docstring states, report it as an inbox finding (the function and the new rule). Behaviour only.

Lemmatizer: the bundled dictionary answers first and gives wrong lemmas that pymorphy3 gets right. Correct them (a correction of the dictionary data or a rule for when pymorphy3 wins; record the rule in ADR 0003): кафе, купе, мини, ширина, шириной, спину, экокожа, подростка, аскона, ножках, петушках, донецке, вещей, временного (склад временного хранения), рус; раскладывающийся / раскладывается keep their own lemmas; a lemma has no ё where the word has none (вперед).

Declension of phrases: accusative of an inanimate noun is its nominative and the adjective agrees (купить кожаный диван, угловой диван, красный диван); an animate one keeps the genitive form (купить кота); a plural phrase declines in the plural (угловые диваны → угловых диванов, дизайнерские диваны → дизайнерскими диванами); the first part of a hyphenated noun compound declines (диван-кровать → дивана-кровати, диваном-кроватью); a feminine adjective in -ая after ш ж ч щ к г х (большая скидка → большой скидки); an adjective with не- (нераскладной диван → нераскладном диване). decline-adjective: синий neuter синее, третий feminine третья, plural accusative третьи, лисий plural лисьи. decline-noun plural: стул → стулья, человек → люди / людей; мебель has no plural. Full names: Белых and Черных stay, Глинка → Глинки, Королёва → Королёвой, accusative Абрамовича Романа Аркадьевича, instrumental Абрамовичем; a row that is not three words stays as it is and the run goes on.

Word forms: the input word is not repeated (as the help says); an unknown word or a phrase gives an empty result, not an error about a text column. Part of speech: an unknown word gets a code (not an empty one, no double spaces). Complements: extract-complements stops at the complement (в москве недорого распродажа → в москве; от производителя распродажа → от производителя), fix-word-order follows. remove-phrase-end buy_markers leaves no hanging preposition (диван с доставкой купить дешево → диван с доставкой).

## Acceptance

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
