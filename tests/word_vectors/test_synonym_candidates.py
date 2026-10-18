"""`synonym-candidates` in a pipeline: candidates per word of the core from the thesaurus and the word vectors."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from ..pipeline.runner import jsonl, semkit
from ..vectors.conftest import LocalSource

pytestmark = pytest.mark.real_encoder


@pytest.fixture
def pulled(words_hub: LocalSource, core_csv: Path) -> Path:
    """Both word data in the cache; the core."""
    for name in ("ruwordnet", "navec"):
        assert semkit("models", "pull", name).exit_code == 0
    return core_csv


def _report(core: Path, *options: str) -> list[dict]:
    result = semkit("read", str(core), "synonym-candidates", *options, "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


def _phrases(*texts: str, options: tuple[str, ...] = ()) -> list[dict]:
    """The report for a core of these phrases."""
    arguments = [argument for text in texts for argument in ("--text", text)]
    result = semkit("read", *arguments, "synonym-candidates", *options, "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


def _candidates(rows: list[dict], word: str) -> list[str]:
    return [row["candidate"] for row in rows if row["word"] == word]


def _of(rows: list[dict], word: str) -> list[tuple]:
    return [(row["candidate"], row["source"], row["score"], row["in_core"]) for row in rows if row["word"] == word]


def test_a_word_gets_its_synonym_with_the_source_and_the_score_and_not_a_related_word(pulled: Path) -> None:
    rows = _report(pulled)

    found = _of(rows, "диван")
    assert ("софа", "ruwordnet", 1.0, True) in found
    assert ("софа", "navec", 0.8, True) in found
    assert [candidate for candidate, source, *_ in found if source == "ruwordnet"] == ["софа"]
    assert list(rows[0]) == ["word", "candidate", "source", "score", "in_core"]


def test_the_words_are_the_lemmas_of_the_core_without_stopwords_and_numbers(pulled: Path) -> None:
    rows = _report(pulled)

    assert list(dict.fromkeys(row["word"] for row in rows)) == ["диван", "софа", "кресло"]


def test_without_all_the_candidates_not_in_the_core_are_left_out(pulled: Path) -> None:
    assert all(row["in_core"] for row in _report(pulled))


def test_all_gives_the_candidates_not_in_the_core_marked_so_and_each_lemma_once(pulled: Path) -> None:
    found = _of(_report(pulled, "--all"), "диван")

    assert ("тахта", "ruwordnet", 1.0, False) in found
    assert ("тахта", "navec", 0.6, False) in found
    assert [candidate for candidate, source, *_ in found if source == "navec"] == ["софа", "тахта", "кресло"]
    assert [row[2] for row in found if row[1] == "navec"] == [0.8, 0.6, 0.0]


def test_top_limits_the_candidates_of_the_word_vectors(pulled: Path) -> None:
    found = _of(_report(pulled, "--all", "--top", "1"), "диван")

    assert [candidate for candidate, source, *_ in found if source == "navec"] == ["софа"]


def test_a_source_leaves_the_other_one_out(pulled: Path) -> None:
    assert {row["source"] for row in _report(pulled, "--source", "ruwordnet")} == {"ruwordnet"}
    assert {row["source"] for row in _report(pulled, "--source", "navec")} == {"navec"}


def test_as_synonyms_gives_the_file_of_synonyms_that_a_step_with_synonyms_reads(pulled: Path, tmp_path: Path) -> None:
    written = tmp_path / "synonyms.csv"
    result = semkit(
        "read", str(pulled), "synonym-candidates", "--source", "ruwordnet", "--as-synonyms", "write", str(written)
    )
    assert result.exit_code == 0, result.output

    table = pd.read_csv(written)
    assert list(table.columns) == ["word", "synonyms"]
    assert table.to_dict("records") == [{"word": "диван", "synonyms": "софа"}, {"word": "софа", "synonyms": "диван"}]
    minus = semkit("read", str(pulled), "add-minus-words", "--synonyms", str(written), "write", "-")
    assert [row["phrase"] for row in jsonl(minus.stdout)][:1] == ["диван -софа"]


def _error(*arguments: str) -> tuple[int, dict]:
    result = semkit("--json", "read", *arguments, "write", "out.csv")
    return result.exit_code, json.loads(result.stdout)["error"]


def test_data_not_in_the_cache_downloads_nothing_and_gives_the_pull_command(
    words_hub: LocalSource, core_csv: Path
) -> None:
    semkit("models", "pull", "ruwordnet")
    downloaded = list(words_hub.downloads)

    code, error = _error(str(core_csv), "synonym-candidates")

    assert code != 0
    assert error["code"] == "MODEL_NOT_PULLED"
    assert "semkit models pull navec" in error["action"]
    assert words_hub.downloads == downloaded


def test_a_source_the_step_lacks_is_refused_with_the_allowed_ones(words_hub: LocalSource, core_csv: Path) -> None:
    result = semkit("--json", "read", str(core_csv), "synonym-candidates", "--source", "nosuch", "write", "out.csv")

    assert result.exit_code == 2
    text = result.stdout + result.stderr
    assert all(name in text for name in ("nosuch", "ruwordnet", "navec", "both"))


def test_a_top_below_one_is_refused(pulled: Path) -> None:
    code, error = _error(str(pulled), "synonym-candidates", "--top", "0")

    assert code == 2
    assert "top" in error["message"]


def test_a_word_has_a_phrase_as_a_synonym_and_a_phrase_has_a_word(pulled: Path) -> None:
    rows = _phrases("растаможка авто", options=("--all", "--source", "ruwordnet"))

    found = _candidates(rows, "растаможка")
    assert "таможенное оформление" in found
    assert "таможенная очистка" in found
    assert ("таможенное оформление", "ruwordnet", 1.0, False) in _of(rows, "растаможка")
    assert "растаможка" in _candidates(
        _phrases("таможенное оформление авто", options=("--all", "--source", "ruwordnet")), "таможенное оформление"
    )


def test_a_phrase_of_the_thesaurus_is_in_core_when_a_phrase_of_the_core_holds_it_as_a_run(pulled: Path) -> None:
    rows = _phrases("растаможка авто", "таможенное оформление машины", options=("--source", "ruwordnet"))

    assert ("таможенное оформление", "ruwordnet", 1.0, True) in _of(rows, "растаможка")
    assert all(row["in_core"] for row in rows)


def test_the_unit_is_the_longest_sense_the_phrase_holds(pulled: Path) -> None:
    rows = _phrases("таможенное оформление товаров", options=("--all", "--source", "ruwordnet"))

    assert "растаможка" in _candidates(rows, "таможенное оформление товаров")
    assert {row["word"] for row in rows} == {"таможенное оформление товаров"}


def test_a_run_in_another_case_is_a_unit_and_a_sense_of_two_words_gives_its_synonyms(pulled: Path) -> None:
    rows = _phrases("таможенное оформление транспортного средства", options=("--all", "--source", "ruwordnet"))

    assert "растаможка" in _candidates(rows, "таможенное оформление")
    assert _candidates(rows, "транспортного средства") == ["средство передвижения", "транспорт"]


def test_a_phrase_that_is_no_sense_gives_no_row_for_the_whole_phrase(pulled: Path) -> None:
    rows = _phrases("растаможка авто", options=("--all",))

    assert "растаможка авто" not in {row["word"] for row in rows}


def test_the_words_inside_a_run_and_the_stopwords_are_no_units(pulled: Path) -> None:
    rows = _phrases("таможенное оформление грузов из индии", options=("--all", "--source", "ruwordnet"))

    assert {row["word"] for row in rows}.isdisjoint({"оформление", "таможенное", "из"})
    assert _candidates(rows, "таможенное оформление") != []


def test_a_word_inside_a_run_gets_no_candidates_of_its_own(pulled: Path) -> None:
    rows = _phrases("таможенное оформление", "оформление", options=("--all", "--source", "ruwordnet"))

    assert _candidates(rows, "оформление") == ["дизайн"]
    assert "дизайн" not in _candidates(rows, "таможенное оформление")


def _slots(*options: str, text: str = "таможенное оформление грузов из индии") -> list[dict]:
    return _phrases(text, options=("--all", "--as-slots", *options))


def test_on_a_tie_the_first_run_from_the_left_wins(pulled: Path) -> None:
    rows = _slots("--source", "ruwordnet", text="зима лето осень")

    assert rows[0] == {"slot_1": "зима лето", "slot_2": "осень"}


def test_a_sense_with_a_stopword_inside_is_one_unit(pulled: Path) -> None:
    rows = _slots("--source", "ruwordnet", text="оформить на таможне")

    assert rows[0] == {"slot_1": "оформить на таможне"}
    assert {row["slot_1"] for row in rows[1:]} == {
        "растаможка",
        "растаможивание",
        "растамаживать",
        "таможенное оформление",
        "таможенная очистка",
        "таможенное оформление товаров",
    }


def test_as_slots_gives_a_column_a_unit_with_the_unit_first_and_no_slot_for_a_stopword(pulled: Path) -> None:
    rows = _slots("--source", "ruwordnet")

    assert list(rows[0]) == ["slot_1", "slot_2", "slot_3"]
    assert rows[0] == {"slot_1": "таможенное оформление", "slot_2": "грузов", "slot_3": "индии"}
    assert "растаможка" in [row["slot_1"] for row in rows[1:]]
    assert {row["slot_2"] for row in rows[1:]} == {""}


def test_as_slots_refuses_a_core_of_two_phrases_and_as_synonyms_with_it(pulled: Path) -> None:
    two = semkit("read", "--text", "диван", "--text", "софа", "synonym-candidates", "--as-slots", "write", "-")
    both = semkit("read", "--text", "диван", "synonym-candidates", "--as-slots", "--as-synonyms", "write", "-")

    assert two.exit_code == 2
    assert both.exit_code == 2


def test_linear_combinations_takes_one_item_of_each_slot_and_the_first_is_the_phrase(pulled: Path) -> None:
    result = semkit(
        "read", "--text", "зима лето осень", "synonym-candidates", "--all", "--as-slots", "--source", "ruwordnet",
        "linear-combinations", "write", "-",
    )  # fmt: skip
    assert result.exit_code == 0, result.output

    rows = jsonl(result.stdout)
    assert rows[0]["phrase"] == "зима лето осень"
    assert {row["phrase"] for row in rows} == {"зима лето осень", "весна осень"}


def test_a_candidate_is_given_once_for_a_unit_whatever_the_senses(pulled: Path) -> None:
    rows = _phrases("растаможка", options=("--all", "--source", "ruwordnet"))

    assert _candidates(rows, "растаможка").count("растамаживать") == 1


def test_as_synonyms_holds_the_candidates_of_one_word_of_the_units_of_one_word_only(pulled: Path) -> None:
    rows = _phrases("растаможка", "таможенное оформление", options=("--all", "--source", "ruwordnet", "--as-synonyms"))

    assert {row["word"] for row in rows} == {"растаможка"}
    assert rows[0]["synonyms"] == "растаможивание растамаживать"
