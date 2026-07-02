"""DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001 metadata-only validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "design_assignment_runtime_contract_defined_no_assignment_generation_or_randomization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001_summary.json"

SCOPE = "contract_only_no_assignment_generation_or_randomization"
RECOMMENDED_NEXT_ARTIFACT = "DESIGN_ASSIGNMENT_RUNTIME_001"
ALTERNATIVE_NEXT_ARTIFACT = "READOUT_METHOD_GOVERNANCE_CONTRACT_001"

DEPENDS_ON = (
    "GEO_KPI_SPEND_DATA_PROFILER_001",
    "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
    "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
    "POWER_MDE_DIAGNOSTICS_RUNTIME_001",
    "DESIGN_CELL_STRUCTURE_RUNTIME_001",
    "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001",
    "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001",
    "METHOD_SUITABILITY_RUNTIME_001",
)

FUTURE_ASSIGNMENT_RUNTIME_STATUSES = (
    "ASSIGNMENT_RUNTIME_READY_TO_GENERATE",
    "ASSIGNMENT_RUNTIME_READY_WITH_WARNINGS",
    "ASSIGNMENT_RUNTIME_PROVISIONAL",
    "ASSIGNMENT_RUNTIME_BLOCKED_BY_DATA_READINESS",
    "ASSIGNMENT_RUNTIME_BLOCKED_BY_GEO_FEASIBILITY",
    "ASSIGNMENT_RUNTIME_BLOCKED_BY_DESIGN_STRUCTURE",
    "ASSIGNMENT_RUNTIME_BLOCKED_BY_SCENARIO_POLICY",
    "ASSIGNMENT_RUNTIME_BLOCKED_BY_ASSIGNMENT_FEASIBILITY",
    "ASSIGNMENT_RUNTIME_BLOCKED_BY_METHOD_SUITABILITY",
    "ASSIGNMENT_RUNTIME_BLOCKED_BY_POWER_MDE_READINESS",
    "ASSIGNMENT_RUNTIME_BLOCKED_BY_UNIT_UNIVERSE",
    "ASSIGNMENT_RUNTIME_BLOCKED_BY_CONSTRAINTS",
    "ASSIGNMENT_RUNTIME_BLOCKED_BY_REPRODUCIBILITY_REQUIREMENTS",
    "ASSIGNMENT_RUNTIME_REQUIRES_REDESIGN_RECHECK",
    "ASSIGNMENT_RUNTIME_NOT_EVALUATED",
)

FUTURE_ASSIGNMENT_CANDIDATE_STATUSES = (
    "ASSIGNMENT_CANDIDATE_GENERATED",
    "ASSIGNMENT_CANDIDATE_GENERATED_WITH_WARNINGS",
    "ASSIGNMENT_CANDIDATE_REJECTED_BY_CONSTRAINTS",
    "ASSIGNMENT_CANDIDATE_REJECTED_BY_BALANCE",
    "ASSIGNMENT_CANDIDATE_REJECTED_BY_INTERFERENCE_RISK",
    "ASSIGNMENT_CANDIDATE_REQUIRES_REVIEW",
    "ASSIGNMENT_CANDIDATE_NOT_GENERATED",
)

ASSIGNMENT_ALGORITHM_CATEGORIES = (
    "DETERMINISTIC_RULE_ASSIGNMENT",
    "MATCHED_PAIR_ASSIGNMENT",
    "BLOCKED_ASSIGNMENT",
    "RERANDOMIZED_ASSIGNMENT",
    "THINNING_ASSIGNMENT",
    "COMMON_CONTROL_ASSIGNMENT",
    "SPLIT_CONTROL_ASSIGNMENT",
    "BUDGET_REALLOCATION_ASSIGNMENT",
    "DOSAGE_ASSIGNMENT",
    "CUSTOM_GOVERNED_ASSIGNMENT",
    "UNKNOWN_ASSIGNMENT_ALGORITHM",
)

FUTURE_CONTRACT_CONCEPTS = (
    "DesignAssignmentRuntimeInput",
    "DesignAssignmentRuntimeConfig",
    "DesignAssignmentRuntimeReport",
    "AssignmentPlan",
    "AssignmentCandidate",
    "AssignmentUnitAllocation",
    "AssignmentCellAllocation",
    "AssignmentConstraintReport",
    "AssignmentConstraintTrace",
    "AssignmentExclusionTrace",
    "AssignmentBalanceDiagnostic",
    "AssignmentBalanceRequirement",
    "AssignmentRandomizationManifest",
    "AssignmentReproducibilityManifest",
    "AssignmentSeedPolicy",
    "AssignmentAlgorithmSpec",
    "AssignmentFailurePacket",
    "AssignmentRetryPolicy",
    "AssignmentAuditTrail",
    "AssignmentArtifactRegistryEntry",
    "AssignmentRuntimeStatus",
    "AssignmentCandidateStatus",
    "AssignmentConstraintStatus",
    "AssignmentClaimBoundaryReport",
)

FUTURE_OUTPUT_CONCEPTS = (
    "DesignAssignmentRuntimeReport",
    "AssignmentPlan",
    "AssignmentCandidate",
    "AssignmentUnitAllocation",
    "AssignmentCellAllocation",
    "AssignmentConstraintReport",
    "AssignmentConstraintTrace",
    "AssignmentExclusionTrace",
    "AssignmentBalanceDiagnostic",
    "AssignmentRandomizationManifest",
    "AssignmentReproducibilityManifest",
    "AssignmentFailurePacket",
    "AssignmentAuditTrail",
    "AssignmentClaimBoundaryReport",
)

ASSIGNMENT_PLAN_FIELDS = (
    "artifact_id",
    "design_id",
    "assignment_runtime_status",
    "assignment_algorithm_category",
    "assignment_algorithm_spec",
    "assignment_seed_policy",
    "unit_universe_summary",
    "cell_requirements",
    "constraint_summary",
    "exclusion_trace",
    "method_suitability_handoff_summary",
    "balance_requirement_summary",
    "interference_risk_summary",
    "reproducibility_manifest",
    "candidate_assignment_count",
    "selected_candidate_id",
    "claim_boundary_report",
)

ASSIGNMENT_CANDIDATE_FIELDS = (
    "candidate_id",
    "design_id",
    "algorithm_category",
    "seed",
    "cell_allocations",
    "unit_allocations",
    "constraint_report",
    "balance_diagnostics",
    "interference_risk_flags",
    "exclusion_trace",
    "candidate_status",
    "rejection_reasons",
    "warnings",
    "artifact_registry_entry",
)

UNIT_ALLOCATION_FIELDS = (
    "unit_id",
    "geo_id",
    "assigned_cell_id",
    "assigned_cell_role",
    "assignment_reason",
    "assignment_algorithm",
    "eligible_at_assignment_time",
    "exclusion_flags",
    "constraint_flags",
    "prior_assignment_flags",
    "audit_trace",
)

INPUT_DEPENDENCIES = (
    "profiler_report",
    "geo_unit_market_feasibility_report",
    "spend_requirement_manipulation_feasibility_report",
    "power_mde_diagnostics_report",
    "design_cell_structure_runtime_report",
    "design_scenario_policy_feasibility_report",
    "design_assignment_feasibility_report",
    "method_suitability_report",
    "assignment_unit_universe",
    "eligible_units",
    "excluded_units",
    "cell_requirements",
    "assignment_constraints",
    "balance_requirements",
    "interference_risk_report",
    "method_instrument_suitability_matrix",
    "selected_assignment_algorithm_spec",
    "random_seed_policy",
    "reproducibility_config",
    "artifact_registry_config",
)

READINESS_GATES = (
    "profiler_data_readiness_gate",
    "geo_unit_market_feasibility_gate",
    "spend_feasibility_gate",
    "power_mde_readiness_gate",
    "design_cell_structure_gate",
    "scenario_policy_feasibility_gate",
    "assignment_feasibility_gate",
    "method_suitability_gate",
    "assignment_unit_universe_gate",
    "assignment_constraint_gate",
    "algorithm_spec_gate",
    "reproducibility_config_gate",
    "artifact_registry_gate",
    "assignment_plan_generation_gate",
)

RETRY_CATEGORIES = (
    "RELAX_CONSTRAINTS_WITH_APPROVAL",
    "REDUCE_CELL_COUNT",
    "INCREASE_ELIGIBLE_UNIT_POOL",
    "SPLIT_OR_MERGE_CELLS",
    "CHANGE_ASSIGNMENT_ALGORITHM",
    "RERUN_FEASIBILITY_DIAGNOSTICS",
    "RERUN_POWER_MDE_DIAGNOSTICS",
    "RERUN_METHOD_SUITABILITY",
    "BLOCK_DESIGN",
)

FUTURE_IMPLEMENTATION_TESTS = (
    "blocked_profiler_blocks_assignment_runtime",
    "blocked_geo_feasibility_blocks_assignment_runtime",
    "blocked_design_structure_blocks_assignment_runtime",
    "blocked_scenario_policy_blocks_or_provisional_assignment_runtime",
    "blocked_assignment_feasibility_blocks_assignment_runtime",
    "all_method_instruments_blocked_blocks_or_requires_review",
    "diagnostic_only_instruments_do_not_authorize_production_assignment",
    "missing_unit_universe_blocks",
    "missing_cell_requirements_blocks",
    "missing_assignment_constraints_blocks_or_provisional",
    "missing_algorithm_spec_blocks",
    "missing_reproducibility_config_blocks",
    "missing_artifact_registry_config_blocks_or_provisional",
    "common_control_dependency_preserved",
    "split_control_redesign_recheck_preserved",
    "randomized_assignment_requires_seed_policy",
    "rerandomization_requires_candidate_generation_policy",
    "constraint_trace_required",
    "exclusion_trace_required",
    "failure_packet_emitted_on_blocking_gates",
    "no_assignment_generated_by_contract",
    "no_lift_roi_pvalues_cis",
    "no_estimator_inference_selection",
    "no_production_authorization",
    "no_fixture_specific_branching",
)

CONTRACT_EXAMPLES = (
    "example_1_ready_to_generate_simple_two_cell",
    "example_2_blocked_by_assignment_feasibility",
    "example_3_blocked_by_method_suitability",
    "example_4_diagnostic_only_method_state",
    "example_5_missing_reproducibility_config",
    "example_6_common_control_assignment",
    "example_7_split_control_assignment",
    "example_8_rerandomized_assignment",
)

_AUTH_FLAGS = {
    "runtime_assignment_generation_implemented": False,
    "assignment_plan_generated": False,
    "assignment_candidate_generated": False,
    "assignment_candidate_selected": False,
    "unit_allocation_generated": False,
    "geo_assignment_computed": False,
    "matched_pairs_generated": False,
    "blocks_generated": False,
    "randomization_computed": False,
    "rerandomization_computed": False,
    "thinning_design_generated": False,
    "matching_optimization_computed": False,
    "balance_optimization_computed": False,
    "balance_diagnostics_computed": False,
    "interference_adjustment_computed": False,
    "scenario_policy_feasibility_computed": False,
    "assignment_feasibility_computed": False,
    "method_suitability_computed": False,
    "method_family_selected": False,
    "estimator_selected": False,
    "inference_method_selected": False,
    "method_promotion_authorized": False,
    "method_production_compatibility_authorized": False,
    "power_computed": False,
    "mde_computed": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "lift_computed": False,
    "roi_computed": False,
    "budget_optimization_authorized": False,
    "candidate_design_authorized": False,
    "treatment_control_assignment_authorized": False,
    "estimator_inference_authorized": False,
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "production_authorization_granted": False,
    "llm_decisioning_authorized": False,
}

CONTRACT_POSITIVE_FLAGS = {
    "design_assignment_runtime_contract_defined": True,
    "assignment_plan_contract_defined": True,
    "assignment_candidate_contract_defined": True,
    "unit_allocation_contract_defined": True,
    "constraint_trace_contract_defined": True,
    "exclusion_trace_contract_defined": True,
    "balance_diagnostic_contract_defined": True,
    "randomization_manifest_contract_defined": True,
    "reproducibility_manifest_contract_defined": True,
    "assignment_failure_packet_contract_defined": True,
    "artifact_registry_entry_contract_defined": True,
    "claim_boundaries_defined": True,
}

NON_GOALS = (
    "no_runtime_assignment_generation",
    "no_geo_assignment",
    "no_matched_pairs_generated",
    "no_blocks_generated",
    "no_randomization",
    "no_rerandomization",
    "no_thinning_design_generation",
    "no_matching_optimization",
    "no_balance_optimization",
    "no_balance_diagnostics_computation",
    "no_interference_adjustment",
    "no_scenario_policy_feasibility_computation",
    "no_assignment_feasibility_computation",
    "no_method_suitability_computation",
    "no_power_mde_computation",
    "no_estimator_inference_selection",
    "no_production_authorization",
)


@dataclass(frozen=True)
class DesignAssignmentRuntimeContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    design_assignment_runtime_contract_defined: bool
    assignment_plan_contract_defined: bool
    assignment_candidate_contract_defined: bool
    unit_allocation_contract_defined: bool
    constraint_trace_contract_defined: bool
    exclusion_trace_contract_defined: bool
    balance_diagnostic_contract_defined: bool
    randomization_manifest_contract_defined: bool
    reproducibility_manifest_contract_defined: bool
    assignment_failure_packet_contract_defined: bool
    artifact_registry_entry_contract_defined: bool
    future_assignment_runtime_statuses: tuple[str, ...]
    future_assignment_candidate_statuses: tuple[str, ...]
    assignment_algorithm_categories: tuple[str, ...]
    future_contract_concepts: tuple[str, ...]
    future_output_concepts: tuple[str, ...]
    assignment_plan_fields: tuple[str, ...]
    assignment_candidate_fields: tuple[str, ...]
    unit_allocation_fields: tuple[str, ...]
    input_dependencies: tuple[str, ...]
    readiness_gates: tuple[str, ...]
    retry_categories: tuple[str, ...]
    contract_examples: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


def build_design_assignment_runtime_contract() -> DesignAssignmentRuntimeContract:
    return DesignAssignmentRuntimeContract(
        artifact_id=_ARTIFACT_ID,
        scope=SCOPE,
        depends_on=DEPENDS_ON,
        design_assignment_runtime_contract_defined=True,
        assignment_plan_contract_defined=True,
        assignment_candidate_contract_defined=True,
        unit_allocation_contract_defined=True,
        constraint_trace_contract_defined=True,
        exclusion_trace_contract_defined=True,
        balance_diagnostic_contract_defined=True,
        randomization_manifest_contract_defined=True,
        reproducibility_manifest_contract_defined=True,
        assignment_failure_packet_contract_defined=True,
        artifact_registry_entry_contract_defined=True,
        future_assignment_runtime_statuses=FUTURE_ASSIGNMENT_RUNTIME_STATUSES,
        future_assignment_candidate_statuses=FUTURE_ASSIGNMENT_CANDIDATE_STATUSES,
        assignment_algorithm_categories=ASSIGNMENT_ALGORITHM_CATEGORIES,
        future_contract_concepts=FUTURE_CONTRACT_CONCEPTS,
        future_output_concepts=FUTURE_OUTPUT_CONCEPTS,
        assignment_plan_fields=ASSIGNMENT_PLAN_FIELDS,
        assignment_candidate_fields=ASSIGNMENT_CANDIDATE_FIELDS,
        unit_allocation_fields=UNIT_ALLOCATION_FIELDS,
        input_dependencies=INPUT_DEPENDENCIES,
        readiness_gates=READINESS_GATES,
        retry_categories=RETRY_CATEGORIES,
        contract_examples=CONTRACT_EXAMPLES,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        alternative_next_artifact=ALTERNATIVE_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_design_assignment_runtime_contract(
    contract: DesignAssignmentRuntimeContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.design_assignment_runtime_contract_defined:
        issues.append("design_assignment_runtime_contract_defined must be true")
    if not contract.reproducibility_manifest_contract_defined:
        issues.append("reproducibility_manifest_contract_defined must be true")
    if len(contract.future_assignment_runtime_statuses) < 15:
        issues.append("future_assignment_runtime_statuses incomplete")
    if len(contract.readiness_gates) < 14:
        issues.append("readiness_gates incomplete")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_design_assignment_runtime_contract()
    validation = validate_design_assignment_runtime_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in FUTURE_ASSIGNMENT_RUNTIME_STATUSES:
        scenarios.append(_s(f"runtime_status_{status}", status in contract.future_assignment_runtime_statuses))
    for status in FUTURE_ASSIGNMENT_CANDIDATE_STATUSES:
        scenarios.append(_s(f"candidate_status_{status}", status in contract.future_assignment_candidate_statuses))
    for cat in ASSIGNMENT_ALGORITHM_CATEGORIES:
        scenarios.append(_s(f"algorithm_category_{cat}", cat in contract.assignment_algorithm_categories))
    for dep in INPUT_DEPENDENCIES:
        scenarios.append(_s(f"input_dependency_{dep}", dep in contract.input_dependencies))
    for gate in READINESS_GATES:
        scenarios.append(_s(f"readiness_gate_{gate}", gate in contract.readiness_gates))
    for field in ASSIGNMENT_PLAN_FIELDS:
        scenarios.append(_s(f"plan_field_{field}", field in contract.assignment_plan_fields))
    for field in ASSIGNMENT_CANDIDATE_FIELDS:
        scenarios.append(_s(f"candidate_field_{field}", field in contract.assignment_candidate_fields))
    for field in UNIT_ALLOCATION_FIELDS:
        scenarios.append(_s(f"unit_allocation_field_{field}", field in contract.unit_allocation_fields))
    for ex in CONTRACT_EXAMPLES:
        scenarios.append(_s(f"example_{ex}", ex in contract.contract_examples))
    for concept in FUTURE_CONTRACT_CONCEPTS:
        scenarios.append(_s(f"contract_concept_{concept}", concept in contract.future_contract_concepts))
    for concept in FUTURE_OUTPUT_CONCEPTS:
        scenarios.append(_s(f"output_concept_{concept}", concept in contract.future_output_concepts))
    for retry in RETRY_CATEGORIES:
        scenarios.append(_s(f"retry_category_{retry}", retry in contract.retry_categories))
    for test_id in FUTURE_IMPLEMENTATION_TESTS:
        scenarios.append(_s(f"future_test_{test_id}", True))
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not contract.authorization_flags[flag]))
    for key in CONTRACT_POSITIVE_FLAGS:
        scenarios.append(_s(f"contract_positive_{key}", CONTRACT_POSITIVE_FLAGS[key]))
    scenarios.append(_s("recommended_next_present", bool(contract.recommended_next_artifact)))
    scenarios.append(_s("final_verdict_matches", contract.final_verdict == _VERDICT))
    scenarios.append(_s("validation_valid", validation["valid"]))
    scenarios.append(_s("failed_scenarios_empty", all(x["passed"] for x in scenarios)))
    return scenarios


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    contract = build_design_assignment_runtime_contract()
    validation = validate_design_assignment_runtime_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "design_assignment_runtime_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": SCOPE,
        "depends_on": list(DEPENDS_ON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "recommended_next_artifact": RECOMMENDED_NEXT_ARTIFACT,
        "alternative_next_artifact": ALTERNATIVE_NEXT_ARTIFACT,
        "failed_scenarios": failed,
        "validation": validation,
        **CONTRACT_POSITIVE_FLAGS,
        **_AUTH_FLAGS,
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {"verdict": _VERDICT, "failed_scenarios": failed, "validation": validation}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=not args.no_write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
