"""Governance registry tests for TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001_REPORT.md"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_FORBIDDEN_TRUE_FLAGS = (
    "coverage_computed",
    "interval_computed",
    "empirical_coverage_computed",
    "kfold_inference_implemented",
    "placebo_inference_implemented",
    "estimator_implemented",
    "inference_implemented",
    "bootstrap_inference_implemented",
    "p_value_computed",
    "confidence_interval_computed",
    "uncertainty_computed",
    "effect_estimate_computed_new",
    "lift_computed_new",
    "roi_computed_new",
    "method_promoted",
    "method_unblocked",
    "production_catalog_unblocked",
    "production_authorization_granted",
    "production_readout_authorized",
    "mmm_runtime_calls_implemented",
    "llm_decisioning_authorized",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_summary_complete() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001"
    assert data["coverage_validation_runtime_implemented"] is True
    assert data["coverage_computed"] is False
    assert data["recommended_next_artifact"] == "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001"


def test_forbidden_flags_false_in_summary() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_governance_registry_references_runtime() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-KFOLD-COVERAGE-VALIDATION-RUNTIME-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-KFOLD-COVERAGE-VALIDATION-RUNTIME-001" in lane_ids


def test_report_documents_runtime() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "coverage_validation_runtime_implemented" in text
    assert "COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK" in text
    assert "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001" in text
    assert "no coverage computation" in text.lower() or "does not compute" in text.lower()
