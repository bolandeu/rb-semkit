"""find-pos through the command line follows the dictionary correction of the parts of speech."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..pipeline.runner import jsonl, semkit


def test_find_pos_takes_luchshe_for_no_noun_and_pokryvalo_for_no_verb(tmp_path: Path) -> None:
    core = tmp_path / "core.csv"
    pd.DataFrame({"phrase": ["лучше", "покрывало на диван"]}).to_csv(core, index=False)

    nouns = semkit("read", str(core), "find-pos", "noun", "write", "-")
    verbs = semkit("read", str(core), "find-pos", "verb", "write", "-")

    assert nouns.exit_code == 0, nouns.output
    assert [row["phrase_find"] for row in jsonl(nouns.stdout)] == [False, True]
    assert [row["phrase_find"] for row in jsonl(verbs.stdout)] == [False, False]
