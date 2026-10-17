"""The step that reports the mean, median, min and max of the numeric columns."""

from __future__ import annotations

from ..core.summary.functions import summary
from . import Prepared, Report, Step


def _prepare(options: dict) -> Prepared:
    return lambda table, column: Report(summary(table))


STEPS = [
    Step(
        "summary",
        summary,
        "report",
        _prepare,
        "The step reports on the whole current table, whatever the working column is; its table replaces the current one.",
    )
]
