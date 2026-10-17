"""Parents, children and basis phrases. A parent of a phrase is another phrase whose words are some of its words, but
not all: «купить стол» is a parent of «купить стол недорого», and that is its child. Word order and repeated words do
not count; words are compared by case and ё. A phrase is never its own parent, in any word order."""

from __future__ import annotations

import functools
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Iterator
from itertools import combinations
from typing import NamedTuple

import pandas as pd

from ..analysis.frequency import _word_keys
from ..errors import InvalidArguments
from ..frame import Frame, map_unique
from ..morph import Lemmatizer
from ..morph.functions import BUNDLED
from ..normalize import norm_phrase
from ..text.base import split_words

__all__ = ["basis_phrases", "first_children", "first_parents", "nearest_parents"]

SUBSET_WORDS = 12  # a phrase of up to this many distinct words looks its subsets up one by one (at most 4094)


class Item(NamedTuple):
    order: int
    text: str
    words: frozenset[str]


def _word_set(phrase: str) -> frozenset[str]:
    return frozenset(norm_phrase(word) for word in split_words(phrase))


def _items(argument: str, phrases: Iterable[str]) -> list[Item]:
    """The non-empty phrases of a list with their word sets, in the order of the list; of the phrases with one set of
    words only the first, as it comes before the others in every search."""
    listed = [phrases] if isinstance(phrases, str) else list(pd.Series(phrases, dtype=object).fillna(""))
    if not all(isinstance(phrase, str) for phrase in listed):
        raise InvalidArguments(f"{argument}: holds a value that is not text; allowed: a list or Series of phrases.")
    firsts: dict[frozenset[str], Item] = {}
    for order, text in enumerate(listed):
        if words := _word_set(text):
            firsts.setdefault(words, Item(order, text, words))
    return list(firsts.values())


class Subsets:
    """The items of a list by their sets of words, to find the items whose words are some of a phrase's."""

    def __init__(self, items: list[Item]) -> None:
        self._items = items
        self._by_words = {item.words: item for item in items}

    @functools.cached_property
    def _by_rarest_word(self) -> dict[str, list[Item]]:
        """Each item filed under its rarest word: the index for a phrase of many words."""
        frequency = Counter(word for item in self._items for word in item.words)
        filed: dict[str, list[Item]] = defaultdict(list)
        for item in self._items:
            filed[min(item.words, key=lambda word: (frequency[word], word))].append(item)
        return filed

    def within(self, words: frozenset[str]) -> Iterator[Item]:
        """The items whose words are some of `words`, but not all."""
        if len(words) > SUBSET_WORDS:
            return (item for word in words for item in self._by_rarest_word.get(word, ()) if item.words < words)
        ordered = sorted(words)
        chosen = (frozenset(part) for size in range(1, len(ordered)) for part in combinations(ordered, size))
        return (item for part in chosen if (item := self._by_words.get(part)) is not None)


def _per_phrase(
    data: pd.Series | pd.DataFrame, find: Callable[[str], str], operation: str, column: str | None, inplace: bool
) -> pd.Series | pd.DataFrame:
    frame = Frame(data, column, inplace)
    return frame.put(map_unique(frame.phrases, find), operation)


def nearest_parents(
    data: pd.Series | pd.DataFrame,
    parents: Iterable[str],
    *,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """The parent from `parents` with the most words for each phrase, or "" when it has none.

    Between parents with as many words, the one whose words stand later in the phrase wins («a b c»: «b c» before
    «a c»), then the first in the list. Empty items of `parents` are skipped.
    """
    subsets = Subsets(_items("parents", parents))

    def nearest(phrase: str) -> str:
        words = [norm_phrase(word) for word in split_words(phrase)]
        place = {word: words.index(word) for word in set(words)}
        best = max(
            subsets.within(frozenset(words)),
            key=lambda item: (len(item.words), sorted(place[word] for word in item.words)),
            default=None,
        )
        return best.text if best else ""

    return _per_phrase(data, nearest, "nearest_parents", column, inplace)


def first_parents(
    data: pd.Series | pd.DataFrame,
    parents: Iterable[str],
    *,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """The first item of `parents` that is a parent of the phrase, or "" when none is. Empty items are skipped."""
    subsets = Subsets(_items("parents", parents))

    def first(phrase: str) -> str:
        found = min(subsets.within(_word_set(phrase)), key=lambda item: item.order, default=None)
        return found.text if found else ""

    return _per_phrase(data, first, "first_parents", column, inplace)


def first_children(
    data: pd.Series | pd.DataFrame,
    children: Iterable[str],
    *,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """The first item of `children` that is a child of the phrase, or "" when none is; an empty phrase has none."""
    items = _items("children", children)
    by_words = {item.words: number for number, item in enumerate(items)}
    holding: dict[str, list[int]] = defaultdict(list)
    for number, item in enumerate(items):
        for word in item.words:
            holding[word].append(number)
    held = {word: set(numbers) for word, numbers in holding.items()}

    def first(phrase: str) -> str:
        words = _word_set(phrase)
        if not words:
            return ""
        own = by_words.get(words)  # the item with these words only is no child
        rarest, *others = sorted(words, key=lambda word: len(holding.get(word, ())))
        if others:
            common = held.get(rarest, set()).intersection(*(held.get(word, set()) for word in others))
            common.discard(own)
            found = min(common, default=None)
        else:
            found = next((number for number in holding.get(rarest, ()) if number != own), None)
        return "" if found is None else items[found].text

    return _per_phrase(data, first, "first_children", column, inplace)


def basis_phrases(
    data: pd.Series | pd.DataFrame,
    *,
    lemmas: bool = False,
    stopwords: bool = True,
    lemmatizer: Lemmatizer = BUNDLED,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Each phrase that is a basis of the core, or "" for the others: a basis holds no smaller phrase of the core.

    A phrase is a basis when it is the first with its set of words and no other phrase of the core has some of its
    words only: «купить диван», «диван», «диван купить» → «», «диван», «». Words are compared by case and ё.
    lemmas: compare the lemmas of the words («диваны» is «диван»), by `lemmatizer`.
    stopwords: False leaves the stopwords out of the comparison; a phrase of stopwords only keeps them.
    """
    frame = Frame(data, column, inplace)
    phrases = frame.phrases
    keys = _word_keys(phrases, lemmatizer=lemmatizer if lemmas else None, stopwords=stopwords)

    def word_set(phrase: str) -> frozenset[str]:
        entries = [keys[word] for word in split_words(phrase)]
        return frozenset(key for key, counts, _ in entries if counts) or frozenset(key for key, _, _ in entries if key)

    sets = map_unique(phrases, word_set).tolist()
    owners: dict[frozenset[str], int] = {}
    for row, words in enumerate(sets):
        owners.setdefault(words, row)
    subsets = Subsets([Item(row, "", words) for words, row in owners.items() if words])
    kept = [
        bool(words) and owners[words] == row and next(subsets.within(words), None) is None
        for row, words in enumerate(sets)
    ]
    return frame.put(phrases.where(kept, ""), "basis_phrases")
