"""Lemmas, parts of speech and wordforms through the public library seam, and the Lemmatizer protocol."""

from __future__ import annotations

from typing import ClassVar

import pandas as pd

import rb_semkit as sk


def test_lemmas_pos_and_wordforms_from_the_bundled_dictionary() -> None:
    phrases = pd.Series(["москве", "купила"], index=[10, 20])

    assert sk.lemmatize(phrases).tolist() == ["москва", "купить"]
    assert sk.lemmatize(phrases).index.tolist() == [10, 20]
    assert sk.part_of_speech(phrases).tolist() == ["n", "v"]
    assert "москве" in sk.wordforms("москва")


def test_phrases_are_lemmatized_word_by_word() -> None:
    phrases = pd.Series(["купила диваны в Москве", "", None])

    assert sk.lemmatize(phrases).tolist() == ["купить диван в москва", "", ""]


def test_lemmas_are_lower_case() -> None:
    assert sk.lemmatize(pd.Series(["Москве"])).tolist() == ["москва"]


def test_a_word_missing_from_the_dictionary_goes_to_pymorphy3() -> None:
    phrases = pd.Series(["стримами"])

    assert sk.lemmatize(phrases).tolist() == ["стрим"]
    assert sk.part_of_speech(phrases).tolist() == ["n"]


def test_a_word_unknown_to_both_gets_the_suffix_fallback() -> None:
    phrases = pd.Series(["зюзюкания", "зюзюкалками"])

    # «ания» → «ание» by lemmSuf; «ками» is not in the table, so the word stays as it is
    assert sk.lemmatize(phrases).tolist() == ["зюзюкание", "зюзюкалками"]


def test_pos_rules_of_the_add_in() -> None:
    lemmatizer = sk.SemtoolsLemmatizer()

    assert lemmatizer.pos("постричься") == "v"  # the dictionary says p; the ending -ься says verb
    assert lemmatizer.pos("выражают") == "v"  # the dictionary says p; the ending -ают says verb
    assert lemmatizer.pos("уют") == "n"  # the word «уют» itself is not a verb
    assert lemmatizer.lemma("зюзюкового") == "зюзюковый"  # unknown word: «вого» → «вый» by lemmSuf
    assert lemmatizer.pos("зюзюкового") == "a"  # and its lemma has an adjective ending
    assert lemmatizer.pos("волнослой") == "unkn"  # an adjective ending, but listed in nounsLikeAdj
    assert lemmatizer.pos("зюзюкалками") == "unkn"  # unknown word, no rule
    assert lemmatizer.pos("15") == "unkn"
    assert lemmatizer.pos("нераскладной") == "a"  # the dictionary says n; «раскладной» is an adjective


def test_a_wordform_with_yo_finds_its_ye_spelling() -> None:
    assert sk.lemmatize(pd.Series(["ёлки"])).tolist() == ["елка"]


def test_wordforms_of_an_unknown_lemma_are_empty() -> None:
    assert sk.wordforms("зюзюка") == []


class FakeLemmatizer:
    """Two entries; any other word is its own lemma with no POS."""

    LEMMAS: ClassVar = {"диваны": ("диван", "n"), "купила": ("купить", "v")}

    def lemma(self, word: str) -> str:
        return self.LEMMAS.get(word, (word, ""))[0]

    def pos(self, word: str) -> str:
        return self.LEMMAS.get(word, (word, ""))[1]

    def forms(self, lemma: str) -> list[str]:
        return [word for word, (found, _) in self.LEMMAS.items() if found == lemma]


def test_a_lemma_dependent_function_uses_only_the_given_lemmatizer() -> None:
    fake = FakeLemmatizer()
    phrases = pd.Series(["купила диваны", "москве"])

    assert sk.lemmatize(phrases, lemmatizer=fake).tolist() == ["купить диван", "москве"]
    assert sk.part_of_speech(phrases, lemmatizer=fake).tolist() == ["v n", ""]
    assert sk.wordforms("диван", lemmatizer=fake) == ["диваны"]


def test_a_lemma_optional_function_works_on_words_as_they_are_without_a_lemmatizer() -> None:
    phrases = pd.Series(["купить диваны", "диван"])

    assert sk.find(phrases, sk.words("диван")).tolist() == [False, True]
    assert sk.find(phrases, sk.words("диван", lemmatizer=FakeLemmatizer())).tolist() == [True, True]
    assert sk.remove(phrases, sk.words("диван", lemmatizer=FakeLemmatizer())).tolist() == ["купить", ""]


def test_lemmatize_a_dataframe_column() -> None:
    df = pd.DataFrame({"phrase": ["купила диваны"], "freq": [5]})

    out = sk.lemmatize(df, column="phrase")

    assert list(out.columns) == ["phrase", "phrase_lemmatize", "freq"]
    assert out["phrase_lemmatize"].tolist() == ["купить диван"]


def test_the_dictionary_correction_codes_luchshe_as_an_adverb_and_pokryvalo_as_a_noun() -> None:
    phrases = pd.Series(["лучше", "покрывало на диван", "покрывала", "покрывалом"])

    assert sk.part_of_speech(phrases).tolist() == ["advb", "n prep n", "n", "n"]
    assert sk.lemmatize(phrases).tolist() == ["хороший", "покрывало на диван", "покрывало", "покрывало"]
