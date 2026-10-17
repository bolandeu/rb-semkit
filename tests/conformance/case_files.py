"""The conformance case files (`cases/<function>.tsv`): read a case, run it through `import rb_semkit as sk`, render.

A file is tab-separated, one case per row, with the columns of CASE_COLUMNS; lines that start with «#» are notes (the
VBA handler and lines the `vba` column is traced from). `function` is a public sk name, or «<matcher>.<verb>» for a
matcher (`markers.extract` is `sk.extract(phrases, sk.markers(**call))`). `call` holds the keyword arguments as JSON:
`against` (a list) becomes a Series; with `weight`, each input item is «phrase [number]» and the call gets a table
with the columns «phrase» and the weight. `input` is one phrase, or several joined by « | » for a whole-column
function; `wordforms` gets it as one word.

A result renders as text: the items of a Series or a list joined by « | », a bool as TRUE / FALSE (as Excel writes
it), an empty value as "", a number as written; an n-gram table as «ngram=value» per row, the value being the sum
with a weight and the count without one.
"""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

import rb_semkit as sk

CASES_DIR = Path(__file__).resolve().parent / "cases"
CASE_COLUMNS = ("case_id", "function", "call", "input", "vba", "expected", "rule", "why")
SEP = " | "
WEIGHTED_ITEM = re.compile(r"(.*) \[(-?[\d.]+)\]")
PHRASE = "phrase"
WORD_FUNCTIONS = frozenset({"wordforms"})


@dataclass(frozen=True)
class Case:
    case_id: str
    function: str
    call: str
    input: str
    vba: str
    expected: str
    rule: str
    why: str
    file: str

    @property
    def kwargs(self) -> dict[str, Any]:
        return json.loads(self.call) if self.call else {}


def read_cases(path: Path) -> list[Case]:
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if not line.startswith("#")]
    rows = list(csv.reader(lines, delimiter="\t", quoting=csv.QUOTE_NONE))
    if tuple(rows[0]) != CASE_COLUMNS:
        raise ValueError(f"{path.name}: the header is {rows[0]}, not {list(CASE_COLUMNS)}")
    return [Case(*row, file=path.name) for row in rows[1:]]


def all_cases() -> list[Case]:
    return [case for path in sorted(CASES_DIR.glob("*.tsv")) for case in read_cases(path)]


def render_value(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)) or value is pd.NA:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def render(result: Any) -> str:
    if isinstance(result, pd.DataFrame) and "ngram" in result.columns:
        return SEP.join(f"{row.iloc[0]}={render_value(row.iloc[-1])}" for _, row in result.iterrows())
    values = result.tolist() if isinstance(result, pd.Series) else list(result)
    return SEP.join(render_value(value) for value in values)


def _data(case: Case, kwargs: dict[str, Any]) -> pd.Series | pd.DataFrame:
    items = case.input.split(SEP)
    weight = kwargs.get("weight")
    if weight is None:
        return pd.Series(items, dtype=object)
    pairs = []
    for item in items:
        pair = WEIGHTED_ITEM.fullmatch(item)
        if pair is None:
            raise ValueError(f"{case.case_id}: with weight every input item is «phrase [number]», not {item!r}")
        pairs.append((pair[1], float(pair[2])))
    kwargs["column"] = PHRASE
    return pd.DataFrame({PHRASE: [phrase for phrase, _ in pairs], weight: [number for _, number in pairs]})


def _new_column(result: pd.DataFrame, before: list[str]) -> pd.Series:
    """The column a per-row function added to the table (it adds it to the table it was given)."""
    (added,) = [name for name in result.columns if name not in before]
    return result[added]


def run(case: Case) -> Any:
    """The result of the case's call through the public API."""
    kwargs = case.kwargs
    name, _, verb = case.function.partition(".")
    function = getattr(sk, name)
    if name in WORD_FUNCTIONS:
        return function(case.input, **kwargs)
    if "against" in kwargs:
        kwargs["against"] = pd.Series(kwargs["against"], dtype=object)
    data = _data(case, kwargs)
    before = list(data.columns) if isinstance(data, pd.DataFrame) else []
    result = getattr(sk, verb)(data, function(**kwargs)) if verb else function(data, **kwargs)
    if isinstance(result, pd.DataFrame) and before and "ngram" not in result.columns:
        return _new_column(result, before)
    return result
