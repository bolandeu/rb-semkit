"""The pipeline as one chained group: `read IN [options] STEP… write OUT` (ADR 0008).

The Click that Typer ships has no chained groups, so this group chains its commands itself, as Click's `chain=True`:
it parses every step of the command line first, then reads the input and runs them in the order written. The options
of read and IN come before the first step: IN is the first word that is no option, the first step the second one.
A usage error of read or of a step is reported as a CliError naming the step (with --json, the error envelope).
"""

from __future__ import annotations

from collections.abc import Generator
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
from .run import run
from .tables import STDIO


@contextmanager
def _reported(ctx: Context) -> Generator[None]:
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


class PipelineGroup(TyperGroup):
    allow_interspersed_args = True  # read's options may follow IN

    def parse_args(self, ctx: Context, args: list[str]) -> list[str]:
        if not args:
            output.help_if_no_command(cast(typer.Context, ctx))
        own, chain = self._split(args)
        with _reported(ctx):
            Command.parse_args(self, ctx, own)
        ctx.args = chain
        return chain

    def _split(self, args: list[str]) -> tuple[list[str], list[str]]:
        """The words of read itself (its options and IN) and the chain of steps after them."""
        takes_value = {name for param in self.params if not getattr(param, "is_flag", True) for name in param.opts}
        source_seen, index = False, 0
        while index < len(args):
            word = args[index]
            if word.startswith("-") and word != STDIO:
                index += 2 if word in takes_value else 1
                continue
            if source_seen:
                return args[:index], args[index:]
            source_seen, index = True, index + 1
        return args, []

    def invoke(self, ctx: Context) -> Any:
        chain, ctx.args = ctx.args, []
        with ctx:
            source = Command.invoke(self, ctx)
            steps = []
            with _reported(ctx):
                while chain:
                    name, command, chain = self.resolve_command(ctx, chain)  # a UsageError for an unknown name
                    step = cast(Command, command).make_context(name, chain, parent=ctx)
                    chain, step.args = step.args, []
                    steps.append(step)
            planned = []
            for step in steps:
                with step:
                    planned.append(step.command.invoke(step))
            return run(ctx, source, planned)
