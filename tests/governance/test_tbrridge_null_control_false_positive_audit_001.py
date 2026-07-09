"""Governance tests for TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_NULL_CONTROL_FIXTURE_FAMILIES = (
    "no-treatment placebo markets",
    "pre-period-only pseudo-treatment windows",
    "shuffled treatment assignment controls",
    "matched donor no-effect controls",
    "synthetic zero-lift injection controls",
    "low-signal sparse metric controls",
    "high-noise stable-null controls",
    "seasonal-null controls",
    "outlier-contaminated null controls",
    "weak-preperiod-fit null controls",
)

_FALSE_POSITIVE_METRICS = (
    "false_positive_rate_diagnostic",
    "directional_false_positive_rate_diagnostic",
    "null_interval_exclusion_rate_diagnostic",
    "null_claim_overstatement_rate_diagnostic",
    "placebo_tail_miscalibration_diagnostic",
    "null_detection_stability_by_fold",
    "null_detection_stability_by_donor_pool",
    "null_detection_stability_by_regularization",
    "null_detection_stability_by_metric_scale",
)

_BLOCKER_CRITERIA = (
    "missing null-control report",
    "incomplete fixture coverage",
    "uncharacterized false-positive behavior",
    "directional false-signal not separated",
    "null-control evidence interpreted as p-value/significance support",
    "diagnostic intervals treated as confidence intervals",
    "aggregate/pooled null behavior used without validation",
    "metric/estimand mismatch",
    "claim authorization boundary missing",
)

_ALLOWED_LANGUAGE = (
    "null-control diagnostic",
    "false-positive behavior audit",
    "no-effect stress case",
    "review-only FPR diagnostic",
    "diagnostic overclaim risk",
    "evidence input for promotion review",
)

_PROHIBITED_LANGUAGE = (
    "validated false-positive rate",
    "approved type-I error",
    "statistical significance support",
    "p-value calibration",
    "confidence interval coverage approval",
    "production-ready null behavior",
    "causal lift claim",
    "ROI claim",
    "method promotion evidence complete",
)

_FORBIDDEN_TRUE_FLAGS = (
    "null_control_evidence_generated",
    "false_positive_rate_computed",
    "type_i_error_validated",
    "p_value_calibrated",
    "statistical_significance_authorized",
    "confidence_interval_authorized",
    "interval_computed",
    "coverage_computed",
    "simulations_implemented",
    "estimator_implemented",
    "inference_implemented",
    "bootstrap_inference_implemented",
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
    "tbrridge_null_control_false_positive_audit_completed",
    "null_control_gap_documented",
    "null_control_fixture_requirements_defined",
    "false_positive_diagnostic_metrics_defined",
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
    assert "TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001" in text
    assert (
        "tbrridge_null_control_false_positive_audited_no_false_positive_computation_or_authorization"
        in text
    )


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001"
    assert data["status"] == "completed"
    assert data["failed_scenarios"] == []


def test_current_tbrridge_posture_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "RANK_0" in text
    assert "BLOCKED" in text
    assert "STAGE_2_DIAGNOSTIC_ONLY" in text


def test_null_control_evidence_gap_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "False-positive evidence gap" in text
    data = _load_summary()
    assert data["null_control_gap_documented"] is True


def test_fixture_requirements_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Required null-control fixture families" in text
    for fixture in _NULL_CONTROL_FIXTURE_FAMILIES:
        assert fixture in text
    data = _load_summary()
    assert data["null_control_fixture_requirements_defined"] is True


def test_false_positive_diagnostic_metrics_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "False-positive diagnostic metrics to be reported later" in text
    for metric in _FALSE_POSITIVE_METRICS:
        assert metric in text
    data = _load_summary()
    assert data["false_positive_diagnostic_metrics_defined"] is True


def test_directional_false_signal_distinction_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Directional false-signal distinction" in text
    assert "directional false signal" in text.lower()


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
    assert "null_control_false_positive_report" in text
    assert "generate_tbrridge_method_promotion_review" in text
    data = _load_summary()
    assert data["runtime_packet_integration_defined"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001"
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001" in text


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
        == "tbrridge_null_control_false_positive_audited_no_false_positive_computation_or_authorization"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-NULL-CONTROL-FALSE-POSITIVE-AUDIT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-NULL-CONTROL-FALSE-POSITIVE-AUDIT-001" in lane_ids
    inv = next(
        i for i in reg["investigations"]
        if i["investigation_id"] == "INV-TBRRIDGE-NULL-CONTROL-FALSE-POSITIVE-AUDIT-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001"
