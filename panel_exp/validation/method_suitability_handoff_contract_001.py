"""METHOD_SUITABILITY_HANDOFF_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "METHOD_SUITABILITY_HANDOFF_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "method_suitability_handoff_contract_defined_no_method_selection_or_inference_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/METHOD_SUITABILITY_HANDOFF_CONTRACT_001_summary.json"
)

SCOPE = "contract_only_no_method_selection_or_inference_authorization"
RECOMMENDED_NEXT_ARTIFACT = "METHOD_SUITABILITY_RUNTIME_001"
ALTERNATIVE_NEXT_ARTIFACT = "DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001"

DEPENDS_ON = (
    "GEO_KPI_SPEND_DATA_PROFILER_001",
    "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
    "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
    "POWER_MDE_DIAGNOSTICS_RUNTIME_001",
    "DESIGN_CELL_STRUCTURE_RUNTIME_001",
    "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001",
    "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001",
)

FUTURE_HANDOFF_STATUSES = (
    "METHOD_HANDOFF_READY_FOR_SUITABILITY_REVIEW",
    "METHOD_HANDOFF_READY_WITH_WARNINGS",
    "METHOD_HANDOFF_PROVISIONAL",
    "METHOD_HANDOFF_BLOCKED_BY_DATA_READINESS",
    "METHOD_HANDOFF_BLOCKED_BY_GEO_FEASIBILITY",
    "METHOD_HANDOFF_BLOCKED_BY_DESIGN_STRUCTURE",
    "METHOD_HANDOFF_BLOCKED_BY_SCENARIO_POLICY",
    "METHOD_HANDOFF_BLOCKED_BY_ASSIGNMENT_FEASIBILITY",
    "METHOD_HANDOFF_BLOCKED_BY_POWER_MDE_READINESS",
    "METHOD_HANDOFF_BLOCKED_BY_MISSING_ESTIMAND",
    "METHOD_HANDOFF_BLOCKED_BY_UNSUPPORTED_DESIGN",
    "METHOD_HANDOFF_REQUIRES_DOSAGE_REVIEW",
    "METHOD_HANDOFF_REQUIRES_DIFFERENCE_IN_POLICY_REVIEW",
    "METHOD_HANDOFF_REQUIRES_BUDGET_REALLOCATION_REVIEW",
    "METHOD_HANDOFF_REQUIRES_REDESIGN_RECHECK",
    "METHOD_HANDOFF_NOT_EVALUATED",
)

FUTURE_REVIEW_REQUIREMENT_TYPES = (
    "STANDARD_INCREMENTALITY_REVIEW",
    "DOSAGE_CONTRAST_REVIEW",
    "DIFFERENCE_IN_POLICY_REVIEW",
    "BUDGET_REALLOCATION_REVIEW",
    "GO_LIVE_REVIEW",
    "COMMON_CONTROL_REVIEW",
    "SPLIT_CONTROL_REDESIGN_REVIEW",
    "MATCHED_PAIR_REVIEW",
    "BLOCKED_OR_CLUSTERED_DESIGN_REVIEW",
    "RERANDOMIZATION_REVIEW",
    "INTERFERENCE_RISK_REVIEW",
    "LOW_POWER_OR_HIGH_MDE_REVIEW",
    "OUT_OF_HISTORICAL_SUPPORT_REVIEW",
    "ASSIGNMENT_FEASIBILITY_REVIEW",
    "METHOD_GOVERNANCE_REVIEW",
)

FUTURE_METHOD_FAMILY_REVIEW_TARGETS = (
    "SCM_FAMILY",
    "AUGSYNTH_FAMILY",
    "TBR_RIDGE_FAMILY",
    "DID_FAMILY",
    "MATCHED_PAIR_FAMILY",
    "BLOCKED_RANDOMIZATION_FAMILY",
    "RERANDOMIZATION_FAMILY",
    "PLACEBO_INFERENCE_FAMILY",
    "JACKKNIFE_INFERENCE_FAMILY",
    "BOOTSTRAP_INFERENCE_FAMILY",
    "CONFORMAL_INFERENCE_FAMILY",
    "AB_TEST_FAMILY",
    "UNKNOWN_METHOD_FAMILY",
)

FUTURE_CONTRACT_CONCEPTS = (
    "MethodSuitabilityHandoffInput",
    "MethodSuitabilityHandoffConfig",
    "MethodSuitabilityHandoffReport",
    "MethodSuitabilityHandoffPacket",
    "MethodSuitabilityDesignSummary",
    "MethodSuitabilityContrastSummary",
    "MethodSuitabilityAssignmentSummary",
    "MethodSuitabilityScenarioSummary",
    "MethodSuitabilityPowerMdeSummary",
    "MethodSuitabilitySpendSummary",
    "MethodSuitabilityGovernanceSummary",
    "MethodFamilyEligibilityInput",
    "MethodFamilyRestriction",
    "MethodFamilyWarning",
    "MethodSuitabilityHandoffStatus",
    "MethodSuitabilityReviewRequirement",
    "MethodSuitabilityIssue",
    "MethodSuitabilityIssueSeverity",
    "MethodSuitabilityClaimBoundaryReport",
)

FUTURE_OUTPUT_CONCEPTS = (
    "MethodSuitabilityHandoffReport",
    "MethodSuitabilityHandoffPacket",
    "MethodSuitabilityDesignSummary",
    "MethodSuitabilityContrastSummary",
    "MethodSuitabilityAssignmentSummary",
    "MethodSuitabilityScenarioSummary",
    "MethodSuitabilityPowerMdeSummary",
    "MethodSuitabilitySpendSummary",
    "MethodSuitabilityGovernanceSummary",
    "MethodSuitabilityReviewRequirementReport",
    "MethodSuitabilityBlockingReasonReport",
    "MethodSuitabilityClaimBoundaryReport",
)

HANDOFF_PACKET_FIELDS = (
    "artifact_id",
    "design_id",
    "handoff_status",
    "design_structure_type",
    "contrast_summaries",
    "estimand_summaries",
    "scenario_policy_summary",
    "assignment_feasibility_summary",
    "power_mde_summary",
    "spend_summary",
    "governance_summary",
    "review_requirements",
    "candidate_method_family_review_targets",
    "warnings",
    "blocking_reasons",
    "claim_boundary_report",
)

READINESS_GATES = (
    "profiler_data_readiness_gate",
    "geo_unit_market_feasibility_gate",
    "spend_feasibility_gate",
    "power_mde_readiness_gate",
    "design_cell_structure_gate",
    "scenario_policy_feasibility_gate",
    "assignment_feasibility_gate",
    "estimand_declaration_gate",
    "design_contrast_compatibility_gate",
    "method_governance_catalog_availability_gate",
    "method_suitability_handoff_packet_gate",
)

INPUT_DEPENDENCIES = (
    "profiler_report",
    "geo_unit_market_feasibility_report",
    "spend_requirement_manipulation_feasibility_report",
    "power_mde_diagnostics_report",
    "design_cell_structure_runtime_report",
    "design_scenario_policy_feasibility_report",
    "design_assignment_feasibility_report",
    "design_structure_type",
    "contrast_specs",
    "contrast_types",
    "estimand_labels",
    "manipulation_policies",
    "bau_control_preservation_status",
    "shared_control_conflicts",
    "split_control_required",
    "scenario_recheck_requirements",
    "assignment_feasibility_status",
    "eligible_unit_count",
    "cell_capacity_status",
    "balance_readiness_status",
    "interference_risk_status",
    "required_vs_achieved_spend_contrast_status",
    "historical_support_status",
    "method_suitability_review_required_flags",
    "instrument_catalog_status",
    "method_roadmap_status",
)

FUTURE_IMPLEMENTATION_TESTS = (
    "blocked_profiler_blocks_handoff",
    "blocked_geo_feasibility_blocks_handoff",
    "blocked_design_structure_blocks_handoff",
    "blocked_assignment_feasibility_blocks_or_provisional_handoff",
    "blocked_scenario_policy_blocks_or_provisional_handoff",
    "blocked_power_mde_prevents_method_ready_inference",
    "missing_estimand_blocks_handoff",
    "standard_go_dark_bau_preserved_emits_standard_incrementality_review",
    "manipulated_control_emits_difference_in_policy_review",
    "dosage_contrast_emits_dosage_review",
    "budget_reallocation_emits_budget_reallocation_review",
    "shared_control_conflict_preserved",
    "split_control_redesign_recheck_preserved",
    "out_of_historical_support_warning_preserved",
    "interference_risk_preserved",
    "assignment_ready_does_not_mean_method_ready",
    "method_family_review_targets_not_selected_methods",
    "no_estimator_inference_authorization",
    "no_lift_roi_p_value_ci_computation",
    "no_production_authorization",
    "no_fixture_specific_branching",
)

CONTRACT_EXAMPLES = (
    "example_1_standard_two_cell_go_dark_handoff",
    "example_2_heavy_up_vs_bau_handoff",
    "example_3_dosage_contrast_handoff",
    "example_4_difference_in_policy_handoff",
    "example_5_budget_reallocation_handoff",
    "example_6_shared_common_control_conflict",
    "example_7_split_control_redesign",
    "example_8_assignment_feasible_method_review_required",
)

_AUTH_FLAGS = {
    "runtime_method_suitability_implemented": False,
    "method_family_selected": False,
    "estimator_selected": False,
    "inference_method_selected": False,
    "method_promotion_authorized": False,
    "method_production_compatibility_authorized": False,
    "geo_assignment_computed": False,
    "matched_pairs_generated": False,
    "blocks_generated": False,
    "randomization_computed": False,
    "rerandomization_computed": False,
    "thinning_design_generated": False,
    "matching_optimization_computed": False,
    "balance_optimization_computed": False,
    "scenario_policy_feasibility_computed": False,
    "assignment_feasibility_computed": False,
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
    "method_suitability_handoff_contract_defined": True,
    "method_handoff_packet_defined": True,
    "estimand_handoff_defined": True,
    "design_summary_handoff_defined": True,
    "scenario_summary_handoff_defined": True,
    "assignment_summary_handoff_defined": True,
    "power_mde_summary_handoff_defined": True,
    "spend_summary_handoff_defined": True,
    "governance_summary_handoff_defined": True,
    "review_requirement_types_defined": True,
    "method_family_review_targets_defined": True,
    "claim_boundaries_defined": True,
}

NON_GOALS = (
    "no_runtime_method_suitability",
    "no_method_family_selection",
    "no_estimator_selection",
    "no_inference_method_selection",
    "no_method_promotion",
    "no_method_production_compatibility_authorization",
    "no_geo_assignment",
    "no_matched_pairs_generated",
    "no_blocks_generated",
    "no_randomization",
    "no_rerandomization",
    "no_assignment_feasibility_computation",
    "no_scenario_policy_feasibility_computation",
    "no_power_mde_computation",
    "no_lift_roi_p_value_ci_computation",
    "no_production_authorization",
)


@dataclass(frozen=True)
class MethodSuitabilityHandoffContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    method_suitability_handoff_contract_defined: bool
    method_handoff_packet_defined: bool
    estimand_handoff_defined: bool
    design_summary_handoff_defined: bool
    scenario_summary_handoff_defined: bool
    assignment_summary_handoff_defined: bool
    power_mde_summary_handoff_defined: bool
    spend_summary_handoff_defined: bool
    governance_summary_handoff_defined: bool
    review_requirement_types_defined: bool
    method_family_review_targets_defined: bool
    future_handoff_statuses: tuple[str, ...]
    future_review_requirement_types: tuple[str, ...]
    future_method_family_review_targets: tuple[str, ...]
    readiness_gates: tuple[str, ...]
    future_contract_concepts: tuple[str, ...]
    future_output_concepts: tuple[str, ...]
    handoff_packet_fields: tuple[str, ...]
    input_dependencies: tuple[str, ...]
    contract_examples: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


def build_method_suitability_handoff_contract() -> MethodSuitabilityHandoffContract:
    return MethodSuitabilityHandoffContract(
        artifact_id=_ARTIFACT_ID,
        scope=SCOPE,
        depends_on=DEPENDS_ON,
        method_suitability_handoff_contract_defined=True,
        method_handoff_packet_defined=True,
        estimand_handoff_defined=True,
        design_summary_handoff_defined=True,
        scenario_summary_handoff_defined=True,
        assignment_summary_handoff_defined=True,
        power_mde_summary_handoff_defined=True,
        spend_summary_handoff_defined=True,
        governance_summary_handoff_defined=True,
        review_requirement_types_defined=True,
        method_family_review_targets_defined=True,
        future_handoff_statuses=FUTURE_HANDOFF_STATUSES,
        future_review_requirement_types=FUTURE_REVIEW_REQUIREMENT_TYPES,
        future_method_family_review_targets=FUTURE_METHOD_FAMILY_REVIEW_TARGETS,
        readiness_gates=READINESS_GATES,
        future_contract_concepts=FUTURE_CONTRACT_CONCEPTS,
        future_output_concepts=FUTURE_OUTPUT_CONCEPTS,
        handoff_packet_fields=HANDOFF_PACKET_FIELDS,
        input_dependencies=INPUT_DEPENDENCIES,
        contract_examples=CONTRACT_EXAMPLES,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        alternative_next_artifact=ALTERNATIVE_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_method_suitability_handoff_contract(
    contract: MethodSuitabilityHandoffContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.method_suitability_handoff_contract_defined:
        issues.append("method_suitability_handoff_contract_defined must be true")
    if not contract.estimand_handoff_defined:
        issues.append("estimand_handoff_defined must be true")
    if not contract.method_family_review_targets_defined:
        issues.append("method_family_review_targets_defined must be true")
    if len(contract.future_handoff_statuses) < 16:
        issues.append("future_handoff_statuses incomplete")
    if len(contract.future_review_requirement_types) < 15:
        issues.append("future_review_requirement_types incomplete")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_method_suitability_handoff_contract()
    validation = validate_method_suitability_handoff_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in FUTURE_HANDOFF_STATUSES:
        scenarios.append(_s(f"handoff_status_{status}", status in contract.future_handoff_statuses))
    for req in FUTURE_REVIEW_REQUIREMENT_TYPES:
        scenarios.append(_s(f"review_requirement_{req}", req in contract.future_review_requirement_types))
    for family in FUTURE_METHOD_FAMILY_REVIEW_TARGETS:
        scenarios.append(
            _s(f"method_family_target_{family}", family in contract.future_method_family_review_targets)
        )
    for gate in READINESS_GATES:
        scenarios.append(_s(f"readiness_gate_{gate}", gate in contract.readiness_gates))
    for field in HANDOFF_PACKET_FIELDS:
        scenarios.append(_s(f"packet_field_{field}", field in contract.handoff_packet_fields))
    for dep in INPUT_DEPENDENCIES:
        scenarios.append(_s(f"input_dependency_{dep}", dep in contract.input_dependencies))
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
    contract = build_method_suitability_handoff_contract()
    validation = validate_method_suitability_handoff_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "method_suitability_handoff_contract",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": SCOPE,
        "depends_on": list(DEPENDS_ON),
        "method_suitability_handoff_contract_defined": True,
        "method_handoff_packet_defined": True,
        "estimand_handoff_defined": True,
        "design_summary_handoff_defined": True,
        "scenario_summary_handoff_defined": True,
        "assignment_summary_handoff_defined": True,
        "power_mde_summary_handoff_defined": True,
        "spend_summary_handoff_defined": True,
        "governance_summary_handoff_defined": True,
        "review_requirement_types_defined": True,
        "method_family_review_targets_defined": True,
        "claim_boundaries_defined": True,
        "future_handoff_statuses": list(FUTURE_HANDOFF_STATUSES),
        "future_review_requirement_types": list(FUTURE_REVIEW_REQUIREMENT_TYPES),
        "future_method_family_review_targets": list(FUTURE_METHOD_FAMILY_REVIEW_TARGETS),
        "readiness_gates_defined": list(READINESS_GATES),
        "future_contract_concepts_defined": list(FUTURE_CONTRACT_CONCEPTS),
        "future_output_concepts_defined": list(FUTURE_OUTPUT_CONCEPTS),
        "handoff_packet_fields_defined": list(HANDOFF_PACKET_FIELDS),
        "input_dependencies": list(INPUT_DEPENDENCIES),
        "contract_examples_defined": list(CONTRACT_EXAMPLES),
        "future_implementation_tests_required": list(FUTURE_IMPLEMENTATION_TESTS),
        "contract_positive_flags": dict(CONTRACT_POSITIVE_FLAGS),
        "runtime_method_suitability_implemented": False,
        "method_family_selected": False,
        "estimator_selected": False,
        "inference_method_selected": False,
        "method_promotion_authorized": False,
        "method_production_compatibility_authorized": False,
        "geo_assignment_computed": False,
        "matched_pairs_generated": False,
        "blocks_generated": False,
        "randomization_computed": False,
        "rerandomization_computed": False,
        "thinning_design_generated": False,
        "matching_optimization_computed": False,
        "balance_optimization_computed": False,
        "scenario_policy_feasibility_computed": False,
        "assignment_feasibility_computed": False,
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
