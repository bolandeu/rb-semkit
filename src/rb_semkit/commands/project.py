"""The project part (copier's include_project): `init`, `status`, `config`, the global --project and its doctor checks."""

from __future__ import annotations

from pathlib import Path

import typer
from typer.core import TyperOption

from .. import output
from ..core import services
from ..core.errors import CliTooOld, ConfigInvalid
from ..core.models import ProjectConfig
from . import config, init, status


def _remember_project(ctx: typer.Context, _param: object, value: str | None) -> None:
    ctx.ensure_object(dict)["project"] = value


def register(app: typer.Typer) -> None:
    """Add the project commands and the global --project to the CLI's root."""
    app.add_typer(config.app, name="config")
    app.command(name="init")(init.init)
    app.command(name="status")(status.status)
    output.RootGroup.part_options.append(
        TyperOption(
            param_decls=["--project"],
            metavar="TEXT",
            help="Path to the project root.",
            expose_value=False,
            callback=_remember_project,
        )
    )


def doctor_checks(ctx: typer.Context) -> tuple[list[dict], ProjectConfig | None]:
    """The `project`, `config` and `cli_compat` checks of `doctor`, and the project's config when it loads."""
    start = Path(ctx.obj.get("project") or Path.cwd())
    output.vecho(ctx, f"Searching for a project root starting at: {start}")
    root = services.find_project_root(start)
    checks: list[dict] = [{"name": "project", "ok": root is not None, "detail": str(root) if root else None}]
    if root is None:
        return checks, None
    try:
        config = services.load_config(root)  # semkit's load_config does not check cli.min_version: output.guard does
    except ConfigInvalid as exc:
        checks.append({"name": "config", "ok": False, "detail": exc.message})
        return checks, None
    checks.append({"name": "config", "ok": True})
    try:
        services.check_cli_compat(config)
        checks.append({"name": "cli_compat", "ok": True, "detail": f"project requires >= {config.cli.min_version}"})
    except CliTooOld as exc:
        checks.append({"name": "cli_compat", "ok": False, "detail": exc.message})
    return checks, config
