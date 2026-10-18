"""synonym_candidates: for each word of the core, the words a thesaurus and word vectors propose as its synonyms."""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Literal

import pandas as pd

from ..analysis.frequency import bundled_stopwords, word_keys
from ..errors import InvalidArguments
from ..morph import Lemmatizer
from ..morph.functions import BUNDLED
from ..normalize import norm_phrase
from ..text.base import split_words
from ..vectors import registry
from ..vectors.cluster import DIGITS
from .navec import NAME as vectors_name
from .navec import WordVectors
from .thesaurus import NAME as thesaurus_name
from .thesaurus import Thesaurus

Source = Literal["ruwordnet", "navec", "both"]
COLUMNS = ["word", "candidate", "source", "score", "in_core"]
SYNONYM_COLUMNS = ["word", "synonyms"]
THESAURUS_SCORE = 1.0
Found = dict[str, list[tuple[str, float]]]  # the candidates of each word, each with its score


def synonym_candidates(
    data: pd.Series,
    *,
    thesaurus: Thesaurus | None,
    word_vectors: WordVectors | None,
    top: int = registry.bundled().words.top,
    all: bool = False,
    as_synonyms: bool = False,
    lemmatizer: Lemmatizer = BUNDLED,
) -> pd.DataFrame:
    """Synonym candidates for the words of the core, from a thesaurus (RuWordNet) and word vectors (navec).

    A candidate is a proposal for the Human to pick, not a synonym: the thesaurus gives the words of the same synset
    (score 1), the word vectors the nearest words (the score is the cosine, 4 places). The step works on lemmas;
    stopwords and words with digits are skipped, and so are candidates of several words. The report has one row for
    each candidate: word, candidate, source, score and in_core (whether the candidate is a word of the core), words in
    the order of the core, each with the candidates of the thesaurus first, then of the vectors from the nearest.
    data: the phrases of the core.
    thesaurus, word_vectors: the data of the sources; None leaves a source out.
    top: how many of the nearest words the word vectors give for each word.
    all: give every candidate. By default only the candidates that occur in the core.
    as_synonyms: the report as the file the steps with `--synonyms` read: the columns word and synonyms (the
    candidates of a word joined by a space), one row for each word that has some.
    lemmatizer: what gives the lemmas.
    """
    if isinstance(top, bool) or not isinstance(top, int) or top < 1:
        raise InvalidArguments(f"top={top!r}; allowed: an integer of 1 or more.")
    words = _core_words(data, lemmatizer)
    inside = frozenset(words)
    lemma_of = functools.cache(lambda word: norm_phrase(lemmatizer.lemma(norm_phrase(word))))
    found = {
        thesaurus_name: _from_thesaurus(thesaurus, words) if thesaurus is not None else {},
        vectors_name: _from_vectors(word_vectors, words, inside, top, all, lemma_of)
        if word_vectors is not None
        else {},
    }
    rows = _rows(words, inside, found, all)
    report = pd.DataFrame(rows, columns=COLUMNS)
    return _as_synonyms(report) if as_synonyms else report


def _rows(
    words: list[str], inside: frozenset[str], found: dict[str, Found], all: bool
) -> list[tuple[str, str, str, float, bool]]:
    """A row for each candidate of each word; by default only the candidates that are words of the core."""
    return [
        (word, candidate, source, score, candidate in inside)
        for word in words
        for source, candidates in found.items()
        for candidate, score in candidates.get(word, ())
        if all or candidate in inside
    ]


def _core_words(data: pd.Series, lemmatizer: Lemmatizer) -> list[str]:
    """The lemmas of the words of the core, each once, in the order of the core."""
    phrases = data.fillna("").astype(str)
    keys = word_keys(phrases, lemmatizer=lemmatizer, stopwords=False)
    lemmas = ((keys[word][0], keys[word][1]) for phrase in phrases.unique() for word in split_words(phrase))
    return list(dict.fromkeys(lemma for lemma, counts in lemmas if counts and _usable(lemma)))


def _usable(word: str) -> bool:
    """Whether a word can be a word of the core or a candidate: one word, no digits, not a stopword."""
    return (
        word != "" and " " not in word and not any(char.isdigit() for char in word) and word not in bundled_stopwords()
    )


def _from_thesaurus(thesaurus: Thesaurus, words: list[str]) -> Found:
    return {
        word: [(synonym, THESAURUS_SCORE) for synonym in thesaurus.synonyms(word) if _usable(synonym)] for word in words
    }


def _from_vectors(
    word_vectors: WordVectors,
    words: list[str],
    inside: frozenset[str],
    top: int,
    all: bool,
    lemma_of: Callable[[str], str],
) -> Found:
    """The `top` nearest lemmas of each word: the nearest words, each as its lemma, a lemma at its nearest form."""
    asked = word_vectors.neighbours(words, None if all else inside, top * registry.bundled().words.pool)
    found = {}
    for word, neighbours in asked.items():
        best: dict[str, float] = {}
        for neighbour, score in neighbours:
            lemma = lemma_of(neighbour)
            if lemma != word and _usable(lemma):
                best.setdefault(lemma, round(float(score), DIGITS))
        found[word] = list(best.items())[:top]
    return found


def _as_synonyms(report: pd.DataFrame) -> pd.DataFrame:
    """The candidates of each word joined by a space, as the file of synonyms is."""
    joined = report.groupby("word", sort=False)["candidate"].agg(lambda candidates: " ".join(dict.fromkeys(candidates)))
    return joined.rename("synonyms").reset_index()[SYNONYM_COLUMNS]
