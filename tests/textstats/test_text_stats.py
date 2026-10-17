"""sk.text_stats through the public library seam."""

from __future__ import annotations

import math
import time

import numpy as np
import pandas as pd
import pytest

import rb_semkit as sk
from rb_semkit.core.textstats.metrics import mtld, zipf

SAMPLE = "Диван купить. Диван и диваны в Москве!"


class Identity:
    """A lemmatizer that leaves words as they are."""

    def lemma(self, word: str) -> str:
        return word


def one(text: str, **kwargs) -> pd.Series:
    return sk.text_stats(pd.Series([text]), **kwargs).iloc[0]


def test_a_text_of_ten_distinct_words_has_ttr_one() -> None:
    text = "красный синий зеленый желтый черный белый серый рыжий розовый лиловый"

    assert one(text, lemmatizer=Identity())["ttr"] == 1.0


def test_the_sample_text_by_hand() -> None:
    row = one(SAMPLE)

    assert row["chars"] == len(SAMPLE)
    assert row["chars_no_spaces"] == len(SAMPLE.replace(" ", ""))
    assert row["words"] == 7
    assert row["top"] == "диван"
    assert row["nausea_classic"] == 1.73
    assert row["nausea_academic"] == pytest.approx(3 / 7)
    assert row["water"] == pytest.approx(2 / 7)
    assert row["unique"] == 3  # диван, купить, москва


def test_a_tie_for_the_top_takes_the_first_in_the_text_and_units_are_no_lemmas() -> None:
    row = one("диван 5000 руб руб руб")

    assert row["top"] == "диван"
    assert row["words"] == 5
    assert row["nausea_classic"] == 1.0


def test_an_in_word_hyphen_keeps_one_word_and_other_punctuation_splits() -> None:
    assert one("кресло-кровать, диван!стол")["words"] == 3


def test_empty_cells_give_zeros_and_an_empty_top() -> None:
    table = sk.text_stats(pd.Series([None, np.nan, "", "диван"], index=[5, 6, 7, 8]))

    assert table.index.tolist() == [5, 6, 7, 8]
    assert (table.iloc[:3].drop(columns="top") == 0).all(axis=None)
    assert table["top"].tolist()[:3] == ["", "", ""]
    assert table.loc[8, "words"] == 1


def test_a_dataframe_gets_the_metric_columns_after_the_text_column() -> None:
    df = pd.DataFrame({"id": [1], "text": [SAMPLE], "tail": ["x"]})

    result = sk.text_stats(df, column="text")

    assert result.columns.tolist()[:3] == ["id", "text", "chars"]
    assert result.columns.tolist()[-1] == "tail"
    assert "words" in result.columns
    assert result.loc[0, "words"] == 7


def test_mtld_equals_lemmas_over_the_mean_of_the_factors() -> None:
    # forward: a b c d a (ttr .8) b (.667 <= .72) is factor 1; c d a b stay at ttr 1: partial 0 -> 1 factor.
    # backward (b a d c b a d c b a): the same shape -> 1 factor. 10 lemmas / 1 = 10.
    assert mtld(list("abcdabcdab")) == 10.0


def test_mtld_adds_the_partial_run() -> None:
    # a b c a: ttr 1 1 1 .75, no factor; partial (1 - .75) / .28 = .8929 both ways -> 4 / .8929 = 4.48
    assert mtld(list("abca")) == 4.48


def test_mtld_takes_lemmas_over_the_mean_of_unequal_directions() -> None:
    # forward a a b c d e: a a (.5) is factor 1; b c d e ttr 1 -> 1.0.
    # backward e d c b a a: five types in six tokens (.833), no factor; partial (1 - .8333) / .28 = .5952.
    # 6 / ((1 + .5952) / 2) = 7.52
    assert mtld(list("aabcde")) == 7.52


def test_mtld_is_zero_for_under_two_lemmas() -> None:
    assert mtld(["a"]) == 0.0
    assert mtld([]) == 0.0


def test_zipf_is_100_for_counts_that_follow_one_over_rank() -> None:
    assert zipf([60, 30, 20, 15, 12]) == 100.0


def test_zipf_is_zero_under_five_distinct_lemmas() -> None:
    assert zipf([4, 3, 2, 1]) == 0.0


def test_zipf_of_a_text_uses_lemma_counts() -> None:
    words = ["а1"] * 60 + ["б2"] * 30 + ["в3"] * 20 + ["г4"] * 15 + ["д5"] * 12

    assert one(" ".join(words), lemmatizer=Identity())["zipf"] == 100.0


def test_nausea_classic_has_two_decimals() -> None:
    assert one("а1 " * 5 + "б2", lemmatizer=Identity())["nausea_classic"] == round(math.sqrt(5), 2)


def test_thousand_texts_of_two_thousand_words_run_fast() -> None:
    words = [f"слово{i}" for i in range(300)]
    texts = pd.Series([" ".join(words[(i + j) % 300] for j in range(2000)) for i in range(1000)])
    sk.text_stats(texts.iloc[:1])  # loads the data

    start = time.perf_counter()
    sk.text_stats(texts)

    assert time.perf_counter() - start < 30
