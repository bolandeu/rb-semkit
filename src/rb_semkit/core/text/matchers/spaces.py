"""Spaces: all, at the left, at the right, at both ends, or the extra ones (runs collapsed to one)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal, get_args

import pandas as pd

from ...frame import map_unique
from ..base import Matcher, choice, collapse

__all__ = ["spaces"]

SpaceKind = Literal["all", "left", "right", "both", "extra"]
CLEANERS: dict[SpaceKind, Callable[[str], str]] = {
    "all": lambda text: "".join(text.split()),
    "left": str.lstrip,
    "right": str.rstrip,
    "both": str.strip,
    "extra": collapse,
}


class Spaces(Matcher):
    def __init__(self, kind: SpaceKind) -> None:
        self._clean = CLEANERS[choice("kind", kind, get_args(SpaceKind))]

    def remove(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, self._clean)


def spaces(kind: SpaceKind) -> Spaces:
    """The spaces to remove (remove only).

    kind: "all"; "left" and "right" (at that end only); "both" (at both ends); "extra" (runs collapsed to one
    space, none at the ends). "left", "right" and "both" keep the spaces inside.

    Example: {cli} read --text "  купить   диван " remove-spaces extra write -
    -> купить диван

    ADR 0005: whitespace of any kind (tab, nbsp, line break) counts as a space.
    """
    return Spaces(kind)
