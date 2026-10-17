from __future__ import annotations

import json
from pathlib import Path

import typer

from .. import output
from ..core import models, services

app = output.group("Manage project configuration.")


def _line(data: dict) -> str:
    """`key = value`, a value that is not text as JSON (["/abs"], not a Python list)."""
    value = data["value"]
    return f"{data['key']} = {value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)}"


@app.command("list")
@output.guard
def list_config(
    ctx: typer.Context,
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
) -> None:
    """List all configuration values, one key per line as `config get` and `config set` name it.

    Example: {cli} config list --json
    """
    config = services.load_config(services.require_project_root(Path(ctx.obj.get("project") or Path.cwd())))
    lines = [_line({"key": key, "value": models.value(config, key)}) for key in models.config_keys()]
    output.emit_success(ctx, config.model_dump(), render_human=lambda _: output.human.echo("\n".join(lines)))


@app.command("get")
@output.guard
def get_config(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="Dotted config key, e.g. cli.min_version (see `config list`)."),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
) -> None:
    """Get a single configuration value, or a whole section (cli).

    Example: {cli} config get cli.min_version
    """
    start = Path(ctx.obj.get("project") or Path.cwd())
    value = models.value(services.load_config(services.require_project_root(start)), key)
    output.emit_success(ctx, {"key": key, "value": value}, render_human=lambda d: output.human.echo(_line(d)))


@app.command("set")
@output.guard
def set_config(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="Dotted config key, e.g. cli.min_version (see `config list`)."),
    value: str = typer.Argument(..., help='New value: text for a text key, JSON for any other, as 2 or \'["/abs/lists"]\'.'),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    dry_run: bool = output.DryRunOption,
) -> None:  # fmt: skip
    """Set a single, non-secret configuration value.

    A value of the wrong form is refused with exit 2 and the form the key takes; lists takes a JSON list of folders.
    The version the project needs is not checked here, so cli.min_version can be lowered.
    With --dry-run the config is not written.

    Example: {cli} config set cli.min_version 0.2.0
    """
    root = services.require_project_root(Path(ctx.obj.get("project") or Path.cwd()))
    config = models.with_value(services.load_config(root), key, value)
    if not output.is_dry_run(ctx):
        services.save_config(root, config)
    verb = output.done(ctx, "Set", "Would set")
    output.emit_success(
        ctx,
        {"key": key, "value": models.value(config, key), "dry_run": output.is_dry_run(ctx)},
        render_human=lambda d: output.human.echo(f"{verb} {_line(d)}"),
    )
