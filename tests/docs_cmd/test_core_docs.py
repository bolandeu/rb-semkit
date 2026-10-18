"""core.docs on a small Typer app with no code of this CLI: the help standard (docs/help-standard.md) applied."""

from __future__ import annotations

import enum

import pytest
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

        Example: semkit paint wall --name Ann
        -> wall: red, 2 coats

        Example: semkit paint door --name Ann --color blue
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


def _document(hook: docs.Hook | None = None) -> dict:
    return docs.document(typer.main.get_command(_app()), hook)


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
        "wall --name Ann  # -> wall: red, 2 coats",
        "door --name Ann --color blue",
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


class OptionOfGroup(docs.Hook):
    """A hook that gives the subcommands of a group the option --level of that group."""

    def inherited(self, group) -> list:
        return [param for param in group.params if param.name == "level"]


def test_an_option_the_hook_inherits_is_recursive_on_the_parent_and_not_copied_into_the_subcommands() -> None:
    tools = _commands(_document(OptionOfGroup()))["tools"]
    [brush] = tools["commands"]

    assert _options(tools)["--level"]["recursive"] is True
    assert [option["name"] for option in brush["options"]] == ["--size"]
    assert "recursive" not in _options(brush)["--size"]


def test_a_hook_cannot_inherit_an_argument() -> None:
    class ArgumentOfGroup(docs.Hook):
        def inherited(self, group) -> list:
            return [typer.main.get_command(_app()).commands["paint"].params[0]]

    with pytest.raises(ValueError, match="options only"):
        _document(ArgumentOfGroup())


def test_the_hook_may_bring_an_example_to_the_form_that_starts_with_its_command_path() -> None:
    class Short(docs.Hook):
        def example(self, path, command: str) -> str:
            return command.replace("semkit paint wall", "semkit paint") if path == ("paint",) else command

    paint = _commands(_document(Short()))["paint"]

    assert paint["examples"][0] == "--name Ann  # -> wall: red, 2 coats"


def test_an_example_that_does_not_start_with_its_command_path_fails_with_the_command_and_the_example() -> None:
    probe = typer.Typer(add_completion=False)

    @probe.command()
    def paint() -> None:
        """Paint.

        Example: semkit wall --name Ann
        """

    @probe.command()
    def other() -> None:
        """Other."""

    with pytest.raises(docs.ExampleOutsidePath) as caught:
        docs.document(typer.main.get_command(probe))

    assert caught.value.exit_code == 1
    assert "'semkit paint'" in caught.value.message
    assert "semkit wall --name Ann" in caught.value.message


def test_the_hook_puts_a_line_before_the_description_of_a_command() -> None:
    class Lead(docs.Hook):
        def lead(self, path) -> str:
            return "Lead line." if path == ("paint",) else ""

    paint = _commands(_document(Lead()))["paint"]

    assert paint["description"].split("\n\n")[:2] == ["Lead line.", "Paint the targets in one color."]
