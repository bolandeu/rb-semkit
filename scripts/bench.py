#!/usr/bin/env python3
"""Time the heavy operations of the library on a big semantic core (default 1M phrases).

    uv run scripts/bench.py [--rows 1000000] [--ops dupes,ngrams,ngrams_lemmas,lemmatize] [--limit 120] [--input core.csv]

The phrases are synthetic (words of the bundled dictionary, a fixed seed) or, with --input, the `phrase` column of a
CSV (a real core exported from Bukvarix). When --rows is larger than the file, its phrases are repeated with the
words shuffled, so the duplicate search still has work. Prints one line per operation and exits 1 when one takes
longer than --limit seconds. An operation whose module is not in the library yet is skipped.
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from collections.abc import Callable
from itertools import accumulate
from pathlib import Path

import pandas as pd

import rb_semkit as sk
from rb_semkit.core import datastore

SEED = 20261016
VOCABULARY = 5000  # distinct words of the synthetic core; the draw is skewed so common words repeat
MAX_WORDS = 5
DEFAULT_ROWS = 1_000_000
DEFAULT_LIMIT = 120.0
DUPE_KINDS = ("exact", "explicit", "implicit", "lemmas")


class ModuleMissing(Exception):
    """The operation needs a library module that is not there yet."""


def synthetic_phrases(rows: int, rng: random.Random) -> list[str]:
    words = rng.sample(sorted(datastore.trie("morph/lemmas.marisa").keys()), VOCABULARY)
    cumulative = list(accumulate(1 / (rank + 1) for rank in range(len(words))))
    return [" ".join(rng.choices(words, cum_weights=cumulative, k=rng.randint(1, MAX_WORDS))) for _ in range(rows)]


def file_phrases(rows: int, source: Path, rng: random.Random) -> list[str]:
    """The first `rows` phrases of the file; past its end, the same phrases again with their words shuffled."""
    phrases = pd.read_csv(source, usecols=["phrase"], dtype=str)["phrase"].dropna().tolist()
    if not phrases:
        raise SystemExit(f"bench: {source} holds no phrases in the column 'phrase'")
    result = phrases[:rows]
    while len(result) < rows:
        for phrase in phrases[: rows - len(result)]:
            words = phrase.split()
            rng.shuffle(words)
            result.append(" ".join(words))
    return result


def build_phrases(rows: int, source: Path | None) -> list[str]:
    rng = random.Random(SEED)  # noqa: S311  # a fixed seed for repeatable data, not a secret
    return synthetic_phrases(rows, rng) if source is None else file_phrases(rows, source, rng)


def _dupes(phrases: pd.Series) -> None:
    try:
        dupes = sk.dupes
    except AttributeError as error:
        raise ModuleMissing from error
    for kind in DUPE_KINDS:
        dupes(phrases, kind=kind, action="mark_except_first")


OPERATIONS: dict[str, Callable[[pd.Series], object]] = {
    "dupes": _dupes,
    "ngrams": lambda phrases: sk.ngrams(phrases),
    "ngrams_lemmas": lambda phrases: sk.ngrams(phrases, lemmas=True, lemmatizer=sk.SemtoolsLemmatizer()),
    "lemmatize": lambda phrases: sk.lemmatize(phrases, lemmatizer=sk.SemtoolsLemmatizer()),
}


def _operation_list(text: str) -> list[str]:
    names = [name.strip() for name in text.split(",") if name.strip()]
    unknown = [name for name in names if name not in OPERATIONS]
    if unknown or not names:
        raise argparse.ArgumentTypeError(f"{unknown or text!r}; allowed: {', '.join(OPERATIONS)}")
    return names


def _arguments(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS, help="number of phrases")
    parser.add_argument("--ops", type=_operation_list, default=list(OPERATIONS), help="comma-separated operations")
    parser.add_argument("--limit", type=float, default=DEFAULT_LIMIT, help="seconds an operation may take")
    parser.add_argument("--input", type=Path, default=None, help="CSV with the column 'phrase' instead of synthetic")
    return parser.parse_args(argv)


def _time(name: str, phrases: pd.Series) -> float | None:
    """Seconds the operation takes; None when its module is missing."""
    started = time.perf_counter()
    try:
        OPERATIONS[name](phrases)
    except ModuleMissing:
        return None
    return time.perf_counter() - started


def main(argv: list[str] | None = None) -> int:
    args = _arguments(argv)
    phrases = pd.Series(build_phrases(args.rows, args.input))
    slow = []
    print(f"{'operation':<16}{'rows':>10}{'seconds':>10}  status")
    for name in args.ops:
        seconds = _time(name, phrases)
        if seconds is None:
            print(f"{name:<16}{len(phrases):>10}{'-':>10}  skipped (module not present yet)")
            continue
        too_slow = seconds > args.limit
        print(f"{name:<16}{len(phrases):>10}{seconds:>10.2f}  {'SLOW' if too_slow else 'ok'}")
        if too_slow:
            slow.append(name)
    if slow:
        print(f"bench: over the limit of {args.limit:g} s: {', '.join(slow)}", file=sys.stderr)
    return 1 if slow else 0


if __name__ == "__main__":
    sys.exit(main())
