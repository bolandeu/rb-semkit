"""relate-phrases in a pipeline: the classes, of, group and reason over the lemmas of the words."""

from __future__ import annotations

from pathlib import Path

from .runner import relate, rows


def test_the_same_lemmas_in_any_order_are_same_of_the_first(tmp_path: Path) -> None:
    found = relate(tmp_path, ["ремонт стиральных машин", "стиральная машина ремонт", "ремонт стиральной машины"])

    assert found["стиральная машина ремонт"][:2] == ("same", "ремонт стиральных машин")
    assert found["ремонт стиральной машины"][:2] == ("same", "ремонт стиральных машин")
    assert found["стиральная машина ремонт"][3] == found["ремонт стиральной машины"][3] == "lemmas"
    assert found["ремонт стиральных машин"][:2] == ("other", "")
    assert {group for _, _, group, _ in found.values()} == {"ремонт стиральных машин"}


def test_extra_units_make_a_refinement_and_a_preposition_is_no_unit(tmp_path: Path) -> None:
    found = relate(
        tmp_path, ["разработка сайтов", "разработка сайтов москва", "разработка сайтов под ключ", "разработка 2 сайтов"]
    )

    assert found["разработка сайтов москва"] == ("refinement", "разработка сайтов", "разработка сайтов", "+москва")
    assert found["разработка сайтов под ключ"] == ("refinement", "разработка сайтов", "разработка сайтов", "+ключ")
    assert found["разработка 2 сайтов"] == ("refinement", "разработка сайтов", "разработка сайтов", "+2")


def test_a_refinement_does_not_depend_on_the_order_of_the_rows(tmp_path: Path) -> None:
    first = relate(tmp_path, ["как сделать сайт", "сделать сайт"])
    reverse = relate(tmp_path, ["сделать сайт", "как сделать сайт"])

    assert first["как сделать сайт"] == ("refinement", "сделать сайт", "как сделать сайт", "+как")
    assert first["сделать сайт"][:3] == ("other", "", "как сделать сайт")
    assert reverse["как сделать сайт"] == ("refinement", "сделать сайт", "сделать сайт", "+как")
    assert reverse["сделать сайт"][:3] == ("other", "", "сделать сайт")


def test_a_word_to_keep_stays_and_a_preposition_does_not_change_the_class(tmp_path: Path) -> None:
    without = relate(tmp_path, ["купить диван", "купить же диван"])
    kept = relate(tmp_path, ["купить диван", "купить же диван"], "--keep", "же")
    prepositions = relate(tmp_path, ["диван москва", "диван в москве", "диван на москве"])

    assert without["купить же диван"][0] == "same"
    assert kept["купить же диван"] == ("refinement", "купить диван", "купить диван", "+же")
    assert prepositions["диван в москве"][:2] == ("same", "диван москва")
    assert prepositions["диван на москве"][:2] == ("same", "диван москва")


def test_a_refinement_goes_to_the_closest_base_and_the_group_to_the_first_row(tmp_path: Path) -> None:
    found = relate(tmp_path, ["диван", "как выбрать угловой диван", "угловой диван"])

    assert found["угловой диван"][:3] == ("refinement", "диван", "диван")
    assert found["как выбрать угловой диван"][:3] == ("refinement", "угловой диван", "диван")
    assert found["диван"][:3] == ("other", "", "диван")
    assert found["диван"][3] == "base of: угловой диван"


def test_unrelated_phrases_are_other_with_the_unlinked_words(tmp_path: Path) -> None:
    found = relate(tmp_path, ["купить диван", "ремонт стиральных машин"])

    assert found["ремонт стиральных машин"] == (
        "other",
        "",
        "ремонт стиральных машин",
        "unlinked: ремонт, стиральный машина",
    )


def test_the_unlinked_words_name_both_sides_of_the_nearest_phrase(tmp_path: Path) -> None:
    found = relate(tmp_path, ["создание сайтов", "разработка сайтов"])

    assert found["разработка сайтов"] == ("other", "", "разработка сайтов", "unlinked: разработка | создание")


def test_a_copy_an_empty_cell_and_a_single_row(tmp_path: Path) -> None:
    found = rows(tmp_path, ["диван", "диван", ""])
    single = rows(tmp_path, ["диван"])

    assert found[1] == ("same", "диван", "диван", "lemmas")
    assert found[2][:3] == ("other", "", "")
    assert single[0][:3] == ("other", "", "диван")
