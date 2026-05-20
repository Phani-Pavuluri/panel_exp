"""Execute example notebooks via nbmake using the active Poetry interpreter."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# tests/ -> repository root (contains pyproject.toml and examples/)
REPO_ROOT = Path(__file__).resolve().parent.parent

NOTEBOOK_DIRS = (
    REPO_ROOT / "examples" / "test_notebooks",
)

# These notebooks read CSVs from paths outside the repo (examples/data not shipped).
NOTEBOOKS_REQUIRING_EXTERNAL_DATA = frozenset(
    {
        "tbr_tests.ipynb",
        "kfold_variations.ipynb",
        "power_test_google_data.ipynb",
    }
)


def test_notebooks():
    pytest.importorskip("nbmake")
    for notebook_dir in NOTEBOOK_DIRS:
        if not notebook_dir.is_dir():
            continue
        for nb_path in sorted(notebook_dir.glob("*.ipynb")):
            if nb_path.name in NOTEBOOKS_REQUIRING_EXTERNAL_DATA:
                # Optional example CSVs (google_sales, meta_geo) are not shipped in-repo.
                continue
            exit_code = subprocess.call(
                [sys.executable, "-m", "pytest", "--nbmake", str(nb_path)],
                cwd=str(REPO_ROOT),
            )
            assert exit_code == 0, f"FAIL! {nb_path}"
