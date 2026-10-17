"""The corpus area: the functions whose first argument is no column of phrases, and the tables in a call.

- levenshtein: the input is «first | second»;
- linear_combinations: each input item is one list, its values joined by «, »;
- cluster_by_serp: each input item is «phrase: url url …», the urls in position order from 1;
- synonyms: each input item is a report row «phrase / condition / matched»;
- add_minus_words: `table` in the call is {word: synonyms}, the table word, synonyms;
- is_typo, typo_correction: `provider` in the call holds the arguments of sk.CoreSpelling.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

import rb_semkit as sk

from ..case_files import SEP, Case, phrases

LIST_SEP = ", "
SERP_SEP = ": "
REPORT_SEP = " / "


def _lists(case: Case) -> pd.DataFrame:
    lists = {f"list{number}": item.split(LIST_SEP) for number, item in enumerate(case.input.split(SEP), start=1)}
    return pd.DataFrame({name: pd.Series(values, dtype=object) for name, values in lists.items()})


def _serp(case: Case) -> pd.DataFrame:
    rows = []
    for item in case.input.split(SEP):
        phrase, _, urls = item.partition(SERP_SEP)
        rows += [(phrase, position, url) for position, url in enumerate(urls.split(), start=1)]
    return pd.DataFrame(rows, columns=["phrase", "position", "url"])


def _report(case: Case) -> pd.DataFrame:
    return pd.DataFrame(
        [item.split(REPORT_SEP) for item in case.input.split(SEP)], columns=["phrase", "condition", "matched"]
    )


INPUTS: dict[str, Callable[[Case], Any]] = {
    "linear_combinations": _lists,
    "cluster_by_serp": _serp,
    "synonyms": _report,
}


def arguments(case: Case) -> tuple[Any, dict[str, Any]]:
    kwargs = case.kwargs
    if case.function == "levenshtein":
        first, second = case.input.split(SEP)
        return first, {"second": second}
    if "table" in kwargs:
        kwargs["table"] = pd.DataFrame(list(kwargs["table"].items()), columns=["word", "synonyms"])
    if "provider" in kwargs:
        kwargs["provider"] = sk.CoreSpelling(**kwargs["provider"])
    return INPUTS.get(case.function, phrases)(case), kwargs
