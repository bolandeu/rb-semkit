"""Words by part of speech through a Lemmatizer: the bundled one, or a fake."""

from __future__ import annotations

from typing import ClassVar

import pandas as pd

import rb_semkit as sk


class FakeLemmatizer:
    CODES: ClassVar[dict[str, str]] = {"диван": "a", "красный": "n", "быстро": "v", "купить": "advb"}

    def lemma(self, word: str) -> str:  # pragma: no cover - not used by pos
        return word

    def pos(self, word: str) -> str:
        return self.CODES.get(word, "")

    def forms(self, lemma: str) -> list[str]:  # pragma: no cover - not used by pos
        return []


def test_bundled_lemmatizer_gives_adjectives() -> None:
    phrases = pd.Series(["красный диван", "быстро купить"], index=[4, 5])

    result = sk.extract(phrases, sk.pos("adj"))

    assert result.tolist() == ["красный", ""]
    assert result.index.tolist() == [4, 5]


def test_bundled_lemmatizer_other_parts_of_speech() -> None:
    phrases = pd.Series(["красный диван", "быстро купить"])

    assert sk.extract(phrases, sk.pos("noun")).tolist() == ["диван", ""]
    assert sk.extract(phrases, sk.pos("verb")).tolist() == ["", "купить"]
    assert sk.extract(phrases, sk.pos("adverb")).tolist() == ["", "быстро"]
    assert sk.remove(phrases, sk.pos("adj")).tolist() == ["диван", "быстро купить"]
    assert sk.find(phrases, sk.pos("adj")).tolist() == [True, False]


def test_a_fake_lemmatizer_decides() -> None:
    phrases = pd.Series(["красный диван", "быстро купить"])

    assert sk.extract(phrases, sk.pos("adj", lemmatizer=FakeLemmatizer())).tolist() == ["диван", ""]
    assert sk.extract(phrases, sk.pos("adverb", lemmatizer=FakeLemmatizer())).tolist() == ["", "купить"]


def test_a_capitalised_word_is_one_part_of_speech() -> None:
    phrases = pd.Series(["диван раскладной Быстро в Москве"])

    adjectives = sk.extract(phrases, sk.pos("adj")).iloc[0].split()
    adverbs = sk.extract(phrases, sk.pos("adverb")).iloc[0].split()

    assert ("Быстро" in adjectives) != ("Быстро" in adverbs)
    assert "Москве" in sk.extract(phrases, sk.pos("noun")).iloc[0].split()


def test_a_capitalised_word_is_looked_up_like_its_lower_case() -> None:
    phrases = pd.Series(["Красный Диван", "красный диван"])

    assert sk.extract(phrases, sk.pos("adj")).tolist() == ["Красный", "красный"]
    assert sk.extract(phrases, sk.pos("noun")).tolist() == ["Диван", "диван"]
