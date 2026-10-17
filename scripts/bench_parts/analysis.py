"""The analysis area: n-grams of words and of lemmas."""

from __future__ import annotations

import rb_semkit as sk

OPERATIONS = {
    "ngrams": lambda phrases: sk.ngrams(phrases),
    "ngrams_lemmas": lambda phrases: sk.ngrams(phrases, lemmas=True, lemmatizer=sk.SemtoolsLemmatizer()),
}
