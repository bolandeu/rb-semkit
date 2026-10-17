"""coverage: the SEO check of texts against a core, one row per core phrase.

The texts are cut into pieces with `split_text`, so a phrase never matches across a sentence end or punctuation.
The pieces are indexed by word, and every phrase is looked up by its words: the text is scanned once, not once per
phrase.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field

import pandas as pd

from ..errors import InvalidArguments
from ..frame import Frame
from ..morph import Lemmatizer
from ..morph.functions import BUNDLED
from ..normalize import norm_phrase
from ..split import split_text
from ..text.base import split_words

MODES = ("exact", "lemmas", "any_order")
COLUMNS = ["phrase", "count", "docs", "density", "first"]

Piece = tuple[int, int, list[str]]  # the text number, the words before the piece in its text, the keys of its words


@dataclass
class _Tally:
    """The hits of each phrase: occurrences, texts that hold it, and where it first starts."""

    size: int
    count: list[int] = field(init=False)
    docs: list[int] = field(init=False)
    first: list[int | None] = field(init=False)
    _last_doc: list[int] = field(init=False)

    def __post_init__(self) -> None:
        self.count = [0] * self.size
        self.docs = [0] * self.size
        self.first = [None] * self.size
        self._last_doc = [-1] * self.size

    def hit(self, phrase: int, doc: int, position: int) -> None:
        """One occurrence of `phrase` in text `doc`, starting at the word `position` (0-based)."""
        self.count[phrase] += 1
        if self._last_doc[phrase] != doc:
            self._last_doc[phrase] = doc
            self.docs[phrase] += 1
        if self.first[phrase] is None:
            self.first[phrase] = position + 1


def _checked_mode(mode: str) -> str:
    if mode not in MODES:
        raise InvalidArguments(f"mode={mode!r}; allowed: {', '.join(map(repr, MODES))}.")
    return mode


def _key_of(mode: str, lemmatizer: Lemmatizer) -> Callable[[str], str]:
    if mode == "exact":
        return norm_phrase
    return lambda word: lemmatizer.lemma(norm_phrase(word))


def _pieces(texts: pd.Series, key: Callable[[str], str]) -> Iterator[Piece]:
    """The pieces of every text in order, each with its words as keys; a word is keyed once however often it occurs."""
    keys: dict[str, str] = {}
    seen: Counter[int] = Counter()
    pieces = split_text(texts)
    for doc, piece in zip(pieces.index.astype(int).tolist(), pieces, strict=True):
        words = [keys[word] if word in keys else keys.setdefault(word, key(word)) for word in split_words(piece)]
        yield doc, seen[doc], words
        seen[doc] += len(words)


def _in_a_row(pieces: list[Piece], phrases: list[list[str]], tally: _Tally) -> None:
    starts: dict[str, list[int]] = defaultdict(list)
    for number, words in enumerate(phrases):
        if words:
            starts[words[0]].append(number)
    for doc, offset, keys in pieces:
        ends: dict[int, int] = {}
        for position, key in enumerate(keys):
            for number in starts.get(key, ()):
                end = position + len(phrases[number])
                if ends.get(number, 0) <= position and keys[position:end] == phrases[number]:
                    ends[number] = end
                    tally.hit(number, doc, offset + position)


def _in_any_order(pieces: list[Piece], phrases: list[list[str]], tally: _Tally) -> None:
    wanted = [set(words) for words in phrases]
    holding: dict[str, list[int]] = defaultdict(list)
    for number, words in enumerate(wanted):
        for word in words:
            holding[word].append(number)
    for doc, offset, keys in pieces:
        place: dict[str, int] = {}
        for position, key in enumerate(keys):
            place.setdefault(key, position)
        found = Counter(number for key in place for number in holding.get(key, ()))
        for number, hits in found.items():
            if hits == len(wanted[number]):
                tally.hit(number, doc, offset + min(place[word] for word in wanted[number]))


def coverage(
    core: pd.Series | pd.DataFrame,
    texts: pd.Series | pd.DataFrame,
    *,
    mode: str = "exact",
    lemmatizer: Lemmatizer = BUNDLED,
    column: str | None = None,
    text_column: str | None = None,
) -> pd.DataFrame:
    """Every distinct core phrase checked against the texts: a table phrase, count, docs, density and first.

    The rows follow the core order; a phrase that is not found stays with count 0, as the missing phrases are the point.
    count: occurrences in all texts; one phrase does not overlap itself, and each phrase is counted on its own.
    docs: the texts that hold the phrase at least once.
    density: count x words of the phrase / words of all texts, a share from 0 to 1.
    first: the number of the word (1-based, all words of the text counted) where the phrase first starts, in the
    first text that holds it; empty when count is 0.
    mode: 'exact' — the words of the phrase in a row, case and ё folded; 'lemmas' — the same by lemmas of both sides,
    by `lemmatizer`; 'any_order' — the lemmas of the phrase all inside one piece of text (one `split_text` phrase),
    in any order; a piece with them is one occurrence.
    core, column: the core phrases, a Series or a DataFrame with `column`. texts, text_column: the texts, one per row.
    """
    mode = _checked_mode(mode)
    core_phrases = Frame(core, column).phrases
    text_rows = Frame(texts, text_column, argument="text_column").phrases.reset_index(drop=True)
    key = _key_of(mode, lemmatizer)
    distinct = list(dict.fromkeys(core_phrases))
    phrases = [[key(word) for word in split_words(phrase)] for phrase in distinct]
    pieces = list(_pieces(text_rows, key))
    tally = _Tally(len(distinct))
    (_in_any_order if mode == "any_order" else _in_a_row)(pieces, phrases, tally)
    total = sum(len(keys) for _, _, keys in pieces)
    density = [count * len(words) / total if total else 0.0 for count, words in zip(tally.count, phrases, strict=True)]
    return pd.DataFrame(
        {
            "phrase": distinct,
            "count": tally.count,
            "docs": tally.docs,
            "density": density,
            "first": pd.array(tally.first, dtype="Int64"),
        },
        columns=COLUMNS,
    )
