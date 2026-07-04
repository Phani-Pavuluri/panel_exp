"""Tests for GOVERNED_RANDOMIZATION_RUNTIME_001."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from panel_exp.validation.assignment_panel_integrity_runtime_001 import (
    ASSIGNMENT_PANEL_INTEGRITY_FAILED,
    ASSIGNMENT_PANEL_INTEGRITY_PASSED,
    evaluate_assignment_panel_integrity,
)
from panel_exp.validation.design_assignment_runtime_001 import (
    AssignmentCandidateStatus,
    DesignAssignmentRuntimeConfig,
    generate_design_assignment,
)
from panel_exp.validation.governed_randomization_runtime_001 import (
    GOVERNED_RANDOMIZATION_BLOCKED,
    GOVERNED_RANDOMIZATION_COMPLETED,
    GOVERNED_RANDOMIZATION_FAILED,
    GovernedRandomizationReport,
    generate_governed_randomization,
    generate_randomized_assignment,
    run_governed_randomization,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/GOVERNED_RANDOMIZATION_RUNTIME_001_summary.json"

_AUTH_FALSE_KEYS = (
    "rerandomization_optimization_implemented",
    "balance_optimization_implemented",
    "matched_market_optimization_implemented",
    "power_mde_computed",
    "estimator_implemented",
    "inference_implemented",
    "bootstrap_inference_implemented",
    "claim_authorization_runtime_implemented",
    "claim_authorized",
    "claim_authorized_with_restrictions",
    "authorized_claim_text_generated",
    "trusted_readout_handoff_generated",
    "production_readout_authorized",
    "causal_claim_authorized",
    "incremental_lift_claim_authorized",
    "roi_claim_authorized",
    "production_authorization_granted",
    "p_value_computed",
    "confidence_interval_computed",
    "uncertainty_computed",
    "mmm_runtime_calls_implemented",
    "mmm_calibration_authorized",
    "llm_decisioning_authorized",
)


def _two_cell_request(**extra: object) -> dict:
    base = {
        "request_id": "rand_test_001",
        "design_id": "design_two_cell",
        "randomization_type": "TWO_CELL_COMPLETE_RANDOMIZATION",
        "seed": 42,
        "seed_policy": "EXPLICIT_SEED",
        "eligible_units": ["u1", "u2", "u3", "u4", "u5", "u6"],
        "cells": [
            {"cell_id": "C0", "role": "CONTROL", "target_size": 3},
            {"cell_id": "T1", "role": "TREATMENT", "target_size": 3},
        ],
    }
    base.update(extra)
    return base


def test_public_api_exists() -> None:
    assert callable(generate_governed_randomization)
    assert callable(run_governed_randomization)
    assert callable(generate_randomized_assignment)
    report = generate_governed_randomization(_two_cell_request())
    assert isinstance(report, GovernedRandomizationReport)


def test_two_cell_randomization_produces_deterministic_assignments() -> None:
    report = generate_governed_randomization(_two_cell_request())
    assert report.status == GOVERNED_RANDOMIZATION_COMPLETED
    assert report.assignment_artifact_generated is True
    assert report.assigned_unit_count == 6
    assert report.cell_counts == {"C0": 3, "T1": 3}


def test_same_seed_and_input_produce_identical_assignment_hash() -> None:
    a = generate_governed_randomization(_two_cell_request())
    b = generate_governed_randomization(_two_cell_request())
    assert isinstance(a, GovernedRandomizationReport)
    assert isinstance(b, GovernedRandomizationReport)
    assert a.assignment_hash == b.assignment_hash
    assert a.unit_allocations == b.unit_allocations


def test_different_seed_changes_assignment_hash() -> None:
    a = generate_governed_randomization(_two_cell_request(seed=1))
    b = generate_governed_randomization(_two_cell_request(seed=2))
    assert isinstance(a, GovernedRandomizationReport)
    assert isinstance(b, GovernedRandomizationReport)
    assert a.assignment_hash != b.assignment_hash


def test_derived_deterministic_seed_when_config_allows() -> None:
    report = generate_governed_randomization(
        {
            "design_id": "derived_seed_design",
            "randomization_type": "TWO_CELL_COMPLETE_RANDOMIZATION",
            "eligible_units": ["a", "b", "c", "d"],
            "cells": [
                {"cell_id": "C0", "role": "CONTROL", "target_size": 2},
                {"cell_id": "T1", "role": "TREATMENT", "target_size": 2},
            ],
        },
        config={"allow_derived_seed": True},
    )
    assert isinstance(report, GovernedRandomizationReport)
    assert report.seed is not None
    assert report.seed_policy == "REQUEST_PAYLOAD_HASH"


def test_production_context_blocks_when_seed_policy_missing() -> None:
    report = generate_governed_randomization(
        {
            "design_id": "prod_no_seed",
            "randomization_type": "TWO_CELL_COMPLETE_RANDOMIZATION",
            "production_context": "production",
            "eligible_units": ["u1", "u2", "u3", "u4"],
            "cells": [
                {"cell_id": "C0", "role": "CONTROL", "target_size": 2},
                {"cell_id": "T1", "role": "TREATMENT", "target_size": 2},
            ],
        },
        config={"allow_derived_seed": False, "require_explicit_seed_in_production": True},
    )
    assert report.status == GOVERNED_RANDOMIZATION_BLOCKED
    assert report.assignment_artifact_generated is False


def test_duplicate_eligible_unit_ids_block() -> None:
    report = generate_governed_randomization(
        _two_cell_request(eligible_units=["u1", "u1", "u2", "u3"])
    )
    assert report.status == GOVERNED_RANDOMIZATION_BLOCKED


def test_insufficient_eligible_units_block() -> None:
    report = generate_governed_randomization(_two_cell_request(eligible_units=["u1", "u2"]))
    assert report.status == GOVERNED_RANDOMIZATION_FAILED


def test_invalid_target_cell_sizes_block() -> None:
    report = generate_governed_randomization(
        _two_cell_request(cells=[
            {"cell_id": "C0", "role": "CONTROL", "target_size": -1},
            {"cell_id": "T1", "role": "TREATMENT", "target_size": 2},
        ])
    )
    assert report.status in {GOVERNED_RANDOMIZATION_BLOCKED, GOVERNED_RANDOMIZATION_FAILED}


def test_invalid_allocation_ratio_blocks() -> None:
    report = generate_governed_randomization(
        _two_cell_request(
            allocation_ratio=1.5,
            cells=[
                {"cell_id": "C0", "role": "CONTROL"},
                {"cell_id": "T1", "role": "TREATMENT"},
            ],
        )
    )
    assert report.status in {GOVERNED_RANDOMIZATION_BLOCKED, GOVERNED_RANDOMIZATION_FAILED}


def test_unsupported_randomization_type_blocks() -> None:
    report = generate_governed_randomization(
        _two_cell_request(randomization_type="THINNING_OPTIMIZATION")
    )
    assert report.status == GOVERNED_RANDOMIZATION_BLOCKED


def test_stratified_randomization_requires_strata_field() -> None:
    report = generate_governed_randomization(
        _two_cell_request(
            randomization_type="STRATIFIED_RANDOMIZATION",
            eligible_units=[
                {"unit_id": "u1", "region": "north"},
                {"unit_id": "u2", "region": "south"},
                {"unit_id": "u3", "region": "north"},
                {"unit_id": "u4", "region": "south"},
            ],
        )
    )
    assert report.status == GOVERNED_RANDOMIZATION_BLOCKED


def test_stratified_randomization_assigns_within_each_stratum() -> None:
    report = generate_governed_randomization(
        _two_cell_request(
            randomization_type="STRATIFIED_RANDOMIZATION",
            strata_field="region",
            eligible_units=[
                {"unit_id": "u1", "region": "north"},
                {"unit_id": "u2", "region": "north"},
                {"unit_id": "u3", "region": "south"},
                {"unit_id": "u4", "region": "south"},
            ],
            cells=[
                {"cell_id": "C0", "role": "CONTROL", "target_size": 1},
                {"cell_id": "T1", "role": "TREATMENT", "target_size": 1},
            ],
        )
    )
    assert report.status == GOVERNED_RANDOMIZATION_COMPLETED
    assert report.strata_counts == {"north": 2, "south": 2}


def test_block_randomization_requires_block_field() -> None:
    report = generate_governed_randomization(
        _two_cell_request(
            randomization_type="BLOCK_RANDOMIZATION",
            eligible_units=["u1", "u2", "u3", "u4"],
        )
    )
    assert report.status == GOVERNED_RANDOMIZATION_BLOCKED


def test_block_randomization_assigns_within_blocks() -> None:
    report = generate_governed_randomization(
        _two_cell_request(
            randomization_type="BLOCK_RANDOMIZATION",
            block_field="block_id",
            eligible_units=[
                {"unit_id": "u1", "block_id": "b1"},
                {"unit_id": "u2", "block_id": "b1"},
                {"unit_id": "u3", "block_id": "b2"},
                {"unit_id": "u4", "block_id": "b2"},
            ],
            cells=[
                {"cell_id": "C0", "role": "CONTROL", "target_size": 1},
                {"cell_id": "T1", "role": "TREATMENT", "target_size": 1},
            ],
        )
    )
    assert report.status == GOVERNED_RANDOMIZATION_COMPLETED
    assert report.block_counts == {"b1": 2, "b2": 2}


def test_common_control_randomization_produces_shared_control() -> None:
    report = generate_governed_randomization({
        "design_id": "common_control",
        "randomization_type": "COMMON_CONTROL_RANDOMIZATION",
        "seed": 7,
        "common_control_cell_id": "C0",
        "eligible_units": ["u1", "u2", "u3", "u4", "u5", "u6"],
        "cells": [
            {"cell_id": "C0", "role": "CONTROL", "target_size": 2},
            {"cell_id": "T1", "role": "TREATMENT", "target_size": 2},
            {"cell_id": "T2", "role": "TREATMENT", "target_size": 2},
        ],
    })
    assert report.status == GOVERNED_RANDOMIZATION_COMPLETED
    assert report.cell_counts["C0"] == 2


def test_split_control_request_blocks_without_full_support() -> None:
    report = generate_governed_randomization(
        _two_cell_request(split_control_cells=["C0A", "C0B"])
    )
    assert report.status == GOVERNED_RANDOMIZATION_BLOCKED


def test_excluded_units_are_not_assigned() -> None:
    report = generate_governed_randomization(
        _two_cell_request(excluded_units=["u1"], cells=[
            {"cell_id": "C0", "role": "CONTROL", "target_size": 2},
            {"cell_id": "T1", "role": "TREATMENT", "target_size": 2},
        ])
    )
    assigned_ids = {row["unit_id"] for row in report.unit_allocations}
    assert "u1" not in assigned_ids
    assert report.excluded_unit_count == 1


def test_generated_artifact_passes_assignment_panel_integrity() -> None:
    report = generate_governed_randomization(_two_cell_request())
    assert isinstance(report, GovernedRandomizationReport)
    artifact = report.assignment_artifact
    assert artifact is not None
    panel = []
    for row in report.unit_allocations:
        panel.append({
            "unit_id": row["unit_id"],
            "cell_id": row["assigned_cell_id"],
            "treated": row["treated"],
        })
    integrity = evaluate_assignment_panel_integrity({
        "assignment_artifact": artifact,
        "assignment_artifact_id": report.assignment_artifact_id,
        "unit_allocations": list(report.unit_allocations),
        "panel_records": panel,
    })
    assert integrity.status == ASSIGNMENT_PANEL_INTEGRITY_PASSED


def test_mismatched_panel_fails_assignment_panel_integrity() -> None:
    report = generate_governed_randomization(_two_cell_request())
    assert isinstance(report, GovernedRandomizationReport)
    panel = []
    for row in report.unit_allocations:
        panel.append({
            "unit_id": row["unit_id"],
            "cell_id": row["assigned_cell_id"],
            "treated": 0 if row["treated"] == 1 else 1,
        })
    integrity = evaluate_assignment_panel_integrity({
        "assignment_artifact": report.assignment_artifact,
        "unit_allocations": list(report.unit_allocations),
        "panel_records": panel,
    })
    assert integrity.status == ASSIGNMENT_PANEL_INTEGRITY_FAILED


def test_design_assignment_runtime_integration_preserves_explicit_pool() -> None:
    explicit = {
        "design_id": "explicit_pool",
        "upstream_statuses": {
            "profiler_status": "PASS",
            "geo_feasibility_status": "PASS",
            "spend_feasibility_status": "PASS",
            "power_mde_status": "PASS",
            "design_cell_structure_status": "PASS",
            "scenario_policy_feasibility_status": "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE",
            "assignment_feasibility_status": "ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME",
            "method_suitability_status": "PASS",
        },
        "method_instrument_suitability_matrix": [{
            "instrument_id": "TBR_RIDGE_BRB",
            "suitability_status": "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW",
        }],
        "assignment_unit_universe": [
            {"unit_id": "DMA_001", "eligible": True},
            {"unit_id": "DMA_002", "eligible": True},
            {"unit_id": "DMA_003", "eligible": True},
            {"unit_id": "DMA_004", "eligible": True},
        ],
        "eligible_unit_pools": {"C0": ["DMA_001", "DMA_002"], "T1": ["DMA_003", "DMA_004"]},
        "cell_requirements": [
            {"cell_id": "C0", "cell_role": "CONTROL", "required_unit_count": 2},
            {"cell_id": "T1", "cell_role": "TREATMENT", "required_unit_count": 2},
        ],
        "assignment_constraints": {"unique_unit_assignment_required": True},
        "assignment_algorithm_spec": {"algorithm_category": "DETERMINISTIC_RULE_ASSIGNMENT"},
        "reproducibility_config": {
            "algorithm_version": "1.0.0",
            "constraint_version": "1.0.0",
            "seed_policy": "NOT_APPLICABLE_DETERMINISTIC",
            "config_hash": "test",
        },
    }
    explicit_report = generate_design_assignment(explicit, DesignAssignmentRuntimeConfig())
    assert explicit_report.assignment_candidates
    assert explicit_report.assignment_candidates[0].candidate_status == AssignmentCandidateStatus.ASSIGNMENT_CANDIDATE_GENERATED


def test_design_assignment_runtime_randomized_path() -> None:
    randomized = {
        "design_id": "randomized_path",
        "upstream_statuses": {
            "profiler_status": "PASS",
            "geo_feasibility_status": "PASS",
            "spend_feasibility_status": "PASS",
            "power_mde_status": "PASS",
            "design_cell_structure_status": "PASS",
            "scenario_policy_feasibility_status": "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE",
            "assignment_feasibility_status": "ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME",
            "method_suitability_status": "PASS",
        },
        "method_instrument_suitability_matrix": [{
            "instrument_id": "MATCHED_PAIR_RANDOMIZATION",
            "suitability_status": "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW",
        }],
        "assignment_unit_universe": [
            {"unit_id": "u1", "eligible": True},
            {"unit_id": "u2", "eligible": True},
            {"unit_id": "u3", "eligible": True},
            {"unit_id": "u4", "eligible": True},
        ],
        "cell_requirements": [
            {"cell_id": "C0", "cell_role": "CONTROL", "required_unit_count": 2},
            {"cell_id": "T1", "cell_role": "TREATMENT", "required_unit_count": 2},
        ],
        "assignment_constraints": {"unique_unit_assignment_required": True},
        "assignment_algorithm_spec": {
            "algorithm_category": "RANDOMIZED_ASSIGNMENT",
            "randomization_type": "TWO_CELL_COMPLETE_RANDOMIZATION",
        },
        "reproducibility_config": {
            "algorithm_version": "1.0.0",
            "constraint_version": "1.0.0",
            "seed_policy": "EXPLICIT_SEED",
            "seed": 99,
            "config_hash": "test",
        },
        "seed": 99,
    }
    report = generate_design_assignment(randomized, DesignAssignmentRuntimeConfig())
    assert report.assignment_candidates
    assert len(report.unit_allocation_report) == 4


def test_list_input_returns_multiple_reports_without_ranking() -> None:
    reports = generate_governed_randomization([
        _two_cell_request(request_id="a", design_id="a"),
        _two_cell_request(request_id="b", design_id="b", seed=99),
    ])
    assert isinstance(reports, list)
    assert len(reports) == 2


@dataclass
class _RandomizationInput:
    design_id: str
    randomization_type: str
    seed: int
    eligible_units: list[str]
    cells: list[dict]


def test_dataclass_like_input_supported() -> None:
    payload = _RandomizationInput(
        design_id="dc_input",
        randomization_type="TWO_CELL_COMPLETE_RANDOMIZATION",
        seed=5,
        eligible_units=["u1", "u2", "u3", "u4"],
        cells=[
            {"cell_id": "C0", "role": "CONTROL", "target_size": 2},
            {"cell_id": "T1", "role": "TREATMENT", "target_size": 2},
        ],
    )
    report = generate_governed_randomization(payload)
    assert isinstance(report, GovernedRandomizationReport)


def test_deterministic_trace_provenance_hash() -> None:
    report = generate_governed_randomization(_two_cell_request())
    assert isinstance(report, GovernedRandomizationReport)
    assert "integrity_hash" in report.randomization_trace
    assert report.provenance.get("integrity_hash") == report.randomization_trace["integrity_hash"]


def test_all_claim_production_authorization_flags_false() -> None:
    report = generate_governed_randomization(_two_cell_request())
    assert isinstance(report, GovernedRandomizationReport)
    boundary = report.claim_boundary_report
    for key in _AUTH_FALSE_KEYS:
        assert boundary.get(key) is False, key


def test_summary_json_and_run_validation() -> None:
    summary = run_validation(write_summary=True)
    assert summary["final_verdict"] == (
        "governed_randomization_runtime_implemented_no_inference_or_claim_authorization"
    )
    assert _SUMMARY.exists()
    loaded = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in _AUTH_FALSE_KEYS:
        assert loaded.get(key) is False, key
