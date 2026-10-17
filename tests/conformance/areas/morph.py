"""The morph area: wordforms takes one word, not a column of phrases."""

from __future__ import annotations

from typing import Any

from ..case_files import Case, phrases


def arguments(case: Case) -> tuple[Any, dict[str, Any]]:
    return (case.input if case.function == "wordforms" else phrases(case)), case.kwargs
