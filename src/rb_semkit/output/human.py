from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.markup import escape
from rich.table import Table

if TYPE_CHECKING:
    import pandas as pd

# Data goes to stdout; errors and diagnostics go to stderr, so
# `<cli> status > out.txt` never captures an "Error: ..." line as data.
console = Console()
err_console = Console(stderr=True)


def echo(message: str) -> None:
    """Print plain text. Escaped: rich would otherwise treat `[...]` in data as markup and drop it."""
    console.print(escape(message))


def echo_markup(message: str) -> None:
    """Print rich markup (`[green]✓[/green]`); escape() any data you put inside it."""
    console.print(message)


def key_values(title: str, pairs: dict) -> None:
    console.print(f"[bold]{escape(title)}[/bold]")
    for key, value in pairs.items():
        console.print(f"  {escape(str(key))}: {escape(str(value))}")


def render_doctor(checks: list[dict]) -> None:
    for check in checks:
        mark = "[green]✓[/green]" if check["ok"] else "[red]✗[/red]"
        detail = f" ({check['detail']})" if check.get("detail") else ""
        console.print(f"{mark} {escape(check['name'] + detail)}")


def is_terminal() -> bool:
    """Whether stdout is a terminal."""
    return console.is_terminal


def render_frame(frame: pd.DataFrame) -> None:
    """Every column and every row of `frame` as a table; an empty cell stays empty."""
    table = Table(*(escape(str(name)) for name in frame.columns))
    for row in frame.astype(object).where(frame.notna(), "").itertuples(index=False):
        table.add_row(*(escape(str(cell)) for cell in row))
    console.print(table)
