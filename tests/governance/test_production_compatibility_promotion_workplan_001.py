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
    assert "INV-METHOD-FAMILY-RETIRE-REPLACE-EXECUTION-PLAN-001" in lane["resolved_investigations"]
    assert lane["open_investigations"] == []


def test_governance_method_family_retire_replace_plan_resolved() -> None:
    inv = investigations_by_id()["INV-METHOD-FAMILY-RETIRE-REPLACE-EXECUTION-PLAN-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001"


def test_governance_method_family_retire_replace_plan_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "METHOD-FAMILY-RETIRE-REPLACE-EXECUTION-PLAN-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == (
        "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001"
    )
    assert lane["resolution_artifact"] == "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001"
    assert lane["open_investigations"] == []


def test_governance_selection_gate_implementation_plan_resolved() -> None:
    inv = investigations_by_id()[
        "INV-DATA-DRIVEN-DESIGN-ESTIMATOR-INFERENCE-SELECTION-GATE-IMPLEMENTATION-PLAN-001"
    ]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == (
        "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001"
    )


def test_governance_selection_gate_implementation_plan_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "DATA-DRIVEN-DESIGN-ESTIMATOR-INFERENCE-SELECTION-GATE-IMPLEMENTATION-PLAN-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001"
    assert lane["resolution_artifact"] == (
        "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001"
    )
    assert "INV-PRODUCTION-AUTHORIZATION-RELEASE-GATE-PLAN-001" in lane["resolved_investigations"]


