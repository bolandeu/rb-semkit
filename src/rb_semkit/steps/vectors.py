"""The steps by meaning: phrases compared by their phrase vectors (the vectors extra and an encoder pulled once).

The options every step by meaning shares are here: --model (the encoder) and --threshold (the similarity of one
intent; by default the threshold of the model). `MEANING` adapts them for a step, `by_meaning` gives the encoder and
the threshold they name; both refuse before the input is read.
"""

from __future__ import annotations

import pandas as pd

from ..core.errors import InvalidArguments
from ..core.frame import Frame
from ..core.vectors import encoder, registry
from ..core.vectors.cluster import cluster_meaning
from ..core.vectors.encoder import Encoder
from . import Adapted, Columns, Prepared, Step, numbers_of, option, prepared_for

MEANING = {
    "encoder": None,
    "threshold": option("threshold", float | None, None),
    "model": option("model", str, registry.default_name()),
}
MODEL_DOC = (
    "model: the encoder, pulled once with `semkit models pull NAME`: e5-small, bge-m3, potion, or hf:<id> of a model"
    " of the Hugging Face hub. Without --threshold the step takes the threshold of the model; a hub model has none."
)
FREQ_DOC = (
    "freq: the column of the frequencies of the phrases in the current table; the cluster is named after its most"
    " frequent phrase. Without it, after the phrase nearest the centre of the cluster (the mean of its vectors)."
)


def by_meaning(options: dict) -> tuple[Encoder, float]:
    """The encoder and the threshold the options --model and --threshold name."""
    model = registry.model(options["model"])
    threshold = registry.threshold(model, options["threshold"])
    return encoder.encoder_for(model, prepared_for()), threshold


def frequencies_of(table: pd.DataFrame, name: str) -> pd.Series:
    if name not in table.columns:
        raise InvalidArguments(
            f"--freq {name}: the table has no such column.",
            action=f"Name one of its columns: {', '.join(map(str, table.columns))}.",
        )
    return numbers_of(table[name], f"--freq {name}")


def _prepare(options: dict) -> Prepared:
    found_encoder, threshold = by_meaning(options)

    def run(table: pd.DataFrame, column: str) -> Columns:
        freq = None if options["freq"] is None else frequencies_of(table, options["freq"])
        found = cluster_meaning(Frame(table, column).phrases, encoder=found_encoder, threshold=threshold, freq=freq)
        return Columns(found, note=f"index: {found.attrs['index']}")

    return run


STEPS = [
    Step(
        "cluster-meaning",
        Adapted(cluster_meaning, {**MEANING, "freq": option("freq", str | None, None)}, MODEL_DOC, FREQ_DOC),
        "change",
        _prepare,
        "The step adds the columns cluster, cluster_name and similarity right after the working column; the rows"
        " stay. Its summary names the index it searched: exact, or hnsw above about 300 000 phrases.",
        example="--freq freq",
        columns=True,
    )
]
