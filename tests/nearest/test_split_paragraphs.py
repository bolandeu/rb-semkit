"""`split-paragraphs` in a pipeline: a text file, or a table of url and text, into one row per paragraph."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from ..pipeline.runner import jsonl, semkit

TEXT = "Диваны\n\nУгловые диваны бывают...\nЕщё строка.\n\n\nПрямые диваны..."


@pytest.fixture(autouse=True)
def in_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


def _rows(*arguments: str) -> list[tuple]:
    result = semkit("read", *arguments, "split-paragraphs", "write", "-")
    assert result.exit_code == 0, result.output
    return [(row["url"] or "", row["number"], row["paragraph"]) for row in jsonl(result.stdout)]


def test_a_text_file_gives_its_blocks_between_empty_lines_with_the_lines_of_a_block_joined(tmp_path: Path) -> None:
    (tmp_path / "article.txt").write_text(TEXT, encoding="utf-8")

    assert _rows("--whole", "article.txt") == [
        ("", 1, "Диваны"),
        ("", 2, "Угловые диваны бывают... Ещё строка."),
        ("", 3, "Прямые диваны..."),
    ]


def test_a_heading_line_followed_by_text_is_a_paragraph_of_its_own(tmp_path: Path) -> None:
    (tmp_path / "article.txt").write_text(
        "  Угловые диваны  \nУгловой диван ставят в углу.\nОн экономит место.\n\nЦены\nОт 20 000 рублей.",
        encoding="utf-8",
    )

    assert _rows("--whole", "article.txt") == [
        ("", 1, "Угловые диваны"),
        ("", 2, "Угловой диван ставят в углу. Он экономит место."),
        ("", 3, "Цены"),
        ("", 4, "От 20 000 рублей."),
    ]


def test_a_table_of_urls_and_texts_numbers_the_paragraphs_of_each_url_from_1(tmp_path: Path) -> None:
    pd.DataFrame({"url": ["/a", "/b", "/c"], "text": ["Первый абзац.\n\nВторой абзац.", "Один абзац.", ""]}).to_csv(
        tmp_path / "pages.csv", index=False
    )

    assert _rows("pages.csv") == [
        ("/a", 1, "Первый абзац."),
        ("/a", 2, "Второй абзац."),
        ("/b", 1, "Один абзац."),
    ]


def test_an_empty_text_gives_no_rows(tmp_path: Path) -> None:
    (tmp_path / "empty.txt").write_text(" \n\n  \n", encoding="utf-8")

    assert _rows("--whole", "empty.txt") == []
