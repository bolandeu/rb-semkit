"""The step that counts the usual SEO metrics of each text."""

from __future__ import annotations

from ..core.frame import Frame
from ..core.textstats.functions import text_stats
from . import Columns, Prepared, Step


def _prepare(options: dict) -> Prepared:
    return lambda table, column: Columns(text_stats(Frame(table, column).phrases, **options))


STEPS = [
    Step(
        "text-stats",
        text_stats,
        "change",
        _prepare,
        "The step reads the working column and adds the metric columns right after it; the rows stay.",
        columns=True,
    )
]
