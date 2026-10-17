"""Adjectives declined word by word: every gender and the plural, 16 forms in all."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk
from rb_semkit.core.errors import InvalidArguments


def _declined(word: str, case: str, **form: str) -> str:
    return sk.decline_adjective(pd.Series([word]), case, **form).iloc[0]


def test_the_forms_of_the_acceptance() -> None:
    assert _declined("красный", "genitive") == "красного"
    assert _declined("красный", "accusative", gender="feminine") == "красную"
    assert _declined("красный", "genitive", gender="neuter") == "красного"
    assert _declined("красный", "genitive", number="plural") == "красных"


def test_the_neuter_oblique_cases_are_adjective_forms() -> None:
    cases = ("nominative", "genitive", "dative", "accusative", "instrumental", "prepositional")

    assert [_declined("красный", case, gender="neuter") for case in cases] == [
        *("красное", "красного", "красному", "красное", "красным", "красном"),
    ]


def test_the_feminine_forms() -> None:
    cases = ("nominative", "genitive", "dative", "accusative", "instrumental", "prepositional")

    assert [_declined("синий", case, gender="feminine") for case in cases] == [
        *("синяя", "синей", "синей", "синюю", "синей", "синей"),
    ]


def test_a_pronoun_of_the_exceptions_and_an_unknown_ending() -> None:
    assert _declined("этот", "dative") == "этому"
    assert _declined("диван", "genitive") == "диван"
    assert _declined("Красный", "instrumental", number="plural") == "Красными"


def test_an_unknown_gender_names_the_argument() -> None:
    with pytest.raises(InvalidArguments, match=r"^gender='common'; allowed: 'masculine', 'feminine', 'neuter'"):
        _declined("красный", "genitive", gender="common")


def test_soft_ordinal_and_possessive_adjectives() -> None:
    assert _declined("синий", "nominative", gender="neuter") == "синее"
    assert _declined("третий", "nominative", gender="feminine") == "третья"
    assert _declined("третий", "accusative", number="plural") == "третьи"
    assert _declined("лисий", "nominative", number="plural") == "лисьи"
