"""The steps that match texts by meaning and cut them into paragraphs: nearest and split-paragraphs.

nearest takes the encoder from the option --model of `steps.vectors`, and its own --threshold: without it no match is
left out. Both give a report that replaces the current table.
"""

from __future__ import annotations

from typing import Annotated

import pandas as pd

from ..core.compare.grams import URL
from ..core.errors import InvalidArguments
from ..core.frame import Frame
from ..core.nearest.matches import check_top, nearest
from ..core.nearest.paragraphs import heading_words, split_paragraphs
from ..core.relevance.page import TEXT
from ..core.vectors import registry
from . import POSITIONAL, REPEATED, Adapted, Prepared, Report, Step, option, table_of, texts_column
from .vectors import ENCODER_DOC, PAGE_NOTE, page_encoder_of

AGAINST_DOC = (
    "against: a file with the texts to match, one per row; the file is read like `read` does."
    " Give it or --to, not both."
)
TO_DOC = "to: a text to match; repeat it for each text, the nearest of them first. It stands for an against file of one column text."
AGAINST_COLUMN_DOC = (
    "against_column: the column of the texts in --against; by default the column text, else its first text column that is no url column."
)


def _against_table(options: dict) -> pd.DataFrame:
    """The table of the texts to match: the file --against, or the texts of --to as a table of one column text."""
    path, texts = options["against"], options["to"]
    if path is not None and texts:
        raise InvalidArguments("--to and AGAINST/--against: given together; allowed: one of them.")
    if path is None and not texts:
        raise InvalidArguments("AGAINST: not given; allowed: AGAINST, --against AGAINST or --to TEXT.")
    return table_of(path, "against") if texts is None else pd.DataFrame({TEXT: texts})


def _prepare_nearest(options: dict) -> Prepared:
    check_top(options["top"])  # the options are refused before the input is read
    if options["threshold"] is not None:
        registry.threshold(registry.model(options["model"]), options["threshold"])
    found_encoder = page_encoder_of(options)
    against = _against_table(options)
    against_column = options["against_column"] or texts_column(against, "against")
    Frame(against, against_column, argument="against_column")  # refuses a column it lacks or one not of text
    top, threshold = options["top"], options["threshold"]

    def run(table: pd.DataFrame, column: str) -> Report:
        found = nearest(
            table,
            column=column,
            against=against,
            against_column=against_column,
            encoder=found_encoder,
            top=top,
            threshold=threshold,
        )
        return Report(found)

    return run


def _prepare_split_paragraphs(options: dict) -> Prepared:
    def run(table: pd.DataFrame, column: str) -> Report:
        texts = texts_column(table, "column") if column == URL else column
        urls = table[URL] if URL in table.columns else None
        return Report(split_paragraphs(Frame(table, texts).phrases, urls=urls))

    return run


STEPS = [
    Step(
        "nearest",
        Adapted(
            nearest,
            {
                "encoder": None,
                "against": option("against", Annotated[str | None, POSITIONAL], None),
                "to": option("to", Annotated[list[str] | None, REPEATED], None),
                "against_column": option("against_column", str | None, None),
                "model": option("model", str, registry.default_name()),
            },
            AGAINST_DOC,
            TO_DOC,
            AGAINST_COLUMN_DOC,
            ENCODER_DOC,
        ),
        "report",
        _prepare_nearest,
        f"{PAGE_NOTE}\n\nThe step takes the working column as the texts to match; the report replaces the current table."
        " To match with a few texts, give them with --to instead of a file: `semkit read phrases.csv nearest --to"
        ' "растаможка авто" --threshold 0.85`.',
        example="--against page_texts.csv --top 2",
    ),
    Step(
        "split-paragraphs",
        split_paragraphs,
        "report",
        _prepare_split_paragraphs,
        f"A heading line has up to {heading_words()} words. The step takes a text file read with --whole, or a table of"
        " url and text: its working column as the texts (the first other text column when it is the url column) and"
        " its url column; the report replaces the current table.",
        source="--whole article.txt",
    ),
]
