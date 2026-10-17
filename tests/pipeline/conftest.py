"""Shared input of the pipeline tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from .runner import CORE


@pytest.fixture
def core_csv(tmp_path: Path) -> Path:
    path = tmp_path / "core.csv"
    pd.DataFrame({"phrase": CORE, "freq": ["5", "4", "3", "2", "1"]}).to_csv(path, index=False)
    return path
