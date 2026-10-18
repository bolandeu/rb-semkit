"""The steps that read pages given as HTML."""

from __future__ import annotations

import pandas as pd

from ..core.errors import InvalidArguments
from ..core.frame import Frame
from ..core.html import headings, parse_html
from ..core.html.parse import COLUMNS, without_html
from . import Columns, Prepared, Report, Step

HTML = "html"


def _html_name(table: pd.DataFrame, column: str) -> str | None:
    """`html` when the column of HTML has the name of a zone, so that the zones keep their names; else None."""
    if column not in COLUMNS:
        return None
    if HTML in table.columns:
        raise InvalidArguments(
            f"parse-html: the column {column} holds the HTML and the column {HTML} exists too.",
            action=f"Rename or drop one of the columns {column} and {HTML}.",
        )
    return HTML


def _prepare_parse(options: dict) -> Prepared:
    def run(table: pd.DataFrame, column: str) -> Columns:
        renamed = _html_name(table, column)
        missing = without_html(Frame(table, column).phrases)
        note = f"{missing} rows without HTML" if missing else None
        return Columns(parse_html(Frame(table, column).phrases, **options), note, renamed)

    return run


def _prepare_headings(options: dict) -> Prepared:
    return lambda table, column: Report(headings(table, column=column, **options))


STEPS = [
    Step(
        "parse-html",
        parse_html,
        "change",
        _prepare_parse,
        "The step reads the working column of HTML and adds the columns right after it; the rows stay.",
        columns=True,
    ),
    Step(
        "headings",
        headings,
        "report",
        _prepare_headings,
        "The step reads the working column of HTML; the table of the headings replaces the current one.",
    ),
]
