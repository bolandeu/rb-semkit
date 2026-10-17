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
8. `cluster-meaning`: one `--threshold`; a phrase without neighbours is a cluster of one; the cluster's name is its
   most frequent phrase (`--freq`) or the one nearest its centre.
9. `off-topic`: distance from the core's centre weighted by frequency, or from `--seed` phrases; a 0–1 score and a
   flag by threshold.
10. The 200 labelled phrase pairs go into the repository as a quality test of the gate; it takes models from the
    cache and is skipped, with a message, when they are not there.
