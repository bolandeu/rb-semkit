"""`init`: make the folder a project: `.{package}/config.toml` in it (`core.services`).

An existing project is kept unless --force; --dry-run writes nothing.
"""

from __future__ import annotations

from pathlib import Path

import typer

from .. import output
from ..core import services


def _render(ctx: typer.Context, data: dict) -> None:
    if data["already_initialized"]:
        output.human.echo(f"Already initialized in {data['path']} (use --force to reset).")
        return
    title = f"{output.done(ctx, 'Initialized', 'Would initialize')} project in {data['path']}"
    output.human.key_values(title, {"name": data["project"]})


@output.guard
def init(
    ctx: typer.Context,
    name: str | None = typer.Option(None, "--name", help="Project name (defaults to directory name)."),
    force: bool = typer.Option(False, "--force", help="Overwrite an already-initialized project's config."),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    verbose: bool = output.VerboseOption,
    dry_run: bool = output.DryRunOption,
) -> None:
    """Initialize a project: creates .{package}/config.toml in the target directory.

    An initialized project is left as it is without --force.
    With --dry-run nothing is written.

    Example: {cli} init --name demo
    """
    target = Path(ctx.obj.get("project") or Path.cwd()).resolve()
    existing = not force and services.find_project_root(target) == target
    if existing:
        output.vecho(ctx, f"Found existing config at {services.config_path(target)}")
        config = services.load_config(target)
    else:
        config = services.init_project(target, name or target.name, dry_run=output.is_dry_run(ctx))
    output.emit_success(
        ctx,
        {
            "project": config.name,
            "path": str(target),
            "already_initialized": existing,
            "dry_run": output.is_dry_run(ctx),
        },
        lambda data: _render(ctx, data),
    )
