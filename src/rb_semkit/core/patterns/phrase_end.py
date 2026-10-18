"""The words at the end of a phrase: prepositions and function words, or buy markers; remove only."""

from __future__ import annotations

from typing import Literal, get_args

import pandas as pd

from ..frame import map_unique
from ..markers.lists import bundled
from ..text.base import Matcher, bundled_list, choice, split_words, word_key

__all__ = ["phrase_end"]

Kind = Literal["prepositions", "buy_markers"]
KINDS = get_args(Kind)
BUY_MARKERS = "sale"  # the bundled marker list of buy and sale words


class PhraseEnd(Matcher):
    def __init__(self, kind: str) -> None:
        if choice("kind", kind, KINDS) == "prepositions":
            self._keys = frozenset(word_key(word) for word in bundled_list("stopwords") + bundled_list("prepositions"))
            self._trailing = self._function_words
        else:
            self._prepositions = frozenset(word_key(word) for word in bundled_list("prepositions"))
            self._trailing = self._buy_markers

    def _function_words(self, words: list[str]) -> int:
        """How many words at the end are stopwords or prepositions."""
        count = 0
        while count < len(words) and word_key(words[-1 - count]) in self._keys:
            count += 1
        return count

    def _buy_markers(self, words: list[str]) -> int:
        """How many words at the end are buy markers, a marker of several words taken whole; a marker right after a
        preposition stays with it («с доставкой»)."""
        markers = bundled(BUY_MARKERS)
        count = 0
        while ends := [hit for hit in markers.hits(words[: len(words) - count]) if hit.stop == len(words) - count]:
            start = min(hit.start for hit in ends)
            if start > 0 and word_key(words[start - 1]) in self._prepositions:
                break
            count = len(words) - start
        return count

    def remove(self, phrases: pd.Series) -> pd.Series:
        def cut(phrase: str) -> str:
            words = split_words(phrase)
            return " ".join(words[: len(words) - self._trailing(words)])

        return map_unique(phrases, cut)


def phrase_end(kind: Kind) -> PhraseEnd:
    """The words at the end of a phrase, cut until the last word is clean; remove only.

    kind: "prepositions" (prepositions and the other function words of the stopword list: «диван в и» → «диван»)
    or "buy_markers" (the words of the bundled list «sale», whole phrases of it too: «диван купить недорого» →
    «диван»; a marker right after a preposition stays: «диван с доставкой купить» → «диван с доставкой»). Words compare
    in any case, ё as е, as written («для,» with its comma stays). A phrase of such words only becomes an empty cell.

    Example: {cli} read --text "диван в и" remove-phrase-end prepositions write -
    -> диван
    Example: {cli} read --text "диван купить недорого" --text "диван с доставкой купить" remove-phrase-end buy_markers write -
    -> диван; диван с доставкой
    """
    return PhraseEnd(kind)
