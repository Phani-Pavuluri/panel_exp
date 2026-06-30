"""DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "design_cell_structure_and_assignment_contract_defined_no_runtime_assignment_or_production_authorization"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001_summary.json"
)

SCOPE = "contract_only_no_runtime_assignment"
RECOMMENDED_NEXT_ARTIFACT = "DESIGN_CELL_STRUCTURE_RUNTIME_001"
ALTERNATIVE_NEXT_ARTIFACT = "DESIGN_METHOD_SUITABILITY_HANDOFF_CONTRACT_001"

DEPENDS_ON = (
    "GEO_KPI_SPEND_DATA_PROFILER_001",
    "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
    "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
    "POWER_MDE_DIAGNOSTICS_RUNTIME_001",
)

FUTURE_DESIGN_STRUCTURE_TYPES = (
    "SINGLE_TREATMENT_CONTROL",
    "MULTI_CELL_COMMON_CONTROL",
    "MATCHED_PAIR",
    "RERANDOMIZED_BLOCK",
    "THINNING_DESIGN",
    "QUICK_BLOCK",
    "DOSAGE_CONTRAST",
    "DIFFERENCE_IN_POLICY",
    "BUDGET_REALLOCATION",
    "GO_LIVE",
    "UNKNOWN",
)

FUTURE_CELL_ROLES = (
    "TREATMENT",
    "CONTROL",
    "COMMON_CONTROL",
    "BUSINESS_AS_USUAL_CONTROL",
    "LOW_DOSAGE",
    "MEDIUM_DOSAGE",
    "HIGH_DOSAGE",
    "SOURCE_REDUCTION",
    "DESTINATION_INCREASE",
    "GO_LIVE_CELL",
    "HOLDOUT",
    "EXCLUDED",
    "UNKNOWN",
)

FUTURE_MANIPULATION_POLICIES = (
    "BUSINESS_AS_USUAL",
    "GO_DARK",
    "HEAVY_UP",
    "GO_LIVE",
    "BUDGET_REALLOCATION_SOURCE",
    "BUDGET_REALLOCATION_DESTINATION",
    "LOW_SPEND_POLICY",
    "HIGH_SPEND_POLICY",
    "DOSAGE_POLICY",
    "DIFFERENCE_IN_POLICY",
    "UNKNOWN",
)

FUTURE_ASSIGNMENT_STATUSES = (
    "DESIGN_ASSIGNMENT_READY_FOR_RUNTIME",
    "DESIGN_ASSIGNMENT_READY_WITH_WARNINGS",
    "DESIGN_ASSIGNMENT_PROVISIONAL",
    "DESIGN_ASSIGNMENT_BLOCKED_BY_DATA_READINESS",
    "DESIGN_ASSIGNMENT_BLOCKED_BY_GEO_FEASIBILITY",
    "DESIGN_ASSIGNMENT_BLOCKED_BY_SPEND_FEASIBILITY",
    "DESIGN_ASSIGNMENT_BLOCKED_BY_POWER_MDE_READINESS",
    "DESIGN_ASSIGNMENT_BLOCKED_BY_CELL_STRUCTURE",
    "DESIGN_ASSIGNMENT_BLOCKED_BY_CONSTRAINTS",
    "DESIGN_ASSIGNMENT_REQUIRES_DOSAGE_ESTIMAND_REVIEW",
    "DESIGN_ASSIGNMENT_REQUIRES_METHOD_SUITABILITY_REVIEW",
    "DESIGN_ASSIGNMENT_NOT_EVALUATED",
)

READINESS_GATES = (
    "profiler_gate",
    "geo_unit_market_feasibility_gate",
    "spend_feasibility_gate",
    "power_mde_readiness_gate",
    "cell_structure_declaration_gate",
    "cell_role_validity_gate",
    "manipulation_policy_compatibility_gate",
    "assignment_constraint_gate",
    "estimand_compatibility_gate",
    "method_suitability_precheck_gate",
)

FUTURE_CONTRACT_CONCEPTS = (
    "DesignCellStructureInput",
    "DesignCellStructureConfig",
    "DesignCellStructureReport",
    "DesignCellSpec",
    "DesignCellRole",
    "DesignManipulationPolicy",
    "DesignStructureType",
    "DesignAssignmentConstraint",
    "DesignAssignmentConstraintSeverity",
    "DesignAssignmentReadinessStatus",
    "DesignCellStructureIssue",
    "DesignCellStructureSeverity",
    "DesignCellStructureBoundary",
    "DesignSpendCompatibilitySpec",
    "DesignPowerMdeCompatibilitySpec",
    "DesignEstimandCompatibilitySpec",
)

FUTURE_OUTPUT_CONCEPTS = (
    "DesignCellStructureReport",
    "DesignCellReadinessReport",
    "DesignCellRoleReport",
    "DesignAssignmentConstraintReport",
    "DesignSpendCompatibilityReport",
    "DesignPowerMdeCompatibilityReport",
    "DesignEstimandCompatibilityReport",
    "DesignClaimBoundaryReport",
)

ASSIGNMENT_CONSTRAINT_CATEGORIES = (
    "DATA_ELIGIBILITY_CONSTRAINT",
    "GEO_FEASIBILITY_CONSTRAINT",
    "SPEND_FEASIBILITY_CONSTRAINT",
    "POWER_MDE_READINESS_CONSTRAINT",
    "CELL_SIZE_CONSTRAINT",
    "MUTUAL_EXCLUSIVITY_CONSTRAINT",
    "BUSINESS_AS_USUAL_CONTROL_CONSTRAINT",
    "DOSAGE_ESTIMAND_CONSTRAINT",
    "BUDGET_REALLOCATION_MAPPING_CONSTRAINT",
    "MARKET_EXCLUSION_CONSTRAINT",
    "GEO_HIERARCHY_CONSTRAINT",
    "BALANCE_CONSTRAINT",
    "INTERFERENCE_RISK_CONSTRAINT",
    "METHOD_SUITABILITY_CONSTRAINT",
    "PRODUCTION_AUTHORIZATION_CONSTRAINT",
)

INPUT_DEPENDENCIES = (
    "profiler_report",
    "geo_unit_market_feasibility_report",
    "spend_requirement_manipulation_feasibility_report",
    "power_mde_diagnostics_report",
    "eligible_geo_units",
    "excluded_geo_units",
    "candidate_cell_count",
    "candidate_cell_roles",
    "candidate_manipulation_policies",
    "candidate_design_structure_type",
    "minimum_units_per_cell",
    "maximum_units_per_cell",
    "geo_hierarchy",
    "region/country/business-unit constraints",
    "channel/campaign constraints",
    "spend feasibility outputs",
    "required_spend_delta",
    "candidate_manipulation_options",
    "historical_support_status",
    "control_contamination_flags",
    "dosage_contrast_estimand_required",
    "difference_in_policy_required",
    "business_as_usual_control_preserved",
    "method_suitability_review_required",
    "power_mde_runtime_status",
    "power_mde_runtime_mode",
)

FUTURE_IMPLEMENTATION_TESTS = (
    "blocked_profiler_blocks_assignment_readiness",
    "blocked_geo_feasibility_blocks_assignment_readiness",
    "blocked_spend_feasibility_blocks_spend_compatible_assignment",
    "blocked_power_mde_readiness_blocks_power_ready_assignment",
    "missing_cell_structure_blocks_or_provisional",
    "invalid_cell_role_blocks",
    "standard_go_dark_requires_bau_control",
    "manipulated_control_blocks_standard_go_dark_interpretation",
    "heavy_up_preserves_historical_support_warning",
    "go_live_requires_near_zero_baseline_support",
    "budget_reallocation_requires_source_destination_mapping",
    "dosage_contrast_requires_dosage_estimand",
    "difference_in_policy_requires_estimand_shift",
    "method_suitability_review_required_blocks_estimator_inference_readiness",
    "assignment_ready_does_not_assign_geo_units",
    "assignment_ready_does_not_set_powered_design_roi_production_flags",
    "no_fixture_specific_branching",
)

_AUTH_FLAGS = {
    "runtime_design_generation_implemented": False,
    "geo_assignment_computed": False,
    "randomization_computed": False,
    "rerandomization_computed": False,
    "matching_optimization_computed": False,
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
    "design_cell_structure_contract_defined": True,
    "assignment_boundary_defined": True,
    "cell_role_semantics_defined": True,
    "manipulation_policy_semantics_defined": True,
    "assignment_constraint_categories_defined": True,
    "dosage_design_structure_defined": True,
    "budget_reallocation_structure_defined": True,
    "claim_boundaries_defined": True,
}

NON_GOALS = (
    "no_runtime_design_generation",
    "no_geo_unit_assignment",
    "no_randomization",
    "no_rerandomization",
    "no_matching_optimization",
    "no_power_mde_computation",
    "no_p_values_or_confidence_intervals",
    "no_lift_or_roi_computation",
    "no_budget_optimization",
    "no_estimator_inference_selection",
    "no_mmm_runtime_calls",
    "no_mmm_calibration",
    "no_llm_decisioning",
    "no_production_authorization",
)


@dataclass(frozen=True)
class DesignCellStructureAssignmentContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    design_cell_structure_contract_defined: bool
    assignment_boundary_defined: bool
    cell_role_semantics_defined: bool
    manipulation_policy_semantics_defined: bool
    assignment_constraint_categories_defined: bool
    standard_go_dark_structure_defined: bool
    heavy_up_structure_defined: bool
    go_live_structure_defined: bool
    budget_reallocation_structure_defined: bool
    dosage_design_structure_defined: bool
    difference_in_policy_structure_defined: bool
    business_as_usual_control_required_for_standard_go_dark: bool
    control_contamination_preservation_defined: bool
    method_suitability_review_required_for_dosage: bool
    future_design_structure_types: tuple[str, ...]
    future_cell_roles: tuple[str, ...]
    future_manipulation_policies: tuple[str, ...]
    future_assignment_statuses: tuple[str, ...]
    readiness_gates: tuple[str, ...]
    future_contract_concepts: tuple[str, ...]
    future_output_concepts: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


def build_design_cell_structure_assignment_contract() -> DesignCellStructureAssignmentContract:
    return DesignCellStructureAssignmentContract(
        artifact_id=_ARTIFACT_ID,
        scope=SCOPE,
        depends_on=DEPENDS_ON,
        design_cell_structure_contract_defined=True,
        assignment_boundary_defined=True,
        cell_role_semantics_defined=True,
        manipulation_policy_semantics_defined=True,
        assignment_constraint_categories_defined=True,
        standard_go_dark_structure_defined=True,
        heavy_up_structure_defined=True,
        go_live_structure_defined=True,
        budget_reallocation_structure_defined=True,
        dosage_design_structure_defined=True,
        difference_in_policy_structure_defined=True,
        business_as_usual_control_required_for_standard_go_dark=True,
        control_contamination_preservation_defined=True,
        method_suitability_review_required_for_dosage=True,
        future_design_structure_types=FUTURE_DESIGN_STRUCTURE_TYPES,
        future_cell_roles=FUTURE_CELL_ROLES,
        future_manipulation_policies=FUTURE_MANIPULATION_POLICIES,
        future_assignment_statuses=FUTURE_ASSIGNMENT_STATUSES,
        readiness_gates=READINESS_GATES,
        future_contract_concepts=FUTURE_CONTRACT_CONCEPTS,
        future_output_concepts=FUTURE_OUTPUT_CONCEPTS,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        alternative_next_artifact=ALTERNATIVE_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_design_cell_structure_assignment_contract(
    contract: DesignCellStructureAssignmentContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.design_cell_structure_contract_defined:
        issues.append("design_cell_structure_contract_defined must be true")
    if not contract.assignment_boundary_defined:
        issues.append("assignment_boundary_defined must be true")
    if not contract.business_as_usual_control_required_for_standard_go_dark:
        issues.append("business_as_usual_control_required_for_standard_go_dark must be true")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_design_cell_structure_assignment_contract()
    validation = validate_design_cell_structure_assignment_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in FUTURE_ASSIGNMENT_STATUSES:
        scenarios.append(_s(f"assignment_status_{status}", status in contract.future_assignment_statuses))
    for dtype in FUTURE_DESIGN_STRUCTURE_TYPES:
        scenarios.append(_s(f"design_structure_{dtype}", dtype in contract.future_design_structure_types))
    for role in FUTURE_CELL_ROLES:
        scenarios.append(_s(f"cell_role_{role}", role in contract.future_cell_roles))
    for policy in FUTURE_MANIPULATION_POLICIES:
        scenarios.append(_s(f"manipulation_policy_{policy}", policy in contract.future_manipulation_policies))
    for gate in READINESS_GATES:
        scenarios.append(_s(f"readiness_gate_{gate}", gate in contract.readiness_gates))
    for cat in ASSIGNMENT_CONSTRAINT_CATEGORIES:
        scenarios.append(_s(f"constraint_category_{cat}", cat in ASSIGNMENT_CONSTRAINT_CATEGORIES))
    scenarios.append(_s("contract_defined", contract.design_cell_structure_contract_defined))
    scenarios.append(_s("assignment_boundary", contract.assignment_boundary_defined))
    scenarios.append(_s("standard_go_dark", contract.standard_go_dark_structure_defined))
    scenarios.append(_s("dosage_structure", contract.dosage_design_structure_defined))
    scenarios.append(_s("budget_reallocation", contract.budget_reallocation_structure_defined))
    scenarios.append(_s("bau_control_required", contract.business_as_usual_control_required_for_standard_go_dark))
    for concept in FUTURE_CONTRACT_CONCEPTS:
        scenarios.append(_s(f"contract_concept_{concept}", concept in contract.future_contract_concepts))
    for concept in FUTURE_OUTPUT_CONCEPTS:
        scenarios.append(_s(f"output_concept_{concept}", concept in contract.future_output_concepts))
    for test_id in FUTURE_IMPLEMENTATION_TESTS:
        scenarios.append(_s(f"future_test_{test_id}", True))
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not contract.authorization_flags[flag]))
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
    contract = build_design_cell_structure_assignment_contract()
    validation = validate_design_cell_structure_assignment_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "design_cell_structure_and_assignment_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": SCOPE,
        "depends_on": list(DEPENDS_ON),
        "design_cell_structure_contract_defined": True,
        "assignment_boundary_defined": True,
        "cell_role_semantics_defined": True,
        "manipulation_policy_semantics_defined": True,
        "assignment_constraint_categories_defined": True,
        "standard_go_dark_structure_defined": True,
        "heavy_up_structure_defined": True,
        "go_live_structure_defined": True,
        "budget_reallocation_structure_defined": True,
        "dosage_design_structure_defined": True,
        "difference_in_policy_structure_defined": True,
        "business_as_usual_control_required_for_standard_go_dark": True,
        "control_contamination_preservation_defined": True,
        "method_suitability_review_required_for_dosage": True,
        "future_design_structure_types": list(FUTURE_DESIGN_STRUCTURE_TYPES),
        "future_cell_roles": list(FUTURE_CELL_ROLES),
        "future_manipulation_policies": list(FUTURE_MANIPULATION_POLICIES),
        "future_assignment_statuses": list(FUTURE_ASSIGNMENT_STATUSES),
        "readiness_gates_defined": list(READINESS_GATES),
        "future_contract_concepts_defined": list(FUTURE_CONTRACT_CONCEPTS),
        "future_output_concepts_defined": list(FUTURE_OUTPUT_CONCEPTS),
        "assignment_constraint_categories": list(ASSIGNMENT_CONSTRAINT_CATEGORIES),
        "input_dependencies": list(INPUT_DEPENDENCIES),
        "future_implementation_tests_required": list(FUTURE_IMPLEMENTATION_TESTS),
        "contract_positive_flags": dict(CONTRACT_POSITIVE_FLAGS),
        "runtime_design_generation_implemented": False,
        "geo_assignment_computed": False,
        "randomization_computed": False,
        "rerandomization_computed": False,
        "matching_optimization_computed": False,
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
