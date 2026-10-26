"""relate-phrases --synonyms: the groups of synonyms of the caller, through the pipeline."""

from __future__ import annotations

from pathlib import Path

from ..pipeline.runner import semkit
from .runner import relate, table

REPAIR = "ремонт | починка | ремонтировать | починить"
MACHINE = "стиральная машина | стиралка | стиральная машинка"


def _groups(tmp_path: Path, *groups: str) -> str:
    path = tmp_path / "groups.csv"
    path.write_text("synonyms\n" + "".join(f'"{group}"\n' for group in groups))
    return str(path)


def test_an_item_of_a_group_makes_a_variation_with_the_reason_of_the_pair(tmp_path: Path) -> None:
    found = relate(
        tmp_path, ["ремонт стиральных машин", "починить стиральную машину"], "--synonyms", _groups(tmp_path, REPAIR)
    )

    assert found["починить стиральную машину"] == (
        "variation",
        "ремонт стиральных машин",
        "ремонт стиральных машин",
        "починить~ремонт (synonyms)",
    )


def test_an_item_of_several_words_is_matched_as_a_run(tmp_path: Path, use_senses) -> None:
    use_senses([])  # the dictionary links стиралка too, and its reason would come first
    phrases = ["ремонт стиральных машин", "ремонт стиралки", "ремонт стиральной машинки"]

    found = relate(tmp_path, phrases, "--synonyms", _groups(tmp_path, MACHINE))

    assert [found[phrase][0] for phrase in phrases[1:]] == ["variation", "variation"]
    assert found["ремонт стиралки"][3] == "стиралка~стиральный машина (synonyms)"
    assert found["ремонт стиральной машинки"][3] == "стиральный машина~стиральный машинка (synonyms)"


def test_the_columns_word_and_synonyms_give_the_same_groups(tmp_path: Path) -> None:
    path = tmp_path / "dupes.csv"
    path.write_text("word,synonyms\nремонт,починка ремонтировать починить\n")
    phrases = ["ремонт стиральных машин", "починить стиральную машину"]

    found = relate(tmp_path, phrases, "--synonyms", str(path))

    assert found == relate(tmp_path, phrases, "--synonyms", _groups(tmp_path, REPAIR))


def test_groups_are_not_chained_and_a_word_of_two_groups_links_through_both(tmp_path: Path) -> None:
    groups = _groups(tmp_path, "ремонт | починка", "починка | наладка")

    chained = relate(tmp_path, ["ремонт х", "наладка х"], "--synonyms", groups)
    both = relate(tmp_path, ["починка х", "ремонт х", "наладка х"], "--synonyms", groups)

    assert chained["наладка х"][0] == "other"
    assert both["ремонт х"] == ("variation", "починка х", "починка х", "починка~ремонт (synonyms)")
    assert both["наладка х"] == ("variation", "починка х", "починка х", "наладка~починка (synonyms)")


def test_a_group_of_one_item_is_ignored(tmp_path: Path) -> None:
    found = relate(tmp_path, ["ремонт х", "починка х"], "--synonyms", _groups(tmp_path, "ремонт", "починка"))

    assert found["починка х"][0] == "other"


def test_a_file_with_neither_shape_is_refused_with_the_missing_column(tmp_path: Path) -> None:
    path = tmp_path / "other.csv"
    path.write_text("phrase\nремонт\n")

    result = semkit("read", str(table(tmp_path, ["ремонт"])), "relate-phrases", "--synonyms", str(path), "write", "-")

    assert result.exit_code != 0
    assert "'synonyms'" in result.output


def test_an_unreadable_file_is_refused_with_its_path(tmp_path: Path) -> None:
    path = tmp_path / "missing.csv"

    result = semkit("read", str(table(tmp_path, ["ремонт"])), "relate-phrases", "--synonyms", str(path), "write", "-")

    assert result.exit_code != 0
    assert str(path) in "".join(result.output.split())  # the terminal wraps the long path
