"""Tests for DESIGN_ASSIGNMENT_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.design_assignment_runtime_001 import (
    AssignmentCandidateStatus,
    AssignmentRuntimeStatus,
    DesignAssignmentRuntimeConfig,
    generate_assignment_candidate,
    generate_design_assignment,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/DESIGN_ASSIGNMENT_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/DESIGN_ASSIGNMENT_RUNTIME_001_REPORT.md"

_UPSTREAM_READY = {
    "profiler_status": "PASS",
    "geo_feasibility_status": "PASS",
    "spend_feasibility_status": "PASS",
    "power_mde_status": "PASS",
    "design_cell_structure_status": "PASS",
    "scenario_policy_feasibility_status": "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE",
    "assignment_feasibility_status": "ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME",
    "method_suitability_status": "PASS",
}

_REPRO = {
    "algorithm_version": "1.0.0",
    "constraint_version": "1.0.0",
    "seed_policy": "NOT_APPLICABLE_DETERMINISTIC",
    "config_hash": "test_config",
    "input_artifact_ids": ["TEST_INPUT"],
}

_INSTRUMENT_ELIGIBLE = [{
    "instrument_id": "TBR_RIDGE_BRB",
    "suitability_status": "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW",
}]


def _universe(*unit_ids: str) -> list[dict]:
    return [{"unit_id": uid, "geo_id": f"G_{uid}", "eligible": True} for uid in unit_ids]


def _request(**extra: object) -> dict:
    base = {
        "design_id": "test_design",
        "upstream_statuses": dict(_UPSTREAM_READY),
        "method_instrument_suitability_matrix": list(_INSTRUMENT_ELIGIBLE),
        "assignment_unit_universe": _universe("DMA_001", "DMA_002", "DMA_003", "DMA_004"),
        "eligible_unit_pools": {
            "C0": ["DMA_001", "DMA_002"],
            "T1": ["DMA_003", "DMA_004"],
        },
        "cell_requirements": [
            {"cell_id": "C0", "cell_role": "CONTROL", "required_unit_count": 2},
            {"cell_id": "T1", "cell_role": "TREATMENT", "required_unit_count": 2},
        ],
        "assignment_constraints": {
            "unique_unit_assignment_required": True,
            "respect_allowed_unit_ids": True,
            "respect_blocked_unit_ids": True,
            "respect_eligible_cell_ids": True,
            "respect_exclusion_flags": True,
            "preserve_declared_cell_roles": True,
        },
        "assignment_algorithm_spec": {"algorithm_category": "DETERMINISTIC_RULE_ASSIGNMENT"},
        "reproducibility_config": dict(_REPRO),
    }
    base.update(extra)
    return base


# --- Success path ---


def test_two_cell_explicit_pool_succeeds() -> None:
    report = generate_design_assignment(_request())
    assert report.assignment_runtime_status in (
        AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_READY_TO_GENERATE,
        AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_READY_WITH_WARNINGS,
    )
    assert len(report.assignment_candidates) == 1
    assert report.assignment_candidates[0].candidate_status == AssignmentCandidateStatus.ASSIGNMENT_CANDIDATE_GENERATED
    assert len(report.unit_allocation_report) == 4
    assert report.claim_boundary_report.geo_assignment_computed


def test_multi_cell_explicit_pool_succeeds() -> None:
    p = _request(
        assignment_unit_universe=_universe("DMA_001", "DMA_002", "DMA_003", "DMA_004", "DMA_005", "DMA_006"),
        eligible_unit_pools={
            "C0": ["DMA_001", "DMA_002"],
            "T1": ["DMA_003", "DMA_004"],
            "T2": ["DMA_005", "DMA_006"],
        },
        cell_requirements=[
            {"cell_id": "C0", "cell_role": "CONTROL", "required_unit_count": 2},
            {"cell_id": "T1", "cell_role": "TREATMENT", "required_unit_count": 1},
            {"cell_id": "T2", "cell_role": "TREATMENT", "required_unit_count": 1},
        ],
    )
    report = generate_design_assignment(p)
    assert len(report.unit_allocation_report) == 4


def test_common_control_explicit_pool_succeeds() -> None:
    p = _request(
        assignment_unit_universe=_universe("DMA_001", "DMA_002", "DMA_003", "DMA_004", "DMA_005"),
        eligible_unit_pools={
            "C0": ["DMA_001", "DMA_002", "DMA_003"],
            "T1": ["DMA_004"],
            "T2": ["DMA_005"],
        },
        cell_requirements=[
            {"cell_id": "C0", "cell_role": "CONTROL", "required_unit_count": 3},
            {"cell_id": "T1", "cell_role": "TREATMENT", "required_unit_count": 1},
            {"cell_id": "T2", "cell_role": "TREATMENT", "required_unit_count": 1},
        ],
        assignment_algorithm_spec={"algorithm_category": "COMMON_CONTROL_ASSIGNMENT"},
    )
    report = generate_design_assignment(p)
    assert report.assignment_candidates
    c0 = next(c for c in report.cell_allocation_report if c.cell_id == "C0")
    assert c0.allocated_unit_count == 3


def test_split_control_when_declared_and_recheck_ok() -> None:
    p = _request(
        assignment_unit_universe=_universe("DMA_001", "DMA_002", "DMA_003", "DMA_004"),
        eligible_unit_pools={
            "C1": ["DMA_001"],
            "C2": ["DMA_002"],
            "T1": ["DMA_003"],
            "T2": ["DMA_004"],
        },
        cell_requirements=[
            {"cell_id": "C1", "cell_role": "CONTROL", "required_unit_count": 1},
            {"cell_id": "C2", "cell_role": "CONTROL", "required_unit_count": 1},
            {"cell_id": "T1", "cell_role": "TREATMENT", "required_unit_count": 1},
            {"cell_id": "T2", "cell_role": "TREATMENT", "required_unit_count": 1},
        ],
        assignment_algorithm_spec={"algorithm_category": "SPLIT_CONTROL_ASSIGNMENT"},
    )
    report = generate_design_assignment(p)
    assert len(report.unit_allocation_report) == 4


def test_stable_sorting_by_unit_id() -> None:
    p = _request(
        assignment_unit_universe=[
            {"unit_id": "DMA_003", "eligible": True},
            {"unit_id": "DMA_001", "eligible": True},
            {"unit_id": "DMA_002", "eligible": True},
            {"unit_id": "DMA_004", "eligible": True},
        ],
    )
    report = generate_design_assignment(p)
    c0_units = [a.unit_id for a in report.unit_allocation_report if a.assigned_cell_id == "C0"]
    assert c0_units == ["DMA_001", "DMA_002"]


def test_custom_deterministic_sort_key() -> None:
    p = _request(
        assignment_unit_universe=[
            {"unit_id": "DMA_001", "geo_id": "Z", "eligible": True},
            {"unit_id": "DMA_002", "geo_id": "A", "eligible": True},
            {"unit_id": "DMA_003", "geo_id": "B", "eligible": True},
            {"unit_id": "DMA_004", "geo_id": "C", "eligible": True},
        ],
    )
    cfg = DesignAssignmentRuntimeConfig(deterministic_sort_key="geo_id")
    report = generate_design_assignment(p, cfg)
    c0_units = [a.unit_id for a in report.unit_allocation_report if a.assigned_cell_id == "C0"]
    assert c0_units == ["DMA_002", "DMA_001"]


# --- Blocking / failure packets ---


def test_missing_unit_universe_blocks() -> None:
    p = _request()
    p.pop("assignment_unit_universe")
    report = generate_design_assignment(p)
    assert report.assignment_runtime_status == AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_UNIT_UNIVERSE
    assert report.failure_packet is not None


def test_missing_cell_requirements_blocks() -> None:
    p = _request()
    p["cell_requirements"] = []
    report = generate_design_assignment(p)
    assert report.assignment_runtime_status == AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_CONSTRAINTS


def test_missing_reproducibility_config_blocks() -> None:
    p = _request()
    p.pop("reproducibility_config")
    report = generate_design_assignment(p)
    assert report.assignment_runtime_status == (
        AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_REPRODUCIBILITY_REQUIREMENTS
    )


def test_unsupported_algorithm_blocks() -> None:
    p = _request(assignment_algorithm_spec={"algorithm_category": "RERANDOMIZED_ASSIGNMENT"})
    report = generate_design_assignment(p)
    assert report.assignment_runtime_status == AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_CONSTRAINTS
    assert report.failure_packet is not None


def test_insufficient_eligible_units_blocks() -> None:
    p = _request(
        eligible_unit_pools={"C0": ["DMA_001"], "T1": ["DMA_003", "DMA_004"]},
        cell_requirements=[
            {"cell_id": "C0", "cell_role": "CONTROL", "required_unit_count": 2},
            {"cell_id": "T1", "cell_role": "TREATMENT", "required_unit_count": 2},
        ],
    )
    report = generate_design_assignment(p)
    assert report.failure_packet is not None
    assert report.assignment_candidates == () or report.assignment_candidates[0].candidate_status in (
        AssignmentCandidateStatus.ASSIGNMENT_CANDIDATE_REJECTED_BY_CONSTRAINTS,
        AssignmentCandidateStatus.ASSIGNMENT_CANDIDATE_NOT_GENERATED,
    )


def test_duplicate_unit_in_pools_blocks() -> None:
    p = _request(
        eligible_unit_pools={"C0": ["DMA_001", "DMA_002"], "T1": ["DMA_001", "DMA_003"]},
        cell_requirements=[
            {"cell_id": "C0", "cell_role": "CONTROL", "required_unit_count": 2},
            {"cell_id": "T1", "cell_role": "TREATMENT", "required_unit_count": 1},
        ],
    )
    report = generate_design_assignment(p)
    assert report.failure_packet is not None or any(
        e.reason.find("already assigned") >= 0 for e in report.exclusion_trace
    )


def test_blocked_unit_excluded_and_traced() -> None:
    p = _request(
        cell_requirements=[
            {"cell_id": "C0", "cell_role": "CONTROL", "required_unit_count": 2, "blocked_unit_ids": ["DMA_001"]},
            {"cell_id": "T1", "cell_role": "TREATMENT", "required_unit_count": 2},
        ],
    )
    report = generate_design_assignment(p)
    reasons = [e.reason for e in report.exclusion_trace]
    assert any("blocked" in r.lower() for r in reasons)


def test_unit_not_eligible_for_cell_traced() -> None:
    p = _request(
        assignment_unit_universe=[
            {"unit_id": "DMA_001", "eligible": True, "eligible_cell_ids": ["T1"]},
            {"unit_id": "DMA_002", "eligible": True},
            {"unit_id": "DMA_003", "eligible": True},
            {"unit_id": "DMA_004", "eligible": True},
        ],
    )
    report = generate_design_assignment(p)
    assert any(e.reason.find("not eligible") >= 0 for e in report.exclusion_trace)


def test_all_method_instruments_blocked() -> None:
    p = _request(method_instrument_suitability_matrix=[{
        "instrument_id": "SCM_UNIT_JACKKNIFE",
        "suitability_status": "METHOD_FAMILY_BLOCKED",
    }])
    report = generate_design_assignment(p)
    assert report.assignment_runtime_status == AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_METHOD_SUITABILITY


def test_assignment_feasibility_blocked() -> None:
    p = _request()
    p["upstream_statuses"]["assignment_feasibility_status"] = "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY"
    report = generate_design_assignment(p)
    assert report.assignment_runtime_status == AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_ASSIGNMENT_FEASIBILITY


def test_design_structure_blocked() -> None:
    p = _request()
    p["upstream_statuses"]["design_cell_structure_status"] = "BLOCKED"
    report = generate_design_assignment(p)
    assert report.assignment_runtime_status == AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_DESIGN_STRUCTURE


def test_scenario_policy_blocked_by_default() -> None:
    p = _request()
    p["upstream_statuses"]["scenario_policy_feasibility_status"] = "SCENARIO_BLOCKED"
    report = generate_design_assignment(p)
    assert report.assignment_runtime_status == AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_SCENARIO_POLICY


def test_scenario_policy_provisional_when_config_allows() -> None:
    p = _request()
    p["upstream_statuses"]["scenario_policy_feasibility_status"] = "SCENARIO_BLOCKED"
    cfg = DesignAssignmentRuntimeConfig(block_scenario_policy_blocked=False)
    report = generate_design_assignment(p, cfg)
    assert report.assignment_runtime_status in (
        AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_PROVISIONAL,
        AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_READY_WITH_WARNINGS,
        AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_READY_TO_GENERATE,
    )


# --- Constraint/exclusion/reproducibility ---


def test_constraint_trace_records_checked_constraints() -> None:
    report = generate_design_assignment(_request())
    assert report.constraint_trace is not None
    assert report.constraint_trace.constraints_checked
    assert report.constraint_trace.constraint_relaxation_used is False


def test_exclusion_trace_records_reasons() -> None:
    p = _request(excluded_units=["DMA_099"])
    report = generate_design_assignment(p)
    assert any(e.excluded_unit_id == "DMA_099" for e in report.exclusion_trace)


def test_reproducibility_manifest_includes_hashes() -> None:
    report = generate_design_assignment(_request())
    assert report.reproducibility_manifest is not None
    m = report.reproducibility_manifest
    assert m.algorithm_version
    assert m.unit_universe_hash
    assert m.eligible_pool_hash
    assert m.output_hash
    assert m.generated_at_policy == "not_recorded_runtime_is_deterministic"


def test_artifact_registry_missing_warning_provisional() -> None:
    p = _request()
    p.pop("artifact_registry_config", None)
    report = generate_design_assignment(p)
    assert report.assignment_candidates


# --- Claim boundaries ---


def test_candidate_generated_but_not_selected() -> None:
    report = generate_design_assignment(_request())
    assert report.claim_boundary_report.assignment_candidate_generated
    assert not report.claim_boundary_report.assignment_candidate_selected
    assert report.assignment_plan is not None
    assert report.assignment_plan.selected_candidate_id is None


def test_no_matched_pairs_or_randomization() -> None:
    report = generate_design_assignment(_request())
    cb = report.claim_boundary_report
    assert not cb.matched_pairs_generated
    assert not cb.blocks_generated
    assert not cb.randomization_computed
    assert not cb.rerandomization_computed
    assert not cb.thinning_design_generated
    assert not cb.matching_optimization_computed
    assert not cb.balance_optimization_computed
    assert not cb.balance_diagnostics_computed


def test_no_method_suitability_computation_or_inference() -> None:
    report = generate_design_assignment(_request())
    cb = report.claim_boundary_report
    assert not cb.method_suitability_computed
    assert not cb.estimator_selected
    assert not cb.inference_method_selected
    assert not cb.production_authorization_granted


def test_diagnostic_only_method_warning() -> None:
    p = _request(method_instrument_suitability_matrix=[{
        "instrument_id": "SCM_PLACEBO",
        "suitability_status": "METHOD_FAMILY_DIAGNOSTIC_ONLY",
    }])
    report = generate_design_assignment(p)
    assert report.assignment_runtime_status == AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_PROVISIONAL
    assert not report.claim_boundary_report.production_authorization_granted


def test_multiple_requests_no_ranking() -> None:
    report = generate_design_assignment([_request(design_id="d1"), _request(design_id="d2")])
    assert report.design_id is None
    assert len(report.design_reports) == 2
    assert report.aggregate_summary is not None


def test_generate_alias() -> None:
    report = generate_assignment_candidate(_request())
    assert report.artifact_id == "DESIGN_ASSIGNMENT_RUNTIME_001"


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["verdict"] == (
        "design_assignment_runtime_implemented_deterministic_explicit_pool_assignment_only_no_matching_or_randomization"
    )
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["runtime_assignment_generation_implemented"] is True
    assert summary["assignment_candidate_selected"] is False


def test_report_exists() -> None:
    assert _REPORT.exists()
