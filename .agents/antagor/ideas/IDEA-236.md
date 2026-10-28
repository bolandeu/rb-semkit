---
id: IDEA-236
title: 'Vectors and thesauri: synonym candidates, semantic dupes, clustering without
  SERP, off-topic phrases, intents'
created: '2026-10-17T20:39:31+00:00'
source_project: semkit
source_path: /Users/bolandau/Work/tools/semkit
status: epic
for_path: /Users/bolandau/Work/tools/semkit
triage:
  serves: []
  risks: []
  why: 'Daily core work needs semantic dupes, clusters without SERP and off-topic
    candidates in one pipeline; Human: the encoder is an option (choice of model),
    Qwen3-Embedding for small cores especially'
  score: 8.0
  route: clarify
  at: '2026-10-17T21:14:20+00:00'
clarify_project: /Users/bolandau/Work/tools/semkit
clarify_since: '2026-10-17T21:14:20+00:00'
epic: E-005
---

Human 2026-10-17: build word/phrase vectors into semkit as an optional extra (rb-semkit[vectors]); steps give candidates in a column, never drop by themselves; LLM generation out (poor on volume); licenses do not matter (not distributed), quality then speed. Research: scratchpad vectors-research.md — thesauri RuWordNet 2.0 / OEWN, word vectors RusVectores / navec, phrase encoders USER2-small / e5-small / model2vec, Qwen3-Embedding as a quality mode, faiss-cpu, kNN graph + Leiden. Next: a measured comparison on the sofa core (10k phrases for speed, ~300 labelled pairs for quality), then clarification. Open: model download vs 'semkit never downloads' (explicit 'semkit models pull').
