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


def test_an_against_table_of_parse_html_output_uses_the_column_text(core_csv: Path) -> None:
    against = _against(
        core_csv.parent, html=["<p>x</p>"] * 5, url=PAGES["url"], text=PAGES["text"], title=["ковёр"] * 5
    )

    rows = _rows(str(core_csv), "nearest", "--against", str(against))

    assert [row["match"] for row in rows] == ["угловой диван", "кресло кровать недорого", "обеденный стол из дуба"]


def test_an_against_table_without_a_column_text_takes_the_first_text_column_that_is_no_url(core_csv: Path) -> None:
    against = _against(core_csv.parent, url=PAGES["url"], body=PAGES["text"])

    rows = _rows(str(core_csv), "nearest", "--against", str(against))

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


def test_to_gives_the_same_report_as_an_against_file_of_one_row(core_csv: Path) -> None:
    against = _against(core_csv.parent, text=["угловой диван"])

    from_file = _rows(str(core_csv), "nearest", "--against", str(against), "--threshold", "0.5")
    from_text = _rows(str(core_csv), "nearest", "--to", "угловой диван", "--threshold", "0.5")

    assert from_text == from_file
    assert list(from_text[0]) == ["phrase", "match", "rank", "similarity"]
    assert (from_text[0]["phrase"], from_text[0]["match"], from_text[0]["similarity"]) == (
        "угловой диван",
        "угловой диван",
        1.0,
    )


def test_each_to_is_a_text_to_match_and_the_nearest_comes_first(core_csv: Path) -> None:
    rows = _rows(str(core_csv), "nearest", "--to", "кресло кровать недорого", "--to", "угловой диван", "--top", "2")

    assert len(rows) == 6
    assert [row["rank"] for row in rows] == [1, 2] * 3
    assert [row["match"] for row in rows[:2]] == ["угловой диван", "кресло кровать недорого"]
    assert [row["match"] for row in rows[2:4]] == ["кресло кровать недорого", "угловой диван"]
    assert all(rows[start]["similarity"] >= rows[start + 1]["similarity"] for start in (0, 2, 4))


def test_to_and_against_together_are_refused_naming_both(core_csv: Path) -> None:
    pages = _against(core_csv.parent, **PAGES)

    result = semkit("read", str(core_csv), "nearest", "--to", "диван", "--against", str(pages), "write", "-")

    assert result.exit_code == 2
    assert "--to" in result.stderr and "--against" in result.stderr


def test_to_and_the_positional_against_together_are_refused_naming_both(core_csv: Path) -> None:
    pages = _against(core_csv.parent, **PAGES)

    result = semkit("read", str(core_csv), "nearest", str(pages), "--to", "диван", "write", "-")

    assert result.exit_code == 2
    assert "--to" in result.stderr and "AGAINST" in result.stderr


def test_neither_to_nor_against_is_refused(core_csv: Path) -> None:
    result = semkit("read", str(core_csv), "nearest", "write", "-")

    assert result.exit_code == 2
    assert "--to" in result.stderr and "AGAINST" in result.stderr
