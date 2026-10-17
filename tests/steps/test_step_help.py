"""The help of every step speaks in the terms of the CLI: no Python names, no porting notes, an own text per option."""

from __future__ import annotations

import re

import pytest

from rb_semkit import steps
from rb_semkit.pipeline.commands import MISSING_HELP, step_options

STEPS = {step.name: step for area in steps.areas().values() for step in area}
# Python names and porting notes; «true», «false» in lower case are the values a user reads in a column.
FORBIDDEN = re.compile(r"\b(?:Series|DataFrame|InvalidArguments|norm_phrase|ADR|True|False|None)\b|\bsk\.|\badd-in\b")


def _forbidden(text: str) -> list[str]:
    return FORBIDDEN.findall(text)


def _shown_help(step: steps.Step) -> str:
    """The help of a step without the explanations of arguments the step has no option for."""
    options = {option.name for option in step_options(step.function)}
    lines = []
    for line in step.help().splitlines():
        start = steps.ARGUMENT_LINE.match(line)
        if start and not set(steps.argument_names(start)) <= options:
            continue
        lines.append(line)
    return "\n".join(lines)


@pytest.mark.parametrize("name", sorted(STEPS))
def test_the_help_of_a_step_has_no_python_terms(name: str) -> None:
    assert _forbidden(_shown_help(STEPS[name])) == []


@pytest.mark.parametrize("name", sorted(STEPS))
def test_every_option_of_a_step_has_its_own_text_without_python_terms(name: str) -> None:
    options = step_options(STEPS[name].function)

    assert [option.name for option in options if option.help.startswith(MISSING_HELP)] == []
    assert {option.name: found for option in options if (found := _forbidden(option.help))} == {}
