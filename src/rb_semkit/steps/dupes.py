"""The duplicates step: marks the duplicates in a new column, or with `--action drop` drops them (a filter)."""

from __future__ import annotations

from typing import cast

import pandas as pd

from ..core.dupes.functions import dupes
from ..core.frame import Frame
from . import Change, Keep, Prepared, Step


def _prepare(options: dict) -> Prepared:
    def run(table, column):
        phrases = Frame(table, column).phrases
        found = cast(pd.Series, dupes(phrases, **options))  # a Series of phrases gives a Series
        if options["action"] == "drop":
            return Keep(phrases.index.to_series().isin(found.index))
        return Change(found)

    return run


STEPS = [
    Step(
        "dupes",
        dupes,
        "change",
        _prepare,
        "The step marks the duplicates of the working column in a new column <column>_dupes; with --action drop it"
        " keeps only the first row of each group.",
        new_column="dupes",
        example="lemmas --action mark_except_first",
    )
]
