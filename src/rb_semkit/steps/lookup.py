"""The step that adds the columns of a lookup table to the current table by a key phrase."""

from __future__ import annotations

from typing import Annotated

from ..core.lookup.functions import REPEATED_KEYS, lookup
from . import POSITIONAL, REPEATED, Adapted, Prepared, Step, View, first_text, option, table_of

FILE_DOC = (
    "file: the lookup table; the file is read like `read` does. The key is --on, by default the working column of the"
    " table and the first text column of the lookup table."
)


def _prepare(options: dict) -> Prepared:
    other = table_of(options["file"], "file", positional=True)

    def run(table, column):
        on = options["on"] or f"{column}={first_text(other, 'file')}"
        joined = lookup(
            table, other, on=on, kind=options["kind"], take=options["take"], matched_only=options["matched_only"]
        )
        return View(joined, column, f"lookup keys that repeat: {joined.attrs[REPEATED_KEYS]}")

    return run


STEPS = [
    Step(
        "lookup",
        Adapted(
            lookup,
            {
                "other": option("file", Annotated[str, POSITIONAL]),
                "take": option("take", Annotated[list[str] | None, REPEATED], None),
            },
            FILE_DOC,
        ),
        "filter",
        _prepare,
        "The step adds the columns after the last column of the table; the working column stays the same. The report"
        " (stderr and --json) says how many keys repeat in the lookup table: the first row of each wins.",
    )
]
