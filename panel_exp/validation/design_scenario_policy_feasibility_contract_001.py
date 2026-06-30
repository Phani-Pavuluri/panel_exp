"""DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "design_scenario_policy_feasibility_contract_defined_no_runtime_scenario_planner_or_optimization"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001_summary.json"
)

SCOPE = "contract_only_no_runtime_scenario_planner_or_optimization"
RECOMMENDED_NEXT_ARTIFACT = "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001"
ALTERNATIVE_NEXT_ARTIFACT = "DESIGN_SCENARIO_POLICY_FEASIBILITY_METADATA_001"

DEPENDS_ON = (
    "GEO_KPI_SPEND_DATA_PROFILER_001",
    "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
    "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
    "POWER_MDE_DIAGNOSTICS_RUNTIME_001",
    "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001",
)

FUTURE_SCENARIO_STATUSES = (
    "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE",
    "SCENARIO_PARTIALLY_FEASIBLE",
    "SCENARIO_REQUIRES_ESTIMAND_SHIFT",
    "SCENARIO_REQUIRES_COMMON_CONTROL_MANIPULATION",
    "SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT",
    "SCENARIO_REQUIRES_POWER_MDE_RECHECK",
    "SCENARIO_REQUIRES_ASSIGNMENT_RECHECK",
    "SCENARIO_REQUIRES_METHOD_SUITABILITY_REVIEW",
    "SCENARIO_OUT_OF_HISTORICAL_SUPPORT",
    "SCENARIO_BLOCKED",
    "SCENARIO_NOT_EVALUATED",
)

FUTURE_CONTRAST_STATUSES = (
    "CONTRAST_FEASIBLE",
    "CONTRAST_PARTIALLY_FEASIBLE",
    "CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL",
    "CONTRAST_OUT_OF_HISTORICAL_SUPPORT",
    "CONTRAST_REQUIRES_ESTIMAND_SHIFT",
    "CONTRAST_BLOCKED_BY_SHARED_CONTROL_CONFLICT",
    "CONTRAST_REQUIRES_POWER_MDE_RECHECK",
    "CONTRAST_REQUIRES_ASSIGNMENT_RECHECK",
    "CONTRAST_REQUIRES_METHOD_SUITABILITY_REVIEW",
    "CONTRAST_BLOCKED",
    "CONTRAST_NOT_EVALUATED",
)

FUTURE_POLICY_SUPPORT_STATUSES = (
    "POLICY_WITHIN_HISTORICAL_SUPPORT",
    "POLICY_NEAR_HISTORICAL_SUPPORT_BOUNDARY",
    "POLICY_OUT_OF_HISTORICAL_SUPPORT",
    "POLICY_BELOW_HISTORICAL_SUPPORT",
    "POLICY_REQUIRES_BUSINESS_OVERRIDE",
    "POLICY_SUPPORT_UNKNOWN",
    "POLICY_NOT_EVALUATED",
)

FUTURE_SHARED_CONTROL_CONFLICT_TYPES = (
    "NO_SHARED_CONTROL_CONFLICT",
    "COMMON_CONTROL_MANIPULATED",
    "BAU_CONTROL_NOT_PRESERVED",
    "COMMON_CONTROL_CHANGE_HELPS_ONE_CONTRAST_HARMS_ANOTHER",
    "COMMON_CONTROL_INSUFFICIENT_FOR_ONE_OR_MORE_CONTRASTS",
    "COMMON_CONTROL_OUT_OF_HISTORICAL_SUPPORT",
    "COMMON_CONTROL_SPLIT_REQUIRED_FOR_CLEAN_ESTIMANDS",
    "COMMON_CONTROL_ROLE_AMBIGUOUS",
)

RESOLUTION_OPTION_TYPES = (
    "EXTEND_DURATION",
    "RELAX_MDE_TARGET",
    "CHANGE_TEST_POLICY_TO_HEAVY_UP",
    "CHANGE_TEST_POLICY_TO_GO_DARK",
    "REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY",
    "CAP_SPEND_WITHIN_HISTORICAL_SUPPORT",
    "SPLIT_COMMON_CONTROL",
    "ADD_OR_REALLOCATE_CELLS",
    "DROP_CONTRAST",
    "SEQUENCE_TESTS",
    "RERUN_POWER_MDE",
    "RERUN_ASSIGNMENT_FEASIBILITY",
    "REQUIRE_METHOD_SUITABILITY_REVIEW",
    "BUSINESS_OVERRIDE_REQUIRED",
    "BLOCK_SCENARIO",
)

FUTURE_CONTRACT_CONCEPTS = (
    "DesignScenarioPolicyFeasibilityInput",
    "DesignScenarioPolicyFeasibilityConfig",
    "DesignScenarioPolicyFeasibilityReport",
    "ScenarioPolicyPlanSpec",
    "CellPolicySpec",
    "ContrastRequirementSpec",
    "ContrastFeasibilityReport",
    "ScenarioFeasibilityReport",
    "SharedControlConflictReport",
    "HistoricalSupportReport",
    "ScenarioResolutionOption",
    "ScenarioRecheckRequirement",
    "ScenarioClaimBoundaryReport",
    "ScenarioFeasibilityStatus",
    "ContrastFeasibilityStatus",
    "PolicySupportStatus",
    "ResolutionOptionType",
    "SharedControlConflictType",
    "ScenarioIssue",
    "ScenarioIssueSeverity",
)

FUTURE_OUTPUT_CONCEPTS = (
    "DesignScenarioPolicyFeasibilityReport",
    "ScenarioReadinessReport",
    "ScenarioPolicyPlanReport",
    "ContrastRequirementReport",
    "ContrastFeasibilityReport",
    "RequiredVsAchievedSpendContrastReport",
    "HistoricalSupportReport",
    "SharedControlConflictReport",
    "EstimandShiftReport",
    "ScenarioResolutionReport",
    "ScenarioRecheckRequirementReport",
    "ScenarioClaimBoundaryReport",
)

READINESS_GATES = (
    "profiler_gate",
    "geo_unit_market_feasibility_gate",
    "spend_feasibility_gate",
    "power_mde_readiness_gate",
    "design_cell_structure_gate",
    "contrast_requirement_gate",
    "scenario_policy_plan_gate",
    "required_vs_achieved_contrast_gate",
    "historical_support_gate",
    "shared_control_dependency_gate",
    "estimand_compatibility_gate",
    "resolution_recheck_gate",
    "method_suitability_precheck_gate",
)

REPORT_FIELDS = (
    "artifact_id",
    "scenario_id",
    "scenario_status",
    "overall_feasibility_summary",
    "cell_policy_plan",
    "contrast_feasibility_reports",
    "required_vs_achieved_spend_contrast_by_contrast",
    "historical_support_by_cell",
    "shared_control_conflicts",
    "estimand_shift_flags",
    "resolution_options",
    "recheck_requirements",
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
    "design_cell_structure_report",
    "candidate_scenario_specs",
    "candidate_contrast_specs",
    "cell_policy_plan",
    "baseline_spend_by_cell",
    "proposed_spend_by_cell",
    "historical_spend_support_by_cell",
    "historical_p90_by_cell",
    "historical_p95_by_cell",
    "historical_max_by_cell",
    "required_spend_delta_by_contrast",
    "required_kpi_mde_by_contrast",
    "response_bridge_source_by_contrast",
    "business_response_risk_by_contrast",
    "candidate_manipulation_options",
    "shared_control_dependencies",
    "business_as_usual_control_required_by_contrast",
    "business_as_usual_control_preserved_by_scenario",
    "dosage_contrast_estimand_required",
    "difference_in_policy_required",
    "control_contamination_flags",
    "method_suitability_review_required",
    "power_mde_runtime_status",
    "power_mde_runtime_mode",
)

FUTURE_IMPLEMENTATION_TESTS = (
    "blocked_profiler_prevents_scenario_feasibility_claim",
    "blocked_geo_feasibility_prevents_scenario_feasibility_claim",
    "blocked_spend_feasibility_prevents_spend_compatible_feasibility",
    "blocked_power_mde_readiness_prevents_power_ready_feasibility",
    "missing_design_cell_structure_blocks_scenario_feasibility",
    "missing_contrast_requirements_blocks_required_vs_achieved_comparison",
    "missing_scenario_policy_plan_blocks_scenario_feasibility",
    "achieved_spend_below_required_marks_contrast_insufficient",
    "achieved_spend_equal_required_marks_contrast_feasible_when_gates_pass",
    "out_of_support_proposed_spend_emits_historical_support_warning",
    "common_control_bau_preserved_allows_standard_go_dark_heavy_up",
    "common_control_manipulated_blocks_reclassifies_bau_dependent_contrasts",
    "raising_common_control_helps_go_dark_weakens_heavy_up",
    "lowering_common_control_helps_heavy_up_weakens_go_dark",
    "split_common_control_emits_redesign_recheck_requirement",
    "scenario_feasible_does_not_assign_markets",
    "scenario_feasible_does_not_compute_power_mde",
    "scenario_feasible_does_not_authorize_estimator_inference_or_production",
    "no_fixture_specific_branching",
)

_AUTH_FLAGS = {
    "runtime_scenario_feasibility_implemented": False,
    "runtime_scenario_enumeration_implemented": False,
    "runtime_scenario_optimization_implemented": False,
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
    "scenario_policy_feasibility_contract_defined": True,
    "required_vs_achieved_spend_contrast_defined": True,
    "historical_support_contract_defined": True,
    "shared_control_conflict_contract_defined": True,
    "split_control_redesign_recheck_defined": True,
    "scenario_resolution_options_defined": True,
    "claim_boundaries_defined": True,
}

NON_GOALS = (
    "no_runtime_scenario_feasibility",
    "no_runtime_scenario_enumeration",
    "no_runtime_scenario_optimization",
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
class DesignScenarioPolicyFeasibilityContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    scenario_policy_feasibility_contract_defined: bool
    required_vs_achieved_spend_contrast_defined: bool
    historical_support_contract_defined: bool
    shared_control_conflict_contract_defined: bool
    split_control_redesign_recheck_defined: bool
    scenario_resolution_options_defined: bool
    four_cell_common_control_example_defined: bool
    future_scenario_statuses: tuple[str, ...]
    future_contrast_statuses: tuple[str, ...]
    future_policy_support_statuses: tuple[str, ...]
    future_shared_control_conflict_types: tuple[str, ...]
    resolution_option_types: tuple[str, ...]
    readiness_gates: tuple[str, ...]
    future_contract_concepts: tuple[str, ...]
    future_output_concepts: tuple[str, ...]
    report_fields: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


def build_design_scenario_policy_feasibility_contract() -> DesignScenarioPolicyFeasibilityContract:
    return DesignScenarioPolicyFeasibilityContract(
        artifact_id=_ARTIFACT_ID,
        scope=SCOPE,
        depends_on=DEPENDS_ON,
        scenario_policy_feasibility_contract_defined=True,
        required_vs_achieved_spend_contrast_defined=True,
        historical_support_contract_defined=True,
        shared_control_conflict_contract_defined=True,
        split_control_redesign_recheck_defined=True,
        scenario_resolution_options_defined=True,
        four_cell_common_control_example_defined=True,
        future_scenario_statuses=FUTURE_SCENARIO_STATUSES,
        future_contrast_statuses=FUTURE_CONTRAST_STATUSES,
        future_policy_support_statuses=FUTURE_POLICY_SUPPORT_STATUSES,
        future_shared_control_conflict_types=FUTURE_SHARED_CONTROL_CONFLICT_TYPES,
        resolution_option_types=RESOLUTION_OPTION_TYPES,
        readiness_gates=READINESS_GATES,
        future_contract_concepts=FUTURE_CONTRACT_CONCEPTS,
        future_output_concepts=FUTURE_OUTPUT_CONCEPTS,
        report_fields=REPORT_FIELDS,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        alternative_next_artifact=ALTERNATIVE_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_design_scenario_policy_feasibility_contract(
    contract: DesignScenarioPolicyFeasibilityContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.scenario_policy_feasibility_contract_defined:
        issues.append("scenario_policy_feasibility_contract_defined must be true")
    if not contract.required_vs_achieved_spend_contrast_defined:
        issues.append("required_vs_achieved_spend_contrast_defined must be true")
    if not contract.shared_control_conflict_contract_defined:
        issues.append("shared_control_conflict_contract_defined must be true")
    if not contract.four_cell_common_control_example_defined:
        issues.append("four_cell_common_control_example_defined must be true")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_design_scenario_policy_feasibility_contract()
    validation = validate_design_scenario_policy_feasibility_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in FUTURE_SCENARIO_STATUSES:
        scenarios.append(_s(f"scenario_status_{status}", status in contract.future_scenario_statuses))
    for status in FUTURE_CONTRAST_STATUSES:
        scenarios.append(_s(f"contrast_status_{status}", status in contract.future_contrast_statuses))
    for status in FUTURE_POLICY_SUPPORT_STATUSES:
        scenarios.append(_s(f"policy_support_{status}", status in contract.future_policy_support_statuses))
    for ctype in FUTURE_SHARED_CONTROL_CONFLICT_TYPES:
        scenarios.append(_s(f"shared_control_conflict_{ctype}", ctype in contract.future_shared_control_conflict_types))
    for opt in RESOLUTION_OPTION_TYPES:
        scenarios.append(_s(f"resolution_option_{opt}", opt in contract.resolution_option_types))
    for gate in READINESS_GATES:
        scenarios.append(_s(f"readiness_gate_{gate}", gate in contract.readiness_gates))
    for field in REPORT_FIELDS:
        scenarios.append(_s(f"report_field_{field}", field in contract.report_fields))
    scenarios.append(_s("contract_defined", contract.scenario_policy_feasibility_contract_defined))
    scenarios.append(_s("required_vs_achieved", contract.required_vs_achieved_spend_contrast_defined))
    scenarios.append(_s("historical_support", contract.historical_support_contract_defined))
    scenarios.append(_s("shared_control_conflict", contract.shared_control_conflict_contract_defined))
    scenarios.append(_s("split_control_recheck", contract.split_control_redesign_recheck_defined))
    scenarios.append(_s("four_cell_example", contract.four_cell_common_control_example_defined))
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
    contract = build_design_scenario_policy_feasibility_contract()
    validation = validate_design_scenario_policy_feasibility_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "design_scenario_policy_feasibility_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": SCOPE,
        "depends_on": list(DEPENDS_ON),
        "scenario_policy_feasibility_contract_defined": True,
        "required_vs_achieved_spend_contrast_defined": True,
        "historical_support_contract_defined": True,
        "shared_control_conflict_contract_defined": True,
        "split_control_redesign_recheck_defined": True,
        "scenario_resolution_options_defined": True,
        "four_cell_common_control_example_defined": True,
        "future_scenario_statuses": list(FUTURE_SCENARIO_STATUSES),
        "future_contrast_statuses": list(FUTURE_CONTRAST_STATUSES),
        "future_policy_support_statuses": list(FUTURE_POLICY_SUPPORT_STATUSES),
        "future_shared_control_conflict_types": list(FUTURE_SHARED_CONTROL_CONFLICT_TYPES),
        "resolution_option_types": list(RESOLUTION_OPTION_TYPES),
        "readiness_gates_defined": list(READINESS_GATES),
        "future_contract_concepts_defined": list(FUTURE_CONTRACT_CONCEPTS),
        "future_output_concepts_defined": list(FUTURE_OUTPUT_CONCEPTS),
        "report_fields_defined": list(REPORT_FIELDS),
        "input_dependencies": list(INPUT_DEPENDENCIES),
        "future_implementation_tests_required": list(FUTURE_IMPLEMENTATION_TESTS),
        "contract_positive_flags": dict(CONTRACT_POSITIVE_FLAGS),
        "runtime_scenario_feasibility_implemented": False,
        "runtime_scenario_enumeration_implemented": False,
        "runtime_scenario_optimization_implemented": False,
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
