"""The step that compares two lists of phrases."""

from __future__ import annotations

from ..core.lists.functions import compare_lists
from . import Adapted, Prepared, Report, Step, first_text, option, table_of

AGAINST_DOC = (
    "against: a file with the second list, one phrase per row; the file is read like `read` does."
    " The phrases are in --second-column, by default the first text column of the file."
)


def _prepare(options: dict) -> Prepared:
    second = table_of(options["against"], "against")
    second_column = options["second_column"] or first_text(second, "against")
    arguments = {name: value for name, value in options.items() if name not in {"against", "second_column"}}
    return lambda table, column: Report(
        compare_lists(table, second, column=column, second_column=second_column, **arguments).to_frame(column)
    )


STEPS = [
    Step(
        "compare-lists",
        Adapted(compare_lists, {"first": None, "second": option("against")}, AGAINST_DOC),
        "report",
        _prepare,
        "The step takes the working column as the first list; the phrases it finds replace the current table, in a"
        " column of the same name.",
        source="phrases.csv",
        example="--against second.csv",
    )
]
