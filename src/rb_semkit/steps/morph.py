"""The morphology steps: lemmas and parts of speech of the words of a phrase, the wordforms of a word."""

from __future__ import annotations

import pandas as pd

from ..core.morph.functions import lemmatize, part_of_speech, wordforms
from . import Prepared, Report, Step, change_step


def _prepare_wordforms(options: dict) -> Prepared:
    return lambda table, column: Report(pd.DataFrame({"wordform": pd.Series(wordforms(**options), dtype=object)}))


STEPS = [
    change_step(lemmatize),
    change_step(part_of_speech, new_column="pos"),
    Step(
        "wordforms",
        wordforms,
        "report",
        _prepare_wordforms,
        "The step ignores the current table: the table of the wordforms replaces it, its column wordform is the working one.",
    ),
]
