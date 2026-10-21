"""Every step meets the help standard, as `semkit docs` shows it.

A summary of one line, one to three examples, every option explained, no option line left in the description, and the
last line of an option giving its default and allowed values as the signature has them (read from `describe`).
"""

from __future__ import annotations

import inspect
import json

import pytest
from typer.testing import CliRunner

from rb_semkit import steps
from rb_semkit.cli import app
from rb_semkit.core.docs import ARGUMENT_LINE, argument_names

STEPS = {step.name: step for area in steps.areas().values() for step in area}


def _invoke(*args: str) -> dict:
    result = CliRunner().invoke(app, list(args), prog_name="semkit")
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


def _read_commands(commands: list[dict]) -> dict:
    """The subcommands of read, by name."""
    read = next(command for command in commands if command["name"] == "read")
    return {command["name"]: command for command in read["commands"]}


DOCS = _read_commands(_invoke("docs")["commands"])
DESCRIBE = _read_commands(_invoke("describe", "--json")["command"]["commands"])


def _values_line(option: dict) -> str:
    """The defaults line the standard asks for, from the option in `describe`: its default and accepted values."""
    meta = {item["name"]: item["value"] for item in option["metadata"]}
    parts = []
    if "arguments" not in option:  # a flag
        parts.append(f"Default: {'on' if meta['x-rb-default'] else 'off'}.")
    elif meta.get("x-rb-default") not in (None, "", []):
        default = meta["x-rb-default"]
        parts.append(f"Default: {', '.join(map(str, default)) if isinstance(default, list) else default}.")
    if accepted := option.get("arguments", [{}])[0].get("acceptedValues"):
        parts.append(f"Allowed: {', '.join(accepted)}.")
    return " ".join(parts)


def _problems(name: str) -> list[str]:
    page, options = DOCS[name], DESCRIBE[name].get("options", [])
    found = []
    summary = page["description"].split("\n\n")[1]  # the first paragraph is the Input line
    if not summary or (inspect.getdoc(STEPS[name].function) or "").splitlines()[0] != summary:
        found.append("the summary is not the first line of the docstring")
    if not 1 <= len(page.get("examples", [])) <= 3:
        found.append("not one to three examples")
    shown = {option["name"]: option for option in page.get("options", [])}
    for option in options:
        lines = shown[option["name"]]["description"].splitlines()
        values = _values_line(option)
        if values and lines[-1] != values:
            found.append(f"{option['name']}: the last line is not {values!r}")
        if not "\n".join(lines[:-1] if values else lines).strip():
            found.append(f"{option['name']}: not explained")
    names = {option["name"].lstrip("-").replace("-", "_") for option in options}
    for line in page["description"].splitlines():
        if (start := ARGUMENT_LINE.match(line)) and set(argument_names(start)) & names:
            found.append(f"an option line in the description: {line[:40]!r}")
    return found


@pytest.mark.parametrize("name", sorted(STEPS))
def test_a_step_meets_the_help_standard(name: str) -> None:
    assert _problems(name) == []
