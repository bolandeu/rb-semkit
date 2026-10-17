"""The steps that place phrases against a reference by meaning: the core, a search query report, the pages of the site.

Each adds columns and never drops a row; the Human decides by sorting and filtering on them. They take the encoder and
the threshold from the options of `steps.vectors`.
"""

from __future__ import annotations

import pandas as pd

from ..core.frame import Frame
from ..core.relevance.classify import classify_queries
from ..core.relevance.off_topic import off_topic
from ..core.relevance.pages import assign_pages, check_pages
from . import Adapted, Columns, Prepared, Step, first_text, option, table_of
from .vectors import MEANING, MODEL_DOC, by_meaning, encoder_of, frequencies

AGAINST_DOC = (
    "against: a file with the core, one phrase per row, in its first text column; the file is read like `read` does."
)
PAGES_DOC = (
    "pages: a file with the pages of the site; the file is read like `read` does. Its columns: url, and text (the"
    " text of the page: its title, H1 and body). A text longer than the input of the model is cut by the encoder."
)
FREQ_DOC = (
    "freq: the column of the frequencies of the phrases in the current table; the centre of the core weighs each"
    " phrase by it. Without it, every phrase weighs the same."
)
SEED_DOC = (
    "seed: the phrases whose centre is the topic, in place of the core: a list of your own as @FILE or @NAME, or"
    " comma-separated."
)


def _prepare_off_topic(options: dict) -> Prepared:
    found_encoder, threshold = by_meaning(options)

    def run(table: pd.DataFrame, column: str) -> Columns:
        freq = None if options["freq"] is None else frequencies(table, options["freq"])
        phrases = Frame(table, column).phrases
        return Columns(off_topic(phrases, encoder=found_encoder, threshold=threshold, freq=freq, seed=options["seed"]))

    return run


def _prepare_classify_queries(options: dict) -> Prepared:
    found_encoder, threshold = by_meaning(options)
    against = table_of(options["against"], "against")
    core = against[first_text(against, "against")]
    return lambda table, column: Columns(
        classify_queries(Frame(table, column).phrases, against=core, encoder=found_encoder, threshold=threshold)
    )


def _prepare_assign_pages(options: dict) -> Prepared:
    found_encoder = encoder_of(options)
    pages = table_of(options["pages"], "pages")
    check_pages(pages)
    return lambda table, column: Columns(assign_pages(Frame(table, column).phrases, pages=pages, encoder=found_encoder))


STEPS = [
    Step(
        "off-topic",
        Adapted(off_topic, {**MEANING, "freq": option("freq", str | None, None)}, MODEL_DOC, FREQ_DOC, SEED_DOC),
        "change",
        _prepare_off_topic,
        "The step adds the columns off_topic_score and off_topic right after the working column; the rows stay.",
        example="--freq freq",
        columns=True,
    ),
    Step(
        "classify-queries",
        Adapted(classify_queries, {**MEANING, "against": option("against")}, AGAINST_DOC, MODEL_DOC),
        "change",
        _prepare_classify_queries,
        "The step takes the working column as the queries of a search query report and adds the columns nearest_phrase,"
        " similarity and target right after it; the rows stay.",
        source="phrases.csv",
        example="--against core.csv",
        columns=True,
    ),
    Step(
        "assign-pages",
        Adapted(assign_pages, {**MEANING, "pages": option("pages"), "threshold": None}, PAGES_DOC, MODEL_DOC),
        "change",
        _prepare_assign_pages,
        "The step adds the columns best_page, best_similarity, second_page and second_similarity right after the working"
        " column; the rows stay.",
        example="--pages page_texts.csv",
        columns=True,
    ),
]
