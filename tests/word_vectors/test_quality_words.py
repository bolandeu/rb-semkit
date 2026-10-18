"""The synonym candidates on 100 labelled word pairs (checked by the Human): of the pairs a source proposes, the
share the Human labelled a synonym usable in a query is not below the measured one minus 0.05.

The measured shares are RuWordNet 0.32 and navec 0.18 (docs/plans/vectors.md). The test runs the real data from the
cache; without it, it is skipped with the command that pulls it.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from rb_semkit.core.errors import CliError
from rb_semkit.core.morph.functions import BUNDLED
from rb_semkit.core.normalize import norm_phrase
from rb_semkit.core.word_vectors.candidates import synonym_candidates
from rb_semkit.core.word_vectors.navec import open_word_vectors
from rb_semkit.core.word_vectors.thesaurus import open_thesaurus

pytestmark = pytest.mark.real_encoder

PAIRS = Path(__file__).parents[1] / "vectors" / "fixtures" / "word_pairs.tsv"
MEASURED = {"ruwordnet": 0.32, "navec": 0.18}
MARGIN = 0.05


def _lemma(word: str) -> str:
    return norm_phrase(BUNDLED.lemma(norm_phrase(word)))


@pytest.fixture(scope="module")
def proposals() -> tuple[pd.DataFrame, pd.DataFrame]:
    """The labelled pairs, and the candidates of every word of the pairs from the real data."""
    try:
        thesaurus, word_vectors = open_thesaurus(Path.cwd()), open_word_vectors(Path.cwd())
    except CliError as error:
        pytest.skip(f"the word data is not in the cache ({error.code}): run '{error.action}'.")
    pairs = pd.read_csv(PAIRS, sep="\t", comment="#")
    found = synonym_candidates(pairs["word_a"], thesaurus=thesaurus, word_vectors=word_vectors, all=True)
    return pairs, found


@pytest.mark.parametrize("source", list(MEASURED))
def test_the_share_of_right_proposals_is_not_below_the_measured_one(
    proposals: tuple[pd.DataFrame, pd.DataFrame], source: str
) -> None:
    pairs, found = proposals
    proposed = set(map(tuple, found.loc[found["source"] == source, ["word", "candidate"]].to_numpy()))
    made = pairs[[(_lemma(a), _lemma(b)) in proposed for a, b in zip(pairs["word_a"], pairs["word_b"], strict=True)]]

    assert len(made) > 0
    assert made["label"].mean() >= MEASURED[source] - MARGIN
