"""The root command: the global options, --version, and every module of the commands package as a command.

A module of the commands package is registered by its name, so a new command needs no edit here. `--ai` (the skill
part) prints the bundled SKILL.md and then the section each command module gives by `ai_section()` (the pipeline steps).
"""

from __future__ import annotations

import typer

from . import commands, output
from .core.version import DEV_VERSION, cli_name, installed_version, optional_module, package_summary

_PACKAGE_NAME = __name__.split(".")[0]
# Optional parts (copier questions, dropped by _exclude): each one ships a module that registers its
# commands and global options. Probed at runtime, so this file needs no template logic.
PARTS = ("project", "skill", "describe", "db")

# A bare `<cli>` is the discovery entry point for humans and agents alike:
# name + version + description, then every command with the first line of
# its docstring. No `no_args_is_help` (that exits 2) — main_options() below
# prints this and exits 0. Shell completion stays enabled.
app = typer.Typer(
    cls=output.RootGroup,  # a usage error under --json is the error envelope
    help=f"{cli_name()} {installed_version() or DEV_VERSION} — {package_summary() or 'project-aware automation CLI'}",
)

for part in PARTS:
    if module := optional_module(f"{_PACKAGE_NAME}.commands.{part}"):
        module.register(app)

_registered = {typer_command.name for typer_command in app.registered_commands} | {
    group.name for group in app.registered_groups
}

# A module is a command group when it exposes a Typer `app` (`auth status` in every CLI), else a command when it has
# a function of its own name (`init.init`). `HIDDEN = True` in a module keeps its command out of the help. A command
# a part registered above is not added again.
for module in commands.modules():
    name = module.__name__.rsplit(".", 1)[-1]
    if name in _registered:
        continue
    if isinstance(getattr(module, "app", None), typer.Typer):
        app.add_typer(module.app, name=name)
    elif callable(getattr(module, name, None)):
        app.command(name=name, hidden=getattr(module, "HIDDEN", False))(getattr(module, name))


def _show_version(ctx: typer.Context) -> None:
    """Print the version, as the envelope `{"ok": true, "version": ...}` with --json, and exit."""
    output.emit_success(ctx, {"version": installed_version() or DEV_VERSION}, lambda data: typer.echo(data["version"]))
    raise typer.Exit()


@app.callback(invoke_without_command=True)
def main_options(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON output."),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress non-essential output."),
    verbose: bool = typer.Option(False, "--verbose", help="Emit extra diagnostic output."),
    non_interactive: bool = typer.Option(False, "--non-interactive", help="Never prompt; fail instead."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would happen without making changes."),
    version: bool = typer.Option(False, "--version", help="Show the version and exit."),
) -> None:
    ctx.ensure_object(dict)  # a part's global option (--project) may have put its value here already
    ctx.obj["json"] = json_output
    ctx.obj["quiet"] = quiet
    ctx.obj["verbose"] = verbose
    ctx.obj["non_interactive"] = non_interactive
    ctx.obj["dry_run"] = dry_run
    output.configure_logging(verbose)
    if version:  # not eager: it reads --json, wherever it stands
        _show_version(ctx)
    output.help_if_no_command(ctx)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
