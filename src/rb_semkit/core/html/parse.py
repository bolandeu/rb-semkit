"""parse_html: the pages of a table as columns that every text step takes."""

from __future__ import annotations

from dataclasses import astuple, fields

import pandas as pd

from ..frame import Frame, map_unique, put_columns
from .page import Page, is_html, parse_page

COLUMNS = [field.name for field in fields(Page)]


def without_html(cells: pd.Series) -> int:
    """The number of cells that are empty or hold no tag."""
    return int((~cells.map(is_html)).sum())


def parse_html(
    data: pd.Series | pd.DataFrame,
    *,
    drop_noindex: bool = False,
    drop_attributes: bool = False,
    column: str | None = None,
) -> pd.DataFrame:
    """The pages of the column as columns: text, links, all, main, title, description, h1. One row per page.

    A cell is the HTML of one page. A cell that is empty or has no tag (a plain text) gets empty columns. The columns
    are added right after the column of the pages.

    The page must hold its text in its HTML: a page built by JavaScript has none, so give the rendered HTML.
    Scripts, styles, noscript, templates and hidden elements are never counted.

    - text: the visible text without the text of links;
    - links: the text of links;
    - all: the text with the text of links;
    - main: the main content, without menus, header and footer;
    - title: the title of the page; description: its meta description; h1: its first H1.

    drop_noindex: leave out the text of <noindex> (the tag and the <!--noindex--> comments); by default it counts.
    drop_attributes: leave out the alt and title attributes; by default their text counts.
    """

    def page_of(cell: str) -> tuple:
        if not is_html(cell):
            return astuple(Page())
        return astuple(parse_page(cell, drop_noindex=drop_noindex, drop_attributes=drop_attributes))

    pages = map_unique(Frame(data, column).phrases, page_of)
    table = pd.DataFrame(pages.tolist(), columns=COLUMNS, index=pages.index)
    return put_columns(data, table, column)
