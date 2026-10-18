"""The command line of each step of the table area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "use-column": ["matches.csv", "use-column", "match"],
    "sort-rows": ["core.csv", "sort-rows", "--by", "freq"],
}
