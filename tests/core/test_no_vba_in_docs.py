"""No docstring of the package names the add-in's VBA (ADR 0006): docstrings describe the behaviour in user terms.

A docstring of a module, a class or a function under src/rb_semkit must not hold the word VBA, the VBA module name, an
obfuscated handler name (latin a, k, o mixed with «·», «—», «–», as `—k—k` or `a·–·`) or a line reference («L1194»,
«line 2218»). The VBA references stand in the notes of the conformance case files.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[2] / "src" / "rb_semkit"
VBA_NAMED = re.compile(r"\bVBA\b|RibbonCallbacks|\bL\d+\b|\blines? \d+|[ako·—–]*(?:[ako][·—–]|[·—–][ako]|·)[ako·—–]*")
CASE_HEADERS = Path(__file__).resolve().parents[1] / "conformance" / "cases"
DOCUMENTED = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def _docstrings(path: Path) -> dict[str, str]:
    """Each docstring of the module, by the name of what it documents."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, DOCUMENTED) and (doc := ast.get_docstring(node)):
            found[getattr(node, "name", path.stem)] = doc
    return found


@pytest.mark.parametrize("path", sorted(PACKAGE.rglob("*.py")), ids=lambda path: path.relative_to(PACKAGE).as_posix())
def test_no_docstring_names_the_vba(path: Path) -> None:
    named = {name: VBA_NAMED.findall(doc) for name, doc in _docstrings(path).items() if VBA_NAMED.search(doc)}

    assert named == {}


def test_the_pattern_finds_each_kind_of_vba_reference() -> None:
    examples = ["as the VBA does", "RibbonCallbacks.vba", "`—k—k` (line 2218)", "a·–·", "ka–a L1005", "lines 2877–2878"]

    assert [bool(VBA_NAMED.search(text)) for text in examples] == [True] * len(examples)
    assert not VBA_NAMED.search("words — at the start, 1–3 of them, ё = е, «Wi-Fi»")


def test_the_case_file_headers_hold_the_vba_references() -> None:
    headers = [path.read_text(encoding="utf-8").split("\ncase_id\t", 1)[0] for path in CASE_HEADERS.glob("*/*.tsv")]

    assert headers
    assert all("VBA" in header for header in headers)
