---
id: SEMKIT-082
title: 'relate-phrases dictionary links: synsets, POS-synonymy and runs of words as
  units'
status: in_review
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
- src/rb_semkit/core/word_vectors/
- src/rb_semkit/steps/word_vectors.py
- tests/word_vectors/
- src/rb_semkit/core/relate/sources/dictionary.py
- tests/relate/conftest.py
- tests/relate/test_dictionary.py
- tests/relate/test_thesaurus_relations.py
- src/rb_semkit/core/relate/functions.py
- src/rb_semkit/core/relate/pairing.py
- src/rb_semkit/core/relate/phrases.py
test_paths:
- tests/relate/test_dictionary.py
- tests/relate/test_thesaurus_relations.py
- tests/conftest.py
- tests/relate/test_classes.py
- tests/relate/test_own_links.py
docs: none
tools: []
worker_args: null
class: hard
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
translation: 'Словарные связи для relate-phrases: общий synset RuWordNet или пара
  POS-synonymy (создание ~ создать, ремонт ~ отремонтировать); единица — слово или
  отрезок слов (биграмма, триграмма…), который тезаурус знает как один смысл; перебор
  всех разрезов фразы. Таблица derivation не используется. Без скачивания нового.'
---

Add the dictionary to relate-phrases: two units are linked when RuWordNet says they mean the same, in the same part of speech or in another one. This gives the variations of the epic: `создание ~ создать ~ создавать`, `разработка ~ разработать`, `ремонт ~ отремонтировать`, `сайт ~ веб-сайт ~ интернет-сайт`, `стиральная машина ~ стиралка`.

Facts of the real file (the pulled model `ruwordnet`, one SQLite file), checked by hand on 2026-10-26; the plan in docs/plans/relate-phrases.md, section 2, has the table:
- `sense(id, name, lemma, synset_id)` holds the senses; the lemma is upper case, some senses are runs of words («РЕМОНТНЫЙ РАБОТА»), some are hyphenated («ВЕБ-САЙТ»), some are glued («ВЕБСАЙТ»).
- `pos_synonymy_relation(left_id, right_id)` links two synsets of one meaning in different parts of speech (создание ~ создать, ремонт ~ отремонтировать, лечение ~ лечить). Aspect pairs usually sit in one synset (создать ~ создавать).
- `derivation_relation` links senses by derivation but is far too wide: купить ~ покупатель, закупка, подкупить; ремонт ~ ремонтник; заказ ~ заказчик. It is never read, never a link.

What to build:
- The thesaurus reader also reads the POS-synonymy pairs of the same file; what it gives today does not change.
- The link source «dictionary», one new module in the package of sources that SEMKIT-081 made (found by itself; do not edit the step module or any other shared file). Its preparing hook opens RuWordNet before the input is read (as synonym-candidates does) and refuses, with the command `semkit models pull ruwordnet`, when it is not pulled. No other download.
- Two units are linked when their lemmas belong to senses of one synset, or of two synsets that make a POS-synonymy pair (either direction). A link is one step: a link of a link is no link. A word with several senses links through any of them; `reason` names the link: `создание~создать (pos_synonymy)`, `сайт~веб-сайт (synset)`.
- Units of any length: every run of adjacent words (a bigram, a trigram, … up to the longest sense) that the thesaurus knows as one sense is a candidate unit, found by the lemmas of the words, or hyphenated, or glued («веб сайт» → веб-сайт, вебсайт). The lookup also tries the other forms of a word that other sources offer (the Latin reading). All the ways to cut a phrase into units are tried and the pairing that explains the most words wins, so a run that overlaps another one is not lost by a fixed order of cuts.

## Acceptance

- Given a test thesaurus with the synsets and POS-synonymy pairs of the real file for these words, When «создание сайтов» comes first and then «создать сайт», «создавать сайты», and «разработка сайтов» then «разработать сайт», and «ремонт стиральных машин» then «отремонтировать стиральную машину», Then each later phrase is a variation of the earlier one, and reason names the link (pos_synonymy; «создать ~ создавать» is synset) [check: tests/relate/test_dictionary.py]
- Given «разработка сайтов» then «разработка веб сайтов» and «разработка интернет сайтов», and «ремонт стиральных машин» then «ремонтные работы стиральных машин» and «ремонт стиралок», When the step runs, Then each is a variation: a bigram that the thesaurus knows as one sense is a unit, by lemmas, hyphenated or glued [check: tests/relate/test_dictionary.py]
- Given «купить диван» and then «покупатель дивана», and a thesaurus that has a derivation pair between купить and покупатель, When the step runs, Then the second is other: a derivation pair alone is not a link [check: tests/relate/test_dictionary.py]
- Given a ~ b linked and b ~ c linked but no link between a and c, When «a x» comes first and then «c x», Then the second is other: no chain of links [check: tests/relate/test_dictionary.py]
- Given a phrase in which a run known as a sense overlaps another such run, When the step compares it, Then the cut that explains the most words wins, whichever phrase the run is in [check: tests/relate/test_dictionary.py]
- Given a small SQLite file with the tables of the real file (sense, synset, pos_synonymy_relation, derivation_relation), When the thesaurus is loaded, Then the POS-synonymy pairs are read, the derivation table is not, and the synonyms it gave before are the same; Given RuWordNet not pulled, When relate-phrases runs, Then it refuses before it reads the input and names semkit models pull ruwordnet [check: tests/relate/test_thesaurus_relations.py]

## How to test

level: unit tests of the thesaurus loader on a small SQLite file, integration through the pipeline; seam: semkit read TABLE.jsonl relate-phrases … write -; data: a small test thesaurus built in tests/relate/conftest.py from the real senses of the words named in the acceptance (override the thesaurus the root conftest patches in); the real file is not used here

## Basis

Follow the Thesaurus class and the way synonym-candidates finds runs of words by lemmas (src/rb_semkit/core/word_vectors/thesaurus.py, units.py), and the interface of the link sources that SEMKIT-081 made; one new module, found by itself

## Read first

- `docs/plans/relate-phrases.md`
- `src/rb_semkit/core/word_vectors/thesaurus.py`
- `src/rb_semkit/core/word_vectors/units.py`
- `tests/conftest.py`

## Out of scope

- The Latin reading, --synonyms, speed and the 200-pair precision check: other tasks. The derivation table. DerivBase.Ru, DeriNet.RU and any new download. A change of synonym-candidates.

## Feedback

### Blocked: scope_held (holders ['SEMKIT-081'], paths ['src/rb_semkit/core/relate/functions.py', 'src/rb_semkit/core/relate/pairing.py', 'src/rb_semkit/core/relate/phrases.py', 'tests/relate/test_classes.py'])

SEMKIT-081 finished; your kept work on src/rb_semkit/core/relate/functions.py, src/rb_semkit/core/relate/pairing.py, src/rb_semkit/core/relate/phrases.py, tests/relate/test_classes.py is back in the worktree; main is merged into your branch where it merges clean

### Attempt 1: file docstring

- update the docstring of src/rb_semkit/core/relate/pairing.py: +Pairing +best_pairing
- update the docstring of src/rb_semkit/core/word_vectors/units.py: +cuts
