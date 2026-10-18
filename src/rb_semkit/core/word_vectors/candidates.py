"""synonym_candidates: for each unit of the core, the words and phrases a thesaurus and word vectors propose as its synonyms."""

from __future__ import annotations

import functools
from collections.abc import Callable, Iterable
from typing import Literal, NamedTuple

import pandas as pd

from ..analysis.frequency import bundled_stopwords
from ..errors import InvalidArguments
from ..morph import Lemmatizer
from ..morph.functions import BUNDLED
from ..normalize import norm_phrase
from ..vectors import registry
from ..vectors.cluster import DIGITS
from .navec import NAME as vectors_name
from .navec import WordVectors
from .thesaurus import NAME as thesaurus_name
from .thesaurus import Lemmas, Sense, Thesaurus
from .units import Token, Unit, segment, tokens

Source = Literal["ruwordnet", "navec", "both"]
COLUMNS = ["word", "candidate", "source", "score", "in_core"]
SYNONYM_COLUMNS = ["word", "synonyms"]
SLOT = "slot_"  # the name of a column of --as-slots, followed by its number
THESAURUS_SCORE = 1.0


class Candidate(NamedTuple):
    name: str
    lemmas: Lemmas
    score: float


Found = dict[str, list[Candidate]]  # the candidates of each unit, by its text


def synonym_candidates(
    data: pd.Series,
    *,
    thesaurus: Thesaurus | None,
    word_vectors: WordVectors | None,
    top: int = registry.bundled().words.top,
    all: bool = False,
    as_synonyms: bool = False,
    as_slots: bool = False,
    lemmatizer: Lemmatizer = BUNDLED,
) -> pd.DataFrame:
    """Synonym candidates for the units of the core, from a thesaurus (RuWordNet) and word vectors (navec).

    A candidate is a proposal for the Human to pick, not a synonym: the thesaurus gives the words and phrases of the
    same synset (score 1), the word vectors the nearest words (the score is the cosine, 4 places).
    A unit is a word of a phrase of the core, or a run of its words that is a sense of several words of the
    thesaurus («таможенное оформление»): of all the ways to cut a phrase into runs, the one with the most words inside
    such senses wins, then the one with fewer units, then the first from the left. A word inside a run has no
    candidates of its own. A stopword is no unit by itself, and so is a word with digits. The step works on lemmas;
    a candidate of the thesaurus has any number of words, a candidate of the vectors is one word, and each is given
    once for a unit. The report has one row for each candidate: word (the unit), candidate, source, score and in_core
    (whether the candidate is a run of words of a phrase of the core), units in the order of the core, each with the
    candidates of the thesaurus first, then of the vectors from the nearest.
    data: the phrases of the core.
    thesaurus, word_vectors: the data of the sources; None leaves a source out.
    top: how many of the nearest words the word vectors give for each word.
    all: give every candidate. By default only the candidates that occur in the core.
    as_synonyms: the report as the file the steps with `--synonyms` read: the columns word and synonyms (the
    candidates of a word joined by a space), one row for each word that has some. The steps compare word by word, so
    it holds the candidates of one word of the units of one word only.
    as_slots: the report as the table of slots that `linear-combinations` reads: a column slot_1, slot_2… for each
    unit of the one phrase of the core, in its order; the first row holds the units, the rows under them their
    candidates. More than one phrase, or together with as_synonyms, is refused.
    lemmatizer: what gives the lemmas.

    Example: {cli} read --text "растаможка" --text "таможенное оформление" synonym-candidates --source ruwordnet write -
    -> растаможка, таможенное оформление, ruwordnet, 1.0, true; таможенное оформление, растаможка, ruwordnet, 1.0, true
    """
    if isinstance(top, bool) or not isinstance(top, int) or top < 1:
        raise InvalidArguments(f"top={top!r}; allowed: an integer of 1 or more.")
    if as_slots and as_synonyms:
        raise InvalidArguments("as_slots and as_synonyms together; allowed: one of them.")
    phrases = [phrase for phrase in data.fillna("").astype(str).unique() if norm_phrase(phrase)]
    if as_slots and len(phrases) != 1:
        raise InvalidArguments(f"as_slots with {len(phrases)} phrases in the core; allowed: a core of one phrase.")
    lemma_of = functools.cache(lambda word: norm_phrase(lemmatizer.lemma(norm_phrase(word))))
    words = [tokens(phrase, lemma_of) for phrase in phrases]
    cut = [_units(phrase, thesaurus) for phrase in words]
    units = list({unit.text: unit for phrase in cut for unit in phrase}.values())
    inside = frozenset(token.lemma for phrase in words for token in phrase if token.counts)
    found = {
        thesaurus_name: _from_thesaurus(thesaurus, units) if thesaurus is not None else {},
        vectors_name: _from_vectors(word_vectors, units, inside, top, all, lemma_of)
        if word_vectors is not None
        else {},
    }
    report = pd.DataFrame(_rows(units, found, _grams(words, found), all), columns=COLUMNS)
    if as_slots:
        return _as_slots(cut[0], report)
    return _as_synonyms(report) if as_synonyms else report


