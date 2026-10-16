"""Word repeats: exact and by wordforms; find and remove (the first occurrence stays)."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk


class FakeLemmatizer:
    """«стол» and «столы» share a lemma; everything else is its own lemma."""

    def lemma(self, word: str) -> str:
        return "стол" if word == "столы" else word

    def pos(self, word: str) -> str:  # pragma: no cover - not used by repeats
        return ""

    def forms(self, lemma: str) -> list[str]:  # pragma: no cover - not used by repeats
        return []


def test_exact_and_wordforms() -> None:
    phrases = pd.Series(["диван диван угловой", "стол столы"])

    assert sk.find(phrases, sk.repeats("exact")).tolist() == [True, False]
    assert sk.find(phrases, sk.repeats("wordforms")).tolist() == [True, True]


def test_wordforms_follow_the_given_lemmatizer() -> None:
    phrases = pd.Series(["стол столы", "диван диваны"])

    mask = sk.find(phrases, sk.repeats("wordforms", lemmatizer=FakeLemmatizer()))

    assert mask.tolist() == [True, False]


def test_remove_keeps_the_first_occurrence() -> None:
    phrases = pd.Series(["Диван купить диван, ДИВАН", "стол столы"])

    assert sk.remove(phrases, sk.repeats("exact")).tolist() == ["Диван купить", "стол столы"]
    assert sk.remove(phrases, sk.repeats("wordforms", lemmatizer=FakeLemmatizer())).tolist() == [
        "Диван купить",
        "стол",
    ]


def test_scopes() -> None:
    phrases = pd.Series(["диван a диван a 5 5", "диван диван a b a"])

    assert sk.remove(phrases, sk.repeats(scope="adjacent")).tolist() == ["диван a диван a 5", "диван a b a"]
    assert sk.remove(phrases, sk.repeats(scope="numbers")).tolist() == ["диван a диван a 5", "диван диван a b a"]
    assert sk.remove(phrases, sk.repeats(scope="en")).tolist() == ["диван a диван 5 5", "диван диван a b"]
    assert sk.remove(phrases, sk.repeats(scope="ru")).tolist() == ["диван a a 5 5", "диван a b a"]


def test_extract_is_not_supported() -> None:
    from rb_semkit.core.errors import InvalidArguments

    try:
        sk.extract(pd.Series(["a a"]), sk.repeats())
    except InvalidArguments as error:
        assert "find, remove" in str(error)
    else:
        raise AssertionError("InvalidArguments expected")
