"""relate_phrases: the class of each phrase of a topic at the other phrases, the phrase it belongs to and its group."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Collection, Iterable, Sequence
from typing import NamedTuple

import pandas as pd

from .. import wordlists
from ..errors import InvalidArguments
from ..morph import Lemmatizer
from ..morph.functions import BUNDLED
from ..word_vectors.thesaurus import Lemmas
from ..word_vectors.units import Unit
from .pairing import Pairing, best_pairing
from .phrases import Phrase, Reader
from .sources import Links

QUESTIONS = "meaning/question"  # the bundled list of the question words, which a phrase keeps
COLUMNS = ["class", "of", "group", "reason"]
SAME, VARIATION, REFINEMENT, OTHER = "same", "variation", "refinement", "other"
RANKS = {SAME: 0, VARIATION: 1, REFINEMENT: 2}  # the better relation first
LEMMAS = "lemmas"  # the reason of a same phrase
TO_ROW = -1  # the row of the phrase of --to: before every row of the table


class Relation(NamedTuple):
    kind: str
    base: Phrase
    reason: str

    def rank(self) -> tuple[int, int, int]:
        """Lower is better: the class, then for a refinement the closest base (the most units), then the earliest row."""
        closest = -len(self.base.units) if self.kind == REFINEMENT else 0
        return RANKS[self.kind], closest, self.base.row


def relate_phrases(
    data: pd.Series,
    *,
    to: str | None = None,
    keep: Iterable[str] | None = None,
    links: Sequence[Links] = (),
    lemmatizer: Lemmatizer = BUNDLED,
) -> pd.DataFrame:
    """The class of each phrase at the other phrases of the table, the phrase it belongs to, its group and the reason.

    A phrase is its words as lemmas; a preposition, a conjunction or a particle is dropped, except the question words
    (the bundled list @meaning/question) and the words to keep. A word with digits stays as it is. A unit is a word,
    or a run of words that a link source knows as one; two units are linked when a link source links them. The class:
    same (the same lemmas in any order, at an earlier row), variation (every unit pairs one to one with a unit of an
    earlier row, equal or linked, at least one pair linked), refinement (every unit of another phrase, of any row,
    pairs with a unit of this one, and this one has units left over) or other. A phrase takes the best relation:
    same, then variation, then refinement; for a refinement the closest base (the most units), then the earliest row.
    The columns: class; of (the phrase it is same, a variation or a refinement of; empty for other); group (the first
    row among the phrases whose chains of `of` end in the same phrase); reason (lemmas; the links of the units; +word
    for each unit left over; for other the phrases that are its refinements, «base of: …», or the units unlinked to
    the nearest phrase, «unlinked: …»). An empty cell is other, with an empty group.
    to: compare every phrase only with this one; of is this phrase or empty.
    keep: more words a phrase never drops, as the question words.
    links: the link sources, prepared.
    lemmatizer: what gives the lemmas and the parts of speech.

    Example: {cli} read --text "разработка сайтов" --text "сайт разработка" --text "разработка сайтов под ключ" relate-phrases write -
    -> разработка сайтов, other, , разработка сайтов, base of: сайт разработка | разработка сайтов под ключ; сайт разработка, same, разработка сайтов, разработка сайтов, lemmas; разработка сайтов под ключ, refinement, разработка сайтов, разработка сайтов, +ключ
    Example: {cli} read --text "угловой диван" --text "кресло" relate-phrases --to "диван" write -
    -> угловой диван, refinement, диван, угловой диван, +угловой; кресло, other, , кресло, unlinked: кресло | диван
    """
    reader = Reader(links, [*wordlists.resolve(QUESTIONS), *(keep or [])], lemmatizer)
    texts = data.fillna("").astype(str).tolist()
    reader.learn([*texts, *([] if to is None else [to])])
    phrases = [reader.phrase(row, text) for row, text in enumerate(texts)]
    table = _Table(phrases, reader, None if to is None else _base(reader, to))
    rows = [table.columns(phrase) for phrase in phrases]
    return pd.DataFrame(rows, index=data.index, columns=COLUMNS, dtype=object)


def _base(reader: Reader, to: str) -> Phrase:
    base = reader.phrase(TO_ROW, to)
    if not base.units:
        raise InvalidArguments(f"to: {to!r} has no words to compare.", action="Give --to a phrase of words.")
    return base


class _Table:
    """The relations of the phrases of a table, found through an index of their units."""

    def __init__(self, phrases: list[Phrase], reader: Reader, to: Phrase | None) -> None:
        self._phrases, self._reader = phrases, reader
        bases = phrases if to is None else [to]
        self._by_row = {phrase.row: phrase for phrase in [*phrases, *bases]}
        self._index: dict[Lemmas, list[Phrase]] = defaultdict(list)
        for phrase in bases:
            for key in phrase.keys:
                self._index[key].append(phrase)
        self._relations = {phrase.row: self._relation(phrase) for phrase in phrases if phrase.units}
        self._dependents: dict[int, list[Phrase]] = defaultdict(list)
        for row, base in self._bases().items():
            self._dependents[base].append(phrases[row])
        self._groups = self._first_rows()

    def _bases(self) -> dict[int, int]:
        """The row of each phrase that has a relation, mapped to the row of its base."""
        return {row: relation.base.row for row, relation in self._relations.items() if relation is not None}

    def columns(self, phrase: Phrase) -> list[str]:
        """The class, of, group and reason of a phrase."""
        if not phrase.units:
            return [OTHER, "", "", ""]
        group = self._phrases[self._groups[phrase.row]].text
        if (relation := self._relations[phrase.row]) is not None:
            return [relation.kind, relation.base.text, group, relation.reason]
        return [OTHER, "", group, self._why_other(phrase)]

    def _hits(self, phrase: Phrase) -> Counter[int]:
        """The other phrases that share a unit with `phrase` or hold a unit linked to one of it: how many of its units."""
        hits: Counter[int] = Counter()
        for key in phrase.keys:
            hits.update({found.row for linked in self._reader.linked(key) for found in self._index.get(linked, [])})
        hits.pop(phrase.row, None)
        return hits

    def _candidates(self, phrase: Phrase) -> list[Phrase]:
        return [self._by_row[row] for row in sorted(self._hits(phrase))]

    def _relation(self, phrase: Phrase) -> Relation | None:
        reach = frozenset().union(*(self._reader.linked(key) for key in phrase.keys))
        found = [
            relation
            for base in self._candidates(phrase)
            if base.before(phrase) and (base.lemmas == phrase.lemmas or base.within(reach))
            if (relation := self._relate(phrase, base)) is not None
        ]
        return min(found, key=Relation.rank, default=None)

    def _relate(self, phrase: Phrase, base: Phrase) -> Relation | None:
        earlier = base.row < phrase.row
        if earlier and base.lemmas == phrase.lemmas:
            return Relation(SAME, base, LEMMAS)
        pairing = best_pairing(phrase.cuts, base.cuts, self._reader.link)
        if len(pairing.pairs) < len(pairing.base):
            return None
        links = self._links(pairing)
        if extra := _unpaired(pairing.units, pairing.pairs.values()):
            return Relation(REFINEMENT, base, "; ".join([" ".join(f"+{name}" for name in extra), *links]))
        return Relation(VARIATION, base, "; ".join(links)) if earlier and links else None

    def _links(self, pairing: Pairing) -> list[str]:
        """The reasons of the links of the pairs that are not equal, in the order of the units of the base."""
        units = [
            (pairing.units[unit].lemmas, pairing.base[other].lemmas) for other, unit in sorted(pairing.pairs.items())
        ]
        return [self._reader.link(unit, other) or "" for unit, other in units if unit != other]

    def _first_rows(self) -> dict[int, int]:
        """The group of each phrase of units: the first row among the phrases whose chains of `of` end where its ends."""
        ends = {row: self._end(row) for row in self._relations}
        first: dict[int, int] = {}
        for row, end in sorted(ends.items()):
            first.setdefault(end, row)
        return {row: first[end] for row, end in ends.items()}

    def _end(self, row: int) -> int:
        while row != TO_ROW and (relation := self._relations[row]) is not None:
            row = relation.base.row
        return row

    def _why_other(self, phrase: Phrase) -> str:
        if dependents := self._dependents.get(phrase.row):
            return "base of: " + " | ".join(dependent.text for dependent in dependents)
        if (base := self._nearest(phrase)) is None:
            return "unlinked: " + ", ".join(_unpaired(phrase.units, ()))
        pairing = best_pairing(phrase.cuts, base.cuts, self._reader.link)
        own, others = _unpaired(pairing.units, pairing.pairs.values()), _unpaired(pairing.base, pairing.pairs)
        return f"unlinked: {', '.join(own)} | {', '.join(others)}"

    def _nearest(self, phrase: Phrase) -> Phrase | None:
        """The phrase that the most units of `phrase` reach, then the earliest; with --to, that phrase."""
        hits = self._hits(phrase)
        if not hits:
            return self._by_row.get(TO_ROW)
        return self._by_row[max(hits, key=lambda row: (hits[row], -row))]


def _unpaired(units: Sequence[Unit], paired: Collection[int]) -> list[str]:
    """The units of a cut whose places are not `paired`, each as its lemmas."""
    return [" ".join(unit.lemmas) for place, unit in enumerate(units) if place not in paired]
