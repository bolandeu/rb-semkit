"""The text area: the matchers that read the package data."""

from __future__ import annotations

import rb_semkit as sk

DATA_OPERATIONS = {
    "stopwords": lambda phrases: sk.remove(phrases, sk.stopwords()),
    "pos": lambda phrases: sk.find(phrases, sk.pos("adj", lemmatizer=sk.SemtoolsLemmatizer())),
}
