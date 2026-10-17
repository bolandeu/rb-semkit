"""The step that counts the usual SEO metrics of each text."""

from __future__ import annotations

from ..core.textstats.functions import text_stats
from . import Prepared, Report, Step


def _prepare(options: dict) -> Prepared:
    return lambda table, column: Report(text_stats(table, column=column, **options))


STEPS = [
    Step(
        "text-stats",
        text_stats,
        "report",
        _prepare,
        "The step reads the working column; the metric columns are added right after it in the current table.",
    )
]
