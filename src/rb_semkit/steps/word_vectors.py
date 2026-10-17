"""The steps by words: candidates from a thesaurus and word vectors (the vectors extra and the word data pulled once).

--source names the data the step opens; it refuses before the input is read, and downloads nothing.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..core.frame import Frame
from ..core.word_vectors.candidates import Source, synonym_candidates
from ..core.word_vectors.navec import open_word_vectors
from ..core.word_vectors.thesaurus import open_thesaurus
from . import Adapted, Prepared, Report, Step, option

SOURCE_DOC = (
    "source: the data to take candidates from, pulled once with `semkit models pull NAME`: ruwordnet (the thesaurus),"
    " navec (the word vectors) or both."
)


def _prepare(options: dict) -> Prepared:
    source, start = options["source"], Path.cwd()
    given = {name: value for name, value in options.items() if name != "source"}
    given["thesaurus"] = open_thesaurus(start) if source in ("ruwordnet", "both") else None
    given["word_vectors"] = open_word_vectors(start) if source in ("navec", "both") else None

    def run(table: pd.DataFrame, column: str) -> Report:
        return Report(synonym_candidates(Frame(table, column).phrases, **given))

    return run


STEPS = [
    Step(
        "synonym-candidates",
        Adapted(
            synonym_candidates,
            {"thesaurus": None, "word_vectors": None, "source": option("source", Source, "both")},
            SOURCE_DOC,
        ),
        "report",
        _prepare,
        "The step makes a table of its result; it replaces the current table, its first text column is the working one."
        " Its candidates are for the Human to pick; the picked go to --synonyms of the steps that take them.",
    )
]
