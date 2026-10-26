"""The link sources of relate-phrases: what says that two units are linked, and why.

A source is a module of this package with a list `SOURCES`; `sources()` finds the modules, so a new source is one new
module and no edit here. A source declares the options it adds to the step and prepares its links from the options
and the folder of the project (`prepare`): it may refuse before the input is read, and it gives None when its options
leave it off. The prepared `Links` give the runs of words the source knows as one unit, whether two units are linked
and why, the units linked to a unit (to find the candidate phrases through an index), and other forms of a word that
the lookups of every source try too. A unit is the tuple of the lemmas of its words.
"""

from __future__ import annotations

import functools
import importlib
import pkgutil
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from ...word_vectors.thesaurus import Lemmas


@dataclass(frozen=True)
class SourceOption:
    """An option a source adds to the step: the name of its argument, its type and its line of the help."""

    name: str
    annotation: Any
    doc: str  # «name: text», as a line of a docstring on an argument


class Links:
    """What a prepared source knows; by default nothing, so a source gives only what it overrides."""

    longest = 1  # the most words of a run it knows

    def knows(self, run: Lemmas) -> bool:
        """Whether the run of words is one unit."""
        return False

    def link(self, unit: Lemmas, other: Lemmas) -> str | None:
        """The reason why the two units are linked («чехол~накидка (synset)»), or None."""
        return None

    def linked(self, unit: Lemmas) -> Iterable[Lemmas]:
        """The units linked to `unit`: those that `link` links with it."""
        return ()

    def forms(self, word: str) -> Iterable[str]:
        """Other forms of the lemma `word` that the lookups of every source try too."""
        return ()


class Source(Protocol):
    """A link source: its options, and `prepare`, which gives its links by the options of the step and the folder of
    the project, or None when the options leave it off."""

    options: tuple[SourceOption, ...]

    def prepare(self, options: Mapping[str, Any], project: Path) -> Links | None: ...


@functools.cache
def sources() -> tuple[Source, ...]:
    """The sources of every module of this package, by the name of the module."""
    found: list[Source] = []
    for module in sorted(info.name for info in pkgutil.iter_modules(__path__)):
        found += getattr(importlib.import_module(f"{__name__}.{module}"), "SOURCES", [])
    return tuple(found)
