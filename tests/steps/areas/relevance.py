"""The command line of each step of the relevance area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "assign-pages": ["core.csv", "assign-pages", "--pages", "page_texts.csv"],
    "classify-queries": ["phrases.csv", "classify-queries", "--against", "core.csv"],
    "off-topic": ["core.csv", "off-topic", "--threshold", "0.5"],
}
