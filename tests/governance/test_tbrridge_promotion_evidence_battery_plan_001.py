"""Governance tests for TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_PLAN = _REPO / "docs/track_d/TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_EVIDENCE_COMPONENTS = (
    "interval semantics",
    "null-control false-positive behavior",
    "directional-error behavior",
    "positive-control recovery",
    "regime sensitivity",
    "donor-pool sensitivity",
    "regularization sensitivity",
    "outlier sensitivity",
    "fold-geometry sensitivity",
    "metric/estimand alignment",
    "aggregate/pooled geometry blocker",
    "claim authorization boundary",
    "production catalog boundary",
    "downstream readout safety",
)

_ORDERED_ARTIFACTS = (
    "TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001",
    "TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001",
    "TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001",
    "TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001",
    "TBRRIDGE_REGIME_SENSITIVITY_PLAN_001",
    "TBRRIDGE_DONOR_POOL_SENSITIVITY_AUDIT_001",
    "TBRRIDGE_REGULARIZATION_SENSITIVITY_AUDIT_001",
    "TBRRIDGE_OUTLIER_SENSITIVITY_AUDIT_001",
    "TBRRIDGE_FOLD_GEOMETRY_SENSITIVITY_AUDIT_001",
    "TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001",
    "TBRRIDGE_AGGREGATE_POOLED_GEOMETRY_BLOCKER_AUDIT_001",
    "TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001",
    "TBRRIDGE_DOWNSTREAM_READOUT_SAFETY_AUDIT_001",
    "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001",
)

_FORBIDDEN_TRUE_FLAGS = (
    "evidence_generated",
    "simulations_implemented",
    "promotion_evidence_runtime_implemented",
    "method_promoted",
    "method_unblocked",
    "method_promotion_authorized",
    "production_catalog_unblocked",
    "production_compatibility_authorized",
    "production_authorization_granted",
    "production_readout_authorized",
    "uncertainty_candidate_approved",
    "uncertainty_authorized",
    "confidence_interval_authorized",
    "p_value_authorized",
    "statistical_significance_authorized",
    "coverage_approval_authorized",
    "coverage_computed",
    "interval_computed",
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
    "mmm_runtime_calls_implemented",
    "llm_decisioning_authorized",
)

_POSITIVE_FLAGS = (
    "tbrridge_promotion_evidence_battery_plan_defined",
    "missing_evidence_inventory_defined",
    "evidence_artifact_sequence_defined",
    "fixture_requirements_defined",
    "simulation_control_requirements_defined",
    "acceptance_criteria_defined",
    "runtime_packet_integration_plan_defined",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_plan_doc_exists() -> None:
    assert _PLAN.exists()
    text = _PLAN.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001" in text
    assert "tbrridge_promotion_evidence_battery_planned_no_evidence_generated_or_promotion" in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001"
    assert data["status"] == "completed"
    assert data["failed_scenarios"] == []


def test_current_tbrridge_posture_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "RANK_0" in text
    assert "BLOCKED" in text
    assert "STAGE_2_DIAGNOSTIC_ONLY" in text
    assert "not promoted" in text.lower() or "not method-promoted" in text.lower()


def test_missing_evidence_inventory_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "Missing evidence inventory" in text
    for component in _EVIDENCE_COMPONENTS:
        assert component in text
    data = _load_summary()
    assert data["missing_evidence_inventory_defined"] is True


def test_evidence_artifact_sequence_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "Ordered evidence artifact sequence" in text
    for artifact in _ORDERED_ARTIFACTS:
        assert artifact in text
    data = _load_summary()
    assert data["evidence_artifact_sequence_defined"] is True


def test_fixture_requirements_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "Fixture requirements" in text
    assert "required fixtures" in text.lower()
    data = _load_summary()
    assert data["fixture_requirements_defined"] is True


def test_simulation_control_requirements_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "Simulation/control requirements" in text
    assert "synthetic" in text.lower() or "historical controls" in text.lower()
    data = _load_summary()
    assert data["simulation_control_requirements_defined"] is True


def test_acceptance_criteria_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "Acceptance criteria by evidence component" in text
    assert "acceptance criteria" in text.lower()
    assert "blocker criteria" in text.lower()
    data = _load_summary()
    assert data["acceptance_criteria_defined"] is True


def test_runtime_packet_integration_plan_documented() -> None:
    text = _PLAN.read_text(encoding="utf-8")
    assert "Runtime packet integration plan" in text
    assert "generate_tbrridge_method_promotion_review" in text
    data = _load_summary()
    assert data["runtime_packet_integration_plan_defined"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001"
    text = _PLAN.read_text(encoding="utf-8")
    assert "TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001" in text


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
        == "tbrridge_promotion_evidence_battery_planned_no_evidence_generated_or_promotion"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-PROMOTION-EVIDENCE-BATTERY-PLAN-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-PROMOTION-EVIDENCE-BATTERY-PLAN-001" in lane_ids
    inv = next(
        i for i in reg["investigations"]
        if i["investigation_id"] == "INV-TBRRIDGE-PROMOTION-EVIDENCE-BATTERY-PLAN-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001"
