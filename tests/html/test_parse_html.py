"""parse-html through the pipeline: the zones of a page, noindex and attributes, cells that are no HTML."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from ..pipeline.runner import jsonl, semkit
from .pages import MEGAGROUP_BASE_SHOP, OST_TERM_IMPORT, run

SOFA = '<html><body><p>Мы рады: <a href="/s">купить диван</a> недорого.</p></body></html>'
HIDDEN = (
    "<html><body><p>видно</p><noindex>скрыто</noindex><!--noindex-->тоже<!--/noindex-->"
    '<img src="a.png" alt="диван"></body></html>'
)


def row_of(tmp_path: Path, page: str, *steps: str) -> dict:
    result = run(tmp_path, {"html": [page]}, "parse-html", *steps)
    assert result.exit_code == 0, result.output
    return result.rows[0]


def words(text: str) -> set[str]:
    return set(text.split())


def test_the_test_page_gives_its_title_description_h1_and_the_main_content_without_menus(tmp_path: Path) -> None:
    row = row_of(tmp_path, OST_TERM_IMPORT)

    assert row["title"] == "Таможенное оформление импорта товаров в Москве и Московской области"
    assert row["description"].startswith("Экспертное оформление экспортных поставок")
    assert row["h1"] == "Таможенное оформление импорта"
    assert "Документы для таможенного оформления импорта" in row["main"]
    assert "Частые вопросы о таможенном оформлении" in row["main"]
    for menu_item in ("Калькулятор СВХ", "Удаленный выпуск (ЦЭД)", "Политика обработки персональных данных"):
        assert menu_item not in row["main"]


def test_the_word_count_of_the_miratext_page_is_within_one_percent_of_the_miratext_count(tmp_path: Path) -> None:
    parsed = tmp_path / "parsed.csv"
    source = tmp_path / "shop.csv"
    pd.DataFrame({"html": [MEGAGROUP_BASE_SHOP]}).to_csv(source, index=False)
    assert semkit("read", str(source), "parse-html", "write", str(parsed)).exit_code == 0

    result = semkit("read", str(parsed), "--column", "all", "text-stats", "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout)[0]["words"] == pytest.approx(1683, rel=0.01)


def test_the_text_of_a_link_goes_to_links_and_not_to_text(tmp_path: Path) -> None:
    row = row_of(tmp_path, SOFA)

    assert row["links"] == "купить диван"
    assert row["text"] == "Мы рады: недорого."
    assert row["all"] == "Мы рады: купить диван недорого."


def test_noindex_and_the_alt_attribute_count_by_default(tmp_path: Path) -> None:
    assert words(row_of(tmp_path, HIDDEN)["all"]) == {"видно", "скрыто", "тоже", "диван"}


def test_drop_noindex_leaves_out_the_tag_and_the_comments(tmp_path: Path) -> None:
    assert words(row_of(tmp_path, HIDDEN, "--drop-noindex")["all"]) == {"видно", "диван"}


def test_drop_attributes_leaves_out_alt_and_title(tmp_path: Path) -> None:
    page = HIDDEN.replace("<p>", '<p title="подсказка">')

    assert words(row_of(tmp_path, page)["all"]) == {"видно", "скрыто", "тоже", "диван", "подсказка"}
    assert words(row_of(tmp_path, page, "--drop-attributes")["all"]) == {"видно", "скрыто", "тоже"}


def test_scripts_styles_templates_and_hidden_elements_are_never_counted(tmp_path: Path) -> None:
    page = (
        "<html><head><title>Заголовок</title><style>.a{}</style></head><body><p>видно</p>"
        "<script>var скрипт = 1;</script><noscript>нескрипт</noscript><template>шаблон</template>"
        '<div hidden>скрытый</div><div style="display: none">стиль</div></body></html>'
    )

    assert row_of(tmp_path, page)["all"] == "видно"


def test_a_cell_without_html_gets_empty_columns_and_the_summary_counts_it(tmp_path: Path) -> None:
    result = run(tmp_path, {"url": ["a", "b", "c"], "html": [SOFA, "", "просто текст"]}, "parse-html")

    assert result.exit_code == 0, result.output
    assert [row["links"] for row in result.rows] == ["купить диван", "", ""]
    assert [row["all"] for row in result.rows[1:]] == ["", ""]
    assert "parse-html: 3 → 3 rows, " in result.stderr
    assert "2 rows without HTML" in result.stderr


def test_the_columns_come_right_after_the_column_of_pages(tmp_path: Path) -> None:
    result = run(tmp_path, {"url": ["https://a.ru/"], "html": [SOFA], "freq": ["5"]}, "parse-html")

    assert list(result.rows[0]) == ["url", "html", "text", "links", "all", "main", "title", "description", "h1", "freq"]
