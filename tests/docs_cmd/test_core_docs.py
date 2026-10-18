"""core.docs on a small Typer app with no code of this CLI: the help standard (docs/help-standard.md) applied."""

from __future__ import annotations

import enum

import typer

from rb_semkit.core import docs


class Color(enum.Enum):
    RED = "red"
    BLUE = "blue"


def _app() -> typer.Typer:
    probe = typer.Typer(add_completion=False)

    @probe.callback()
    def main(verbose: bool = typer.Option(False, "--verbose", help="More output.")) -> None:
        """Probe 1.0 — a probe."""

    @probe.command()
    def paint(
        targets: list[str] = typer.Argument(..., help="What to paint."),
        color: Color = typer.Option(Color.RED, "--color", help="Which color."),
        coats: int = typer.Option(2, "--coats", help="How many coats."),
        tag: list[str] = typer.Option([], "--tag", help="A tag, repeatable."),
        name: str = typer.Option(..., "--name", help="Who paints."),
        dry: bool = typer.Option(False, "--dry", help="Paint nothing."),
    ) -> None:
        """Paint the targets in one color. Each target gets every coat.

        A coat dries before the next one.
        coats: how many coats each target gets.
        tag: a tag of the job.

        Example: probe paint wall --name Ann
        -> wall: red, 2 coats

        Example: probe paint door --name Ann --color blue
        """

    group = typer.Typer()

    @group.callback()
    def tools(level: int = typer.Option(1, "--level", help="The level.")) -> None:
        """Tools."""

    @group.command()
    def brush(size: int = typer.Option(3, "--size", help="The size.")) -> None:
        """Use a brush."""

    probe.add_typer(group, name="tools")
    return probe


def _document(inherited: docs.Inherited | None = None) -> dict:
    return docs.document(typer.main.get_command(_app()), inherited)


def _commands(document: dict) -> dict:
    return {command["name"]: command for command in document["commands"]}


def _options(command: dict) -> dict:
    return {option["name"]: option for option in command["options"]}


def test_the_commands_options_arguments_and_examples_are_at_the_root() -> None:
    document = _document()

    assert set(document) == {"opencli", "info", "commands", "options", "arguments", "examples"}
    assert [command["name"] for command in document["commands"]] == ["paint", "tools"]
    assert [option["name"] for option in document["options"]] == ["--verbose"]
    assert document["arguments"] == [] and document["examples"] == []
    assert [command["name"] for command in _commands(document)["tools"]["commands"]] == ["brush"]


def test_the_description_is_the_summary_then_the_paragraphs_without_option_and_example_lines() -> None:
    paint = _commands(_document())["paint"]

    assert (
        paint["description"]
        == "Paint the targets in one color.\n\nEach target gets every coat.\n\nA coat dries before the next one."
    )


def test_an_example_is_one_string_with_its_result() -> None:
    paint = _commands(_document())["paint"]

    assert paint["examples"] == [
        "probe paint wall --name Ann  # -> wall: red, 2 coats",
        "probe paint door --name Ann --color blue",
    ]


def test_the_last_line_of_an_option_gives_its_default_and_allowed_values() -> None:
    options = _options(_commands(_document())["paint"])

    assert options["--color"]["description"] == "Which color.\nDefault: red. Allowed: red, blue."
    assert options["--coats"]["description"] == "How many coats.\nDefault: 2."
    assert options["--dry"]["description"] == "Paint nothing.\nDefault: off."
    assert options["--name"]["description"] == "Who paints."
    assert options["--tag"]["description"] == "A tag, repeatable."


def test_an_option_that_does_not_repeat_takes_at_most_one_value() -> None:
    options = _options(_commands(_document())["paint"])

    assert options["--coats"]["arguments"][0]["arity"] == {"minimum": 1, "maximum": 1}
    assert options["--tag"]["arguments"][0]["arity"] == {"minimum": 1}
    assert options["--color"]["arguments"][0]["acceptedValues"] == ["red", "blue"]


def test_the_hook_gives_a_subcommand_the_parameters_of_its_group() -> None:
    def inherited(group, name: str) -> list:
        return [param for param in group.params if param.name == "level"] if name == "brush" else []

    [brush] = _commands(_document(inherited))["tools"]["commands"]

    assert [option["name"] for option in brush["options"]] == ["--level", "--size"]
