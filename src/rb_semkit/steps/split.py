"""The step that cuts texts into phrases."""

from __future__ import annotations

from typing import cast

import pandas as pd

from ..core.split.phrases import split_text
from . import Prepared, Report, Step


def _prepare(options: dict) -> Prepared:
    return lambda table, column: Report(cast(pd.DataFrame, split_text(table, column=column, **options)))


STEPS = [
    Step(
        "split-text",
        split_text,
        "report",
        _prepare,
        "The step cuts each cell of the working column; the table of the phrases replaces the current one, each row"
        " keeps the other columns of its source row, and the working column stays.",
    )
]
