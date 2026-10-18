"""The coverage-meaning step: which phrases of the core a text covers by meaning.

--text is a text file (.txt), cut into paragraphs, or a table of url and text; the paragraphs are those of
split-paragraphs.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..core.compare.grams import URL
from ..core.coverage_meaning.report import coverage_meaning
from ..core.errors import InvalidArguments
from ..core.frame import Frame
from ..core.nearest.paragraphs import split_paragraphs
from ..core.vectors import registry
from ..pipeline.tables import Source
from . import Adapted, Columns, Prepared, Step, flag, option, table_of, texts_column
from .vectors import MEANING, MODEL_DOC, page_encoder_of

TEXT_DOC = (
    "text: a text file (.txt), or a table of url and text, that is cut into paragraphs like `split-paragraphs` does;"
    " the table file is read like `read` does."
)
CLUSTER_DOC = (
    "cluster: the column of the clusters of the phrases in the current table (as `cluster-meaning` gives it); every"
    " phrase also gets cluster_covered, yes when any phrase of its cluster is covered."
)


def _paragraphs_of(path: str) -> pd.DataFrame:
    """The paragraphs of the file the option --text names."""
    if Path(path).suffix.lower() != ".txt":
        texts = table_of(path, "text")
        column = texts_column(texts, "text")
        urls = texts[URL] if URL in texts.columns else None
        return split_paragraphs(Frame(texts, column).phrases, urls=urls)
    table_of(path, "text")  # refuses a file that does not exist
    return split_paragraphs(Source(path, whole=True).read().iloc[:, 0])


def _clusters_of(table: pd.DataFrame, name: str | None) -> pd.Series | None:
    if name is None:
        return None
    if name not in table.columns:
        raise InvalidArguments(
            f"{flag('cluster')} {name}: the table has no such column.",
            action=f"Name one of its columns: {', '.join(map(str, table.columns))}.",
        )
    return table[name]


def _prepare(options: dict) -> Prepared:
    threshold = registry.threshold(registry.encoder(options["model"]), options["threshold"])
    found_encoder = page_encoder_of(options)
    paragraphs = _paragraphs_of(options["text"])

    def run(table: pd.DataFrame, column: str) -> Columns:
        clusters = _clusters_of(table, options["cluster"])
        found = coverage_meaning(
            Frame(table, column).phrases, paragraphs, encoder=found_encoder, threshold=threshold, clusters=clusters
        )
        return Columns(found)

    return run


STEPS = [
    Step(
        "coverage-meaning",
        Adapted(
            coverage_meaning,
            {
                "phrases": None,
                "paragraphs": option("text"),
                "encoder": None,
                "threshold": MEANING["threshold"],
                "model": MEANING["model"],
                "clusters": None,
                "cluster": option("cluster", str | None, None),
            },
            TEXT_DOC,
            CLUSTER_DOC,
            MODEL_DOC,
        ),
        "change",
        _prepare,
        "The step takes the working column as the core and adds the columns url, number, paragraph, similarity and"
        " covered (and cluster_covered) right after it; the rows stay.",
        example="--text article.txt",
        columns=True,
    )
]
