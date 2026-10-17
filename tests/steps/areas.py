"""The steps of each area of the step table, written out (the pipeline core's areas are in tests/pipeline)."""

from __future__ import annotations

AREAS = {
    "change": [
        "change-case", "chpu", "drop-minus-words", "drop-modifiers", "extract-utm", "fix-word-order", "guillemets",
        "hash-text", "insert", "match-type", "move-words", "phonetic", "remove-utm", "replace-text", "replace-words",
        "reverse", "similar-chars", "sort-words", "split-digits", "switch-layout", "translit",
    ],
    "compare": ["bm25", "compare-grams", "compare-stats"],
    "corpus": [
        "add-minus-words", "basis-phrases", "cluster-by-frequency", "first-children", "first-parents", "is-typo",
        "linear-combinations", "nearest-parents", "ordered-pairs", "permutations", "sentiment", "split-by-words",
        "synonyms", "typo-correction",
    ],
    "coverage": ["coverage"],
    "declension": [
        "decline", "decline-adjective", "decline-full-name", "decline-noun", "drop-ready-pattern", "extract-complements",
        "extract-ready-pattern", "find-ready-pattern", "irrelevant-words", "keep-ready-pattern", "remove-phrase-end",
        "remove-ready-pattern",
    ],
    "listtools": ["compare-lists"],
    "markers": ["drop-markers", "extract-markers", "find-markers", "keep-markers", "remove-markers"],
    "morph": ["lemmatize", "part-of-speech", "wordforms"],
    "serp": ["cluster-serp"],
    "split": ["split-text"],
    "summary": ["summary"],
    "textstats": ["text-stats"],
    "vectors": ["cluster-meaning"],
}  # fmt: skip
