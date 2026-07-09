"""Governance tests for TBRRIDGE_REGIME_SENSITIVITY_PLAN_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_PLAN = _REPO / "docs/track_d/TBRRIDGE_REGIME_SENSITIVITY_PLAN_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_REGIME_SENSITIVITY_PLAN_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_REGIME_FAMILIES = (
    "donor-pool size and quality",
    "donor-pool shift / instability",
    "regularization strength",
    "outlier contamination",
    "fold geometry",
    "sparse metrics",
    "high-noise metrics",
    "seasonal structure",
    "weak pre-period fit",
    "metric scale / variance regime",
    "treatment timing shape",
    "heterogeneous market response",
    "delayed / decaying effects",
    "low sample size",
    "aggregate / pooled geometry stress",
)

_MATRIX_AXES = (
    "donor_pool_size",
    "donor_pool_quality",
    "regularization_strength",
    "outlier_contamination",
    "fold_geometry",
    "metric_density",
    "noise_regime",
    "seasonality",
    "preperiod_fit",
    "metric_scale",
    "effect_shape",
)

_SENSITIVITY_ARTIFACT_SEQUENCE = (
    "TBRRIDGE_DONOR_POOL_SENSITIVITY_AUDIT_001",
    "TBRRIDGE_REGULARIZATION_SENSITIVITY_AUDIT_001",
    "TBRRIDGE_OUTLIER_SENSITIVITY_AUDIT_001",
    "TBRRIDGE_FOLD_GEOMETRY_SENSITIVITY_AUDIT_001",
    "TBRRIDGE_SPARSE_HIGH_NOISE_METRIC_SENSITIVITY_AUDIT_001",
    "TBRRIDGE_SEASONALITY_PREPERIOD_FIT_SENSITIVITY_AUDIT_001",
    "TBRRIDGE_METRIC_SCALE_SENSITIVITY_AUDIT_001",
    "TBRRIDGE_AGGREGATE_POOLED_GEOMETRY_BLOCKER_AUDIT_001",
)

_DIAGNOSTIC_METRICS = (
    "regime_sensitivity_summary_diagnostic",
    "donor_pool_sensitivity_diagnostic",
    "regularization_sensitivity_diagnostic",
    "outlier_sensitivity_diagnostic",
    "fold_geometry_sensitivity_diagnostic",
    "sparse_metric_sensitivity_diagnostic",
    "high_noise_sensitivity_diagnostic",
    "seasonality_sensitivity_diagnostic",
    "weak_preperiod_fit_sensitivity_diagnostic",
    "metric_scale_sensitivity_diagnostic",
    "crossed_regime_failure_rate_diagnostic",
    "regime_specific_blocker_rate_diagnostic",
    "recovery_stability_by_regime",
    "directional_stability_by_regime",
    "false_positive_stability_by_regime",
)

_RUNTIME_REPORTS = (
    "regime_sensitivity_report",
    "donor_pool_sensitivity_report",
    "regularization_sensitivity_report",
    "outlier_sensitivity_report",
    "fold_geometry_sensitivity_report",
    "aggregate_pooled_geometry_blocker_report",
)

_FORBIDDEN_TRUE_FLAGS = (
    "regime_sensitivity_evidence_generated",
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
    "tbrridge_regime_sensitivity_plan_defined",
    "sensitivity_evidence_inventory_defined",
    "coordinated_regime_matrix_defined",
    "crossed_regime_testing_plan_defined",
    "sensitivity_artifact_sequence_defined",
    "runtime_packet_integration_defined",
    "blocker_criteria_defined",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_plan_doc_exists() -> None:
    assert _PLAN.exists()
    text = _PLAN.read_text(encoding="utf-8")
    assert "TBRRIDGE_REGIME_SENSITIVITY_PLAN_001" in text
    assert (
        "tbrridge_regime_sensitivity_planned_no_sensitivity_computation_or_authorization"
        in text
    )


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_REGIME_SENSITIVITY_PLAN_001"
    assert data["status"] == "completed"


def test_current_tbrridge_posture_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "RANK_0" in text
    assert "BLOCKED" in text
    assert "STAGE_2_DIAGNOSTIC_ONLY" in text


def test_sensitivity_evidence_inventory_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "Remaining sensitivity evidence inventory" in text
    for family in _REGIME_FAMILIES:
        assert family in text
    data = _load_summary()
    assert data["sensitivity_evidence_inventory_defined"] is True


def test_coordinated_regime_matrix_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "Coordinated regime matrix" in text
    for axis in _MATRIX_AXES:
        assert axis in text
    data = _load_summary()
    assert data["coordinated_regime_matrix_defined"] is True


def test_crossed_regime_testing_plan_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "Crossed-regime testing plan" in text
    assert "Tier 1" in text
    assert "Tier 2" in text
    data = _load_summary()
    assert data["crossed_regime_testing_plan_defined"] is True


def test_ordered_sensitivity_artifact_sequence_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "Ordered sensitivity artifact sequence" in text
    for artifact in _SENSITIVITY_ARTIFACT_SEQUENCE:
        assert artifact in text
    data = _load_summary()
    assert data["sensitivity_artifact_sequence_defined"] is True


def test_diagnostic_metrics_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "Diagnostic metrics to be reported later" in text
    for metric in _DIAGNOSTIC_METRICS:
        assert metric in text


def test_runtime_packet_integration_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "Runtime packet integration plan" in text
    assert "generate_tbrridge_method_promotion_review" in text
    for report in _RUNTIME_REPORTS:
        assert report in text
    data = _load_summary()
    assert data["runtime_packet_integration_defined"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_DONOR_POOL_SENSITIVITY_AUDIT_001"
    text = _PLAN.read_text(encoding="utf-8")
    assert "TBRRIDGE_DONOR_POOL_SENSITIVITY_AUDIT_001" in text


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_positive_flags_true() -> None:
    data = _load_summary()
    for flag in _POSITIVE_FLAGS:
        assert data[flag] is True, flag


def test_final_verdict_correct() -> None:
    data = _load_summary()
    assert (
        data["final_verdict"]
        == "tbrridge_regime_sensitivity_planned_no_sensitivity_computation_or_authorization"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-REGIME-SENSITIVITY-PLAN-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-REGIME-SENSITIVITY-PLAN-001" in lane_ids
    inv = next(
        i
        for i in reg["investigations"]
        if i["investigation_id"] == "INV-TBRRIDGE-REGIME-SENSITIVITY-PLAN-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "TBRRIDGE_REGIME_SENSITIVITY_PLAN_001"
