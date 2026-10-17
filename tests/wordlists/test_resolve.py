"""The resolver: the project's folder, the config's folders, SEMKIT_LISTS, the bundled lists; sk.word_list."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pytest

import rb_semkit as sk
from rb_semkit.core import services, wordlists
from rb_semkit.core.errors import InvalidArguments

from .conftest import set_config_lists, write_list

MEBEL = "# Мебель: минус-слова\nбу\nдешевый\n"


def _by_name() -> dict[str, wordlists.catalog.WordList]:
    return {entry.name: entry for entry in wordlists.names()}


def test_a_bundled_list_has_its_description_source_and_lines(home: Path) -> None:
    cheap = _by_name()["minus/cheap"]

    assert cheap.source == "bundled"
    assert cheap.lines == 28
    assert cheap.description
    assert wordlists.resolve("minus/cheap")[:3] == ["недорого", "недорогой", "акционный"]


def test_the_add_ins_lists_have_names_in_the_same_scheme(home: Path) -> None:
    by_name = _by_name()

    assert {"stop/semtools", "markers/geo", "markers/MO", "stop/wordstat", "combine/tourism/turkey"} <= set(by_name)
    assert "и" in wordlists.resolve("stop/semtools")
    assert "Москва" in wordlists.resolve("markers/geo")


def test_a_list_of_a_folder_from_the_config_with_its_description(project: Path, home: Path) -> None:
    write_list(home / "x", "niche/mebel", MEBEL)
    set_config_lists(project, ["~/x"])

    entry = _by_name()["niche/mebel"]

    assert wordlists.resolve("niche/mebel") == ["бу", "дешевый"]
    assert (entry.source, entry.lines, entry.description) == ("~/x", 2, "Мебель: минус-слова")


def test_a_list_of_a_folder_from_semkit_lists(home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_list(home / "x", "niche/mebel", MEBEL)
    write_list(home / "y", "niche/oil", "нефть\n")
    monkeypatch.setenv("SEMKIT_LISTS", f"~/x{os.pathsep}~/y")

    assert wordlists.resolve("niche/mebel") == ["бу", "дешевый"]
    assert wordlists.resolve("niche/oil") == ["нефть"]
    assert _by_name()["niche/oil"].source == "~/y"


def test_a_list_without_a_description_line(home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_list(home / "x", "plain", "﻿один\r\n\r\n  два  \r\n# не описание\n")
    monkeypatch.setenv("SEMKIT_LISTS", str(home / "x"))

    assert wordlists.resolve("plain") == ["один", "два", "# не описание"]
    assert _by_name()["plain"].description == ""


def test_the_project_list_wins_over_semkit_lists_then_the_config_then_the_bundled(
    project: Path, home: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_list(services.project_lists_dir(project), "minus/cheap", "project\n")
    write_list(home / "x", "minus/cheap", "config\n")
    write_list(home / "x", "minus/free", "config\n")
    write_list(home / "x", "minus/countries", "config\n")
    write_list(home / "y", "minus/free", "env\n")
    write_list(home / "y", "minus/computer", "env\n")
    set_config_lists(project, ["~/x"])
    monkeypatch.setenv("SEMKIT_LISTS", str(home / "y"))

    assert wordlists.resolve("minus/cheap") == ["project"]
    assert wordlists.resolve("minus/free") == ["env"]
    assert wordlists.resolve("minus/computer") == ["env"]
    assert wordlists.resolve("minus/countries") == ["config"]
    assert _by_name()["minus/cheap"].source == "project"
    assert len([entry for entry in wordlists.names() if entry.name == "minus/cheap"]) == 1


def test_a_relative_folder_of_the_config_is_relative_to_the_project(project: Path) -> None:
    write_list(project / "lists-here", "a", "x\n")
    set_config_lists(project, ["lists-here"])

    assert wordlists.resolve("a") == ["x"]


def test_the_project_is_found_from_a_folder_below_it(project: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_list(services.project_lists_dir(project), "a", "x\n")
    (project / "sub").mkdir()
    monkeypatch.chdir(project / "sub")

    assert wordlists.resolve("a") == ["x"]


def test_describe_gives_the_list_without_its_items(project: Path) -> None:
    write_list(services.project_lists_dir(project), "a", "# Моя\nx\ny\n")

    assert wordlists.describe("a") == wordlists.catalog.WordList("a", "project", 2, "Моя")


def test_word_list_is_a_series_of_the_items(home: Path) -> None:
    series = sk.word_list("minus/free")

    assert isinstance(series, pd.Series)
    assert series.tolist()[:2] == ["бесплатно", "бесплатный"]
    assert len(series) == 26


def test_an_unknown_name_raises_with_the_close_names(home: Path) -> None:
    with pytest.raises(InvalidArguments) as error:
        sk.word_list("minus/chep")

    assert "minus/cheap" in error.value.message


@pytest.mark.parametrize("name", ["", "../x", "/etc/passwd", "a.txt"])
def test_a_name_that_is_not_a_relative_path_without_suffix_is_refused(home: Path, name: str) -> None:
    with pytest.raises(InvalidArguments):
        wordlists.resolve(name)


def test_the_meaning_list_of_non_refining_words_is_bundled_with_its_russian_description(home: Path) -> None:
    neutral = _by_name()["meaning/neutral"]

    assert neutral.source == "bundled"
    assert "распродажа" in wordlists.resolve("meaning/neutral")
    assert "новинка" not in wordlists.resolve("meaning/neutral")
    assert neutral.description.startswith("Неуточняющие слова")


def test_the_description_of_the_semtools_stop_list_does_not_name_the_add_in(home: Path) -> None:
    assert _by_name()["stop/semtools"].description == "Стоп-слова: предлоги, союзы, частицы"
