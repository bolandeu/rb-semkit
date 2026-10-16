"""Spaces: all, at the left, at the right, at both ends, or the extra ones (runs collapsed to one)."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from ...frame import map_unique
from ..base import Matcher, choice, collapse

CLEANERS: dict[str, Callable[[str], str]] = {
    "all": lambda text: "".join(text.split()),
    "left": str.lstrip,
    "right": str.rstrip,
    "both": str.strip,
    "extra": collapse,
}


class Spaces(Matcher):
    def __init__(self, kind: str) -> None:
        self._clean = CLEANERS[choice("kind", kind, tuple(CLEANERS))]

    def remove(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, self._clean)


def spaces(kind: str) -> Spaces:
    """The spaces to remove (remove only).

    kind: "all"; "left" and "right" (at that end only); "both" (at both ends); "extra" (runs collapsed to one
    space, none at the ends). "left", "right" and "both" keep the spaces inside.

    VBA (RibbonCallbacks.vba):
        remove: `–aal` (line 1941) extra («Лишние пробелы > Все»), `—ako` (line 2926) left, `a–o—` (line 2230) right,
        `a–k—` (line 1878) both; all: no VBA handler: derived from `–aal` (line 1941), every space cut.
    ADR 0005: whitespace of any kind (tab, nbsp, line break) counts as a space.
    """
    return Spaces(kind)
