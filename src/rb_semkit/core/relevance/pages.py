"""assign_pages: each phrase of the core against the pages of the site."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..errors import InvalidArguments
from .page import PageEncoder
from .vectors import DIGITS, nearest

PAGE_COLUMNS = ("url", "text")


def assign_pages(data: pd.Series, *, pages: pd.DataFrame, encoder: PageEncoder) -> pd.DataFrame:
    """The best two pages of the site for each phrase of the core, by meaning.

    pages: a table with the columns url and text (the text of the page: its title, H1 and body), and title and h1 when
    it has them; each page gets its page vector.

    The columns: best_page, best_similarity, second_page and second_similarity (4 places); the second page and its
    similarity are empty when the table has one page; an empty cell gets none. No row is dropped.

    Example: {cli} read --text "угловые диваны угловой диван" assign-pages --pages one_page.csv write -
    -> угловые диваны угловой диван, /uglovye, 1.0, ,
    """
    check_pages(pages)
    vectors, found = encoder.encode(data)
    page_vectors, _ = encoder.encode(pages["text"], pages)
    ids, similarities = nearest(vectors, page_vectors, 2)
    urls = np.append(pages["url"].astype(str).to_numpy(), "")  # the id -1 of a missing page is the last one
    table = pd.DataFrame(index=data.index)
    for place, name in enumerate(("best", "second")):
        has_page = found & (ids[:, place] >= 0)
        table[f"{name}_page"] = np.where(found, urls[ids[:, place]], "")
        table[f"{name}_similarity"] = np.where(has_page, similarities[:, place].astype(float).round(DIGITS), np.nan)
    return table


def check_pages(pages: pd.DataFrame) -> None:
    """Refuse a table of pages that lacks a column or has no page."""
    for name in PAGE_COLUMNS:
        if name not in pages.columns:
            raise InvalidArguments(
                f"pages: the table has no column {name}.", action="Give a table with the columns url and text."
            )
    if pages.empty:
        raise InvalidArguments("pages: the table has no pages.", action="Give a table with a row for each page.")
