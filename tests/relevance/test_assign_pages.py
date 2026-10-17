"""`assign-pages` in a pipeline: every phrase of the core gets its best page, the second page and their similarity;
no row is dropped."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from ..pipeline.runner import jsonl, semkit

CORE = ["угловой диван", "прямой диван"]
PAGES = {
    "url": ["/uglovye", "/pryamye"],
    "text": ["угловые диваны угловой диван", "прямые диваны прямой диван"],
}


@pytest.fixture
def core_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "core.csv"
    pd.DataFrame({"phrase": CORE}).to_csv(path, index=False)
    return path


def _pages(tmp_path: Path, **columns: list[str]) -> Path:
    path = tmp_path / "pages.csv"
    pd.DataFrame(columns).to_csv(path, index=False)
    return path


def test_a_phrase_gets_the_best_page_and_the_second_one_with_their_similarity(core_csv: Path) -> None:
    pages = _pages(core_csv.parent, **PAGES)

    result = semkit("read", str(core_csv), "assign-pages", "--pages", str(pages), "write", "-")

    assert result.exit_code == 0, result.output
    rows = jsonl(result.stdout)
    assert [row["phrase"] for row in rows] == CORE
    assert [(row["best_page"], row["second_page"]) for row in rows] == [
        ("/uglovye", "/pryamye"),
        ("/pryamye", "/uglovye"),
    ]
    assert rows[0]["best_similarity"] > rows[0]["second_similarity"] > 0


@pytest.mark.parametrize("missing", ["url", "text"])
def test_pages_without_a_url_or_a_text_column_are_refused(core_csv: Path, missing: str) -> None:
    pages = _pages(core_csv.parent, **{name: values for name, values in PAGES.items() if name != missing})

    result = semkit("read", str(core_csv), "assign-pages", "--pages", str(pages), "write", "-")

    assert result.exit_code == 2
    assert "--pages" in result.stderr and missing in result.stderr


def test_one_page_leaves_the_second_page_and_its_similarity_empty(core_csv: Path) -> None:
    pages = _pages(core_csv.parent, url=["/uglovye"], text=[PAGES["text"][0]])

    result = semkit("read", str(core_csv), "assign-pages", "--pages", str(pages), "write", "-")

    assert result.exit_code == 0, result.output
    rows = jsonl(result.stdout)
    assert [row["best_page"] for row in rows] == ["/uglovye"] * 2
    assert all(row["second_page"] in ("", None) and row["second_similarity"] is None for row in rows)
