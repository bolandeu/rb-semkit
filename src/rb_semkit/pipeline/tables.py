"""Reading and writing through dataio (ADR 0001, docs/plan.md §3): types as dataio infers them, the text columns text
with NaN as ''; a text column whose every cell is a number with spaces around (« 10») is numbers. '-' is JSONL on
stdin/stdout.

The input, OUT and the trace are checked before the input is read: IN exists, OUT has a format dataio writes and a
folder, the trace has a folder. A dataio error is told in the terms of the command line (IN, OUT, `--trace`).
A file is written to a temporary file next to it and renamed over it: OUT holds the whole result or stays as it was.
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import rb_dataio
from pandas.api import types

from ..core.errors import CliError, InvalidArguments
from ..core.frame import text_columns

STDIO = "-"
STREAM_FORMAT = "jsonl"
WHOLE_COLUMN = "text"
TEXT_COLUMN = "phrase"
BOM = "﻿"
ONE_COLUMN_FORMATS = ("txt",)
REMOTE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)  # a URL or a gsheet:// address: dataio checks it
# The parts of a dataio action that name its Python arguments, not the options of the command line.
PYTHON_HINTS = ("format=", "sep=", "encoding=")
REFUSED = "INVALID_ARGUMENTS"  # the code of a dataio error for a wrong argument: exit 2


def _cli_action(error: rb_dataio.DataioError, action: str) -> str:
    """The action of a dataio error, or `action` when dataio's names its Python arguments."""
    given = error.action or ""
    return action if not given or any(hint in given for hint in PYTHON_HINTS) else given


@contextmanager
def _dataio(action: str, exit_code: int = 1) -> Generator[None]:
    """A DataioError as a CliError with its code and message; `action` replaces an action in Python terms.

    A wrong argument (`INVALID_ARGUMENTS`) exits 2.
    """
    try:
        yield
    except rb_dataio.DataioError as error:
        code = 2 if error.code == REFUSED else exit_code
        raise CliError(error.code, error.message, action=_cli_action(error, action), exit_code=code) from None


def as_text(values: pd.Series) -> pd.Series:
    """The cells as `str`, NaN as ''; a whole float is written without its point (10.0 → '10')."""
    if types.is_float_dtype(values):
        values = values.map(lambda number: int(number) if pd.notna(number) and number.is_integer() else number)
    return values.astype(object).where(values.notna(), "").astype(str)


def numbers(values: pd.Series) -> pd.Series:
    """The cells as numbers when every non-empty one is a number (spaces around are no matter): whole ones as Int64.

    Otherwise the cells as they are.
    """
    text = values.astype(object).where(values.notna(), "").astype(str).str.strip()
    try:
        found = pd.to_numeric(text.mask(text == ""))
    except (TypeError, ValueError):
        return values
    if found.isna().all() and (text != "").any():
        return values
    whole = found.dropna()
    return found.astype("Int64") if (whole == whole.round()).all() else found


def _padded(values: pd.Series) -> bool:
    """Whether a cell of a text column has spaces around its text."""
    text = values.dropna().astype(str)
    return bool((text != text.str.strip()).any())


def exists(address: str) -> bool:
    """Whether the file of `address` is there; '-' and a remote address are taken as they are."""
    return address == STDIO or bool(REMOTE.match(address)) or Path(address.split("#", 1)[0]).exists()


def _check_trace(trace: Path, *, overwrite: bool) -> None:
    """Refuse a trace file that exists without `overwrite` (write's --overwrite), or whose folder does not exist."""
    if trace.exists() and not overwrite:
        raise CliError(
            "OUTPUT_EXISTS",
            f"read: --trace {trace} exists.",
            action="Add --overwrite after 'write OUT' to replace it, or name another file after --trace.",
            exit_code=2,
        )
    if not trace.parent.is_dir():
        raise InvalidArguments(
            f"read: --trace {trace}: its folder does not exist.", action="Name a file in a folder that exists."
        )


