from __future__ import annotations

import typer

from .. import output

HIDDEN = True  # not implemented: kept out of the help (cli.py) until it does something

# Extension point: replace the body with a call into core.services for this CLI's main operation. If it changes
# external state, check `output.is_dry_run(ctx)` first and return a preview instead of acting, and — if the action is
# irreversible — call `output.require_confirmation(ctx, "...", confirm)` right before the change itself.


@output.guard
def run(
    ctx: typer.Context,
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    dry_run: bool = output.DryRunOption,
) -> None:
    """Not implemented yet, and hidden from the help: it changes nothing and says so.

    Example: {cli} run --dry-run
    """
    if output.is_dry_run(ctx):
        output.emit_success(
            ctx,
            {"result": "dry-run", "would_do": "nothing implemented yet — this is a placeholder"},
            render_human=lambda d: output.human.echo("Dry run: no changes made (placeholder operation)."),
        )
        return

    output.emit_success(
        ctx, {"result": "not implemented"}, render_human=lambda d: output.human.echo("run: not implemented yet")
    )
