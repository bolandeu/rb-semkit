"""The benchmark parts of scripts/bench.py, one per area (`<area>.py`).

A part names the operations of its area, each a function of a Series of phrases, in up to two dicts:

    OPERATIONS        timed on the whole core
    DATA_OPERATIONS   data-backed: first run on one phrase, which loads their data and is timed as `load`

Every operation runs within the budgets of the bench (--limit, --load-limit). A file whose name starts with «_» is
not a part.
"""
