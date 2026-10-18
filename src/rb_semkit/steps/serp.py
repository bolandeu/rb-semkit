"""The SERP step: clusters of phrases by the common URLs of their tops."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..core.errors import InvalidArguments
from ..core.serp.cluster import cluster_serp
from . import Adapted, Prepared, Report, Step, first_text, numbers_of, option, table_of

FREQ_DOC = (
    "freq: a file with the phrases in its first text column and their frequencies in --freq-column; the file is read"
    " like `read` does.\n"
    "freq_column: the column of the frequencies in the --freq file; by default the first column of numbers."
)


def _frequency_column(table: pd.DataFrame, given: str | None) -> str:
    if given is not None:
        if given not in table.columns:
            raise InvalidArguments(
                f"--freq-column {given}: the --freq file has no such column.",
                action=f"Name one of its columns: {', '.join(map(str, table.columns))}.",
            )
        return given
    numeric = [name for name in table.columns if pd.api.types.is_numeric_dtype(table[name])]
    if not numeric:
        raise InvalidArguments(
            "--freq: the file has no column of numbers.",
            action="Name the column of the frequencies with --freq-column.",
        )
    return numeric[0]


def _frequencies(path: str, column: str | None) -> pd.Series:
    """The frequency of each phrase of the --freq file, by phrase."""
    table = table_of(path, "freq")
    phrases, given = first_text(table, "freq"), _frequency_column(table, column)
    return pd.Series(numbers_of(table[given], f"--freq {given}").to_numpy(), index=table[phrases].to_numpy())


def _prepare(options: dict) -> Prepared:
    freq = None if options["freq"] is None else _frequencies(options["freq"], options["freq_column"])
    arguments: dict[str, Any] = {**{k: v for k, v in options.items() if k != "freq_column"}, "freq": freq}
    return lambda table, column: Report(cluster_serp(table, **arguments))


STEPS = [
    Step(
        "cluster-serp",
        Adapted(
            cluster_serp,
            {
                "serp": None,
                "freq": option("freq", str | None, None),
                "freq_column": option("freq_column", str | None, None),
            },
            FREQ_DOC,
        ),
        "report",
        _prepare,
        "The step reads the current table, a SERP with the columns phrase, position and url; the table of the"
        " clusters replaces it, its column phrase is the working one.",
    )
]
