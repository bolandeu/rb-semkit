"""sk.cluster_by_frequency through the public library seam; SERP tables go to sk.cluster_serp."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pytest

import rb_semkit as sk

DEVIATIONS = Path(__file__).resolve().parents[2] / "docs" / "vba" / "deviations" / "corpus.md"


def deviations(section: str) -> dict[str, str]:
    """The deviations of a section of the corpus deviations document: each rule (the bold start of an item), its text."""
    text = DEVIATIONS.read_text(encoding="utf-8")
    body = text.split(f"## {section}\n", 1)[1].split("\n## ", 1)[0]
    items = re.split(r"^- ", body, flags=re.MULTILINE)[1:]
    return {
        match.group(1): " ".join(match.group(2).split())
        for match in (re.match(r"\*\*(.+?)\*\*(.*)", item, flags=re.DOTALL) for item in items)
        if match
    }


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


def test_the_corpus_area_has_no_serp_clustering_and_the_add_in_method_is_recorded() -> None:
    assert not hasattr(sk, "cluster_by_serp")
    assert callable(sk.cluster_serp)
    recorded = deviations("Кластеризация")["Кластеризация по выдаче не переносится: её делает `sk.cluster_serp`."]
    for fact in ("5 4 3 2 1", "от 24", "компонента связности", "без единого общего URL", "ADR 0007"):
        assert fact in recorded


def test_a_frequency_cluster_spells_a_word_as_it_first_stands_in_the_core() -> None:
    core = pd.Series(["Ёлка купить", "елка", "ёлка"])

    assert sk.cluster_by_frequency(core, threshold=2).tolist() == ["ёлка", "ёлка", "ёлка"]
