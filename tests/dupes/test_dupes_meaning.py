"""`dupes --kind meaning` in a pipeline: close vectors and only non-refining words, synonyms or the home city between
the phrases (the test encoder: a phrase is the sum of its words, so phrases that share words are close)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..pipeline.runner import jsonl, semkit

CLOSE = "0.1"  # the phrases of these cases share a word or more; a refinement must not count however close they are


def _run(tmp_path: Path, phrases: list[str], *options: str, action: str = "mark_except_first") -> list[dict]:
    path = tmp_path / "phrases.csv"
    pd.DataFrame({"phrase": phrases, "n": range(len(phrases))}).to_csv(
        path, index=False
    )  # n: an empty phrase is not a blank line
    result = semkit("read", str(path), "dupes", "--kind", "meaning", "--action", action, *options, "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


def _marks(rows: list[dict]) -> list[bool]:
    return [row["phrase_dupes"] for row in rows]


def test_a_neutral_word_a_word_form_and_the_home_city_do_not_make_another_intent(tmp_path: Path) -> None:
    rows = _run(
        tmp_path, ["купить диван недорого москва", "диван купить в москве"], "--home", "москва", "--threshold", "0.4"
    )

    assert _marks(rows) == [False, True]
    assert [row["dupe_of"] for row in rows] == ["", "купить диван недорого москва"]
    assert 0.4 <= rows[1]["similarity"] <= 1
    assert rows[0]["similarity"] is None


def test_a_refinement_makes_another_intent_however_close_the_vectors(tmp_path: Path) -> None:
    rows = _run(tmp_path, ["угловой диван", "прямой диван"], "--threshold", CLOSE)

    assert _marks(rows) == [False, False]


def test_another_city_is_a_refinement_and_the_home_city_only_with_home(tmp_path: Path) -> None:
    other = _run(tmp_path, ["диван москва", "диван саратов"], "--home", "москва", "--threshold", CLOSE)
    home = _run(tmp_path, ["диван", "диван москва"], "--home", "москва", "--threshold", CLOSE)
    no_home = _run(tmp_path, ["диван", "диван москва"], "--threshold", CLOSE)

    assert _marks(other) == [False, False]
    assert _marks(home) == [False, True]
    assert _marks(no_home) == [False, False]


def test_a_word_and_its_synonym_are_the_same_word(tmp_path: Path) -> None:
    synonyms = tmp_path / "synonyms.csv"
    pd.DataFrame({"word": ["диван"], "sure": [True], "synonyms": ["софа"]}).to_csv(synonyms, index=False)
    phrases = ["софа угловой", "угловой диван"]

    with_file = _run(tmp_path, phrases, "--threshold", CLOSE, "--synonyms", str(synonyms))
    without = _run(tmp_path, phrases, "--threshold", CLOSE)

    assert _marks(with_file) == [False, True]
    assert _marks(without) == [False, False]


def test_the_human_list_adds_to_the_bundled_neutral_words(tmp_path: Path) -> None:
    neutral = tmp_path / "neutral.txt"
    neutral.write_text("новинка\n", encoding="utf-8")
    phrases = ["диван новинка", "диван недорого", "диван"]

    rows = _run(tmp_path, phrases, "--threshold", CLOSE, "--neutral", f"@{neutral}")
    plain = _run(tmp_path, phrases, "--threshold", CLOSE)

    assert _marks(rows) == [False, True, True]
    assert [row["dupe_of"] for row in rows] == ["", "диван новинка", "диван новинка"]
    assert _marks(plain) == [False, False, True]  # the bundled list holds недорого, not новинка


def test_drop_keeps_the_first_row_of_a_group_and_mark_all_marks_every_row(tmp_path: Path) -> None:
    phrases = ["диван купить", "диван цена", "стол", "диван недорого"]

    kept = _run(tmp_path, phrases, "--threshold", CLOSE, action="drop")
    marked = _run(tmp_path, phrases, "--threshold", CLOSE, action="mark_all")

    assert [row["phrase"] for row in kept] == ["диван купить", "стол"]
    assert _marks(marked) == [True, True, False, True]


def test_an_empty_phrase_and_an_equal_phrase(tmp_path: Path) -> None:
    rows = _run(tmp_path, ["диван", "", "диван"], "--threshold", CLOSE)

    assert _marks(rows) == [False, False, True]
    assert rows[2]["dupe_of"] == "диван"
    assert rows[2]["similarity"] == 1.0


def test_a_list_that_does_not_exist_is_refused_naming_the_flag_and_the_list(tmp_path: Path) -> None:
    path = tmp_path / "phrases.csv"
    pd.DataFrame({"phrase": ["диван"]}).to_csv(path, index=False)

    result = semkit(
        "read", str(path), "dupes", "--kind", "meaning", "--action", "drop", "--neutral", "@no/such", "write", "-"
    )

    assert result.exit_code == 2
    assert "--neutral" in result.output
    assert "no/such" in result.output


def test_a_threshold_below_zero_is_refused_naming_the_step_and_the_flag(tmp_path: Path) -> None:
    path = tmp_path / "phrases.csv"
    pd.DataFrame({"phrase": ["диван"]}).to_csv(path, index=False)

    result = semkit(
        "read", str(path), "dupes", "--kind", "meaning", "--action", "drop", "--threshold=-0.1", "write", "-"
    )

    assert result.exit_code == 2
    assert "dupes" in result.output
    assert "--threshold" in result.output


def test_an_option_by_meaning_with_another_kind_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "phrases.csv"
    pd.DataFrame({"phrase": ["диван"]}).to_csv(path, index=False)

    result = semkit(
        "read", str(path), "dupes", "--kind", "lemmas", "--action", "drop", "--home", "москва", "write", "-"
    )

    assert result.exit_code == 2
    assert "home" in result.output
