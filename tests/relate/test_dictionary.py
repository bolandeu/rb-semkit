"""The link source dictionary through the pipeline: RuWordNet links two units of one synset or of a POS-synonymy pair,
one step only; a run of words the thesaurus knows as one sense is a unit, by lemmas, hyphenated or glued."""

from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import SENSES
from .runner import relate


def test_a_noun_and_its_verbs_are_variations_by_the_pos_synonymy_and_the_aspect_pair_by_the_synset(
    tmp_path: Path,
) -> None:
    found = relate(tmp_path, ["создание сайтов", "создать сайт", "создавать сайты"])
    aspect = relate(tmp_path, ["создать сайт", "создавать сайты"])

    assert found["создать сайт"] == (
        "variation",
        "создание сайтов",
        "создание сайтов",
        "создать~создание (pos_synonymy)",
    )
    assert found["создавать сайты"] == (
        "variation",
        "создание сайтов",
        "создание сайтов",
        "создавать~создание (pos_synonymy)",
    )
    assert aspect["создавать сайты"] == ("variation", "создать сайт", "создать сайт", "создавать~создать (synset)")


@pytest.mark.parametrize(
    ("first", "later", "reason"),
    [
        ("разработка сайтов", "разработать сайт", "разработать~разработка (pos_synonymy)"),
        ("ремонт стиральных машин", "отремонтировать стиральную машину", "отремонтировать~ремонт (pos_synonymy)"),
        (
            "отремонтировать стиральную машину",
            "ремонтировать стиральные машины",
            "ремонтировать~отремонтировать (synset)",
        ),
    ],
)
def test_a_noun_and_its_verb_are_a_variation_in_either_direction_of_the_pair(
    tmp_path: Path, first: str, later: str, reason: str
) -> None:
    found = relate(tmp_path, [first, later])

    assert found[later] == ("variation", first, first, reason)


@pytest.mark.parametrize(
    ("first", "later", "reason"),
    [
        ("разработка сайтов", "разработка веб сайтов", "веб-сайт~сайт (synset)"),
        ("разработка сайтов", "разработка интернет сайтов", "интернет-сайт~сайт (synset)"),
        ("ремонт стиральных машин", "ремонтные работы стиральных машин", "ремонтные работы~ремонт (synset)"),
        ("ремонт стиральных машин", "ремонт стиралок", "стиралка~стиральная машина (synset)"),
    ],
)
def test_a_run_the_thesaurus_knows_as_one_sense_is_a_unit(tmp_path: Path, first: str, later: str, reason: str) -> None:
    found = relate(tmp_path, [first, later])

    assert found[later] == ("variation", first, first, reason)


def test_a_run_is_found_glued_when_the_thesaurus_has_no_hyphen(tmp_path: Path, use_senses) -> None:
    use_senses([sense for sense in SENSES if sense[1] != "ВЕБ-САЙТ"])

    found = relate(tmp_path, ["разработка сайтов", "разработка веб сайтов"])

    assert found["разработка веб сайтов"] == (
        "variation",
        "разработка сайтов",
        "разработка сайтов",
        "вебсайт~сайт (synset)",
    )


def test_a_run_of_a_later_phrase_links_to_a_word_of_an_earlier_one_either_way(tmp_path: Path) -> None:
    found = relate(tmp_path, ["разработка веб сайтов", "разработка сайтов"])

    assert found["разработка сайтов"] == (
        "variation",
        "разработка веб сайтов",
        "разработка веб сайтов",
        "сайт~веб-сайт (synset)",
    )


def test_a_derivation_pair_alone_is_no_link(tmp_path: Path) -> None:
    found = relate(tmp_path, ["купить диван", "покупатель дивана"])

    assert found["покупатель дивана"] == ("other", "", "покупатель дивана", "unlinked: покупатель | купить")


def test_a_link_of_a_link_is_no_link(tmp_path: Path) -> None:
    bribe = relate(tmp_path, ["подкупить диван", "купить диван"])
    stock = relate(tmp_path, ["купить диван", "накупить диван"])
    chain = relate(tmp_path, ["подкупить диван", "накупить диван"])

    assert bribe["купить диван"][:2] == ("variation", "подкупить диван")
    assert stock["накупить диван"][:2] == ("variation", "купить диван")
    assert chain["накупить диван"] == ("other", "", "накупить диван", "unlinked: накупить | подкупить")


@pytest.mark.parametrize(
    ("first", "later", "reason"),
    [
        ("косметическая починка обуви", "косметический ремонт обуви", "ремонт обуви~починка обуви (synset)"),
        ("косметический ремонт обуви", "косметическая починка обуви", "починка обуви~ремонт обуви (synset)"),
    ],
)
def test_of_overlapping_runs_the_cut_that_explains_the_most_words_wins_in_either_phrase(
    tmp_path: Path, first: str, later: str, reason: str
) -> None:
    found = relate(tmp_path, [first, later])

    assert found[later] == ("variation", first, first, reason)
