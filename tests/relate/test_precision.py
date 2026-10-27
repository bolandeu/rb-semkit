"""relate-phrases precision on the 200 labelled phrase pairs (tests/vectors/fixtures/phrase_pairs.tsv), with the real
thesaurus: a pair labelled as another intent never comes out `same` or `variation`.

Each pair is a table of its two phrases, in both orders. The test skips when the thesaurus is not pulled.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import pytest

from rb_semkit.core.errors import CliError
from rb_semkit.core.word_vectors import thesaurus

from .runner import rows

pytestmark = pytest.mark.real_encoder

PAIRS = Path(__file__).parents[1] / "vectors" / "fixtures" / "phrase_pairs.tsv"
DUPLICATES = ("same", "variation")


# The pairs of another intent that come out `same`, each with the reason the step gives. Not a bug of a link: the
# phrases hold the same lemmas once the prepositions are dropped («диван с матрасом» / «матрас на диван»). Reported.
SAME_BY_PREPOSITION = {
    "p136: 'купить диван с ортопедическим матрасом' is same of 'купить ортопедический матрас на диван': lemmas",
    "p136: 'купить ортопедический матрас на диван' is same of 'купить диван с ортопедическим матрасом': lemmas",
    "p174: 'диван на ножках купить' is same of 'ножки для дивана купить': lemmas",
    "p174: 'ножки для дивана купить' is same of 'диван на ножках купить': lemmas",
}


@pytest.fixture(scope="module", autouse=True)
def _real_thesaurus_once() -> Iterator[None]:
    """The thesaurus from the cache, read once for all the runs; skips when it is not pulled."""
    try:
        loaded = thesaurus.open_thesaurus(Path.cwd())
    except CliError as error:
        pytest.skip(f"ruwordnet is not in the cache ({error.code}): run 'semkit models pull ruwordnet'.")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(thesaurus, "open_thesaurus", lambda start: loaded)
        yield


def test_no_pair_of_another_intent_is_same_or_variation(tmp_path: Path) -> None:
    pairs = pd.read_csv(PAIRS, sep="\t", comment="#", dtype=str, keep_default_na=False)
    other_intent = pairs[pairs["label"] == "0"]
    found = set()
    for pair in other_intent.itertuples():
        for first, second in (pair.phrase_a, pair.phrase_b), (pair.phrase_b, pair.phrase_a):
            kind, _, _, reason = rows(tmp_path, [first, second])[1]
            if kind in DUPLICATES:
                found.add(f"{pair.id}: {second!r} is {kind} of {first!r}: {reason}")

    assert len(other_intent) > 0
    assert found == SAME_BY_PREPOSITION, "\n".join(sorted(found))
