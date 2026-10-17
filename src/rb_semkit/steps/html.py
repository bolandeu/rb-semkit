"""The steps that read pages given as HTML."""

from __future__ import annotations

import pandas as pd

from ..core.frame import Frame
from ..core.html import headings, parse_html
from ..core.html.parse import without_html
from . import Columns, Prepared, Report, Step


def _prepare_parse(options: dict) -> Prepared:
    def run(table: pd.DataFrame, column: str) -> Columns:
        missing = without_html(Frame(table, column).phrases)
        note = f"{missing} rows without HTML" if missing else ""
        return Columns(parse_html(Frame(table, column).phrases, **options), note)

    return run


def _prepare_headings(options: dict) -> Prepared:
    return lambda table, column: Report(headings(table, column=column, **options))


PAGES = "--column html pages.csv"  # the working column of the example is the HTML, not the url

STEPS = [
    Step(
        "parse-html",
        parse_html,
        "change",
        _prepare_parse,
        "The step reads the working column of HTML and adds the columns right after it; the rows stay.",
        source=PAGES,
        columns=True,
    ),
    Step(
        "headings",
        headings,
        "report",
        _prepare_headings,
        "The step reads the working column of HTML; the table of the headings replaces the current one.",
        source=PAGES,
    ),
]
