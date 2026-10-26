"""The seam of the link sources: a test source plugs into relate_phrases through `Links`, and a module of the package
of sources with a list SOURCES is found."""

from __future__ import annotations

import sys
from collections.abc import Iterable
from pathlib import Path

import pandas as pd
import pytest

from rb_semkit.core.relate import relate_phrases
from rb_semkit.core.relate import sources as package
from rb_semkit.core.relate.sources import Links

Unit = tuple[str, ...]
COVER, THROW = ("чехол",), ("накидка",)
MACHINE, WASHER = ("стиральный", "машина"), ("стиралка",)


class Covers(Links):
    """Links чехол with накидка, and the run «стиральная машина» (one unit) with стиралка."""

    longest = 2
    pairs = ({COVER, THROW}, {MACHINE, WASHER})

    def knows(self, run: Unit) -> bool:
        return run == MACHINE

    def link(self, unit: Unit, other: Unit) -> str | None:
        return f"{' '.join(unit)}~{' '.join(other)} (test)" if {unit, other} in self.pairs else None

    def linked(self, unit: Unit) -> Iterable[Unit]:
        return [other for pair in self.pairs if unit in pair for other in pair - {unit}]


class Reading(Links):
    """Gives web the form веб, and links nothing."""

    def forms(self, word: str) -> Iterable[str]:
        return ["веб"] if word == "web" else []


class Web(Links):
    """Links веб with интернет; it knows nothing of web."""

    def link(self, unit: Unit, other: Unit) -> str | None:
        return "веб~интернет (test)" if {unit, other} == {("веб",), ("интернет",)} else None

    def linked(self, unit: Unit) -> Iterable[Unit]:
        return {("веб",): [("интернет",)], ("интернет",): [("веб",)]}.get(unit, [])


def _found(phrases: list[str], *links: Links) -> dict[str, tuple[str, str, str]]:
    table = relate_phrases(pd.Series(phrases), links=links)
    found = table.to_dict("records")
    return {phrase: (row["class"], row["of"], row["reason"]) for phrase, row in zip(phrases, found, strict=True)}


def test_a_linked_unit_makes_a_variation_with_the_reason_of_the_source() -> None:
    found = _found(["чехол на диван", "накидка на диван"], Covers())

    assert found["накидка на диван"] == ("variation", "чехол на диван", "накидка~чехол (test)")


def test_a_variation_is_found_through_the_linked_units_without_a_shared_word() -> None:
    found = _found(["чехол", "накидка"], Covers())

    assert found["накидка"] == ("variation", "чехол", "накидка~чехол (test)")


def test_a_run_of_words_the_source_knows_is_one_unit() -> None:
    found = _found(["ремонт стиральных машин", "ремонт стиралок"], Covers())
    alone = _found(["ремонт стиральных машин", "ремонт стиралок"])

    assert found["ремонт стиралок"] == ("variation", "ремонт стиральных машин", "стиралка~стиральный машина (test)")
    assert alone["ремонт стиралок"][0] == "other"


def test_a_refinement_works_through_a_linked_unit() -> None:
    found = _found(["чехол на диван", "накидка на угловой диван"], Covers())

    assert found["накидка на угловой диван"] == ("refinement", "чехол на диван", "+угловой; накидка~чехол (test)")


def test_the_lookups_of_a_source_try_the_forms_another_source_gives() -> None:
    found = _found(["интернет студия", "web студия"], Reading(), Web())
    alone = _found(["интернет студия", "web студия"], Web())

    assert found["web студия"] == ("variation", "интернет студия", "веб~интернет (test)")
    assert alone["web студия"][0] == "other"


def test_a_module_of_the_package_of_sources_with_a_list_sources_is_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "covers.py").write_text("SOURCES = ['the covers source']\n")
    monkeypatch.setattr(package, "__path__", [*package.__path__, str(tmp_path)])
    monkeypatch.delitem(sys.modules, f"{package.__name__}.covers", raising=False)
    package.sources.cache_clear()
    try:
        assert "the covers source" in package.sources()
    finally:
        package.sources.cache_clear()
        sys.modules.pop(f"{package.__name__}.covers", None)
