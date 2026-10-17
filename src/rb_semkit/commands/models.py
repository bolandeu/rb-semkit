"""Encoders of the steps by meaning: `models pull NAME` downloads one once into the cache, `models list` shows them,
`models remove NAME` takes one out (`core/vectors/cache`, ADR 0009). They need the vectors extra."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.markup import escape
from rich.table import Table

from .. import output
from ..core.vectors import cache

app = output.group(
    "Encoders of the steps by meaning: pull one once into the cache, list them, remove one."
    " The cache is the system cache, or the folder of the config key models.dir."
)

NAME_HELP = "The encoder: e5-small, bge-m3, potion, or hf:<id> of a model of the Hugging Face hub."
MEGABYTE = 1_000_000


def _start(ctx: typer.Context) -> Path:
    return Path(ctx.obj.get("project") or Path.cwd())


def _payload(pulled: cache.Pulled) -> dict:
    model = pulled.model
    return {
        "name": model.name,
        "repo": model.repo,
        "revision": model.revision,
        "path": str(pulled.folder),
        "size": pulled.size,
        "downloaded": pulled.downloaded,
    }


def _megabytes(size: int) -> str:
    return f"{size / MEGABYTE:.0f} MB"


def _render_pull(data: dict) -> None:
    if data["downloaded"]:
        output.human.echo(
            f"Pulled {data['name']} ({data['repo']}@{data['revision']}): {data['path']}, {_megabytes(data['size'])}."
        )
    else:
        output.human.echo(f"{data['name']} is already in the cache, nothing downloaded: {data['path']}.")


@app.command("pull")
@output.guard
def pull(
    ctx: typer.Context,
    name: str = typer.Argument(..., help=NAME_HELP),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
) -> None:
    """Download an encoder once into the cache, at its pinned revision, and check the checksum of each file.

    A model already in the cache is not downloaded again.
    A pull that fails keeps nothing of the model and exits 5; run it again.
    A hub model (hf:<id>) is fetched at its latest revision: an ONNX export with tokenizer.json, or a model2vec model.

    Example: {cli} models pull e5-small
    """
    output.emit_success(ctx, _payload(cache.pull(name, _start(ctx))), _render_pull)


def _render_list(payload: dict) -> None:
    table = Table("name", "repo", "pulled", "size", "threshold", "path")
    for entry in payload["models"]:
        table.add_row(
            entry["name"],
            escape(entry["repo"]),
            "yes" if entry["pulled"] else "no",
            _megabytes(entry["size"]) if entry["pulled"] else "",
            "" if entry["threshold"] is None else str(entry["threshold"]),
            escape(entry["path"] or ""),
        )
    output.human.console.print(table)


@app.command("list")
@output.guard
def list_models(
    ctx: typer.Context,
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
) -> None:
    """Every encoder semkit knows and every hub model pulled: its repo, revision, whether it is pulled, its size in bytes, its default threshold and its folder.

    Example: {cli} models list --json
    """  # fmt: skip
    output.emit_success(ctx, {"models": cache.catalog(_start(ctx))}, _render_list)


@app.command("remove")
@output.guard
def remove(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The pulled encoder to remove, as `models list` names it."),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    dry_run: bool = output.DryRunOption,
) -> None:
    """Remove an encoder from the cache.

    A model that is not pulled is refused with exit 2 and the pulled ones.
    With --dry-run nothing is removed: it says which folder it would remove.

    Example: {cli} models remove e5-small
    """
    removed = cache.remove(name, _start(ctx), dry_run=output.is_dry_run(ctx))
    verb = output.done(ctx, "Removed", "Would remove")
    output.emit_success(
        ctx,
        {**_payload(removed), "dry_run": output.is_dry_run(ctx)},
        lambda data: output.human.echo(f"{verb} {data['name']}: {data['path']}"),
    )
