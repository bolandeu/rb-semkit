---
id: SEMKIT-013
title: 'Analysis block: combinations, parents and basis phrases, good/bad split, clustering,
  synonyms to minus-words, typos, sentiment'
status: in_progress
attempts: 1
blocked: true
blocked_reason: needs_scope
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: human
worker: claude-code
type: feature
owns_paths:
- src/rb_semkit/core/corpus/
- scripts/bench_parts/corpus.py
- tests/conformance/cases/corpus/
- tests/conformance/areas/corpus.py
- src/rb_semkit/data/corpus/languagetool.toml
test_paths:
- tests/corpus/
- tests/conformance/case_files.py
docs:
- docs/vba/deviations/corpus.md
- docs/vba/conformance/corpus.md
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
translation: 'Блок анализа ядра: перестановки, пары, линейные комбинации; родители,
  дети, базисы; деление на хорошие/плохие; кластеризация по частотам и по выдаче (настройки
  — аргументы, без сети); синонимы и минус-слова; опечатки по Левенштейну и словарю
  ядра + LanguageTool по желанию (повторы, ошибка поставщика); тональность. Исправления
  надстройки — в документе области.'
---


Operations over a whole semantic core, as Python functions (the v1 frame; a result that is a table is a DataFrame). The algorithms come from docs/vba/analysis.md (§5–§11), improved where Python does better or the add-in is broken.

Area «corpus»:
- combinations: every permutation of the words of a phrase; ordered pairs from a list (a two-column table, not «x\y» with a useless FALSE column); linear combinations of several lists (the Cartesian product, one column per list); a result size limit as an argument, InvalidArguments above it;
- hierarchy: nearest parents, first parents, first children against a list of phrases; basis phrases (by lemmas and without stopwords as arguments);
- the good/bad split of a core by words or lemmas → good, bad, rest, and the frequency dictionary of the rest;
- clustering by the frequency dictionary (threshold as an argument); no network. Clustering by a SERP table is NOT here: the add-in menu item maps to sk.cluster_serp (soft/hard, SEMKIT-018, ADR 0007); record in docs/vba/deviations/corpus.md how the add-in clustered by SERP (positional score 5 4 3 2 1 + 1, threshold 24, connected components) and why it is not ported; no conformance cases for it;
- synonyms: the list from a search-query report (query, condition, matched phrase) and appending the synonyms as minus-words;
- typos: is a word a typo, the most likely correction — Levenshtein against the core's own frequency dictionary (offline, fast on 1M); an optional spelling provider (LanguageTool on homeserver, plan §3a: batches of ~1000 lines, at most 2 parallel requests, retry with backoff on 5xx and timeouts, client timeout ≥ 60 s, stdlib HTTP) behind a provider interface;
- sentiment by a user dictionary (word → score): mean, min, max per phrase.

Fixes of the add-in (record each in the area deviations document, with how the add-in did it and why): a phrase is never its own parent; clustering by frequency treats the words of a phrase as a set (word order does not make two clusters); synonyms take the initial word from the condition; minus-words skip a synonym already in the phrase; Levenshtein compares whole code points; sentiment of a phrase without a marker is empty, max can be negative, the dictionary matches in any case with ё = е. Docstrings describe the behaviour in user terms, never the VBA (ADR 0006).

## Acceptance

- Given «a b c», When permutations run, Then «a b c», «a c b», «b a c», «b c a», «c a b», «c b a»; given a limit below the result size, Then InvalidArguments names the limit [check: tests/corpus/test_combinations.py]
- Given the parents «стол», «купить стол» and the children «купить стол недорого», «стол», When nearest parents run, Then «купить стол» and «» (a phrase is not its own parent) [check: tests/corpus/test_hierarchy.py]
- Given «купить диван», «диван», «купить диван недорого», «стол», «диван купить», When basis phrases run, Then «диван» and «стол» are the basis, the rest are empty [check: tests/corpus/test_hierarchy.py]
- Given a core and the good word «диван» and the bad word «бу», When the split runs by lemmas, Then «диваны бу» is bad, a phrase of good words only is good, the rest keeps its frequency dictionary [check: tests/corpus/test_split.py]
- Given the corpus area, When its public names are listed, Then there is no cluster_by_serp (SERP tables go to sk.cluster_serp) and docs/vba/deviations/corpus.md records the add-in's SERP method and why it is not ported [check: tests/corpus/test_clustering.py]
- Given a report row with the condition «купить диван» and the matched phrase «купить софа», When the synonym list runs, Then «диван» has the synonym «софа»; When minus-words are appended to «купить диван -софа», Then «-софа» is not added again [check: tests/corpus/test_synonyms.py]
- Given a core where «диван» is frequent, When the typo check runs on «диавн», Then it is a typo and the correction is «диван» [check: tests/corpus/test_typos.py]
- Given a spelling provider that times out or answers 5xx, When the check runs, Then it retries with backoff and then raises a project error naming the provider; a partial result is never returned [check: tests/corpus/test_spelling_provider.py]
- Given the dictionary «отличный 5», «плохой -3» and the phrases «Отличный диван», «плохой плохой стол», «стул», When sentiment runs, Then the mean is 5, -3 and empty; the max of the second is -3 [check: tests/corpus/test_sentiment.py]
- Given each function of the area, When its conformance cases run, Then each has a case file with at least 5 rows and all pass, and the area report equals the script output [check: tests/corpus/test_conformance.py]
- Given 1M phrases, When clustering by the frequency dictionary runs, Then it fits its benchmark budget [check: tests/corpus/test_bench_part.py]

