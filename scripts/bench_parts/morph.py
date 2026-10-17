"""The morph area: parts of speech, lemmas and the wordforms of every word of the core."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk


def _wordforms(phrases: pd.Series) -> None:
    lemmatizer = sk.SemtoolsLemmatizer()
    for word in {word for phrase in phrases for word in phrase.split()}:
        sk.wordforms(word, lemmatizer=lemmatizer)


DATA_OPERATIONS = {
    "part_of_speech": lambda phrases: sk.part_of_speech(phrases, lemmatizer=sk.SemtoolsLemmatizer()),
    "lemmatize": lambda phrases: sk.lemmatize(phrases, lemmatizer=sk.SemtoolsLemmatizer()),
    "wordforms": _wordforms,
}
