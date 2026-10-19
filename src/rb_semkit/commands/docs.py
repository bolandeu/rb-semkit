"""`docs`: the help of every command and step as one document for people (`core.docs`), for a viewer such as InSpectra."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.markup import escape

from .. import output
from ..core import docs as document
from ..core.errors import InvalidArguments
from ..steps.docs_hook import ReadSteps


@output.guard
def docs(
    ctx: typer.Context,
    out: Path = typer.Option(None, "--out", metavar="FILE", help="Write the document to FILE (replaced when it exists); by default to stdout."),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    verbose: bool = output.VerboseOption,
) -> None:  # fmt: skip
    """Write the help of every command and step as one document for people: OpenCLI with the commands at the root.

    The document follows the help standard: each command has its summary, description and examples apart, each option ends with its default and allowed values, and each step page shows how to give the step its input. The same version writes the same bytes. A viewer such as InSpectra renders it as HTML.

    Example: {cli} docs --out docs.json
    """
    root = ctx.find_root().command
    text = document.text(root, ReadSteps(root))
    if out is None:
        typer.echo(text, nl=False)
        return
    try:
        out.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise InvalidArguments(f"Cannot write {out}: {exc.strerror}.") from exc
    # stdout stays empty without --json (the document's bytes go to FILE only): the report goes to stderr.
    output.emit_success(
        ctx, {"path": str(out)}, lambda data: output.human.err_console.print(escape(f"Wrote {data['path']}"))
    )
