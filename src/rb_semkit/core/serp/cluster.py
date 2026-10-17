"""cluster_serp: phrases of a given SERP table grouped by the number of URLs their tops share.

semkit never fetches search results; the table comes from another tool. Pairs of phrases come from an inverted
index url -> phrases, so only phrases that share a URL are ever compared. `soft` grows a cluster around a center;
`hard` lets a phrase join a cluster only when it shares enough URLs with every member.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Literal, get_args

import pandas as pd

from ..errors import InvalidArguments

Method = Literal["soft", "hard"]
METHODS = get_args(Method)
SERP_COLUMNS = ("phrase", "position", "url")
COLUMNS = ["phrase", "cluster", "center", "common"]
_URL_HEAD = r"^\s*(?:[a-z][a-z0-9+.-]*://)?(?:www\.)?"


def _checked(serp: pd.DataFrame, method: str, common: int, top: int) -> None:
    if not isinstance(serp, pd.DataFrame):
        raise InvalidArguments(f"serp is a {type(serp).__name__}; allowed: a pandas DataFrame.")
    missing = [name for name in SERP_COLUMNS if name not in serp.columns]
    if missing:
        raise InvalidArguments(
            f"serp: no column {', '.join(map(repr, missing))}; allowed columns: {', '.join(map(repr, SERP_COLUMNS))}."
        )
    if method not in METHODS:
        raise InvalidArguments(f"method={method!r}; allowed: {', '.join(map(repr, METHODS))}.")
    for name, value in (("common", common), ("top", top)):
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise InvalidArguments(f"{name}={value!r}; allowed: an integer from 1.")


def _tops(serp: pd.DataFrame, top: int) -> dict[str, frozenset[str]]:
    """The set of normalized URLs of each phrase's top; a phrase without a URL gets an empty set."""
    phrases = serp["phrase"].fillna("").astype(str)
    position = pd.to_numeric(serp["position"], errors="coerce")
    urls = (
        serp["url"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.replace(_URL_HEAD, "", regex=True)
        .str.rstrip("/")
        .str.strip()
    )
    kept = (position <= top) & (urls != "")
    tops: dict[str, set[str]] = {phrase: set() for phrase in phrases.unique()}
    for phrase, url in zip(phrases[kept], urls[kept], strict=True):
        tops[phrase].add(url)
    return {phrase: frozenset(urls_) for phrase, urls_ in tops.items()}


def _frequencies(freq: pd.DataFrame | pd.Series | None, phrases: list[str]) -> dict[str, float] | None:
    if freq is None:
        return None
    if isinstance(freq, pd.DataFrame):
        if not {"phrase", "freq"} <= set(freq.columns):
            raise InvalidArguments("freq: a DataFrame needs the columns 'phrase' and 'freq'; or give a Series.")
        freq = freq.set_index("phrase")["freq"]
    elif not isinstance(freq, pd.Series):
        raise InvalidArguments(f"freq is a {type(freq).__name__}; allowed: a Series, a DataFrame or None.")
    given = pd.to_numeric(freq, errors="coerce").fillna(0)
    given = given[~given.index.duplicated()]
    return {phrase: float(given.get(phrase, 0)) for phrase in phrases}


def _shared(tops: dict[str, frozenset[str]]) -> dict[str, Counter[str]]:
    """For each phrase, how many URLs it shares with every other phrase that shares any."""
    holders: dict[str, list[str]] = defaultdict(list)
    for phrase, urls in tops.items():
        for url in urls:
            holders[url].append(phrase)
    shared: dict[str, Counter[str]] = {phrase: Counter() for phrase in tops}
    for group in holders.values():
        for phrase in group:
            shared[phrase].update(group)
    for phrase in tops:
        del shared[phrase][phrase]
    return shared


def _links(shared: dict[str, Counter[str]], common: int) -> dict[str, set[str]]:
    return {phrase: {other for other, count in counts.items() if count >= common} for phrase, counts in shared.items()}


def _order(links: dict[str, set[str]], freq: dict[str, float] | None) -> list[str]:
    if freq is None:
        return sorted(links, key=lambda phrase: (-len(links[phrase]), phrase))
    return sorted(links, key=lambda phrase: (-freq[phrase], phrase))


def _soft(order: list[str], links: dict[str, set[str]]) -> list[list[str]]:
    rank = {phrase: index for index, phrase in enumerate(order)}
    assigned: set[str] = set()
    clusters = []
    for phrase in order:
        if phrase in assigned:
            continue
        members = [phrase, *sorted(links[phrase] - assigned, key=rank.__getitem__)]
        assigned.update(members)
        clusters.append(members)
    return clusters


def _hard(order: list[str], links: dict[str, set[str]]) -> list[list[str]]:
    clusters: list[list[str]] = []
    where: dict[str, int] = {}
    for phrase in order:
        joined = sorted({where[other] for other in links[phrase] if other in where})
        target = next((index for index in joined if links[phrase].issuperset(clusters[index])), None)
        if target is None:
            clusters.append([])
            target = len(clusters) - 1
        clusters[target].append(phrase)
        where[phrase] = target
    return clusters


def cluster_serp(
    serp: pd.DataFrame,
    *,
    method: Method = "soft",
    common: int = 3,
    top: int = 10,
    freq: pd.DataFrame | pd.Series | None = None,
) -> pd.DataFrame:
    """Cluster the phrases of a SERP table (columns phrase, position, url) by the common URLs of their tops.

    serp: the SERP table, one row per phrase and position.
    method: "soft" grows a cluster around its center: a phrase joins when it shares enough URLs with the center;
    "hard" lets a phrase join only when it shares enough URLs with every member of the cluster.
    common: how many URLs two phrases must share.
    top: how many first positions of each phrase count.
    freq: the frequency of each phrase; the most frequent phrase goes first. Without it the phrase with the most
    links to the others goes first, ties by phrase.

    One row per phrase: phrase, cluster (1 = the largest), center (the first phrase of the cluster) and common (URLs
    shared with the center; the center gets the size of its own top).
    """
    _checked(serp, method, common, top)
    tops = _tops(serp, top)
    frequencies = _frequencies(freq, list(tops))
    shared = _shared(tops)
    links = _links(shared, common)
    order = _order(links, frequencies)
    clusters = (_soft if method == "soft" else _hard)(order, links)
    rank = {phrase: index for index, phrase in enumerate(order)}
    clusters.sort(key=lambda members: (-len(members), rank[members[0]]))
    rows = [
        (phrase, number, members[0], len(tops[phrase]) if phrase == members[0] else shared[phrase][members[0]])
        for number, members in enumerate(clusters, start=1)
        for phrase in sorted(members, key=rank.__getitem__)
    ]
    return pd.DataFrame(rows, columns=COLUMNS)
