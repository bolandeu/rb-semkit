"""headings through the pipeline: the heading structure of the pages, in page order."""

from __future__ import annotations

from pathlib import Path

from .pages import OST_TERM_IMPORT, run


def test_the_rows_of_the_test_page_start_with_h1_and_two_h2_in_page_order(tmp_path: Path) -> None:
    result = run(tmp_path, {"html": [OST_TERM_IMPORT]}, "headings")

    assert result.exit_code == 0, result.output
    assert result.rows[:3] == [
        {"order": 1, "level": "H1", "text": "Таможенное оформление импорта"},
        {"order": 2, "level": "H2", "text": "ОСТ-ТЕРМИНАЛ"},
        {"order": 3, "level": "H2", "text": "Расположение таможенного поста и склада"},
    ]


def test_each_row_carries_its_url_and_the_order_restarts_for_each_page(tmp_path: Path) -> None:
    pages = {
        "url": ["https://a.ru/", "https://b.ru/"],
        "html": ["<h1>Диваны</h1><h2>Цены</h2>", "<h1>Кровати</h1><h3>Размеры</h3><h2>Цены</h2>"],
    }

    result = run(tmp_path, pages, "headings")

    assert result.rows == [
        {"url": "https://a.ru/", "order": 1, "level": "H1", "text": "Диваны"},
        {"url": "https://a.ru/", "order": 2, "level": "H2", "text": "Цены"},
        {"url": "https://b.ru/", "order": 1, "level": "H1", "text": "Кровати"},
        {"url": "https://b.ru/", "order": 2, "level": "H3", "text": "Размеры"},
        {"url": "https://b.ru/", "order": 3, "level": "H2", "text": "Цены"},
    ]


def test_a_cell_without_html_and_a_hidden_heading_give_no_rows(tmp_path: Path) -> None:
    pages = {"html": ["просто текст", "<h1>Видно</h1><h2 hidden>Скрыто</h2><h2></h2>"]}

    assert [row["text"] for row in run(tmp_path, pages, "headings").rows] == ["Видно"]
