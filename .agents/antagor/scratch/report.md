Done: SEMKIT-012. The checks pass (`check_command_docstrings.py`, `release.py --check`: gate passed).

## What is new

1. Area declension (`src/rb_semkit/core/declension/`): `sk.decline_noun`, `sk.decline_adjective`, `sk.decline_full_name`, `sk.decline` (everything that declines), `sk.irrelevant_words`.
2. Area patterns (`src/rb_semkit/core/patterns/`): `sk.ready_pattern(kind)` (domain, email, phone, date_ddmmyyyy, date_yyyymmdd; find/remove/extract), `sk.phrase_end(kind)` (prepositions, buy_markers; remove), `sk.complements()` (extract).
3. `sk.lemmatize(..., fallback="pymorphy")` and `SemtoolsLemmatizer(fallback="pymorphy")`. The default does not change.
4. Data: `declension/tables.json` (2.1 MB, loads in about 10 ms), built by `scripts/build_parts/declension.py`, manifest `tests/conformance/data_manifest/declension.json`. The word lists for the case rules come from the VBA literals: `arrPron` (RibbonCallbacks.vba) and the six case lists of `findIrr.frm`. New source key `find_irrelevant` in `scripts/build_data.toml`.
5. Conformance: 8 case files (74 cases, 41 deviations, 0 xfail); reports `docs/vba/conformance/declension.md`, `patterns.md`. The summary `docs/vba/conformance.md` is not updated (it is the epic check). Deviations: `docs/vba/deviations/declension.md`, `patterns.md`.
6. Bench part `scripts/bench_parts/declension.py`: `decline` on 1M phrases runs in 1.6 s (load 0.05 s).

## Decisions inside the task (recorded in the deviations documents)

1. A consonant-final noun whose ending is missing from the table also takes the usual ending (not only an empty cell). The accusative stays table-only, as the VBA.
2. An indeclinable word stays in every case: the VBA accusative path skipped `nonDecl` (553 words changed).
3. «Everything that declines»: verb, adverb, preposition, conjunction, particle stay; a pronoun declines only by the adjective tables («он» stays, «этот» → «этого»); a noun never goes to the adjective branch («зной»). The VBA rule «a word after a governing word stays only from the 3rd word on» is kept: «мой синий стол» declines as a whole.
4. Male surname in «-ой» declines as an adjective: the acceptance needs «Толстого», the VBA gives «Толстоя».
5. Dates: the separator is optional (the acceptance needs «01022024»), and a date inside a longer number is not found.

## Changed existing tests (for the release report)

- `tests/core/test_build_data.py`: `declension/tables.json` added to BUILT_FILES and to the compact-JSON check; the test `test_json_files_are_compact_and_no_declension_tables_are_built` is renamed to `..._the_declension_tables_are_not_in_morph`, because the declension tables are built now (in their own area).

## Other files outside Owns

`README.md` (two examples, the fallback), `scripts/build_parts/morph.py` (docstring and a comment: the declension tables are built by their own part), `scripts/build_data.toml` (the source key). `morph/functions.py`: `_word_by_word` is now `word_by_word`, so the declension area uses it.

## Findings

- inbox #1: the epic says the default lemma of an unknown word is the word itself, as the add-in; the v1 default (ADR 0003) asks pymorphy3. I kept the v1 default, as the task says.
