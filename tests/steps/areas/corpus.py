"""The command line of each step of the corpus area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "add-minus-words": ["phrases.csv", "add-minus-words", "--synonyms", "synonyms.csv"],
    "basis-phrases": ["phrases.csv", "basis-phrases"],
    "cluster-by-frequency": ["phrases.csv", "cluster-by-frequency", "--threshold", "1"],
    "first-children": ["phrases.csv", "first-children", "--children", "диван"],
    "first-parents": ["phrases.csv", "first-parents", "--parents", "диван"],
    "is-typo": ["phrases.csv", "is-typo"],
    "linear-combinations": ["phrases.csv", "linear-combinations"],
    "nearest-parents": ["phrases.csv", "nearest-parents", "--parents", "диван"],
    "ordered-pairs": ["phrases.csv", "ordered-pairs"],
    "permutations": ["phrases.csv", "permutations"],
    "sentiment": ["phrases.csv", "sentiment", "--dictionary", "dictionary.csv"],
    "split-by-words": ["phrases.csv", "split-by-words", "--keep", "rest"],
    "synonyms": ["report.csv", "synonyms"],
    "typo-correction": ["phrases.csv", "typo-correction"],
}
