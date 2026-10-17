"""The ad groups step: small groups of one intent by the rule of `dupes --kind meaning` (the vectors extra)."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from ..core.adgroups import ad_groups
from ..core.frame import Frame
from . import Adapted, Columns, Prepared, Step, option
from .dupes import HOME_DOC, NEUTRAL_DOC, SYNONYMS_DOC, THRESHOLD_DOC, refining_options
from .vectors import MEANING, MODEL_DOC, by_meaning, frequencies_of

MAX_SIZE_DOC = (
    "max_size: the most phrases in an ad group, 1 or more; a larger group is split by vector. Without it no group is"
    " split."
)
FREQ_DOC = (
    "freq: the column of the frequencies of the phrases in the current table; the ad group is named after its most"
    " frequent phrase. Without it, after its first phrase."
)


def _prepare(options: dict) -> Prepared:
    found_encoder, threshold = by_meaning(options)
    neutral, synonyms = refining_options(options)

    def run(table: pd.DataFrame, column: str) -> Columns:
        freq = None if options["freq"] is None else frequencies_of(table, options["freq"])
        found = ad_groups(
            Frame(table, column).phrases,
            encoder=found_encoder,
            threshold=threshold,
            max_size=options["max_size"],
            freq=freq,
            neutral=neutral,
            synonyms=synonyms,
            home=options["home"],
        )
        return Columns(found)

    return run


STEPS = [
    Step(
        "ad-groups",
        Adapted(
            ad_groups,
            {
                **MEANING,
                "max_size": option("max_size", int | None, None),
                "freq": option("freq", str | None, None),
                "neutral": option("neutral", Iterable[str] | None, None),
                "synonyms": option("synonyms", str | None, None),
                "home": option("home", str | None, None),
            },
            MAX_SIZE_DOC,
            FREQ_DOC,
            NEUTRAL_DOC,
            SYNONYMS_DOC,
            HOME_DOC,
            THRESHOLD_DOC,
            MODEL_DOC,
        ),
        "change",
        _prepare,
        "The step adds the columns ad_group and ad_group_name right after the working column; the rows stay.",
        example="--max-size 20 --freq freq",
        columns=True,
    )
]
