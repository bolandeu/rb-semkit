"""The command line of each step of the declension area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "agree": ["combinations.csv", "agree"],
    "decline": ["phrases.csv", "decline", "genitive"],
    "decline-adjective": ["phrases.csv", "decline-adjective", "genitive"],
    "decline-full-name": ["names.csv", "decline-full-name", "genitive"],
    "decline-noun": ["phrases.csv", "decline-noun", "genitive"],
    "drop-ready-pattern": ["ready.csv", "drop-ready-pattern", "domain"],
    "extract-complements": ["ready.csv", "extract-complements"],
    "extract-ready-pattern": ["ready.csv", "extract-ready-pattern", "domain"],
    "find-ready-pattern": ["ready.csv", "find-ready-pattern", "domain"],
    "irrelevant-words": ["ready.csv", "irrelevant-words", "--word", "телефон"],
    "keep-ready-pattern": ["ready.csv", "keep-ready-pattern", "domain"],
    "remove-phrase-end": ["ready.csv", "remove-phrase-end", "prepositions"],
    "remove-ready-pattern": ["ready.csv", "remove-ready-pattern", "domain"],
}
