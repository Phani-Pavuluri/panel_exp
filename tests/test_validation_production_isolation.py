"""
Guardrail: synthetic validation must not be imported by production paths.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Set

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL_EXP = REPO_ROOT / "panel_exp"
VALIDATION_PREFIX = "panel_exp.validation"

PRODUCTION_ENTRY_MODULES = (
    "panel_exp.design.geo_experiment_design",
    "panel_exp.impact",
    "panel_exp.design.registry",
    "panel_exp.inference.registry",
)


def _module_path(dotted: str) -> Path | None:
    if not dotted.startswith("panel_exp."):
        return None
    rel = Path(*dotted.split(".")[1:])
    file_path = PANEL_EXP / f"{rel}.py"
    if file_path.is_file():
        return file_path
    init_path = PANEL_EXP / rel / "__init__.py"
    if init_path.is_file():
        return init_path
    return None


def _imports_in_file(path: Path) -> Set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
            for alias in node.names:
                if node.module == "panel_exp" and alias.name == "validation":
                    found.add(VALIDATION_PREFIX)
    return found


def _panel_exp_import_closure(entry_modules: Iterable[str]) -> Set[str]:
    """All ``panel_exp.*`` modules reachable via static imports from entry points."""
    seen: Set[str] = set()
    queue = list(entry_modules)
    while queue:
        mod = queue.pop()
        if mod in seen:
            continue
        if not mod.startswith("panel_exp."):
            continue
        if mod == VALIDATION_PREFIX or mod.startswith(f"{VALIDATION_PREFIX}."):
            raise AssertionError(
                f"production import closure includes validation module: {mod}"
            )
        seen.add(mod)
        path = _module_path(mod)
        if path is None:
            continue
        for imp in _imports_in_file(path):
            if imp.startswith("panel_exp.") and imp not in seen:
                queue.append(imp)
    return seen


def test_production_entry_points_do_not_statically_import_validation():
    closure = _panel_exp_import_closure(PRODUCTION_ENTRY_MODULES)
    assert closure, "expected non-empty production module closure"
    validation_hits = {m for m in closure if m.startswith(VALIDATION_PREFIX)}
    assert not validation_hits, (
        "panel_exp.validation must not appear in static imports from production "
        f"entry points; found: {sorted(validation_hits)}"
    )


@pytest.mark.parametrize("rel_path", [
    "design/geo_experiment_design.py",
    "impact.py",
    "design/registry.py",
    "inference/registry.py",
    "design/geo_runner.py",
    "design/modes/__init__.py",
    "inference/modes/__init__.py",
])
def test_production_source_files_contain_no_validation_import_string(rel_path: str):
    text = (PANEL_EXP / rel_path).read_text(encoding="utf-8")
    assert "panel_exp.validation" not in text, (
        f"{rel_path} must not reference panel_exp.validation"
    )


def test_importing_production_paths_does_not_load_validation_subprocess():
    """Runtime check: loading registries must not register panel_exp.validation in sys.modules."""
    script = f"""
import importlib

entry = {list(PRODUCTION_ENTRY_MODULES)!r}
for name in entry:
    importlib.import_module(name)

importlib.import_module("panel_exp.design.registry").get_design_registry()
importlib.import_module("panel_exp.inference.registry").get_inference_registry()

loaded = sorted(
    k for k in __import__("sys").modules
    if k == "{VALIDATION_PREFIX}" or k.startswith("{VALIDATION_PREFIX}.")
)
if loaded:
    raise SystemExit("validation loaded: " + ", ".join(loaded))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "production imports loaded panel_exp.validation\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
