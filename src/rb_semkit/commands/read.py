"""The pipeline command `read IN STEP … write OUT` (ADR 0008): read, a command for each step of the step table, write.

read opens the pipeline and write closes it; the steps between come from `steps.areas()`. `ai_section()` gives the
steps to `--ai`.
"""

from __future__ import annotations

from pathlib import Path

import typer

from .. import output, steps
from ..core.errors import InvalidArguments
from ..pipeline.commands import ListsHelp, step_command, takes_items
from ..pipeline.group import PipelineGroup
from ..pipeline.tables import Source, Target


@output.guard
def read(
    ctx: typer.Context,
    source: str = typer.Argument(None, metavar="IN", help="The table to read: a file of any format dataio reads, or '-' for JSONL on stdin. Left out with --text."),
    texts: list[str] = typer.Option(None, "--text", metavar="TEXT", help="A phrase from the command line, repeatable: the table has one column phrase and a row for each --text, in the order given. IN is then left out."),
    column: str = typer.Option(None, "--column", help="The working column the steps read and change; by default the first text column."),
    whole: bool = typer.Option(False, "--whole", help="Read a text file as one cell of the column text (an article)."),
    trace: Path = typer.Option(None, "--trace", metavar="FILE", help="Write every cell a step changes and every row it drops to FILE as JSONL: row (1 is the first row under the header), step, column, before, after. An existing FILE needs --overwrite."),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    dry_run: bool = typer.Option(False, "--dry-run", help="Read and run every step, print the summary, write nothing."),
) -> Source:  # fmt: skip
    """Read a table, run the steps in the order written, write the result: one pipeline.

    Each step works on the current table. A change step rewrites the working column (with --as NAME it writes a new column NAME, which the next steps work on), a filter keeps or drops rows, a report (n-grams) makes its table the current one and its first text column the working one. After each step one line goes to stderr: the step, the rows before and after it, the cells it changed; the last line says how many rows went where. A pipeline that ends without write prints the result as a table in the terminal; with --json, or when stdout is not a terminal, it writes JSONL to stdout as `write -` does. Every step and option is checked before the input is read.

    Columns are read with the types of the file: numbers stay numbers, a text column is text and its empty cell an empty text. A column of numbers with spaces around a cell is numbers too. A column of numbers picked as the working column is text for the step and is written back as numbers. An option that takes items takes a comma list 'a,b', @FILE (one item per line, or the first column of a table without its header) or @NAME of a list (@stop/semtools, @minus/cheap…; `{cli} lists` shows them all). `{cli} read IN STEP --help` shows a step.

    Example: {cli} read core.csv remove-words --items купить dupes --kind lemmas --action drop write out.csv

    Phrases from the command line, the result as a table: {cli} read --text "растаможка авто" synonym-candidates --all
    """
    return Source(source, column, whole, trace, tuple(texts or ()))


@output.guard
def write(
    ctx: typer.Context,
    target: str = typer.Argument(..., metavar="OUT", help="The file to write, its format by its extension; '-' for JSONL on stdout."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Replace OUT when it exists."),
    columns: list[str] = typer.Option(None, "--columns", metavar="NAME,NAME", help="The columns to write, in this order: a comma list, repeatable. By default all, as the steps made them."),
    rename: list[str] = typer.Option(None, "--rename", metavar="OLD=NEW", help="Write the column OLD under the name NEW, repeatable; applied after --columns, so OLD is a name the selection keeps. A swap a=b, b=a is allowed."),
) -> Target:  # fmt: skip
    """Write the current table to OUT: the last step of a pipeline.

    The file is written whole or not at all: a failed step or write leaves it as it was. With --dry-run nothing is written. A closed output (`| head`) ends the pipeline quietly.

    --columns and --rename choose, order and name the output columns; a name the table lacks, or two columns with one name, is refused (exit 2) with the columns there are.

    Example: {cli} read core.csv dupes --kind exact --action drop write out.csv --overwrite

    Chosen columns, renamed: {cli} read phrases.csv nearest --to Q write - --columns phrase,similarity --rename similarity=сходство
    """
    names = [name.strip() for value in columns or () for name in value.split(",")]
    return Target(target, overwrite, names or None, _renames(rename) or None)


def _renames(pairs: list[str] | None) -> dict[str, str]:
    """`OLD=NEW` pairs as a mapping; the pair is split on its first '='."""
    renames = {}
    for pair in pairs or ():
        old, found, new = pair.partition("=")
        if not found:
            raise InvalidArguments(f"write: --rename {pair}: no '='.", action="Give --rename OLD=NEW.")
        renames[old] = new
    return renames


app = typer.Typer(cls=PipelineGroup, help=read.__doc__)
app.callback(invoke_without_command=True)(read)
for area_steps in steps.areas().values():
    for step in area_steps:
        app.command(step.name, cls=ListsHelp if takes_items(step) else None)(step_command(step))
app.command("write")(write)


def ai_section() -> str:
    """The steps, for `semkit --ai`."""
    return steps.ai_section()
