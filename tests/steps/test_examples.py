"""Every Example of every step runs on the small files of tests/steps/fixtures and gives the result its «->» line says.

The result of a command that ends with `write -` is its rows: the cells of a row joined by «, » (a flag as true or
false, an empty cell as nothing), the rows joined by «; ». So `-> kupit divan` is one row, `-> диван; купить диван` two.
"""

from __future__ import annotations

import json
import shlex
from pathlib import Path

import pytest

from rb_semkit import steps

from ..pipeline.runner import semkit

FIXTURES = Path(__file__).parent / "fixtures"
STEPS = sorted(step.name for area in steps.areas().values() for step in area)
SEPARATOR = "  # -> "
PROGRAM = "semkit"


def _read_examples() -> dict[str, list[str]]:
    """The examples of each step in `semkit docs`, as the document has them: «<command>  # -> <result>»."""
    read = next(command for command in json.loads(semkit("docs").stdout)["commands"] if command["name"] == "read")
    return {command["name"]: command.get("examples", []) for command in read["commands"]}


EXAMPLES = _read_examples()
CASES = [(name, example) for name in STEPS for example in EXAMPLES[name]]


def _cell(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return "" if value is None else str(value)


def _rows(output: str) -> str:
    rows = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
    return "; ".join(", ".join(_cell(value) for value in row.values()) for row in rows)


def test_every_step_has_examples() -> None:
    assert [name for name in STEPS if not EXAMPLES[name]] == []


@pytest.mark.parametrize(("name", "example"), CASES, ids=[f"{name}-{index}" for index, (name, _) in enumerate(CASES)])
def test_an_example_runs_and_gives_its_result(name: str, example: str, monkeypatch: pytest.MonkeyPatch) -> None:
    command, separator, result = example.partition(SEPARATOR)
    program, *arguments = shlex.split(command)
    assert separator and program == PROGRAM and arguments[-2:] == ["write", "-"], f"{name}: {example}"
    monkeypatch.chdir(FIXTURES)

    run = semkit(*arguments)

    assert run.exit_code == 0, f"{command}: {run.output}"
    assert _rows(run.stdout).rstrip() == result, command
