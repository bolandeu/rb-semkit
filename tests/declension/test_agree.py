"""sk.agree: the words of a phrase put in agreement by the rules on neighbouring words."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import rb_semkit as sk

from ..pipeline.runner import jsonl, semkit


def _agreed(phrases: list[str]) -> list[str]:
    return sk.agree(pd.Series(phrases))["agreed"].tolist()


def _notes(phrases: list[str]) -> list[str]:
    return sk.agree(pd.Series(phrases))["agree_note"].tolist()


def test_a_noun_after_a_verb_goes_to_the_accusative() -> None:
    assert _agreed(["растаможить машина"]) == ["растаможить машину"]


def test_a_noun_group_after_a_noun_goes_to_the_genitive() -> None:
    assert _agreed(["растаможка автомобиль", "таможенное оформление автомобиль"]) == [
        "растаможка автомобиля",
        "таможенное оформление автомобиля",
    ]


def test_an_adjective_takes_the_gender_number_and_case_of_its_noun() -> None:
    assert _agreed(["легковой машина", "купить рыжий кот"]) == ["легковая машина", "купить рыжего кота"]


def test_a_noun_after_a_preposition_takes_its_case_and_an_indeclinable_word_stays() -> None:
    assert _agreed(["растаможка авто из германия"]) == ["растаможка авто из германии"]


def test_a_preposition_of_the_table_gives_its_case() -> None:
    assert _agreed(["подарок к новый год", "доставка с водитель", "машина для семья"]) == [
        "подарок к новому году",
        "доставка с водителем",
        "машина для семьи",
    ]


def test_v_and_na_give_the_prepositional_for_a_place_and_keep_the_accusative_already_there() -> None:
    assert _agreed(["купить диван в москва", "купить в кредит"]) == ["купить диван в москве", "купить в кредит"]


def test_phrases_that_agree_already_stay_with_an_empty_note() -> None:
    phrases = ["растаможка авто", "купить диван", "растаможить машину", "легковая машина"]

    assert _agreed(phrases) == phrases
    assert _notes(phrases) == ["", "", "", ""]


def test_the_note_of_an_agreed_phrase_is_empty() -> None:
    assert _notes(["растаможить машина"]) == [""]


def test_a_phrase_no_rule_fits_stays_and_the_note_names_the_reason() -> None:
    phrases = ["машина купить", "быстро растаможить машина", "купить легковой"]

    assert _agreed(phrases) == phrases
    assert _notes(phrases) == [
        "no rule for «машина купить»",
        "no rule for «быстро»",
        "«легковой» has no noun after it",
    ]


def test_an_unsure_rule_keeps_the_phrase_and_the_note_names_the_reason() -> None:
    phrases = ["лекарство в аптека", "доставка по город", "купить машиной"]

    assert _agreed(phrases) == phrases
    assert _notes(phrases) == [
        "the case after «в» is unsure: «аптека» is no toponym",
        "no case for the preposition «по»",
        "«машиной» is in another case",
    ]


def test_a_word_keeps_its_capitals_and_an_empty_phrase_stays() -> None:
    assert _agreed(["Растаможить Машина", ""]) == ["Растаможить Машину", ""]


def test_a_table_gets_the_columns_right_after_its_column() -> None:
    table = pd.DataFrame({"phrase": ["растаможить машина"], "count": [3]})

    found = sk.agree(table, column="phrase")

    assert found.columns.tolist() == ["phrase", "agreed", "agree_note", "count"]
    assert found["agreed"].tolist() == ["растаможить машину"]


def test_linear_combinations_then_agree_through_the_command_line(tmp_path: Path) -> None:
    source = tmp_path / "combine.csv"
    pd.DataFrame({"a": ["растаможить", "растаможка"], "b": ["машина", "автомобиль"]}).to_csv(source, index=False)

    result = semkit("read", str(source), "linear-combinations", "agree", "write", "-")

    assert result.exit_code == 0, result.output
    assert [(row["phrase"], row["agree_note"]) for row in jsonl(result.stdout)] == [
        ("растаможить машину", ""),
        ("растаможить автомобиль", ""),
        ("растаможка машины", ""),
        ("растаможка автомобиля", ""),
    ]
    assert list(jsonl(result.stdout)[0]) == ["phrase", "agree_note", "a", "b"]


def test_agree_as_writes_a_new_column_and_the_note_after_it(tmp_path: Path) -> None:
    source = tmp_path / "core.csv"
    pd.DataFrame({"phrase": ["машина купить"]}).to_csv(source, index=False)

    result = semkit("read", str(source), "agree", "--as", "agreed", "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [
        {"phrase": "машина купить", "agreed": "машина купить", "agree_note": "no rule for «машина купить»"}
    ]
