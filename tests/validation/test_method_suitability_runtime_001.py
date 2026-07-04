"""Tests for METHOD_SUITABILITY_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.method_suitability_runtime_001 import (
    MethodFamilySuitabilityStatus,
    MethodHandoffStatus,
    MethodSuitabilityConfig,
    ReviewRequirementType,
    evaluate_method_family_suitability,
    evaluate_method_suitability,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_SUITABILITY_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/METHOD_SUITABILITY_RUNTIME_001_REPORT.md"

_UPSTREAM_READY = {
    "profiler_status": "PASS",
    "geo_feasibility_status": "PASS",
    "spend_feasibility_status": "PASS",
    "power_mde_status": "PASS",
    "design_cell_structure_status": "PASS",
    "scenario_policy_feasibility_status": "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE",
    "assignment_feasibility_status": "ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME",
}

_GOV_BASE = {
    "instrument_catalog_status": "AVAILABLE",
    "method_roadmap_status": "CURRENT",
    "governed_methods": ["TBR_RIDGE_FAMILY", "DID_FAMILY"],
}


def _packet(**extra: object) -> dict:
    base = {
        "design_id": "test_design",
        "design_structure_type": "SINGLE_TREATMENT_CONTROL",
        "upstream_statuses": dict(_UPSTREAM_READY),
        "contrast_summaries": [{
            "contrast_id": "T1_vs_C0",
            "contrast_type": "GO_DARK_VS_BAU",
            "estimand_label": "GO_DARK_VS_BAU",
            "bau_control_preserved": True,
            "manipulation_policy": "GO_DARK",
        }],
        "estimand_summaries": ["GO_DARK_VS_BAU"],
        "governance_summary": dict(_GOV_BASE),
        "candidate_method_family_review_targets": ["TBR_RIDGE_FAMILY", "DID_FAMILY"],
        "assignment_feasibility_summary": {
            "assignment_feasibility_status": "ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME",
        },
        "power_mde_summary": {"power_mde_status": "PASS"},
        "spend_summary": {"spend_feasibility_status": "PASS"},
        "scenario_policy_summary": {
            "scenario_policy_status": "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE",
        },
    }
    base.update(extra)
    return base


def _family_status(report: object, family: str) -> MethodFamilySuitabilityStatus:
    for entry in report.method_family_suitability_reports:
        if entry.method_family == family:
            return entry.suitability_status
    raise AssertionError(f"family {family} not found")


def _instrument_status(report: object, instrument_id: str) -> MethodFamilySuitabilityStatus:
    for entry in report.instrument_suitability_reports:
        if entry.instrument_id == instrument_id:
            return entry.suitability_status
    raise AssertionError(f"instrument {instrument_id} not found")


def _instrument_entry(report: object, instrument_id: str) -> object:
    for entry in report.instrument_suitability_reports:
        if entry.instrument_id == instrument_id:
            return entry
    raise AssertionError(f"instrument {instrument_id} not found")


# --- Upstream gates ---


def test_blocked_profiler_blocks() -> None:
    p = _packet()
    p["upstream_statuses"]["profiler_status"] = "BLOCKED"
    report = evaluate_method_suitability(p)
    assert report.handoff_status == MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_DATA_READINESS


def test_blocked_geo_blocks() -> None:
    p = _packet()
    p["upstream_statuses"]["geo_feasibility_status"] = "BLOCKED"
    report = evaluate_method_suitability(p)
    assert report.handoff_status == MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_GEO_FEASIBILITY


def test_blocked_design_structure_blocks() -> None:
    p = _packet()
    p["upstream_statuses"]["design_cell_structure_status"] = "BLOCKED"
    report = evaluate_method_suitability(p)
    assert report.handoff_status == MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_DESIGN_STRUCTURE


def test_blocked_scenario_policy_blocks_by_default() -> None:
    p = _packet()
    p["upstream_statuses"]["scenario_policy_feasibility_status"] = "SCENARIO_BLOCKED"
    report = evaluate_method_suitability(p)
    assert report.handoff_status == MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_SCENARIO_POLICY


def test_blocked_scenario_provisional_when_config_allows() -> None:
    p = _packet()
    p["upstream_statuses"]["scenario_policy_feasibility_status"] = "SCENARIO_BLOCKED"
    cfg = MethodSuitabilityConfig(block_scenario_policy_blocked=False)
    report = evaluate_method_suitability(p, cfg)
    assert report.handoff_status in (
        MethodHandoffStatus.METHOD_HANDOFF_PROVISIONAL,
        MethodHandoffStatus.METHOD_HANDOFF_READY_WITH_WARNINGS,
        MethodHandoffStatus.METHOD_HANDOFF_READY_FOR_SUITABILITY_REVIEW,
    )


def test_blocked_assignment_blocks_by_default() -> None:
    p = _packet()
    p["upstream_statuses"]["assignment_feasibility_status"] = "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY"
    report = evaluate_method_suitability(p)
    assert report.handoff_status == MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_ASSIGNMENT_FEASIBILITY


def test_blocked_assignment_provisional_when_config_allows() -> None:
    p = _packet()
    p["upstream_statuses"]["assignment_feasibility_status"] = "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY"
    cfg = MethodSuitabilityConfig(block_assignment_feasibility_blocked=False)
    report = evaluate_method_suitability(p, cfg)
    assert report.handoff_status == MethodHandoffStatus.METHOD_HANDOFF_PROVISIONAL


def test_blocked_power_mde_emits_low_power_review() -> None:
    p = _packet()
    p["power_mde_summary"] = {"power_mde_status": "BLOCKED"}
    report = evaluate_method_suitability(p)
    assert ReviewRequirementType.LOW_POWER_OR_HIGH_MDE_REVIEW.value in report.review_requirements
    assert report.power_mde_handoff_report.inference_ready_claim_allowed is False


def test_blocked_power_mde_blocks_when_config_requires() -> None:
    p = _packet()
    p["power_mde_summary"] = {"power_mde_status": "BLOCKED"}
    cfg = MethodSuitabilityConfig(block_power_mde_blocked=True)
    report = evaluate_method_suitability(p, cfg)
    assert report.handoff_status == MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_POWER_MDE_READINESS


# --- Estimand gates ---


def test_missing_estimand_blocks_by_default() -> None:
    p = _packet()
    p.pop("estimand_summaries")
    p["contrast_summaries"] = [{"contrast_id": "T1_vs_C0", "contrast_type": "GO_DARK_VS_BAU"}]
    report = evaluate_method_suitability(p)
    assert report.handoff_status == MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_MISSING_ESTIMAND


def test_standard_go_dark_emits_standard_incrementality_review() -> None:
    report = evaluate_method_suitability(_packet())
    assert ReviewRequirementType.STANDARD_INCREMENTALITY_REVIEW.value in report.review_requirements
    assert report.estimand_gate_report.standard_incrementality_allowed


def test_heavy_up_bau_preserved_emits_standard_review() -> None:
    p = _packet()
    p["contrast_summaries"] = [{
        "contrast_id": "T1_vs_C0",
        "contrast_type": "HEAVY_UP_VS_BAU",
        "estimand_label": "HEAVY_UP_VS_BAU",
        "bau_control_preserved": True,
    }]
    p["estimand_summaries"] = ["HEAVY_UP_VS_BAU"]
    report = evaluate_method_suitability(p)
    assert ReviewRequirementType.STANDARD_INCREMENTALITY_REVIEW.value in report.review_requirements


def test_manipulated_control_blocks_standard_incrementality() -> None:
    p = _packet()
    p["contrast_summaries"] = [{
        "contrast_id": "T1_vs_C0",
        "contrast_type": "GO_DARK_VS_BAU",
        "estimand_label": "GO_DARK_VS_BAU",
        "bau_control_preserved": False,
        "manipulated_control": True,
    }]
    report = evaluate_method_suitability(p)
    assert not report.estimand_gate_report.standard_incrementality_allowed
    assert ReviewRequirementType.DIFFERENCE_IN_POLICY_REVIEW.value in report.review_requirements


def test_dosage_contrast_requires_dosage_review() -> None:
    p = _packet()
    p["design_structure_type"] = "DOSAGE_CONTRAST"
    p["estimand_summaries"] = ["DOSAGE_CONTRAST"]
    p["contrast_summaries"] = [{
        "contrast_id": "low_vs_high",
        "contrast_type": "DOSAGE_LOW_VS_HIGH",
        "estimand_label": "DOSAGE_CONTRAST",
    }]
    report = evaluate_method_suitability(p)
    assert ReviewRequirementType.DOSAGE_CONTRAST_REVIEW.value in report.review_requirements
    assert report.handoff_status in (
        MethodHandoffStatus.METHOD_HANDOFF_REQUIRES_DOSAGE_REVIEW,
        MethodHandoffStatus.METHOD_HANDOFF_READY_WITH_WARNINGS,
    )


def test_difference_in_policy_requires_dip_review() -> None:
    p = _packet()
    p["design_structure_type"] = "DIFFERENCE_IN_POLICY"
    p["estimand_summaries"] = ["DIFFERENCE_IN_POLICY"]
    report = evaluate_method_suitability(p)
    assert ReviewRequirementType.DIFFERENCE_IN_POLICY_REVIEW.value in report.review_requirements


def test_budget_reallocation_requires_budget_review() -> None:
    p = _packet()
    p["design_structure_type"] = "BUDGET_REALLOCATION"
    p["estimand_summaries"] = ["BUDGET_REALLOCATION"]
    report = evaluate_method_suitability(p)
    assert ReviewRequirementType.BUDGET_REALLOCATION_REVIEW.value in report.review_requirements


def test_go_live_requires_go_live_review() -> None:
    p = _packet()
    p["design_structure_type"] = "GO_LIVE"
    p["estimand_summaries"] = ["GO_LIVE"]
    report = evaluate_method_suitability(p)
    assert ReviewRequirementType.GO_LIVE_REVIEW.value in report.review_requirements


# --- Review requirements ---


def test_shared_control_conflict_emits_common_control_review() -> None:
    p = _packet()
    p["scenario_policy_summary"]["shared_control_conflict"] = True
    report = evaluate_method_suitability(p)
    assert ReviewRequirementType.COMMON_CONTROL_REVIEW.value in report.review_requirements


def test_split_control_recheck_emits_redesign_review() -> None:
    p = _packet()
    p["assignment_feasibility_summary"]["redesign_recheck_required"] = True
    report = evaluate_method_suitability(p)
    assert report.handoff_status == MethodHandoffStatus.METHOD_HANDOFF_REQUIRES_REDESIGN_RECHECK
    assert ReviewRequirementType.SPLIT_CONTROL_REDESIGN_REVIEW.value in report.review_requirements


def test_out_of_historical_support_emits_review() -> None:
    p = _packet()
    p["spend_summary"]["historical_support_status"] = "OUT_OF_HISTORICAL_SUPPORT"
    report = evaluate_method_suitability(p)
    assert ReviewRequirementType.OUT_OF_HISTORICAL_SUPPORT_REVIEW.value in report.review_requirements


def test_interference_risk_emits_review() -> None:
    p = _packet()
    p["interference_risk_status"] = "HIGH"
    report = evaluate_method_suitability(p)
    assert ReviewRequirementType.INTERFERENCE_RISK_REVIEW.value in report.review_requirements


def test_upstream_method_review_required_preserved() -> None:
    p = _packet()
    p["contrast_summaries"][0]["method_suitability_review_required"] = True
    report = evaluate_method_suitability(p)
    assert ReviewRequirementType.METHOD_GOVERNANCE_REVIEW.value in report.review_requirements


def test_missing_governance_emits_governance_review() -> None:
    p = _packet()
    p["governance_summary"] = {}
    report = evaluate_method_suitability(p)
    assert ReviewRequirementType.METHOD_GOVERNANCE_REVIEW.value in report.review_requirements


# --- Method-family classification ---


def test_governed_family_eligible_for_review() -> None:
    report = evaluate_method_suitability(_packet())
    status = _family_status(report, "TBR_RIDGE_FAMILY")
    assert status in (
        MethodFamilySuitabilityStatus.METHOD_FAMILY_ELIGIBLE_FOR_REVIEW,
        MethodFamilySuitabilityStatus.METHOD_FAMILY_ELIGIBLE_WITH_WARNINGS,
    )


def test_restricted_family_marked_restricted() -> None:
    p = _packet()
    p["governance_summary"]["restricted_methods"] = ["SCM_FAMILY"]
    p["candidate_method_family_review_targets"] = ["SCM_FAMILY", "DID_FAMILY"]
    report = evaluate_method_suitability(p)
    assert _family_status(report, "SCM_FAMILY") == MethodFamilySuitabilityStatus.METHOD_FAMILY_RESTRICTED


def test_diagnostic_only_family_marked() -> None:
    p = _packet()
    p["governance_summary"]["diagnostic_only_methods"] = ["AUGSYNTH_FAMILY"]
    p["candidate_method_family_review_targets"] = ["AUGSYNTH_FAMILY"]
    report = evaluate_method_suitability(p)
    assert _family_status(report, "AUGSYNTH_FAMILY") == MethodFamilySuitabilityStatus.METHOD_FAMILY_DIAGNOSTIC_ONLY


def test_blocked_family_marked_blocked() -> None:
    p = _packet()
    p["governance_summary"]["blocked_methods"] = ["SCM_FAMILY"]
    p["candidate_method_family_review_targets"] = ["SCM_FAMILY"]
    report = evaluate_method_suitability(p)
    assert _family_status(report, "SCM_FAMILY") == MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED


def test_unknown_family_not_evaluated() -> None:
    p = _packet()
    p["candidate_method_family_review_targets"] = ["UNKNOWN_METHOD_FAMILY"]
    report = evaluate_method_suitability(p)
    assert _family_status(report, "UNKNOWN_METHOD_FAMILY") == MethodFamilySuitabilityStatus.METHOD_FAMILY_NOT_EVALUATED


def test_blocked_handoff_prevents_eligible_family() -> None:
    p = _packet()
    p["upstream_statuses"]["profiler_status"] = "BLOCKED"
    report = evaluate_method_suitability(p)
    for entry in report.method_family_suitability_reports:
        assert entry.suitability_status != MethodFamilySuitabilityStatus.METHOD_FAMILY_ELIGIBLE_FOR_REVIEW


# --- Handoff preservation ---


def test_scenario_status_preserved() -> None:
    report = evaluate_method_suitability(_packet())
    assert report.scenario_policy_handoff_report.preserved_status is not None


def test_assignment_status_preserved() -> None:
    report = evaluate_method_suitability(_packet())
    assert report.assignment_handoff_report.preserved_status is not None


def test_power_mde_status_preserved() -> None:
    report = evaluate_method_suitability(_packet())
    assert report.power_mde_handoff_report.preserved_status == "PASS"


def test_spend_historical_support_preserved() -> None:
    p = _packet()
    p["spend_summary"]["historical_support_status"] = "POLICY_NEAR_HISTORICAL_SUPPORT_BOUNDARY"
    report = evaluate_method_suitability(p)
    assert report.spend_handoff_report.historical_support_status is not None


def test_governance_stance_preserved() -> None:
    report = evaluate_method_suitability(_packet())
    assert report.governance_handoff_report.governed_methods


def test_multiple_packets_no_ranking() -> None:
    report = evaluate_method_suitability([_packet(design_id="d1"), _packet(design_id="d2")])
    assert report.design_id is None
    assert len(report.design_reports) == 2
    assert report.aggregate_summary is not None


# --- Claim boundaries ---


def test_eligible_does_not_select_estimator() -> None:
    report = evaluate_method_suitability(_packet())
    assert not report.claim_boundary_report.estimator_selected
    assert not report.claim_boundary_report.method_family_selected


def test_no_inference_method_selection() -> None:
    report = evaluate_method_suitability(_packet())
    assert not report.claim_boundary_report.inference_method_selected


def test_no_p_value_ci_lift_roi() -> None:
    report = evaluate_method_suitability(_packet())
    assert not report.claim_boundary_report.p_value_computed
    assert not report.claim_boundary_report.confidence_interval_computed
    assert not report.claim_boundary_report.lift_computed
    assert not report.claim_boundary_report.roi_computed


def test_no_production_authorization() -> None:
    report = evaluate_method_suitability(_packet())
    assert not report.claim_boundary_report.production_authorization_granted
    assert not report.claim_boundary_report.method_promotion_authorized


def test_no_geo_assignment_or_randomization() -> None:
    report = evaluate_method_suitability(_packet())
    assert not report.claim_boundary_report.geo_assignment_computed
    assert not report.claim_boundary_report.randomization_computed


def test_evaluate_alias() -> None:
    report = evaluate_method_family_suitability(_packet())
    assert report.artifact_id == "METHOD_SUITABILITY_RUNTIME_001"


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["verdict"] == (
        "method_suitability_runtime_implemented_review_classification_only_no_estimator_or_inference_authorization"
    )
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["instrument_suitability_matrix_implemented"] is True
    assert summary["method_family_only_classification"] is False
    assert summary["method_winner_selected"] is False


# --- Instrument suitability matrix ---


def test_evaluates_multiple_candidate_instruments() -> None:
    report = evaluate_method_suitability(_packet())
    assert report.candidate_instrument_count >= 2
    assert len(report.instrument_suitability_reports) == report.candidate_instrument_count
    assert len(report.instrument_suitability_matrix) == report.candidate_instrument_count


def test_does_not_choose_winner_or_rank_instruments() -> None:
    report = evaluate_method_suitability(_packet())
    assert not report.claim_boundary_report.method_winner_selected
    assert not report.claim_boundary_report.primary_readout_stack_selected
    assert not report.claim_boundary_report.sensitivity_stack_selected
    assert not report.claim_boundary_report.diagnostic_stack_selected
    matrix = report.instrument_suitability_matrix
    assert all("rank" not in row for row in matrix)
    assert all("winner" not in str(row).lower() for row in matrix)


def test_scm_unit_jackknife_blocked_on_multi_cell_common_control() -> None:
    p = _packet()
    p["design_structure_type"] = "MULTI_CELL_COMMON_CONTROL"
    p["candidate_instrument_review_targets"] = ["SCM_UNIT_JACKKNIFE"]
    report = evaluate_method_suitability(p)
    entry = _instrument_entry(report, "SCM_UNIT_JACKKNIFE")
    assert entry.suitability_status in (
        MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED,
        MethodFamilySuitabilityStatus.METHOD_FAMILY_RESTRICTED,
    )
    assert entry.design_compatibility_status in ("BLOCKED", "RESTRICTED")
    assert entry.blocking_reasons


def test_scm_placebo_diagnostic_only() -> None:
    p = _packet(candidate_instrument_review_targets=["SCM_PLACEBO"])
    report = evaluate_method_suitability(p)
    assert _instrument_status(report, "SCM_PLACEBO") == (
        MethodFamilySuitabilityStatus.METHOD_FAMILY_DIAGNOSTIC_ONLY
    )
    assert _instrument_entry(report, "SCM_PLACEBO").diagnostic_only_reason is not None


def test_tbr_ridge_brb_restricted_by_governance() -> None:
    p = _packet()
    p["governance_summary"]["restricted_instruments"] = ["TBR_RIDGE_BRB"]
    p["candidate_instrument_review_targets"] = ["TBR_RIDGE_BRB"]
    report = evaluate_method_suitability(p)
    assert _instrument_status(report, "TBR_RIDGE_BRB") == (
        MethodFamilySuitabilityStatus.METHOD_FAMILY_RESTRICTED
    )


def test_tbr_ridge_placebo_diagnostic_or_restricted() -> None:
    p = _packet(candidate_instrument_review_targets=["TBR_RIDGE_PLACEBO"])
    report = evaluate_method_suitability(p)
    status = _instrument_status(report, "TBR_RIDGE_PLACEBO")
    assert status in (
        MethodFamilySuitabilityStatus.METHOD_FAMILY_DIAGNOSTIC_ONLY,
        MethodFamilySuitabilityStatus.METHOD_FAMILY_RESTRICTED,
    )


def test_did_2x2_point_estimate_eligible_with_warnings_on_parallel_trends() -> None:
    p = _packet()
    p["parallel_trends_warning_status"] = "WARNING"
    p["candidate_instrument_review_targets"] = ["DID_2X2_POINT_ESTIMATE"]
    report = evaluate_method_suitability(p)
    assert _instrument_status(report, "DID_2X2_POINT_ESTIMATE") == (
        MethodFamilySuitabilityStatus.METHOD_FAMILY_ELIGIBLE_WITH_WARNINGS
    )


def test_augsynth_jackknife_diagnostic_or_restricted() -> None:
    p = _packet(candidate_instrument_review_targets=["AUGSYNTH_JACKKNIFE"])
    report = evaluate_method_suitability(p)
    assert _instrument_status(report, "AUGSYNTH_JACKKNIFE") in (
        MethodFamilySuitabilityStatus.METHOD_FAMILY_DIAGNOSTIC_ONLY,
        MethodFamilySuitabilityStatus.METHOD_FAMILY_RESTRICTED,
    )


def test_ab_standard_inference_blocked_on_geo_panel() -> None:
    p = _packet(candidate_instrument_review_targets=["AB_STANDARD_INFERENCE"])
    report = evaluate_method_suitability(p)
    entry = _instrument_entry(report, "AB_STANDARD_INFERENCE")
    assert entry.suitability_status == MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED
    assert entry.design_compatibility_status == "BLOCKED"


def test_dosage_design_blocks_standard_incrementality_instruments() -> None:
    p = _packet()
    p["design_structure_type"] = "DOSAGE_CONTRAST"
    p["estimand_summaries"] = ["DOSAGE_CONTRAST"]
    p["contrast_summaries"] = [{
        "contrast_id": "low_vs_high",
        "contrast_type": "DOSAGE_LOW_VS_HIGH",
        "estimand_label": "DOSAGE_CONTRAST",
    }]
    p["candidate_instrument_review_targets"] = ["SCM_UNIT_JACKKNIFE", "TBR_RIDGE_BRB"]
    report = evaluate_method_suitability(p)
    for iid in ("SCM_UNIT_JACKKNIFE", "TBR_RIDGE_BRB"):
        assert _instrument_status(report, iid) == MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED


def test_missing_instrument_governance_emits_review_and_provisional() -> None:
    p = _packet()
    p["governance_summary"] = {}
    p.pop("candidate_method_family_review_targets", None)
    report = evaluate_method_suitability(p)
    assert ReviewRequirementType.METHOD_GOVERNANCE_REVIEW.value in report.review_requirements
    assert report.candidate_instrument_count == 10


def test_diagnostic_only_instruments_never_promoted() -> None:
    p = _packet(candidate_instrument_review_targets=["SCM_PLACEBO", "AUGSYNTH_JACKKNIFE"])
    report = evaluate_method_suitability(p)
    for iid in ("SCM_PLACEBO", "AUGSYNTH_JACKKNIFE"):
        entry = _instrument_entry(report, iid)
        assert entry.suitability_status == MethodFamilySuitabilityStatus.METHOD_FAMILY_DIAGNOSTIC_ONLY
    assert not report.claim_boundary_report.method_promotion_authorized


def test_restricted_instruments_not_eligible_for_production() -> None:
    p = _packet()
    p["governance_summary"]["restricted_instruments"] = ["TBR_RIDGE_BRB"]
    p["candidate_instrument_review_targets"] = ["TBR_RIDGE_BRB"]
    report = evaluate_method_suitability(p)
    entry = _instrument_entry(report, "TBR_RIDGE_BRB")
    assert entry.suitability_status == MethodFamilySuitabilityStatus.METHOD_FAMILY_RESTRICTED
    assert entry.suitability_status != MethodFamilySuitabilityStatus.METHOD_FAMILY_ELIGIBLE_FOR_REVIEW


def test_blocked_instruments_include_blocking_reasons() -> None:
    p = _packet(candidate_instrument_review_targets=["AB_STANDARD_INFERENCE"])
    report = evaluate_method_suitability(p)
    entry = _instrument_entry(report, "AB_STANDARD_INFERENCE")
    assert entry.suitability_status == MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED
    assert entry.blocking_reasons


def test_eligible_instruments_are_review_only_not_approved() -> None:
    p = _packet(candidate_instrument_review_targets=["DID_2X2_POINT_ESTIMATE"])
    report = evaluate_method_suitability(p)
    status = _instrument_status(report, "DID_2X2_POINT_ESTIMATE")
    assert status in (
        MethodFamilySuitabilityStatus.METHOD_FAMILY_ELIGIBLE_FOR_REVIEW,
        MethodFamilySuitabilityStatus.METHOD_FAMILY_ELIGIBLE_WITH_WARNINGS,
    )
    assert not report.claim_boundary_report.estimator_inference_authorized
    assert not report.claim_boundary_report.production_authorization_granted


def test_did_bootstrap_blocked_as_inference_alias() -> None:
    p = _packet(candidate_instrument_review_targets=["DID_BOOTSTRAP"])
    report = evaluate_method_suitability(p)
    status = _instrument_status(report, "DID_BOOTSTRAP")
    assert status == MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED


def test_instrument_matrix_includes_production_catalog_overlay() -> None:
    p = _packet(candidate_instrument_review_targets=["DID_2X2_POINT_ESTIMATE"])
    report = evaluate_method_suitability(p)
    row = next(r for r in report.instrument_suitability_matrix if r["instrument_id"] == "DID_2X2_POINT_ESTIMATE")
    assert row.get("production_catalog_status")
    assert row.get("is_production_blocked") is False
    assert row.get("production_restrictions")
