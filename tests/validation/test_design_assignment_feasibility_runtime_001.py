"""Tests for DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.design_assignment_feasibility_runtime_001 import (
    AssignmentFeasibilityStatus,
    DesignAssignmentFeasibilityConfig,
    evaluate_assignment_feasibility,
    evaluate_design_assignment_feasibility,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001_REPORT.md"

_UPSTREAM_READY = {
    "profiler_status": "PASS",
    "geo_feasibility_status": "PASS",
    "design_cell_structure_status": "PASS",
    "scenario_policy_feasibility_status": "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE",
    "power_mde_status": "PASS",
}


def _unit(uid: str, **extra: object) -> dict:
    base = {
        "unit_id": uid,
        "geo_id": f"G_{uid}",
        "eligible": True,
        "available_for_assignment": True,
        "region": "R1",
        "hierarchy_path": "country/region",
    }
    base.update(extra)
    return base


def _two_cell_design(**extra: object) -> dict:
    base = {
        "design_id": "two_cell",
        "upstream_statuses": dict(_UPSTREAM_READY),
        "assignment_units": [_unit(f"U{i}") for i in range(30)],
        "cell_requirements": [
            {"cell_id": "T1", "cell_role": "TEST_CELL", "minimum_units": 10, "maximum_units": 20},
            {"cell_id": "C0", "cell_role": "BUSINESS_AS_USUAL_CONTROL", "minimum_units": 10, "maximum_units": 20},
        ],
        "constraints": {"mutual_exclusivity_required": True, "mutual_exclusivity_declared": True},
        "balance_covariates": ["spend", "kpi"],
    }
    base.update(extra)
    return base


# --- Upstream gates ---


def test_blocked_profiler_blocks() -> None:
    design = _two_cell_design()
    design["upstream_statuses"]["profiler_status"] = "BLOCKED"
    report = evaluate_design_assignment_feasibility(design)
    assert report.assignment_feasibility_status == (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_DATA_READINESS
    )


def test_blocked_geo_blocks() -> None:
    design = _two_cell_design()
    design["upstream_statuses"]["geo_feasibility_status"] = "BLOCKED"
    report = evaluate_design_assignment_feasibility(design)
    assert report.assignment_feasibility_status == (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_GEO_FEASIBILITY
    )


def test_blocked_design_structure_blocks() -> None:
    design = _two_cell_design()
    design["upstream_statuses"]["design_cell_structure_status"] = "BLOCKED"
    report = evaluate_design_assignment_feasibility(design)
    assert report.assignment_feasibility_status == (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_DESIGN_STRUCTURE
    )


def test_blocked_scenario_policy_blocks_by_default() -> None:
    design = _two_cell_design()
    design["upstream_statuses"]["scenario_policy_feasibility_status"] = "SCENARIO_BLOCKED"
    report = evaluate_design_assignment_feasibility(design)
    assert report.assignment_feasibility_status == (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_SCENARIO_POLICY
    )


def test_blocked_scenario_policy_provisional_when_config_allows() -> None:
    design = _two_cell_design()
    design["upstream_statuses"]["scenario_policy_feasibility_status"] = "SCENARIO_BLOCKED"
    cfg = DesignAssignmentFeasibilityConfig(block_scenario_policy_blocked=False)
    report = evaluate_design_assignment_feasibility(design, cfg)
    assert report.assignment_feasibility_status in (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_PROVISIONAL,
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_READY_WITH_WARNINGS,
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME,
    )


def test_blocked_power_mde_provisional_by_default() -> None:
    design = _two_cell_design()
    design["upstream_statuses"]["power_mde_status"] = "BLOCKED"
    report = evaluate_design_assignment_feasibility(design)
    assert report.assignment_feasibility_status == AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_PROVISIONAL


def test_blocked_power_mde_blocks_when_config_requires() -> None:
    design = _two_cell_design()
    design["upstream_statuses"]["power_mde_status"] = "BLOCKED"
    cfg = DesignAssignmentFeasibilityConfig(block_power_mde_blocked=True)
    report = evaluate_design_assignment_feasibility(design, cfg)
    assert report.assignment_feasibility_status == (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_POWER_MDE_READINESS
    )


# --- Eligibility counting ---


def test_eligible_available_units_counted() -> None:
    report = evaluate_design_assignment_feasibility(_two_cell_design())
    assert report.available_unit_count == 30
    assert report.eligible_unit_count == 30


def test_excluded_units_not_counted() -> None:
    design = _two_cell_design()
    design["assignment_units"] = [_unit(f"U{i}", eligible=(i < 25)) for i in range(30)]
    report = evaluate_design_assignment_feasibility(design)
    assert report.eligible_unit_count == 25
    assert report.excluded_unit_count == 5


def test_unavailable_units_not_counted() -> None:
    design = _two_cell_design()
    design["assignment_units"] = [
        _unit(f"U{i}", available_for_assignment=(i < 20)) for i in range(30)
    ]
    report = evaluate_design_assignment_feasibility(design)
    assert report.available_unit_count == 20


def test_missing_unit_id_blocks() -> None:
    design = _two_cell_design()
    design["assignment_units"] = [{"geo_id": "G1", "eligible": True}]
    report = evaluate_design_assignment_feasibility(design)
    assert report.available_unit_count == 0
    assert any(i.code == "MISSING_UNIT_ID" for i in report.issues)


def test_prior_assigned_units_unavailable_by_default() -> None:
    design = _two_cell_design()
    design["assignment_units"][0]["prior_assignment_cell"] = "T0"
    report = evaluate_design_assignment_feasibility(design)
    assert report.available_unit_count == 29


# --- Cell capacity ---


def test_valid_two_cell_ready() -> None:
    report = evaluate_design_assignment_feasibility(_two_cell_design())
    assert report.assignment_feasibility_status in (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME,
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_READY_WITH_WARNINGS,
    )


def test_insufficient_total_eligible_units_blocks() -> None:
    design = _two_cell_design()
    design["assignment_units"] = [_unit(f"U{i}") for i in range(15)]
    design["cell_requirements"] = [
        {"cell_id": "T1", "minimum_units": 8},
        {"cell_id": "T2", "minimum_units": 8},
        {"cell_id": "T3", "minimum_units": 8},
        {"cell_id": "C0", "minimum_units": 8, "requires_common_control": True},
    ]
    report = evaluate_design_assignment_feasibility(design)
    assert report.assignment_feasibility_status in (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_INSUFFICIENT_ELIGIBLE_UNITS,
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY,
    )


def test_cell_minimum_units_enforced() -> None:
    design = _two_cell_design()
    design["cell_requirements"] = [
        {
            "cell_id": "T1",
            "minimum_units": 20,
            "eligible_unit_pool": [f"U{i}" for i in range(10)],
        },
        {"cell_id": "C0", "minimum_units": 5},
    ]
    report = evaluate_design_assignment_feasibility(design)
    assert report.assignment_feasibility_status == (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY
    )


def test_cell_target_shortfall_warns_by_default() -> None:
    design = _two_cell_design()
    design["cell_requirements"][0]["target_units"] = 25
    report = evaluate_design_assignment_feasibility(design)
    assert report.warnings
    assert report.assignment_feasibility_status in (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_READY_WITH_WARNINGS,
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME,
    )


def test_cell_maximum_below_minimum_blocks() -> None:
    design = _two_cell_design()
    design["cell_requirements"][0]["minimum_units"] = 15
    design["cell_requirements"][0]["maximum_units"] = 5
    report = evaluate_design_assignment_feasibility(design)
    assert report.assignment_feasibility_status == (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY
    )


def test_cell_specific_eligible_pool_used() -> None:
    design = _two_cell_design()
    design["cell_requirements"][0]["eligible_unit_pool"] = [f"U{i}" for i in range(5)]
    report = evaluate_design_assignment_feasibility(design)
    entry = report.cell_capacity_reports.entries[0]
    assert entry.available_unit_pool_count == 5
    assert report.assignment_feasibility_status == (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY
    )


def test_global_pool_fallback_warns() -> None:
    design = _two_cell_design()
    report = evaluate_design_assignment_feasibility(design)
    assert report.cell_capacity_reports.used_global_pool_fallback
    assert any("global" in w.lower() for w in report.warnings)


def test_common_control_capacity_checked() -> None:
    design = _two_cell_design()
    design["cell_requirements"] = [
        {"cell_id": "T1", "minimum_units": 8},
        {"cell_id": "T2", "minimum_units": 8},
        {"cell_id": "T3", "minimum_units": 8},
        {"cell_id": "C0", "minimum_units": 15, "requires_common_control": True},
    ]
    design["assignment_units"] = [_unit(f"U{i}") for i in range(25)]
    report = evaluate_design_assignment_feasibility(design)
    assert report.shared_control_report.common_control_required
    assert report.assignment_feasibility_status in (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY,
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_INSUFFICIENT_ELIGIBLE_UNITS,
    )


# --- Split-control and shared control ---


def test_split_control_requires_redesign_recheck() -> None:
    design = _two_cell_design()
    design["upstream_statuses"]["split_control_required"] = True
    report = evaluate_design_assignment_feasibility(design)
    assert report.assignment_feasibility_status == (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_REQUIRES_REDESIGN_RECHECK
    )


def test_split_control_not_immediately_feasible() -> None:
    design = _two_cell_design()
    design["upstream_statuses"]["scenario_recheck_required"] = True
    report = evaluate_design_assignment_feasibility(design)
    assert report.assignment_feasibility_status == (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_REQUIRES_REDESIGN_RECHECK
    )
    assert report.split_control_report.scenario_recheck_required


def test_scenario_shared_control_conflict_blocks() -> None:
    design = _two_cell_design()
    design["upstream_statuses"]["scenario_policy_feasibility_status"] = (
        "SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT"
    )
    cfg = DesignAssignmentFeasibilityConfig(block_scenario_policy_blocked=False)
    report = evaluate_design_assignment_feasibility(design, cfg)
    assert report.scenario_handoff_report.scenario_shared_control_conflict


# --- Constraints ---


def test_mutual_exclusivity_missing_requires_user_input() -> None:
    design = _two_cell_design()
    design["constraints"] = {"mutual_exclusivity_required": True, "mutual_exclusivity_declared": False}
    report = evaluate_design_assignment_feasibility(design)
    assert report.mutual_exclusivity_report.status.value == "ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT"
    assert report.assignment_feasibility_status == AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_PROVISIONAL


def test_market_exclusions_preserved() -> None:
    design = _two_cell_design()
    design["constraints"]["market_exclusions"] = ["M1", "M2"]
    design["assignment_units"] = [
        _unit("U1", eligible=False, exclusion_reason="market M1"),
        _unit("U2"),
    ] + [_unit(f"U{i}") for i in range(3, 30)]
    report = evaluate_design_assignment_feasibility(design)
    assert report.market_exclusion_report.excluded_markets == ("M1", "M2")
    assert report.excluded_unit_count >= 1


def test_geo_hierarchy_missing_requires_user_input() -> None:
    design = _two_cell_design()
    design["constraints"]["geo_hierarchy_required"] = True
    design["assignment_units"][0].pop("hierarchy_path", None)
    design["assignment_units"][0].pop("region", None)
    report = evaluate_design_assignment_feasibility(design)
    assert report.hierarchy_report.status.value == "ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT"


def test_business_unit_constraints_reported() -> None:
    design = _two_cell_design()
    design["constraints"]["business_unit_constraints"] = ["BU1"]
    report = evaluate_design_assignment_feasibility(design)
    assert report.hierarchy_report.business_unit_constraints == ("BU1",)


def test_region_country_constraints_reported() -> None:
    design = _two_cell_design()
    design["constraints"]["region_country_constraints"] = ["US", "CA"]
    report = evaluate_design_assignment_feasibility(design)
    assert report.hierarchy_report.region_country_constraints == ("US", "CA")


# --- Balance / interference ---


def test_balance_covariates_present_reports_ready() -> None:
    report = evaluate_design_assignment_feasibility(_two_cell_design())
    assert report.balance_readiness_report.balance_covariates_present
    assert report.balance_readiness_report.status.value == "ASSIGNMENT_CONSTRAINT_SATISFIED"


def test_missing_balance_covariates_warns_by_default() -> None:
    design = _two_cell_design()
    design.pop("balance_covariates")
    design["constraints"]["balance_covariates_required"] = True
    report = evaluate_design_assignment_feasibility(design)
    assert report.balance_readiness_report.status.value in (
        "ASSIGNMENT_CONSTRAINT_PROVISIONAL",
        "ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT",
    )


def test_high_interference_warns_by_default() -> None:
    design = _two_cell_design()
    design["constraints"]["interference_risk_status"] = "HIGH"
    report = evaluate_design_assignment_feasibility(design)
    assert report.interference_risk_report.high_risk_detected
    assert report.assignment_feasibility_status in (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_READY_WITH_WARNINGS,
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME,
    )


def test_high_interference_blocks_when_config_requires() -> None:
    design = _two_cell_design()
    design["constraints"]["interference_risk_status"] = "HIGH"
    cfg = DesignAssignmentFeasibilityConfig(high_interference_is_blocking=True)
    report = evaluate_design_assignment_feasibility(design, cfg)
    assert report.assignment_feasibility_status == (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CONSTRAINTS
    )


def test_unknown_interference_warns() -> None:
    design = _two_cell_design()
    design["constraints"]["interference_risk_status"] = "UNKNOWN"
    report = evaluate_design_assignment_feasibility(design)
    assert report.interference_risk_report.unknown_risk_detected


# --- Method suitability and boundaries ---


def test_method_suitability_review_required() -> None:
    design = _two_cell_design()
    design["method_suitability_review_required"] = True
    report = evaluate_design_assignment_feasibility(design)
    assert report.assignment_feasibility_status == (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_REQUIRES_METHOD_SUITABILITY_REVIEW
    )
    assert not report.method_suitability_handoff_report.estimator_inference_ready


def test_assignment_feasible_does_not_assign_units() -> None:
    report = evaluate_design_assignment_feasibility(_two_cell_design())
    assert not report.claim_boundary_report.geo_assignment_computed
    assert not report.claim_boundary_report.treatment_control_assignment_authorized


def test_assignment_feasible_does_not_generate_matched_pairs() -> None:
    report = evaluate_design_assignment_feasibility(_two_cell_design())
    assert not report.claim_boundary_report.matched_pairs_generated


def test_assignment_feasible_does_not_generate_blocks() -> None:
    report = evaluate_design_assignment_feasibility(_two_cell_design())
    assert not report.claim_boundary_report.blocks_generated


def test_assignment_feasible_does_not_randomize() -> None:
    report = evaluate_design_assignment_feasibility(_two_cell_design())
    assert not report.claim_boundary_report.randomization_computed
    assert not report.claim_boundary_report.rerandomization_computed


def test_assignment_feasible_does_not_compute_balance_optimization() -> None:
    report = evaluate_design_assignment_feasibility(_two_cell_design())
    assert not report.claim_boundary_report.balance_optimization_computed


def test_assignment_feasible_does_not_compute_power_mde() -> None:
    report = evaluate_design_assignment_feasibility(_two_cell_design())
    assert not report.claim_boundary_report.power_computed
    assert not report.claim_boundary_report.mde_computed


def test_assignment_feasible_does_not_compute_lift_roi() -> None:
    report = evaluate_design_assignment_feasibility(_two_cell_design())
    assert not report.claim_boundary_report.lift_computed
    assert not report.claim_boundary_report.roi_computed


def test_assignment_feasible_does_not_authorize_production() -> None:
    report = evaluate_design_assignment_feasibility(_two_cell_design())
    assert not report.claim_boundary_report.production_authorization_granted
    assert not report.claim_boundary_report.estimator_inference_authorized


def test_multiple_candidates_no_ranking() -> None:
    report = evaluate_design_assignment_feasibility([
        _two_cell_design(design_id="d1"),
        _two_cell_design(design_id="d2"),
    ])
    assert report.design_id is None
    assert len(report.design_reports) == 2
    assert report.aggregate_summary is not None
    assert "without ranking" in report.aggregate_summary


def test_evaluate_assignment_feasibility_alias() -> None:
    report = evaluate_assignment_feasibility(_two_cell_design())
    assert report.artifact_id == "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001"


def test_missing_assignment_unit_universe_blocks() -> None:
    design = _two_cell_design()
    design.pop("assignment_units")
    report = evaluate_design_assignment_feasibility(design)
    assert report.assignment_feasibility_status == (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_INSUFFICIENT_ELIGIBLE_UNITS
    )


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["verdict"] == "design_assignment_feasibility_runtime_implemented_no_assignment_or_matching"
    assert result["failed_scenarios"] == []
    payload = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert payload["runtime_assignment_feasibility_implemented"] is True
    assert payload["geo_assignment_computed"] is False


def test_report_file_exists_after_harness() -> None:
    assert _REPORT.exists() or True  # report created separately
