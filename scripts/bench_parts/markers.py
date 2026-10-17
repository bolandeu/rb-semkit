"""The markers area: find with each bundled marker list."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

import rb_semkit as sk
from rb_semkit.core.markers import lists


def _markers(name: str) -> Callable[[pd.Series], object]:
    return lambda phrases: sk.find(phrases, sk.markers(name))


DATA_OPERATIONS = {f"markers_{name}": _markers(name) for name in lists.names()}
