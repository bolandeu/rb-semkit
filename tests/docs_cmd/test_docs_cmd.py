"""`semkit docs`: the help of every command and step as one document for people, read as InSpectra reads it."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from rb_semkit import steps
from rb_semkit.cli import app
from rb_semkit.core import docs

STEPS = sorted(step.name for area in steps.areas().values() for step in area)
READ_PARAMETERS = {"arguments": ["IN"], "options": ["--text", "--column", "--whole"]}


def _docs(*args: str):
    result = CliRunner().invoke(app, ["docs", *args], prog_name="semkit")
    assert result.exit_code == 0, result.output
    return result


@pytest.fixture(scope="module")
def document(tmp_path_factory: pytest.TempPathFactory) -> dict:
    out = tmp_path_factory.mktemp("docs") / "d.json"
    _docs("--out", str(out))
    return json.loads(out.read_text(encoding="utf-8"))


def _command(document: dict, *path: str) -> dict:
    found = document
    for name in path:
        found = next(command for command in found["commands"] if command["name"] == name)
    return found


def _options(command: dict) -> dict:
    return {option["name"]: option for option in command["options"]}


def test_commands_options_arguments_and_examples_are_at_the_root_and_the_steps_under_read(document: dict) -> None:
    assert {"commands", "options", "arguments", "examples"} <= set(document)
    assert "command" not in document
    assert "--project" in _options(document)
    read = _command(document, "read")
    assert sorted(command["name"] for command in read["commands"]) == sorted([*STEPS, "write"])


def test_the_description_of_a_step_has_no_option_line_and_no_example_line(document: dict) -> None:
    lines = _command(document, "read", "synonym-candidates")["description"].splitlines()

    assert (
        lines[0]
        == "Synonym candidates for the units of the core, from a thesaurus (RuWordNet) and word vectors (navec)."
    )
    assert [
        line for line in lines if line.startswith(("top: ", "all: ", "as_synonyms: ", "as_slots: ", "source: "))
    ] == []
    assert [line for line in lines if line.startswith(("Example: ", "-> "))] == []


def test_the_examples_of_a_step_are_in_its_examples_field(document: dict) -> None:
    examples = _command(document, "read", "synonym-candidates")["examples"]

    assert examples == [
        'semkit read --text "растаможка" --text "таможенное оформление" synonym-candidates --source ruwordnet write -'
        "  # -> растаможка, таможенное оформление, ruwordnet, 1.0, true;"
        " таможенное оформление, растаможка, ruwordnet, 1.0, true"
    ]


def test_an_option_ends_with_its_default_and_allowed_values(document: dict) -> None:
    options = _options(_command(document, "read", "synonym-candidates"))

    assert options["--top"]["description"].splitlines()[-1] == "Default: 10."
    assert options["--source"]["description"].splitlines()[-1] == "Default: both. Allowed: ruwordnet, navec, both."
    assert options["--all"]["description"].splitlines()[-1] == "Default: off."
    assert options["--top"]["arguments"][0]["arity"] == {"minimum": 1, "maximum": 1}


@pytest.mark.parametrize("name", STEPS)
def test_a_step_carries_the_input_of_read(document: dict, name: str) -> None:
    step = _command(document, "read", name)
    read = _command(document, "read")

    assert [argument["name"] for argument in step.get("arguments", [])][:1] == READ_PARAMETERS["arguments"]
    assert [option["name"] for option in step["options"]][:3] == READ_PARAMETERS["options"]
    assert step["options"][0]["description"] == _options(read)["--text"]["description"]


def test_write_is_no_step_and_takes_no_input_of_read(document: dict) -> None:
    write = _command(document, "read", "write")

    assert [argument["name"] for argument in write["arguments"]] == ["OUT"]
    assert "--text" not in _options(write)


def test_two_runs_give_the_same_bytes(tmp_path: Path) -> None:
    first, second = tmp_path / "1.json", tmp_path / "2.json"
    _docs("--out", str(first))
    _docs("--out", str(second))

    assert first.read_bytes() == second.read_bytes()


def test_without_out_the_document_goes_to_stdout(document: dict) -> None:
    assert json.loads(_docs().stdout) == document


def test_core_docs_names_no_module_step_or_command_of_semkit(document: dict) -> None:
    source = Path(docs.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {command["name"] for command in document["commands"]} | set(STEPS) | {"write"}
    imported = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.level]
    texts = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)}

    assert "semkit" not in source
    assert [module for module in imported if module and module.split(".")[0] in {"steps", "commands", "pipeline"}] == []
    assert texts & names == set()
