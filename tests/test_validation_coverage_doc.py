"""Consistency check: every catalog estimator appears in VALIDATION_COVERAGE.md."""

from __future__ import annotations

import re
from pathlib import Path

from panel_exp.method_registry import get_method_registry

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "VALIDATION_COVERAGE.md"


def _estimator_names_in_doc(text: str) -> set[str]:
    """Extract registry estimator names mentioned in the coverage doc."""
    found: set[str] = set()
    for name in get_method_registry().list_estimator_names():
        # Word-boundary match on registry name (e.g. TBRRidge, SCM).
        if re.search(rf"\b{re.escape(name)}\b", text):
            found.add(name)
    return found


def test_validation_coverage_doc_exists():
    assert DOC_PATH.is_file(), f"Missing {DOC_PATH}"


def test_every_catalog_estimator_documented():
    text = DOC_PATH.read_text(encoding="utf-8")
    registry_names = set(get_method_registry().list_estimator_names())
    documented = _estimator_names_in_doc(text)
    missing = sorted(registry_names - documented)
    assert not missing, (
        f"Estimators missing from {DOC_PATH.name}: {missing}. "
        f"Documented: {sorted(documented)}"
    )


def test_doc_sections_present():
    text = DOC_PATH.read_text(encoding="utf-8")
    for heading in (
        "What “validated” means in this repo",
        "What is explicitly not validated",
        "Why no estimator is currently `production_safe`",
        "Promotion criteria",
    ):
        assert heading in text, f"Section missing: {heading}"


def test_minimum_required_estimators_documented():
    required = {
        "TBRRidge",
        "TBR",
        "SCM",
        "SyntheticControlCVXPY",
        "AugSynthCVXPY",
        "DID",
        "SyntheticDID",
        "AugSynth",
        "BayesianTBR",
        "BayesianTBRHorseShoe",
        "TROP",
        "MTGP",
    }
    text = DOC_PATH.read_text(encoding="utf-8")
    documented = _estimator_names_in_doc(text)
    assert required <= documented
