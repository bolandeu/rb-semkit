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


def _split(command: str) -> tuple[dict[str, str], list[str]]:
    """The variables a command line sets in front of the program, and the program with its arguments."""
    words = shlex.split(command)
    count = next(index for index, word in enumerate(words) if "=" not in word)
    return dict(word.split("=", 1) for word in words[:count]), words[count:]


def test_the_guide_shows_the_typical_pipelines() -> None:
    steps = {word for command, _ in EXAMPLES for word in shlex.split(command)}

    assert {"drop-words", "split-text", "compare-grams", "coverage", "cluster-serp", "compare-lists"} <= steps


def test_the_clean_a_core_pipeline_uses_the_bundled_phrase_list_and_a_folder_of_the_users_lists() -> None:
    commands = [_split(command) for command, _ in EXAMPLES]

    assert any(words[1:5] == ["read", "core.csv", "drop-phrases", "@minus/universal"] for _, words in commands)
    assert any(env == {"SEMKIT_LISTS": "lists"} and "@niche/minus" in words for env, words in commands)


@pytest.mark.parametrize(("command", "shown"), EXAMPLES, ids=[_split(c)[1][3] for c, _ in EXAMPLES])
def test_a_pipeline_of_the_guide_gives_the_output_it_shows(
    command: str, shown: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(FIXTURES)
    variables, (program, *arguments) = _split(command)
    for name, value in variables.items():
        monkeypatch.setenv(name, value)
    assert program == "semkit"

    result = semkit(*arguments)

    assert result.exit_code == 0, result.output
    assert [json.loads(line) for line in result.stdout.splitlines()] == [
        json.loads(line) for line in shown.splitlines()
    ]
