"""The step relate-phrases: the class of each phrase at the other phrases of the table, by lemmas and the link sources.

Each link source declares its options, and the step takes them as its own; the step prepares the sources from them
before the input is read.
"""

from __future__ import annotations

import pandas as pd

from ..core.frame import Frame
from ..core.relate import relate_phrases
from ..core.relate.sources import sources
from . import Adapted, Columns, Prepared, Step, option, prepared_for

SOURCE_OPTIONS = [found for source in sources() for found in source.options]


def _prepare(options: dict) -> Prepared:
    start = prepared_for()
    links = [found for source in sources() if (found := source.prepare(options, start)) is not None]
    to, keep = options["to"], options["keep"]
    relate_phrases(pd.Series([], dtype=object), to=to, keep=keep, links=links)

    def run(table: pd.DataFrame, column: str) -> Columns:
        return Columns(relate_phrases(Frame(table, column).phrases, to=to, keep=keep, links=links))

    return run


STEPS = [
    Step(
        "relate-phrases",
        Adapted(
            relate_phrases,
            {"links": None, **{found.name: option(found.name, found.annotation, None) for found in SOURCE_OPTIONS}},
            *(found.doc for found in SOURCE_OPTIONS),
        ),
        "change",
        _prepare,
        "The step adds the columns class, of, group and reason right after the working column; the rows stay. The"
        " caller gives the phrases in its order (by frequency): the first phrase of a group is the one kept.",
        columns=True,
    )
]
