"""`semkit docs`: the help of every command as one OpenCLI document for people, as InSpectra reads it.

The real CLI is read through the runner; the cases of the help standard (examples, defaults, inherited options)
run on a throwaway Typer app.
"""

from __future__ import annotations

import enum
import json
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from rb_semkit.cli import app
from rb_semkit.commands import docs as docs_command
from rb_semkit.core import docs

CLI = "semkit"
COMMANDS = ["init", "status", "doctor", "run", "describe", "docs", "auth", "skill", "config"]
runner = CliRunner()


def _run(*args: str):
    return runner.invoke(app, ["docs", *args], prog_name=CLI)


def _document() -> dict:
    result = _run()
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


class Mode(enum.Enum):
    A = "a"
    B = "b"


class Color(enum.Enum):
    RED = "red"
    BLUE = "blue"


def _probe() -> typer.Typer:
    probe = typer.Typer(add_completion=False)

    @probe.command()
    def paint(
        color: Color = typer.Option(Color.RED, "--color", help="Which color."),
        coats: int = typer.Option(10, "--coats", help="How many coats."),
        mode: Mode = typer.Option(Mode.A, "--mode", help="Which mode."),
        finish: Mode = typer.Option(Mode.B, "--finish", help="Which finish."),
        tag: list[str] = typer.Option([], "--tag", help="A tag, repeatable."),
        dry: bool = typer.Option(False, "--dry", help="Paint nothing."),
    ) -> None:
        """Paint the wall. Each coat dries first.

        A coat dries before the next one.
        coats: how many coats the wall gets.
        mode: how the paint goes on:
        - a: by brush
        - b: by roller

        Example: semkit paint --coats 3
        -> a wall with 3 coats
        """

    group = typer.Typer()

    @group.callback()
    def tools(level: int = typer.Option(1, "--level", help="The level."), where: str = typer.Argument("x")) -> None:
        """Tools."""

    @group.command()
    def brush(size: int = typer.Option(3, "--size", help="The size.")) -> None:
        """Use a brush."""

    probe.add_typer(group, name="tools")
    return probe


def _probe_document(hook: docs.Hook | None = None) -> dict:
    return docs.document(typer.main.get_command(_probe()), hook)


def _by_name(entries: list[dict]) -> dict:
    return {entry["name"]: entry for entry in entries}


def test_the_document_has_its_parts_at_the_root_and_every_template_command() -> None:
    document = _document()

    assert {"opencli", "info", "commands", "options", "arguments", "examples"} <= set(document)
    assert "command" not in document
    assert set(COMMANDS) <= set(_by_name(document["commands"]))


def test_the_example_of_describe_is_in_examples_not_in_the_description() -> None:
    describe = _by_name(_document()["commands"])["describe"]

    assert describe["examples"] == ["--json"]
    assert not [line for line in describe["description"].splitlines() if line.startswith("Example")]


def test_the_description_is_the_summary_then_the_paragraphs_without_option_and_example_lines() -> None:
    paint = _by_name(_probe_document()["commands"])["paint"]

    assert paint["description"] == "Paint the wall.\n\nEach coat dries first.\n\nA coat dries before the next one."


def test_an_example_is_one_string_with_its_result() -> None:
    paint = _by_name(_probe_document()["commands"])["paint"]

    assert paint["examples"] == ["--coats 3  # -> a wall with 3 coats"]


def _outside_path_probe() -> typer.Typer:
    """A CLI with `docs` whose `paint` has an example that does not start with `<program> paint`."""
    probe = typer.Typer(add_completion=False)

    @probe.callback()
    def main(ctx: typer.Context, json_output: bool = typer.Option(False, "--json")) -> None:
        ctx.ensure_object(dict)
        ctx.obj["json"] = json_output

    @probe.command()
    def paint() -> None:
        """Paint.

        Example: semkit wall --name Ann
        """

    probe.command(name="docs")(docs_command.docs)
    return probe


def test_the_hook_may_bring_an_example_to_the_form_that_starts_with_its_command_path() -> None:
    class Short(docs.Hook):
        def example(self, path, command: str) -> str:
            return command.replace("semkit wall", "semkit paint") if path == ("paint",) else command

    paint = _by_name(docs.document(typer.main.get_command(_outside_path_probe()), Short())["commands"])["paint"]

    assert paint["examples"] == ["--name Ann"]


