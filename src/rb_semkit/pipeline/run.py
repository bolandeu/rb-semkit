"""Running a pipeline: check its shape, OUT, IN and the trace, read, run the steps in order with a line each on stderr,
write, and end with one line that says what was written."""

from __future__ import annotations

import typer

from .. import output
from ..core.errors import InvalidArguments
from .state import Planned, State, check_as
from .tables import STDIO, Source, Target, write_records

SHAPE = "a pipeline is 'read IN STEP… write OUT': write comes once, last"


def _shape(planned: list[Planned | Target]) -> tuple[list[Planned], Target]:
    *steps, target = planned or [None]
    if not isinstance(target, Target) or any(isinstance(step, Target) for step in steps):
        raise InvalidArguments(f"read: {SHAPE}.", action="Add 'write OUT' at the end: a file, or '-' for stdout.")
    return [step for step in steps if isinstance(step, Planned)], target


def _check(source: Source, steps: list[Planned], target: Target) -> None:
    """Everything that can be refused before the input is read."""
    target.check()
    source.check(overwrite=target.overwrite)
    if any(step.as_column is not None for step in steps) and (columns := source.columns()) is not None:
        check_as(steps, columns)


def _ending(payload: dict) -> str:
    """The last line of a pipeline in human mode."""
    if not payload["written"]:
        return f"Dry run: {payload['rows']} rows, nothing written."
    target = "stdout" if payload["output"] == STDIO else payload["output"]
    return f"Wrote {payload['rows']} rows to {target}."


@output.guard
def run(ctx: typer.Context, source: Source, planned: list[Planned | Target]) -> None:
    """Run the steps of `planned` over the table of `source` and write it as its last entry says."""
    steps, target = _shape(planned)
    _check(source, steps, target)
    table = source.read()
    check_as(steps, table.columns)  # again for stdin, whose columns are known only now
    state = State(table, source.column, journal=source.trace is not None)
    summaries = []
    for step in steps:
        summaries.append(state.apply(step))
        if not ctx.obj.get("quiet"):
            typer.echo(summaries[-1].line(), err=True)
    written = not output.is_dry_run(ctx)
    if written:
        # The trace first: when it fails, OUT stays as it was.
        if source.trace is not None and state.journal is not None:
            write_records(state.journal, source.trace)
        target.write(state.table)
    payload = {
        "output": target.address,
        "rows": len(state.table),
        "written": written,
        "steps": [s.to_dict() for s in summaries],
    }
    if target.address != STDIO:
        output.emit_success(ctx, payload, render_human=lambda data: typer.echo(_ending(data)))
    elif not ctx.obj.get("quiet") and not ctx.obj.get("json"):
        typer.echo(_ending(payload), err=True)
