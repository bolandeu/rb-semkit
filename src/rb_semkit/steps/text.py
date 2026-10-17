"""Text steps: each matcher as `<verb>-<matcher>` for the verbs it supports, and `keep-` / `drop-<matcher>` row filters
for a matcher that can find (ADR 0004)."""

from __future__ import annotations

import inspect
import sys
from types import FunctionType
from typing import Literal

from ..core.frame import Frame
from ..core.text.base import Matcher, verbs
from ..core.text.matchers.around import around
from ..core.text.matchers.cells import cells
from ..core.text.matchers.chars import chars
from ..core.text.matchers.edges import edges
from ..core.text.matchers.phrases import phrases
from ..core.text.matchers.pos import pos
from ..core.text.matchers.positions import positions
from ..core.text.matchers.regex import regex
from ..core.text.matchers.repeats import repeats
from ..core.text.matchers.spaces import spaces
from ..core.text.matchers.stopwords import stopwords
from ..core.text.matchers.word_case import word_case
from ..core.text.matchers.word_content import word_content
from ..core.text.matchers.word_position import word_position
from ..core.text.matchers.words import words
from . import Change, Keep, Prepared, Step

MatcherFactory = FunctionType  # a function of the library that makes a matcher

MATCHERS: tuple[MatcherFactory, ...] = (
    words, phrases, stopwords, chars, spaces, regex, around, edges, positions,
    word_case, word_content, word_position, pos, repeats, cells,
)  # fmt: skip
VERB_NOTES = {
    "find": "marks the rows where the matcher finds something, in a new column <column>_find of true and false.",
    "remove": "removes what the matcher finds from the working column.",
    "extract": "keeps only what the matcher finds in the working column; an empty cell where it finds nothing.",
}
FILTER_NOTES = {
    "keep": "keeps only the rows where the matcher finds something in the working column.",
    "drop": "drops the rows where the matcher finds something in the working column.",
}


def _matcher_type(factory: MatcherFactory) -> type[Matcher]:
    """The class of the matchers `factory` makes: its return annotation, read in its module."""
    return getattr(sys.modules[factory.__module__], inspect.signature(factory).return_annotation)


def _slug(factory: MatcherFactory) -> str:
    return factory.__name__.replace("_", "-")


def _verb_step(factory: MatcherFactory, verb: str) -> Step:
    def prepare(options: dict) -> Prepared:
        apply = getattr(factory(**options), verb)
        return lambda table, column: Change(apply(Frame(table, column).phrases))

    new_column = "find" if verb == "find" else None
    name = f"{verb}-{_slug(factory)}"
    return Step(name, factory, "change", prepare, f"{name} {VERB_NOTES[verb]}", new_column)


def _filter_step(factory: MatcherFactory, action: Literal["keep", "drop"]) -> Step:
    def prepare(options: dict) -> Prepared:
        find = factory(**options).find

        def run(table, column):
            found = find(Frame(table, column).phrases)
            return Keep(found if action == "keep" else ~found)

        return run

    name = f"{action}-{_slug(factory)}"
    return Step(name, factory, "filter", prepare, f"{name} {FILTER_NOTES[action]}")


def _steps(factory: MatcherFactory) -> list[Step]:
    supported = verbs(_matcher_type(factory))
    filters = [_filter_step(factory, action) for action in ("keep", "drop")] if "find" in supported else []
    return [*(_verb_step(factory, verb) for verb in supported), *filters]


STEPS = [step for factory in MATCHERS for step in _steps(factory)]
