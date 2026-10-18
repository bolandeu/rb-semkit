"""compare_grams: the density of each gram of the competitors' texts against mine, and how many occurrences to add."""

from __future__ import annotations

from collections.abc import Iterable
from functools import partial

import numpy as np
import pandas as pd

from ..analysis.frequency import checked_n
from ..textstats.skip import Skip
from .shared import DECIMALS, Norm, TextCounts, checked_norm, checked_number, checked_text, texts_of, verdicts, whole

COLUMNS = [
    "ngram", "docs", "docs_share", "median", "mean", "min", "max", "mine", "verdict", "need", "have", "add", "med_count",
]  # fmt: skip
URL = "url"


def _names(competitors: object, column: str | None, count: int) -> list[str]:
    """The names of the density columns of `--per-text`: the url column of a table of competitors, else text_1…"""
    if isinstance(competitors, pd.DataFrame) and URL in competitors.columns and column != URL:
        return competitors[URL].astype(str).tolist()
    return [f"text_{number}" for number in range(1, count + 1)]


def _rounded_half_up(values: pd.Series) -> pd.Series:
    return np.floor(values + 0.5).astype("int64")


def compare_grams(
    mine: str,
    competitors: pd.Series | pd.DataFrame | list[str],
    *,
    n: int = 1,
    lemmas: bool = True,
    stopwords: bool = False,
    tolerance: float = 0.3,
    column: str | None = None,
    norm: Norm = "median",
    words: int | None = None,
    per_text: bool = False,
    no_digits: bool = False,
    exclude: Iterable[str] = (),
) -> pd.DataFrame:
    """How the grams of my text differ from the competitors' texts: a row per gram met in any competitor.

    mine: my text, one text.
    competitors: the texts of the competitors, one per row.

    The density of a gram in a text is its count / the words of that text; a competitor without the gram counts as 0.
    Grams are those of ngrams. With lemmas, a word without a lemma (a single letter, an abbreviation or a unit: «г»,
    «руб», «см») is in no gram, but counts in the words of a text.
    n: how many words in a gram.
    lemmas: compare lemmas of the words («диваны» is «диван»).
    stopwords: on, every word makes grams; off (the default), only the words that are no stopwords.
    tolerance: how far from the norm a density is still within, a share of the norm (0.3 is ±30 %).
    norm: «median» (the default) or «mean»: the density the verdict and the recommended occurrences go by.
    words: the size of the text to recommend occurrences for, in words; by default the words of my text.
    per_text: add a density column per competitor text, named by its url column when the table of the competitors has
    one, else text_1, text_2…
    no_digits: leave out the words with a digit of every count, the words total included, as text-stats does.
    exclude: words to leave out of every count the same way, as written, with case and ё folded, not by lemma.

    The columns: ngram; docs, the competitors that hold it; docs_share, docs / competitors, 0..1; median, mean, min,
    max, the density in the competitors; mine, its density in my text; verdict, «below», «within» or «above», mine
    against norm x (1 ± tolerance), and when the norm is 0, «within» if mine is 0, else «above»; need, the norm x
    `words`, rounded to a whole number of occurrences; have, the occurrences in my text; add, need - have (negative:
    remove); med_count, the median number of occurrences in the competitors. Densities are rounded to 4 decimals.
    Sorted by median, biggest first, then ngram. With per_text, the density columns come last.

    Example: {cli} read --whole mine.txt compare-grams competitors.csv -n 3 write -
    -> диван кожаный диван, 1, 0.3333, 0.0, 0.0476, 0.0, 0.1429, 0.0, within, 0, 0, 0, 0; диван угловой кресло, 1, 0.3333, 0.0, 0.0476, 0.0, 0.1429, 0.0, within, 0, 0, 0, 0; кожаный диван угловой, 1, 0.3333, 0.0, 0.0476, 0.0, 0.1429, 0.0, within, 0, 0, 0, 0; купить диван недорогой, 1, 0.3333, 0.0, 0.0476, 0.0, 0.1429, 0.0, within, 0, 0, 0, 0
    """
    text, others = checked_text(mine), texts_of(competitors, column, "competitors")
    limit, chosen = checked_number(tolerance, "tolerance"), checked_norm(norm)
    counts = partial(TextCounts, n=checked_n(n), lemmas=lemmas, stopwords=stopwords, skip=Skip.of(no_digits, exclude))
    found, mine_counts = [counts(other) for other in others], counts(text)
    density = pd.concat([one.density for one in found], axis=1).fillna(0)
    held = pd.concat([one.counts for one in found], axis=1).fillna(0)
    own = mine_counts.density.reindex(density.index, fill_value=0)
    size = mine_counts.words if words is None else checked_number(words, "words")
    median, mean = density.median(axis=1), density.mean(axis=1)
    target = median if chosen == "median" else mean
    need, have = _rounded_half_up(target * size), mine_counts.counts.reindex(density.index, fill_value=0)
    middle = held.median(axis=1)
    docs = (density > 0).sum(axis=1)
    table = pd.DataFrame(
        {
            "ngram": density.index,
            "docs": docs.to_numpy(),
            "docs_share": (docs / len(others)).round(DECIMALS).to_numpy(),
            "median": median.round(DECIMALS).to_numpy(),
            "mean": mean.round(DECIMALS).to_numpy(),
            "min": density.min(axis=1).round(DECIMALS).to_numpy(),
            "max": density.max(axis=1).round(DECIMALS).to_numpy(),
            "mine": own.round(DECIMALS).to_numpy(),
            "verdict": verdicts(own, target, limit).to_numpy(),
            "need": need.to_numpy(),
            "have": have.astype("int64").to_numpy(),
            "add": (need - have).astype("int64").to_numpy(),
            "med_count": middle.map(whole).astype(object).to_numpy(),
        },
        columns=COLUMNS,
    )
    if per_text:
        names = _names(competitors, column, len(others))
        table = pd.concat([table, pd.DataFrame(density.round(DECIMALS).to_numpy(), columns=names)], axis=1)
    return table.sort_values(["median", "ngram"], ascending=[False, True]).reset_index(drop=True)
