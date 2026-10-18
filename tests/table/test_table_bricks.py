"""use-column and sort-rows through the semkit command line, on small JSONL tables."""

from __future__ import annotations

import json
from pathlib import Path

from ..pipeline.runner import jsonl, semkit


def table(tmp_path: Path, rows: list[dict]) -> str:
    path = tmp_path / "table.jsonl"
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    return str(path)


def test_use_column_then_drop_cells_empty_keeps_the_matched_rows_only(tmp_path: Path) -> None:
    source = table(
        tmp_path,
        [
            {"phrase": "купить диван", "match": "диван купить", "similarity": 0.95},
            {"phrase": "кресло", "match": None, "similarity": None},
            {"phrase": "стол", "match": "столик", "similarity": 0.9},
        ],
    )

    result = semkit("read", source, "use-column", "match", "drop-cells", "empty", "write", "-")

    assert result.exit_code == 0, result.output
    assert [row["phrase"] for row in jsonl(result.stdout)] == ["купить диван", "стол"]


def test_use_column_leaves_the_table_as_it_is_and_switches_the_next_steps(tmp_path: Path) -> None:
    source = table(tmp_path, [{"phrase": "Диван", "match": "Кресло"}])

    result = semkit("read", source, "use-column", "match", "change-case", "lower", "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [{"phrase": "Диван", "match": "кресло"}]


def test_use_column_of_a_missing_column_exits_2_naming_the_columns(tmp_path: Path) -> None:
    source = table(tmp_path, [{"phrase": "диван", "match": "кресло"}])

    result = semkit("read", source, "use-column", "nope", "write", "-")

    assert result.exit_code == 2
    assert "nope" in result.output
    assert "'phrase'" in result.output
    assert "'match'" in result.output


def test_sort_rows_desc_orders_numbers_as_numbers_and_puts_empty_cells_last(tmp_path: Path) -> None:
    source = table(
        tmp_path,
        [
            {"phrase": "a", "similarity": 0.9},
            {"phrase": "b", "similarity": 0.95},
            {"phrase": "c", "similarity": None},
            {"phrase": "d", "similarity": 0.8},
        ],
    )

    result = semkit("read", source, "sort-rows", "--by", "similarity", "--desc", "write", "-")

    assert result.exit_code == 0, result.output
    assert [row["phrase"] for row in jsonl(result.stdout)] == ["b", "a", "d", "c"]


def test_sort_rows_ascending_puts_empty_cells_last_too(tmp_path: Path) -> None:
    source = table(tmp_path, [{"p": "a", "n": None}, {"p": "b", "n": 10}, {"p": "c", "n": 9}])

    result = semkit("read", source, "sort-rows", "--by", "n", "write", "-")

    assert [row["n"] for row in jsonl(result.stdout)] == [9, 10, None]


def test_sort_rows_reads_number_text_as_numbers(tmp_path: Path) -> None:
    path = tmp_path / "t.csv"
    path.write_text("phrase,n\na,10\nb,9\nc,\n", encoding="utf-8")

    result = semkit("read", str(path), "sort-rows", "--by", "n", "write", "-")

    assert [row["phrase"] for row in jsonl(result.stdout)] == ["b", "a", "c"]


def test_sort_rows_orders_texts_with_yo_after_ye(tmp_path: Path) -> None:
    source = table(tmp_path, [{"w": "ёлка"}, {"w": "ежик"}, {"w": "елка"}, {"w": "дом"}])

    result = semkit("read", source, "sort-rows", "--by", "w", "write", "-")

    assert [row["w"] for row in jsonl(result.stdout)] == ["дом", "ежик", "елка", "ёлка"]


def test_sort_rows_keeps_the_order_of_equal_rows(tmp_path: Path) -> None:
    source = table(
        tmp_path, [{"phrase": "a", "n": 1}, {"phrase": "b", "n": 1}, {"phrase": "c", "n": 0}, {"phrase": "d", "n": 1}]
    )

    for extra in ([], ["--desc"]):
        result = semkit("read", source, "sort-rows", "--by", "n", *extra, "write", "-")
        phrases = [row["phrase"] for row in jsonl(result.stdout)]
        assert phrases == (["c", "a", "b", "d"] if not extra else ["a", "b", "d", "c"])


def test_sort_rows_by_a_second_column_breaks_ties(tmp_path: Path) -> None:
    source = table(
        tmp_path,
        [{"a": 1, "b": "y"}, {"a": 0, "b": "z"}, {"a": 1, "b": "x"}, {"a": 0, "b": "w"}],
    )

    result = semkit("read", source, "sort-rows", "--by", "a", "--by", "b", "write", "-")

    assert [(row["a"], row["b"]) for row in jsonl(result.stdout)] == [(0, "w"), (0, "z"), (1, "x"), (1, "y")]


def test_sort_rows_keeps_the_working_column(tmp_path: Path) -> None:
    source = table(tmp_path, [{"phrase": "Б", "n": 2}, {"phrase": "А", "n": 1}])

    result = semkit("read", source, "sort-rows", "--by", "n", "change-case", "lower", "write", "-")

    assert jsonl(result.stdout) == [{"phrase": "а", "n": 1}, {"phrase": "б", "n": 2}]


def test_sort_rows_of_a_missing_column_exits_2_naming_the_columns(tmp_path: Path) -> None:
    source = table(tmp_path, [{"phrase": "диван", "n": 1}])

    result = semkit("read", source, "sort-rows", "--by", "n", "--by", "nope", "write", "-")

    assert result.exit_code == 2
    assert "nope" in result.output
    assert "'phrase'" in result.output
    assert "'n'" in result.output


def test_sort_rows_without_by_exits_2(tmp_path: Path) -> None:
    source = table(tmp_path, [{"phrase": "диван"}])

    result = semkit("read", source, "sort-rows", "write", "-")

    assert result.exit_code == 2
