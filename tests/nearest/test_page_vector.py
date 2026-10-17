"""The page vector: a text longer than the input of the model is cut into pieces the model takes whole and its vector is
the mean of theirs; the title and h1 columns of a table weigh more. Seen through `nearest` and `assign-pages`."""

from __future__ import annotations

import zlib
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from rb_semkit.core.vectors import encoder
from rb_semkit.core.vectors.registry import Model

from ..pipeline.runner import jsonl, semkit

MODEL_INPUT = 512  # the tokens of a text e5-small reads, the default model


class ReadingEncoder:
    """A model that reads only the first 512 words of a text (a word is a token), as a real one cuts its input.

    A text is the normalized sum of its words, each word a fixed vector of length 1 (seeded by the word): a text of
    two words in equal number has the vector of the text of these two words once.
    """

    def encode(self, phrases: Sequence[str]) -> np.ndarray:
        vectors = np.zeros((len(phrases), 64), dtype=np.float32)
        for row, phrase in enumerate(phrases):
            for word in phrase.lower().split()[:MODEL_INPUT]:
                vector = np.random.default_rng(zlib.crc32(word.encode())).standard_normal(64)
                vectors[row] += vector / np.linalg.norm(vector)
        lengths = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.where(lengths == 0, 1, lengths)


@pytest.fixture
def reading_encoder(monkeypatch: pytest.MonkeyPatch) -> None:
    def opened(model: Model, start: Path) -> ReadingEncoder:
        return ReadingEncoder()

    monkeypatch.setattr(encoder, "encoder_for", opened)


@pytest.fixture(autouse=True)
def in_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


def _table(name: str, **columns: list[str]) -> str:
    pd.DataFrame(columns).to_csv(name, index=False)
    return name


def _nearest(core: list[str], *arguments: str) -> list[dict]:
    result = semkit("read", _table("core.csv", phrase=core), "nearest", *arguments, "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


@pytest.mark.usefixtures("reading_encoder")
def test_a_text_longer_than_the_model_input_is_the_mean_of_its_pieces() -> None:
    long = "диван " * 600 + "кресло " * 600  # the model would read only «диван»
    pages = _table("pages.csv", url=["/long", "/short"], text=[long, "диван кресло"])

    rows = _nearest(["кресло"], "--against", pages, "--top", "2")

    similarity = {row["url"]: row["similarity"] for row in rows}
    assert similarity["/short"] > 0.6
    assert similarity["/long"] == pytest.approx(similarity["/short"], abs=0.01)


@pytest.mark.usefixtures("reading_encoder")
@pytest.mark.parametrize("heading", ["title", "h1"])
def test_a_page_whose_heading_matches_the_phrase_ranks_above_one_that_has_it_deep_in_its_text(heading: str) -> None:
    body = "стол " * 300
    pages = _table(
        "pages.csv",
        url=["/deep", "/headed"],
        **{heading: ["", "угловой диван"]},
        text=[body + "угловой диван", body],
    )

    rows = _nearest(["угловой диван"], "--against", pages, "--against-column", "text", "--top", "2")

    assert [row["url"] for row in rows] == ["/headed", "/deep"]
    assert rows[0]["similarity"] > rows[1]["similarity"] > 0


def test_assign_pages_gives_the_same_output_for_short_page_texts() -> None:
    core = _table("core.csv", phrase=["угловой диван", "прямой диван", "кресло кровать"])
    pages = _table(
        "pages.csv",
        url=["/uglovye", "/pryamye", "/kresla"],
        text=[
            "Угловые диваны: угловой диван в гостиную.",
            "Прямые диваны, прямой диван недорого",
            "кресло-кровать и кресло",
        ],
    )

    result = semkit("read", core, "assign-pages", "--pages", pages, "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [  # the output of assign-pages before the page vector
        {"phrase": "угловой диван", "best_page": "/uglovye", "best_similarity": 0.5833, "second_page": "/pryamye",
         "second_similarity": 0.4811},
        {"phrase": "прямой диван", "best_page": "/pryamye", "best_similarity": 0.5038, "second_page": "/uglovye",
         "second_similarity": 0.2546},
        {"phrase": "кресло кровать", "best_page": "/kresla", "best_similarity": 0.3409, "second_page": "/pryamye",
         "second_similarity": 0.0468},
    ]  # fmt: skip


@pytest.mark.usefixtures("reading_encoder")
def test_assign_pages_takes_the_page_vector_of_a_long_text() -> None:
    core = _table("core.csv", phrase=["кресло"])
    long = "диван " * 600 + "кресло " * 600
    pages = _table("pages.csv", url=["/long", "/tables"], text=[long, "стол"])

    result = semkit("read", core, "assign-pages", "--pages", pages, "write", "-")

    assert result.exit_code == 0, result.output
    row = jsonl(result.stdout)[0]
    assert (row["best_page"], row["best_similarity"] > 0.6) == ("/long", True)