## How to test

Public library seam (import rb_semkit as sk), pytest per function group; the spelling provider through a fake HTTP server in the test; plus the conformance case files of the area.

## Basis

docs/vba/analysis.md §5–§11 (handlers, quirks, worked examples); the v1 frame, n-gram counting and the lemmatizer; plan §3a for the spelling provider; the per-area parts of SEMKIT-010; ADR 0005, ADR 0006.

## Read first

- `docs/vba/analysis.md`
- `docs/plan.md`
- `docs/adr/0005-port-vba-fix-defects.md`
- `docs/adr/0006-vba-is-a-porting-source.md`

## Out of scope

- Irrelevant words (the morphology block).
- Typo check through Yandex Suggest.
- A real network call in the tests.

## Feedback

### Attempt 0 (not counted): main moved and conflicts with the work

`main` changed since your work began, and merging it conflicts in:

- `tests/conformance/case_files.py`

Merge it into your branch (`git merge main`), resolve each file keeping both behaviours, `git add` it and run the checks; do not commit: Antagor commits the merge with your work when the round ends (IDEA-201).

### Answer to finding #2

> SEMKIT-013: the corpus area (hierarchy, split, clustering, synonyms) reuses the private helper rb_semkit.core.analysis.frequency._word_keys (word -> key, lemma, stopword flag) instead of copying it. Make it a public helper of the analysis area in a later task, so other areas do not import a private name.

A follow-up task after SEMKIT-013 makes _word_keys a public helper of the analysis area.

### Attempt 1: the Architect's verdict

The review found blockers; close each:

- [blocker] C2 src/rb_semkit/core/corpus/clustering.py: `cluster_by_serp` ports the add-in method (positional score, chains of links = connected components). ADR 0007 (docs/adr/0007-serp-clustering-by-common-urls.md) says: «Метод надстройки (позиционный счёт и компоненты связности) не переносим: он сцепляет A и C через B без единого общего URL». `sk.cluster_serp` (soft/hard, SEMKIT-018) already clusters a SERP table. The task text asks for this function, so the two collide. The work followed the task silently and did not report the collision. The Architect must decide: amend ADR 0007 (and say why two SERP clusterings exist), or change the task. I did not add an inbox question; the Architect owns the ADR.
- [blocker] [wrong] Same collision as C2 above: the task demands the add-in SERP method, ADR 0007 rejects it. Until the Architect decides, the work cannot be accepted or rejected on this point — «clustering ... by a SERP table (phrase, position, url; the bonuses and the threshold as arguments, defaults 5 4 3 2 1, 1 and 24)».

Minor remarks of the review: optional, if they do not widen the task:

- [minor] C8 src/rb_semkit/core/corpus/clustering.py `cluster_by_serp` (CCN 12, 6 params incl. keyword-only), typos.py `CoreSpelling._corrections` (CCN 13), `check` (CCN 11): above lizard's usual limit of 10. I did not find the project limit in the tree; if it is 10, these are blockers. Tool result is the authority.
- [minor] C7 src/rb_semkit/core/corpus/hierarchy.py `SUBSET_WORDS = 12`, combinations.py `LIMIT = 1_048_576`, typos.py `distance=2, ratio=10`: tunable thresholds as literals in code. `LIMIT` and the typo defaults are argument defaults and documented, so low weight.
- [minor] C5 hierarchy.py / split.py / synonyms.py / clustering.py: import the private `_word_keys` of the analysis area. Already known (answer to finding #2, follow-up task), so no action here.
- [minor] C1 hierarchy.py `basis_phrases`: local name `tokens` (CONTEXT.md avoids «token» for wordform). Rename to `entries`.
- [minor] [wrong] `is_typo` and `typo_correction` work on whole phrases, not on a word — «typos: is a word a typo, the most likely correction». A phrase-level result is consistent with the other per-row functions; a one-word input works too. Accept.
- [minor] [extra] `add_minus_words` leaves a phrase in quotes unchanged; `synonyms` adds a «to check» row from the query when there is no matched phrase. The task does not say either. Both are documented in the docstrings; the second is the add-in behaviour. Accept.
