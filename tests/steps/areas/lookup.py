"""The command line of each step of the lookup area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "lookup": ["phrases.csv", "lookup", "lookup/urls.csv", "--on", "phrase", "--take", "url"],
}
