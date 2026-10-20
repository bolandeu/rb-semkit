"""Running a pipeline: check its shape, OUT, IN and the trace, read, run the steps in order with a line each on stderr,
write, and end with one line that says what was written.

`run_each` runs a chain once for each phrase of the input (a workflow with per_phrase) and joins the parts.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

import pandas as pd
import typer

from .. import output
from ..core.errors import InvalidArguments
from .state import Planned, State, Summary, check_as
from .tables import STDIO, TEXT_COLUMN, Source, Target, as_text, write_records

SHAPE = "a pipeline is 'read IN STEP… write OUT': write comes once, last"
INPUT_COLUMN = "input"  # the phrase each row of a run for each phrase comes from


def _shape(planned: list[Planned | Target]) -> tuple[list[Planned], Target | None]:
    """The steps and the write that closes them; None when the pipeline ends without write."""
    target = planned[-1] if planned and isinstance(planned[-1], Target) else None
    steps = planned[:-1] if target else planned
    if not all(isinstance(step, Planned) for step in steps):
        raise InvalidArguments(f"read: {SHAPE}.", action="Put 'write OUT' once, at the end: a file, or '-' for stdout.")
    return cast("list[Planned]", steps), target


def _check(source: Source, steps: list[Planned], target: Target | None) -> None:
    """Everything that can be refused before the input is read."""
    if target is not None:
        target.check()
    source.check(overwrite=target is not None and target.overwrite)
    if any(step.as_column is not None for step in steps) and (columns := source.columns()) is not None:
        check_as(steps, columns)


def _ending(payload: dict) -> str:
    """The last line of a pipeline in human mode."""
    if not payload["written"]:
        return f"Dry run: {payload['rows']} rows, nothing written."
    if payload["output"] is None:
        return f"Printed {payload['rows']} rows."
    target = "stdout" if payload["output"] == STDIO else payload["output"]
    return f"Wrote {payload['rows']} rows to {target}."


def _target(ctx: typer.Context, target: Target | None) -> Target | None:
    """The write of the pipeline; for a pipeline without one: None to print a table, else '-' for JSONL on stdout."""
    if target is not None:
        return target
    printed = not ctx.obj.get("json") and not output.is_dry_run(ctx) and output.human.is_terminal()
    return None if printed else Target(STDIO)


def _applied(ctx: typer.Context, state: State, steps: list[Planned]) -> list[Summary]:
    """Run `steps` over the table of `state`, a line on stderr after each one."""
    summaries = []
    for step in steps:
        summaries.append(state.apply(step))
        if not ctx.obj.get("quiet"):
            typer.echo(summaries[-1].line(), err=True)
    return summaries


def _close(ctx: typer.Context, target: Target | None, table: pd.DataFrame, summaries: list[Summary]) -> None:
    """Print or write the result, then the line that says what was written."""
    written = not output.is_dry_run(ctx)
    if written:
        if target is None:
            output.human.render_frame(table)
        else:
            target.write(table)
    payload = {
        "output": target.address if target else None,
        "rows": len(table),
        "written": written,
        "steps": [s.to_dict() for s in summaries],
    }
    if target is not None and target.address != STDIO:
        output.emit_success(ctx, payload, render_human=lambda data: typer.echo(_ending(data)))
    elif not ctx.obj.get("quiet") and not ctx.obj.get("json"):
        typer.echo(_ending(payload), err=True)


@output.guard
def run(ctx: typer.Context, source: Source, planned: list[Planned | Target]) -> None:
    """Run the steps of `planned` over the table of `source` and write it as its last entry says.

    Without a write the result is printed as a table in a terminal, else written as JSONL to stdout.
    """
    steps, closing = _shape(planned)
    target = _target(ctx, closing)
    _check(source, steps, target)
    table = source.read()
    check_as(steps, table.columns)  # again for stdin, whose columns are known only now
    state = State(table, source.column, journal=source.trace is not None)
    summaries = _applied(ctx, state, steps)
    # The trace first: when it fails, OUT stays as it was.
    if not output.is_dry_run(ctx) and source.trace is not None and state.journal is not None:
        write_records(state.journal, source.trace)
    _close(ctx, target, state.table, summaries)


@output.guard
def run_each(ctx: typer.Context, source: Source, plan: Callable[[str], list[Planned]], closing: Target | None) -> None:
    """Run the steps `plan` gives for each phrase of the working column of `source`, over that phrase alone.

    The parts are joined in the order of the input, each under a first column `input` that holds its phrase, and
    written as `run` writes them.
    """
    target = _target(ctx, closing)
    _check(source, [], target)
    whole = State(source.read(), source.column)
    parts, summaries = [], []
    for phrase in as_text(whole.table[whole.column]):
        steps = plan(phrase)
        check_as(steps, [TEXT_COLUMN])
        state = State(pd.DataFrame({TEXT_COLUMN: [phrase]}), None)
        summaries += _applied(ctx, state, steps)
        parts.append(state.table.reset_index(drop=True))
        parts[-1].insert(0, INPUT_COLUMN, phrase)
    _close(
        ctx, target, pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=[INPUT_COLUMN]), summaries
    )
