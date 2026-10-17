"""The typical pipelines of SKILL.md: each command line runs on its fixtures and writes the rows the guide shows."""

from __future__ import annotations

import json
import re
import shlex
from importlib import resources
from pathlib import Path

import pytest

from ..pipeline.runner import semkit

FIXTURES = Path(__file__).parent / "fixtures"
GUIDE = resources.files("rb_semkit.data").joinpath("SKILL.md").read_text(encoding="utf-8")
EXAMPLE = re.compile(r"```console\n\$ (?P<command>[^\n]+)\n(?P<output>.*?)```", re.DOTALL)
EXAMPLES = [(match["command"], match["output"]) for match in EXAMPLE.finditer(GUIDE)]


def test_the_guide_shows_the_typical_pipelines() -> None:
    steps = {word for command, _ in EXAMPLES for word in shlex.split(command)}

    assert {"drop-words", "split-text", "compare-grams", "coverage", "cluster-serp", "compare-lists"} <= steps


@pytest.mark.parametrize(("command", "shown"), EXAMPLES, ids=[shlex.split(c)[3] for c, _ in EXAMPLES])
def test_a_pipeline_of_the_guide_gives_the_output_it_shows(
    command: str, shown: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(FIXTURES)
    program, *arguments = shlex.split(command)
    assert program == "semkit"

    result = semkit(*arguments)

    assert result.exit_code == 0, result.output
    assert [json.loads(line) for line in result.stdout.splitlines()] == [
        json.loads(line) for line in shown.splitlines()
    ]
