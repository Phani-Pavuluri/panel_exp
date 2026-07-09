"""Governance tests for TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_BUNDLE = _REPO / "docs/track_d/TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001.md"
_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_SENSITIVITY_FAMILIES = (
    "donor_pool_sensitivity",
    "regularization_sensitivity",
    "outlier_sensitivity",
    "fold_geometry_sensitivity",
    "sparse_high_noise_metric_sensitivity",
    "seasonality_preperiod_fit_sensitivity",
    "metric_scale_sensitivity",
    "aggregate_pooled_geometry_blocker",
)

_DIAGNOSTIC_METRICS = (
    "donor_pool_sensitivity_diagnostic",
    "donor_pool_shift_diagnostic",
    "donor_quality_degradation_diagnostic",
    "regularization_sensitivity_diagnostic",
    "regularization_overconstraint_diagnostic",
    "regularization_underconstraint_diagnostic",
    "outlier_sensitivity_diagnostic",
    "outlier_directional_instability_diagnostic",
    "fold_geometry_sensitivity_diagnostic",
    "fold_imbalance_instability_diagnostic",
    "sparse_metric_sensitivity_diagnostic",
    "high_noise_sensitivity_diagnostic",
    "seasonality_sensitivity_diagnostic",
    "preperiod_fit_sensitivity_diagnostic",
    "metric_scale_sensitivity_diagnostic",
    "aggregate_pooled_geometry_blocker_diagnostic",
    "crossed_regime_failure_rate_diagnostic",
    "sensitivity_blocker_rate_diagnostic",
)

_RUNTIME_REPORTS = (
    "regime_sensitivity_report",
    "donor_pool_sensitivity_report",
    "regularization_sensitivity_report",
    "outlier_sensitivity_report",
    "fold_geometry_sensitivity_report",
    "aggregate_pooled_geometry_blocker_report",
)

_REQUIREMENT_FLAGS = (
    "donor_pool_sensitivity_requirements_defined",
    "regularization_sensitivity_requirements_defined",
    "outlier_sensitivity_requirements_defined",
    "fold_geometry_sensitivity_requirements_defined",
    "sparse_high_noise_metric_sensitivity_requirements_defined",
    "seasonality_preperiod_fit_sensitivity_requirements_defined",
    "metric_scale_sensitivity_requirements_defined",
    "aggregate_pooled_geometry_blocker_requirements_defined",
)

_FORBIDDEN_TRUE_FLAGS = (
    "sensitivity_evidence_generated",
    "sensitivity_metrics_computed",
    "simulations_implemented",
    "robustness_validated",
    "sensitivity_behavior_approved",
    "estimator_implemented",
    "inference_implemented",
    "kfold_inference_implemented",
    "placebo_inference_implemented",
    "method_promoted",
    "method_unblocked",
    "method_promotion_authorized",
    "production_catalog_unblocked",
    "production_compatibility_authorized",
    "production_authorization_granted",
    "production_readout_authorized",
    "uncertainty_authorized",
    "uncertainty_candidate_approved",
    "confidence_interval_authorized",
    "p_value_authorized",
    "statistical_significance_authorized",
    "interval_computed",
    "coverage_computed",
    "effect_estimate_computed_new",
    "lift_computed_new",
    "roi_computed_new",
    "mmm_runtime_calls_implemented",
    "llm_decisioning_authorized",
)

_POSITIVE_FLAGS = (
    "tbrridge_sensitivity_evidence_audit_bundle_defined",
    "crossed_regime_testing_policy_defined",
    "runtime_packet_integration_defined",
    "blocker_criteria_defined",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_bundle_doc_exists() -> None:
    assert _BUNDLE.exists()
    text = _BUNDLE.read_text(encoding="utf-8")
    assert "TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001" in text
    assert (
        "tbrridge_sensitivity_evidence_audit_bundle_defined_no_sensitivity_computation_or_authorization"
        in text
    )


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001"
    assert data["status"] == "completed"


def test_current_tbrridge_posture_documented() -> None:
    text = _BUNDLE.read_text(encoding="utf-8")
    assert "RANK_0" in text
    assert "BLOCKED" in text
    assert "STAGE_2_DIAGNOSTIC_ONLY" in text


def test_all_eight_sensitivity_families_documented() -> None:
    text = _BUNDLE.read_text(encoding="utf-8")
    for family in _SENSITIVITY_FAMILIES:
        assert family in text


def test_crossed_regime_testing_policy_documented() -> None:
    text = _BUNDLE.read_text(encoding="utf-8")
    assert "Crossed-regime testing policy" in text
    assert "Tier 1" in text
    assert "Tier 2" in text
    assert "Tier 3" in text
    data = _load_summary()
    assert data["crossed_regime_testing_policy_defined"] is True


def test_full_factorial_explicitly_blocked() -> None:
    text = _BUNDLE.read_text(encoding="utf-8")
    assert "Full factorial" in text
    assert "prohibited" in text.lower() or "blocked" in text.lower()


def test_diagnostic_metrics_documented() -> None:
    text = _BUNDLE.read_text(encoding="utf-8")
    assert "Diagnostic metrics to be reported later" in text
    for metric in _DIAGNOSTIC_METRICS:
        assert metric in text


def test_runtime_packet_integration_documented() -> None:
    text = _BUNDLE.read_text(encoding="utf-8")
    assert "Runtime packet integration plan" in text
    assert "generate_tbrridge_method_promotion_review" in text
    for report in _RUNTIME_REPORTS:
        assert report in text
    data = _load_summary()
    assert data["runtime_packet_integration_defined"] is True


def test_all_eight_requirement_flags_true() -> None:
    data = _load_summary()
    for flag in _REQUIREMENT_FLAGS:
        assert data[flag] is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_positive_flags_true() -> None:
    data = _load_summary()
    for flag in _POSITIVE_FLAGS:
        assert data[flag] is True, flag


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001"
    text = _BUNDLE.read_text(encoding="utf-8")
    assert "TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001" in text


def test_final_verdict_correct() -> None:
    data = _load_summary()
    assert (
        data["final_verdict"]
        == "tbrridge_sensitivity_evidence_audit_bundle_defined_no_sensitivity_computation_or_authorization"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-SENSITIVITY-EVIDENCE-AUDIT-BUNDLE-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-SENSITIVITY-EVIDENCE-AUDIT-BUNDLE-001" in lane_ids
    inv = next(
        i
        for i in reg["investigations"]
        if i["investigation_id"] == "INV-TBRRIDGE-SENSITIVITY-EVIDENCE-AUDIT-BUNDLE-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001"
