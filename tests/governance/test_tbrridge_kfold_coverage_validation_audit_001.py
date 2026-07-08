"""Governance tests for TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_EVIDENCE_TAXONOMY = (
    "leakage_diagnostic_report",
    "placebo_calibration_diagnostic_report",
    "interval_semantics_report",
    "simulation_design_manifest",
    "null_control_manifest",
    "positive_control_manifest",
    "fold_geometry_regime_manifest",
    "sample_size_regime_manifest",
    "empirical_coverage_report",
    "false_positive_rate_report",
    "placebo_calibrated_tail_report",
    "lineage_provenance_manifest",
)

_READINESS_STATUSES = (
    "COVERAGE_VALIDATION_NOT_STARTED",
    "COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK",
    "COVERAGE_VALIDATION_BLOCKED_BY_PLACEBO_MISCALIBRATION",
    "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS",
    "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_SIMULATION_DESIGN",
    "COVERAGE_VALIDATION_EVIDENCE_BUILDING",
    "COVERAGE_VALIDATION_READY_FOR_CONTRACT",
    "COVERAGE_VALIDATION_READY_FOR_RUNTIME",
    "COVERAGE_VALIDATION_READY_FOR_UNCERTAINTY_CANDIDATE_REVIEW",
    "COVERAGE_VALIDATION_REQUIRES_METHOD_REVIEW",
)

_FORBIDDEN_TRUE_FLAGS = (
    "coverage_runtime_implemented",
    "kfold_inference_implemented",
    "placebo_inference_implemented",
    "estimator_implemented",
    "inference_implemented",
    "bootstrap_inference_implemented",
    "p_value_computed",
    "confidence_interval_computed",
    "uncertainty_computed",
    "coverage_computed",
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

_POSITIVE_FLAGS = (
    "coverage_validation_audit_completed",
    "coverage_evidence_taxonomy_defined",
    "interval_semantics_gap_documented",
    "simulation_design_requirements_defined",
    "null_control_requirements_defined",
    "positive_control_requirements_defined",
    "placebo_calibrated_false_positive_requirements_defined",
    "fold_geometry_regime_requirements_defined",
    "sample_size_regime_requirements_defined",
    "stop_go_criteria_defined",
    "future_contract_recommended",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001" in text
    assert "tbrridge_kfold_coverage_validation_requirements_audited_no_coverage_runtime_or_uncertainty" in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001"
    assert data["status"] == "completed"
    assert data["failed_scenarios"] == []


def test_source_files_inspected_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001" in text
    assert "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001" in text
    assert "D5_TRUST_TBRRIDGE_KFOLD_001" in text


def test_relationship_to_leakage_runtime_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "KFold leakage" in text or "leakage diagnostic" in text.lower()
    assert "leakage_diagnostic_report" in text


def test_relationship_to_placebo_runtime_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "placebo calibration" in text.lower()
    assert "placebo_calibration_diagnostic_report" in text


def test_coverage_evidence_taxonomy_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    for item in _EVIDENCE_TAXONOMY:
        assert item in text
    data = _load_summary()
    assert data["coverage_evidence_taxonomy_defined"] is True


def test_interval_semantics_gap_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "interval_semantics_report" in text
    assert "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS" in text
    data = _load_summary()
    assert data["interval_semantics_gap_documented"] is True


def test_simulation_design_requirements_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "simulation_design_manifest" in text
    data = _load_summary()
    assert data["simulation_design_requirements_defined"] is True


def test_null_control_requirements_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "null_control_manifest" in text
    data = _load_summary()
    assert data["null_control_requirements_defined"] is True


def test_positive_control_requirements_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "positive_control_manifest" in text
    data = _load_summary()
    assert data["positive_control_requirements_defined"] is True


def test_placebo_calibrated_false_positive_requirements_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "placebo_calibrated_tail_report" in text
    data = _load_summary()
    assert data["placebo_calibrated_false_positive_requirements_defined"] is True


def test_fold_geometry_regime_requirements_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "fold_geometry_regime_manifest" in text
    data = _load_summary()
    assert data["fold_geometry_regime_requirements_defined"] is True


def test_sample_size_regime_requirements_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "sample_size_regime_manifest" in text
    data = _load_summary()
    assert data["sample_size_regime_requirements_defined"] is True


def test_stop_go_criteria_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Stop/go" in text or "stop/go" in text.lower()
    for status in _READINESS_STATUSES:
        assert status in text
    data = _load_summary()
    assert data["stop_go_criteria_defined"] is True


def test_future_contract_recommended() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_CONTRACT_001"
    assert data["future_contract_recommended"] is True
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_CONTRACT_001" in text


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data[flag] is False, flag


def test_positive_flags_true() -> None:
    data = _load_summary()
    for flag in _POSITIVE_FLAGS:
        assert data[flag] is True, flag


def test_final_verdict_correct() -> None:
    data = _load_summary()
    assert (
        data["final_verdict"]
        == "tbrridge_kfold_coverage_validation_requirements_audited_no_coverage_runtime_or_uncertainty"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-KFOLD-COVERAGE-VALIDATION-AUDIT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-KFOLD-COVERAGE-VALIDATION-AUDIT-001" in lane_ids
    inv = next(
        i for i in reg["investigations"]
        if i["investigation_id"] == "INV-TBRRIDGE-KFOLD-COVERAGE-VALIDATION-AUDIT-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001"
