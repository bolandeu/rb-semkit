"""The duplicates step: marks the duplicates in a new column, or with `--action drop` drops them (a filter).

`--kind meaning` is a step by meaning (the vectors extra): it adds the columns dupes, dupe_of and similarity.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal, cast

import pandas as pd

from ..core import wordlists
from ..core.dupes.functions import DupeKind, dupes
from ..core.dupes.meaning import dupes_meaning
from ..core.errors import InvalidArguments
from ..core.frame import Frame
from . import Adapted, Change, Columns, Keep, Prepared, Step, as_table, flag, option, table_of
from .vectors import MEANING, MODEL_DOC, by_meaning

MEANING_KIND = "meaning"
BUNDLED_NEUTRAL = ("meaning/neutral", "stop/semtools")  # the commercial words, then the prepositions and particles
KIND_DOC = (
    "kind: exact (the same text), explicit (the same in any case, with ё as е and any spaces), implicit (the same words"
    " in another order), lemmas (the same lemmas in any order) or meaning (close phrase vectors, and the words that"
    " differ are only non-refining words, synonyms or the home city)."
)
NEUTRAL_DOC = (
    "neutral: the Human's non-refining words for --kind meaning, as @FILE or @NAME of a list; they add to the bundled"
    " list @meaning/neutral. Words are compared by lemma."
)
SYNONYMS_DOC = (
    "synonyms: a file with the columns word and synonyms, as the step `synonyms` gives, for --kind meaning; a word and"
    " its synonyms are the same word. The file is read like `read` does."
)
THRESHOLD_DOC = (
    "threshold: the similarity from 0 to 1 two phrases need to be one intent, for --kind meaning. Without it the"
    " threshold of the model."
)
HOME_DOC = "home: the name of the home city for --kind meaning; its word is non-refining, another city's is not."
MEANING_OPTIONS = ("threshold", "neutral", "synonyms", "home")


def _prepare(options: dict) -> Prepared:
    if options["kind"] == MEANING_KIND:
        return _prepare_meaning(options)
    if given := [flag(name) for name in MEANING_OPTIONS if options[name] is not None]:
        raise InvalidArguments(f"kind: {options['kind']!r} takes no {', '.join(given)}; allowed: meaning.")

    def run(table, column):
        phrases = Frame(table, column).phrases
        found = cast(pd.Series, dupes(phrases, kind=options["kind"], action=options["action"]))
        if options["action"] == "drop":
            return Keep(phrases.index.to_series().isin(found.index))
        return Change(found)

    return run


def refining_options(options: dict) -> tuple[list[str], pd.DataFrame | None]:
    """The non-refining words (the bundled lists and --neutral) and the synonyms table that the options name."""
    synonyms = None if options["synonyms"] is None else as_table(table_of(options["synonyms"], "synonyms"), "synonyms")
    return [item for name in BUNDLED_NEUTRAL for item in wordlists.resolve(name)] + (options["neutral"] or []), synonyms


def _prepare_meaning(options: dict) -> Prepared:
    found_encoder, threshold = by_meaning(options)
    neutral, synonyms = refining_options(options)

    def run(table, column):
        found = dupes_meaning(
            Frame(table, column).phrases,
            encoder=found_encoder,
            threshold=threshold,
            action=options["action"],
            neutral=neutral,
            synonyms=synonyms,
            home=options["home"],
        )
        if options["action"] == "drop":
            return Keep(~found["dupes"])
        return Columns(found.rename(columns={"dupes": f"{column}_dupes"}))

    return run


STEPS = [
    Step(
        "dupes",
        Adapted(
            dupes,
            {
                "kind": option("kind", Literal[DupeKind, "meaning"]),
                **MEANING,
                "neutral": option("neutral", Iterable[str] | None, None),
                "synonyms": option("synonyms", str | None, None),
                "home": option("home", str | None, None),
            },
            KIND_DOC,
            NEUTRAL_DOC,
            SYNONYMS_DOC,
            HOME_DOC,
            THRESHOLD_DOC,
            MODEL_DOC,
        ),
        "change",
        _prepare,
        "The step marks the duplicates of the working column in a new column <column>_dupes; with --action drop it"
        " keeps only the first row of each group. With --kind meaning it also adds the columns dupe_of (the first row"
        " of the group, the phrase kept) and similarity (the cosine to it) next to it.",
        new_column="dupes",
        example="lemmas --action mark_except_first",
    )
]
