"""The CLI pipeline: read a parquet file, run 5 cleaning steps, write a parquet file, as one `semkit` process.

Its budget is the budget of every operation of the bench (--limit): the library steps plus the read and the write.
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


def _pipeline(phrases: pd.Series) -> None:
    with tempfile.TemporaryDirectory() as folder:
        source, target = Path(folder) / "core.parquet", Path(folder) / "clean.parquet"
        rb_dataio.write(pd.DataFrame({"phrase": phrases}), source, backup=False)
        command = [sys.executable, "-m", "rb_semkit.cli", "read", str(source), "--quiet", *STEPS, "write", str(target)]
        subprocess.run(command, check=True)


OPERATIONS = {"pipeline": _pipeline}
