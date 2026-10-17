"""Text steps: each matcher as `<verb>-<matcher>` for the verbs it supports, and `keep-` / `drop-<matcher>` row filters
for a matcher that can find (ADR 0004). `matcher_steps` makes them for any matcher factory (`MatcherFactory`: a library
function that makes a matcher); other areas reuse it. `ByLemmas` gives the words and phrases matchers the option
--lemmas: they compare the lemmas of the bundled dictionary.
"""

from __future__ import annotations

import inspect
import sys
from types import FunctionType
from typing import Any, Literal, Protocol

from ..core.errors import InvalidArguments
from ..core.frame import Frame
from ..core.morph.functions import BUNDLED
from ..core.text.base import Matcher, NotSingleWords, verbs
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
from . import Adapted, Change, Keep, Prepared, Step, option


class MatcherFactory(Protocol):
    """A function of the library that makes a matcher (or an `Adapted` one)."""

    __name__: str
    __module__: str

    def __call__(self, *args: Any, **kwargs: Any) -> Matcher: ...


LEMMAS_DOC = "lemmas: compare the lemmas of the words (the bundled dictionary): «дешевые диваны» is «дешевый диван»."


class ByLemmas(Adapted):
    """A matcher factory with the flag `lemmas` in place of its lemmatizer: on, the bundled one."""

    def __init__(self, factory: FunctionType) -> None:
        super().__init__(factory, {"lemmatizer": None, "lemmas": option("lemmas", bool, False)}, LEMMAS_DOC)

    def __call__(self, *args: Any, lemmas: bool = False, **kwargs: Any) -> Any:
        return self.__wrapped__(*args, lemmatizer=BUNDLED if lemmas else None, **kwargs)


MATCHERS: tuple[MatcherFactory, ...] = (
    ByLemmas(words), ByLemmas(phrases), stopwords, chars, spaces, regex, around, edges, positions,
    word_case, word_content, word_position, pos, repeats, cells,
)  # fmt: skip
# The text after the step name in the example of the help, by the name of a matcher whose required option the
# generator cannot fill.
EXAMPLES = {
    "words": "@stop/wordstat",
    "word_content": "starts --pattern куп",
    "word_position": "--nth 3",
    "word_case": "Capital",
    "around": "' в ' --after --include",
    "edges": "--end '!'",
    "cells": "contains --items бесплатно,скачать",
}
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


def _matcher(factory: MatcherFactory, options: dict, name: str) -> Matcher:
    """The matcher of a step; a list of phrases given to a step of words is sent to the step of phrases."""
    try:
        return factory(**options)
    except NotSingleWords as error:
        if not name.endswith("-words"):
            raise
        instead = name.removesuffix("-words") + "-phrases"
        raise InvalidArguments(error.message, action=f"Use {instead} for phrases of several words.") from None


def _verb_step(factory: MatcherFactory, verb: str, example: str | None) -> Step:
    name = f"{verb}-{_slug(factory)}"

    def prepare(options: dict) -> Prepared:
        apply = getattr(_matcher(factory, options, name), verb)
        return lambda table, column: Change(apply(Frame(table, column).phrases))

    new_column = "find" if verb == "find" else None
    return Step(name, factory, "change", prepare, f"{name} {VERB_NOTES[verb]}", new_column, example=example)


def _filter_step(factory: MatcherFactory, action: Literal["keep", "drop"], example: str | None) -> Step:
    name = f"{action}-{_slug(factory)}"

    def prepare(options: dict) -> Prepared:
        find = _matcher(factory, options, name).find

        def run(table, column):
            found = find(Frame(table, column).phrases)
            return Keep(found if action == "keep" else ~found)

        return run

    return Step(name, factory, "filter", prepare, f"{name} {FILTER_NOTES[action]}", example=example)


def matcher_steps(factory: MatcherFactory, example: str | None = None) -> list[Step]:
    """The steps of a matcher: a verb step for each verb it supports, and the keep and drop filters if it can find.

    `example` is the text after the step name in the example of their help, for a matcher whose required option the
    generator cannot fill.
    """
    supported = verbs(_matcher_type(factory))
    filters = [_filter_step(factory, action, example) for action in ("keep", "drop")] if "find" in supported else []
    return [*(_verb_step(factory, verb, example) for verb in supported), *filters]


STEPS = [step for factory in MATCHERS for step in matcher_steps(factory, EXAMPLES.get(factory.__name__))]
