"""Morphology: lemmas, parts of speech and wordforms (ADR 0003)."""

from .functions import lemmatize, part_of_speech, wordforms
from .lemmatizer import Lemmatizer, SemtoolsLemmatizer

__all__ = ["Lemmatizer", "SemtoolsLemmatizer", "lemmatize", "part_of_speech", "wordforms"]
