"""headings: the heading structure of the pages of a table."""

from __future__ import annotations

import pandas as pd

from ..frame import Frame
from .page import is_html, parse_headings

URL = "url"


def headings(data: pd.Series | pd.DataFrame, *, column: str | None = None) -> pd.DataFrame:
    """The headings of the pages, one row per heading in page order: url, order, level (H1-H6), text.

    A cell is the HTML of one page. The url comes from the column url, when the table has it and it is no column of the
    pages. The order starts at 1 for each page. A cell that is empty or has no tag gives no rows.

    The page must hold its text in its HTML: a page built by JavaScript has none, so give the rendered HTML.
    """
    pages = Frame(data, column).phrases
    with_url = isinstance(data, pd.DataFrame) and URL in data and column != URL
    rows = []
    for row, cell in pages.items():
        found = parse_headings(cell) if is_html(cell) else []
        url = [str(data.loc[row, URL])] if with_url else []
        rows += [[*url, order, f"H{level}", text] for order, (level, text) in enumerate(found, 1)]
    return pd.DataFrame(rows, columns=[*([URL] if with_url else []), "order", "level", "text"])
