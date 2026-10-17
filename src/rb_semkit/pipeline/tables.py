"""Reading and writing through dataio (ADR 0001, docs/plan.md §3): types as dataio infers them, but the working
column and the other text columns are text with NaN as ''; '-' is JSONL on stdin/stdout.

A file is written to a temporary file next to it and renamed over it: OUT holds the whole result or stays as it was.
"""

from __future__ import annotations

import os
import sys
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import rb_dataio

from ..core.errors import CliError, InvalidArguments
from ..core.frame import text_columns

STDIO = "-"
STREAM_FORMAT = "jsonl"
WHOLE_COLUMN = "text"
BOM = "\ufeff"


@contextmanager
def _dataio() -> Generator[None]:
    """A DataioError as a CliError with its code, message and action."""
    try:
        yield
    except rb_dataio.DataioError as error:
        raise CliError(error.code, error.message, action=error.action) from None


@dataclass(frozen=True)
class Source:
    """The input of a pipeline and how it is read."""

    address: str
    column: str | None = None
    whole: bool = False
    trace: Path | None = None

    def read(self) -> pd.DataFrame:
        """The table; with `whole` the text of the input as one cell of the column `text`."""
        if self.whole:
            return pd.DataFrame({WHOLE_COLUMN: [self._text()]})
        stream = STREAM_FORMAT if self.address == STDIO else None
        with _dataio():
            table = rb_dataio.read(self.address, format=stream)
        return self._as_text(table)

    def _as_text(self, table: pd.DataFrame) -> pd.DataFrame:
        """The text columns and the working column as `str`, NaN as ''; the other columns keep their types.

        The working column is `column`, else the first text column, else the first column ('2024' is a phrase).
        """
        if table.empty and not len(table.columns):
            return table
        texts = text_columns(table)
        working = self.column if self.column in table.columns else (texts or list(table.columns))[0]
        for name in dict.fromkeys([*texts, working]):
            table[name] = table[name].astype(object).where(table[name].notna(), "").astype(str)
        return table

    def _text(self) -> str:
        """The text of the input as written, blank lines too, without a BOM; line ends become '\\n'.

        Not through dataio: its txt format reads one row per line and skips the blank ones.
        """
        if self.address == STDIO:
            return sys.stdin.read().removeprefix(BOM)
        path = Path(self.address)
        if not path.is_file():
            raise CliError(
                "SOURCE_NOT_FOUND",
                f"read: {self.address} does not exist.",
                action="Name a text file that exists, or '-' for stdin.",
                exit_code=2,
            )
        return path.read_text(encoding="utf-8-sig")


@dataclass(frozen=True)
class Target:
    """The output of a pipeline: a file, or '-' for stdout."""

    address: str
    overwrite: bool = False

    def check(self) -> None:
        """Refuse an OUT that exists without --overwrite, or whose folder does not exist."""
        if self.address == STDIO:
            return
        path = Path(self.address)
        if path.exists() and not self.overwrite:
            raise CliError(
                "OUTPUT_EXISTS",
                f"write: {self.address} exists.",
                action=f"Add --overwrite after 'write {self.address}' to replace it, or name another file.",
                exit_code=2,
            )
        if not path.parent.is_dir():
            raise InvalidArguments(f"write: the folder of {self.address} does not exist; allowed: a file in a folder.")

    def write(self, table: pd.DataFrame) -> None:
        if self.address == STDIO:
            with _dataio():
                rb_dataio.write(table, STDIO, format=STREAM_FORMAT)
            return
        path = Path(self.address)
        with tempfile.TemporaryDirectory(dir=path.parent, prefix=f".{path.name}.") as folder:
            part = Path(folder) / path.name
            with _dataio():
                rb_dataio.write(table, part, backup=False)
            os.replace(part, path)


def read_lines(address: str) -> list[str]:
    """The lines of a text file or stdin, without line ends and a BOM; dataio skips the blank ones."""
    with _dataio():
        lines = rb_dataio.read(address, format="txt", as_text=True)[WHOLE_COLUMN].fillna("")
    return [line.rstrip("\r") for line in lines]


def write_records(records: list[dict], path: Path) -> None:
    """Rows as JSONL into `path`, replacing it."""
    with _dataio():
        rb_dataio.write(pd.DataFrame(records), path, format=STREAM_FORMAT, backup=False, overwrite=True)
