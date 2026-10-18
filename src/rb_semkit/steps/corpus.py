"""The corpus steps: combinations, the hierarchy of phrases, the good / bad split, clusters, synonyms, typos, sentiment."""

from __future__ import annotations

from typing import Literal

import pandas as pd

from ..core.corpus.clustering import cluster_by_frequency
from ..core.corpus.combinations import linear_combinations, ordered_pairs, permutations
from ..core.corpus.hierarchy import basis_phrases, first_children, first_parents, nearest_parents
from ..core.corpus.sentiment import sentiment
from ..core.corpus.split import split_by_words
from ..core.corpus.synonyms import add_minus_words, synonyms
from ..core.corpus.typos import is_typo, typo_correction
from ..core.frame import Frame
from . import (
    CHANGE_NOTE,
    Adapted,
    Keep,
    Prepared,
    Report,
    Step,
    as_table,
    change_step,
    changing,
    option,
    scores_of,
    slug,
)

Part = Literal["good", "bad", "rest"]
KEEP_DOC = "keep: the part of the core to keep: the good phrases, the bad ones or the rest."
SYNONYMS_DOC = "synonyms: a file with the columns word and synonyms, as the step `synonyms` gives; the file is read like `read` does."
DICTIONARY_DOC = (
    "dictionary: a file of two columns, a word and its score; the first row is the header,"
    " the file is read like `read` does."
)
# The example of a step whose result grows fast: a real core gives millions of rows.
TABLE_NOTE = (
    "The step makes a table of its result; it replaces the current table, its first text column is the working one."
)


def _report(function) -> Step:
    def prepare(options: dict) -> Prepared:
        return lambda table, column: Report(function(Frame(table, column).phrases, **options).to_frame(column))

    return Step(slug(function), function, "report", prepare, TABLE_NOTE)


def _prepare_split(options: dict) -> Prepared:
    keep, arguments = options["keep"], {name: value for name, value in options.items() if name != "keep"}

    def run(table: pd.DataFrame, column: str) -> Keep:
        parts = split_by_words(Frame(table, column).phrases.reset_index(drop=True), **arguments)
        rows = pd.Series(False, index=table.index)
        rows.iloc[getattr(parts, keep).index] = True
        return Keep(rows)

    return run


def _prepare_pairs(options: dict) -> Prepared:
    return lambda table, column: Report(ordered_pairs(Frame(table, column).phrases, **options))


def _prepare_combinations(options: dict) -> Prepared:
    return lambda table, column: Report(linear_combinations(table, **options))


def _prepare_synonyms(options: dict) -> Prepared:
    return lambda table, column: Report(synonyms(table, **options))


SPLIT = Adapted(split_by_words, {"keep": option("keep", Part)}, KEEP_DOC)
STEPS = [
    Step(
        "linear-combinations",
        Adapted(linear_combinations, {"lists": None}),
        "report",
        _prepare_combinations,
        TABLE_NOTE,
    ),
    Step("ordered-pairs", ordered_pairs, "report", _prepare_pairs, TABLE_NOTE),
    _report(permutations),
    *(change_step(function, new_column="parent") for function in (first_parents, nearest_parents)),
    change_step(first_children, new_column="child"),
    change_step(basis_phrases, new_column="basis"),
    Step(
        "split-by-words",
        SPLIT,
        "filter",
        _prepare_split,
        "The step keeps only the rows of the part named by --keep.",
    ),
    change_step(cluster_by_frequency, new_column="cluster"),
    Step("synonyms", Adapted(synonyms, {"report": None}), "report", _prepare_synonyms, TABLE_NOTE),
    Step(
        "add-minus-words",
        Adapted(add_minus_words, {"table": option("synonyms")}, SYNONYMS_DOC),
        "change",
        changing(add_minus_words, table=("synonyms", as_table)),
        CHANGE_NOTE,
    ),
    change_step(is_typo, new_column="typo"),
    change_step(typo_correction),
    Step(
        "sentiment",
        Adapted(sentiment, {"scores": option("dictionary")}, DICTIONARY_DOC),
        "change",
        changing(sentiment, scores=("dictionary", scores_of)),
        "The step writes the scores to a new column <column>_sentiment.",
        "sentiment",
    ),
]
