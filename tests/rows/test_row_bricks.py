"""fill-down, sample-rows and shuffle-rows through the semkit command line, on small JSONL tables."""

from __future__ import annotations

from pathlib import Path

import pytest

from ..pipeline.runner import jsonl, semkit
from ..table.test_table_bricks import table

TEN = [{"id": number} for number in range(10)]


def ids(output: str) -> list[int]:
    return [int(row["id"]) for row in jsonl(output)]


def test_fill_down_takes_the_nearest_filled_cell_above_and_leaves_leading_empties(tmp_path: Path) -> None:
    source = table(
        tmp_path,
        [
            {"group": "", "n": 1},
            {"group": "A", "n": 2},
            {"group": "", "n": 3},
            {"group": "  ", "n": 4},
            {"group": "B", "n": 5},
            {"group": None, "n": 6},
        ],
    )

    result = semkit("read", source, "fill-down", "--column", "group", "write", "-")

    assert result.exit_code == 0, result.output
    assert [row["group"] for row in jsonl(result.stdout)] == ["", "A", "A", "A", "B", "B"]
    assert [row["n"] for row in jsonl(result.stdout)] == [1, 2, 3, 4, 5, 6]


def test_fill_down_without_column_fills_the_working_column_and_repeats_for_more(tmp_path: Path) -> None:
    source = table(tmp_path, [{"a": "x", "b": "p"}, {"a": "", "b": ""}, {"a": "y", "b": ""}])

    working = semkit("read", source, "fill-down", "write", "-")
    both = semkit("read", source, "fill-down", "--column", "a", "--column", "b", "write", "-")

    assert jsonl(working.stdout) == [{"a": "x", "b": "p"}, {"a": "x", "b": ""}, {"a": "y", "b": ""}]
    assert jsonl(both.stdout) == [{"a": "x", "b": "p"}, {"a": "x", "b": "p"}, {"a": "y", "b": "p"}]


def test_sample_rows_with_a_seed_keeps_the_same_rows_in_table_order(tmp_path: Path) -> None:
    source = table(tmp_path, TEN)

    first = semkit("read", source, "sample-rows", "--n", "3", "--seed", "1", "write", "-")
    second = semkit("read", source, "sample-rows", "--n", "3", "--seed", "1", "write", "-")

    assert first.exit_code == 0, first.output
    assert ids(first.stdout) == ids(second.stdout)
    assert len(ids(first.stdout)) == 3
    assert ids(first.stdout) == sorted(ids(first.stdout))


def test_sample_rows_share_rounds_to_the_nearest_row_and_a_big_n_keeps_all(tmp_path: Path) -> None:
    source = table(tmp_path, TEN)

    share = semkit("read", source, "sample-rows", "--share", "0.25", "--seed", "1", "write", "-")
    big = semkit("read", source, "sample-rows", "--n", "20", "write", "-")

    assert len(ids(share.stdout)) == 3
    assert ids(big.stdout) == list(range(10))


def test_shuffle_rows_with_a_seed_gives_the_same_order_of_the_same_rows(tmp_path: Path) -> None:
    source = table(tmp_path, TEN)

    first = semkit("read", source, "shuffle-rows", "--seed", "1", "write", "-")
    second = semkit("read", source, "shuffle-rows", "--seed", "1", "write", "-")

    assert ids(first.stdout) == ids(second.stdout)
    assert sorted(ids(first.stdout)) == list(range(10))
    assert ids(first.stdout) != list(range(10))


@pytest.mark.parametrize(
    ("args", "named"),
    [
        (["fill-down", "--column", "nope"], ["nope", "'id'"]),
        (["sample-rows", "--n", "2", "--share", "0.5"], ["n", "share"]),
        (["sample-rows"], ["n", "share"]),
        (["sample-rows", "--n", "-1"], ["-1"]),
        (["sample-rows", "--share", "0"], ["0"]),
        (["sample-rows", "--share", "1.5"], ["1.5"]),
    ],
)
def test_a_wrong_input_exits_2_naming_the_value_before_writing(
    tmp_path: Path, args: list[str], named: list[str]
) -> None:
    source = table(tmp_path, TEN)
    out = tmp_path / "out.jsonl"

    result = semkit("read", source, *args, "write", str(out))

    assert result.exit_code == 2
    assert all(text in result.output for text in named)
    assert not out.exists()