def test_the_hook_puts_a_line_before_the_description_of_a_command() -> None:
    class Lead(docs.Hook):
        def lead(self, path) -> str:
            return "Lead line." if path == ("paint",) else ""

    paint = _by_name(_probe_document(Lead())["commands"])["paint"]

    assert paint["description"].split("\n\n")[:2] == ["Lead line.", "Paint the wall."]


def test_an_example_outside_the_command_path_fails_and_writes_nothing(tmp_path: Path) -> None:
    out = tmp_path / "docs.json"

    result = runner.invoke(_outside_path_probe(), ["--json", "docs", "--out", str(out)], prog_name=CLI)

    assert result.exit_code == 1
    error = json.loads(result.stdout)["error"]
    assert f"'{CLI} paint'" in error["message"]
    assert f"{CLI} wall --name Ann" in error["message"]
    assert not out.exists()


def test_an_example_outside_the_command_path_without_json_and_out_fails_with_an_empty_stdout() -> None:
    result = runner.invoke(_outside_path_probe(), ["docs"], prog_name=CLI)

    assert result.exit_code == 1
    assert result.stdout == ""


def test_an_option_ends_with_its_default_and_allowed_values() -> None:
    options = _by_name(_by_name(_probe_document()["commands"])["paint"]["options"])

    assert options["--coats"]["description"].endswith("Default: 10.")
    assert options["--mode"]["description"].splitlines()[-1] == "Default: a. Allowed: a, b."


def test_an_option_with_default_b_and_choices_a_b_ends_with_the_line_of_both() -> None:
    finish = _by_name(_by_name(_probe_document()["commands"])["paint"]["options"])["--finish"]

    assert finish["description"] == "Which finish.\nDefault: b. Allowed: a, b."


def test_a_flag_ends_with_default_off_and_has_no_arity_and_a_multiple_option_has_no_maximum() -> None:
    options = _by_name(_by_name(_probe_document()["commands"])["paint"]["options"])

    assert options["--dry"]["description"].splitlines()[-1] == "Default: off."
    assert "arguments" not in options["--dry"]
    assert options["--coats"]["arguments"][0]["arity"] == {"minimum": 1, "maximum": 1}
    assert options["--tag"]["arguments"][0]["arity"] == {"minimum": 1}


class LevelAndWhere(docs.Hook):
    """A hook that names an option and a positional argument of the group."""

    def inherited(self, group) -> list:
        return [param for param in group.params if param.name in {"level", "where"}]


def test_a_hook_cannot_inherit_an_argument() -> None:
    with pytest.raises(ValueError, match="options only"):
        _probe_document(LevelAndWhere())


def test_the_inherited_option_is_once_on_the_group_and_the_argument_is_not_inherited() -> None:
    class Level(docs.Hook):
        def inherited(self, group) -> list:
            return [param for param in group.params if param.name == "level"]

    tools = _by_name(_probe_document(Level())["commands"])["tools"]
    [brush] = tools["commands"]

    assert _by_name(tools["options"])["--level"]["recursive"] is True
    assert [option["name"] for option in brush["options"]] == ["--size"]
    assert [argument["name"] for argument in tools["arguments"]] == ["where"]
    assert "arguments" not in brush


def test_two_runs_give_the_same_bytes() -> None:
    assert _run().stdout == _run().stdout


def test_out_holds_the_same_bytes_and_stdout_is_empty(tmp_path: Path) -> None:
    out = tmp_path / "docs.json"
    result = _run("--out", str(out))

    assert result.exit_code == 0, result.output
    assert result.stdout == ""
    assert out.read_text(encoding="utf-8") == _run().stdout


def test_out_in_a_missing_directory_is_an_error_envelope_and_no_file(tmp_path: Path) -> None:
    out = tmp_path / "missing" / "docs.json"
    result = runner.invoke(app, ["--json", "docs", "--out", str(out)], prog_name=CLI)

    assert result.exit_code != 0
    assert json.loads(result.stdout)["ok"] is False
    assert not out.exists()
