"""The command line of each step of the reshape area of the step table: the file it reads and its words."""

from __future__ import annotations

COMMANDS = {
    "group-rows": ["reshape/clusters.csv", "group-rows", "--by", "cluster", "--sum", "freq"],
    "split-rows": ["reshape/cells.csv", "split-rows", "--sep", ";"],
    "unpivot": ["reshape/regions.csv", "unpivot", "--keep", "phrase"],
}
