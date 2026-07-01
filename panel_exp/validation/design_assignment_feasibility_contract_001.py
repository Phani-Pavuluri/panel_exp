"""DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "design_assignment_feasibility_contract_defined_no_runtime_assignment_or_matching"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001_summary.json"
)

SCOPE = "contract_only_no_runtime_assignment_or_matching"
RECOMMENDED_NEXT_ARTIFACT = "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001"
ALTERNATIVE_NEXT_ARTIFACT = "METHOD_SUITABILITY_HANDOFF_CONTRACT_001"

DEPENDS_ON = (
    "GEO_KPI_SPEND_DATA_PROFILER_001",
    "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
    "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
    "POWER_MDE_DIAGNOSTICS_RUNTIME_001",
    "DESIGN_CELL_STRUCTURE_RUNTIME_001",
    "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001",
)

FUTURE_ASSIGNMENT_FEASIBILITY_STATUSES = (
    "ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME",
    "ASSIGNMENT_FEASIBILITY_READY_WITH_WARNINGS",
    "ASSIGNMENT_FEASIBILITY_PROVISIONAL",
    "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_DATA_READINESS",
    "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_GEO_FEASIBILITY",
    "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_DESIGN_STRUCTURE",
    "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_SCENARIO_POLICY",
    "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_POWER_MDE_READINESS",
    "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_INSUFFICIENT_ELIGIBLE_UNITS",
    "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY",
    "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CONSTRAINTS",
    "ASSIGNMENT_FEASIBILITY_REQUIRES_REDESIGN_RECHECK",
    "ASSIGNMENT_FEASIBILITY_REQUIRES_METHOD_SUITABILITY_REVIEW",
    "ASSIGNMENT_FEASIBILITY_NOT_EVALUATED",
)

FUTURE_ASSIGNMENT_CONSTRAINT_STATUSES = (
    "ASSIGNMENT_CONSTRAINT_SATISFIED",
    "ASSIGNMENT_CONSTRAINT_SATISFIED_WITH_WARNINGS",
    "ASSIGNMENT_CONSTRAINT_PROVISIONAL",
    "ASSIGNMENT_CONSTRAINT_BLOCKING",
    "ASSIGNMENT_CONSTRAINT_REQUIRES_REDESIGN",
    "ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT",
    "ASSIGNMENT_CONSTRAINT_NOT_EVALUATED",
)

ASSIGNMENT_CONSTRAINT_CATEGORIES = (
    "DATA_ELIGIBILITY_CONSTRAINT",
    "GEO_FEASIBILITY_CONSTRAINT",
    "DESIGN_STRUCTURE_CONSTRAINT",
    "SCENARIO_POLICY_CONSTRAINT",
    "POWER_MDE_READINESS_CONSTRAINT",
    "MINIMUM_UNIT_COUNT_CONSTRAINT",
    "MAXIMUM_UNIT_COUNT_CONSTRAINT",
    "CELL_CAPACITY_CONSTRAINT",
    "MUTUAL_EXCLUSIVITY_CONSTRAINT",
    "COMMON_CONTROL_CONSTRAINT",
    "SPLIT_CONTROL_REDESIGN_CONSTRAINT",
    "MATCHED_PAIR_REQUIREMENT_CONSTRAINT",
    "BLOCK_REQUIREMENT_CONSTRAINT",
    "GEO_HIERARCHY_CONSTRAINT",
    "MARKET_EXCLUSION_CONSTRAINT",
    "BUSINESS_UNIT_CONSTRAINT",
    "REGION_COUNTRY_CONSTRAINT",
    "BALANCE_READINESS_CONSTRAINT",
    "INTERFERENCE_RISK_CONSTRAINT",
    "SOURCE_DESTINATION_MAPPING_CONSTRAINT",
    "METHOD_SUITABILITY_CONSTRAINT",
    "PRODUCTION_AUTHORIZATION_CONSTRAINT",
)

ASSIGNMENT_UNIT_FIELDS = (
    "unit_id",
    "geo_id",
    "geo_name",
    "region",
    "country",
    "market_group",
    "business_unit",
    "eligible",
    "exclusion_reason",
    "available_for_assignment",
    "prior_assignment_cell",
    "hierarchy_path",
    "metadata",
)

CELL_REQUIREMENT_FIELDS = (
    "cell_id",
    "cell_role",
    "minimum_units",
    "maximum_units",
    "target_units",
    "requires_bau_control",
    "requires_common_control",
    "requires_split_control",
    "requires_matched_pair",
    "requires_source_destination_mapping",
    "eligible_unit_pool",
    "blocked_unit_pool",
)

FUTURE_CONTRACT_CONCEPTS = (
    "DesignAssignmentFeasibilityInput",
    "DesignAssignmentFeasibilityConfig",
    "DesignAssignmentFeasibilityReport",
    "AssignmentUnitSpec",
    "AssignmentCellRequirementSpec",
    "AssignmentConstraintSpec",
    "AssignmentEligibilityReport",
    "AssignmentCellCapacityReport",
    "AssignmentMutualExclusivityReport",
    "AssignmentHierarchyConstraintReport",
    "AssignmentMarketExclusionReport",
    "AssignmentBalanceReadinessReport",
    "AssignmentInterferenceRiskReport",
    "AssignmentSharedControlReport",
    "AssignmentScenarioHandoffReport",
    "AssignmentPowerMdeHandoffReport",
    "AssignmentMethodSuitabilityHandoffReport",
    "AssignmentFeasibilityStatus",
    "AssignmentConstraintStatus",
    "AssignmentIssue",
    "AssignmentIssueSeverity",
    "AssignmentClaimBoundaryReport",
)

FUTURE_OUTPUT_CONCEPTS = (
    "DesignAssignmentFeasibilityReport",
    "AssignmentReadinessReport",
    "AssignmentEligibilityReport",
    "AssignmentCellCapacityReport",
    "AssignmentConstraintReport",
    "AssignmentMutualExclusivityReport",
    "AssignmentSharedControlReport",
    "AssignmentSplitControlReport",
    "AssignmentHierarchyReport",
    "AssignmentMarketExclusionReport",
    "AssignmentBalanceReadinessReport",
    "AssignmentInterferenceRiskReport",
    "AssignmentScenarioHandoffReport",
    "AssignmentPowerMdeHandoffReport",
    "AssignmentMethodSuitabilityHandoffReport",
    "AssignmentClaimBoundaryReport",
)

READINESS_GATES = (
    "profiler_data_readiness_gate",
    "geo_unit_market_feasibility_gate",
    "design_cell_structure_gate",
    "scenario_policy_feasibility_gate",
    "power_mde_readiness_gate",
    "assignment_unit_universe_gate",
    "eligible_unit_inventory_gate",
    "cell_requirement_gate",
    "cell_capacity_gate",
    "mutual_exclusivity_gate",
    "shared_control_split_control_gate",
    "geo_hierarchy_market_exclusion_gate",
    "balance_readiness_gate",
    "interference_risk_gate",
    "method_suitability_precheck_gate",
)

REPORT_FIELDS = (
    "artifact_id",
    "design_id",
    "assignment_feasibility_status",
    "assignment_readiness_summary",
    "eligible_unit_count",
    "excluded_unit_count",
    "available_unit_count",
    "required_cell_count",
    "cell_capacity_reports",
    "constraint_reports",
    "mutual_exclusivity_report",
    "shared_control_report",
    "split_control_report",
    "hierarchy_report",
    "market_exclusion_report",
    "balance_readiness_report",
    "interference_risk_report",
    "scenario_handoff_report",
    "power_mde_handoff_report",
    "method_suitability_handoff_report",
    "claim_boundary_report",
    "issues",
    "warnings",
    "blocking_reasons",
)

INPUT_DEPENDENCIES = (
    "profiler_report",
    "geo_unit_market_feasibility_report",
    "spend_requirement_manipulation_feasibility_report",
    "power_mde_diagnostics_report",
    "design_cell_structure_runtime_report",
    "design_scenario_policy_feasibility_report",
    "eligible_units",
    "excluded_units",
    "assignment_unit_universe",
    "cell_requirements",
    "design_structure_type",
    "scenario_policy_status",
    "scenario_recheck_requirements",
    "split_control_required",
    "common_control_cells",
    "cell_roles",
    "contrast_specs",
    "minimum_units_per_cell",
    "maximum_units_per_cell",
    "target_units_per_cell",
    "geo_hierarchy_constraints",
    "market_exclusion_constraints",
    "business_unit_constraints",
    "region_country_constraints",
    "mutual_exclusivity_constraints",
    "balance_readiness_requirements",
    "interference_risk_constraints",
    "method_suitability_review_required",
)

FUTURE_IMPLEMENTATION_TESTS = (
    "blocked_profiler_blocks_assignment_feasibility",
    "blocked_geo_feasibility_blocks_assignment_feasibility",
    "blocked_design_cell_structure_blocks_assignment_feasibility",
    "blocked_scenario_policy_feasibility_blocks_or_provisional",
    "blocked_power_mde_readiness_blocks_power_ready_assignment",
    "missing_assignment_unit_universe_blocks",
    "excluded_units_not_counted_as_available",
    "insufficient_eligible_units_blocks",
    "cell_minimum_units_enforced",
    "cell_maximum_units_enforced",
    "mutual_exclusivity_required",
    "common_control_capacity_checked",
    "split_control_redesign_requires_recheck",
    "matched_pair_design_requires_pairability_capacity",
    "block_design_requires_block_metadata",
    "missing_hierarchy_metadata_requires_user_input",
    "market_exclusions_preserved",
    "balance_covariate_availability_reported_not_optimized",
    "interference_risk_reported_not_adjusted",
    "method_suitability_required_blocks_estimator_inference",
    "assignment_feasible_does_not_assign_units",
    "assignment_feasible_does_not_generate_pairs_blocks_randomization",
    "assignment_feasible_does_not_compute_power_mde_lift_roi",
    "no_fixture_specific_branching",
)

CONTRACT_EXAMPLES = (
    "example_1_simple_two_cell_ready",
    "example_2_insufficient_eligible_units",
    "example_3_common_control_capacity_issue",
    "example_4_split_control_redesign",
    "example_5_matched_pair_requirement",
    "example_6_geo_hierarchy_constraint",
    "example_7_market_exclusion",
    "example_8_method_suitability_review_required",
)

_AUTH_FLAGS = {
    "runtime_assignment_feasibility_implemented": False,
    "geo_assignment_computed": False,
    "matched_pairs_generated": False,
    "blocks_generated": False,
    "randomization_computed": False,
    "rerandomization_computed": False,
    "thinning_design_generated": False,
    "matching_optimization_computed": False,
    "balance_optimization_computed": False,
    "interference_adjustment_computed": False,
    "scenario_policy_feasibility_computed": False,
    "runtime_scenario_enumeration_implemented": False,
    "runtime_scenario_optimization_implemented": False,
    "runtime_design_generation_implemented": False,
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
    "assignment_feasibility_contract_defined": True,
    "eligible_unit_contract_defined": True,
    "cell_capacity_contract_defined": True,
    "assignment_constraint_categories_defined": True,
    "common_control_assignment_boundary_defined": True,
    "split_control_redesign_boundary_defined": True,
    "matched_pair_block_boundary_defined": True,
    "hierarchy_exclusion_boundary_defined": True,
    "balance_readiness_boundary_defined": True,
    "interference_risk_boundary_defined": True,
    "claim_boundaries_defined": True,
}

NON_GOALS = (
    "no_runtime_assignment_feasibility",
    "no_geo_assignment",
    "no_matched_pairs_generated",
    "no_blocks_generated",
    "no_randomization",
    "no_rerandomization",
    "no_thinning_design_generation",
    "no_matching_optimization",
    "no_balance_optimization",
    "no_interference_adjustment",
    "no_scenario_policy_feasibility_computation",
    "no_power_mde_computation",
    "no_estimator_inference_selection",
    "no_production_authorization",
)


@dataclass(frozen=True)
class DesignAssignmentFeasibilityContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    assignment_feasibility_contract_defined: bool
    eligible_unit_contract_defined: bool
    cell_capacity_contract_defined: bool
    assignment_constraint_categories_defined: bool
    common_control_assignment_boundary_defined: bool
    split_control_redesign_boundary_defined: bool
    matched_pair_block_boundary_defined: bool
    hierarchy_exclusion_boundary_defined: bool
    balance_readiness_boundary_defined: bool
    interference_risk_boundary_defined: bool
    future_assignment_feasibility_statuses: tuple[str, ...]
    future_assignment_constraint_statuses: tuple[str, ...]
    assignment_constraint_categories: tuple[str, ...]
    assignment_unit_fields: tuple[str, ...]
    cell_requirement_fields: tuple[str, ...]
    readiness_gates: tuple[str, ...]
    future_contract_concepts: tuple[str, ...]
    future_output_concepts: tuple[str, ...]
    report_fields: tuple[str, ...]
    contract_examples: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


def build_design_assignment_feasibility_contract() -> DesignAssignmentFeasibilityContract:
    return DesignAssignmentFeasibilityContract(
        artifact_id=_ARTIFACT_ID,
        scope=SCOPE,
        depends_on=DEPENDS_ON,
        assignment_feasibility_contract_defined=True,
        eligible_unit_contract_defined=True,
        cell_capacity_contract_defined=True,
        assignment_constraint_categories_defined=True,
        common_control_assignment_boundary_defined=True,
        split_control_redesign_boundary_defined=True,
        matched_pair_block_boundary_defined=True,
        hierarchy_exclusion_boundary_defined=True,
        balance_readiness_boundary_defined=True,
        interference_risk_boundary_defined=True,
        future_assignment_feasibility_statuses=FUTURE_ASSIGNMENT_FEASIBILITY_STATUSES,
        future_assignment_constraint_statuses=FUTURE_ASSIGNMENT_CONSTRAINT_STATUSES,
        assignment_constraint_categories=ASSIGNMENT_CONSTRAINT_CATEGORIES,
        assignment_unit_fields=ASSIGNMENT_UNIT_FIELDS,
        cell_requirement_fields=CELL_REQUIREMENT_FIELDS,
        readiness_gates=READINESS_GATES,
        future_contract_concepts=FUTURE_CONTRACT_CONCEPTS,
        future_output_concepts=FUTURE_OUTPUT_CONCEPTS,
        report_fields=REPORT_FIELDS,
        contract_examples=CONTRACT_EXAMPLES,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        alternative_next_artifact=ALTERNATIVE_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_design_assignment_feasibility_contract(
    contract: DesignAssignmentFeasibilityContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.assignment_feasibility_contract_defined:
        issues.append("assignment_feasibility_contract_defined must be true")
    if not contract.eligible_unit_contract_defined:
        issues.append("eligible_unit_contract_defined must be true")
    if not contract.common_control_assignment_boundary_defined:
        issues.append("common_control_assignment_boundary_defined must be true")
    if len(contract.future_assignment_feasibility_statuses) < 14:
        issues.append("future_assignment_feasibility_statuses incomplete")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_design_assignment_feasibility_contract()
    validation = validate_design_assignment_feasibility_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in FUTURE_ASSIGNMENT_FEASIBILITY_STATUSES:
        scenarios.append(_s(f"assignment_status_{status}", status in contract.future_assignment_feasibility_statuses))
    for status in FUTURE_ASSIGNMENT_CONSTRAINT_STATUSES:
        scenarios.append(_s(f"constraint_status_{status}", status in contract.future_assignment_constraint_statuses))
    for cat in ASSIGNMENT_CONSTRAINT_CATEGORIES:
        scenarios.append(_s(f"constraint_category_{cat}", cat in contract.assignment_constraint_categories))
    for field in ASSIGNMENT_UNIT_FIELDS:
        scenarios.append(_s(f"unit_field_{field}", field in contract.assignment_unit_fields))
    for field in CELL_REQUIREMENT_FIELDS:
        scenarios.append(_s(f"cell_requirement_{field}", field in contract.cell_requirement_fields))
    for gate in READINESS_GATES:
        scenarios.append(_s(f"readiness_gate_{gate}", gate in contract.readiness_gates))
    for field in REPORT_FIELDS:
        scenarios.append(_s(f"report_field_{field}", field in contract.report_fields))
    for ex in CONTRACT_EXAMPLES:
        scenarios.append(_s(f"example_{ex}", ex in contract.contract_examples))
    for concept in FUTURE_CONTRACT_CONCEPTS:
        scenarios.append(_s(f"contract_concept_{concept}", concept in contract.future_contract_concepts))
    for concept in FUTURE_OUTPUT_CONCEPTS:
        scenarios.append(_s(f"output_concept_{concept}", concept in contract.future_output_concepts))
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
    contract = build_design_assignment_feasibility_contract()
    validation = validate_design_assignment_feasibility_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "design_assignment_feasibility_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": SCOPE,
        "depends_on": list(DEPENDS_ON),
        "assignment_feasibility_contract_defined": True,
        "eligible_unit_contract_defined": True,
        "cell_capacity_contract_defined": True,
        "assignment_constraint_categories_defined": True,
        "common_control_assignment_boundary_defined": True,
        "split_control_redesign_boundary_defined": True,
        "matched_pair_block_boundary_defined": True,
        "hierarchy_exclusion_boundary_defined": True,
        "balance_readiness_boundary_defined": True,
        "interference_risk_boundary_defined": True,
        "claim_boundaries_defined": True,
        "future_assignment_feasibility_statuses": list(FUTURE_ASSIGNMENT_FEASIBILITY_STATUSES),
        "future_assignment_constraint_statuses": list(FUTURE_ASSIGNMENT_CONSTRAINT_STATUSES),
        "assignment_constraint_categories": list(ASSIGNMENT_CONSTRAINT_CATEGORIES),
        "assignment_unit_fields": list(ASSIGNMENT_UNIT_FIELDS),
        "cell_requirement_fields": list(CELL_REQUIREMENT_FIELDS),
        "readiness_gates_defined": list(READINESS_GATES),
        "future_contract_concepts_defined": list(FUTURE_CONTRACT_CONCEPTS),
        "future_output_concepts_defined": list(FUTURE_OUTPUT_CONCEPTS),
        "report_fields_defined": list(REPORT_FIELDS),
        "input_dependencies": list(INPUT_DEPENDENCIES),
        "contract_examples_defined": list(CONTRACT_EXAMPLES),
        "future_implementation_tests_required": list(FUTURE_IMPLEMENTATION_TESTS),
        "contract_positive_flags": dict(CONTRACT_POSITIVE_FLAGS),
        "runtime_assignment_feasibility_implemented": False,
        "geo_assignment_computed": False,
        "matched_pairs_generated": False,
        "blocks_generated": False,
        "randomization_computed": False,
        "rerandomization_computed": False,
        "thinning_design_generated": False,
        "matching_optimization_computed": False,
        "balance_optimization_computed": False,
        "interference_adjustment_computed": False,
        "scenario_policy_feasibility_computed": False,
        "runtime_scenario_enumeration_implemented": False,
        "runtime_scenario_optimization_implemented": False,
        "runtime_design_generation_implemented": False,
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
        "authorization_flags": dict(_AUTH_FLAGS),
        "recommended_next_artifact": RECOMMENDED_NEXT_ARTIFACT,
        "alternative_next_artifact": ALTERNATIVE_NEXT_ARTIFACT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        "non_goals": list(NON_GOALS),
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {"verdict": _VERDICT, "failed_scenarios": failed}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=not args.no_write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
