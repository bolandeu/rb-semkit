"""The command line of each step of the compare area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "bm25": ["phrases.csv", "bm25", "--query", "диван"],
    "compare-grams": ["--whole", "mine.txt", "compare-grams", "--competitors", "competitors.csv"],
    "compare-stats": ["--whole", "mine.txt", "compare-stats", "--competitors", "competitors.csv"],
}
