"""lemmatize(..., fallback='pymorphy'): pymorphy3 gives the lemma of a word missing from the bundled dictionary."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk
from rb_semkit.core.errors import InvalidArguments

# Missing from the bundled dictionary and unknown to the pymorphy3 dictionary; its last letters are no lemma rule.
MISSING = pd.Series(["тиктокерами", "купила"])


def test_the_fallback_gives_the_pymorphy3_lemma() -> None:
    assert sk.lemmatize(MISSING, fallback="pymorphy").tolist() == ["тиктокер", "купить"]


def test_without_the_fallback_the_word_stays_as_it_is() -> None:
    assert sk.lemmatize(MISSING).tolist() == ["тиктокерами", "купить"]


def test_an_unknown_fallback_names_the_argument() -> None:
    with pytest.raises(InvalidArguments, match=r"^fallback='mystem'; allowed: 'pymorphy'"):
        sk.lemmatize(MISSING, fallback="mystem")


def test_the_fallback_is_for_the_bundled_lemmatizer() -> None:
    with pytest.raises(InvalidArguments, match=r"^fallback: "):
        sk.lemmatize(MISSING, fallback="pymorphy", lemmatizer=sk.SemtoolsLemmatizer())


def test_a_lemmatizer_with_the_fallback() -> None:
    lemmatizer = sk.SemtoolsLemmatizer(fallback="pymorphy")

    assert (lemmatizer.lemma("тиктокерами"), lemmatizer.pos("тиктокерами")) == ("тиктокер", "n")
