"""Full names «Фамилия Имя Отчество» declined to five cases, the gender by the patronymic."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
import pytest

import rb_semkit as sk
from rb_semkit.core.errors import InvalidArguments


def _declined(names: Sequence[str | None], case: str) -> list[str]:
    return sk.decline_full_name(pd.Series(names), case).tolist()


def test_the_genitive_and_the_accusative_of_a_man_and_a_woman() -> None:
    names = ["Иванов Сергей Петрович", "Петрова Анна Ивановна"]

    assert _declined(names, "genitive") == ["Иванова Сергея Петровича", "Петровой Анны Ивановны"]
    assert _declined(names, "accusative") == ["Иванова Сергея Петровича", "Петрову Анну Ивановну"]


def test_a_name_in_ij_has_no_apostrophe_and_a_surname_in_oj_declines_as_an_adjective() -> None:
    assert _declined(["Толстой Дмитрий Ильич"], "genitive") == ["Толстого Дмитрия Ильича"]


def test_the_other_cases() -> None:
    name = ["петрова анна ивановна"]

    assert [_declined(name, case)[0] for case in ("dative", "instrumental", "prepositional")] == [
        "Петровой Анне Ивановне",
        "Петровой Анной Ивановной",
        "Петровой Анне Ивановне",
    ]


def test_an_empty_cell_stays_empty() -> None:
    assert _declined(["", None], "genitive") == ["", ""]


def test_a_value_that_is_not_three_words_stays_and_the_others_decline() -> None:
    names = ["Мамедов Эльчин Гусейн оглы", "Иванов Сергей", "Иванов Сергей Петрович"]

    assert _declined(names, "genitive") == ["Мамедов Эльчин Гусейн оглы", "Иванов Сергей", "Иванова Сергея Петровича"]


def test_a_surname_in_ykh_stays_and_one_in_a_declines() -> None:
    assert _declined(["Белых Никита Юрьевич", "Глинка Михаил Иванович"], "genitive") == [
        "Белых Никиты Юрьевича",
        "Глинки Михаила Ивановича",
    ]


def test_a_surname_with_yo_declines_and_keeps_it() -> None:
    assert _declined(["Королёва Наталья Кузьминична"], "genitive") == ["Королёвой Натальи Кузьминичны"]


def test_the_accusative_and_the_instrumental_of_a_man() -> None:
    name = ["Абрамович Роман Аркадьевич"]

    assert _declined(name, "accusative") == ["Абрамовича Романа Аркадьевича"]
    assert _declined(name, "instrumental") == ["Абрамовичем Романом Аркадьевичем"]


def test_the_nominative_is_no_case_of_a_full_name() -> None:
    with pytest.raises(InvalidArguments, match=r"^case='nominative'; allowed: 'genitive'"):
        _declined(["Иванов Сергей Петрович"], "nominative")
