"""The dupes area: `against` (a list in the call) is the other column, a Series."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..case_files import Case, phrases


def arguments(case: Case) -> tuple[Any, dict[str, Any]]:
    kwargs = case.kwargs
    if "against" in kwargs:
        kwargs["against"] = pd.Series(kwargs["against"], dtype=object)
    return phrases(case), kwargs
