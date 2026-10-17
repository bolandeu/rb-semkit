"""The change steps: each function that rewrites a phrase (case, insert, replace, order, characters, match types, UTM)."""

from __future__ import annotations

from ..core.change.case import change_case
from ..core.change.chars import chpu, guillemets, similar_chars, switch_layout, translit
from ..core.change.insert import insert, move_words
from ..core.change.match_types import drop_minus_words, drop_modifiers, match_type
from ..core.change.order import reverse, sort_words, split_digits
from ..core.change.phonetic import phonetic
from ..core.change.replace import replace_text, replace_words
from ..core.change.web import extract_utm, hash_text, remove_utm
from ..core.change.word_order import fix_word_order
from . import CHANGE_NOTE, Adapted, Step, change_step, changing, option, pairs_of, slug

PAIRS_DOC = (
    "pairs: a file of two columns, what to find and its replacement; the first row is the header,"
    " the file is read like `read` does."
)


def _replace_step(function) -> Step:
    pairs = Adapted(function, {"pairs": option("pairs")}, PAIRS_DOC)
    return Step(slug(function), pairs, "change", changing(function, pairs=("pairs", pairs_of)), CHANGE_NOTE)


# The text after the step name in the example of the help (where the generator cannot fill the option), the file it reads.
EXAMPLES = {
    insert: "--after ' в москве'",
    move_words: "@stop/wordstat",
    change_case: "lower",
    match_type: "quotes",
}
SOURCES = {extract_utm: "urls.csv", remove_utm: "urls.csv"}
STEPS = [
    *(
        change_step(function, source=SOURCES.get(function, "core.csv"), example=EXAMPLES.get(function))
        for function in (
            change_case, insert, move_words, split_digits, reverse, sort_words, guillemets, translit, chpu,
            switch_layout, similar_chars, match_type, drop_minus_words, drop_modifiers, extract_utm, remove_utm,
            hash_text, fix_word_order, phonetic,
        )
    ),
    _replace_step(replace_text),
    _replace_step(replace_words),
]  # fmt: skip
