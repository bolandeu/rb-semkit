"""Public names are found in the area modules: a module of an area declares them in `__all__`, the root finds them.

Each test runs a fresh interpreter: it adds a temporary folder to the path of `rb_semkit.core`, so the area modules the
test writes there count as areas of the package.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

PROBE = """
import json, sys
import rb_semkit as sk
import rb_semkit.core as core
core.__path__.append(sys.argv[1])
loaded = lambda: sorted(m for m in sys.modules if m.startswith("rb_semkit.core.") and m.count(".") >= 2)
before = loaded()
try:
    value = getattr(sk, sys.argv[2])
    result = {"value": value() if callable(value) else value, "listed": sys.argv[2] in dir(sk)}
except Exception as error:
    result = {"error": f"{type(error).__name__}: {error}"}
print(json.dumps({"before": before, **result}))
"""


def _write(root: Path, files: dict[str, str]) -> Path:
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def _probe(root: Path, name: str) -> dict:
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", PROBE, str(root), name], capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def test_a_new_area_module_is_reachable_by_its_declared_name(tmp_path: Path) -> None:
    root = _write(
        tmp_path,
        {
            "zarea/__init__.py": '"""A temporary area."""\n',
            "zarea/greet.py": '__all__ = ["greet"]\n\n\ndef greet():\n    return "hello"\n',
        },
    )

    probe = _probe(root, "greet")

    assert probe["value"] == "hello"
    assert probe["listed"] is True


def test_importing_the_package_loads_no_area_module(tmp_path: Path) -> None:
    probe = _probe(tmp_path, "nope")

    assert probe["before"] == []


def test_a_name_the_module_does_not_declare_is_not_public(tmp_path: Path) -> None:
    root = _write(tmp_path, {"zarea/__init__.py": "", "zarea/greet.py": "def greet():\n    return 'hello'\n"})

    probe = _probe(root, "greet")

    assert probe["error"].startswith("AttributeError")


def test_a_name_declared_by_two_modules_is_an_error_naming_both(tmp_path: Path) -> None:
    module = '__all__ = ["greet"]\n\n\ndef greet():\n    return "hello"\n'
    root = _write(tmp_path, {"zarea/__init__.py": "", "zarea/one.py": module, "zarea/two.py": module})

    probe = _probe(root, "greet")

    assert probe["error"].startswith("ImportError")
    assert "rb_semkit.core.zarea.one" in probe["error"]
    assert "rb_semkit.core.zarea.two" in probe["error"]


def test_dir_lists_the_public_names_and_no_import_of_the_root() -> None:
    code = "import json, rb_semkit as sk; print(json.dumps(dir(sk)))"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)  # noqa: S603
    listed = json.loads(result.stdout)

    assert {"InvalidArguments", "ngrams", "bigrams", "counts"} <= set(listed)
    assert not {"ast", "functools", "importlib", "Path", "Any", "annotations"} & set(listed)
    assert listed == sorted(listed)


def test_no_module_outside_analysis_imports_a_private_name_of_analysis() -> None:
    source = Path(__file__).parents[2] / "src" / "rb_semkit"
    pattern = re.compile(r"from\s+(?:\.+|rb_semkit\.core\.)analysis[\w.]*\s+import\s+\(?[^)\n]*\b_\w+")
    found = [
        path.name
        for path in source.rglob("*.py")
        if "analysis" not in path.relative_to(source).parts and pattern.search(path.read_text(encoding="utf-8"))
    ]

    assert found == []
