"""Pages for the tests of the HTML steps: the pages of the plan and a run of the pipeline over a table of HTML."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..pipeline.runner import jsonl, semkit

FIXTURES = Path(__file__).parent / "fixtures"
OST_TERM_IMPORT = (FIXTURES / "ost-term-import.html").read_text(encoding="utf-8")
MEGAGROUP_BASE_SHOP = (FIXTURES / "megagroup-base-shop.html").read_text(encoding="utf-8")


def run(tmp_path: Path, table: dict[str, list[str]], *steps: str, column: str = "html"):
    """`semkit read` over the table written to a file, with --column; the rows of the result are in `.rows`."""
    source = tmp_path / "pages.csv"
    pd.DataFrame(table).to_csv(source, index=False)
    result = semkit("read", str(source), "--column", column, *steps, "write", "-")
    result.rows = jsonl(result.stdout)
    return result
