"""Governance tests for TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001.md"
_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_POSITIVE_CONTROL_FIXTURE_FAMILIES = (
    "small positive synthetic lift injections",
    "medium positive synthetic lift injections",
    "large positive synthetic lift injections",
    "negative synthetic lift injections if needed for symmetry reference",
    "near-MDE positive controls",
    "below-MDE positive controls",
    "delayed-effect positive controls",
    "decaying-effect positive controls",
    "heterogeneous market-level positive controls",
    "sparse-metric positive controls",
    "high-noise positive controls",
    "seasonal positive controls",
    "outlier-contaminated positive controls",
    "weak-preperiod-fit positive controls",
    "donor-pool-shift positive controls",
    "fold-geometry positive controls",
)

_RECOVERY_METRICS = (
    "positive_control_recovery_rate_diagnostic",
    "effect_size_recovery_bias_diagnostic",
    "effect_size_recovery_ratio_diagnostic",
    "under_recovery_rate_diagnostic",
    "over_recovery_rate_diagnostic",
    "near_mde_recovery_stability_diagnostic",
    "delayed_effect_recovery_diagnostic",
    "heterogeneous_effect_recovery_diagnostic",
    "recovery_stability_by_fold",
    "recovery_stability_by_donor_pool",
    "recovery_stability_by_regularization",
    "recovery_stability_by_metric_scale",
    "recovery_stability_by_noise_regime",
)

_BLOCKER_CRITERIA = (
    "missing positive-control recovery report",
    "incomplete injected-effect fixture coverage",
    "known effects not recoverable under basic compatible regimes",
    "severe under-recovery or over-recovery not characterized",
    "recovery confused with directional correctness",
    "near-MDE behavior treated as power/significance evidence",
    "diagnostic intervals treated as confidence intervals",
    "aggregate/pooled recovery used without validation",
    "metric/estimand mismatch",
    "claim authorization boundary missing",
)

_ALLOWED_LANGUAGE = (
    "positive-control recovery diagnostic",
    "known-effect recovery audit",
    "injected-effect stress case",
    "review-only recovery diagnostic",
    "recovery stability diagnostic",
    "evidence input for promotion review",
)

_PROHIBITED_LANGUAGE = (
    "validated recovery rate",
    "approved effect recovery",
    "statistical power approval",
    "statistical significance support",
    "p-value calibration",
    "confidence interval coverage approval",
    "production-ready recovery behavior",
    "causal lift claim",
    "ROI claim",
    "method promotion evidence complete",
)

_FORBIDDEN_TRUE_FLAGS = (
    "positive_control_evidence_generated",
    "recovery_rate_computed",
    "effect_recovery_validated",
    "statistical_power_validated",
    "p_value_calibrated",
    "statistical_significance_authorized",
    "confidence_interval_authorized",
    "interval_computed",
    "coverage_computed",
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
    "effect_estimate_computed_new",
    "lift_computed_new",
    "roi_computed_new",
    "mmm_runtime_calls_implemented",
    "llm_decisioning_authorized",
)

_POSITIVE_FLAGS = (
    "tbrridge_positive_control_recovery_audit_completed",
    "positive_control_recovery_gap_documented",
    "positive_control_fixture_requirements_defined",
    "recovery_diagnostic_metrics_defined",
    "directional_error_distinction_defined",
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
    assert "TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001" in text
    assert (
        "tbrridge_positive_control_recovery_audited_no_recovery_computation_or_authorization"
        in text
    )


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001"
    assert data["status"] == "completed"
    assert data["failed_scenarios"] == []


def test_current_tbrridge_posture_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "RANK_0" in text
    assert "BLOCKED" in text
    assert "STAGE_2_DIAGNOSTIC_ONLY" in text


def test_positive_control_recovery_evidence_gap_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Positive-control recovery evidence gap" in text
    data = _load_summary()
    assert data["positive_control_recovery_gap_documented"] is True


def test_positive_control_fixture_requirements_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Required positive-control fixture families" in text
    for fixture in _POSITIVE_CONTROL_FIXTURE_FAMILIES:
        assert fixture in text
    data = _load_summary()
    assert data["positive_control_fixture_requirements_defined"] is True


def test_recovery_diagnostic_metrics_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Recovery diagnostic metrics to be reported later" in text
    for metric in _RECOVERY_METRICS:
        assert metric in text
    data = _load_summary()
    assert data["recovery_diagnostic_metrics_defined"] is True


def test_directional_error_distinction_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Distinction from directional-error behavior" in text
    assert "directional error" in text.lower()
    data = _load_summary()
    assert data["directional_error_distinction_defined"] is True


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
    assert "positive_control_recovery_report" in text
    assert "generate_tbrridge_method_promotion_review" in text
    data = _load_summary()
    assert data["runtime_packet_integration_defined"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_REGIME_SENSITIVITY_PLAN_001"
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_REGIME_SENSITIVITY_PLAN_001" in text


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
        == "tbrridge_positive_control_recovery_audited_no_recovery_computation_or_authorization"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-POSITIVE-CONTROL-RECOVERY-AUDIT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-POSITIVE-CONTROL-RECOVERY-AUDIT-001" in lane_ids
    inv = next(
        i
        for i in reg["investigations"]
        if i["investigation_id"] == "INV-TBRRIDGE-POSITIVE-CONTROL-RECOVERY-AUDIT-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001"
