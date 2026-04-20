"""Stage the Python package used by the static Pyodide app."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PACKAGE = ROOT / "src" / "sodium_uncertainty"
DOCS_PACKAGE = ROOT / "docs" / "sodium_uncertainty"
SRC_DEFAULTS = ROOT / "data" / "variability_defaults.json"
DOCS_DEFAULTS = ROOT / "docs" / "variability_defaults.json"


def ignore_generated(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name == "__pycache__" or name.endswith((".pyc", ".pyo"))}


def patch_browser_default_path() -> None:
    defaults_path = DOCS_PACKAGE / "defaults.py"
    text = defaults_path.read_text()
    text = text.replace(
        'parents[2] / "data" / "variability_defaults.json"',
        'parents[1] / "variability_defaults.json"',
    )
    defaults_path.write_text(text)


def main() -> None:
    if not SRC_PACKAGE.exists():
        raise SystemExit(f"Missing source package: {SRC_PACKAGE}")
    if not SRC_DEFAULTS.exists():
        raise SystemExit(f"Missing defaults file: {SRC_DEFAULTS}")

    if DOCS_PACKAGE.exists():
        shutil.rmtree(DOCS_PACKAGE)
    shutil.copytree(SRC_PACKAGE, DOCS_PACKAGE, ignore=ignore_generated)
    patch_browser_default_path()
    shutil.copy2(SRC_DEFAULTS, DOCS_DEFAULTS)
    print(f"Staged {SRC_PACKAGE.relative_to(ROOT)} -> {DOCS_PACKAGE.relative_to(ROOT)}")
    print(f"Staged {SRC_DEFAULTS.relative_to(ROOT)} -> {DOCS_DEFAULTS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
