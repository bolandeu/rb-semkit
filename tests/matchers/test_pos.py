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
