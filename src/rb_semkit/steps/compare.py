"""The steps that compare my text with the texts of the competitors."""

from __future__ import annotations

from types import FunctionType

import pandas as pd

from ..core.compare.bm25 import bm25
from ..core.compare.grams import compare_grams
from ..core.compare.stats import compare_stats
from ..core.frame import Frame
from . import Adapted, Change, Prepared, Report, Step, joined, option, slug, table_of, texts_of

COMPETITORS_DOC = (
    "competitors: a file with the texts of the competitors, one per row, in its first text column;"
    " the file is read like `read` does."
)
NOTE = (
    "The step takes the working column as my text (its cells, one per line); the table of the comparison replaces the"
    " current one."
)


def _comparison(function: FunctionType) -> Step:
    def prepare(options: dict) -> Prepared:
        competitors = texts_of(table_of(options["competitors"], "competitors"), "competitors")
        arguments = {name: value for name, value in options.items() if name != "competitors"}
        return lambda table, column: Report(function(joined(table, column), competitors, **arguments))

    adapted = Adapted(function, {"mine": None, "competitors": option("competitors")}, COMPETITORS_DOC)
    return Step(slug(function), adapted, "report", prepare, NOTE)


def _prepare_bm25(options: dict) -> Prepared:
    bm25(pd.Series(["text"]), **options)  # the options are checked as the function checks them, on one text
    return lambda table, column: Change(bm25(Frame(table, column).phrases, **options))


BM25 = Step(
    "bm25",
    Adapted(bm25, {"texts": None}),
    "change",
    _prepare_bm25,
    "The step takes each cell of the working column as a text and writes its score for the query to a new column"
    " <column>_bm25; to rank my text among the competitors, put all the texts in the working column.",
    "bm25",
)
STEPS = [_comparison(compare_grams), _comparison(compare_stats), BM25]
