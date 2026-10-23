"""group-rows, split-rows and unpivot through the semkit command line, on small JSONL tables."""

from __future__ import annotations

from pathlib import Path

import pytest

from ..pipeline.runner import jsonl, semkit
from ..table.test_table_bricks import table

CLUSTERS = [
    {"cluster": "диван", "phrase": "купить диван", "freq": 10},
    {"cluster": "диван", "phrase": "диван недорого", "freq": 5},
    {"cluster": "кресло", "phrase": "кресло", "freq": 3},
]


def test_group_rows_makes_a_row_of_each_group_with_the_joined_phrases_count_and_sum(tmp_path: Path) -> None:
    source = table(tmp_path, CLUSTERS)

    result = semkit(
        "read", source, "--column", "phrase", "group-rows", "--by", "cluster", "--sum", "freq", "write", "-"
    )

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [
        {"cluster": "диван", "phrase": "купить диван, диван недорого", "count": 2, "freq": 15},
        {"cluster": "кресло", "phrase": "кресло", "count": 1, "freq": 3},
    ]


def test_group_rows_takes_the_order_of_the_first_row_the_sep_and_leaves_empty_cells_out(tmp_path: Path) -> None:
    source = table(
        tmp_path,
        [
            {"g": "b", "phrase": "x", "freq": "5,5"},
            {"g": "a", "phrase": "", "freq": "1 000"},
            {"g": "b", "phrase": "y", "freq": ""},
            {"g": "b", "phrase": None, "freq": "2"},
        ],
    )

    result = semkit(
        "read", source, "--column", "phrase", "group-rows", "--by", "g", "--sep", " | ", "--sum", "freq", "write", "-"
    )

    assert jsonl(result.stdout) == [
        {"g": "b", "phrase": "x | y", "count": 3, "freq": 7.5},
        {"g": "a", "phrase": "", "count": 1, "freq": 1000.0},
    ]


def test_group_rows_by_two_columns_groups_by_the_pair(tmp_path: Path) -> None:
    source = table(
        tmp_path,
        [
            {"a": 1, "b": "x", "phrase": "p"},
            {"a": 1, "b": "y", "phrase": "q"},
            {"a": 1, "b": "x", "phrase": "r"},
        ],
    )

    result = semkit("read", source, "--column", "phrase", "group-rows", "--by", "a", "--by", "b", "write", "-")

    assert jsonl(result.stdout) == [
        {"a": 1, "b": "x", "phrase": "p, r", "count": 2},
        {"a": 1, "b": "y", "phrase": "q", "count": 1},
    ]


def test_split_rows_cuts_trims_and_copies_the_other_columns(tmp_path: Path) -> None:
    source = table(tmp_path, [{"phrase": "диван, софа ,", "freq": 7}])

    result = semkit("read", source, "split-rows", "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [{"phrase": "диван", "freq": 7}, {"phrase": "софа", "freq": 7}]


def test_split_rows_takes_another_sep_and_keeps_a_cell_without_it_and_an_empty_cell(tmp_path: Path) -> None:
    source = table(tmp_path, [{"phrase": "а;б", "n": 1}, {"phrase": "а,б", "n": 2}, {"phrase": "", "n": 3}])

    result = semkit("read", source, "split-rows", "--sep", ";", "write", "-")

    assert jsonl(result.stdout) == [
        {"phrase": "а", "n": 1},
        {"phrase": "б", "n": 1},
        {"phrase": "а,б", "n": 2},
        {"phrase": "", "n": 3},
    ]


def test_unpivot_turns_the_other_columns_into_rows_and_makes_the_value_column_the_working_one(tmp_path: Path) -> None:
    source = table(tmp_path, [{"phrase": "диван", "msk": 10, "spb": 4}])

    result = semkit("read", source, "unpivot", "--keep", "phrase", "write", "-")
    renamed = semkit(
        "read", source, "unpivot", "--keep", "phrase", "--name-column", "region", "--value-column", "freq",
        "change-case", "upper", "write", "-",
    )  # fmt: skip

    assert jsonl(result.stdout) == [
        {"phrase": "диван", "column": "msk", "value": 10},
        {"phrase": "диван", "column": "spb", "value": 4},
    ]
    assert jsonl(renamed.stdout) == [
        {"phrase": "диван", "region": "msk", "freq": 10},
        {"phrase": "диван", "region": "spb", "freq": 4},
    ]


def test_unpivot_gives_the_rows_of_each_kept_row_together(tmp_path: Path) -> None:
    source = table(tmp_path, [{"k": "a", "x": 1, "y": 2}, {"k": "b", "x": 3, "y": 4}])

    result = semkit("read", source, "unpivot", "--keep", "k", "write", "-")

    assert [(row["k"], row["column"]) for row in jsonl(result.stdout)] == [
        ("a", "x"),
        ("a", "y"),
        ("b", "x"),
        ("b", "y"),
    ]


@pytest.mark.parametrize(
    ("step", "named"),
    [
        (["group-rows", "--by", "nope"], ["'nope'", "'cluster', 'phrase', 'freq'"]),
        (["group-rows", "--by", "cluster", "--sum", "nope"], ["'nope'", "'cluster', 'phrase', 'freq'"]),
        (["group-rows", "--by", "cluster", "--sum", "name"], ["'много'", "row 2"]),
        (["group-rows", "--by", "cluster", "--sep", ""], ["--sep"]),
        (["split-rows", "--sep", ""], ["--sep"]),
        (["unpivot", "--keep", "nope"], ["'nope'", "'cluster', 'phrase', 'freq'"]),
        (["unpivot", "--keep", "cluster", "--keep", "phrase", "--keep", "freq", "--keep", "name"], ["every column"]),
        (["unpivot", "--keep", "cluster", "--value-column", "cluster"], ["'cluster'"]),
        (["unpivot", "--keep", "cluster", "--name-column", "cluster"], ["'cluster'"]),
    ],
)
def test_a_wrong_input_is_refused_before_a_row_is_written_and_the_message_names_it(
    tmp_path: Path, step: list[str], named: list[str]
) -> None:
    source = table(tmp_path, [{**row, "name": "много" if row["freq"] == 5 else "1"} for row in CLUSTERS])
    out = tmp_path / "out.jsonl"

    result = semkit("read", source, "--column", "phrase", *step, "write", str(out))

    assert result.exit_code == 2, result.output
    assert all(text in result.output for text in named), result.output
    assert not out.exists()
