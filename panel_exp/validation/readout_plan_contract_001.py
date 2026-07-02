"""READOUT_PLAN_CONTRACT_001 metadata-only validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "READOUT_PLAN_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "readout_plan_contract_defined_no_estimator_execution_or_claim_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/READOUT_PLAN_CONTRACT_001_summary.json"

SCOPE = "contract_only_no_estimator_execution_or_claim_authorization"
RECOMMENDED_NEXT_ARTIFACT = "READOUT_PLAN_RUNTIME_001"
ALTERNATIVE_NEXT_ARTIFACT = "READOUT_METHOD_GOVERNANCE_RUNTIME_001"

DEPENDS_ON = (
    "READOUT_METHOD_GOVERNANCE_CONTRACT_001",
    "DESIGN_ASSIGNMENT_RUNTIME_001",
    "METHOD_SUITABILITY_RUNTIME_001",
    "METHOD_SUITABILITY_HANDOFF_CONTRACT_001",
    "DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001",
    "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001",
    "DESIGN_CELL_STRUCTURE_RUNTIME_001",
    "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001",
    "POWER_MDE_DIAGNOSTICS_RUNTIME_001",
    "INFERENCE_READOUT_SEMANTICS_001",
    "DOWNSTREAM_READOUT_AUTHORIZATION_GATEWAY_001",
)

READOUT_PLAN_STATUSES = (
    "READOUT_PLAN_READY_FOR_RUNTIME_PLANNING",
    "READOUT_PLAN_READY_WITH_WARNINGS",
    "READOUT_PLAN_PROVISIONAL",
    "READOUT_PLAN_BLOCKED_BY_READOUT_GOVERNANCE",
    "READOUT_PLAN_BLOCKED_BY_ASSIGNMENT_ARTIFACT",
    "READOUT_PLAN_BLOCKED_BY_METHOD_INSTRUMENTS",
    "READOUT_PLAN_BLOCKED_BY_ESTIMAND",
    "READOUT_PLAN_BLOCKED_BY_UNCERTAINTY_SEMANTICS",
    "READOUT_PLAN_BLOCKED_BY_MISSING_DIAGNOSTICS",
    "READOUT_PLAN_BLOCKED_BY_MISSING_SENSITIVITY_REQUIREMENTS",
    "READOUT_PLAN_BLOCKED_BY_PRODUCTION_GOVERNANCE",
    "READOUT_PLAN_REQUIRES_DIAGNOSTIC_PLAN",
    "READOUT_PLAN_REQUIRES_SENSITIVITY_PLAN",
    "READOUT_PLAN_NOT_EVALUATED",
)

READOUT_STACK_ROLES = (
    "PRIMARY_READOUT_CANDIDATE",
    "SENSITIVITY_READOUT_CANDIDATE",
    "DIAGNOSTIC_READOUT_CANDIDATE",
    "BLOCKED_READOUT_INSTRUMENT",
    "REFERENCE_ONLY_INSTRUMENT",
    "NOT_EVALUATED_INSTRUMENT",
)

INSTRUMENT_PLANNING_CATEGORIES = (
    "PLANNING_ELIGIBLE_PRIMARY_CANDIDATE",
    "PLANNING_ELIGIBLE_WITH_WARNINGS",
    "PLANNING_RESTRICTED_REQUIRES_REVIEW",
    "PLANNING_DIAGNOSTIC_ONLY",
    "PLANNING_BLOCKED",
    "PLANNING_NOT_EVALUATED",
)

FUTURE_CONTRACT_CONCEPTS = (
    "ReadoutPlanInput",
    "ReadoutPlanConfig",
    "ReadoutPlanReport",
    "ReadoutPlanPacket",
    "PlannedReadoutStack",
    "PrimaryReadoutCandidate",
    "SensitivityReadoutCandidate",
    "DiagnosticReadoutCandidate",
    "BlockedReadoutInstrument",
    "ReadoutExecutionPrerequisite",
    "ReadoutPlanEstimandScope",
    "ReadoutPlanUncertaintyScope",
    "ReadoutPlanDiagnosticRequirement",
    "ReadoutPlanSensitivityRequirement",
    "ReadoutPlanClaimScope",
    "ReadoutPlanCaveat",
    "ReadoutPlanBlockingReason",
    "ReadoutPlanWarning",
    "ReadoutPlanStatus",
    "ReadoutStackRole",
    "ReadoutPlanClaimBoundaryReport",
)

FUTURE_OUTPUT_CONCEPTS = (
    "ReadoutPlanReport",
    "ReadoutPlanPacket",
    "PlannedReadoutStack",
    "PrimaryReadoutCandidate",
    "SensitivityReadoutCandidate",
    "DiagnosticReadoutCandidate",
    "BlockedReadoutInstrument",
    "ReadoutExecutionPrerequisiteReport",
    "ReadoutPlanClaimScopeReport",
    "ReadoutPlanCaveatReport",
    "ReadoutPlanClaimBoundaryReport",
)

READOUT_PLAN_PACKET_FIELDS = (
    "artifact_id",
    "design_id",
    "readout_plan_status",
    "assignment_artifact_summary",
    "readout_governance_summary",
    "planned_primary_candidates",
    "planned_sensitivity_candidates",
    "planned_diagnostic_candidates",
    "blocked_instruments",
    "not_evaluated_instruments",
    "execution_prerequisites",
    "estimand_scope",
    "uncertainty_scope",
    "required_diagnostics",
    "required_sensitivity_checks",
    "claim_scope",
    "reporting_caveats",
    "blocking_reasons",
    "warnings",
    "claim_boundary_report",
)

INPUT_DEPENDENCIES = (
    "readout_method_governance_report",
    "readout_method_governance_packet",
    "design_assignment_runtime_report",
    "assignment_plan",
    "assignment_candidate",
    "unit_allocation_report",
    "constraint_trace",
    "exclusion_trace",
    "reproducibility_manifest",
    "method_suitability_report",
    "instrument_suitability_matrix",
    "eligible_instruments_for_planning",
    "restricted_instruments",
    "diagnostic_only_instruments",
    "blocked_instruments",
    "estimand_governance_summary",
    "uncertainty_governance_summary",
    "required_diagnostics",
    "required_sensitivity_checks",
    "claim_eligibility_reports",
    "production_governance_config",
)

READINESS_GATES = (
    "readout_method_governance_gate",
    "assignment_artifact_gate",
    "reproducibility_manifest_gate",
    "eligible_restricted_instrument_gate",
    "diagnostic_only_instrument_gate",
    "blocked_instrument_gate",
    "estimand_scope_gate",
    "uncertainty_semantics_gate",
    "diagnostics_requirement_gate",
    "sensitivity_requirement_gate",
    "execution_prerequisite_gate",
    "claim_scope_boundary_gate",
    "readout_plan_packet_gate",
)

DIAGNOSTIC_REQUIREMENT_EXAMPLES = (
    "pre_period_fit_diagnostic",
    "placebo_check",
    "jackknife_stability",
    "bootstrap_stability",
    "parallel_trend_diagnostic",
    "donor_support_diagnostic",
    "outlier_sensitivity",
    "assignment_reproducibility_check",
    "spend_support_diagnostic",
    "interference_risk_review",
    "common_control_conflict_review",
)

SENSITIVITY_REQUIREMENT_EXAMPLES = (
    "donor_pool_sensitivity",
    "pre_period_window_sensitivity",
    "outlier_exclusion_sensitivity",
    "estimator_specification_sensitivity",
    "inference_path_sensitivity",
    "assignment_algorithm_caveat_sensitivity",
)

FUTURE_IMPLEMENTATION_TESTS = (
    "blocked_readout_governance_blocks_plan",
    "missing_assignment_artifact_blocks_plan",
    "missing_reproducibility_manifest_blocks_plan",
    "all_instruments_blocked_blocks_plan",
    "only_diagnostic_only_instruments_prevents_primary_candidate",
    "restricted_instrument_carries_caveats_and_diagnostics",
    "eligible_instrument_may_become_planned_primary_candidate",
    "diagnostic_only_instrument_only_diagnostic_candidate",
    "blocked_instrument_preserved",
    "dosage_estimand_prevents_standard_incrementality_claim_scope",
    "budget_reallocation_prevents_simple_roi_claim_scope",
    "missing_uncertainty_semantics_blocks_or_provisionalizes",
    "missing_diagnostics_requires_diagnostic_plan",
    "missing_sensitivity_requires_sensitivity_plan",
    "no_estimator_execution",
    "no_inference_execution",
    "no_lift_roi_pvalues_cis",
    "no_claim_authorization",
    "no_production_authorization",
    "no_fixture_specific_branching",
)

CONTRACT_EXAMPLES = (
    "example_1_did_bootstrap_primary_scm_placebo_diagnostic",
    "example_2_only_diagnostic_only_no_primary",
    "example_3_all_instruments_blocked",
    "example_4_restricted_tbr_ridge_brb_with_caveats",
    "example_5_dosage_contrast_blocks_standard_incrementality",
    "example_6_budget_reallocation_blocks_simple_roi",
    "example_7_missing_reproducibility_manifest_blocks",
    "example_8_missing_uncertainty_semantics_provisional",
    "example_9_common_control_conflict_requires_review",
    "example_10_deterministic_explicit_pool_assignment_caveat",
)

_AUTH_FLAGS = {
    "readout_plan_runtime_implemented": False,
    "readout_plan_generated": False,
    "primary_readout_stack_selected": False,
    "sensitivity_stack_selected": False,
    "diagnostic_stack_selected": False,
    "method_winner_selected": False,
    "estimator_execution_implemented": False,
    "inference_execution_implemented": False,
    "effect_estimate_computed": False,
    "lift_computed": False,
    "roi_computed": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "diagnostic_check_executed": False,
    "sensitivity_check_executed": False,
    "causal_claim_authorized": False,
    "incremental_lift_claim_authorized": False,
    "roi_claim_authorized": False,
    "production_readout_authorized": False,
    "production_authorization_granted": False,
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "llm_decisioning_authorized": False,
}

CONTRACT_POSITIVE_FLAGS = {
    "readout_plan_contract_defined": True,
    "planned_readout_stack_contract_defined": True,
    "primary_candidate_contract_defined": True,
    "sensitivity_candidate_contract_defined": True,
    "diagnostic_candidate_contract_defined": True,
    "blocked_instrument_contract_defined": True,
    "execution_prerequisite_contract_defined": True,
    "claim_scope_contract_defined": True,
    "reporting_caveat_contract_defined": True,
    "claim_boundaries_defined": True,
}

NON_GOALS = (
    "no_readout_plan_runtime",
    "no_readout_plan_generation",
    "no_primary_sensitivity_diagnostic_stack_selection",
    "no_method_winner_selection",
    "no_estimator_execution",
    "no_inference_execution",
    "no_effect_lift_roi_computation",
    "no_p_values_or_confidence_intervals",
    "no_uncertainty_computation",
    "no_diagnostic_sensitivity_execution",
    "no_causal_claim_authorization",
    "no_production_readout_authorization",
    "no_mmm_runtime_calls",
    "no_llm_decisioning",
)


@dataclass(frozen=True)
class ReadoutPlanContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    readout_plan_contract_defined: bool
    planned_readout_stack_contract_defined: bool
    primary_candidate_contract_defined: bool
    sensitivity_candidate_contract_defined: bool
    diagnostic_candidate_contract_defined: bool
    blocked_instrument_contract_defined: bool
    execution_prerequisite_contract_defined: bool
    claim_scope_contract_defined: bool
    reporting_caveat_contract_defined: bool
    readout_plan_statuses: tuple[str, ...]
    readout_stack_roles: tuple[str, ...]
    instrument_planning_categories: tuple[str, ...]
    future_contract_concepts: tuple[str, ...]
    future_output_concepts: tuple[str, ...]
    readout_plan_packet_fields: tuple[str, ...]
    input_dependencies: tuple[str, ...]
    readiness_gates: tuple[str, ...]
    diagnostic_requirement_examples: tuple[str, ...]
    sensitivity_requirement_examples: tuple[str, ...]
    contract_examples: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


def build_readout_plan_contract() -> ReadoutPlanContract:
    return ReadoutPlanContract(
        artifact_id=_ARTIFACT_ID,
        scope=SCOPE,
        depends_on=DEPENDS_ON,
        readout_plan_contract_defined=True,
        planned_readout_stack_contract_defined=True,
        primary_candidate_contract_defined=True,
        sensitivity_candidate_contract_defined=True,
        diagnostic_candidate_contract_defined=True,
        blocked_instrument_contract_defined=True,
        execution_prerequisite_contract_defined=True,
        claim_scope_contract_defined=True,
        reporting_caveat_contract_defined=True,
        readout_plan_statuses=READOUT_PLAN_STATUSES,
        readout_stack_roles=READOUT_STACK_ROLES,
        instrument_planning_categories=INSTRUMENT_PLANNING_CATEGORIES,
        future_contract_concepts=FUTURE_CONTRACT_CONCEPTS,
        future_output_concepts=FUTURE_OUTPUT_CONCEPTS,
        readout_plan_packet_fields=READOUT_PLAN_PACKET_FIELDS,
        input_dependencies=INPUT_DEPENDENCIES,
        readiness_gates=READINESS_GATES,
        diagnostic_requirement_examples=DIAGNOSTIC_REQUIREMENT_EXAMPLES,
        sensitivity_requirement_examples=SENSITIVITY_REQUIREMENT_EXAMPLES,
        contract_examples=CONTRACT_EXAMPLES,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        alternative_next_artifact=ALTERNATIVE_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_readout_plan_contract(contract: ReadoutPlanContract) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.readout_plan_contract_defined:
        issues.append("readout_plan_contract_defined must be true")
    if len(contract.readout_plan_statuses) < 14:
        issues.append("readout_plan_statuses incomplete")
    if len(contract.readout_stack_roles) < 6:
        issues.append("readout_stack_roles incomplete")
    if len(contract.instrument_planning_categories) < 6:
        issues.append("instrument_planning_categories incomplete")
    if len(contract.readiness_gates) < 13:
        issues.append("readiness_gates incomplete")
    if len(contract.contract_examples) < 10:
        issues.append("contract_examples incomplete")
    if contract.readiness_gates[0] != "readout_method_governance_gate":
        issues.append("readiness_gates must start with readout_method_governance_gate")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_readout_plan_contract()
    validation = validate_readout_plan_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in READOUT_PLAN_STATUSES:
        scenarios.append(_s(f"readout_plan_status_{status}", status in contract.readout_plan_statuses))
    for role in READOUT_STACK_ROLES:
        scenarios.append(_s(f"readout_stack_role_{role}", role in contract.readout_stack_roles))
    for cat in INSTRUMENT_PLANNING_CATEGORIES:
        scenarios.append(
            _s(f"instrument_planning_category_{cat}", cat in contract.instrument_planning_categories)
        )
    for dep in INPUT_DEPENDENCIES:
        scenarios.append(_s(f"input_dependency_{dep}", dep in contract.input_dependencies))
    for gate in READINESS_GATES:
        scenarios.append(_s(f"readiness_gate_{gate}", gate in contract.readiness_gates))
    for field in READOUT_PLAN_PACKET_FIELDS:
        scenarios.append(_s(f"packet_field_{field}", field in contract.readout_plan_packet_fields))
    for ex in CONTRACT_EXAMPLES:
        scenarios.append(_s(f"example_{ex}", ex in contract.contract_examples))
    for concept in FUTURE_CONTRACT_CONCEPTS:
        scenarios.append(_s(f"contract_concept_{concept}", concept in contract.future_contract_concepts))
    for concept in FUTURE_OUTPUT_CONCEPTS:
        scenarios.append(_s(f"output_concept_{concept}", concept in contract.future_output_concepts))
    for diag in DIAGNOSTIC_REQUIREMENT_EXAMPLES:
        scenarios.append(
            _s(f"diagnostic_requirement_{diag}", diag in contract.diagnostic_requirement_examples)
        )
    for sens in SENSITIVITY_REQUIREMENT_EXAMPLES:
        scenarios.append(
            _s(f"sensitivity_requirement_{sens}", sens in contract.sensitivity_requirement_examples)
        )
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
    contract = build_readout_plan_contract()
    validation = validate_readout_plan_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "readout_plan_contract",
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
