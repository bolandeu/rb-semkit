"""The declension steps: declining words and phrases, agreeing the words of a phrase, the candidates for minus-words, the ready patterns."""

from __future__ import annotations

import pandas as pd

from ..core.declension.agreement import AGREED, NOTE, agree
from ..core.declension.full_names import decline_full_name
from ..core.declension.irrelevant import irrelevant_words
from ..core.declension.phrase import decline
from ..core.declension.words import decline_adjective, decline_noun
from ..core.frame import Frame
from ..core.patterns.complements import complements
from ..core.patterns.phrase_end import phrase_end
from ..core.patterns.ready import ready_pattern
from . import CHANGE_NOTE, Change, Prepared, Report, Step, change_step
from .text import matcher_steps


def _agreed(phrases: pd.Series) -> Change:
    found = agree(phrases)
    return Change(found[AGREED], found[[NOTE]])


def _prepare_agree(options: dict) -> Prepared:
    return lambda table, column: _agreed(Frame(table, column).phrases)


def _prepare_irrelevant(options: dict) -> Prepared:
    return lambda table, column: Report(irrelevant_words(Frame(table, column).phrases, **options))


STEPS = [
    *(change_step(function) for function in (decline, decline_noun, decline_adjective)),
    change_step(decline_full_name, source="names.csv"),
    Step(
        "agree",
        agree,
        "change",
        _prepare_agree,
        f"{CHANGE_NOTE} The column agree_note goes right after it.",
        source="combinations.csv",
    ),
    Step(
        "irrelevant-words",
        irrelevant_words,
        "report",
        _prepare_irrelevant,
        "The step reads the working column; the table replaces the current one, its column word is the working one.",
    ),
    *matcher_steps(ready_pattern, "domain"),
    *matcher_steps(complements),
    *matcher_steps(phrase_end, "prepositions"),
]
