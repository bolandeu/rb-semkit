"""The command line of each step of the html area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "headings": ["--column", "html", "pages.csv", "headings"],
    "parse-html": ["--column", "html", "pages.csv", "parse-html"],
}
