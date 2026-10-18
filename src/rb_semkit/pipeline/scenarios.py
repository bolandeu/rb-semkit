"""A scenario (`core.scenarios`) as one read pipeline: each step line is one step of the read group.

`loaded` loads the scenarios and checks every step line in the read group: a step that does not exist, or an option
the step does not take, is refused naming the file and the line. `io` gives the input and the output of `run NAME`.
`run` fills the placeholders with the parameters and puts --set STEP.OPTION=VALUE into the options of the steps, then
runs the chain once over the whole table or, with per_phrase, once for each phrase (`run_each`).
"""

from __future__ import annotations

from collections.abc import Collection, Iterable, Mapping
from pathlib import Path
from typing import cast

import typer
from typer._click.core import Command, Context, Parameter
from typer._click.exceptions import UsageError
from typer.core import TyperGroup, TyperOption

from .. import steps
from ..core import scenarios
from ..core.errors import InvalidArguments
from ..core.scenarios import Scenario, Settings
from ..core.version import cli_name
from .commands import POSITIONAL_PREFIX
from .group import planned, reported
from .run import run as run_pipeline
from .run import run_each
from .state import Planned
from .tables import Source, Target

WRITE = "write"
SHAPE = "a scenario runs as 'run NAME [IN | --text TEXT…] [--set NAME=VALUE…] [write OUT]'"


def loaded(group: TyperGroup, start: Path) -> dict[str, Scenario]:
    """The scenarios of the project at or above `start` (with the bundled ones), each step line checked."""
    return {name: _checked(group, scenarios.load(path)) for name, path in scenarios.find(start).items()}


def _step_names() -> set[str]:
    return {step.name for found in steps.areas().values() for step in found}


def _checked(group: TyperGroup, scenario: Scenario) -> Scenario:
    """The scenario, when every step line names a step and gives it options it takes (the defaults filled)."""
    values = scenario.values({}, f"{{{scenarios.TEXT}}}")  # the phrase stays a placeholder
    names = _step_names()
    for line in scenario.steps:
        name, *args = line.words(values)
        if name not in names:
            raise scenario.refused(line, f"no step {name}; '{cli_name()} read --help' lists the steps.")
        try:
            group.commands[name].make_context(name, args, parent=Context(group, info_name="read"))
        except UsageError as error:
            raise scenario.refused(line, error.format_message()) from None
    return scenario


def _option_name(param: Parameter) -> str:
    """The name of an option in --set STEP.OPTION: its flag without the dashes (`against-column`, `as`)."""
    return param.opts[0].lstrip("-")


def _options(command: Command) -> list[Parameter]:
    return [param for param in command.params if isinstance(param, TyperOption)]


def _check_options(group: TyperGroup, scenario: Scenario, options: Mapping[str, Mapping[str, str]]) -> None:
    """Refuse --set STEP.OPTION of a step the scenario does not have, or of an option the step does not take."""
    taken = {
        line.step(): [_option_name(param) for param in _options(group.commands[line.step()])] for line in scenario.steps
    }
    for step, given in options.items():
        for option, value in given.items():
            if option in taken.get(step, ()):
                continue
            reason = f"{step} takes no option {option}" if step in taken else f"the scenario has no step {step}"
            listed = "; ".join(f"{name} ({', '.join(found) or 'no options'})" for name, found in taken.items())
            raise InvalidArguments(
                f"run {scenario.name}: --set {step}.{option}={value}: {reason}.",
                action=f"Set an option of a step of the scenario: {listed}.",
            )


def _set(step: Context, options: Mapping[str, str]) -> None:
    """Put the options --set gives into the parsed step: each replaces the value of the step, or adds the option."""
    for param in _options(step.command):
        if (value := options.get(_option_name(param))) is None:
            continue
        name = str(param.name)
        step.params[name] = param.type_cast_value(step, (value,) if param.multiple else value)
        if POSITIONAL_PREFIX + name in step.params:  # the same option given positionally gives way
            step.params[POSITIONAL_PREFIX + name] = None


def _planned(
    ctx: typer.Context, group: TyperGroup, scenario: Scenario, settings: Settings, text: str | None
) -> list[Planned]:
    """The steps of the scenario planned with the values of its parameters and the phrase `text`."""
    read = Context(group, info_name="read", parent=ctx)
    values = scenario.values(settings.values, text)
    contexts = []
    with reported(read):
        for line in scenario.steps:
            name, *args = line.words(values)
            contexts.append(group.commands[name].make_context(name, args, parent=read))
            _set(contexts[-1], settings.options.get(name, {}))
        return cast("list[Planned]", planned(contexts))


def io(
    scenario: Scenario, words: Collection[str], texts: Iterable[str], overwrite: bool
) -> tuple[Source, Target | None]:
    """The input and the output of `run NAME [IN] [write OUT]`."""
    words = list(words)
    before, after = (words[: words.index(WRITE)], words[words.index(WRITE) + 1 :]) if WRITE in words else (words, None)
    if len(before) > 1 or (after is not None and len(after) != 1):
        raise InvalidArguments(
            f"run {scenario.name}: {' '.join(words)}: {SHAPE}.",
            action="Give one IN (or --text), then 'write OUT' once, at the end.",
        )
    source = Source(before[0] if before else None, texts=tuple(texts))
    return source, None if after is None else Target(after[0], overwrite)


def run(
    ctx: typer.Context,
    group: TyperGroup,
    scenario: Scenario,
    given: Iterable[str],
    source: Source,
    target: Target | None,
) -> None:
    """Run `scenario` with the --set values `given` over `source` into `target`, as one read pipeline."""
    settings = scenarios.settings(scenario, given)
    _check_options(group, scenario, settings.options)
    if scenario.per_phrase:
        run_each(ctx, source, lambda text: _planned(ctx, group, scenario, settings, text), target)
        return
    run_pipeline(ctx, source, [*_planned(ctx, group, scenario, settings, None), *([target] if target else [])])
