"""Word lists: `lists` shows every list, `lists show NAME` its items, `lists add` and `lists rm` change the Human's folders.

The commands work on the files of a folder of lists (`core/wordlists`); the bundled lists are shown and used, never
changed. `ai_section()` gives the lists to `--ai`.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import typer
from rich.markup import escape
from rich.table import Table

from .. import output
from ..core import services, wordlists
from ..core.wordlists import folders

app = typer.Typer(help="Word lists: the bundled ones and the Human's own (list, show, add, rm).")
PROJECT_FOLDER = folders.PROJECT
FOLDER_HELP = (
    f"'{PROJECT_FOLDER}' (the project's {services.PROJECT_DIR_NAME}/{services.LISTS_DIR_NAME}) or the path of a folder"
    " of lists; ~ is the home folder."
)


def _start(ctx: typer.Context) -> Path:
    return Path(ctx.obj.get("project") or Path.cwd())


def _folder(ctx: typer.Context, where: str) -> Path:
    """The folder `--to` or `--from` names: the project's lists folder, or a path."""
    if where == PROJECT_FOLDER:
        return services.project_lists_dir(services.require_project_root(_start(ctx)))
    return Path(where).expanduser()


def _render_lists(payload: dict) -> None:
    table = Table("name", "source", "lines", "description")
    for entry in payload["lists"]:
        table.add_row(entry["name"], escape(entry["source"]), str(entry["lines"]), escape(entry["description"]))
    output.human.console.print(table)


@app.callback(invoke_without_command=True)
@output.guard
def lists(
    ctx: typer.Context,
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
) -> None:
    """Show every word list: its name, where it comes from, its lines and its description.

    A step takes a list as @NAME in an option that takes items. The project's lists come first, then the folders of
    the config key lists and of the variable SEMKIT_LISTS, then the bundled lists.

    Example: {cli} lists --json
    """
    if ctx.invoked_subcommand is not None:
        return
    found = wordlists.names(_start(ctx))
    output.emit_success(ctx, {"lists": [asdict(entry) for entry in found]}, _render_lists)


@app.command("show")
@output.guard
def show(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The name of the list, as niche/mebel (see `lists`)."),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
) -> None:
    """Show the items of a word list, one per line.

    Example: {cli} lists show minus/cheap
    """
    start = _start(ctx)
    entry = wordlists.describe(name, start)
    items = wordlists.resolve(name, start)
    output.emit_success(ctx, {**asdict(entry), "items": items}, lambda data: typer.echo("\n".join(data["items"])))


@app.command("add")
@output.guard
def add(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The name to give the list, as niche/mebel."),
    file: Path = typer.Argument(..., help="The text file to copy: one item per line, a first line '# …' is the description."),
    to: str = typer.Option(PROJECT_FOLDER, "--to", help=f"Where to put the list: {FOLDER_HELP}"),
    replace: bool = typer.Option(False, "--replace", help="Overwrite the list when the folder has it."),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    dry_run: bool = output.DryRunOption,
) -> None:  # fmt: skip
    """Copy a file into a folder of word lists under a name.

    An existing list is refused without --replace. With --dry-run the file is not copied.

    Example: {cli} lists add niche/mebel mebel.txt --to project
    """
    target = wordlists.store.add(name, file, _folder(ctx, to), replace=replace, dry_run=output.is_dry_run(ctx))
    verb = "Would add" if output.is_dry_run(ctx) else "Added"
    output.emit_success(
        ctx,
        {"name": name, "path": str(target), "dry_run": output.is_dry_run(ctx)},
        lambda data: output.human.echo(f"{verb} {data['name']}: {data['path']}"),
    )


@app.command("rm")
@output.guard
def rm(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The name of the list to remove, as niche/mebel."),
    source_folder: str = typer.Option(PROJECT_FOLDER, "--from", help=f"Where the list is: {FOLDER_HELP}"),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    dry_run: bool = output.DryRunOption,
) -> None:
    """Remove a word list from a folder of lists. A bundled list is never removed.

    With --dry-run nothing is removed.

    Example: {cli} lists rm niche/mebel --from project
    """
    target = wordlists.store.remove(name, _folder(ctx, source_folder), dry_run=output.is_dry_run(ctx))
    verb = "Would remove" if output.is_dry_run(ctx) else "Removed"
    output.emit_success(
        ctx,
        {"name": name, "path": str(target), "dry_run": output.is_dry_run(ctx)},
        lambda data: output.human.echo(f"{verb} {data['name']}: {data['path']}"),
    )


def ai_section() -> str:
    """The word lists, for `semkit --ai`."""
    lines = [
        "## Word lists",
        "",
        "`@NAME` in an option that takes items is a list; `semkit lists show NAME` shows its items. Lists you add:",
        "`semkit lists add NAME FILE [--to project|PATH]`, `semkit lists rm NAME`.",
        "",
    ]
    lines += [
        f"- `{entry.name}` ({entry.source}, {entry.lines} lines): {entry.description}" for entry in wordlists.names()
    ]
    return "\n".join(lines) + "\n"
