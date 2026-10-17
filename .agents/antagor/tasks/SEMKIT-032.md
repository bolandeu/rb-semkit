---
id: SEMKIT-032
title: 'Change functions on real phrases: match types with operators, a reversible
  translit, toponyms, phonetic, replace-words, UTM'
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
- src/rb_semkit/core/change
- src/rb_semkit/data/change
- scripts/build_parts/change.py
- docs/vba/deviations/change.md
test_paths:
- tests/change
- tests/conformance/cases/change
docs:
- docs/vba/deviations/change.md
tools: []
worker_args: null
class: standard
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
translation: '**Функции изменения на реальных фразах.** match_type не дублирует кавычки
  и скобки и не клеит операторы к ним (валидный синтаксис Директа); translit ru обращает
  en (ЖУК, Цой, Чайка, щука); топонимы с дефисом и перед пунктуацией; phonetic IKEA
  → ИКЕА; replace_words с пунктуацией у слова; extract_utm/remove_utm одинаково понимают
  #фрагмент; switch_layout туда-обратно; split_digits не рвёт 140х200.'
---

The end-to-end check (docs/plans/e2e-quality.md, items 23-26) found the change functions give wrong results on real phrases. Fix the library behaviour. Do not change the public docstrings: SEMKIT-033 updates them and the help snapshots after this task; when your fix changes a rule a docstring states, report it as an inbox finding (the function and the new rule).

match_type: a phrase that already has quotes, brackets or operators is not wrapped again and no operator is glued to a quote or a bracket: «"купить диван" -бесплатно» plus_every_word → «"+купить +диван" -бесплатно»; «[диван в икеа] -бу» brackets → «[диван в икеа] -бу»; quotes of a quoted phrase stay one pair; fixed_forms gives «"!купить !диван"», «[!диван !в !икеа] -бу». The result is valid Yandex Direct syntax.

translit: ru reverses en for the add-in's table: ЖУК → ZHUK → ЖУК, ЖКХ → ZHKKH → ЖКХ, Цой → Tsoy → Цой, Чайка → Chayka → Чайка, щука → shchuka → щука, съёмный → syomnyy → съёмный where the table makes it unambiguous; the cases that cannot reverse (ь, ъ) are stated in the deviations document.

change_case toponyms: a hyphenated name (ростов-на-дону → Ростов-на-Дону) and a name before punctuation (в москве. → в Москве.) are capitalised.

phonetic: IKEA → ИКЕА.

replace_words: a word with punctuation attached is replaced, the punctuation kept (машинка, → машина,).

extract_utm and remove_utm agree: a tag in the #fragment is no UTM tag for both (extract gives '', remove keeps the fragment as is).

switch_layout: en → ru → en is a round trip for the punctuation of the Russian layout (б ю ж э . , ; ' and their capitals).

split_digits: a size NxM (140х200, 140x200) stays whole by default.

## Acceptance

- Given «"купить диван" -бесплатно» and «[диван в икеа] -бу», When match_type runs with plus_every_word, brackets, quotes and fixed_forms, Then «"+купить +диван" -бесплатно», «[+диван +в +икеа] -бу», «[диван в икеа] -бу», «"купить диван" -бесплатно», «"!купить !диван" -бесплатно» — no doubled quote or bracket, no operator before a quote or a bracket [check: tests/conformance/cases/change]
- Given ЖУК, ЖКХ, Цой, Чайка, щука, When translit en then translit ru run, Then ЖУК, ЖКХ, Цой, Чайка, щука [check: tests/change]
- Given «диван ростов-на-дону» and «купить диван в москве. отзывы!», When change_case toponyms runs, Then «диван Ростов-на-Дону» and «купить диван в Москве. отзывы!» [check: tests/conformance/cases/change]
- Given IKEA, When phonetic runs, Then ИКЕА [check: tests/conformance/cases/change]
- Given «швейная машинка, дешево» and pairs машинка→машина, дешево→недорого, When replace_words runs, Then «швейная машина, недорого» [check: tests/conformance/cases/change]
- Given https://site.ru/?utm_source=vk#utm_medium=x, When extract_utm medium and remove_utm run, Then '' and https://site.ru/#utm_medium=x [check: tests/change]
- Given «Хрущёвка, «ж»: Б. ю?», When switch_layout en then ru run, Then the text comes back as it was [check: tests/change]
- Given «диван 140х200 ps5», When split_digits runs, Then «диван 140х200 ps 5» [check: tests/conformance/cases/change]

## How to test

Unit through the library (import rb_semkit as sk) and the conformance case files of the change area

## Basis

ADR 0005: follow the add-in, fix explicit defects, record each deviation in docs/vba/deviations/change.md with the rule and why

## Read first

- `docs/plans/e2e-quality.md`
- `docs/vba/deviations/change.md`
- `tests/conformance/case_files.py`

## Out of scope

- The step help, its snapshots, the docstrings and the guide: SEMKIT-033
- Other areas' functions
