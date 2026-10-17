"""Clustering of a semantic core: by the frequency dictionary of its words, and by the search results of its phrases."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from collections.abc import Sequence
from itertools import combinations

import pandas as pd
from pandas.api import types

from ..analysis.frequency import _word_keys
from ..errors import InvalidArguments
from ..frame import Frame
from ..text.base import split_words, whole_number
from .tables import require_columns

__all__ = ["cluster_by_frequency", "cluster_by_serp"]

SERP_COLUMNS = ("phrase", "position", "url")


def cluster_by_frequency(
    data: pd.Series | pd.DataFrame,
    *,
    threshold: int,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """The cluster of each phrase: its words that stand in at least `threshold` phrases of the core.

    A word counts once per phrase; words are compared by case and ё; stopwords are left out. The cluster lists its
    words in lower case, the most frequent first, then alphabetically, so «купить диван» and «диван купить» make one
    cluster. A phrase with no such word gets "".
    """
    whole_number("threshold", threshold)
    frame = Frame(data, column, inplace)
    phrases = frame.phrases
    keys = _word_keys(phrases, lemmatizer=None, stopwords=False)
    spelling: dict[str, str] = {}  # each key as its word first stands in the core, in lower case
    word_sets = {}
    for phrase in phrases.unique():
        counted = [(keys[word][0], word) for word in split_words(phrase) if keys[word][1]]
        for key, word in counted:
            spelling.setdefault(key, word.lower())
        word_sets[phrase] = frozenset(key for key, _ in counted)
    frequency: Counter[str] = Counter()
    for phrase, rows in phrases.value_counts(sort=False).items():
        frequency.update(dict.fromkeys(word_sets[phrase], rows))

    def cluster(words: frozenset[str]) -> str:
        kept = sorted((key for key in words if frequency[key] >= threshold), key=lambda key: (-frequency[key], key))
        return " ".join(spelling[key] for key in kept)

    return frame.put(phrases.map({phrase: cluster(words) for phrase, words in word_sets.items()}), "cluster")


def _tops(table: pd.DataFrame) -> dict[str, dict[str, int]]:
    """The top of each phrase in the order of its first row: each url and its last position (from 0)."""
    require_columns(table, "table", SERP_COLUMNS)
    positions = table["position"]
    if not types.is_integer_dtype(positions) or (positions < 1).any():
        raise InvalidArguments("table: the column 'position' holds a value that is no integer of 1 or more.")
    tops: dict[str, dict[str, int]] = {}
    for phrase, position, url in table.sort_values("position", kind="stable")[list(SERP_COLUMNS)].itertuples(
        index=False
    ):
        tops.setdefault(str(phrase), {})[str(url)] = position - 1
    return tops


def _score(first: dict[str, int], second: dict[str, int], top_bonuses: list[int], shared_bonus: int) -> int:
    """How alike two tops are: `shared_bonus` per shared url, plus the top bonus of the lower of its two positions."""
    score = 0
    for url, position in first.items():
        if url in second:
            lower = max(position, second[url])
            score += shared_bonus + (top_bonuses[lower] if lower < len(top_bonuses) else 0)
    return score


def _components(phrases: list[str], links: dict[str, list[str]]) -> list[list[str]]:
    """The linked groups of phrases, each walked breadth-first from its first phrase."""
    seen: set[str] = set()
    groups = []
    for start in phrases:
        if start in seen:
            continue
        seen.add(start)
        group, queue = [], deque([start])
        while queue:
            phrase = queue.popleft()
            group.append(phrase)
            for linked in links[phrase]:
                if linked not in seen:
                    seen.add(linked)
                    queue.append(linked)
        groups.append(group)
    return groups


def cluster_by_serp(
    table: pd.DataFrame,
    *,
    bonuses: Sequence[int] = (5, 4, 3, 2, 1),
    shared_bonus: int = 1,
    threshold: int = 24,
) -> pd.DataFrame:
    """Clusters of phrases with alike search results: a table phrase, cluster (1 is the largest cluster).

    table: the search results, one row per url, with the columns phrase, position (from 1) and url.
    Two tops are alike by their score: each url they share adds `shared_bonus`, and when it stands within the first
    len(`bonuses`) positions of both, also the sum of `bonuses` from its lower position on (with the defaults 15 for
    position 1 of both, then 10, 6, 3, 1). Two phrases whose score is `threshold` or more are linked, and a cluster is
    a chain of links. Clusters come largest first, then in the order of the table; a phrase is in one cluster only.
    """
    tops = _tops(table)
    top_bonuses = [sum(bonuses[position:]) for position in range(len(bonuses))]
    phrases = list(tops)
    order = {phrase: row for row, phrase in enumerate(phrases)}
    by_url: dict[str, list[str]] = defaultdict(list)
    for phrase, top in tops.items():
        for url in top:
            by_url[url].append(phrase)
    pairs = {pair for holders in by_url.values() for pair in combinations(holders, 2)}
    links: dict[str, list[str]] = {phrase: [] for phrase in phrases}
    for first, second in sorted(pairs, key=lambda pair: (order[pair[0]], order[pair[1]])):
        if _score(tops[first], tops[second], top_bonuses, shared_bonus) >= threshold:
            links[first].append(second)
            links[second].append(first)
    groups = sorted(_components(phrases, links), key=len, reverse=True)
    clustered = [(phrase, number) for number, group in enumerate(groups, start=1) for phrase in group]
    return pd.DataFrame(clustered, columns=["phrase", "cluster"])
