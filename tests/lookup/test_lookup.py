"""lookup through the semkit command line, on small JSONL tables."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ..pipeline.runner import jsonl, semkit
from ..table.test_table_bricks import table

PHRASES = [{"phrase": "купить диван"}, {"phrase": "кресло"}, {"phrase": "стол"}]
LOOKUP = [
    {"phrase": "купить диван", "freq": 10, "url": "/d"},
    {"phrase": "кресло", "freq": 3, "url": "/k"},
]


def lookup_table(tmp_path: Path, rows: list[dict]) -> str:
    path = tmp_path / "lookup.jsonl"
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    return str(path)


def test_rows_get_the_columns_of_the_first_matching_row_and_unmatched_rows_get_empty_cells(tmp_path: Path) -> None:
    result = semkit(
        "read", table(tmp_path, PHRASES), "lookup", lookup_table(tmp_path, LOOKUP), "--on", "phrase", "write", "-"
    )

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [
        {"phrase": "купить диван", "freq": 10, "url": "/d"},
        {"phrase": "кресло", "freq": 3, "url": "/k"},
        {"phrase": "стол", "freq": None, "url": None},
    ]


def test_matched_only_drops_the_rows_without_a_match_and_take_narrows_the_columns(tmp_path: Path) -> None:
    source, other = table(tmp_path, PHRASES), lookup_table(tmp_path, LOOKUP)

    dropped = semkit("read", source, "lookup", other, "--matched-only", "write", "-")
    narrowed = semkit("read", source, "lookup", other, "--take", "freq", "write", "-")

    assert [row["phrase"] for row in jsonl(dropped.stdout)] == ["купить диван", "кресло"]
    assert jsonl(narrowed.stdout)[0] == {"phrase": "купить диван", "freq": 10}


def test_kind_implicit_matches_the_same_words_in_another_order_and_exact_does_not(tmp_path: Path) -> None:
    source = table(tmp_path, [{"phrase": "купить диван"}])
    other = lookup_table(tmp_path, [{"phrase": "Диван купить", "freq": 7}])

    exact = semkit("read", source, "lookup", other, "write", "-")
    implicit = semkit("read", source, "lookup", other, "--kind", "implicit", "write", "-")

    assert jsonl(exact.stdout) == [{"phrase": "купить диван", "freq": None}]
    assert jsonl(implicit.stdout) == [{"phrase": "купить диван", "freq": 7}]


def test_a_key_that_repeats_gives_its_first_row_and_the_report_counts_it(tmp_path: Path) -> None:
    other = lookup_table(tmp_path, [{"phrase": "кресло", "freq": 3}, {"phrase": "кресло", "freq": 4}])

    out = tmp_path / "out.jsonl"

    result = semkit("--json", "read", table(tmp_path, PHRASES), "lookup", other, "write", str(out))

    summary = json.loads(result.stdout)["steps"][0]
    assert [row["freq"] for row in jsonl(out.read_text(encoding="utf-8"))] == [None, 3, None]
    assert summary["rows_after"] == 3
    assert summary["note"] == "lookup keys that repeat: 1"


def test_a_lookup_column_the_table_has_gets_the_suffix_lookup(tmp_path: Path) -> None:
    source = table(tmp_path, [{"phrase": "кресло", "freq": 1}])

    result = semkit("read", source, "lookup", lookup_table(tmp_path, LOOKUP), "--take", "freq", "write", "-")

    assert jsonl(result.stdout) == [{"phrase": "кресло", "freq": 1, "freq_lookup": 3}]


def test_on_main_equals_lookup_matches_differently_named_key_columns(tmp_path: Path) -> None:
    other = lookup_table(tmp_path, [{"query": "кресло", "freq": 3}])

    result = semkit("read", table(tmp_path, PHRASES), "lookup", other, "--on", "phrase=query", "write", "-")

    assert [row["freq"] for row in jsonl(result.stdout)] == [None, 3, None]


@pytest.mark.parametrize(
    ("arguments", "named"),
    [
        (["{dir}/missing.csv"], "missing.csv"),
        (["{lookup}", "--on", "nothing"], "'nothing'"),
        (["{lookup}", "--on", "phrase=nothing"], "'nothing'"),
        (["{lookup}", "--take", "color"], "'color'"),
        (["{lookup}", "--kind", "nonsense"], "nonsense"),
    ],
)
def test_a_wrong_input_is_refused_before_any_row_is_written(tmp_path: Path, arguments: list[str], named: str) -> None:
    out = tmp_path / "out.jsonl"
    words = [word.format(dir=tmp_path, lookup=lookup_table(tmp_path, LOOKUP)) for word in arguments]

    result = semkit("read", table(tmp_path, PHRASES), "lookup", *words, "write", str(out))

    assert result.exit_code == 2
    assert named in result.output
    assert not out.exists()


def test_a_missing_key_column_names_the_columns_there_are(tmp_path: Path) -> None:
    result = semkit(
        "read", table(tmp_path, PHRASES), "lookup", lookup_table(tmp_path, LOOKUP), "--on", "x", "write", "-"
    )

    assert "'x' is not in the table" in result.output
    assert "'phrase'" in result.output
    assert "'freq'" not in result.output


def test_a_missing_key_column_of_the_lookup_table_names_its_columns(tmp_path: Path) -> None:
    result = semkit(
        "read", table(tmp_path, PHRASES), "lookup", lookup_table(tmp_path, LOOKUP), "--on", "phrase=x", "write", "-"
    )

    assert "'x' is not in the lookup table" in result.output
    assert "'phrase', 'freq', 'url'" in result.output


def test_an_unmatched_cell_is_empty_so_a_number_column_stays_numbers_and_csv_has_an_empty_cell(tmp_path: Path) -> None:
    source = table(tmp_path, [{"phrase": "купить диван"}, {"phrase": "кресло"}])
    other = lookup_table(tmp_path, [{"phrase": "купить диван", "freq": 99}])
    out = tmp_path / "out.csv"

    jsonl_result = semkit("read", source, "lookup", other, "--on", "phrase", "write", "-")
    csv_result = semkit("read", source, "lookup", other, "--on", "phrase", "write", str(out))

    assert jsonl(jsonl_result.stdout) == [{"phrase": "купить диван", "freq": 99}, {"phrase": "кресло", "freq": None}]
    assert csv_result.exit_code == 0, csv_result.output
    assert out.read_text(encoding="utf-8").splitlines()[1:] == ["купить диван,99", "кресло,"]


def test_a_missing_lookup_file_is_refused_naming_the_file_argument(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"

    result = semkit("--json", "read", table(tmp_path, PHRASES), "lookup", str(missing), "write", "-")

    assert result.exit_code == 2, result.output
    error = json.loads(result.stdout)["error"]
    assert error["message"] == f"lookup: FILE {missing} does not exist."
    assert error["action"] == "Give FILE a file that exists."
