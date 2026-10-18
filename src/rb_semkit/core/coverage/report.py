"""coverage: the SEO check of texts against a core, one row per core phrase.

The texts are cut into pieces: sentences (`text.words.ends_sentence`), so an occurrence crosses a dash or a comma but
never a sentence end; for 'any_order' the phrases of `split_text` (`text.words.ends_phrase`). The pieces are indexed by
word, and every phrase is looked up by its words: the text is scanned once, not once per phrase.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Literal, get_args

import pandas as pd

from ..errors import InvalidArguments
from ..frame import Frame
from ..morph import Lemmatizer
from ..morph.functions import BUNDLED
from ..normalize import norm_phrase
from ..text.base import split_words
from ..text.words import Cut, ends_phrase, ends_sentence, pieces

Mode = Literal["exact", "lemmas", "any_order"]
MODES = get_args(Mode)
COLUMNS = ["phrase", "count", "docs", "density", "first"]
DECIMALS = 4

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


def _checked_gap(gap: int, mode: str) -> None:
    if gap < 0:
        raise InvalidArguments(f"gap={gap}; allowed: 0 or more.")
    if gap and mode == "any_order":
        raise InvalidArguments("gap does not apply to mode 'any_order': its words are already anywhere in one piece.")


def _key_of(mode: str, lemmatizer: Lemmatizer) -> Callable[[str], str]:
    if mode == "exact":
        return norm_phrase
    return lambda word: lemmatizer.lemma(norm_phrase(word))


def _pieces(texts: pd.Series, key: Callable[[str], str], cuts: Cut) -> Iterator[Piece]:
    """The pieces of every text in order, each with its words as keys; a word is keyed once however often it occurs."""
    keys: dict[str, str] = {}
    for doc, text in enumerate(texts):
        seen = 0
        for piece in pieces(text, cuts):
            words = [keys[word] if word in keys else keys.setdefault(word, key(word)) for word in piece]
            yield doc, seen, words
            seen += len(words)


def _end_of_match(keys: list[str], position: int, words: list[str], gap: int) -> int | None:
    """Where the phrase `words` that starts at `position` ends (the first end it can have), or None if it does not."""
    reached = [position]
    for word in words[1:]:
        reached = sorted(
            {at for last in reached for at in range(last + 1, min(last + gap + 2, len(keys))) if keys[at] == word}
        )
        if not reached:
            return None
    return reached[0] + 1


def _in_a_row(pieces: list[Piece], phrases: list[list[str]], tally: _Tally, gap: int) -> None:
    starts: dict[str, list[int]] = defaultdict(list)
    for number, words in enumerate(phrases):
        if words:
            starts[words[0]].append(number)
    for doc, offset, keys in pieces:
        ends: dict[int, int] = {}
        for position, key in enumerate(keys):
            for number in starts.get(key, ()):
                if ends.get(number, 0) > position:
                    continue
                end = _end_of_match(keys, position, phrases[number], gap)
                if end is not None:
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
    mode: Mode = "exact",
    gap: int = 0,
    lemmatizer: Lemmatizer = BUNDLED,
    column: str | None = None,
    text_column: str | None = None,
) -> pd.DataFrame:
    """Every distinct core phrase checked against the texts: a table phrase, count, docs, density and first.

    mode: 'exact' — the words of the phrase in a row, case and ё folded; 'lemmas' — the same by lemmas of both sides;
    'any_order' — the lemmas of the phrase all inside one piece of text (one phrase of split-text), in any order; a
    piece with them is one occurrence.
    gap: how many words may stand between each two neighbouring words of the phrase in 'exact' and 'lemmas' («купить
    недорогие пластиковые окна» is «купить пластиковые окна» with gap 1); the order stays and a gap never crosses a
    sentence end; 0 allows none. It does not apply to 'any_order', where the words are already anywhere in one piece.
    core: the core phrases.
    column: the column of the core phrases.
    texts: the texts, one per row.
    text_column: the column of the texts.
    lemmatizer: what gives the lemmas.

    exact and lemmas cross any punctuation inside a sentence («хранения — это» is «хранения это», a comma too), never a
    sentence end (. ! ? …; the point of an abbreviation such as «г.» is none). The rows follow the core order; a phrase
    that is not found stays with count 0, as the missing phrases are the point. The columns:
    - count: occurrences in all texts; one phrase does not overlap itself, and each phrase is counted on its own;
    - docs: the texts that hold the phrase at least once;
    - density: count x words of the phrase / words of all texts, a share from 0 to 1, rounded to 4 decimals;
    - first: the number of the word (1-based, all words of the text counted) where the phrase first starts, in the
      first text that holds it; empty when count is 0.

    Example: {cli} read --text "купить диван" --text "кресло" coverage texts.csv write -
    -> купить диван, 1, 1, 0.1667, 5; кресло, 2, 2, 0.1667, 4
    """
    _checked_mode(mode)
    _checked_gap(gap, mode)
    core_phrases = Frame(core, column).phrases
    text_rows = Frame(texts, text_column, argument="text_column").phrases.reset_index(drop=True)
    key = _key_of(mode, lemmatizer)
    distinct = list(dict.fromkeys(core_phrases))
    phrases = [[key(word) for word in split_words(phrase)] for phrase in distinct]
    any_order = mode == "any_order"
    found = list(_pieces(text_rows, key, ends_phrase if any_order else ends_sentence))
    tally = _Tally(len(distinct))
    if any_order:
        _in_any_order(found, phrases, tally)
    else:
        _in_a_row(found, phrases, tally, gap)
    total = sum(len(keys) for _, _, keys in found)
    density = [
        round(count * len(words) / total, DECIMALS) if total else 0.0
        for count, words in zip(tally.count, phrases, strict=True)
    ]
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
