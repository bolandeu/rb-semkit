"""The command line of each step of the rows area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "fill-down": ["rows/groups.csv", "fill-down", "--column", "group"],
    "sample-rows": ["core.csv", "sample-rows", "--n", "3", "--seed", "1"],
    "shuffle-rows": ["core.csv", "shuffle-rows", "--seed", "1"],
}
