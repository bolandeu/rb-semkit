"""The dupes area: each kind of duplicate, marked except the first."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk

DUPE_KINDS = ("exact", "explicit", "implicit", "lemmas")


def _dupes(phrases: pd.Series) -> None:
    for kind in DUPE_KINDS:
        sk.dupes(phrases, kind=kind, action="mark_except_first")


OPERATIONS = {"dupes": _dupes}
