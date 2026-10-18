"""The command line of each step of the change area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "change-case": ["phrases.csv", "change-case", "title"],
    "chpu": ["phrases.csv", "chpu"],
    "drop-minus-words": ["phrases.csv", "drop-minus-words"],
    "drop-modifiers": ["phrases.csv", "drop-modifiers"],
    "extract-utm": ["urls.csv", "extract-utm", "source"],
    "fix-word-order": ["phrases.csv", "fix-word-order"],
    "guillemets": ["phrases.csv", "guillemets"],
    "hash-text": ["phrases.csv", "hash-text", "--algorithm", "sha256"],
    "insert": ["phrases.csv", "insert", "--after", "!"],
    "match-type": ["phrases.csv", "match-type", "quotes"],
    "move-words": ["phrases.csv", "move-words", "недорого"],
    "phonetic": ["phrases.csv", "phonetic"],
    "remove-utm": ["urls.csv", "remove-utm"],
    "replace-text": ["phrases.csv", "replace-text", "--pairs", "pairs.csv"],
    "replace-words": ["phrases.csv", "replace-words", "--pairs", "pairs.csv"],
    "reverse": ["phrases.csv", "reverse"],
    "similar-chars": ["phrases.csv", "similar-chars", "--to", "en"],
    "sort-words": ["phrases.csv", "sort-words"],
    "split-digits": ["phrases.csv", "split-digits"],
    "switch-layout": ["phrases.csv", "switch-layout", "--to", "ru"],
    "translit": ["phrases.csv", "translit", "--to", "en"],
}
