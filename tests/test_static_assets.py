import json
import os
import re
import subprocess
import sys
from pathlib import Path

from sodium_uncertainty.defaults import load_defaults

ROOT = Path(__file__).resolve().parents[1]
SRC_PACKAGE = ROOT / "src" / "sodium_uncertainty"
DOCS_PACKAGE = ROOT / "docs" / "sodium_uncertainty"


def _expected_staged_text(source: Path) -> str:
    text = source.read_text()
    if source.name == "defaults.py":
        return text.replace(
            'parents[2] / "data" / "variability_defaults.json"',
            'parents[1] / "variability_defaults.json"',
        )
    return text


def test_default_variability_file_loads_from_source_path() -> None:
    data = load_defaults()
    assert data["units"] == "mmol/L"
    assert data["defaults"]["analytic_repeatability"]["central_lab_indirect_ISE"]


def test_docs_defaults_match_source_defaults() -> None:
    source = json.loads((ROOT / "data" / "variability_defaults.json").read_text())
    staged = json.loads((ROOT / "docs" / "variability_defaults.json").read_text())
    assert staged == source


def test_staged_package_matches_source_package_with_browser_path_patch() -> None:
    source_files = sorted(path.relative_to(SRC_PACKAGE) for path in SRC_PACKAGE.rglob("*.py"))
    staged_files = sorted(path.relative_to(DOCS_PACKAGE) for path in DOCS_PACKAGE.rglob("*.py"))

    assert staged_files == source_files
    for relative_path in source_files:
        source = SRC_PACKAGE / relative_path
        staged = DOCS_PACKAGE / relative_path
        assert staged.read_text() == _expected_staged_text(source)


def test_index_loads_every_staged_package_file_into_pyodide() -> None:
    index_text = (ROOT / "docs" / "index.html").read_text()
    match = re.search(r"const packageFiles = \[(.*?)\];", index_text, re.DOTALL)
    assert match is not None

    listed_files = set(re.findall(r'"([^"]+)"', match.group(1)))
    staged_files = {f"sodium_uncertainty/{path.name}" for path in DOCS_PACKAGE.glob("*.py")}

    assert staged_files <= listed_files


def test_docs_app_compiles_and_exposes_compute_from_json() -> None:
    compile((ROOT / "docs" / "app.py").read_text(), str(ROOT / "docs" / "app.py"), "exec")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "docs")
    code = "import app; assert callable(app.compute_from_json)"
    subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT / "docs",
        env=env,
        check=True,
    )
