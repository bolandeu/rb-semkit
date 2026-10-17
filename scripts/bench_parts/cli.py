"""The CLI pipeline as one `semkit` process: `pipeline` reads a parquet file, runs 5 cleaning steps and writes a parquet
file; `write-xlsx` reads a parquet file and writes it to xlsx with no step (the speed of dataio's xlsx writer).

Their budget is the budget of every operation of the bench (--limit): the library steps plus the read and the write.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd
import rb_dataio

STEPS = [
    "remove-chars", "--kind", "punctuation",
    "remove-stopwords",
    "remove-spaces", "--kind", "extra",
    "drop-cells", "--kind", "empty",
    "dupes", "--kind", "implicit", "--action", "drop",
]  # fmt: skip


def _run(phrases: pd.Series, steps: list[str], target_name: str) -> None:
    with tempfile.TemporaryDirectory() as folder:
        source, target = Path(folder) / "core.parquet", Path(folder) / target_name
        rb_dataio.write(pd.DataFrame({"phrase": phrases}), source, backup=False)
        command = [sys.executable, "-m", "rb_semkit.cli", "read", str(source), "--quiet", *steps, "write", str(target)]
        subprocess.run(command, check=True)


def _pipeline(phrases: pd.Series) -> None:
    _run(phrases, STEPS, "clean.parquet")


def _write_xlsx(phrases: pd.Series) -> None:
    _run(phrases, [], "core.xlsx")


OPERATIONS = {"pipeline": _pipeline, "write-xlsx": _write_xlsx}
