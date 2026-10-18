"""The pipeline as one chained group: `read IN [options] STEP… write OUT` (ADR 0008).

The Click that Typer ships has no chained groups, so this group chains its commands itself, as Click's `chain=True`:
it parses every step of the command line first, then reads the input and runs them in the order written. The command
line is cut at each word that names a step (but not at the value of an option: `--items dupes`), so the options and
the positional argument of a step come in any order. A usage error of read or of a step is reported as a CliError
naming the step (with --json, the error envelope).
"""

from __future__ import annotations

from collections.abc import Collection, Generator
from contextlib import contextmanager
from typing import Any, cast

import typer
from typer._click.core import Command, Context
from typer._click.exceptions import UsageError
from typer.core import TyperGroup

from .. import output
from ..core.errors import InvalidArguments
from ..core.version import cli_name
from .commands import help_hint
from .run import SHAPE, run


@contextmanager
def reported(ctx: Context) -> Generator[None]:
    """A usage error as the CliError INVALID_ARGUMENTS, its message led by the name of the step."""
    try:
        yield
    except UsageError as error:
        failed = error.ctx or ctx
        step = failed.info_name or ""
        own = failed.command is ctx.command
        action = f"Run '{cli_name()} read --help' for its options and the steps." if own else help_hint(step)
        message = f"{step}: {error.format_message()}"
        output.emit_error(cast(typer.Context, ctx), InvalidArguments(message, action=action))


def _end(command: Command, args: list[str], steps: Collection[str]) -> int:
    """Where the words of `command` end in `args`: at the first word that names a step and is no option's value."""
    takes_value = {name for param in command.params if not getattr(param, "is_flag", True) for name in param.opts}
    index = 0
    while index < len(args) and args[index] not in steps:
        index += 2 if args[index] in takes_value else 1
    return index


class PipelineGroup(TyperGroup):
    allow_interspersed_args = True  # read's options may follow IN

    def parse_args(self, ctx: Context, args: list[str]) -> list[str]:
        if not args:
            output.emit_error(
                cast(typer.Context, ctx),
                InvalidArguments(
                    f"read: IN not given; {SHAPE}.", action=f"Run '{cli_name()} read --help' for an example."
                ),
            )
        end = _end(self, args, self.commands)
        with reported(ctx):
            Command.parse_args(self, ctx, args[:end])
            if ctx.args:  # a word after IN that names no step: Typer's «No such command», with suggestions
                self.resolve_command(ctx, ctx.args)
        ctx.args = args[end:]
        return ctx.args

    def invoke(self, ctx: Context) -> Any:
        chain, ctx.args = ctx.args, []
        with ctx:
            source = Command.invoke(self, ctx)
            steps = []
            with reported(ctx):
                while chain:
                    name, command, rest = self.resolve_command(ctx, chain)  # a UsageError for an unknown name
                    command = cast(Command, command)
                    end = _end(command, rest, self.commands)
                    steps.append(command.make_context(name, rest[:end], parent=ctx))
                    chain = rest[end:]
            return run(ctx, source, planned(steps))


def planned(steps: list[Context]) -> list[Any]:
    """The step of each parsed context, checked: a `Planned`, or the `Target` of write."""
    found = []
    for step in steps:
        with step:
            found.append(step.command.invoke(step))
    return found
