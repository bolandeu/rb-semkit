---
id: SEMKIT-081
title: 'relate-phrases core: classes, of, group and reason over lemmas, the step,
  the link seam'
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
- src/rb_semkit/core/relate/
- src/rb_semkit/steps/relate.py
- src/rb_semkit/data/
- scripts/
- tests/relate/
- tests/snapshots/
- tests/wordlists/
- tests/data/
test_paths:
- tests/relate/test_classes.py
- tests/relate/test_links_seam.py
- tests/relate/test_step.py
- tests/conformance/case_files.py
- tests/conformance/data_manifest/wordlists.json
- tests/steps/areas/relate.py
docs: none
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-009
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
resident: null
tool: null
pr: null
translation: 'Ядро шага relate-phrases: классы (та же / вариация / уточнение / другое),
  of, group и reason по леммам, сам шаг (--to, --keep), список вопросительных слов
  и шов для источников связей (словарь, латиница, свои группы — следующие задачи).
  Уточнение определяется словами, не порядком строк.'
---

Build the thin end-to-end path of the step `relate-phrases`: the step, its class rules, `of`, `group` and `reason`, over the lemmas of the words. The next tasks add the link sources (the thesaurus, the Latin reading, the caller's groups) to this frame, in parallel, so the frame must take them through one small interface and let each one come as one new module.

The contract of the classes, `of`, `group`, `reason` and the options is the plan in docs/plans/relate-phrases.md, sections 1 and 3 (it is read first; it beats this text where they differ). In short:

- The step reads the working column, one phrase per row, in the caller's order, and adds the columns `class` (same, variation, refinement or other), `of`, `group` and `reason`.
- A phrase is its words as lemmas (the bundled lemmatizer). Prepositions, conjunctions and particles are dropped, except the question words (a new bundled word list, about 20 words: как, где, сколько, почему, зачем, что, какой, какая, какое, какие, когда, куда, откуда, чем, кто, ли, можно; `--keep` adds words, as @FILE or @NAME). A number or a word with digits stays as a unit. A unit is a word in this task; the cut of a phrase into units asks the link sources for the runs of words they know (none yet), so a later source can add runs.
- `same`: the same lemmas in any order. `refinement`: every unit of the other phrase is in this phrase (equal, or linked by a source) and this phrase has units left over; it looks at all rows and does not depend on the order of the rows («как сделать сайт» before «сделать сайт» is a refinement of it). `variation`: all units pair one to one, equal or linked, at least one pair linked (no real source yet, so only a test source makes one). `other`: none of these.
- `same` and `variation` look only at earlier rows. A phrase takes the best relation over the table (same, variation, refinement); for a refinement the closest base (the most units), then the earliest row. `of` is that phrase; for `other` it is empty. Every relation points to a phrase that is before it by (the number of units, the row), so the chains of `of` end. `group` is the first row among the phrases whose chains of `of` end in the same phrase.
- `reason` names the rule and the words: `lemmas`; `+москва`; for `other` the unlinked words (`unlinked: …`) or what hangs on it (`base of: …`).
- `--to PHRASE`: every row is compared only with that phrase.
- The link sources are separate modules behind one small interface, and they are found, not listed: a module of a package of sources (core/relate/sources/) with a list `SOURCES` is a source, as the steps are found by `areas()` in steps/__init__.py. A new source is one new module and no edit of a shared file; three tasks add three sources at the same time. A source gives: the options it adds to the step (name, type, help; the step declares them), a hook that prepares the source from the options and the project folder (it may refuse before the input is read, for example a model that is not pulled), the runs of words it knows as one unit, whether two units are linked and why (the reason text), the units linked to a unit (for finding candidate pairs through an index, not over all pairs), and other forms of a word that the lookups of the other sources may try too (the Latin reading; none by default). The equality of lemmas is the only source of this task; a test source plugs in through the same interface.
- The step is atomic: it knows nothing of a pipeline. Its help follows the help standard, with examples; the help snapshots are updated.

## Acceptance

- Given the phrases «ремонт стиральных машин», «стиральная машина ремонт», «ремонт стиральной машины», When relate-phrases runs, Then the second and the third are same, of the first, with reason lemmas; the first is other, with an empty of, and the group of all three [check: tests/relate/test_classes.py]
- Given «разработка сайтов», «разработка сайтов москва», «разработка сайтов под ключ» and «разработка 2 сайтов», When the step runs, Then the last three are refinements of the first (москва, ключ and 2 are extra units; «под» is dropped) and reason is +москва, +ключ, +2 [check: tests/relate/test_classes.py]
- Given «как сделать сайт» and «сделать сайт» in this order and in the reverse order, When the step runs, Then in both orders «как сделать сайт» is a refinement of «сделать сайт» (reason +как), and «сделать сайт» is other with the group «как сделать сайт» in the first order, and its own group in the reverse order [check: tests/relate/test_classes.py]
- Given --keep with a word the question list lacks, When the step runs, Then that word stays in the phrase; Given a phrase with the preposition «в» or «на», Then the preposition does not change the class [check: tests/relate/test_classes.py]
- Given «диван» and then «как выбрать угловой диван» and «угловой диван», When the step runs, Then «угловой диван» is a refinement of «диван», «как выбрать угловой диван» is a refinement of «угловой диван» (the closest base, not «диван»), and all three have the group «диван» [check: tests/relate/test_classes.py]
- Given two unrelated phrases «купить диван» and «ремонт стиральных машин», When the step runs, Then the second is other, of is empty, group is the phrase itself and reason names the unlinked words [check: tests/relate/test_classes.py]
- Given the same phrase twice, an empty cell, and a table of one row, When the step runs, Then the second copy is same of the first, an empty cell is other with an empty of and group, and the single row is other [check: tests/relate/test_classes.py]
- Given a test link source that links the words «чехол» and «накидка», When the library function runs with it, Then «накидка на диван» at «чехол на диван» is a variation with the reason the source gives, a run of words that the source knows is one unit, and a refinement through a linked unit works [check: tests/relate/test_links_seam.py]
- Given --to PHRASE, When the step runs, Then every row is compared only with that phrase and of is that phrase or empty; Given a column the table lacks, or an empty table, Then the step refuses with a message that names the problem; Given --dry-run and --json, Then they work as in the other steps [check: tests/relate/test_step.py]

## How to test

level: unit tests of the library function with test link sources, and integration through the pipeline; seam: semkit read TABLE.jsonl relate-phrases … write -; data: small JSONL tables of phrases written in the test; the word list of question words is read from the bundled data

## Basis

Follow synonym-candidates (the step, its units and the way a step opens its data): src/rb_semkit/steps/word_vectors.py and src/rb_semkit/core/word_vectors/units.py; the bundled lemmatizer of the morph area; a bundled word list is built like meaning/neutral (scripts/build_parts/wordlists.py, its manifest); a step with options and a table result follows steps/dupes.py

## Read first

- `docs/plans/relate-phrases.md`
- `src/rb_semkit/core/word_vectors/units.py`
- `src/rb_semkit/steps/word_vectors.py`
- `src/rb_semkit/steps/dupes.py`
- `scripts/build_parts/wordlists.py`

## Out of scope

- The thesaurus, the Latin reading and --synonyms: the next tasks. No dictionary data is read in this task. SERP, roles, frequencies, vectors.
