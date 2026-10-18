"""`run NAME`: a scenario, a named chain of semkit's own steps (bundled or in the project), run as one read pipeline.

The scenarios are the commands of the group, found each time the group is asked for them: in the project of
--project, else of the current folder, so `run --help` and `semkit docs` list them. A scenario file that does not load
is refused then, with exit 2. Each scenario is a copy of one command whose help is the scenario's own.
"""

from __future__ import annotations

import copy
import functools
from pathlib import Path
from typing import Any

import typer
from rich.markup import escape
from typer._click.globals import get_current_context
from typer.core import TyperCommand, TyperGroup

from .. import output
from ..core.errors import CliError
from ..core.scenarios import Scenario
from ..core.version import cli_name
from ..pipeline import scenarios
from . import read

HELP = f"""Run a scenario: a named chain of semkit's own steps, kept so that a frequent chain runs by its name.

The scenarios are the commands below: the bundled ones and the project's own, a file NAME.toml in .rb_semkit/scenarios/ (one of the same name overrides the bundled one). 'run NAME [IN | --text TEXT…] [--set NAME=VALUE…] [write OUT]' reads the input as read does, runs the steps of the scenario as one read pipeline and writes the result; without write it prints a table, as read does. --set NAME=VALUE fills a parameter of the scenario, --set STEP.OPTION=VALUE an option of one of its steps. 'run NAME --help' shows its parameters with their defaults and its steps.

Example: {cli_name()} run intent-synonyms --text "растаможка авто"
"""  # fmt: skip


class ScenarioCommand(TyperCommand):
    """The command of one scenario."""

    scenario: Scenario


@functools.cache
def _read_group() -> TyperGroup:
    return typer.main.get_command(read.app)  # ty: ignore[invalid-return-type]


def _scenarios(ctx: Any) -> dict[str, Scenario]:
    """The scenarios of the project of the command line (--project, else the current folder), refused when one does
    not load."""
    start = Path((ctx.find_root().obj or {}).get("project") or Path.cwd()) if ctx else Path.cwd()
    try:
        return scenarios.loaded(_read_group(), start)
    except CliError as error:
        if ctx is not None:
            output.emit_error(ctx, error)  # it exits
        raise


class ScenarioGroup(TyperGroup):
    """The group whose commands are the scenarios of the project of the command line."""

    @property
    def commands(self) -> dict[str, Any]:
        return {name: _command(found) for name, found in _scenarios(get_current_context(silent=True)).items()}

    @commands.setter
    def commands(self, value: dict[str, Any]) -> None:
        """Click sets the commands in its constructor; the group finds the scenarios instead."""

    def format_help(self, ctx: Any, formatter: Any) -> None:
        """The help, once every scenario loads: a scenario that does not load is refused before any line of it."""
        _scenarios(ctx)
        super().format_help(ctx, formatter)


@output.guard
def scenario(
    ctx: typer.Context,
    words: list[str] = typer.Argument(None, metavar="[IN] [write OUT]", help="The table to read, as read takes it ('-' for JSONL on stdin; left out with --text), then 'write OUT': the file to write, '-' for JSONL on stdout."),
    texts: list[str] = typer.Option(None, "--text", metavar="TEXT", help="A phrase from the command line, repeatable, as read takes it. IN is then left out."),
    sets: list[str] = typer.Option(None, "--set", metavar="NAME=VALUE", help="A value of a parameter of the scenario (NAME=VALUE), or of an option of one of its steps (STEP.OPTION=VALUE); repeatable."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Replace OUT when it exists."),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    dry_run: bool = typer.Option(False, "--dry-run", help="Read and run every step, print the summary, write nothing."),
) -> None:  # fmt: skip
    """Run the scenario of this command over the input.

    Example: {cli} run intent-synonyms --text "растаможка авто"
    """
    found = ctx.command.scenario  # ty: ignore[unresolved-attribute]
    source, target = scenarios.io(found, words or [], texts or [], overwrite)
    scenarios.run(ctx, _read_group(), found, sets or [], source, target)


_holder = typer.Typer(add_completion=False)
_holder.command("scenario", cls=ScenarioCommand)(scenario)
_BASE = typer.main.get_command(_holder)


def _command(found: Scenario) -> ScenarioCommand:
    command = copy.copy(_BASE)
    command.name = found.name
    command.help = escape(found.help())
    command.short_help = escape(found.description)
    command.scenario = found  # ty: ignore[unresolved-attribute]
    return command  # ty: ignore[invalid-return-type]


app = output.group(HELP, cls=ScenarioGroup)
