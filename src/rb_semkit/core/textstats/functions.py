"""text_stats: the metrics of each text of a table, one row per text."""

from __future__ import annotations

import math
from collections import Counter

import pandas as pd

from ..analysis.frequency import bundled_stopwords
from ..frame import Frame, map_unique
from ..morph import Lemmatizer
from ..morph.functions import BUNDLED
from ..normalize import norm_phrase
from ..text.words import has_lemma, text_words
from .metrics import mtld, zipf

COLUMNS = [
    "chars",
    "chars_no_spaces",
    "words",
    "unique",
    "water",
    "nausea_classic",
    "nausea_academic",
    "top",
    "ttr",
    "mtld",
    "zipf",
]


def _metrics(text: str, lemma_of: dict[str, str], stopwords: frozenset[str]) -> list:
    keys = [norm_phrase(word) for word in text_words(text)]
    content = [key for key in keys if key not in stopwords]
    lemmas = [lemma_of[key] for key in content if has_lemma(key)]
    counts = Counter(lemmas)
    top = max(counts, key=counts.__getitem__) if counts else ""
    biggest = counts[top] if counts else 0
    return [
        len(text),
        len("".join(text.split())),
        len(keys),
        len({lemma_of[key] for key in content}),
        (len(keys) - len(content)) / len(keys) if keys else 0.0,
        round(math.sqrt(biggest), 2),
        biggest / len(keys) if keys else 0.0,
        top,
        len(counts) / len(lemmas) if lemmas else 0.0,
        mtld(lemmas),
        zipf(list(counts.values())),
    ]


def text_stats(
    data: pd.Series | pd.DataFrame,
    *,
    lemmatizer: Lemmatizer = BUNDLED,
    column: str | None = None,
) -> pd.DataFrame:
    """The usual SEO metrics of each text, the same numbers each run: a table with the input index, a row per text.

    A cell is a text; an empty cell (None, NaN, "") gives zeros and an empty `top`. With a DataFrame and `column=`
    the metric columns are added right after `column` to your table, which is returned.

    Words: the punctuation of sk.chars('punctuation') is dropped (a hyphen between two word characters stays,
    «кресло-кровать» is one word), the rest splits on whitespace, case and ё are folded. Stopwords are the bundled
    list of the n-grams. Lemmas are the words that are no stopwords, by `lemmatizer`. A unit without a meaning
    (руб, рублей, шт, см, мм, мл, кг, кв, стр, ул) is a word but no lemma for top, nausea, ttr, mtld and zipf.
    Columns, in this order:
    chars: all characters of the text. chars_no_spaces: the same without whitespace.
    words: the words of the text, stopwords and units included.
    unique: distinct lemmas of the words that are no stopwords (units included).
    water: stopwords / words, 0..1.
    nausea_classic: the square root of the count of the most frequent lemma (the top), 2 decimals.
    nausea_academic: that count / words, 0..1.
    top: that lemma; on a tie, the first in the text.
    ttr: distinct lemmas / lemmas, 0..1 (lemmas as above: no stopwords, no units).
    mtld: Measure of Textual Lexical Diversity (McCarthy and Jarvis 2010), threshold 0.72. Read the lemmas forward:
    each time the running type/token ratio falls to 0.72 or below, count a factor and restart; the last partial run
    adds (1 - ttr) / (1 - 0.72). Do it backward too; mtld = lemmas / mean of the two factor counts, 2 decimals;
    0 for under 2 lemmas.
    zipf: R² x 100, 1 decimal, of the linear regression of log count on log rank over the lemma counts (rank 1 is
    the biggest count), so f(r) = C / r^s fits; 0 for under 5 distinct lemmas.
    No norms and no verdicts: the caller sets them.
    """
    frame = Frame(data, column)
    texts, stopwords = frame.phrases, bundled_stopwords()
    words = {norm_phrase(word) for text in texts.unique() for word in text_words(text)}
    lemma_of = {word: lemmatizer.lemma(word) for word in words - stopwords}
    rows = map_unique(texts, lambda text: _metrics(text, lemma_of, stopwords))
    table = pd.DataFrame(rows.tolist(), columns=COLUMNS, index=texts.index)
    if isinstance(data, pd.Series):
        return table
    for position, name in enumerate(COLUMNS, data.columns.get_loc(column) + 1):
        if name in data.columns:
            data[name] = table[name]
        else:
            data.insert(position, name, table[name])
    return data
