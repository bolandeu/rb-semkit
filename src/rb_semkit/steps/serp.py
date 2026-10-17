"""The SERP step: clusters of phrases by the common URLs of their tops."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..core.errors import InvalidArguments
from ..core.serp.cluster import cluster_serp
from . import Adapted, Prepared, Report, Step, option, table_of

FREQ_DOC = (
    "freq: a file with the columns phrase and freq, the frequency of each phrase; the file is read like `read` does."
)


def _frequencies(path: str) -> pd.DataFrame:
    table = table_of(path, "freq")
    try:
        return table.assign(freq=pd.to_numeric(table["freq"]))
    except (KeyError, ValueError):
        raise InvalidArguments(
            "freq: the file needs a column freq of numbers; allowed: columns phrase and freq."
        ) from None


def _prepare(options: dict) -> Prepared:
    freq = None if options["freq"] is None else _frequencies(options["freq"])
    arguments: dict[str, Any] = {**options, "freq": freq}
    return lambda table, column: Report(cluster_serp(table, **arguments))


STEPS = [
    Step(
        "cluster-serp",
        Adapted(cluster_serp, {"serp": None, "freq": option("freq", str | None, None)}, FREQ_DOC),
        "report",
        _prepare,
        "The step reads the current table, a SERP with the columns phrase, position and url; the table of the"
        " clusters replaces it, its column phrase is the working one.",
    )
]
