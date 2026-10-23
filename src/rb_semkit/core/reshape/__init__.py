"""Bricks that change the shape of a table: group rows into one, cut a cell into rows, turn columns into rows."""

from .functions import group_rows, split_rows, unpivot

__all__ = ["group_rows", "split_rows", "unpivot"]
