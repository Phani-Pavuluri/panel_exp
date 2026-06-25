"""Tests for PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.governance.investigation_lifecycle_contract import (
    investigations_by_id,
    load_registry,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001_summary.json"
_REPORT = _REPO / "docs/track_d/PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001.md"

_REQUIRED_ORDERED_ARTIFACTS = [
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
    "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
    "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001",
    "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
    "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001",
    "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
    "BAYESIAN_TBR_CALIBRATION_REPLAY_RESEARCH_PLAN_001",
    "TBRRIDGE_DIAGNOSTIC_REMEDIATION_DECISION_PLAN_001",
    "TROP_EVIDENCE_SCOUT_PLAN_001",
    "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
]

_REQUIRED_LANES = frozenset({
    "lane_1_scm_production_candidate_validation",
    "lane_2_augsynth_remediation_diagnostic_validation",
    "lane_3_did_conditional_production_candidate_validation",
    "lane_4_synthetic_did_implementation_readiness",
    "lane_5_tbrridge_diagnostic_remediation_decision",
    "lane_6_classic_tbr_retire_replace_execution",
    "lane_7_bayesian_tbr_calibration_replay_research",
    "lane_8_trop_research_only_evidence",
    "lane_9_multicell_dependence_multiplicity_validation",
    "lane_10_platform_authorization_release_gate",
})

_BOUNDARY_FLAGS = {
    "scm_first_production_candidate_validation_lane": True,
    "multicell_validation_precedes_multicell_production_claims": True,
    "augsynth_remediation_before_production_validation": True,
    "did_conditional_designs_only": True,
    "synthetic_did_requires_implementation_readiness": True,
    "classic_tbr_retire_replace_priority": True,
    "bayesian_tbr_requires_calibration_replay": True,
    "tbrridge_diagnostic_unless_remediated": True,
    "trop_research_only_unless_future_evidence": True,
    "no_method_production_authorized_by_workplan": True,
    "downstream_work_paused": True,
}

_AUTH_FLAGS = (
    "production_p_value_authorized",
    "causal_confidence_interval_authorized",
    "trustreport_authorized",
    "calibration_signal_allowed",
    "mmm_ingestion_allowed",
    "llm_decisioning_allowed",
    "production_decisioning_allowed",
    "live_api_authorized",
    "scheduler_authorized",
    "budget_optimization_allowed",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_summary_json_and_workplan_doc_exist() -> None:
    assert _SUMMARY.is_file()
    assert _REPORT.is_file()
    data = _load_summary()
    assert data["artifact_id"] == "PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001"


def test_workplan_lane_count_and_coverage() -> None:
    data = _load_summary()
    assert data["workplan_lane_count"] >= 10
    assert data["failed_scenarios"] == []
    assert set(data["lanes_covered"]) == _REQUIRED_LANES
    assert data["all_required_lanes_covered"] is True
    assert len(data["lanes"]) == data["workplan_lane_count"]


def test_ordered_next_artifacts_sequence() -> None:
    data = _load_summary()
    assert data["ordered_next_artifacts"] == _REQUIRED_ORDERED_ARTIFACTS


def test_boundary_flags() -> None:
    data = _load_summary()
    for flag, expected in _BOUNDARY_FLAGS.items():
        assert data[flag] is expected


def test_no_downstream_authorization() -> None:
    data = _load_summary()
    for flag in _AUTH_FLAGS:
        assert data[flag] is False


def test_recommended_next_artifacts() -> None:
    data = _load_summary()
    assert data["recommended_next_artifacts"][0] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"
    assert data["verdict"] == (
        "production_compatibility_promotion_workplan_defined_no_downstream_authorization"
    )


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "does not authorize production inference" in text
    assert "does not authorize production p-values" in text
    assert "does not authorize causal confidence intervals" in text
    assert "TrustReport" in text
    assert "Lane 1" in text
    assert "Lane 10" in text


def test_governance_workplan_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "PRODUCTION-COMPATIBILITY-PROMOTION-WORKPLAN-001"
    )
    assert lane["status"] == "complete"
    assert lane["resolution_artifact"] == "PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001"
    assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"
    assert "INV-PRODUCTION-COMPATIBILITY-PROMOTION-WORKPLAN-001" in lane["resolved_investigations"]
    assert "INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001" in lane["resolved_investigations"]
    assert lane["open_investigations"] == []


def test_governance_workplan_investigation_resolved() -> None:
    inv = investigations_by_id()["INV-PRODUCTION-COMPATIBILITY-PROMOTION-WORKPLAN-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001"


def test_governance_scm_validation_plan_resolved() -> None:
    inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"


def test_governance_multicell_validation_plan_resolved() -> None:
    inv = investigations_by_id()["INV-MULTICELL-DEPENDENCE-AND-MULTIPLICITY-VALIDATION-PLAN-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001"


def test_governance_multicell_validation_plan_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "MULTICELL-DEPENDENCE-AND-MULTIPLICITY-VALIDATION-PLAN-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "PRODUCTION_READINESS_BACKLOG_LEDGER_001"


def test_governance_backlog_ledger_resolved() -> None:
    inv = investigations_by_id()["INV-PRODUCTION-READINESS-BACKLOG-LEDGER-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "PRODUCTION_READINESS_BACKLOG_LEDGER_001"


def test_governance_backlog_ledger_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "PRODUCTION-READINESS-BACKLOG-LEDGER-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == (
        "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001"
    )


def test_governance_selection_gate_requirements_resolved() -> None:
    inv = investigations_by_id()[
        "INV-DATA-DRIVEN-DESIGN-ESTIMATOR-INFERENCE-SELECTION-GATE-REQUIREMENTS-001"
    ]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == (
        "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001"
    )


def test_governance_selection_gate_requirements_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "DATA-DRIVEN-DESIGN-ESTIMATOR-INFERENCE-SELECTION-GATE-REQUIREMENTS-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001"


def test_governance_augsynth_remediation_plan_resolved() -> None:
    inv = investigations_by_id()["INV-AUGSYNTH-REMEDIATION-AND-DIAGNOSTIC-VALIDATION-PLAN-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001"


def test_governance_augsynth_remediation_plan_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "AUGSYNTH-REMEDIATION-AND-DIAGNOSTIC-VALIDATION-PLAN-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"
    assert "INV-DID-CONDITIONAL-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001" in lane["resolved_investigations"]
    assert lane["open_investigations"] == []


def test_governance_did_conditional_validation_plan_resolved() -> None:
    inv = investigations_by_id()["INV-DID-CONDITIONAL-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"


def test_governance_did_conditional_validation_plan_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "DID-CONDITIONAL-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001"
    assert lane["resolution_artifact"] == "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"
    assert "INV-SYNTHETIC-DID-IMPLEMENTATION-READINESS-PLAN-001" in lane["resolved_investigations"]
    assert lane["open_investigations"] == []


def test_governance_synthetic_did_readiness_plan_resolved() -> None:
    inv = investigations_by_id()["INV-SYNTHETIC-DID-IMPLEMENTATION-READINESS-PLAN-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001"


def test_governance_synthetic_did_readiness_plan_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "SYNTHETIC-DID-IMPLEMENTATION-READINESS-PLAN-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001"
    assert lane["resolution_artifact"] == "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001"
