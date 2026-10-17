"""The textstats area: each case is one text in a table; `metric` in the call names the column that is the result."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..case_files import Case, phrases

TEXT = "text"


def arguments(case: Case) -> tuple[Any, dict[str, Any]]:
    return pd.DataFrame({TEXT: phrases(case)}), {"column": TEXT}


def outcome(case: Case, result: pd.DataFrame) -> pd.Series:
    return result[case.kwargs["metric"]]
