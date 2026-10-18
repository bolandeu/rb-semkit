"""The command line of each step of the nearest area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "nearest": ["core.csv", "nearest", "--against", "page_texts.csv", "--top", "2"],
    "split-paragraphs": ["--whole", "article.txt", "split-paragraphs"],
}
