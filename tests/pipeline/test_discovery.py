"""What an agent learns about the pipeline: describe --json, the help of each step, --ai."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .runner import semkit

SNAPSHOTS = Path(__file__).resolve().parents[1] / "snapshots" / "help"
# The steps of this task by area, written out: the matchers by the verbs each one supports.
MATCHER_VERBS = {
    "words": ("find", "remove", "extract"),
    "chars": ("find", "remove", "extract"),
    "cells": ("find", "remove", "extract"),
    "stopwords": ("remove",),
    "spaces": ("remove",),
    "regex": ("find", "remove", "extract"),
    "around": ("remove", "extract"),
    "edges": ("remove",),
    "word-case": ("find", "extract"),
    "word-content": ("find", "remove", "extract"),
    "word-position": ("find", "remove", "extract"),
    "positions": ("remove", "extract"),
    "pos": ("find", "remove", "extract"),
    "repeats": ("find", "remove"),
    "phrases": ("find", "remove", "extract"),
}
TEXT_STEPS = sorted(
    [f"{verb}-{matcher}" for matcher, verbs in MATCHER_VERBS.items() for verb in verbs]
    + [f"{verb}-{matcher}" for matcher, verbs in MATCHER_VERBS.items() if "find" in verbs for verb in ("keep", "drop")]
)
AREAS = {"text": TEXT_STEPS, "dupes": ["dupes"], "analysis": ["bigrams", "ngrams"]}


def _read_command() -> dict:
    result = semkit("describe", "--json")
    commands = json.loads(result.stdout)["command"]["commands"]
    return next(command for command in commands if command["name"] == "read")


def _options(command: dict) -> list[str]:
    return [option["name"] for option in command.get("options", [])]


def test_describe_lists_read_write_and_every_step_with_its_options() -> None:
    read = _read_command()
    steps = {command["name"]: command for command in read["commands"]}

    assert {"--column", "--whole", "--trace"} <= set(_options(read))
    assert "--overwrite" in _options(steps["write"])
    assert sorted(steps) == sorted(["write", *[name for names in AREAS.values() for name in names]])
    assert {"--items", "--mode", "--where", "--as"} <= set(_options(steps["remove-words"]))
    assert {"--kind", "--action", "--as"} <= set(_options(steps["dupes"]))
    assert "-n" in _options(steps["ngrams"])
    assert "--as" not in _options(steps["keep-words"])


def test_choices_are_listed_in_describe() -> None:
    steps = {command["name"]: command for command in _read_command()["commands"]}
    mode = next(option for option in steps["remove-words"]["options"] if option["name"] == "--mode")

    assert mode["arguments"][0]["acceptedValues"] == ["any", "all"]


@pytest.mark.parametrize("area", sorted(AREAS))
def test_every_step_has_a_help_snapshot_under_its_area(area: str) -> None:
    stored = sorted(path.stem for path in (SNAPSHOTS / "steps" / area).glob("*.txt"))

    assert stored == sorted(AREAS[area])


def test_step_help_is_the_docstring_of_the_function() -> None:
    result = semkit("read", "IN", "remove-chars", "--help")

    assert result.exit_code == 0, result.output
    assert "The characters of one type." in result.output
    assert "Example: semkit read" in result.output


def test_ai_prints_the_skill_and_the_steps() -> None:
    result = semkit("--ai")

    assert result.exit_code == 0, result.output
    assert result.stdout.startswith("---\nname: semkit")
    assert "remove-words" in result.stdout and "ngrams" in result.stdout
