"""A matcher of parts of the text, not of whole words: it marks character spans; the verbs follow from that."""

from __future__ import annotations

import pandas as pd

from ...frame import map_unique
from ..base import Matcher, collapse


class SpanMatcher(Matcher):
    """`spans(phrase)` gives the (start, stop) of each found part, in order and apart; the three verbs follow.

    find: any span. remove: the phrase without the spans. extract: the spans joined by a space.
    Both texts come out with single spaces and none at the edges.
    """

    def spans(self, phrase: str) -> list[tuple[int, int]]:
        raise NotImplementedError

    def find(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, lambda phrase: bool(self.spans(phrase))).astype(bool)

    def remove(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, self._without)

    def extract(self, phrases: pd.Series) -> pd.Series:
        return map_unique(phrases, self._found)

    def _without(self, phrase: str) -> str:
        kept, end = [], 0
        for start, stop in self.spans(phrase):
            kept.append(phrase[end:start])
            end = stop
        kept.append(phrase[end:])
        return collapse("".join(kept))

    def _found(self, phrase: str) -> str:
        return collapse(" ".join(phrase[start:stop] for start, stop in self.spans(phrase)))
