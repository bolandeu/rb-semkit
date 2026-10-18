"""The conformance case files (`cases/<area>/<function>.tsv`): read a case, run it through `import rb_semkit as sk`, render.

A file is tab-separated, one case per row, with the columns of CASE_COLUMNS; lines that start with «#» are notes (the
VBA handler and lines the `vba` column is traced from). Its folder is the area of the function. `function` is a public
sk name, or «<matcher>.<verb>» for a matcher (`markers.extract` is `sk.extract(phrases, sk.markers(**call))`). `call`
holds the keyword arguments as JSON. `input` is one phrase, or several joined by « | » for a whole-column function; it
becomes a Series. An area whose functions take another input has a hook module `areas/<area>.py` with
`arguments(case) -> (data, kwargs)`: the first argument of the call and the keyword arguments; it may also have
`outcome(case, result)`, which picks the result to compare from the call's. `xfail` is empty, or the
reason the library does not give `expected` yet (reported to the Architect as a finding).

A result renders by its type as text: the items of a Series or a list joined by « | », a table as «first=last» per row
(an n-gram and its sum, or its count: the other columns, such as docs, are not in the add-in), a bool as TRUE / FALSE
(as Excel writes it), an empty value as "", a number (a single result too) as written, the parts of a tuple (a named
tuple) each by its type, joined by « || ». A per-row function given a table adds its column to it: that column is the
result.

A case that differs from the VBA quotes its rules from ADR 0005 or from its area's deviations document
(`docs/vba/deviations/<area>.md`).
"""

from __future__ import annotations

import csv
import importlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

import pandas as pd

import rb_semkit as sk

ROOT = Path(__file__).resolve().parents[2]
CASES_DIR = Path(__file__).resolve().parent / "cases"
HOOKS_DIR = Path(__file__).resolve().parent / "areas"
DEVIATIONS_DIR = ROOT / "docs" / "vba" / "deviations"
ADR_FILE = ROOT / "docs" / "adr" / "0005-port-vba-fix-defects.md"
CASE_COLUMNS = ("case_id", "function", "call", "input", "vba", "expected", "rule", "why", "xfail")
VERBS = ("find", "remove", "extract")
# A function that is not from the add-in has no conformance case: the report compares semkit with the add-in, and a case
# without a VBA column to compare would count as «the VBA». Such a function is tested in its own area tests.
NOT_CASED = {
    *VERBS,  # the verbs and the pipe run in the cases of every matcher
    "pipe",
    "split_text",
    "coverage",
    "cluster_serp",  # takes a SERP table and replaces the add-in's method (ADR 0005)
    "text_stats",
    "summary",
    "compare_grams",
    "compare_stats",
    "bm25",
    "compare_lists",
    "edges",
    "parse_html",
    "headings",
    "ad_groups",  # semkit's own, by vectors: no add-in function
    "word_list",  # semkit's own: the word lists, not a function of the add-in
    "agree",  # semkit's own: the add-in does not agree the words of a phrase
    "use_column",  # semkit's own: a brick of the pipeline over the whole table, no add-in function
    "sort_rows",  # semkit's own: a brick of the pipeline over the whole table, no add-in function
}
SEP = " | "
PART_SEP = " || "
RULE_SEP = "; "


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
    xfail: str
    area: str
    file: str

    @property
    def kwargs(self) -> dict[str, Any]:
        return json.loads(self.call) if self.call else {}


@dataclass(frozen=True)
class CaseFile:
    """The cases of one public function, with the notes of its file (the «#» lines, joined)."""

    area: str
    function: str
    notes: str
    cases: list[Case]


def read_case_file(path: Path) -> CaseFile:
    lines = path.read_text(encoding="utf-8").splitlines()
    notes = " ".join(line.removeprefix("#").strip() for line in lines if line.startswith("#"))
    table = [line for line in lines if not line.startswith("#")]
    rows = list(csv.reader(table, delimiter="\t", quoting=csv.QUOTE_NONE))
    if tuple(rows[0]) != CASE_COLUMNS:
        raise ValueError(f"{path.name}: the header is {rows[0]}, not {list(CASE_COLUMNS)}")
    area = path.parent.name
    cases = [Case(*row, area=area, file=f"{area}/{path.name}") for row in rows[1:]]
    return CaseFile(area, path.stem, notes, cases)


def case_files(cases_dir: Path = CASES_DIR) -> list[CaseFile]:
    """The case files of every area folder, by area, then by function."""
    return [read_case_file(path) for path in sorted(cases_dir.glob("*/*.tsv"))]


def all_cases(cases_dir: Path = CASES_DIR) -> list[Case]:
    return [case for case_file in case_files(cases_dir) for case in case_file.cases]


def unquoted_rules(case: Case, deviations_dir: Path = DEVIATIONS_DIR) -> list[str]:
    """The rules of the case found neither in ADR 0005 nor in its area's deviations document."""
    deviations = deviations_dir / f"{case.area}.md"
    sources = ADR_FILE.read_text(encoding="utf-8")
    if deviations.is_file():
        sources += deviations.read_text(encoding="utf-8")
    return [rule for rule in case.rule.split(RULE_SEP) if not rule or rule not in sources]


def render_value(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)) or value is pd.NA:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def render(result: Any) -> str:
    if isinstance(result, tuple):
        return PART_SEP.join(render(part) for part in result)
    if isinstance(result, str | int | float):
        return render_value(result)
    if isinstance(result, pd.DataFrame):
        value = next((name for name in ("sum", "count") if name in result.columns), result.columns[-1])
        return SEP.join(f"{row.iloc[0]}={render_value(row[value])}" for _, row in result.iterrows())
    values = result.tolist() if isinstance(result, pd.Series) else list(result)
    return SEP.join(render_value(value) for value in values)


def phrases(case: Case) -> pd.Series:
    """The input of the case as a column of phrases."""
    return pd.Series(case.input.split(SEP), dtype=object)


def _hook(area: str) -> ModuleType | None:
    if not (HOOKS_DIR / f"{area}.py").is_file():
        return None
    return importlib.import_module(f"{__package__}.areas.{area}")


def arguments(case: Case) -> tuple[Any, dict[str, Any]]:
    """The first argument of the call and its keyword arguments: the area's hook gives them, else phrases and `call`."""
    hook = _hook(case.area)
    return hook.arguments(case) if hook is not None else (phrases(case), case.kwargs)


def run(case: Case) -> Any:
    """The result of the case's call through the public API."""
    data, kwargs = arguments(case)
    before = set(data.columns) if isinstance(data, pd.DataFrame) else None
    name, _, verb = case.function.partition(".")
    function = getattr(sk, name)
    result = getattr(sk, verb)(data, function(**kwargs)) if verb else function(data, **kwargs)
    hook = _hook(case.area)
    if hook is not None and hasattr(hook, "outcome"):
        return hook.outcome(case, result)
    if before is not None and isinstance(result, pd.DataFrame) and before < set(result.columns):
        (added,) = [column for column in result.columns if column not in before]
        return result[added]
    return result
