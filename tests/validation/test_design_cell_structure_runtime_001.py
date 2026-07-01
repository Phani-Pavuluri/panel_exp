"""Tests for DESIGN_CELL_STRUCTURE_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.design_cell_structure_runtime_001 import (
    AssignmentReadinessStatus,
    DesignCellStructureConfig,
    DesignStructureStatus,
    evaluate_design_cell_structure,
    run_validation,
    validate_design_cell_structure,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/DESIGN_CELL_STRUCTURE_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/DESIGN_CELL_STRUCTURE_RUNTIME_001_REPORT.md"

_UPSTREAM = {
    "profiler_status": "PASS",
    "geo_feasibility_status": "PASS",
    "spend_feasibility_status": "PASS",
    "power_mde_status": "PASS",
}


def _single_treatment_control(**extra: object) -> dict:
    base = {
        "design_id": "single_tc",
        "design_structure_type": "SINGLE_TREATMENT_CONTROL",
        "upstream_statuses": dict(_UPSTREAM),
        "cells": [
            {
                "cell_id": "C0",
                "cell_role": "BUSINESS_AS_USUAL_CONTROL",
                "manipulation_policy": "BUSINESS_AS_USUAL",
                "is_bau_policy": True,
                "eligible_for_assignment": True,
            },
            {
                "cell_id": "T1",
                "cell_role": "TEST_CELL",
                "manipulation_policy": "GO_DARK",
                "eligible_for_assignment": True,
            },
        ],
        "contrasts": [
            {
                "contrast_id": "T1_vs_C0",
                "contrast_type": "GO_DARK_VS_BAU",
                "treatment_cell_id": "T1",
                "comparison_cell_id": "C0",
                "bau_control_required": True,
                "contrast_specific_roles": {
                    "T1": "TREATMENT_FOR_CONTRAST",
                    "C0": "BAU_CONTROL_FOR_CONTRAST",
                },
            },
        ],
        "shared_control_dependencies": [],
    }
    base.update(extra)
    return base


def _multi_cell_common(**extra: object) -> dict:
    base = {
        "design_id": "multi_common",
        "design_structure_type": "MULTI_CELL_COMMON_CONTROL",
        "upstream_statuses": dict(_UPSTREAM),
        "cells": [
            {
                "cell_id": "C0",
                "cell_role": "COMMON_CONTROL",
                "manipulation_policy": "BUSINESS_AS_USUAL",
                "is_common_control": True,
                "is_bau_policy": True,
                "eligible_for_assignment": True,
            },
            {"cell_id": "T1", "cell_role": "TEST_CELL", "manipulation_policy": "GO_DARK", "eligible_for_assignment": True},
            {"cell_id": "T2", "cell_role": "TEST_CELL", "manipulation_policy": "HEAVY_UP", "eligible_for_assignment": True},
        ],
        "contrasts": [
            {
                "contrast_id": "T1_vs_C0",
                "contrast_type": "GO_DARK_VS_BAU",
                "treatment_cell_id": "T1",
                "comparison_cell_id": "C0",
                "bau_control_required": True,
                "contrast_specific_roles": {"T1": "TREATMENT_FOR_CONTRAST", "C0": "BAU_CONTROL_FOR_CONTRAST"},
            },
            {
                "contrast_id": "T2_vs_C0",
                "contrast_type": "HEAVY_UP_VS_BAU",
                "treatment_cell_id": "T2",
                "comparison_cell_id": "C0",
                "bau_control_required": True,
                "contrast_specific_roles": {"T2": "TREATMENT_FOR_CONTRAST", "C0": "BAU_CONTROL_FOR_CONTRAST"},
            },
        ],
        "shared_control_dependencies": [
            {
                "shared_cell_id": "C0",
                "dependent_contrast_ids": ["T1_vs_C0", "T2_vs_C0"],
                "required_policy": "BUSINESS_AS_USUAL",
                "role_by_contrast": {"T1_vs_C0": "BAU_CONTROL_FOR_CONTRAST", "T2_vs_C0": "BAU_CONTROL_FOR_CONTRAST"},
            },
        ],
    }
    base.update(extra)
    return base


def test_valid_single_treatment_control_ready() -> None:
    report = evaluate_design_cell_structure(_single_treatment_control())
    assert report.design_structure_status == DesignStructureStatus.DESIGN_CELL_STRUCTURE_READY_FOR_SCENARIO_FEASIBILITY
    assert report.scenario_feasibility_handoff_ready
    assert report.assignment_readiness_status == AssignmentReadinessStatus.DESIGN_ASSIGNMENT_READY_FOR_RUNTIME


def test_valid_multi_cell_common_control_ready() -> None:
    report = evaluate_design_cell_structure(_multi_cell_common())
    assert report.design_structure_status == DesignStructureStatus.DESIGN_CELL_STRUCTURE_READY_FOR_SCENARIO_FEASIBILITY
    assert report.scenario_feasibility_handoff_ready
    assert len(report.shared_control_dependency_report.implied_shared_cells) >= 1


def test_duplicate_cell_ids_block() -> None:
    design = _single_treatment_control()
    design["cells"] = [
        {"cell_id": "C0", "cell_role": "CONTROL", "manipulation_policy": "BUSINESS_AS_USUAL", "is_bau_policy": True},
        {"cell_id": "C0", "cell_role": "TEST_CELL", "manipulation_policy": "GO_DARK"},
    ]
    report = evaluate_design_cell_structure(design)
    assert report.design_structure_status == DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_INVALID_CELL_ROLES
    assert report.cell_report.duplicate_cell_ids == ("C0",)


def test_missing_cells_block() -> None:
    report = evaluate_design_cell_structure(_single_treatment_control(cells=[]))
    assert report.design_structure_status == DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_MISSING_CELLS


def test_unknown_cell_role_warns_by_default() -> None:
    design = _single_treatment_control()
    design["cells"][1]["cell_role"] = "NOT_A_VALID_ROLE"
    report = evaluate_design_cell_structure(design)
    assert any(i.code == "UNKNOWN_CELL_ROLE" for i in report.issues)


def test_unknown_cell_role_blocks_when_configured() -> None:
    design = _single_treatment_control()
    design["cells"][1]["cell_role"] = "UNKNOWN"
    report = evaluate_design_cell_structure(design, DesignCellStructureConfig(unknown_cell_role_is_blocking=True))
    assert "UNKNOWN_CELL_ROLE" in {i.code for i in report.issues}


def test_common_control_design_without_common_control_warns() -> None:
    design = _multi_cell_common()
    design["cells"][0]["cell_role"] = "CONTROL"
    design["cells"][0].pop("is_common_control", None)
    report = evaluate_design_cell_structure(design)
    assert any(i.code == "MISSING_COMMON_CONTROL" for i in report.issues)


def test_split_control_requires_separate_controls_or_marker() -> None:
    design = _multi_cell_common(design_structure_type="MULTI_CELL_SPLIT_CONTROL")
    report = evaluate_design_cell_structure(design)
    assert report.design_structure_status != DesignStructureStatus.DESIGN_CELL_STRUCTURE_READY_FOR_SCENARIO_FEASIBILITY

    design2 = _multi_cell_common(
        design_structure_type="MULTI_CELL_SPLIT_CONTROL",
        split_control_redesign_marker=True,
    )
    report2 = evaluate_design_cell_structure(design2)
    assert report2.assignment_readiness_status == AssignmentReadinessStatus.DESIGN_ASSIGNMENT_REQUIRES_REDESIGN_RECHECK


def test_missing_contrasts_block() -> None:
    report = evaluate_design_cell_structure(_single_treatment_control(contrasts=[]))
    assert report.design_structure_status == DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_MISSING_CONTRASTS


def test_contrast_references_undeclared_cell_blocks() -> None:
    design = _single_treatment_control()
    design["contrasts"][0]["comparison_cell_id"] = "MISSING"
    report = evaluate_design_cell_structure(design)
    assert report.design_structure_status == DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_INVALID_CONTRASTS


def test_unknown_contrast_type_blocks_by_default() -> None:
    design = _single_treatment_control()
    design["contrasts"][0]["contrast_type"] = "UNKNOWN"
    report = evaluate_design_cell_structure(design)
    assert report.design_structure_status == DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_INVALID_CONTRASTS


def test_go_dark_vs_bau_requires_bau_control_role() -> None:
    design = _single_treatment_control()
    design["contrasts"][0]["contrast_specific_roles"] = {"T1": "TREATMENT_FOR_CONTRAST"}
    report = evaluate_design_cell_structure(design)
    assert any(i.code == "MISSING_BAU_CONTROL_ROLE" for i in report.issues)


def test_dosage_contrast_requires_roles() -> None:
    design = _single_treatment_control()
    design["design_structure_type"] = "DOSAGE_CONTRAST"
    design["contrasts"] = [
        {
            "contrast_id": "low_vs_high",
            "contrast_type": "DOSAGE_LOW_VS_HIGH",
            "treatment_cell_id": "T1",
            "comparison_cell_id": "C0",
            "contrast_specific_roles": {"T1": "TREATMENT_FOR_CONTRAST", "C0": "COMPARISON_FOR_CONTRAST"},
        },
    ]
    report = evaluate_design_cell_structure(design)
    assert any(i.code == "MISSING_DOSAGE_ROLES" for i in report.issues)
    assert report.design_structure_status == DesignStructureStatus.DESIGN_CELL_STRUCTURE_REQUIRES_DOSAGE_ESTIMAND_REVIEW


def test_budget_reallocation_requires_source_destination_roles() -> None:
    design = _single_treatment_control()
    design["cells"] = [
        {"cell_id": "SRC", "cell_role": "SOURCE_REDUCTION", "manipulation_policy": "BUDGET_REALLOCATION_SOURCE"},
        {"cell_id": "DST", "cell_role": "DESTINATION_INCREASE", "manipulation_policy": "BUDGET_REALLOCATION_DESTINATION"},
    ]
    design["contrasts"] = [
        {
            "contrast_id": "realloc",
            "contrast_type": "BUDGET_REALLOCATION_SOURCE_VS_DESTINATION",
            "treatment_cell_id": "SRC",
            "comparison_cell_id": "DST",
            "contrast_specific_roles": {"SRC": "TREATMENT_FOR_CONTRAST", "DST": "COMPARISON_FOR_CONTRAST"},
        },
    ]
    report = evaluate_design_cell_structure(design)
    assert any(i.code == "MISSING_REALLOCATION_ROLES" for i in report.issues)


def test_method_suitability_prevents_final_assignment() -> None:
    design = _single_treatment_control()
    design["contrasts"][0]["method_suitability_review_required"] = True
    report = evaluate_design_cell_structure(design)
    assert report.assignment_readiness_status == AssignmentReadinessStatus.DESIGN_ASSIGNMENT_REQUIRES_METHOD_SUITABILITY_REVIEW


def test_same_cell_different_contrast_specific_roles_across_contrasts() -> None:
    design = _multi_cell_common()
    report = evaluate_design_cell_structure(design)
    c0_roles = [e.contrast_specific_role for e in report.contrast_specific_role_report.entries if e.cell_id == "C0"]
    assert c0_roles.count("BAU_CONTROL_FOR_CONTRAST") == 2


def test_contradictory_roles_within_contrast_block() -> None:
    design = _single_treatment_control()
    design["cells"] = [
        {
            "cell_id": "X1",
            "cell_role": "TEST_CELL",
            "manipulation_policy": "GO_DARK",
            "eligible_for_assignment": True,
        },
    ]
    design["contrasts"] = [
        {
            "contrast_id": "self_contrast",
            "contrast_type": "GO_DARK_VS_BAU",
            "treatment_cell_id": "X1",
            "comparison_cell_id": "X1",
            "bau_control_required": False,
            "contrast_specific_roles": {
                "X1": "TREATMENT_FOR_CONTRAST",
            },
        },
    ]
    report = evaluate_design_cell_structure(design)
    assert (
        "CONTRADICTORY_ROLES" in {i.code for i in report.issues}
        or report.contrast_specific_role_report.contradictory_contrast_ids
    )


def test_bau_control_non_bau_policy_blocks() -> None:
    design = _single_treatment_control()
    design["cells"][0]["manipulation_policy"] = "HEAVY_UP"
    report = evaluate_design_cell_structure(design)
    assert any(i.code == "BAU_POLICY_MISMATCH" for i in report.issues)


def test_go_dark_on_treatment_valid() -> None:
    report = evaluate_design_cell_structure(_single_treatment_control())
    t1 = next(e for e in report.manipulation_policy_report.entries if e.cell_id == "T1")
    assert t1.policy_compatible_with_role


def test_go_dark_on_bau_control_invalid() -> None:
    design = _single_treatment_control()
    design["cells"][0]["manipulation_policy"] = "GO_DARK"
    report = evaluate_design_cell_structure(design)
    assert any(i.code == "GO_DARK_ON_CONTROL" for i in report.issues)


def test_heavy_up_on_treatment_valid() -> None:
    design = _multi_cell_common()
    report = evaluate_design_cell_structure(design)
    t2 = next(e for e in report.manipulation_policy_report.entries if e.cell_id == "T2")
    assert t2.policy_compatible_with_role


def test_heavy_up_on_bau_control_requires_reframe() -> None:
    design = _single_treatment_control()
    design["cells"][0]["manipulation_policy"] = "HEAVY_UP"
    report = evaluate_design_cell_structure(design)
    assert any(i.code == "HEAVY_UP_ON_BAU" for i in report.issues)


def test_common_control_across_contrasts_detected() -> None:
    report = evaluate_design_cell_structure(_multi_cell_common())
    assert "C0" in report.shared_control_dependency_report.implied_shared_cells


def test_missing_shared_control_dependency_warns_by_default() -> None:
    design = _multi_cell_common(shared_control_dependencies=[])
    report = evaluate_design_cell_structure(design)
    assert any(i.code == "MISSING_SHARED_CONTROL_DEP" for i in report.issues)


def test_shared_bau_required_but_not_bau_blocks() -> None:
    design = _multi_cell_common()
    design["cells"][0]["manipulation_policy"] = "HEAVY_UP"
    design["cells"][0]["is_bau_policy"] = False
    report = evaluate_design_cell_structure(design)
    assert any(i.code == "SHARED_BAU_NOT_PRESERVED" for i in report.issues)


def test_handoff_ready_does_not_mean_scenario_feasible() -> None:
    report = evaluate_design_cell_structure(_multi_cell_common())
    assert report.scenario_feasibility_handoff_ready
    assert not report.claim_boundary_report.scenario_policy_feasibility_computed


def test_scenario_conflict_blocks_assignment() -> None:
    design = _multi_cell_common()
    design["upstream_statuses"] = {**_UPSTREAM, "scenario_policy_feasibility_status": "SCENARIO_BLOCKED"}
    report = evaluate_design_cell_structure(design)
    assert report.assignment_readiness_status == AssignmentReadinessStatus.DESIGN_ASSIGNMENT_BLOCKED_BY_SCENARIO_CONFLICT


def test_blocked_profiler_blocks_structure() -> None:
    design = _single_treatment_control()
    design["upstream_statuses"] = {**_UPSTREAM, "profiler_status": "BLOCKED"}
    report = evaluate_design_cell_structure(design)
    assert report.design_structure_status == DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_DATA_READINESS


def test_blocked_geo_blocks_structure() -> None:
    design = _single_treatment_control()
    design["upstream_statuses"] = {**_UPSTREAM, "geo_feasibility_status": "BLOCKED"}
    report = evaluate_design_cell_structure(design)
    assert report.design_structure_status == DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_GEO_FEASIBILITY


def test_multiple_structures_without_ranking() -> None:
    report = evaluate_design_cell_structure([_single_treatment_control(), _multi_cell_common()])
    assert report.design_id is None
    assert len(report.design_reports) == 2
    assert "without ranking" in (report.aggregate_summary or "")


def test_validate_alias() -> None:
    report = validate_design_cell_structure(_single_treatment_control())
    assert report.artifact_id == "DESIGN_CELL_STRUCTURE_RUNTIME_001"


def test_claim_boundaries() -> None:
    report = evaluate_design_cell_structure(_multi_cell_common())
    cb = report.claim_boundary_report
    assert cb.runtime_design_cell_structure_validation_implemented
    assert cb.scenario_policy_feasibility_computed is False
    assert cb.geo_assignment_computed is False
    assert cb.power_computed is False
    assert cb.production_authorization_granted is False
    assert cb.estimator_inference_authorized is False


def test_no_geo_assignment_produced() -> None:
    report = evaluate_design_cell_structure(_multi_cell_common())
    assert not report.claim_boundary_report.geo_assignment_computed
    assert not report.claim_boundary_report.randomization_computed


def test_summary_json() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["runtime_design_cell_structure_validation_implemented"] is True
    assert data["scenario_policy_feasibility_computed"] is False
    assert data["failed_scenarios"] == []
