"""The corpus area: clustering by the frequency dictionary, basis phrases, parents and children against the core
itself, and typos learnt from the core."""

from __future__ import annotations

import rb_semkit as sk

OPERATIONS = {
    "cluster_by_frequency": lambda phrases: sk.cluster_by_frequency(phrases, threshold=2),
    "basis_phrases": lambda phrases: sk.basis_phrases(phrases),
    "nearest_parents": lambda phrases: sk.nearest_parents(phrases, phrases),
    "first_children": lambda phrases: sk.first_children(phrases, phrases),
    "is_typo": lambda phrases: sk.is_typo(phrases),
}
