"""The looked-up units of a phrase: a segmentation of it into runs of words that do not overlap.

A run is a sense of several words of the thesaurus (found by lemmas); a word in no such sense is a unit by itself. A
stopword is no unit by itself, and stays inside a run when the sense holds it.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import NamedTuple

from ..analysis.frequency import bundled_stopwords
from ..normalize import norm_phrase
from ..text.base import split_words
from .thesaurus import Lemmas


class Token(NamedTuple):
    word: str  # as the phrase has it, in lower case
    lemma: str
    counts: bool  # whether the word can be a unit by itself: no stopword, no digit


class Unit(NamedTuple):
    text: str
    lemmas: Lemmas


def tokens(phrase: str, lemma_of: Callable[[str], str]) -> list[Token]:
    """The words of `phrase`, each with its lemma."""
    words = [word for word in map(norm_phrase, split_words(phrase)) if word]
    return [
        Token(word, lemma_of(word), word not in bundled_stopwords() and not any(char.isdigit() for char in word))
        for word in words
    ]


def segment(words: list[Token], phrases: frozenset[Lemmas], longest: int) -> list[Unit]:
    """The units of a phrase: of all the segmentations, the one with the most words inside the `phrases` (senses of
    several words) wins, then the one with fewer units, then the first from the left."""
    best: list[tuple[int, int, list[Unit]]] = [(0, 0, [])] * (len(words) + 1)
    for start in range(len(words) - 1, -1, -1):
        options = []
        for stop in range(min(len(words), start + longest), start + 1, -1):
            run = words[start:stop]
            if _lemmas(run) in phrases:
                covered, units, rest = best[stop]
                options.append((covered + len(run), units + 1, [_unit(run), *rest]))
        covered, units, rest = best[start + 1]
        alone = [_unit(words[start : start + 1])] if words[start].counts else []
        options.append((covered, units + len(alone), [*alone, *rest]))
        best[start] = max(options, key=lambda option: (option[0], -option[1]))
    return best[0][2]


def cuts(words: list[Token], phrases: frozenset[Lemmas], longest: int) -> list[list[Unit]]:
    """Every segmentation of a phrase that leaves no run of `phrases` out (each run is in it or overlaps one of it):
    the segmentation of `segment` first, then the others from the left."""
    runs = [
        (start, stop)
        for start in range(len(words))
        for stop in range(start + 2, min(len(words), start + longest) + 1)
        if _lemmas(words[start:stop]) in phrases
    ]
    found = [segment(words, phrases, longest)]
    for chosen in _choices(runs, []):
        if (units := _units(words, chosen)) not in found:
            found.append(units)
    return found


Run = tuple[int, int]  # the place of the first word of a run and the place after its last word


def _choices(runs: list[Run], chosen: list[Run]) -> list[list[Run]]:
    """The sets of `runs`, besides `chosen`, that do not overlap and leave out no run that fits beside them."""
    if not runs:
        return [chosen]
    first, rest = runs[0], runs[1:]
    beside = [run for run in rest if not _overlaps(run, [first])]
    found = _choices(beside, [*chosen, first])
    if len(beside) < len(rest):  # a run overlaps the first one: the first may be left out for it
        found += [option for option in _choices(rest, chosen) if _overlaps(first, option)]
    return found


def _overlaps(run: Run, chosen: list[Run]) -> bool:
    return any(start < run[1] and run[0] < stop for start, stop in chosen)


def _units(words: list[Token], chosen: list[Run]) -> list[Unit]:
    """The runs chosen as units, and every other word that counts as a unit by itself, in the order of the phrase."""
    stops = dict(chosen)
    units, place = [], 0
    while place < len(words):
        if place in stops:
            units.append(_unit(words[place : stops[place]]))
            place = stops[place]
            continue
        if words[place].counts:
            units.append(_unit(words[place : place + 1]))
        place += 1
    return units


def _unit(run: list[Token]) -> Unit:
    return Unit(" ".join(token.word for token in run), _lemmas(run))


def _lemmas(run: list[Token]) -> Lemmas:
    return tuple(token.lemma for token in run)
