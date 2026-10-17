"""A text against competitor texts: gram density, metrics and BM25 against the competitors' median."""

from .bm25 import bm25
from .grams import compare_grams
from .stats import compare_stats

__all__ = ["bm25", "compare_grams", "compare_stats"]
