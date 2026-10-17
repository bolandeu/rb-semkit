"""`nearest` in a pipeline: each row of the working table gets the top rows of --against by meaning, in a long report
of the phrase, the match, its rank, its similarity and the url of the match."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from ..pipeline.runner import jsonl, semkit

CORE = ["угловой диван", "кресло кровать", "стол обеденный"]
PAGES = {
    "url": ["/uglovye", "/pryamye", "/kresla", "/stoly", "/shkafy"],
    "text": ["угловой диван", "прямой диван", "кресло кровать недорого", "обеденный стол из дуба", "шкаф купе"],
}


@pytest.fixture
def core_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "core.csv"
    pd.DataFrame({"phrase": CORE, "freq": [3, 2, 1]}).to_csv(path, index=False)
    return path


def _against(tmp_path: Path, **columns: list[str]) -> Path:
    path = tmp_path / "pages.csv"
    pd.DataFrame(columns).to_csv(path, index=False)
    return path


def _rows(*arguments: str) -> list[dict]:
    result = semkit("read", *arguments, "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


def test_top_3_gives_three_ranked_matches_per_phrase_with_their_urls(core_csv: Path) -> None:
    pages = _against(core_csv.parent, **PAGES)

    rows = _rows(str(core_csv), "nearest", "--against", str(pages), "--top", "3")

    assert len(rows) == 9
    assert list(rows[0]) == ["phrase", "match", "rank", "similarity", "url"]
    assert [row["phrase"] for row in rows] == [phrase for phrase in CORE for _ in range(3)]
    assert [row["rank"] for row in rows] == [1, 2, 3] * 3
    for start in (0, 3, 6):
        similarities = [row["similarity"] for row in rows[start : start + 3]]
        assert similarities == sorted(similarities, reverse=True)
    assert (rows[0]["match"], rows[0]["similarity"], rows[0]["url"]) == ("угловой диван", 1.0, "/uglovye")
    assert rows[1]["match"] == "прямой диван"
    assert (rows[3]["match"], rows[3]["url"]) == ("кресло кровать недорого", "/kresla")
    assert (rows[6]["match"], rows[6]["url"]) == ("обеденный стол из дуба", "/stoly")
    url_of = dict(zip(PAGES["text"], PAGES["url"], strict=True))
    assert all(row["url"] == url_of[row["match"]] for row in rows)


def test_the_default_top_is_one_match_per_phrase(core_csv: Path) -> None:
    pages = _against(core_csv.parent, **PAGES)

    rows = _rows(str(core_csv), "nearest", "--against", str(pages))

    assert [(row["phrase"], row["match"], row["rank"]) for row in rows] == [
        ("угловой диван", "угловой диван", 1),
        ("кресло кровать", "кресло кровать недорого", 1),
        ("стол обеденный", "обеденный стол из дуба", 1),
    ]


def test_an_against_table_without_a_url_column_gives_no_url_column(core_csv: Path) -> None:
    against = _against(core_csv.parent, phrase=PAGES["text"])

    rows = _rows(str(core_csv), "nearest", "--against", str(against))

    assert list(rows[0]) == ["phrase", "match", "rank", "similarity"]


def test_against_column_names_the_column_of_the_texts(core_csv: Path) -> None:
    against = _against(core_csv.parent, url=PAGES["url"], title=["диван"] * 5, text=PAGES["text"])

    rows = _rows(str(core_csv), "nearest", "--against", str(against), "--against-column", "text")

    assert [row["match"] for row in rows] == ["угловой диван", "кресло кровать недорого", "обеденный стол из дуба"]


def test_a_phrase_whose_matches_are_all_below_the_threshold_keeps_one_row_with_an_empty_match(core_csv: Path) -> None:
    pages = _against(core_csv.parent, **PAGES)

    rows = _rows(str(core_csv), "nearest", "--against", str(pages), "--top", "3", "--threshold", "0.9")

    assert [(row["phrase"], row["match"], row["rank"]) for row in rows] == [
        ("угловой диван", "угловой диван", 1),
        ("кресло кровать", "", None),
        ("стол обеденный", "", None),
    ]
    assert rows[1]["similarity"] is None and rows[1]["url"] in ("", None)


@pytest.mark.parametrize(
    ("arguments", "named"),
    [
        (["--against", "pages.csv", "--top", "0"], "--top"),
        (["--against", "nosuch.csv"], "--against nosuch.csv"),
        (["--against", "pages.csv", "--against-column", "body"], "--against-column"),
    ],
)
def test_a_wrong_option_is_refused_naming_it(core_csv: Path, arguments: list[str], named: str) -> None:
    _against(core_csv.parent, **PAGES)

    result = semkit("read", str(core_csv), "nearest", *arguments, "write", "-")

    assert result.exit_code == 2
    assert named in result.stderr
