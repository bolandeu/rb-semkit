"""The link source «latin»: the reading of a Latin word and the links by sound, alone and through relate-phrases."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from rb_semkit.core.relate import relate_phrases
from rb_semkit.core.relate.sources import Links
from rb_semkit.core.relate.sources.latin import SOURCES

from .runner import relate

Unit = tuple[str, ...]


def _latin() -> Links:
    links = SOURCES[0].prepare({}, Path())
    assert links is not None
    return links


def _found(phrases: list[str], *links: Links) -> dict[str, tuple[str, str, str]]:
    table = relate_phrases(pd.Series(phrases), links=[_latin(), *links])
    found = table.to_dict("records")
    return {phrase: (row["class"], row["of"], row["reason"]) for phrase, row in zip(phrases, found, strict=True)}


class Sites(Links):
    """Knows the run «веб сайт» as one unit, and links it with «интернет сайт»."""

    longest = 2
    run, other = ("веб", "сайт"), ("интернет", "сайт")

    def knows(self, run: Unit) -> bool:
        return run in (self.run, self.other)

    def link(self, unit: Unit, other: Unit) -> str | None:
        return "веб сайт~интернет сайт (test)" if {unit, other} == {self.run, self.other} else None

    def linked(self, unit: Unit) -> Iterable[Unit]:
        return {self.run: [self.other], self.other: [self.run]}.get(unit, [])


def test_the_reading_of_a_latin_word_and_the_words_that_have_none() -> None:
    links = _latin()

    assert list(links.forms("web")) == ["веб"]
    assert list(links.forms("wordpress")) == ["вордпресс"]
    assert links.link(("bosch",), ("бош",)) == "bosch~бош (latin)"
    assert links.link(("бош",), ("bosch",)) == "bosch~бош (latin)"
    assert links.link(("iphone",), ("бош",)) is None
    assert list(links.forms("a1")) == [] and list(links.forms("сайт")) == [] and list(links.forms("сайт1")) == []
    assert links.link(("a1",), ("а1",)) is None and links.link(("сайт",), ("сайт",)) is None


def test_a_cyrillic_word_is_linked_to_the_latin_word_of_the_table_before_it() -> None:
    found = _found(["как создать сайт на wordpress", "как создать сайт на вордпресс"])

    assert found["как создать сайт на вордпресс"] == (
        "variation",
        "как создать сайт на wordpress",
        "wordpress~вордпресс (latin)",
    )


def test_a_latin_word_is_a_variation_of_the_cyrillic_phrase_before_it() -> None:
    found = _found(["ремонт стиральных машин бош", "ремонт стиральных машин bosch"])

    assert found["ремонт стиральных машин bosch"][:3] == (
        "variation",
        "ремонт стиральных машин бош",
        "bosch~бош (latin)",
    )


def test_the_variation_comes_before_the_refinement() -> None:
    phrases = ["ремонт стиральных машин", "ремонт стиральных машин бош", "ремонт стиральных машин bosch"]

    found = _found(phrases)

    assert found[phrases[2]][:2] == ("variation", phrases[1])


def test_without_the_cyrillic_phrase_the_latin_word_is_a_refinement() -> None:
    found = _found(["ремонт стиральных машин", "ремонт стиральных машин bosch"])

    assert found["ремонт стиральных машин bosch"] == ("refinement", "ремонт стиральных машин", "+bosch")


def test_a_latin_word_without_a_cyrillic_match_is_an_extra_unit() -> None:
    found = _found(["ремонт", "ремонт iphone"])

    assert found["ремонт iphone"] == ("refinement", "ремонт", "+iphone")


def test_the_reading_is_a_form_that_the_lookup_of_a_run_by_another_source_tries() -> None:
    found = _found(["разработка интернет сайтов", "разработка web сайтов"], Sites())

    assert found["разработка web сайтов"][:2] == ("variation", "разработка интернет сайтов")


def test_the_step_links_the_latin_word_by_itself(tmp_path: Path) -> None:
    found = relate(tmp_path, ["ремонт стиральных машин бош", "ремонт стиральных машин bosch"])

    assert found["ремонт стиральных машин bosch"][0] == "variation"
    assert found["ремонт стиральных машин bosch"][3] == "bosch~бош (latin)"