def test_governance_production_authorization_release_gate_plan_resolved() -> None:
    inv = investigations_by_id()["INV-PRODUCTION-AUTHORIZATION-RELEASE-GATE-PLAN-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001"


def test_governance_production_authorization_release_gate_plan_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "PRODUCTION-AUTHORIZATION-RELEASE-GATE-PLAN-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001"
    assert lane["resolution_artifact"] == "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001"
    assert "INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-PLAN-001" in lane["resolved_investigations"]


def test_governance_scm_validation_implementation_plan_resolved() -> None:
    inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-PLAN-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001"


def test_governance_scm_validation_implementation_plan_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-PLAN-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001"
    assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001"


def test_governance_scm_validation_implementation_resolved() -> None:
    inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001"


def test_governance_scm_validation_implementation_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-VALIDATION-IMPLEMENTATION-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001"
    assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001"


def test_governance_scm_null_calibration_implementation_plan_resolved() -> None:
    inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-NULL-CALIBRATION-IMPLEMENTATION-PLAN-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001"


def test_governance_scm_null_calibration_implementation_plan_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-NULL-CALIBRATION-IMPLEMENTATION-PLAN-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001"
    assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001"


def test_governance_scm_null_calibration_implementation_resolved() -> None:
    inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-NULL-CALIBRATION-IMPLEMENTATION-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001"


def test_governance_scm_null_calibration_implementation_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-NULL-CALIBRATION-IMPLEMENTATION-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001"
    assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001"


def test_governance_scm_jackknife_sensitivity_implementation_plan_resolved() -> None:
    inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-JACKKNIFE-SENSITIVITY-IMPLEMENTATION-PLAN-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001"


def test_governance_scm_jackknife_sensitivity_implementation_plan_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-JACKKNIFE-SENSITIVITY-IMPLEMENTATION-PLAN-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001"
    assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001"


def test_governance_scm_jackknife_sensitivity_implementation_resolved() -> None:
    inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-JACKKNIFE-SENSITIVITY-IMPLEMENTATION-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001"


def test_governance_scm_jackknife_sensitivity_implementation_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-JACKKNIFE-SENSITIVITY-IMPLEMENTATION-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001"
    assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001"


def test_governance_scm_release_gate_review_plan_resolved() -> None:
    inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-REVIEW-PLAN-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001"


def test_governance_scm_release_gate_review_plan_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-REVIEW-PLAN-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001"
    assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001"


def test_governance_scm_release_gate_review_packet_resolved() -> None:
    inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-REVIEW-PACKET-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001"


def test_governance_scm_release_gate_review_packet_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-REVIEW-PACKET-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001"
    assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001"


def test_governance_scm_release_gate_decision_plan_resolved() -> None:
    inv = investigations_by_id()["INV-SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-DECISION-PLAN-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001"


def test_governance_scm_release_gate_decision_plan_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "SCM-PRODUCTION-CANDIDATE-RELEASE-GATE-DECISION-PLAN-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001"
    assert lane["resolution_artifact"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001"


def test_governance_method_portfolio_prioritization_checkpoint_resolved() -> None:
    inv = investigations_by_id()["INV-METHOD-PORTFOLIO-PRIORITIZATION-CHECKPOINT-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001"


def test_governance_method_portfolio_prioritization_checkpoint_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "METHOD-PORTFOLIO-PRIORITIZATION-CHECKPOINT-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001"
    assert lane["resolution_artifact"] == "METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001"


def test_governance_experiment_portfolio_planner_agent_roadmap_resolved() -> None:
    inv = investigations_by_id()["INV-EXPERIMENT-PORTFOLIO-PLANNER-AGENT-ROADMAP-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001"


def test_governance_experiment_portfolio_planner_agent_roadmap_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "EXPERIMENT-PORTFOLIO-PLANNER-AGENT-ROADMAP-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001"
    assert lane["resolution_artifact"] == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001"


def test_governance_experiment_portfolio_planner_agent_tooling_contract_resolved() -> None:
    inv = investigations_by_id()["INV-EXPERIMENT-PORTFOLIO-PLANNER-AGENT-TOOLING-CONTRACT-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001"


def test_governance_experiment_portfolio_planner_agent_tooling_contract_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "EXPERIMENT-PORTFOLIO-PLANNER-AGENT-TOOLING-CONTRACT-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"
    assert lane["resolution_artifact"] == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001"


def test_governance_roadmap_implementation_detail_gap_audit_resolved() -> None:
    inv = investigations_by_id()["INV-ROADMAP-IMPLEMENTATION-DETAIL-GAP-AUDIT-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001"


def test_governance_roadmap_implementation_detail_gap_audit_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "ROADMAP-IMPLEMENTATION-DETAIL-GAP-AUDIT-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001"
    assert lane["resolution_artifact"] == "ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001"


def test_governance_geo_kpi_spend_data_contract_resolved() -> None:
    inv = investigations_by_id()["INV-GEO-KPI-SPEND-DATA-CONTRACT-AND-PROFILER-SPEC-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001"


def test_governance_geo_kpi_spend_data_contract_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "GEO-KPI-SPEND-DATA-CONTRACT-AND-PROFILER-SPEC-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"
    assert lane["resolution_artifact"] == "GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001"


def test_governance_experiment_portfolio_intake_contract_resolved() -> None:
    inv = investigations_by_id()["INV-EXPERIMENT-PORTFOLIO-INTAKE-CONTRACT-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"


def test_governance_experiment_portfolio_intake_contract_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "EXPERIMENT-PORTFOLIO-INTAKE-CONTRACT-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001"
    assert lane["resolution_artifact"] == "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"


def test_governance_panel_exp_agent_run_packet_contract_resolved() -> None:
    inv = investigations_by_id()["INV-PANEL-EXP-AGENT-RUN-PACKET-CONTRACT-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001"


def test_governance_panel_exp_agent_run_packet_contract_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "PANEL-EXP-AGENT-RUN-PACKET-CONTRACT-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001"
    assert lane["resolution_artifact"] == "PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001"


def test_governance_panel_exp_artifact_registry_provenance_contract_resolved() -> None:
    inv = investigations_by_id()["INV-PANEL-EXP-ARTIFACT-REGISTRY-AND-PROVENANCE-CONTRACT-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001"


def test_governance_panel_exp_artifact_registry_provenance_contract_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "PANEL-EXP-ARTIFACT-REGISTRY-AND-PROVENANCE-CONTRACT-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001"
    assert lane["resolution_artifact"] == "PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001"


def test_governance_panel_exp_golden_path_acceptance_tests_resolved() -> None:
    inv = investigations_by_id()["INV-PANEL-EXP-GOLDEN-PATH-ACCEPTANCE-TESTS-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001"


def test_governance_panel_exp_golden_path_acceptance_tests_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "PANEL-EXP-GOLDEN-PATH-ACCEPTANCE-TESTS-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "GEO_KPI_SPEND_DATA_PROFILER_001"
    assert lane["resolution_artifact"] == "PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001"


def test_governance_geo_kpi_spend_data_profiler_resolved() -> None:
    inv = investigations_by_id()["INV-GEO-KPI-SPEND-DATA-PROFILER-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "GEO_KPI_SPEND_DATA_PROFILER_001"


def test_governance_geo_kpi_spend_data_profiler_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "GEO-KPI-SPEND-DATA-PROFILER-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001"
    assert lane["resolution_artifact"] == "GEO_KPI_SPEND_DATA_PROFILER_001"


def test_governance_geo_unit_market_feasibility_diagnostics_resolved() -> None:
    inv = investigations_by_id()["INV-GEO-UNIT-AND-MARKET-FEASIBILITY-DIAGNOSTICS-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001"


def test_governance_geo_unit_market_feasibility_diagnostics_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "GEO-UNIT-AND-MARKET-FEASIBILITY-DIAGNOSTICS-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001"
    assert lane["resolution_artifact"] == "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001"


def test_governance_spend_contrast_feasibility_tooling_contract_resolved() -> None:
    inv = investigations_by_id()["INV-SPEND-CONTRAST-FEASIBILITY-TOOLING-CONTRACT-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001"


def test_governance_spend_contrast_feasibility_tooling_contract_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "SPEND-CONTRAST-FEASIBILITY-TOOLING-CONTRACT-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001"
    assert lane["resolution_artifact"] == "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001"


def test_governance_spend_requirement_manipulation_feasibility_contract_resolved() -> None:
    inv = investigations_by_id()["INV-SPEND-REQUIREMENT-AND-MANIPULATION-FEASIBILITY-CONTRACT-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001"


def test_governance_spend_requirement_manipulation_feasibility_contract_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "SPEND-REQUIREMENT-AND-MANIPULATION-FEASIBILITY-CONTRACT-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001"
    assert lane["resolution_artifact"] == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001"


def test_governance_spend_requirement_manipulation_feasibility_diagnostics_resolved() -> None:
    inv = investigations_by_id()["INV-SPEND-REQUIREMENT-AND-MANIPULATION-FEASIBILITY-DIAGNOSTICS-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001"


def test_governance_spend_requirement_manipulation_feasibility_diagnostics_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "SPEND-REQUIREMENT-AND-MANIPULATION-FEASIBILITY-DIAGNOSTICS-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001"
    assert lane["resolution_artifact"] == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001"


def test_governance_power_mde_spend_feasibility_handoff_contract_resolved() -> None:
    inv = investigations_by_id()["INV-POWER-MDE-REQUIREMENT-AND-SPEND-FEASIBILITY-HANDOFF-CONTRACT-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001"


def test_governance_power_mde_spend_feasibility_handoff_contract_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "POWER-MDE-REQUIREMENT-AND-SPEND-FEASIBILITY-HANDOFF-CONTRACT-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001"
    assert lane["resolution_artifact"] == "POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001"


def test_governance_power_mde_diagnostics_lane_contract_resolved() -> None:
    inv = investigations_by_id()["INV-POWER-MDE-DIAGNOSTICS-LANE-CONTRACT-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001"


def test_governance_power_mde_diagnostics_lane_contract_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "POWER-MDE-DIAGNOSTICS-LANE-CONTRACT-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "POWER_MDE_DIAGNOSTICS_RUNTIME_001"
    assert lane["resolution_artifact"] == "POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001"


def test_governance_power_mde_diagnostics_runtime_resolved() -> None:
    inv = investigations_by_id()["INV-POWER-MDE-DIAGNOSTICS-RUNTIME-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "POWER_MDE_DIAGNOSTICS_RUNTIME_001"


def test_governance_power_mde_diagnostics_runtime_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "POWER-MDE-DIAGNOSTICS-RUNTIME-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001"
    assert lane["resolution_artifact"] == "POWER_MDE_DIAGNOSTICS_RUNTIME_001"


def test_governance_design_cell_structure_assignment_contract_resolved() -> None:
    inv = investigations_by_id()["INV-DESIGN-CELL-STRUCTURE-AND-ASSIGNMENT-CONTRACT-001"]
    assert inv.status == "RESOLVED"
    assert inv.resolution_artifact == "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001"


def test_governance_design_cell_structure_assignment_contract_lane_complete() -> None:
    reg = load_registry()
    lane = next(
        b for b in reg["roadmap_lane_bindings"]
        if b["lane_id"] == "DESIGN-CELL-STRUCTURE-AND-ASSIGNMENT-CONTRACT-001"
    )
    assert lane["status"] == "complete"
    assert lane["next_artifact"] == "DESIGN_CELL_STRUCTURE_RUNTIME_001"
    assert lane["resolution_artifact"] == "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001"
