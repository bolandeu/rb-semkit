"""Every bundled agent skill: frontmatter present, name = <cli>-<dir name> (<cli> for the conventions skill),
and no skill lists the CLI's commands (standard §9: the help is the list)."""

from __future__ import annotations

import re
from pathlib import Path

import typer.main

from rb_semkit.cli import app
from rb_semkit.core import opencli, skills
from rb_semkit.core.version import cli_name

DATA = Path(skills.__file__).resolve().parents[1] / "data"


def _command_names() -> list[str]:
    document = opencli.document(typer.main.get_command(app))
    return sorted(command["name"] for command in document["command"]["commands"])


def _problems(data: Path) -> list[str]:
    """What is wrong with the skills under a data dir, each line naming the file."""
    cli = cli_name()
    found = []
    paths = [data / "SKILL.md", *sorted(data.glob(f"{skills.EXTRAS_DIR}/*/SKILL.md"))]
    list_item = re.compile(rf"^\s*(?:[-*]|\d+\.|\|)\s*`?{re.escape(cli)} ({'|'.join(_command_names())})\b", re.M)
    for path in paths:
        text = path.read_text()
        meta = skills.frontmatter(text)
        expected = cli if path.parent == data else f"{cli}-{path.parent.name}"
        if not meta:
            found.append(f"{path}: no frontmatter")
            continue
        if meta.get("name") != expected:
            found.append(f"{path}: name is {meta.get('name')!r}, expected {expected!r}")
        if not meta.get("description"):
            found.append(f"{path}: no description")
        if list_item.search(text):
            found.append(f"{path}: lists the commands of {cli}")
    return found


def test_every_bundled_skill_follows_the_standard() -> None:
    assert _problems(DATA) == []


def test_a_wrong_name_no_frontmatter_or_a_command_list_names_the_file(tmp_path: Path) -> None:
    cli = cli_name()
    good = f"---\nname: {cli}\ndescription: d\n---\n\n# x\n"
    (tmp_path / "SKILL.md").write_text(good)
    extras = tmp_path / skills.EXTRAS_DIR
    for directory, text in {
        "fine": f"---\nname: {cli}-fine\ndescription: d\n---\n",
        "misnamed": f"---\nname: {cli}-other\ndescription: d\n---\n",
        "bare": "# no frontmatter\n",
        "listing": f"---\nname: {cli}-listing\ndescription: d\n---\n\n- `{cli} {_command_names()[0]}` does a thing\n",
    }.items():
        (extras / directory).mkdir(parents=True)
        (extras / directory / "SKILL.md").write_text(text)
    problems = _problems(tmp_path)
    assert [Path(line.split(":")[0]).parent.name for line in problems] == ["bare", "listing", "misnamed"]


def test_frontmatter_of_text_without_it_is_empty() -> None:
    assert skills.frontmatter("# title\n") == {}
    assert skills.frontmatter("---\nname: a\n") == {}
    assert skills.frontmatter("---\nname: a\ndescription: b: c\n---\nbody") == {"name": "a", "description": "b: c"}
