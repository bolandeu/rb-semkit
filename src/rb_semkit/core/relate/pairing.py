"""The one-to-one pairing of the units of a phrase with the units of a base: equal units first, then linked ones.

A phrase may have several cuts into units (runs that overlap); `best_pairing` pairs every cut of a phrase with every
cut of its base and keeps the `Pairing` that explains the most words.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import NamedTuple

from ..word_vectors.thesaurus import Lemmas
from ..word_vectors.units import Unit

Link = Callable[[Lemmas, Lemmas], str | None]
Cut = tuple[Unit, ...]


class Pairing(NamedTuple):
    """A cut of a phrase, a cut of its base and the pairs of their units (the place in `base` → the place in `units`)."""

    units: Cut
    base: Cut
    pairs: dict[int, int]

    def words(self) -> int:
        """How many words the pairs explain, on both sides."""
        return sum(len(self.units[unit].lemmas) + len(self.base[other].lemmas) for other, unit in self.pairs.items())


def best_pairing(cuts: Sequence[Cut], base: Sequence[Cut], link: Link) -> Pairing:
    """Of every cut of a phrase with every cut of its base, the pairing that explains the most words; the first cuts
    on a tie."""
    pairings = (Pairing(units, other, pair(units, other, link)) for units in cuts for other in base)
    return max(pairings, key=Pairing.words)


def pair(units: Sequence[Unit], base: Sequence[Unit], link: Link) -> dict[int, int]:
    """The most units of `base` paired one to one with units of `units`, each with an equal unit or a linked one.

    Maps the place of a unit of `base` to the place of its unit of `units`; an equal unit is tried before a linked one.
    """
    edges = [_edges(units, other, link) for other in base]
    owner: dict[int, int] = {}  # the place of a unit of `units` → the place of its unit of `base`

    def augment(other: int, seen: set[int]) -> bool:
        for unit in edges[other]:
            if unit not in seen:
                seen.add(unit)
                if unit not in owner or augment(owner[unit], seen):
                    owner[unit] = other
                    return True
        return False

    for other in range(len(base)):
        augment(other, set())
    return {other: unit for unit, other in owner.items()}


def _edges(units: Sequence[Unit], other: Unit, link: Link) -> list[int]:
    equal = [place for place, unit in enumerate(units) if unit.lemmas == other.lemmas]
    linked = [place for place, unit in enumerate(units) if place not in equal and link(unit.lemmas, other.lemmas)]
    return equal + linked
