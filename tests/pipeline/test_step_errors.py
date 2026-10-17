"""The refusals of a step: exit 2, the step and its option named as the command line has them, an action in CLI terms."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from .runner import jsonl, semkit

PYTHON_HINTS = ("format=", "sep=", "encoding=", "text_column", "first_only", "InvalidArguments")


def _refusal(*args: str) -> dict:
    result = semkit("--json", "read", *args)
    assert result.exit_code == 2, result.output
    error = json.loads(result.stdout)["error"]
    assert not any(hint in error["message"] + error.get("action", "") for hint in PYTHON_HINTS), error
    return error


@pytest.mark.parametrize(
    ("step", "flag"),
    [
        (["coverage", "--against"], "--against"),
        (["compare-lists", "--against"], "--against"),
        (["compare-grams", "--competitors"], "--competitors"),
        (["cluster-serp", "--freq"], "--freq"),
        (["replace-text", "--pairs"], "--pairs"),
        (["add-minus-words", "--synonyms"], "--synonyms"),
        (["sentiment", "--dictionary"], "--dictionary"),
    ],
)
def test_a_missing_file_of_an_option_is_refused_before_the_input_is_read(
    tmp_path: Path, step: list[str], flag: str
) -> None:
    missing = tmp_path / "missing.csv"

    error = _refusal(str(tmp_path / "no-input.csv"), *step, str(missing), "write", "-")

    assert error["message"] == f"{step[0]}: {flag} {missing} does not exist."
    assert flag in error["action"]


def test_a_missing_file_of_an_at_option_is_refused(tmp_path: Path) -> None:
    error = _refusal(str(tmp_path / "no-input.csv"), "drop-words", f"@{tmp_path / 'minus.txt'}", "write", "-")

    assert error["message"] == f"drop-words: @{tmp_path / 'minus.txt'}: the file does not exist."


@pytest.mark.parametrize(
    ("step", "flag"),
    [
        (["coverage", "--against", "texts.csv", "--mode", "fuzzy"], "--mode"),
        (["cluster-serp", "--method", "foo"], "--method"),
        (["compare-lists", "--against", "second.csv", "--op", "foo"], "--op"),
        (["counts", "--what", "foo"], "--what"),
        (["reverse", "--what", "foo"], "--what"),
    ],
)
def test_a_bad_value_of_an_enum_option_is_refused_before_the_input_is_read(
    tmp_path: Path, step: list[str], flag: str
) -> None:
    error = _refusal(str(tmp_path / "no-input.csv"), *step, "write", "-")

    assert error["message"].startswith(f"{step[0]}: ")
    assert flag in error["message"]
    assert f"{step[0]} --help" in error["action"]


def test_a_too_big_result_names_the_step_and_limit(tmp_path: Path) -> None:
    source = tmp_path / "core.csv"
    phrase = " ".join(f"слово{number}" for number in range(8))
    pd.DataFrame({"phrase": [phrase] * 2000}).to_csv(source, index=False)

    error = _refusal(str(source), "permutations", "write", "-")

    assert error["message"].startswith("permutations: --limit ")
    assert "--limit" in error["action"]


def test_a_weight_that_is_not_a_number_names_the_row_and_the_value(tmp_path: Path) -> None:
    source = tmp_path / "core.csv"
    pd.DataFrame({"phrase": ["диван", "кресло"], "freq": ["5", "много"]}).to_csv(source, index=False)

    error = _refusal(str(source), "ngrams", "--weight", "freq", "write", "-")

    assert error["message"] == "ngrams: --weight freq: row 2 holds 'много', not a number."


def test_weights_with_a_decimal_comma_and_spaces_between_digit_groups_are_numbers(tmp_path: Path) -> None:
    source = tmp_path / "core.csv"
    pd.DataFrame({"phrase": ["диван", "диван"], "freq": ["5,5", "1 000"]}).to_csv(source, index=False)

    result = semkit("read", str(source), "ngrams", "--weight", "freq", "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [{"ngram": "диван", "count": 2, "docs": 2, "sum": 1005.5}]


def test_a_list_of_phrases_given_to_a_words_step_names_five_items_and_the_phrases_step(tmp_path: Path) -> None:
    error = _refusal(str(tmp_path / "no-input.csv"), "drop-words", "@minus/cheap", "write", "-")

    assert error["message"].startswith("drop-words: --items: ")
    named = error["message"].count("«")
    assert 1 <= named <= 5
    assert "drop-phrases" in error["action"]
    assert len(error["message"]) < 400


def test_an_unknown_list_name_lists_the_names_that_exist_closest_first(tmp_path: Path) -> None:
    error = _refusal(str(tmp_path / "no-input.csv"), "drop-phrases", "@minus/cheep", "write", "-")

    assert error["message"].startswith("drop-phrases: minus/cheep: no such list; the lists closest to it: minus/cheap")


def test_an_at_csv_reads_its_first_column_without_the_header(tmp_path: Path) -> None:
    source, minus = tmp_path / "core.csv", tmp_path / "minus.csv"
    pd.DataFrame({"phrase": ["купить диван", "phrase стол", "кресло"]}).to_csv(source, index=False)
    pd.DataFrame({"phrase": ["диван"], "note": ["x"]}).to_csv(minus, index=False)

    result = semkit("read", str(source), "drop-words", f"@{minus}", "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [{"phrase": "phrase стол"}, {"phrase": "кресло"}]


def test_find_markers_takes_a_bundled_marker_list_by_its_word_list_name(tmp_path: Path) -> None:
    source = tmp_path / "core.csv"
    pd.DataFrame({"phrase": ["диван в москве", "диван"]}).to_csv(source, index=False)

    result = semkit("read", str(source), "find-markers", "--lists", "@markers/geo", "write", "-")

    assert result.exit_code == 0, result.output
    assert [row["phrase_find"] for row in jsonl(result.stdout)] == [True, False]


def test_find_markers_takes_a_marker_file_of_the_user(tmp_path: Path) -> None:
    source, brands = tmp_path / "core.csv", tmp_path / "brands.txt"
    pd.DataFrame({"phrase": ["диван аскона", "диван"]}).to_csv(source, index=False)
    brands.write_text("аскона\nикеа\n", encoding="utf-8")

    result = semkit("read", str(source), "extract-markers", "--lists", f"geo,@{brands}", "write", "-")

    assert result.exit_code == 0, result.output
    assert [row["phrase"] for row in jsonl(result.stdout)] == ["аскона", ""]


def test_cluster_serp_takes_the_frequency_column_by_name(tmp_path: Path) -> None:
    serp, freq = tmp_path / "serp.csv", tmp_path / "freq.csv"
    rows = [("b", 1, "u1"), ("b", 2, "u2"), ("a", 1, "u1"), ("a", 2, "u2")]
    pd.DataFrame(rows, columns=["phrase", "position", "url"]).to_csv(serp, index=False)
    pd.DataFrame({"phrase": ["a", "b"], "freq_msk_exact": [100, 1]}).to_csv(freq, index=False)

    result = semkit(
        "read", str(serp), "cluster-serp", "--common", "2", "--freq", str(freq), "--freq-column", "freq_msk_exact",
        "write", "-",
    )  # fmt: skip

    assert result.exit_code == 0, result.output
    assert {row["center"] for row in jsonl(result.stdout)} == {"a"}
