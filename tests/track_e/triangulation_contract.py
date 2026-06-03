"""Track E triangulation contract (E5/E6) — delegates to production evaluator.

E6 tests import from here for fixture loading helpers; evaluation logic lives in
``panel_exp.track_b.triangulation``.
"""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.track_b.triangulation import (
    TriangulationOutcome,
    apply_e5_calibration_policy,
    assert_forbidden_actions,
    evaluate_triangulation,
    evaluate_triangulation_fixture,
)

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "track_e_conflicts"
MANIFEST_PATH = FIXTURES_DIR / "manifest.json"


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_e4_fixture(relative_path: str) -> dict:
    return json.loads((FIXTURES_DIR / relative_path).read_text(encoding="utf-8"))


def load_all_e4_fixtures() -> list[dict]:
    manifest = load_manifest()
    return [load_e4_fixture(entry["file"]) for entry in manifest["fixtures"]]


def evaluate_e4_fixture(fixture: dict) -> TriangulationOutcome:
    return evaluate_triangulation_fixture(fixture)


__all__ = [
    "FIXTURES_DIR",
    "MANIFEST_PATH",
    "TriangulationOutcome",
    "apply_e5_calibration_policy",
    "assert_forbidden_actions",
    "evaluate_e4_fixture",
    "evaluate_triangulation",
    "load_all_e4_fixtures",
    "load_e4_fixture",
    "load_manifest",
]
