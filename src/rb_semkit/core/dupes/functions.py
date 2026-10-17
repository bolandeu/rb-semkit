"""`dupes`: each distinct phrase gets a key by its kind once; the keys are compared and the result is mapped back.

An empty phrase (no words) has no key, so it is never a duplicate of anything.

`key_function` gives the key of a kind; other tools (`compare_lists`) reuse it as the one notion of «the same phrase».
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal, get_args

import pandas as pd

from ..errors import InvalidArguments
from ..frame import Frame, map_unique
from ..morph.functions import BUNDLED
from ..morph.lemmatizer import Lemmatizer
from ..normalize import norm_phrase
from ..text.base import split_words

DupeKind = Literal["exact", "explicit", "implicit", "lemmas"]
Action = Literal["mark_except_first", "mark_all", "drop"]
ACTIONS = get_args(Action)


def _exact(phrase: str) -> str:
    return phrase if phrase.strip() else ""


def _explicit(phrase: str) -> str:
    return norm_phrase(phrase)


def _implicit(phrase: str) -> str:
    return " ".join(sorted(split_words(norm_phrase(phrase))))


def _lemma_key(lemmatizer: Lemmatizer) -> Callable[[str], str]:
    def key(phrase: str) -> str:
        return " ".join(sorted(lemmatizer.lemma(word) for word in split_words(norm_phrase(phrase))))

    return key


def key_function(kind: DupeKind, lemmatizer: Lemmatizer | None) -> Callable[[str], str]:
    simple = {"exact": _exact, "explicit": _explicit, "implicit": _implicit}
    if kind in simple:
        return simple[kind]
    if kind == "lemmas":
        return _lemma_key(lemmatizer or BUNDLED)
    allowed = ", ".join(get_args(DupeKind))
    raise InvalidArguments(f"kind: {kind!r} is not a kind of duplicates; allowed: {allowed}.")


def _marks(keys: pd.Series, action: str, against_keys: pd.Series | None) -> pd.Series:
    """True for a duplicate; an empty key never is."""
    filled = keys != ""
    if against_keys is not None:
        return filled & keys.isin(set(against_keys[against_keys != ""]))
    return filled & keys.duplicated(keep="first" if action != "mark_all" else False)


def dupes(
    data: pd.Series | pd.DataFrame,
    *,
    kind: DupeKind,
    action: Action,
    against: pd.Series | None = None,
    lemmatizer: Lemmatizer | None = None,
    column: str | None = None,
) -> pd.Series | pd.DataFrame:
    """Duplicates of the phrases, by kind.

    kind: exact (the same text), explicit (the same in any case, with ё as е and any spaces), implicit (the same words in
    another order) or lemmas (the same lemmas in any order).
    action: mark_except_first (true for each duplicate, false for the first of its group), mark_all (true for every
    member of a group of 2 or more), drop (keep the first, drop the rest).
    against: other phrases; with them a phrase is a duplicate when it stands among them.
    lemmatizer: what gives the lemmas.
    """
    key_of = key_function(kind, lemmatizer)
    if action not in ACTIONS:
        raise InvalidArguments(f"action: {action!r} is not an action; allowed: {', '.join(ACTIONS)}.")
    frame = Frame(data, column)
    against_keys = None if against is None else map_unique(Frame(against).phrases, key_of)
    marks = _marks(map_unique(frame.phrases, key_of), action, against_keys)
    if action != "drop":
        return frame.put(marks, "dupes")
    return data[~marks.to_numpy()]
