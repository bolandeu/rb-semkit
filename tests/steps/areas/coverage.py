"""The command line of each step of the coverage area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "coverage": ["phrases.csv", "coverage", "--against", "competitors.csv"],
}
