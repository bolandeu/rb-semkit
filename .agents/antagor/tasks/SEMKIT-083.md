---
id: SEMKIT-083
title: 'relate-phrases Latin reading: web = веб, bosch = бош'
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
type: feature
owns_paths:
- src/rb_semkit/core/relate/sources/latin.py
- tests/relate/test_latin.py
test_paths:
- tests/relate/test_latin.py
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-081
budget_usd: null
epic: E-009
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
resident: null
tool: null
pr: null
translation: 'Чтение латиницы для relate-phrases: латинское слово читается по-русски
  через таблицу translit (ш и щ — один звук: bosch = бош, web = веб, wordpress = вордпресс)
  и связывается с кириллическим словом с тем же чтением. Источник связей может подсказывать
  другие формы слова чужим поискам.'
---

Add the Latin reading to relate-phrases: a word in Latin letters and a word in Cyrillic letters that sound the same are linked, so `web = веб`, `wordpress = вордпресс`, `bosch = бош`.

- A Latin word has a Cyrillic reading, made with the translit table en→ru of the change area (reuse it; do not change it). ш and щ are one sound: bosch reads «бощ», and it equals «бош». Words with digits, words in Cyrillic and words of other scripts have no reading.
- The link source «latin», one new module in the package of sources that SEMKIT-081 made (found by itself; do not edit the step module or any other shared file): a Latin word and a Cyrillic word are linked when the reading of the first equals the second after the same folding (щ as ш, ё as е, lower case). `reason` names it: `bosch~бош (latin)`. A Latin word that no Cyrillic word of the table matches stays an extra unit (a refinement: «ремонт iphone» at «ремонт»).
- The source gives the reading as another form of the word, so that the dictionary lookup of SEMKIT-082 finds the run «веб сайт» for «web сайт». Test it with a test source that looks a run up; the join with the real dictionary is tested in the last task of the epic.

## Acceptance

- Given the words web, wordpress, bosch, iphone, a word with digits and a Cyrillic word, When the reading is made, Then web is веб, wordpress is вордпресс, bosch equals бош (ш = щ), and a word with digits or in Cyrillic has no reading [check: tests/relate/test_latin.py]
- Given «как создать сайт на wordpress» first and then «как создать сайт на вордпресс», When the step runs, Then the second is a variation of the first with reason wordpress~вордпресс (latin) [check: tests/relate/test_latin.py]
- Given «ремонт стиральных машин бош» and «ремонт стиральных машин bosch», When the step runs, Then the bosch phrase is a variation of the бош phrase; Given «ремонт стиральных машин» first, then «ремонт стиральных машин бош», then «ремонт стиральных машин bosch», Then the third takes the variation of the second, not the refinement of the first; Given only the first and the third, Then the third is a refinement of the first (+bosch) [check: tests/relate/test_latin.py]
- Given «ремонт» and then «ремонт iphone», When the step runs, Then the second is a refinement (+iphone) [check: tests/relate/test_latin.py]
- Given a test link source that offers another form of a word, When another source looks up a run, Then it tries that form too [check: tests/relate/test_latin.py]

## How to test

level: unit tests of the reading and integration through the pipeline; seam: semkit read TABLE.jsonl relate-phrases … write -; data: small JSONL tables; no thesaurus data needed (the root conftest patches a small one in)

## Basis

Follow the translit of the change area (src/rb_semkit/core/change/chars.py) and the interface of the link sources that SEMKIT-081 made; one new module, found by itself

## Read first

- `docs/plans/relate-phrases.md`
- `src/rb_semkit/core/change/chars.py`
- `tests/conftest.py`

## Out of scope

- A Cyrillic-to-Latin direction beyond what the comparison needs; brands that read unlike they are spelled (hyundai, xiaomi): they come in --synonyms. The dictionary run lookup with the reading: the last task. A change of translit.
