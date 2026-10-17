"""Running a pipeline: check its shape and OUT, read, run the steps in order with a line each on stderr, write."""

from __future__ import annotations

import typer

from .. import output
from ..core.errors import InvalidArguments
from .state import Planned, State
from .tables import STDIO, Source, Target, write_records

SHAPE = "a pipeline is 'read IN STEP… write OUT': write comes once, last"


def _shape(planned: list[Planned | Target]) -> tuple[list[Planned], Target]:
    *steps, target = planned or [None]
    if not isinstance(target, Target) or any(isinstance(step, Target) for step in steps):
        raise InvalidArguments(f"read: {SHAPE}.", action="Add 'write OUT' at the end: a file, or '-' for stdout.")
    return [step for step in steps if isinstance(step, Planned)], target


@output.guard
def run(ctx: typer.Context, source: Source, planned: list[Planned | Target]) -> None:
    """Run the steps of `planned` over the table of `source` and write it as its last entry says."""
    steps, target = _shape(planned)
    target.check()
    state = State(source.read(), source.column, journal=source.trace is not None)
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
    if target.address != STDIO:
        payload = {
            "output": target.address,
            "rows": len(state.table),
            "written": written,
            "steps": [s.to_dict() for s in summaries],
        }
        output.emit_success(ctx, payload, render_human=lambda _: None)
