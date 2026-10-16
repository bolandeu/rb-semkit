"""The text core: the Matcher protocol, the three verbs and the pipe (ADR 0004); matchers live in `matchers/`."""

from .base import Matcher, extract, find, pipe, remove

__all__ = ["Matcher", "extract", "find", "pipe", "remove"]