def _units(phrase: list[Token], thesaurus: Thesaurus | None) -> list[Unit]:
    """The units of a phrase; with no thesaurus every word is a unit."""
    return segment(phrase, *((thesaurus.phrases, thesaurus.longest) if thesaurus is not None else (frozenset(), 1)))


def _grams(words: list[list[Token]], found: dict[str, Found]) -> frozenset[Lemmas]:
    """The runs of words, by lemmas, of the phrases of the core: as long as the longest candidate."""
    size = max(
        (len(candidate.lemmas) for source in found.values() for each in source.values() for candidate in each),
        default=1,
    )
    return frozenset(
        tuple(token.lemma for token in phrase[start : start + length])
        for phrase in words
        for length in range(1, size + 1)
        for start in range(len(phrase) - length + 1)
    )


def _rows(
    units: list[Unit], found: dict[str, Found], grams: frozenset[Lemmas], all: bool
) -> list[tuple[str, str, str, float, bool]]:
    """A row for each candidate of each unit; by default only the candidates that are runs of words of the core."""
    return [
        (unit.text, candidate.name, source, candidate.score, candidate.lemmas in grams)
        for unit in units
        for source, candidates in found.items()
        for candidate in candidates.get(unit.text, ())
        if all or candidate.lemmas in grams
    ]


def _usable(word: str) -> bool:
    """Whether a word can be a candidate: no digits, not a stopword."""
    return (
        word != "" and " " not in word and not any(char.isdigit() for char in word) and word not in bundled_stopwords()
    )


def _proposable(sense: Sense) -> bool:
    """Whether a sense can be a candidate: a phrase with no digits, or a word that is usable."""
    return _usable(sense.name) if len(sense.lemmas) == 1 else not any(char.isdigit() for char in sense.name)


def _from_thesaurus(thesaurus: Thesaurus, units: list[Unit]) -> Found:
    return {
        unit.text: [
            Candidate(sense.name, sense.lemmas, THESAURUS_SCORE)
            for sense in thesaurus.synonyms(unit.lemmas)
            if _proposable(sense)
        ]
        for unit in units
    }


def _from_vectors(
    word_vectors: WordVectors,
    units: list[Unit],
    inside: frozenset[str],
    top: int,
    all: bool,
    lemma_of: Callable[[str], str],
) -> Found:
    """For each unit of one word, the `top` nearest lemmas: the nearest words, each as its lemma, a lemma at its
    nearest form."""
    lemmas = list(dict.fromkeys(unit.lemmas[0] for unit in units if len(unit.lemmas) == 1))
    asked = word_vectors.neighbours(lemmas, None if all else inside, top * registry.bundled().words.pool)
    nearest = {lemma: _nearest(lemma, neighbours, lemma_of)[:top] for lemma, neighbours in asked.items()}
    return {
        unit.text: [Candidate(name, (name,), score) for name, score in nearest[unit.lemmas[0]]]
        for unit in units
        if len(unit.lemmas) == 1 and unit.lemmas[0] in nearest
    }


def _nearest(
    word: str, neighbours: Iterable[tuple[str, float]], lemma_of: Callable[[str], str]
) -> list[tuple[str, float]]:
    best: dict[str, float] = {}
    for neighbour, score in neighbours:
        lemma = lemma_of(neighbour)
        if lemma != word and _usable(lemma):
            best.setdefault(lemma, round(float(score), DIGITS))
    return list(best.items())


def _as_slots(phrase: list[Unit], report: pd.DataFrame) -> pd.DataFrame:
    """A column for each unit of the phrase: the unit, then its candidates, each once; short columns end in empty cells."""
    columns = []
    for unit in phrase:
        candidates = report.loc[report["word"] == unit.text, "candidate"]
        columns.append([unit.text, *dict.fromkeys(candidates)])
    height = max(map(len, columns), default=0)
    return pd.DataFrame(
        {f"{SLOT}{number}": column + [""] * (height - len(column)) for number, column in enumerate(columns, 1)},
        dtype=object,
    )


def _as_synonyms(report: pd.DataFrame) -> pd.DataFrame:
    """The candidates of one word of each unit of one word, joined by a space, as the file of synonyms is."""
    words = report[~report["word"].str.contains(" ") & ~report["candidate"].str.contains(" ")]
    joined = words.groupby("word", sort=False)["candidate"].agg(lambda candidates: " ".join(dict.fromkeys(candidates)))
    return joined.rename("synonyms").reset_index()[SYNONYM_COLUMNS]
