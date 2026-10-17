"""Nouns declined word by word: the 12 forms, the endings by the last letters, and words that do not change."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk
from rb_semkit.core.errors import InvalidArguments


def _declined(words: list[str], case: str, number: str = "singular") -> list[str]:
    return sk.decline_noun(pd.Series(words), case, number=number).tolist()


def test_the_genitive_singular_of_a_consonant_and_of_a_vowel_ending() -> None:
    assert _declined(["диван", "парк", "книга"], "genitive") == ["дивана", "парка", "книги"]


def test_the_genitive_plural() -> None:
    assert _declined(["диван"], "genitive", "plural") == ["диванов"]


def test_the_twelve_forms_of_a_noun() -> None:
    cases = ("nominative", "genitive", "dative", "accusative", "instrumental", "prepositional")
    forms = [_declined(["диван"], case, number)[0] for number in ("singular", "plural") for case in cases]

    # the accusative comes from the endings table only, which takes «-ван» as animate («Иван»)
    assert forms == [
        *("диван", "дивана", "дивану", "дивана", "диваном", "диване"),
        *("диваны", "диванов", "диванам", "диваны", "диванами", "диванах"),
    ]


def test_each_word_declines_with_its_capital_and_an_indeclinable_word_or_an_abbreviation_stays() -> None:
    assert _declined(["Москва", "МТС", "кафе"], "genitive") == ["Москвы", "МТС", "кафе"]
    assert _declined(["диван стол"], "dative") == ["дивану столу"]


def test_a_dataframe_gets_the_forms_in_a_new_column_and_empty_cells_stay_empty() -> None:
    table = pd.DataFrame({"phrase": ["диван", None]})

    result = sk.decline_noun(table, "genitive", column="phrase")

    assert result["phrase_decline_noun"].tolist() == ["дивана", ""]


@pytest.mark.parametrize(("argument", "kwargs"), [("case", {"case": "vocative"}), ("number", {"number": "dual"})])
def test_an_unknown_case_or_number_names_the_argument(argument: str, kwargs: dict) -> None:
    with pytest.raises(InvalidArguments, match=rf"^{argument}=.*allowed: 'nominative'|^{argument}=.*'singular'"):
        sk.decline_noun(pd.Series(["диван"]), **({"case": "genitive"} | kwargs))
