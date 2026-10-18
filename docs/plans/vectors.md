# Vectors and thesauri in semkit: measured choice

Working plan for IDEA-236. Measured on 2026-10-18 on the sofa core (tests/e2e/fixtures/sofa_core.csv,
1000 real phrases), Apple M4 CPU, 2 threads, fp32.

## Decisions of the Human

- Vectors are in semkit, as an optional extra; steps give candidates in a column, never drop by themselves.
- LLM generation is out: poor on volume.
- Licenses do not matter (semkit is not distributed); quality first, then speed.
- The encoder is an option; a slow quality model for small cores.
- Same intent of two phrases: one landing page serves both. For goods a refinement (type, mechanism, size,
  material, room, brand, used) makes another intent; commercial words (недорого, распродажа, от производителя,
  с доставкой, цены), the word form, the word order and the home city do not.

## Speed (1000 phrases; 100k and 1M are linear estimates)

| model | phrases/s | 100k | 1M | disk MB |
|---|---|---|---|---|
| minishlab/potion-multilingual-128M (model2vec) | 44000 | 2 s | 23 s | 513 |
| cointegrated/rubert-tiny2 | 4510 | 22 s | 3.7 min | 115 |
| deepvk/USER2-small | 1315 | 76 s | 13 min | 136 |
| intfloat/multilingual-e5-small | 949 | 105 s | 18 min | 471 |
| deepvk/USER-bge-m3 | 132 | 13 min | 2.1 h | 1374 |
| Qwen/Qwen3-Embedding-0.6B | 35 | 47 min | 7.9 h | 1152 |

faiss-cpu IndexFlatIP top-10: 100k all-kNN 5.7 s; 1M about 9.3 min and 3.3 GB, so 1M needs HNSW.

## Quality: 200 phrase pairs (same intent or not), labelled and checked by the Human

ROC AUC of the cosine against the label: USER-bge-m3 0.958, e5-small 0.943, Qwen3-0.6B 0.930, potion 0.910,
rubert-tiny2 0.759, USER2-small 0.751 (it ranks another city near the top: саранск ~ саратов).

Word synonyms (100 pairs): share of right proposals — RuWordNet 0.32, RusVectores 0.26, navec 0.18.
Dictionary and word-vector synonyms are candidates only.

## Proposed defaults

- Default encoder: e5-small. Small cores, quality mode: USER-bge-m3 (better and 4x faster than Qwen3 here).
  Very large cores: potion.
- Thresholds come from this label set; the label set goes into the repository as a quality test.

## Scope (the Human, 2026-10-18)

First epic: the base (`semkit models`, phrase vectors, the `--model` and `--threshold` options), duplicates by
meaning, clustering by meaning, off-topic phrases, classifying a search query report against the core
(minus candidates), assigning phrases to the site's pages.

Second epic, built on the same base (not to be forgotten):
- SEO: competing pages (cannibalization), core clusters no page or text covers (gaps), the main phrase of each
  cluster as an H1/title candidate, page pairs for internal links.
- Copywriting: coverage by meaning per paragraph, paragraphs off the text's topic, the meaning of paragraphs
  against competitor texts.
- Ads: small ad groups of one intent, how an ad text fits each phrase of its group, the landing page per phrase.
- Synonym candidates for words (RuWordNet + word vectors), coverage of a text by meaning.

## Clarification, decided (the Human, 2026-10-18)

1. Models: `semkit models pull NAME` once into the system cache (ADR 0009); `semkit models list`.
2. Duplicates by meaning are a kind of `dupes` (`--kind meaning`), with a similarity column.
3. A duplicate by meaning needs close vectors and only non-refining words or synonyms between the phrases;
   bundled list `@meaning/neutral` (commercial words), the Human's own list adds to it; the home city by `--home`.
4. `classify-queries`: a query report and `--against` the core; the nearest core phrase, similarity, target yes/no.
   Nothing is dropped.
5. `assign-pages`: `--pages` table (url + text); the best page, its similarity, the second page and its similarity.
6. `--model` takes short names (e5-small default, bge-m3, potion) and `hf:<id>`.
7. Exact search up to about 300k phrases, HNSW above, chosen by size and named in the step summary; deterministic.
8. `cluster-meaning`: one `--threshold`, by default the `cluster_threshold` of the model (e5-small 0.975: at the pair
   threshold 0.97 the sofa core joins «диван кровать купить в москве» with «диваны купить в москве», at 0.98 one intent
   splits; a model without it uses its `threshold`; the pair steps keep `threshold`); a phrase without neighbours is a
   cluster of one; the cluster's name is its most frequent phrase (`--freq`) or the one nearest its centre.
9. `off-topic`: distance from the core's centre weighted by frequency, or from `--seed` phrases; a 0–1 score and a
   flag by threshold.
