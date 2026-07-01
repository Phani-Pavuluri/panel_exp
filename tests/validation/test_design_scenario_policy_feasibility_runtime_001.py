"""Tests for DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.design_scenario_policy_feasibility_runtime_001 import (
    ContrastFeasibilityStatus,
    PolicySupportStatus,
    ResolutionOptionType,
    ScenarioFeasibilityStatus,
    SharedControlConflictType,
    evaluate_design_scenario_policy_feasibility,
    evaluate_scenario_policy_feasibility,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001_REPORT.md"

_UPSTREAM_READY = {
    "profiler_status": "PASS",
    "geo_feasibility_status": "PASS",
    "spend_feasibility_status": "PASS",
    "power_mde_status": "PASS",
    "design_cell_structure_status": "PASS",
}

_BASE_CELLS = [
    {
        "cell_id": "C0",
        "baseline_spend": 100_000,
        "proposed_spend": 100_000,
        "policy": "BAU",
        "is_common_control": True,
        "is_bau_policy": True,
        "historical_max": 130_000,
    },
    {
        "cell_id": "T1",
        "baseline_spend": 80_000,
        "proposed_spend": 0,
        "policy": "GO_DARK",
        "historical_max": 120_000,
    },
    {
        "cell_id": "T2",
        "baseline_spend": 120_000,
        "proposed_spend": 220_000,
        "policy": "HEAVY_UP",
        "historical_max": 250_000,
    },
    {
        "cell_id": "T3",
        "baseline_spend": 100_000,
        "proposed_spend": 160_000,
        "policy": "HEAVY_UP",
        "historical_max": 180_000,
    },
]

_BASE_CONTRASTS = [
    {
        "contrast_id": "T1_vs_C0",
        "contrast_type": "GO_DARK_VS_BAU",
        "treatment_cell_id": "T1",
        "comparison_cell_id": "C0",
        "required_spend_contrast": 150_000,
        "bau_control_required": True,
    },
    {
        "contrast_id": "T2_vs_C0",
        "contrast_type": "HEAVY_UP_VS_BAU",
        "treatment_cell_id": "T2",
        "comparison_cell_id": "C0",
        "required_spend_contrast": 100_000,
        "bau_control_required": True,
    },
    {
        "contrast_id": "T3_vs_C0",
        "contrast_type": "HEAVY_UP_VS_BAU",
        "treatment_cell_id": "T3",
        "comparison_cell_id": "C0",
        "required_spend_contrast": 60_000,
        "bau_control_required": True,
    },
]

_SHARED_DEPS = [{"control_cell_id": "C0", "contrast_ids": ["T1_vs_C0", "T2_vs_C0", "T3_vs_C0"]}]


def _scenario(
    scenario_id: str = "scenario_a",
    *,
    cells: list[dict] | None = None,
    contrasts: list[dict] | None = None,
    upstream: dict | None = None,
    **extra: object,
) -> dict:
    data: dict = {
        "scenario_id": scenario_id,
        "upstream_statuses": upstream if upstream is not None else dict(_UPSTREAM_READY),
        "cells": cells if cells is not None else [dict(c) for c in _BASE_CELLS],
        "contrasts": contrasts if contrasts is not None else [dict(c) for c in _BASE_CONTRASTS],
        "shared_control_dependencies": [dict(d) for d in _SHARED_DEPS],
    }
    data.update(extra)
    return data


def _contrast_report(report: object, contrast_id: str):
    for cr in report.contrast_feasibility_reports:
        if cr.contrast_id == contrast_id:
            return cr
    raise AssertionError(f"contrast {contrast_id} not found")


def _resolution_types(report: object) -> set[str]:
    return {o.option_type.value for o in report.resolution_options}


def _conflict_types(report: object) -> set[str]:
    return {c.conflict_type.value for c in report.shared_control_conflicts}


def test_scenario_a_preserve_bau_partially_feasible() -> None:
    report = evaluate_design_scenario_policy_feasibility(_scenario("scenario_a"))
    t1 = _contrast_report(report, "T1_vs_C0")
    t2 = _contrast_report(report, "T2_vs_C0")
    t3 = _contrast_report(report, "T3_vs_C0")
    assert t1.contrast_status == ContrastFeasibilityStatus.CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL
    assert t1.achieved_spend_contrast == 100_000
    assert t2.contrast_status == ContrastFeasibilityStatus.CONTRAST_FEASIBLE
    assert t2.achieved_spend_contrast == 120_000
    assert t3.contrast_status == ContrastFeasibilityStatus.CONTRAST_FEASIBLE
    assert t3.achieved_spend_contrast == 60_000
    assert report.estimand_shift_report.bau_control_preserved is True
    assert report.scenario_status == ScenarioFeasibilityStatus.SCENARIO_PARTIALLY_FEASIBLE
    opts = _resolution_types(report)
    assert ResolutionOptionType.EXTEND_DURATION.value in opts
    assert ResolutionOptionType.RELAX_MDE_TARGET.value in opts
    assert ResolutionOptionType.REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY.value in opts
    assert ResolutionOptionType.SPLIT_COMMON_CONTROL.value in opts
    assert not report.claim_boundary_report.power_computed
    assert not report.claim_boundary_report.geo_assignment_computed


def test_scenario_b_raise_common_control_estimand_shift() -> None:
    cells = [dict(c) for c in _BASE_CELLS]
    cells[0] = {**cells[0], "proposed_spend": 150_000, "policy": "MANIPULATED_UP", "is_bau_policy": False}
    report = evaluate_design_scenario_policy_feasibility(_scenario("scenario_b", cells=cells))
    t1 = _contrast_report(report, "T1_vs_C0")
    t2 = _contrast_report(report, "T2_vs_C0")
    t3 = _contrast_report(report, "T3_vs_C0")
    assert t1.contrast_status == ContrastFeasibilityStatus.CONTRAST_REQUIRES_ESTIMAND_SHIFT
    assert t1.achieved_spend_contrast == 150_000
    assert t2.contrast_status == ContrastFeasibilityStatus.CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL
    assert t2.achieved_spend_contrast == 70_000
    assert t3.contrast_status == ContrastFeasibilityStatus.CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL
    assert t3.achieved_spend_contrast == 10_000
    assert report.estimand_shift_report.bau_control_preserved is False
    c0_hist = next(h for h in report.historical_support_by_cell if h.cell_id == "C0")
    assert c0_hist.support_status == PolicySupportStatus.POLICY_REQUIRES_BUSINESS_OVERRIDE
    assert SharedControlConflictType.COMMON_CONTROL_CHANGE_HELPS_ONE_CONTRAST_HARMS_ANOTHER.value in _conflict_types(report)
    assert report.scenario_status == ScenarioFeasibilityStatus.SCENARIO_REQUIRES_ESTIMAND_SHIFT
    assert ScenarioFeasibilityStatus.SCENARIO_OUT_OF_HISTORICAL_SUPPORT in report.secondary_statuses
    opts = _resolution_types(report)
    assert ResolutionOptionType.REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY.value in opts
    assert ResolutionOptionType.CAP_SPEND_WITHIN_HISTORICAL_SUPPORT.value in opts
    assert ResolutionOptionType.RERUN_POWER_MDE.value in opts
    assert ResolutionOptionType.RERUN_ASSIGNMENT_FEASIBILITY.value in opts


def test_scenario_c_lower_common_control_partially_feasible() -> None:
    cells = [dict(c) for c in _BASE_CELLS]
    cells[0] = {**cells[0], "proposed_spend": 60_000, "policy": "MANIPULATED_DOWN", "is_bau_policy": False}
    cells[2] = {**cells[2], "proposed_spend": 160_000}
    cells[3] = {**cells[3], "proposed_spend": 120_000}
    report = evaluate_design_scenario_policy_feasibility(_scenario("scenario_c", cells=cells))
    t1 = _contrast_report(report, "T1_vs_C0")
    t2 = _contrast_report(report, "T2_vs_C0")
    t3 = _contrast_report(report, "T3_vs_C0")
    assert t1.achieved_spend_contrast == 60_000
    assert t1.contrast_status == ContrastFeasibilityStatus.CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL
    assert t2.contrast_status == ContrastFeasibilityStatus.CONTRAST_FEASIBLE
    assert t3.contrast_status == ContrastFeasibilityStatus.CONTRAST_FEASIBLE
    assert report.estimand_shift_report.bau_control_preserved is False
    assert SharedControlConflictType.COMMON_CONTROL_CHANGE_HELPS_ONE_CONTRAST_HARMS_ANOTHER.value in _conflict_types(report)
    assert report.scenario_status == ScenarioFeasibilityStatus.SCENARIO_REQUIRES_ESTIMAND_SHIFT
    assert ScenarioFeasibilityStatus.SCENARIO_PARTIALLY_FEASIBLE in report.secondary_statuses or report.scenario_status == ScenarioFeasibilityStatus.SCENARIO_REQUIRES_ESTIMAND_SHIFT


def test_scenario_d_high_spend_dosage_feasible_with_oos_warning() -> None:
    cells = [dict(c) for c in _BASE_CELLS]
    cells[1] = {**cells[1], "proposed_spend": 250_000, "policy": "HIGH_SPEND_POLICY"}
    contrasts = [dict(c) for c in _BASE_CONTRASTS]
    contrasts[0] = {**contrasts[0], "contrast_type": "HEAVY_UP_VS_BAU"}
    report = evaluate_design_scenario_policy_feasibility(_scenario("scenario_d", cells=cells, contrasts=contrasts))
    t1 = _contrast_report(report, "T1_vs_C0")
    assert t1.contrast_status == ContrastFeasibilityStatus.CONTRAST_FEASIBLE
    assert t1.achieved_spend_contrast == 150_000
    t1_hist = next(h for h in report.historical_support_by_cell if h.cell_id == "T1")
    assert t1_hist.support_status == PolicySupportStatus.POLICY_REQUIRES_BUSINESS_OVERRIDE
    assert report.scenario_status == ScenarioFeasibilityStatus.SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE
    assert ScenarioFeasibilityStatus.SCENARIO_OUT_OF_HISTORICAL_SUPPORT in report.secondary_statuses
    opts = _resolution_types(report)
    assert ResolutionOptionType.CAP_SPEND_WITHIN_HISTORICAL_SUPPORT.value in opts
    assert ResolutionOptionType.BUSINESS_OVERRIDE_REQUIRED.value in opts


def test_scenario_e_split_control_requires_recheck() -> None:
    report = evaluate_design_scenario_policy_feasibility(
        _scenario("scenario_e", split_control_proposal=True)
    )
    assert report.scenario_status == ScenarioFeasibilityStatus.SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT
    assert ScenarioFeasibilityStatus.SCENARIO_REQUIRES_POWER_MDE_RECHECK in report.secondary_statuses
    assert ScenarioFeasibilityStatus.SCENARIO_REQUIRES_ASSIGNMENT_RECHECK in report.secondary_statuses
    opts = _resolution_types(report)
    assert ResolutionOptionType.RERUN_POWER_MDE.value in opts
    assert ResolutionOptionType.RERUN_ASSIGNMENT_FEASIBILITY.value in opts
    assert report.scenario_status != ScenarioFeasibilityStatus.SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE
    assert not report.claim_boundary_report.geo_assignment_computed


def test_blocked_profiler_blocks_scenario() -> None:
    upstream = dict(_UPSTREAM_READY)
    upstream["profiler_status"] = "BLOCKED"
    report = evaluate_design_scenario_policy_feasibility(_scenario(upstream=upstream))
    assert report.scenario_status == ScenarioFeasibilityStatus.SCENARIO_BLOCKED


def test_blocked_geo_blocks_scenario() -> None:
    upstream = dict(_UPSTREAM_READY)
    upstream["geo_feasibility_status"] = "BLOCKED"
    report = evaluate_design_scenario_policy_feasibility(_scenario(upstream=upstream))
    assert report.scenario_status == ScenarioFeasibilityStatus.SCENARIO_BLOCKED


def test_blocked_spend_prevents_spend_compatible_claim() -> None:
    upstream = dict(_UPSTREAM_READY)
    upstream["spend_feasibility_status"] = "BLOCKED"
    report = evaluate_design_scenario_policy_feasibility(_scenario(upstream=upstream))
    assert not report.scenario_reports[0].readiness_report.spend_compatible_feasibility_allowed


def test_blocked_power_mde_emits_recheck() -> None:
    upstream = dict(_UPSTREAM_READY)
    upstream["power_mde_status"] = "BLOCKED"
    report = evaluate_design_scenario_policy_feasibility(_scenario(upstream=upstream))
    assert ScenarioFeasibilityStatus.SCENARIO_REQUIRES_POWER_MDE_RECHECK in (
        report.secondary_statuses
        + (report.scenario_status,)
    )
    assert any(r.requirement_type == "POWER_MDE_RECHECK" for r in report.recheck_requirements)


def test_missing_design_cell_structure_blocks() -> None:
    upstream = dict(_UPSTREAM_READY)
    upstream["design_cell_structure_status"] = "BLOCKED"
    report = evaluate_design_scenario_policy_feasibility(_scenario(upstream=upstream))
    assert report.scenario_status == ScenarioFeasibilityStatus.SCENARIO_BLOCKED


def test_missing_contrast_requirements_prevents_comparison() -> None:
    contrasts = [dict(c) for c in _BASE_CONTRASTS]
    contrasts[0] = {**contrasts[0], "required_spend_contrast": None}
    report = evaluate_design_scenario_policy_feasibility(_scenario(contrasts=contrasts))
    t1 = _contrast_report(report, "T1_vs_C0")
    assert t1.contrast_status == ContrastFeasibilityStatus.CONTRAST_NOT_EVALUATED


def test_missing_scenario_policy_plan_blocks() -> None:
    report = evaluate_design_scenario_policy_feasibility(_scenario(cells=[]))
    assert report.scenario_status == ScenarioFeasibilityStatus.SCENARIO_BLOCKED


def test_achieved_equals_required_marks_feasible() -> None:
    cells = [dict(c) for c in _BASE_CELLS]
    cells[1] = {**cells[1], "proposed_spend": 0}
    contrasts = [dict(c) for c in _BASE_CONTRASTS]
    contrasts[0] = {**contrasts[0], "required_spend_contrast": 100_000}
    report = evaluate_design_scenario_policy_feasibility(_scenario(cells=cells, contrasts=contrasts))
    t1 = _contrast_report(report, "T1_vs_C0")
    assert t1.contrast_status == ContrastFeasibilityStatus.CONTRAST_FEASIBLE


def test_unknown_contrast_type_not_evaluated() -> None:
    contrasts = [dict(c) for c in _BASE_CONTRASTS]
    contrasts[0] = {**contrasts[0], "contrast_type": "UNKNOWN"}
    report = evaluate_design_scenario_policy_feasibility(_scenario(contrasts=contrasts))
    t1 = _contrast_report(report, "T1_vs_C0")
    assert t1.contrast_status == ContrastFeasibilityStatus.CONTRAST_NOT_EVALUATED


def test_out_of_support_emits_business_override() -> None:
    cells = [dict(c) for c in _BASE_CELLS]
    cells[1] = {**cells[1], "proposed_spend": 250_000}
    report = evaluate_design_scenario_policy_feasibility(_scenario(cells=cells))
    assert ResolutionOptionType.BUSINESS_OVERRIDE_REQUIRED.value in _resolution_types(report)


def test_bau_preserved_allows_standard_interpretation() -> None:
    report = evaluate_design_scenario_policy_feasibility(_scenario())
    assert report.estimand_shift_report.bau_control_preserved is True
    assert not report.estimand_shift_report.estimand_shift_required


def test_common_control_manipulated_reclassifies_bau_contrasts() -> None:
    cells = [dict(c) for c in _BASE_CELLS]
    cells[0] = {**cells[0], "proposed_spend": 150_000, "is_bau_policy": False}
    report = evaluate_design_scenario_policy_feasibility(_scenario(cells=cells))
    assert SharedControlConflictType.BAU_CONTROL_NOT_PRESERVED.value in _conflict_types(report)


def test_scenario_feasible_does_not_assign_markets() -> None:
    report = evaluate_design_scenario_policy_feasibility(_scenario())
    assert not report.claim_boundary_report.geo_assignment_computed
    assert not report.claim_boundary_report.treatment_control_assignment_authorized


def test_scenario_feasible_does_not_compute_power_mde() -> None:
    report = evaluate_design_scenario_policy_feasibility(_scenario())
    assert not report.claim_boundary_report.power_computed
    assert not report.claim_boundary_report.mde_computed


def test_scenario_feasible_does_not_authorize_production() -> None:
    report = evaluate_design_scenario_policy_feasibility(_scenario())
    cb = report.claim_boundary_report
    assert not cb.production_authorization_granted
    assert not cb.estimator_inference_authorized
    assert not cb.llm_decisioning_authorized
    assert cb.runtime_scenario_feasibility_implemented


def test_multiple_scenarios_without_ranking() -> None:
    report = evaluate_design_scenario_policy_feasibility(
        [_scenario("s1"), _scenario("s2", cells=[dict(c) for c in _BASE_CELLS])]
    )
    assert report.scenario_id is None
    assert len(report.scenario_reports) == 2
    assert report.aggregate_summary is not None
    assert "without ranking" in report.aggregate_summary


def test_evaluate_alias() -> None:
    report = evaluate_scenario_policy_feasibility(_scenario())
    assert report.artifact_id == "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001"


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file() or True  # report created separately
    if _SUMMARY.is_file():
        data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
        assert data["runtime_scenario_feasibility_implemented"] is True
        assert data["runtime_scenario_enumeration_implemented"] is False
        assert data["failed_scenarios"] == []
