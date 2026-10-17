"""The marker steps: each verb of the marker matcher, and the keep and drop filters (ADR 0004).

--lists names the lists: a bundled marker list by its name (geo) or as the word list @markers/geo, and a list of the
Human's own as @FILE or @NAME, each a list of phrases.
"""

from __future__ import annotations

from typing import Any

from ..core.errors import InvalidArguments
from ..core.markers.lists import names
from ..core.markers.matcher import markers
from ..pipeline.items import items
from . import Adapted, option, prepared_for
from .text import matcher_steps

BUNDLED_PREFIX = "markers/"
LISTS_DOC = (
    "lists: the marker lists, comma-separated: a bundled one by its name (geo) or as @markers/geo, or a list of your"
    " own as @FILE (one phrase per line, or the first column of a table) or @NAME of a word list."
)


def _bundled_name(entry: str) -> str | None:
    """The bundled marker list an entry names: «geo» or «@markers/geo»; None for any other entry."""
    name = entry.removeprefix("@").removeprefix(BUNDLED_PREFIX) if entry.startswith(f"@{BUNDLED_PREFIX}") else entry
    return name if name in names() else None


def marker_lists(value: str) -> tuple[list[str], dict[str, list[str]]]:
    """The bundled lists and the Human's own lists (by the entry that names them) of the option --lists."""
    bundled, own = [], {}
    for entry in (part.strip() for part in value.split(",")):
        if not entry:
            continue
        if (name := _bundled_name(entry)) is not None:
            bundled.append(name)
        elif entry.startswith("@"):
            own[entry] = items(entry, prepared_for())
        else:
            raise InvalidArguments(
                f"--lists: {entry} is no bundled marker list.",
                action=f"Name one of {', '.join(names())}, or a list of your own as @FILE or @NAME.",
            )
    return bundled, own


class Lists(Adapted):
    """The marker matcher with one option --lists for the bundled lists and the Human's own."""

    def __init__(self) -> None:
        super().__init__(markers, {"lists": option("lists", str), "user": None}, LISTS_DOC)

    def __call__(self, *args: Any, lists: str, **kwargs: Any) -> Any:
        bundled, own = marker_lists(lists)
        return self.__wrapped__(*args, lists=bundled, user=own, **kwargs)


STEPS = matcher_steps(Lists(), "--lists geo")
