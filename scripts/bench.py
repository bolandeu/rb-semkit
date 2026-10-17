#!/usr/bin/env python3
"""Time the heavy operations of the library on a big semantic core (default 1M phrases).

    uv run scripts/bench.py [--rows 1000000] [--ops dupes,ngrams,lemmatize,...] [--limit 120] [--load-limit 0.5]
                            [--input core.csv] [--parts scripts/bench_parts]

The operations come from the benchmark parts, one per area (`<area>.py` of the parts folder, the contract in
scripts/bench_parts/__init__.py). The phrases are synthetic (words of the bundled dictionary, a fixed seed) or, with
--input, the `phrase` column of a CSV (a real core exported from Bukvarix). When --rows is larger than the file, its
phrases are repeated with the words shuffled, so the duplicate search still has work. The data-backed operations first
run on one phrase: that run loads their data and is timed as `load`. Prints one line per operation and exits 1 when
one takes longer than --limit seconds, or its load longer than --load-limit.
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from collections.abc import Callable
from itertools import accumulate
from pathlib import Path
from typing import NamedTuple

import pandas as pd

from rb_semkit.core import datastore

sys.path.insert(0, str(Path(__file__).resolve().parent))

from area_parts import load_parts

SEED = 20261016
VOCABULARY = 5000  # distinct words of the synthetic core; the draw is skewed so common words repeat
MAX_WORDS = 5
DEFAULT_ROWS = 1_000_000
DEFAULT_LIMIT = 120.0
DEFAULT_LOAD_LIMIT = 0.5
DEFAULT_PARTS = Path(__file__).resolve().parent / "bench_parts"


class Operation(NamedTuple):
    run: Callable[[pd.Series], object]
    data_backed: bool


def operations(folder: Path) -> dict[str, Operation]:
    """The operations of every benchmark part of `folder`, by name."""
    found = {}
    for part in load_parts(folder).values():
        found |= {name: Operation(run, False) for name, run in getattr(part, "OPERATIONS", {}).items()}
        found |= {name: Operation(run, True) for name, run in getattr(part, "DATA_OPERATIONS", {}).items()}
    return found


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


def _arguments(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS, help="number of phrases")
    parser.add_argument("--ops", default="", help="comma-separated operations (default: all)")
    parser.add_argument("--limit", type=float, default=DEFAULT_LIMIT, help="seconds an operation may take")
    parser.add_argument(
        "--load-limit", type=float, default=DEFAULT_LOAD_LIMIT, help="seconds the first load of its data may take"
    )
    parser.add_argument("--input", type=Path, default=None, help="CSV with the column 'phrase' instead of synthetic")
    parser.add_argument("--parts", type=Path, default=DEFAULT_PARTS, help="the benchmark parts directory")
    args = parser.parse_args(argv)
    args.operations = operations(args.parts)
    args.ops = [name.strip() for name in args.ops.split(",") if name.strip()] or list(args.operations)
    unknown = [name for name in args.ops if name not in args.operations]
    if unknown:
        parser.error(f"--ops: {unknown!r}; allowed: {', '.join(args.operations)}")
    return args


def _seconds(run: Callable[[pd.Series], object], phrases: pd.Series) -> float:
    started = time.perf_counter()
    run(phrases)
    return time.perf_counter() - started


def _time(operation: Operation, phrases: pd.Series) -> tuple[float, float]:
    """Seconds of the first run on one phrase (the load of the data) and of the run."""
    load = _seconds(operation.run, phrases.iloc[:1]) if operation.data_backed else 0.0
    return load, _seconds(operation.run, phrases)


def main(argv: list[str] | None = None) -> int:
    args = _arguments(argv)
    phrases = pd.Series(build_phrases(args.rows, args.input))
    slow = []
    print(f"{'operation':<20}{'rows':>10}{'load':>10}{'seconds':>10}  status")
    for name in args.ops:
        load, seconds = _time(args.operations[name], phrases)
        too_slow = seconds > args.limit or load > args.load_limit
        print(f"{name:<20}{len(phrases):>10}{load:>10.3f}{seconds:>10.2f}  {'SLOW' if too_slow else 'ok'}")
        if too_slow:
            slow.append(name)
    if slow:
        limits = f"{args.limit:g} s, load {args.load_limit:g} s"
        print(f"bench: over the limit of {limits}: {', '.join(slow)}", file=sys.stderr)
    return 1 if slow else 0


if __name__ == "__main__":
    sys.exit(main())
