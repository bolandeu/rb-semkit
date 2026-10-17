"""The root command: the global options, --version, --ai, and every module of the commands package as a command.

A module of the commands package is registered by its name, so a new command needs no edit here. --ai prints the
bundled SKILL.md and then the section each command module gives by `ai_section()` (the pipeline steps).
"""

from __future__ import annotations

import importlib
import pkgutil
from importlib import resources
from types import ModuleType

import typer

from . import commands, output
from .core.version import DEV_VERSION, cli_name, installed_version, package_summary

_PACKAGE_NAME = __name__.split(".")[0]

# A bare `<cli>` is the discovery entry point for humans and agents alike:
# name + version + description, then every command with the first line of
# its docstring. No `no_args_is_help` (that exits 2) — main_options() below
# prints this and exits 0. Shell completion stays enabled.
app = typer.Typer(
    help=f"{cli_name()} {installed_version() or DEV_VERSION} — {package_summary() or 'project-aware automation CLI'}"
)


def _command_modules() -> list[ModuleType]:
    """Every module of the commands package, by name: a new command module needs no edit here."""
    names = sorted(info.name for info in pkgutil.iter_modules(commands.__path__))
    return [importlib.import_module(f"{commands.__name__}.{name}") for name in names]


COMMAND_MODULES = _command_modules()

# A module is a command group when it exposes a Typer `app` (`auth status` in every CLI), else a command when it has
# a function of its own name (`init.init`). `HIDDEN = True` in a module keeps its command out of the help.
for module in COMMAND_MODULES:
    name = module.__name__.rsplit(".", 1)[-1]
    if isinstance(getattr(module, "app", None), typer.Typer):
        app.add_typer(module.app, name=name)
    elif callable(getattr(module, name, None)):
        app.command(name=name, hidden=getattr(module, "HIDDEN", False))(getattr(module, name))


def _show_version(ctx: typer.Context) -> None:
    """Print the version, as the envelope `{"ok": true, "version": ...}` with --json, and exit."""
    output.emit_success(ctx, {"version": installed_version() or DEV_VERSION}, lambda data: typer.echo(data["version"]))
    raise typer.Exit()


def _ai_callback(value: bool) -> None:
    """Print the bundled agent skill doc to stdout, then the section each command module gives by `ai_section()`.

    For agents that can execute this CLI but cannot read files from disk
    (e.g. a sandboxed shell with no access to a SKILL.md on the filesystem),
    this is the fallback way to get full usage guidance.
    """
    if not value:
        return
    content = resources.files(f"{_PACKAGE_NAME}.data").joinpath("SKILL.md").read_text()
    sections = [module.ai_section() for module in COMMAND_MODULES if hasattr(module, "ai_section")]
    typer.echo("\n".join([content, *sections]))
    raise typer.Exit()


@app.callback(invoke_without_command=True)
def main_options(
    ctx: typer.Context,
    project: str = typer.Option(None, "--project", help="Path to the project root."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON output."),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress non-essential output."),
    verbose: bool = typer.Option(False, "--verbose", help="Emit extra diagnostic output."),
    non_interactive: bool = typer.Option(False, "--non-interactive", help="Never prompt; fail instead."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would happen without making changes."),
    version: bool = typer.Option(False, "--version", help="Show the version and exit."),
    ai: bool = typer.Option(
        False,
        "--ai",
        callback=_ai_callback,
        is_eager=True,
        help="Print AI-oriented usage documentation (the bundled skill doc) and exit.",
    ),
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["project"] = project
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
