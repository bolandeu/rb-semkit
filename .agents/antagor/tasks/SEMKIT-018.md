---
id: SEMKIT-018
title: 'Clustering by a given SERP table: soft and hard, by the number of common URLs
  in the top'
status: done
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
- src/rb_semkit/core/serp/
test_paths:
- tests/serp/
- tests/conformance/test_cases.py
docs:
- docs/adr/0005-port-vba-fix-defects.md
- docs/adr/
tools: []
worker_args: null
class: standard
decision: true
visual: null
depends_on: []
budget_usd: null
epic: E-002
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**Группировка по готовой таблице выдачи: soft и hard.** На входе таблица
  phrase, position, url (+ частоты по желанию); сеть не нужна. soft: фразы по убыванию
  частоты, свободная фраза — центр, к ней — фразы с ≥N общими URL с центром. hard:
  фраза входит в кластер, только если с каждым его членом ≥N общих URL. Отход от надстройки
  (ADR 0005): там баллы за позиции и цепочки (A и C вместе через B без общих URL)
  — кластеры расползаются.'
---

semkit clusters a SERP table it is given; it never fetches search results (another tool collects them). Add sk.cluster_serp(serp, *, method='soft', common=3, top=10, freq=None) -> DataFrame. serp: a DataFrame with the columns phrase, position (1 = first), url; one row per URL of a phrase's top; positions above top are ignored; URLs compare after trimming the scheme, 'www.' and a trailing slash. freq: an optional DataFrame or Series phrase -> frequency (the soft centers come from it; without it the phrase with the most links to the others is first, ties by phrase). method 'soft': phrases in descending frequency; an unassigned phrase becomes a center; each unassigned phrase with at least `common` URLs in common with the center joins it. method 'hard': phrases in descending frequency; a phrase joins the first cluster where it has at least `common` common URLs with every member, else it starts a new one. Output: one row per phrase of the input: phrase, cluster (1, 2, … largest cluster first, ties by the center's frequency), center (the first phrase of its cluster), common (URLs in common with the center; the center gets its own top size). A phrase without results is a cluster of one. ADR 0005 deviation to write: the add-in links two phrases by a position-weighted score (bonuses 5 4 3 2 1, threshold 24) and takes connected components (single linkage), so A and C land together through B without one common URL and clusters chain; semkit uses the standard soft and hard methods by common URLs instead, as SEO tools do.

## Acceptance

- Given A, B, C where A and B share 4 URLs, B and C share 4, A and C share 0, When method='hard', common=3, Then A and C are in different clusters; When method='soft' with freq A > B > C, Then A and B are one cluster and C another [check: tests/serp/]
- Given the URLs 'https://www.site.ru/a/' and 'http://site.ru/a', When compared, Then they are the same URL [check: tests/serp/]
- Given a phrase whose top shares fewer than `common` URLs with everyone, When clustered, Then it is a cluster of one and its center is itself [check: tests/serp/]
- Given a table without the column url, a method other than soft or hard, or common < 1, When clustered, Then sk.InvalidArguments names the argument [check: tests/serp/]
- Given 20 000 phrases x 10 URLs, When clustered either way, Then it ends in seconds [check: tests/serp/]

## How to test

Unit tests in tests/serp/ over small hand-made tables; one timing test (marked like the other speed tests) for 20 000 phrases.

## Basis

The input handling and errors of the other areas (Frame, sk.InvalidArguments); the public name in __all__ of the new area. Pair candidates through an inverted index url -> phrases, never all pairs: only phrases that share a URL can link. docs/vba/analysis.md §8 «По топ-10 выдачи» is the add-in's method this task replaces.

## Read first

- `docs/vba/analysis.md`
- `src/rb_semkit/core/dupes/__init__.py`
- `src/rb_semkit/core/frame.py`

## Out of scope

- Fetching search results (another tool; the serp CLI).
- Clustering by embeddings; the add-in's position-weighted single-linkage method.

## Feedback

### Attempt 1: decision not recorded

no new decision file in docs/adr/ (NNNN-slug.md, format in docs/adr/README.md)