10. The 200 labelled phrase pairs go into the repository as a quality test of the gate; it takes models from the
    cache and is skipped, with a message, when they are not there.

## The next epic: primitives by meaning (the Human, 2026-10-18)

semkit takes only what a script cannot do well: models, vectors, the index, the rules of language. Aggregations over
ready columns (core gaps, competing pages, internal links, ad fit, competitor topics, off-topic paragraphs) are
recipes in the guide: a pipeline plus a few lines of pandas. A recipe used again and again on live projects becomes a
step later. One epic instead of three: about half the code, the same possibilities.

Steps of the epic (each gives columns or a report, none drops rows; it starts when E-005 is closed):
- `nearest`: for each row of the working table, the top `--top` rows of `--against` (a table read as `read` reads it)
  with their similarity, in a long report (row, match, rank, similarity). Long texts get a page vector: the text is cut
  into pieces the model takes whole, the piece vectors are averaged, title and h1 columns (when present) weigh more.
  `assign-pages` moves to the same page vector.
- `split-paragraphs`: texts (a file, or a table of url and text) into paragraphs: blocks between empty lines, a
  heading line is a paragraph of its own; a report (url, number, paragraph) that `nearest` and `coverage-meaning` take.
- `coverage-meaning`: per core phrase, the best paragraph of a text, its similarity and covered yes/no; with a cluster
  column, also per cluster. It complements the word `coverage`.
- `ad-groups`: small groups of one intent by the rule of `dupes --kind meaning`; `--max-size` splits a large group by
  vector; the group name is its most frequent phrase.
- `synonym-candidates`: per word of the core, candidates from RuWordNet and word vectors (navec) with the source and a
  score; RuWordNet and navec are pulled by `semkit models pull` (ADR 0009); the 100 labelled word pairs are its
  quality test.

Tasks: T1 `nearest` + page vector + `split-paragraphs` (the frame) → T4 `coverage-meaning`; T2 `ad-groups` and T3
`synonym-candidates` beside T1.

## Scenarios, recorded for later (the Human, 2026-10-18)

Now only the atomic commands; the scenarios are built in later (as steps, recipes or another tool) when the Human
chooses. Each names the commands it is made of.

SEO:
- Core gaps: `cluster-meaning` → `nearest --against pages --top 1` per cluster; a cluster whose best page is below a
  threshold is a gap; sort by the total frequency of the cluster.
- H1 and title candidates per cluster: H1 the most frequent phrase (`cluster-meaning --freq`), title the phrase that
  holds the most words of the cluster.
- Competing pages (cannibalization): `nearest --against pages --top 2` per phrase; pages whose best and second differ
  by less than a margin for many phrases, or `nearest` of pages against pages above a threshold; sort by the frequency
  of the disputed phrases.
- Internal links: `nearest` of pages against pages; pairs between a link threshold and the competing threshold, both
  ways, at most N per page; the anchor is the most frequent core phrase whose best page is the target.
- Landing page per phrase: `assign-pages`.

Copywriting:
- Coverage by meaning per paragraph: `split-paragraphs` → `coverage-meaning`.
- Paragraphs off the topic of the text: `split-paragraphs` → `off-topic` with the core as `--seed`.
- Competitor topics I do not cover: `split-paragraphs` of competitor texts → `cluster-meaning` of their paragraphs →
  `nearest --against` my paragraphs; groups that several competitors have and my text has no close paragraph for.

Ads:
- Small ad groups of one intent: `ad-groups`.
- Ad fit: `nearest` of the phrases of a group against its ad (title and text); a weak fit is below a threshold.
- Landing page per phrase: `assign-pages`.

Words:
- Synonym candidates: `synonym-candidates`; the Human picks, the picked go to `--synonyms` of `dupes --kind meaning`.
- Phrase synonyms of one intent (the Human's first scenario, 2026-10-18; works on v0.1.42):
  `read --text Q synonym-candidates --all --source ruwordnet --as-slots linear-combinations agree
  nearest --to Q --threshold 0.85 --model bge-m3`, then the rows with a match, sorted by similarity, and the demand of
  each by `bukvarix freq` (another tool). On «таможенное оформление импорта»: 112 combinations, 74 above 0.85,
  4 with demand above 0. Gaps of bricks: no step keeps the rows with a match (`nearest` keeps an empty match for each
  row below the threshold) and no step sorts by a column, so jq does both now.
- Saved scenarios (the Human, 2026-10-18): `semkit run NAME` runs a named chain of semkit's own steps only (a bundled
  one or one in the project folder), seen in `run --help` and in `semkit docs`. A flow that calls other CLIs too
  (bukvarix, wordstat, serp) is built outside semkit, in a shell or a runner over all the tools.

Order: now IDEA-235 (the help of is-typo) as a task outside the epics, beside E-005; the epic after E-005.
