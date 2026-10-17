"""semkit lists, lists show, lists add, lists rm; a list as an item argument of a step and in the help."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rb_semkit.core import services
from tests.pipeline.runner import CORE, jsonl, semkit

from .conftest import set_config_lists, write_list

MEBEL = "# Мебель: минус-слова\nбу\nдешевый\n"


def _lists() -> dict[str, dict]:
    result = semkit("--json", "lists")
    assert result.exit_code == 0, result.output
    return {entry["name"]: entry for entry in json.loads(result.stdout)["lists"]}


def _core(tmp_path: Path) -> Path:
    path = tmp_path / "core.csv"
    path.write_text("phrase\n" + "\n".join(CORE) + "\n", encoding="utf-8")
    return path


def test_lists_json_holds_the_bundled_lists(home: Path) -> None:
    lists = _lists()

    cheap = lists["minus/cheap"]
    assert cheap["source"] == "bundled" and cheap["lines"] > 0 and cheap["description"]
    assert {"stop/wordstat", "combine/tourism/turkey", "stop/semtools", "markers/geo"} <= set(lists)
    assert len(lists) == 86


def test_lists_in_human_form_shows_a_table(home: Path) -> None:
    result = semkit("lists")

    assert result.exit_code == 0, result.output
    assert "minus/cheap" in result.output and "bundled" in result.output


def test_a_list_of_the_config_is_shown_with_its_description_and_source(project: Path, home: Path) -> None:
    write_list(home / "x", "niche/mebel", MEBEL)
    set_config_lists(project, ["~/x"])

    assert _lists()["niche/mebel"] == {
        "name": "niche/mebel",
        "source": "~/x",
        "lines": 2,
        "description": "Мебель: минус-слова",
    }


def test_a_list_of_semkit_lists_is_a_step_item(home: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_list(home / "x", "niche/mebel", "угловой\n")
    monkeypatch.setenv("SEMKIT_LISTS", "~/x")

    result = semkit("read", str(_core(tmp_path)), "drop-words", "--items", "@niche/mebel", "write", "-")

    assert [row["phrase"] for row in jsonl(result.stdout)] == [
        "купить диван",
        "диван",
        "угловые диваны",
        "диван недорого",
    ]


def test_a_bundled_list_drops_the_phrases_with_its_items(home: Path, tmp_path: Path) -> None:
    source = tmp_path / "core.csv"
    source.write_text("phrase\nдиван\nдиван дешево\nкупить диван по дешевке\nугловой диван\n", encoding="utf-8")

    result = semkit("read", str(source), "drop-phrases", "--items", "@minus/cheap", "write", "-")

    assert result.exit_code == 0, result.output
    assert [row["phrase"] for row in jsonl(result.stdout)] == ["диван", "угловой диван"]


def test_show_prints_the_items(project: Path) -> None:
    write_list(services.project_lists_dir(project), "a", "# Моя\nx\ny\n")

    assert semkit("lists", "show", "a").stdout == "x\ny\n"
    payload = json.loads(semkit("--json", "lists", "show", "a").stdout)
    assert (payload["items"], payload["source"], payload["description"]) == (["x", "y"], "project", "Моя")


def test_show_of_an_unknown_name_is_refused_with_the_close_names(home: Path) -> None:
    result = semkit("--json", "lists", "show", "minus/chep")

    assert result.exit_code == 2
    assert "minus/cheap" in json.loads(result.stdout)["error"]["message"]


def test_add_copies_the_file_into_the_project_and_the_list_resolves(project: Path, tmp_path: Path) -> None:
    source = tmp_path / "f.txt"
    source.write_text(MEBEL, encoding="utf-8")

    result = semkit("--json", "lists", "add", "niche/x", str(source))

    assert result.exit_code == 0, result.output
    assert (services.project_lists_dir(project) / "niche" / "x.txt").read_text(encoding="utf-8") == MEBEL
    assert _lists()["niche/x"]["source"] == "project"


def test_add_to_a_folder_by_path(project: Path, home: Path, tmp_path: Path) -> None:
    source = tmp_path / "f.txt"
    source.write_text("a\n", encoding="utf-8")

    assert semkit("lists", "add", "niche/x", str(source), "--to", "~/shared").exit_code == 0
    assert (home / "shared" / "niche" / "x.txt").read_text(encoding="utf-8") == "a\n"


def test_add_refuses_an_existing_name_naming_replace_and_replace_overwrites(project: Path, tmp_path: Path) -> None:
    source = tmp_path / "f.txt"
    source.write_text("one\n", encoding="utf-8")
    semkit("lists", "add", "niche/x", str(source))
    source.write_text("two\n", encoding="utf-8")

    refused = semkit("--json", "lists", "add", "niche/x", str(source))
    assert refused.exit_code == 2
    assert "--replace" in json.loads(refused.stdout)["error"]["message"]
    assert semkit("lists", "show", "niche/x").stdout == "one\n"

    assert semkit("lists", "add", "niche/x", str(source), "--replace").exit_code == 0
    assert semkit("lists", "show", "niche/x").stdout == "two\n"


def test_add_of_a_missing_file_is_refused(project: Path, tmp_path: Path) -> None:
    result = semkit("lists", "add", "niche/x", str(tmp_path / "none.txt"))

    assert result.exit_code == 2
    assert not services.project_lists_dir(project).exists()


def test_add_outside_a_project_is_refused(home: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.chdir(bare)
    source = tmp_path / "f.txt"
    source.write_text("a\n", encoding="utf-8")

    assert semkit("lists", "add", "niche/x", str(source)).exit_code == 4


def test_dry_run_changes_nothing(project: Path, tmp_path: Path) -> None:
    source = tmp_path / "f.txt"
    source.write_text("a\n", encoding="utf-8")

    added = semkit("--json", "lists", "add", "niche/x", str(source), "--dry-run")
    assert json.loads(added.stdout)["dry_run"] is True
    assert not services.project_lists_dir(project).exists()

    semkit("lists", "add", "niche/x", str(source))
    removed = semkit("--json", "lists", "rm", "niche/x", "--dry-run")
    assert json.loads(removed.stdout)["dry_run"] is True
    assert (services.project_lists_dir(project) / "niche" / "x.txt").is_file()


def test_rm_removes_the_list_and_the_folders_left_empty(project: Path) -> None:
    write_list(services.project_lists_dir(project), "niche/x", "a\n")

    assert semkit("lists", "rm", "niche/x").exit_code == 0
    assert not (services.project_lists_dir(project) / "niche").exists()
    assert services.project_lists_dir(project).is_dir()


def test_rm_from_a_folder_by_path(project: Path, home: Path) -> None:
    write_list(home / "shared", "a", "x\n")

    assert semkit("lists", "rm", "a", "--from", "~/shared").exit_code == 0
    assert not (home / "shared" / "a.txt").exists()


def test_rm_of_a_bundled_list_is_refused_saying_so(project: Path) -> None:
    result = semkit("--json", "lists", "rm", "minus/cheap")

    assert result.exit_code == 2
    assert "bundled" in json.loads(result.stdout)["error"]["message"]
    assert "minus/cheap" in _lists()


def test_rm_of_a_list_that_is_not_there_is_refused(project: Path) -> None:
    assert semkit("lists", "rm", "niche/none").exit_code == 2


def test_the_end_of_a_step_help_lists_the_available_names(project: Path, home: Path) -> None:
    write_list(home / "x", "niche/mebel", MEBEL)
    set_config_lists(project, ["~/x"])

    result = semkit("read", "IN", "drop-words", "--help")

    assert result.exit_code == 0, result.output
    tail = " ".join(result.output.split())[-6000:]
    assert "@minus/cheap" in tail and "@niche/mebel" in tail
    assert result.output.rstrip().splitlines()[-1].strip().endswith("descriptions.")


def test_a_step_without_items_has_no_list_names_in_its_help(home: Path) -> None:
    result = semkit("read", "IN", "remove-chars", "--help")

    assert result.exit_code == 0, result.output
    assert "@minus/cheap" not in result.output


def test_describe_and_ai_list_the_lists_with_descriptions(project: Path, home: Path) -> None:
    write_list(services.project_lists_dir(project), "niche/mebel", MEBEL)

    document = json.loads(semkit("describe", "--json").stdout)
    metadata = {item["name"]: item["value"] for item in document["command"]["metadata"]}
    described = {entry["name"]: entry for entry in metadata["x-rb-lists"]}
    assert described["niche/mebel"]["description"] == "Мебель: минус-слова"
    assert described["minus/cheap"]["source"] == "bundled"

    ai = semkit("--ai").stdout
    assert "- `niche/mebel` (project, 2 lines): Мебель: минус-слова" in ai
    assert "- `minus/cheap` (bundled, 28 lines): " in ai