@dataclass(frozen=True)
class Source:
    """The input of a pipeline and how it is read."""

    address: str | None
    column: str | None = None
    whole: bool = False
    trace: Path | None = None
    texts: tuple[str, ...] = ()

    def check(self, *, overwrite: bool) -> None:
        """Refuse an IN that does not exist or comes with --text, and a trace file that exists (without `overwrite`) or has no folder."""
        if self.trace is not None:
            _check_trace(self.trace, overwrite=overwrite)
        if self.address is not None and self.texts:
            raise InvalidArguments(
                "read: IN and --text together.", action="Name a table IN, or give phrases with --text, not both."
            )
        if self.address is None and not self.texts:
            raise InvalidArguments(
                "read: IN not given; a pipeline is 'read IN STEP… write OUT'.",
                action="Name a table IN, or give phrases with --text.",
            )
        if self.address is not None and not exists(self.address):
            raise CliError(
                "SOURCE_NOT_FOUND",
                f"read: IN {self.address} does not exist.",
                action="Name a file that exists, or '-' for JSONL on stdin.",
                exit_code=2,
            )

    def columns(self) -> list[str] | None:
        """The columns of the input without its rows; None for stdin, which can be read once only."""
        if self.texts:
            return [TEXT_COLUMN]
        if self.whole:
            return [WHOLE_COLUMN]
        if self.address == STDIO:
            return None
        with _dataio(READ_ACTION, exit_code=2):
            return list(rb_dataio.read(self._address(), limit=0).columns)

    def read(self) -> pd.DataFrame:
        """The table; with `texts` a row of the column `phrase` for each; with `whole` the input as one cell of `text`."""
        if self.texts:
            return pd.DataFrame({TEXT_COLUMN: list(self.texts)})
        if self.whole:
            return pd.DataFrame({WHOLE_COLUMN: [self._text()]})
        if self.address == STDIO:
            with _dataio(STDIN_ACTION, exit_code=2):
                table = _read_stdin()
        else:
            with _dataio(READ_ACTION, exit_code=2):
                table = rb_dataio.read(self._address())
        return self._typed(table)

    def _address(self) -> str:
        """The address of the input; `check` has refused a pipeline without one."""
        if self.address is None:
            raise InvalidArguments("read: IN not given.", action="Name a table IN, or give phrases with --text.")
        return self.address

    def _typed(self, table: pd.DataFrame) -> pd.DataFrame:
        """The text columns as `str`, NaN as ''; a column of numbers that a cell padded with spaces made text, numbers."""
        for name in text_columns(table):
            found = numbers(table[name]) if _padded(table[name]) else table[name]
            table[name] = found if types.is_numeric_dtype(found) else as_text(found)
        return table

    def _text(self) -> str:
        """The text of the input as written, blank lines too, without a BOM; line ends become '\\n'.

        Not through dataio: its txt format reads one row per line and skips the blank ones.
        """
        if self.address == STDIO:
            return sys.stdin.read().removeprefix(BOM)
        return Path(str(self.address)).read_text(encoding="utf-8-sig")


READ_ACTION = "Check that IN is a table file of a format dataio reads (csv, tsv, xlsx, json, jsonl, parquet, txt)."
STDIN_ACTION = "'-' is JSONL on stdin: pass the path of the file as IN instead (any format)."


def _read_stdin() -> pd.DataFrame:
    """The JSONL of stdin; an input that is no JSONL (a CSV) is refused as such."""
    try:
        return rb_dataio.read(STDIO, format=STREAM_FORMAT)
    except rb_dataio.DataioError as error:
        raise CliError(
            "READ_FAILED",
            "read: '-' reads JSONL from stdin, and the input is no JSONL.",
            action=STDIN_ACTION,
            exit_code=2,
        ) from error


@dataclass(frozen=True)
class Target:
    """The output of a pipeline: a file, or '-' for stdout."""

    address: str
    overwrite: bool = False
    columns: list[str] | None = None
    rename: dict[str, str] | None = None

    def check(self) -> None:
        """Refuse an OUT that exists without --overwrite, whose folder does not exist or whose format is unknown."""
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
            raise InvalidArguments(
                f"write: the folder of {self.address} does not exist.", action="Name a file in a folder that exists."
            )
        self.format()

    def format(self) -> str:
        """The format of OUT by its extension; an unknown one is refused with the known ones."""
        known = {ext: info.name for info in rb_dataio.formats() if info.write for ext in info.extensions}
        suffix = Path(self.address).suffix.lower()
        if suffix not in known:
            raise InvalidArguments(
                f"write: OUT {self.address} has no extension of a format dataio writes.",
                action=f"End OUT with one of: {', '.join(known)}; or write '-' for JSONL on stdout.",
            )
        return known[suffix]

    def write(self, table: pd.DataFrame) -> None:
        if self.address == STDIO:
            with _dataio(WRITE_ACTION):
                rb_dataio.write(table, STDIO, format=STREAM_FORMAT, columns=self.columns, rename=self.rename)
            return
        width = len(self.columns) if self.columns else len(table.columns)
        if self.format() in ONE_COLUMN_FORMATS and width > 1:
            raise InvalidArguments(
                f"write: OUT {self.address} holds one column, the table has {width}.",
                action="Write to another format (.csv, .xlsx, .jsonl…), or keep one column before write.",
            )
        path = Path(self.address)
        with tempfile.TemporaryDirectory(dir=path.parent, prefix=f".{path.name}.") as folder:
            part = Path(folder) / path.name
            with _dataio(WRITE_ACTION):
                rb_dataio.write(table, part, backup=False, columns=self.columns, rename=self.rename)
            os.replace(part, path)


WRITE_ACTION = "Check that the folder of OUT is writable and OUT is not open in another program."


def read_lines(address: str) -> list[str]:
    """The lines of a text file or stdin, without line ends and a BOM; dataio skips the blank ones."""
    with _dataio(READ_ACTION, exit_code=2):
        lines = rb_dataio.read(address, format="txt", as_text=True)[WHOLE_COLUMN].fillna("")
    return [line.rstrip("\r") for line in lines]


def write_records(records: list[dict], path: Path) -> None:
    """Rows as JSONL into `path`, replacing it."""
    with _dataio(WRITE_ACTION):
        rb_dataio.write(pd.DataFrame(records), path, format=STREAM_FORMAT, backup=False, overwrite=True)
