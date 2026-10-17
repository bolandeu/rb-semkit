"""The bundled data against the data manifests (`data_manifest/<area>.json`, written by scripts/build_data.py).

Each bundled file, or each table of a JSON file, holds the number of items its area's manifest says; the source count
less the dropped items plus the added ones is that number; every dropped item has its reason; every bundled file is in
the manifest of its area, and every manifest entry is a bundled file. Runs offline: only the package data and the
manifests are read. tests/core/test_build_data.py checks, where the sources are on the machine, that the manifests are
what the build writes.
"""

from __future__ import annotations

from rb_semkit.core import datastore

from .manifests import MANIFEST_DIR, mismatches


def test_the_package_data_holds_what_the_manifests_say() -> None:
    assert mismatches(datastore.DATA_DIR, MANIFEST_DIR) == []
