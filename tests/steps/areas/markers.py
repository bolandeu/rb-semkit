"""The command line of each step of the markers area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "drop-markers": ["phrases.csv", "drop-markers", "--lists", "sale"],
    "extract-markers": ["phrases.csv", "extract-markers", "--lists", "sale"],
    "find-markers": ["phrases.csv", "find-markers", "--lists", "sale"],
    "keep-markers": ["phrases.csv", "keep-markers", "--lists", "sale"],
    "remove-markers": ["phrases.csv", "remove-markers", "--lists", "sale"],
}
