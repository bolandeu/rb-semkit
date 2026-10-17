"""sk.cluster_serp: soft and hard clusters by common URLs, URL comparison, lone phrases and bad arguments."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk


def serp_of(tops: dict[str, list[str]]) -> pd.DataFrame:
    rows = [(phrase, position, url) for phrase, urls in tops.items() for position, url in enumerate(urls, start=1)]
    return pd.DataFrame(rows, columns=["phrase", "position", "url"])


def urls(*numbers: int) -> list[str]:
    return [f"https://site{number}.ru/" for number in numbers]


# A and B share 4 URLs, B and C share 4, A and C share none.
CHAIN = {"A": urls(1, 2, 3, 4), "B": urls(1, 2, 3, 4, 5, 6, 7, 8), "C": urls(5, 6, 7, 8)}


def clusters_of(table: pd.DataFrame) -> dict[str, int]:
    return dict(zip(table["phrase"], table["cluster"], strict=True))


def test_hard_keeps_a_and_c_apart_when_b_is_between_them() -> None:
    freq = pd.Series({"A": 30, "B": 20, "C": 10})

    table = sk.cluster_serp(serp_of(CHAIN), method="hard", common=3, freq=freq)

    clusters = clusters_of(table)
    assert clusters["A"] == clusters["B"]
    assert clusters["C"] != clusters["A"]


def test_soft_joins_phrases_to_the_center_by_frequency() -> None:
    freq = pd.Series({"A": 30, "B": 20, "C": 10})

    table = sk.cluster_serp(serp_of(CHAIN), method="soft", common=3, freq=freq)

    assert table.to_dict("records") == [
        {"phrase": "A", "cluster": 1, "center": "A", "common": 4},
        {"phrase": "B", "cluster": 1, "center": "A", "common": 4},
        {"phrase": "C", "cluster": 2, "center": "C", "common": 4},
    ]


def test_hard_requires_enough_common_urls_with_every_member() -> None:
    tops = {"A": urls(1, 2, 3), "B": urls(1, 2, 3, 4), "C": urls(2, 3, 4)}
    freq = pd.Series({"A": 3, "B": 2, "C": 1})

    table = sk.cluster_serp(serp_of(tops), method="hard", common=3, freq=freq)

    assert clusters_of(table) == {"A": 1, "B": 1, "C": 2}


def test_urls_equal_after_trimming_scheme_www_and_trailing_slash() -> None:
    tops = {"A": ["https://www.site.ru/a/"], "B": ["http://site.ru/a"]}

    table = sk.cluster_serp(serp_of(tops), common=1)

    assert table["cluster"].tolist() == [1, 1]
    assert table["common"].tolist() == [1, 1]


def test_positions_above_top_are_ignored() -> None:
    tops = {"A": urls(1, 2, 3), "B": urls(7, 8, 3)}

    table = sk.cluster_serp(serp_of(tops), common=1, top=2)

    assert table["cluster"].tolist() == [1, 2]


def test_phrase_without_enough_common_urls_is_a_cluster_of_one() -> None:
    tops = {"A": urls(1, 2, 3), "B": urls(1, 2, 3), "lone": urls(1, 9, 10)}

    table = sk.cluster_serp(serp_of(tops), common=3)

    row = table[table["phrase"] == "lone"].iloc[0]
    assert (row["cluster"], row["center"], row["common"]) == (2, "lone", 3)


def test_phrase_without_results_is_a_cluster_of_one() -> None:
    serp = pd.DataFrame({"phrase": ["A", "B"], "position": [1, 1], "url": ["x.ru", None]})

    table = sk.cluster_serp(serp, common=1)

    assert table.to_dict("records") == [
        {"phrase": "A", "cluster": 1, "center": "A", "common": 1},
        {"phrase": "B", "cluster": 2, "center": "B", "common": 0},
    ]


def test_without_freq_the_phrase_with_most_links_is_the_center() -> None:
    table = sk.cluster_serp(serp_of(CHAIN), method="soft", common=3)

    assert table["center"].tolist() == ["B", "B", "B"]


def test_larger_cluster_is_first_and_a_freq_dataframe_is_accepted() -> None:
    tops = {"x": urls(1, 2), "y": urls(3, 4), "z": urls(3, 4), "w": urls(3, 4)}
    freq = pd.DataFrame({"phrase": ["x", "y", "z", "w"], "freq": [100, 5, 4, 3]})

    table = sk.cluster_serp(serp_of(tops), common=2, freq=freq)

    assert clusters_of(table) == {"y": 1, "z": 1, "w": 1, "x": 2}


@pytest.mark.parametrize(
    ("kwargs", "named"),
    [({"method": "single"}, "method"), ({"common": 0}, "common"), ({"top": 0}, "top")],
)
def test_bad_arguments_are_named(kwargs: dict, named: str) -> None:
    with pytest.raises(sk.InvalidArguments, match=named):
        sk.cluster_serp(serp_of(CHAIN), **kwargs)


def test_table_without_url_is_refused_naming_the_column() -> None:
    with pytest.raises(sk.InvalidArguments, match="url"):
        sk.cluster_serp(serp_of(CHAIN).drop(columns="url"))
