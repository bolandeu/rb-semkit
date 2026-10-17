---
id: SEMKIT-013
title: 'Analysis block: combinations, parents and basis phrases, good/bad split, clustering,
  synonyms to minus-words, typos, sentiment'
status: in_progress
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
- src/rb_semkit/core/corpus/
- scripts/bench_parts/corpus.py
- tests/conformance/cases/corpus/
- tests/conformance/areas/corpus.py
test_paths:
- tests/corpus/
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
- clustering by the frequency dictionary (threshold as an argument) and by a SERP table (phrase, position, url; the bonuses and the threshold as arguments, defaults 5 4 3 2 1, 1 and 24); no network;
- synonyms: the list from a search-query report (query, condition, matched phrase) and appending the synonyms as minus-words;
- typos: is a word a typo, the most likely correction — Levenshtein against the core's own frequency dictionary (offline, fast on 1M); an optional spelling provider (LanguageTool on homeserver, plan §3a: batches of ~1000 lines, at most 2 parallel requests, retry with backoff on 5xx and timeouts, client timeout ≥ 60 s, stdlib HTTP) behind a provider interface;
- sentiment by a user dictionary (word → score): mean, min, max per phrase.

Fixes of the add-in (record each in the area deviations document, with how the add-in did it and why): a phrase is never its own parent; SERP clusters come largest first; a keyword twice in one component does not fail; clustering by frequency treats the words of a phrase as a set (word order does not make two clusters); synonyms take the initial word from the condition; minus-words skip a synonym already in the phrase; Levenshtein compares whole code points; sentiment of a phrase without a marker is empty, max can be negative, the dictionary matches in any case with ё = е. Docstrings describe the behaviour in user terms, never the VBA (ADR 0006).

## Acceptance

- Given «a b c», When permutations run, Then «a b c», «a c b», «b a c», «b c a», «c a b», «c b a»; given a limit below the result size, Then InvalidArguments names the limit [check: tests/corpus/test_combinations.py]
- Given the parents «стол», «купить стол» and the children «купить стол недорого», «стол», When nearest parents run, Then «купить стол» and «» (a phrase is not its own parent) [check: tests/corpus/test_hierarchy.py]
- Given «купить диван», «диван», «купить диван недорого», «стол», «диван купить», When basis phrases run, Then «диван» and «стол» are the basis, the rest are empty [check: tests/corpus/test_hierarchy.py]
- Given a core and the good word «диван» and the bad word «бу», When the split runs by lemmas, Then «диваны бу» is bad, a phrase of good words only is good, the rest keeps its frequency dictionary [check: tests/corpus/test_split.py]
- Given two SERP tops sharing positions 1, 2 and 8, When clustered with the defaults, Then the score is 28 and they are one cluster; identical tops score 45; clusters come largest first [check: tests/corpus/test_clustering.py]
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

### Answer to question #1

> SEMKIT-013 asks for sk.cluster_by_serp over a given SERP table (offline), but docs/plan.md §3b (the Human, 2026-10-17) says clustering by search results is another tool.
> Question: Does semkit keep the offline SERP-table clustering of SEMKIT-013?
> Options:
> 1. Keep it: it ports an add-in menu function over a given table, no network; I implement it as the task says
> 2. Drop it from SEMKIT-013 and leave SERP clustering to the other tool
> Recommended: Keep it: it ports an add-in menu function over a given table, no network; I implement it as the task says

Drop sk.cluster_by_serp: the Human decided (2026-10-17) that clustering by search results belongs to the other tool, even over a given table. Do not implement it; list it as out of scope in the task result.
