"""The coverage step: which phrases of the core stand in the texts."""

from __future__ import annotations

from ..core.coverage.report import coverage
from . import Adapted, Prepared, Report, Step, first_text, option, table_of

AGAINST_DOC = (
    "against: a file with the texts, one per row; the file is read like `read` does."
    " The texts are in --text-column, by default the first text column of the file."
)


def _prepare(options: dict) -> Prepared:
    texts = table_of(options["against"], "against")
    text_column = options["text_column"] or first_text(texts, "against")
    arguments = {name: value for name, value in options.items() if name not in {"against", "text_column"}}
    return lambda table, column: Report(coverage(table, texts, column=column, text_column=text_column, **arguments))


STEPS = [
    Step(
        "coverage",
        Adapted(coverage, {"core": None, "texts": option("against")}, AGAINST_DOC),
        "report",
        _prepare,
        "The step takes the working column as the core; the table phrase, count, docs, density and first replaces"
        " the current one.",
    )
]
