"""The analysis area: with `weight`, each input item is «phrase [number]» and the call gets a table with the columns
«phrase» and the weight."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from ..case_files import Case, phrases

WEIGHTED_ITEM = re.compile(r"(.*) \[(-?[\d.]+)\]")
PHRASE = "phrase"


def arguments(case: Case) -> tuple[Any, dict[str, Any]]:
    kwargs = case.kwargs
    weight = kwargs.get("weight")
    if weight is None:
        return phrases(case), kwargs
    pairs = []
    for item in phrases(case):
        pair = WEIGHTED_ITEM.fullmatch(item)
        if pair is None:
            raise ValueError(f"{case.case_id}: with weight every input item is «phrase [number]», not {item!r}")
        pairs.append((pair[1], float(pair[2])))
    table = pd.DataFrame({PHRASE: [phrase for phrase, _ in pairs], weight: [number for _, number in pairs]})
    return table, {**kwargs, "column": PHRASE}
