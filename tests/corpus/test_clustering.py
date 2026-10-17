"""sk.cluster_by_frequency and sk.cluster_by_serp through the public library seam."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk


def rows(table: pd.DataFrame) -> list[tuple]:
    return list(table.itertuples(index=False, name=None))


def serp(tops: dict[str, list[str]]) -> pd.DataFrame:
    """A SERP table: one row per phrase and position, the urls of each top in position order from 1."""
    table = [(phrase, position, url) for phrase, urls in tops.items() for position, url in enumerate(urls, start=1)]
    return pd.DataFrame(table, columns=["phrase", "position", "url"])


def test_frequency_clusters_keep_the_frequent_words_of_a_phrase_in_any_word_order() -> None:
    core = pd.Series(["купить диван", "диван купить недорого", "диван угловой", "купить стол"])

    result = sk.cluster_by_frequency(core, threshold=2)

    assert result.tolist() == ["диван купить", "диван купить", "диван", "купить"]


def test_frequency_clusters_put_the_most_frequent_word_first() -> None:
    core = pd.Series(["купить диван", "диван угловой", "диван", "купить"])

    assert sk.cluster_by_frequency(core, threshold=2).tolist() == ["диван купить", "диван", "диван", "купить"]


def test_frequency_clusters_count_a_word_once_per_phrase_in_any_case_and_drop_stopwords() -> None:
    core = pd.Series(["Диван диван в москве", "диван в спб", "в москве"])

    assert sk.cluster_by_frequency(core, threshold=2).tolist() == ["диван москве", "диван", "москве"]


def test_a_frequency_threshold_below_one_is_refused() -> None:
    with pytest.raises(sk.InvalidArguments, match="threshold"):
        sk.cluster_by_frequency(pd.Series(["диван"]), threshold=0)


def test_two_tops_sharing_positions_1_2_and_8_score_28_and_are_one_cluster() -> None:
    first = [f"a{i}.ru" for i in range(1, 11)]
    second = ["a1.ru", "a2.ru", "b3.ru", "b4.ru", "b5.ru", "b6.ru", "b7.ru", "a8.ru", "b9.ru", "b10.ru"]

    assert rows(sk.cluster_by_serp(serp({"x": first, "y": second}))) == [("x", 1), ("y", 1)]
    assert rows(sk.cluster_by_serp(serp({"x": first, "y": second}), threshold=29)) == [("x", 1), ("y", 2)]


def test_identical_tops_score_45() -> None:
    top = [f"a{i}.ru" for i in range(1, 11)]

    assert rows(sk.cluster_by_serp(serp({"x": top, "y": top}), threshold=45)) == [("x", 1), ("y", 1)]
    assert rows(sk.cluster_by_serp(serp({"x": top, "y": top}), threshold=46)) == [("x", 1), ("y", 2)]


def test_clusters_come_largest_first_and_link_in_a_chain() -> None:
    tops = {
        "alone": ["z1", "z2", "z3"],
        "a": ["a1", "a2", "a3", "a4", "a5"],
        "b": ["a1", "a2", "a3", "a4", "b5"],
        "c": ["c1", "a2", "a3", "a4", "b5"],
    }

    assert rows(sk.cluster_by_serp(serp(tops))) == [("a", 1), ("b", 1), ("c", 1), ("alone", 2)]


def test_the_bonuses_and_the_shared_url_bonus_are_arguments() -> None:
    tops = {"x": ["u1", "u2"], "y": ["u1", "u3"]}

    assert rows(sk.cluster_by_serp(serp(tops), bonuses=(10,), shared_bonus=0, threshold=10)) == [("x", 1), ("y", 1)]
    assert rows(sk.cluster_by_serp(serp(tops), bonuses=(9,), shared_bonus=0, threshold=10)) == [("x", 1), ("y", 2)]


def test_the_rows_of_a_phrase_may_stand_anywhere_in_the_table() -> None:
    table = serp({"x": ["u1", "u2", "u3", "u4", "u5"], "y": ["u1", "u2", "u3", "u4", "u5"]}).sample(
        frac=1, random_state=1
    )

    assert rows(sk.cluster_by_serp(table)) == [("x", 1), ("y", 1)]


def test_a_serp_table_without_its_columns_is_refused_naming_them() -> None:
    with pytest.raises(sk.InvalidArguments, match="position"):
        sk.cluster_by_serp(pd.DataFrame({"phrase": ["x"], "url": ["u1"]}))


def test_a_position_below_one_is_refused() -> None:
    with pytest.raises(sk.InvalidArguments, match="position"):
        sk.cluster_by_serp(pd.DataFrame({"phrase": ["x"], "position": [0], "url": ["u1"]}))


def test_a_frequency_cluster_spells_a_word_as_it_first_stands_in_the_core() -> None:
    core = pd.Series(["Ёлка купить", "елка", "ёлка"])

    assert sk.cluster_by_frequency(core, threshold=2).tolist() == ["ёлка", "ёлка", "ёлка"]
