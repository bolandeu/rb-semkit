"""scripts/build_data.py on the sandbox sources: re-runnable, byte-identical, the committed data and manifests are its output."""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import marisa_trie  # ty: ignore[unresolved-import]  # a compiled extension without type stubs
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build_data.py"
CONFIG = ROOT / "scripts" / "build_data.toml"
PACKAGE_DATA = ROOT / "src" / "rb_semkit" / "data"
MANIFESTS = ROOT / "tests" / "conformance" / "data_manifest"
BUILT_FILES = (
    "morph/lemmas.marisa",
    "morph/forms.marisa",
    "morph/morph.json",
    "text/lists.json",
    "declension/tables.json",
    "change/translit.json",
    "change/word_order.json",
)
SOURCES = tomllib.loads(CONFIG.read_text())["sources"]
SANDBOX_ABSENT = not all(Path(path).exists() for path in SOURCES.values())

pytestmark = pytest.mark.skipif(SANDBOX_ABSENT, reason="the !SEMTools sandbox sources are not on this machine")


def _build(out: Path, config: Path = CONFIG) -> subprocess.CompletedProcess[str]:
    """The data into `out`, the manifests into `out/manifests`."""
    return subprocess.run(  # noqa: S603
        [
            sys.executable,
            str(SCRIPT),
            "--config",
            str(config),
            "--out",
            str(out),
            "--manifests",
            str(out / "manifests"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("built")
    result = _build(out)
    assert result.returncode == 0, result.stderr
    return out


def test_two_runs_are_byte_identical_and_match_the_package(built: Path, tmp_path: Path) -> None:
    assert _build(tmp_path).returncode == 0
    for name in BUILT_FILES:
        assert (tmp_path / name).read_bytes() == (built / name).read_bytes(), name
        assert (PACKAGE_DATA / name).read_bytes() == (built / name).read_bytes(), f"{name}: rebuild the package data"


def test_the_committed_manifests_are_what_the_script_builds(built: Path) -> None:
    built_manifests = sorted(path.name for path in (built / "manifests").iterdir())

    assert built_manifests == sorted(path.name for path in MANIFESTS.iterdir())
    for name in built_manifests:
        assert (MANIFESTS / name).read_bytes() == (built / "manifests" / name).read_bytes(), f"{name}: rebuild"


def test_json_files_are_compact_and_the_declension_tables_are_not_in_morph(built: Path) -> None:
    for name in (name for name in BUILT_FILES if name.endswith(".json")):
        assert len((built / name).read_text().splitlines()) == 1, name
    assert not (built / "morph/decline.json").exists()


def test_missing_source_exits_naming_the_file(tmp_path: Path) -> None:
    missing = tmp_path / "nope" / "lemms.tsv"
    config = tmp_path / "build_data.toml"
    sources = {**SOURCES, "lemmas": str(missing)}
    config.write_text("[sources]\n" + "".join(f'{key} = "{value}"\n' for key, value in sources.items()))

    result = _build(tmp_path / "out", config)

    assert result.returncode != 0
    assert str(missing) in result.stderr
    assert not (tmp_path / "out" / "morph" / "lemmas.marisa").exists()


def test_row_counts(built: Path) -> None:
    lemmas = marisa_trie.BytesTrie().mmap(str(built / "morph/lemmas.marisa"))
    forms = marisa_trie.BytesTrie().mmap(str(built / "morph/forms.marisa"))
    morph = json.loads((built / "morph/morph.json").read_text())
    lists = json.loads((built / "text/lists.json").read_text())

    # 845 374 source rows minus 6 junk rows (a number, «од?оклассники», 4 without a POS), 397 repeated wordforms,
    # plus 4 wordforms of the corrections (morph.toml) that lemms.tsv lacks
    assert len(lemmas) == 844_975
    assert len(set(forms.keys())) == 169_939  # lower-cased lemmas, the corrected ones too
    assert len(morph["lemma_suffixes"]) == 256
    assert len(morph["nouns_like_adjectives"]) == 417
    assert len(morph["adjective_endings"]) == 89  # the first column of adjSuffixes
    assert len(lists["abbreviations"]) == 1_016
    assert len(lists["phrase_start_words"]) == 644
    assert len(lists["prepositions"]) == 46  # 47 in the VBA literal, the stray latin «g» dropped
    assert len(lists["complement_prepositions"]) == 16
    assert lists["toponym_prepositions_ru"] == ["в", "во", "на", "по", "из", "до", "г", "и"]
    assert lists["toponym_prepositions_en"] == ["in", "at", "by", "to"]


KNOWN_LEMMAS = {
    "москве": "москва\tn",
    "купила": "купить\tv",
    "диваны": "диван\tn",
    "красный": "красный\ta",
    "быстро": "быстрый\tadvb",
    "смартфонами": "смартфон\tn",
    "айфона": "айфон\tn",
    "нашем": "наш\tprn",
    "подо": "под\tprep",
    "нет": "нет\tprt",
    "раздела": "раздел\tnv",
    "изобретаемый": "изобретаемый\tp",
    "абазе": "абаза\tn",  # lemma lower-cased (Абаза in the source)
    "азов": "аз\tn",  # a repeated wordform: the last row wins, as the add-in's sorted VLOOKUP
    "купили": "купить\tv",
    "лучший": "хороший\ta",
    "смартфон": "смартфон\tn",
}
KNOWN_FORMS = {"москва": "москве", "купить": "купила", "диван": "диваны"}  # 17 + 3 = 20 known lookups


def test_known_lookups(built: Path) -> None:
    lemmas = marisa_trie.BytesTrie().mmap(str(built / "morph/lemmas.marisa"))
    forms = marisa_trie.BytesTrie().mmap(str(built / "morph/forms.marisa"))
    morph = json.loads((built / "morph/morph.json").read_text())
    lists = json.loads((built / "text/lists.json").read_text())

    for wordform, value in KNOWN_LEMMAS.items():
        assert [v.decode() for v in lemmas[wordform]] == [value], wordform
    for lemma, wordform in KNOWN_FORMS.items():
        assert wordform in [v.decode() for v in forms[lemma]], lemma
    assert "0,0000001" not in lemmas
    assert morph["lemma_suffixes"]["ания"] == "ание"
    assert "ный" in morph["adjective_endings"]
    assert "по" in lists["prepositions"]
    assert "пo" not in lists["prepositions"]  # latin «o» fixed
    assert "g" not in lists["stopwords"]
    assert "СПб" in lists["abbreviations"]
