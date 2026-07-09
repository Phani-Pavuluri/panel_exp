"""Governance tests for TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001.md"
_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_ALIGNMENT_DIMENSIONS = (
    "outcome_metric_name",
    "outcome_metric_definition",
    "numerator_definition",
    "denominator_definition",
    "transformation_applied",
    "modeled_target_scale",
    "reporting_scale",
    "causal_estimand",
    "business_estimand",
    "treatment_contrast",
    "exposure_definition",
    "time_window",
    "pre_period_window",
    "post_period_window",
    "geography_unit",
    "donor_pool_scope",
    "treatment_unit_scope",
    "aggregation_level",
    "weighting_scheme",
    "missing_data_policy",
    "outlier_policy",
    "seasonality_adjustment_policy",
    "lag_or_carryover_policy",
)

_DIAGNOSTIC_CHECKS = (
    "metric_estimand_alignment_diagnostic",
    "modeled_target_reporting_scale_alignment_diagnostic",
    "transformation_invertibility_diagnostic",
    "aggregation_consistency_diagnostic",
    "denominator_stability_diagnostic",
    "time_window_alignment_diagnostic",
    "treatment_contrast_alignment_diagnostic",
    "geography_unit_alignment_diagnostic",
    "donor_pool_scope_alignment_diagnostic",
    "missing_data_policy_alignment_diagnostic",
    "outlier_policy_alignment_diagnostic",
    "lag_carryover_alignment_diagnostic",
)

_BLOCKER_CRITERIA = (
    "missing metric/estimand alignment report",
    "undefined causal or business estimand",
    "modeled target differs from reporting target without governed bridge",
    "transformation or inverse transformation unspecified",
    "treatment contrast mismatch",
    "time-window mismatch",
    "geography/unit mismatch",
    "aggregation or weighting mismatch",
    "denominator instability unaddressed",
    "missing-data or outlier policy unspecified",
    "lag/carryover policy unspecified",
    "metric-scale diagnostic interpreted as business lift",
    "ROI inferred without governed cost/revenue mapping",
    "claim authorization boundary missing",
)

_ALLOWED_LANGUAGE = (
    "metric/estimand alignment audit",
    "modeled target diagnostic",
    "reporting-scale alignment requirement",
    "estimand mapping requirement",
    "diagnostic alignment evidence",
    "future promotion-review input",
)

_PROHIBITED_LANGUAGE = (
    "estimand approved",
    "metric compatibility authorized",
    "validated business lift",
    "ROI-ready output",
    "production-ready readout",
    "confidence interval support",
    "p-value/significance support",
    "method promotion evidence complete",
    "catalog unblock support",
)

_FORBIDDEN_TRUE_FLAGS = (
    "metric_estimand_alignment_evidence_generated",
    "metric_compatibility_authorized",
    "estimand_approved",
    "business_lift_authorized",
    "roi_authorized",
    "alignment_metrics_computed",
    "simulations_implemented",
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
    "tbrridge_metric_estimand_alignment_audit_completed",
    "metric_estimand_gap_documented",
    "alignment_dimensions_defined",
    "transformation_requirements_defined",
    "diagnostic_checks_defined",
    "blocker_criteria_defined",
    "runtime_packet_integration_defined",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001" in text
    assert (
        "tbrridge_metric_estimand_alignment_audited_no_estimand_approval_or_metric_authorization"
        in text
    )


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001"
    assert data["status"] == "completed"


def test_current_tbrridge_posture_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "RANK_0" in text
    assert "BLOCKED" in text
    assert "STAGE_2_DIAGNOSTIC_ONLY" in text


def test_metric_estimand_evidence_gap_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Alignment evidence gap" in text
    data = _load_summary()
    assert data["metric_estimand_gap_documented"] is True


def test_required_alignment_dimensions_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Required alignment dimensions" in text
    for dimension in _ALIGNMENT_DIMENSIONS:
        assert dimension in text
    data = _load_summary()
    assert data["alignment_dimensions_defined"] is True


def test_metric_transformation_requirements_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Metric transformation requirements" in text
    assert "log-transformed" in text
    assert "inverse transform" in text.lower()
    data = _load_summary()
    assert data["transformation_requirements_defined"] is True


def test_future_diagnostic_checks_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Required future diagnostic checks" in text
    for check in _DIAGNOSTIC_CHECKS:
        assert check in text
    data = _load_summary()
    assert data["diagnostic_checks_defined"] is True


def test_blocker_criteria_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Blocker criteria for future promotion review" in text
    for criterion in _BLOCKER_CRITERIA:
        assert criterion in text
    data = _load_summary()
    assert data["blocker_criteria_defined"] is True


def test_allowed_prohibited_language_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Allowed language" in text
    assert "Prohibited language" in text
    for phrase in _ALLOWED_LANGUAGE:
        assert phrase in text
    for phrase in _PROHIBITED_LANGUAGE:
        assert phrase in text


def test_runtime_packet_integration_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Runtime packet integration plan" in text
    assert "metric_estimand_alignment_report" in text
    assert "generate_tbrridge_method_promotion_review" in text
    data = _load_summary()
    assert data["runtime_packet_integration_defined"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001"
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001" in text


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
        == "tbrridge_metric_estimand_alignment_audited_no_estimand_approval_or_metric_authorization"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-METRIC-ESTIMAND-ALIGNMENT-AUDIT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-METRIC-ESTIMAND-ALIGNMENT-AUDIT-001" in lane_ids
    inv = next(
        i
        for i in reg["investigations"]
        if i["investigation_id"] == "INV-TBRRIDGE-METRIC-ESTIMAND-ALIGNMENT-AUDIT-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001"
