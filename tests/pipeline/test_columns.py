"""The columns of a pipeline: --as and the new columns of a step, empty cells, number columns."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import rb_dataio

from .runner import jsonl, semkit


def test_as_over_an_existing_column_is_refused_before_the_steps_run(core_csv: Path, tmp_path: Path) -> None:
    trace = tmp_path / "t.jsonl"

    result = semkit("--json", "read", str(core_csv), "--trace", str(trace), "chpu", "--as", "freq", "write", "-")

    payload = json.loads(result.stdout)
    assert result.exit_code == 2
    assert payload["error"]["message"].startswith("chpu: --as freq:")
    assert "freq" in payload["error"]["action"]
    assert not trace.exists()


def test_as_over_a_column_an_earlier_as_made_is_refused(core_csv: Path) -> None:
    result = semkit("--json", "read", str(core_csv), "chpu", "--as", "url", "lemmatize", "--as", "url", "write", "-")

    assert result.exit_code == 2
    assert json.loads(result.stdout)["error"]["message"].startswith("lemmatize: --as url:")


def test_a_step_after_as_works_on_the_new_column_and_the_old_one_stays(tmp_path: Path) -> None:
    source = tmp_path / "core.csv"
    pd.DataFrame({"phrase": ["угловые диваны купить"]}).to_csv(source, index=False)

    result = semkit("read", str(source), "lemmatize", "--as", "key", "sort-words", "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [{"phrase": "угловые диваны купить", "key": "диван купить угловой"}]


def test_as_columns_keep_the_order_written(core_csv: Path) -> None:
    result = semkit("read", str(core_csv), "lemmatize", "--as", "a", "chpu", "--as", "b", "write", "-")

    assert result.exit_code == 0, result.output
    assert list(jsonl(result.stdout)[0]) == ["phrase", "a", "b", "freq"]


def test_cells_changed_of_as_counts_the_non_empty_new_values(tmp_path: Path) -> None:
    source = tmp_path / "core.csv"
    pd.DataFrame({"phrase": ["диван", "кресло", ""], "freq": [1, 2, 3]}).to_csv(source, index=False)

    result = semkit("read", str(source), "lemmatize", "--as", "key", "write", "-")

    assert result.exit_code == 0, result.output
    assert result.stderr.splitlines()[0] == "lemmatize: 3 → 3 rows, 2 cells changed"


def test_a_second_find_of_the_same_column_gets_its_own_column(core_csv: Path) -> None:
    result = semkit(
        "read", str(core_csv), "find-words", "купить", "find-words", "угловые", "write", "-"
    )  # fmt: skip

    assert result.exit_code == 0, result.output
    rows = jsonl(result.stdout)
    assert list(rows[0]) == ["phrase", "phrase_find", "phrase_find_2", "freq"]
    assert [row["phrase_find"] for row in rows] == [True, False, True, False, False]
    assert [row["phrase_find_2"] for row in rows] == [False, False, False, True, False]


def test_remove_cells_empty_drops_the_rows_with_an_empty_cell(tmp_path: Path) -> None:
    source = tmp_path / "core.csv"
    pd.DataFrame({"phrase": ["диван", None, "кресло"], "freq": [1, 2, 3]}).to_csv(source, index=False)

    result = semkit("read", str(source), "remove-cells", "empty", "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [{"phrase": "диван", "freq": 1}, {"phrase": "кресло", "freq": 3}]
    assert result.stderr.splitlines()[0] == "remove-cells: 3 → 2 rows, 0 cells changed"


def test_an_int_column_with_an_empty_cell_stays_int_from_jsonl_and_xlsx(tmp_path: Path) -> None:
    table = pd.DataFrame({"phrase": ["a", "b", "c"], "freq": pd.array([10, 2, None], dtype="Int64")})
    for name in ("in.jsonl", "in.xlsx"):
        rb_dataio.write(table, tmp_path / name)

        result = semkit("read", str(tmp_path / name), "write", "-")

        assert result.exit_code == 0, result.output
        assert [row["freq"] for row in jsonl(result.stdout)] == [10, 2, None]
        assert all(not isinstance(row["freq"], float) for row in jsonl(result.stdout))


def test_a_number_column_with_a_space_padded_cell_stays_numbers(tmp_path: Path) -> None:
    source = tmp_path / "core.csv"
    source.write_text('phrase,freq\nдиван," 10"\nкресло,2\n', encoding="utf-8")

    result = semkit("read", str(source), "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [{"phrase": "диван", "freq": 10}, {"phrase": "кресло", "freq": 2}]


def test_a_number_column_picked_as_working_column_is_written_back_as_numbers(tmp_path: Path) -> None:
    source = tmp_path / "core.csv"
    source.write_text("phrase,freq\nдиван,10\nкресло,2\n", encoding="utf-8")

    result = semkit("read", str(source), "--column", "freq", "insert", "--after", "0", "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [{"phrase": "диван", "freq": 100}, {"phrase": "кресло", "freq": 20}]
