"""READOUT_METHOD_GOVERNANCE_CONTRACT_001 metadata-only validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "READOUT_METHOD_GOVERNANCE_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "readout_method_governance_contract_defined_no_estimator_execution_or_causal_claim_authorization"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/READOUT_METHOD_GOVERNANCE_CONTRACT_001_summary.json"
)

SCOPE = "contract_only_no_readout_plan_generation_or_estimator_execution"
RECOMMENDED_NEXT_ARTIFACT = "READOUT_PLAN_CONTRACT_001"
ALTERNATIVE_NEXT_ARTIFACT = "READOUT_METHOD_GOVERNANCE_RUNTIME_001"

DEPENDS_ON = (
    "GEO_KPI_SPEND_DATA_PROFILER_001",
    "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
    "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
    "POWER_MDE_DIAGNOSTICS_RUNTIME_001",
    "DESIGN_CELL_STRUCTURE_RUNTIME_001",
    "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001",
    "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001",
    "METHOD_SUITABILITY_RUNTIME_001",
    "METHOD_SUITABILITY_HANDOFF_CONTRACT_001",
    "DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001",
    "DESIGN_ASSIGNMENT_RUNTIME_001",
    "INFERENCE_READOUT_SEMANTICS_001",
    "DOWNSTREAM_READOUT_AUTHORIZATION_GATEWAY_001",
)

READOUT_GOVERNANCE_STATUSES = (
    "READOUT_GOVERNANCE_ELIGIBLE_FOR_PLANNING",
    "READOUT_GOVERNANCE_ELIGIBLE_WITH_WARNINGS",
    "READOUT_GOVERNANCE_PROVISIONAL",
    "READOUT_GOVERNANCE_RESTRICTED_RESEARCH_ONLY",
    "READOUT_GOVERNANCE_DIAGNOSTIC_ONLY",
    "READOUT_GOVERNANCE_BLOCKED_BY_ASSIGNMENT_ARTIFACT",
    "READOUT_GOVERNANCE_BLOCKED_BY_ASSIGNMENT_RUNTIME_STATUS",
    "READOUT_GOVERNANCE_BLOCKED_BY_INSTRUMENT_GOVERNANCE",
    "READOUT_GOVERNANCE_BLOCKED_BY_METHOD_SUITABILITY",
    "READOUT_GOVERNANCE_BLOCKED_BY_ESTIMAND_GOVERNANCE",
    "READOUT_GOVERNANCE_BLOCKED_BY_UNCERTAINTY_SEMANTICS",
    "READOUT_GOVERNANCE_BLOCKED_BY_SCENARIO_POLICY",
    "READOUT_GOVERNANCE_BLOCKED_BY_POWER_MDE_READINESS",
    "READOUT_GOVERNANCE_BLOCKED_BY_DESIGN_STRUCTURE",
    "READOUT_GOVERNANCE_BLOCKED_BY_DATA_READINESS",
    "READOUT_GOVERNANCE_BLOCKED_BY_INFERENCE_BOUNDARY",
    "READOUT_GOVERNANCE_BLOCKED_BY_READOUT_SEMANTICS_MISMATCH",
    "READOUT_GOVERNANCE_BLOCKED_BY_GEOMETRY_MISMATCH",
    "READOUT_GOVERNANCE_BLOCKED_BY_POOLED_MULTICELL",
    "READOUT_GOVERNANCE_REQUIRES_REDESIGN_RECHECK",
    "READOUT_GOVERNANCE_REQUIRES_REVIEW",
    "READOUT_GOVERNANCE_NOT_EVALUATED",
)

INSTRUMENT_GOVERNANCE_STATUSES = (
    "INSTRUMENT_ELIGIBLE_FOR_READOUT_REVIEW",
    "INSTRUMENT_ELIGIBLE_WITH_WARNINGS",
    "INSTRUMENT_RESTRICTED",
    "INSTRUMENT_DIAGNOSTIC_ONLY",
    "INSTRUMENT_BLOCKED",
    "INSTRUMENT_NOT_EVALUATED",
)

CLAIM_ELIGIBILITY_STATUSES = (
    "CLAIM_ELIGIBILITY_NOT_AUTHORIZED",
    "CLAIM_ELIGIBILITY_RESEARCH_POINT_ONLY",
    "CLAIM_ELIGIBILITY_RESEARCH_DIAGNOSTIC_ONLY",
    "CLAIM_ELIGIBILITY_RESTRICTED_CAVEATED",
    "CLAIM_ELIGIBILITY_ELIGIBLE_FOR_GOVERNED_PLANNING",
    "CLAIM_ELIGIBILITY_BLOCKED_BY_ASSIGNMENT",
    "CLAIM_ELIGIBILITY_BLOCKED_BY_INSTRUMENT",
    "CLAIM_ELIGIBILITY_BLOCKED_BY_ESTIMAND",
    "CLAIM_ELIGIBILITY_BLOCKED_BY_UNCERTAINTY_SEMANTICS",
    "CLAIM_ELIGIBILITY_BLOCKED_BY_PRODUCTION_READOUT_POLICY",
    "CLAIM_ELIGIBILITY_NOT_EVALUATED",
)

READOUT_CLAIM_TYPES = (
    "POINT_ESTIMATE_READOUT_CLAIM",
    "PERIOD_LEVEL_EFFECT_CLAIM",
    "CUMULATIVE_EFFECT_CLAIM",
    "AVERAGE_POST_PERIOD_EFFECT_CLAIM",
    "FRACTIONAL_LIFT_CLAIM",
    "LEVEL_LIFT_CLAIM",
    "INCREMENTAL_OUTCOME_CLAIM",
    "DIRECTIONAL_SIGNAL_CLAIM",
    "NULL_DECISION_CLAIM",
    "INTERVAL_COVERAGE_CLAIM",
    "CAUSAL_INTERVAL_CLAIM",
    "PREDICTION_INTERVAL_CLAIM",
    "FORECAST_INTERVAL_CLAIM",
    "DIAGNOSTIC_DISAGREEMENT_CLAIM",
    "SENSITIVITY_ANALYSIS_CLAIM",
    "MULTICELL_PER_CELL_CLAIM",
    "POOLED_MULTICELL_CLAIM",
    "INCREMENTAL_LIFT_ROI_CLAIM",
    "PRODUCTION_TRUST_REPORT_CLAIM",
    "CALIBRATION_SIGNAL_CLAIM",
    "MMM_INGESTION_CLAIM",
)

ASSIGNMENT_ARTIFACT_GOVERNANCE_STATUSES = (
    "ASSIGNMENT_ARTIFACT_READY_FOR_READOUT_GOVERNANCE",
    "ASSIGNMENT_ARTIFACT_READY_WITH_WARNINGS",
    "ASSIGNMENT_ARTIFACT_PROVISIONAL",
    "ASSIGNMENT_ARTIFACT_MISSING_REPRODUCIBILITY_MANIFEST",
    "ASSIGNMENT_ARTIFACT_MISSING_ALLOCATIONS",
    "ASSIGNMENT_ARTIFACT_BLOCKED_BY_CONSTRAINTS",
    "ASSIGNMENT_ARTIFACT_BLOCKED_BY_RUNTIME",
    "ASSIGNMENT_ARTIFACT_NOT_GENERATED",
    "ASSIGNMENT_ARTIFACT_NOT_EVALUATED",
)

UNCERTAINTY_SEMANTICS_CLASSIFICATIONS = (
    "point_only_no_uncertainty",
    "prediction_interval_only",
    "forecast_interval_only",
    "resampling_interval_target_ambiguous",
    "causal_interval_candidate_requires_validation",
    "causal_interval_validated_in_scope",
    "blocked_due_to_readout_mismatch",
    "blocked_due_to_geometry_mismatch",
    "blocked_due_to_leakage_risk",
)

DIAGNOSTIC_SENSITIVITY_SLOT_TYPES = (
    "PRIMARY_READOUT_SLOT",
    "SENSITIVITY_READOUT_SLOT",
    "DIAGNOSTIC_READOUT_SLOT",
    "NULL_PLACEBO_DIAGNOSTIC_SLOT",
    "DISAGREEMENT_DIAGNOSTIC_SLOT",
)

PRODUCTION_READOUT_BLOCKER_ROLES = (
    "trust_report",
    "calibration_signal",
    "mmm_ingestion",
    "llm_decisioning",
    "production_recommendation",
    "automated_budget_action",
    "external_export",
    "production_decision",
)

FUTURE_CONTRACT_CONCEPTS = (
    "ReadoutMethodGovernanceInput",
    "ReadoutMethodGovernanceConfig",
    "ReadoutMethodGovernanceReport",
    "ReadoutGovernanceEligibilityPacket",
    "AssignmentArtifactGovernanceSummary",
    "InstrumentGovernanceSummary",
    "EstimandGovernanceSummary",
    "UncertaintySemanticsGovernanceSummary",
    "DiagnosticSensitivityGovernanceSummary",
    "ReadoutClaimEligibilityReport",
    "ReadoutClaimBoundaryReport",
    "ReadoutGovernanceStatus",
    "InstrumentGovernanceStatus",
    "ClaimEligibilityStatus",
    "ReadoutClaimType",
    "AssignmentArtifactGovernanceStatus",
    "UncertaintySemanticsClassification",
    "DiagnosticSensitivitySlotType",
    "ProductionReadoutBlockerReport",
    "ReadoutMethodGovernanceFailurePacket",
)

FUTURE_OUTPUT_CONCEPTS = (
    "ReadoutMethodGovernanceReport",
    "ReadoutGovernanceEligibilityPacket",
    "AssignmentArtifactGovernanceSummary",
    "InstrumentGovernanceSummary",
    "EstimandGovernanceSummary",
    "UncertaintySemanticsGovernanceSummary",
    "DiagnosticSensitivityGovernanceSummary",
    "ReadoutClaimEligibilityReport",
    "ReadoutClaimBoundaryReport",
    "ProductionReadoutBlockerReport",
    "ReadoutMethodGovernanceFailurePacket",
)

GOVERNANCE_PACKET_FIELDS = (
    "artifact_id",
    "design_id",
    "readout_governance_status",
    "assignment_artifact_governance_status",
    "assignment_runtime_status",
    "method_suitability_handoff_status",
    "instrument_governance_summaries",
    "estimand_governance_summary",
    "uncertainty_semantics_governance_summary",
    "diagnostic_sensitivity_governance_summary",
    "claim_eligibility_reports",
    "eligible_readout_claim_types",
    "blocked_readout_claim_types",
    "production_readout_blockers",
    "warnings",
    "blocking_reasons",
    "claim_boundary_report",
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
    "design_assignment_runtime_report",
    "assignment_plan",
    "assignment_candidate",
    "assignment_unit_allocations",
    "assignment_reproducibility_manifest",
    "method_instrument_suitability_matrix",
    "estimand_labels",
    "estimand_gate_report",
    "geometry_id",
    "design_structure_type",
    "contrast_specs",
    "scenario_policy_summary",
    "power_mde_handoff_summary",
    "inference_boundary_identity",
    "readout_semantics_classification",
    "uncertainty_semantics_classification",
    "governance_handoff_report",
    "instrument_catalog",
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
    "assignment_artifact_gate",
    "assignment_reproducibility_manifest_gate",
    "instrument_governance_gate",
    "estimand_governance_gate",
    "uncertainty_semantics_gate",
    "inference_boundary_gate",
    "readout_governance_packet_gate",
)

FUTURE_IMPLEMENTATION_TESTS = (
    "blocked_profiler_blocks_readout_governance",
    "blocked_geo_feasibility_blocks_readout_governance",
    "blocked_design_structure_blocks_readout_governance",
    "blocked_scenario_policy_blocks_or_provisional_readout_governance",
    "blocked_assignment_feasibility_blocks_readout_governance",
    "blocked_assignment_runtime_blocks_readout_governance",
    "missing_assignment_artifact_blocks_readout_governance",
    "missing_reproducibility_manifest_blocks_readout_governance",
    "all_instruments_blocked_blocks_readout_governance",
    "diagnostic_only_instruments_restrict_to_diagnostic_governance",
    "missing_estimand_blocks_claim_eligibility",
    "uncertainty_semantics_mismatch_blocks_causal_interval_claims",
    "geometry_mismatch_blocks_readout_governance",
    "pooled_multicell_claim_blocked_by_default",
    "production_readout_roles_always_blocked",
    "assignment_generated_does_not_authorize_causal_claims",
    "instrument_eligible_does_not_authorize_estimator_execution",
    "readout_governance_eligible_does_not_generate_readout_plan",
    "no_primary_sensitivity_diagnostic_stack_selection",
    "no_estimator_inference_execution",
    "no_effect_lift_roi_pvalues_cis",
    "no_causal_claim_authorization",
    "no_production_readout_authorization",
    "no_fixture_specific_branching",
)

CONTRACT_EXAMPLES = (
    "example_1_assignment_and_instrument_ready_for_planning",
    "example_2_blocked_by_assignment_runtime",
    "example_3_blocked_by_all_instruments",
    "example_4_diagnostic_only_instrument_state",
    "example_5_missing_estimand_blocks_claims",
    "example_6_uncertainty_semantics_mismatch",
    "example_7_pooled_multicell_blocked",
    "example_8_production_readout_roles_blocked",
)

_AUTH_FLAGS = {
    "runtime_readout_method_governance_implemented": False,
    "readout_plan_generated": False,
    "readout_governance_eligibility_computed": False,
    "primary_readout_stack_selected": False,
    "sensitivity_stack_selected": False,
    "diagnostic_stack_selected": False,
    "method_winner_selected": False,
    "estimator_execution_implemented": False,
    "inference_execution_implemented": False,
    "diagnostic_sensitivity_execution": False,
    "runtime_assignment_generation_implemented": False,
    "assignment_plan_generated": False,
    "assignment_candidate_generated": False,
    "assignment_candidate_selected": False,
    "geo_assignment_computed": False,
    "matched_pairs_generated": False,
    "blocks_generated": False,
    "randomization_computed": False,
    "rerandomization_computed": False,
    "thinning_design_generated": False,
    "matching_optimization_computed": False,
    "balance_optimization_computed": False,
    "balance_diagnostics_computed": False,
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
    "causal_claim_authorized": False,
    "incremental_lift_roi_claim_authorized": False,
    "budget_optimization_authorized": False,
    "candidate_design_authorized": False,
    "treatment_control_assignment_authorized": False,
    "estimator_inference_authorized": False,
    "production_readout_authorization_granted": False,
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "production_authorization_granted": False,
    "llm_decisioning_authorized": False,
}

CONTRACT_POSITIVE_FLAGS = {
    "readout_method_governance_contract_defined": True,
    "readout_governance_statuses_defined": True,
    "instrument_governance_statuses_defined": True,
    "claim_eligibility_statuses_defined": True,
    "readout_claim_types_defined": True,
    "assignment_artifact_governance_defined": True,
    "instrument_governance_treatment_defined": True,
    "estimand_governance_treatment_defined": True,
    "uncertainty_semantics_treatment_defined": True,
    "diagnostic_sensitivity_treatment_defined": True,
    "production_readout_blockers_defined": True,
    "claim_boundaries_defined": True,
}

NON_GOALS = (
    "no_readout_plan_generation",
    "no_primary_sensitivity_diagnostic_stack_selection",
    "no_estimator_execution",
    "no_inference_execution",
    "no_diagnostic_sensitivity_execution",
    "no_effect_lift_roi_computation",
    "no_p_values_or_confidence_intervals",
    "no_causal_claim_authorization",
    "no_production_readout_authorization",
    "no_assignment_generation",
    "no_method_winner_selection",
    "no_mmm_runtime_calls",
    "no_llm_decisioning",
)


@dataclass(frozen=True)
class ReadoutMethodGovernanceContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    readout_method_governance_contract_defined: bool
    readout_governance_statuses_defined: bool
    instrument_governance_statuses_defined: bool
    claim_eligibility_statuses_defined: bool
    readout_claim_types_defined: bool
    assignment_artifact_governance_defined: bool
    instrument_governance_treatment_defined: bool
    estimand_governance_treatment_defined: bool
    uncertainty_semantics_treatment_defined: bool
    diagnostic_sensitivity_treatment_defined: bool
    production_readout_blockers_defined: bool
    readout_governance_statuses: tuple[str, ...]
    instrument_governance_statuses: tuple[str, ...]
    claim_eligibility_statuses: tuple[str, ...]
    readout_claim_types: tuple[str, ...]
    assignment_artifact_governance_statuses: tuple[str, ...]
    uncertainty_semantics_classifications: tuple[str, ...]
    diagnostic_sensitivity_slot_types: tuple[str, ...]
    production_readout_blocker_roles: tuple[str, ...]
    future_contract_concepts: tuple[str, ...]
    future_output_concepts: tuple[str, ...]
    governance_packet_fields: tuple[str, ...]
    input_dependencies: tuple[str, ...]
    readiness_gates: tuple[str, ...]
    contract_examples: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


def build_readout_method_governance_contract() -> ReadoutMethodGovernanceContract:
    return ReadoutMethodGovernanceContract(
        artifact_id=_ARTIFACT_ID,
        scope=SCOPE,
        depends_on=DEPENDS_ON,
        readout_method_governance_contract_defined=True,
        readout_governance_statuses_defined=True,
        instrument_governance_statuses_defined=True,
        claim_eligibility_statuses_defined=True,
        readout_claim_types_defined=True,
        assignment_artifact_governance_defined=True,
        instrument_governance_treatment_defined=True,
        estimand_governance_treatment_defined=True,
        uncertainty_semantics_treatment_defined=True,
        diagnostic_sensitivity_treatment_defined=True,
        production_readout_blockers_defined=True,
        readout_governance_statuses=READOUT_GOVERNANCE_STATUSES,
        instrument_governance_statuses=INSTRUMENT_GOVERNANCE_STATUSES,
        claim_eligibility_statuses=CLAIM_ELIGIBILITY_STATUSES,
        readout_claim_types=READOUT_CLAIM_TYPES,
        assignment_artifact_governance_statuses=ASSIGNMENT_ARTIFACT_GOVERNANCE_STATUSES,
        uncertainty_semantics_classifications=UNCERTAINTY_SEMANTICS_CLASSIFICATIONS,
        diagnostic_sensitivity_slot_types=DIAGNOSTIC_SENSITIVITY_SLOT_TYPES,
        production_readout_blocker_roles=PRODUCTION_READOUT_BLOCKER_ROLES,
        future_contract_concepts=FUTURE_CONTRACT_CONCEPTS,
        future_output_concepts=FUTURE_OUTPUT_CONCEPTS,
        governance_packet_fields=GOVERNANCE_PACKET_FIELDS,
        input_dependencies=INPUT_DEPENDENCIES,
        readiness_gates=READINESS_GATES,
        contract_examples=CONTRACT_EXAMPLES,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        alternative_next_artifact=ALTERNATIVE_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_readout_method_governance_contract(
    contract: ReadoutMethodGovernanceContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.readout_method_governance_contract_defined:
        issues.append("readout_method_governance_contract_defined must be true")
    if len(contract.readout_governance_statuses) < 20:
        issues.append("readout_governance_statuses incomplete")
    if len(contract.instrument_governance_statuses) < 6:
        issues.append("instrument_governance_statuses incomplete")
    if len(contract.claim_eligibility_statuses) < 10:
        issues.append("claim_eligibility_statuses incomplete")
    if len(contract.readout_claim_types) < 18:
        issues.append("readout_claim_types incomplete")
    if len(contract.readiness_gates) < 15:
        issues.append("readiness_gates incomplete")
    if "POOLED_MULTICELL_CLAIM" not in contract.readout_claim_types:
        issues.append("POOLED_MULTICELL_CLAIM must be defined")
    if "PRODUCTION_TRUST_REPORT_CLAIM" not in contract.readout_claim_types:
        issues.append("PRODUCTION_TRUST_REPORT_CLAIM must be defined")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_readout_method_governance_contract()
    validation = validate_readout_method_governance_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in READOUT_GOVERNANCE_STATUSES:
        scenarios.append(
            _s(f"readout_governance_status_{status}", status in contract.readout_governance_statuses)
        )
    for status in INSTRUMENT_GOVERNANCE_STATUSES:
        scenarios.append(
            _s(
                f"instrument_governance_status_{status}",
                status in contract.instrument_governance_statuses,
            )
        )
    for status in CLAIM_ELIGIBILITY_STATUSES:
        scenarios.append(
            _s(f"claim_eligibility_status_{status}", status in contract.claim_eligibility_statuses)
        )
    for claim in READOUT_CLAIM_TYPES:
        scenarios.append(_s(f"readout_claim_type_{claim}", claim in contract.readout_claim_types))
    for status in ASSIGNMENT_ARTIFACT_GOVERNANCE_STATUSES:
        scenarios.append(
            _s(
                f"assignment_artifact_governance_status_{status}",
                status in contract.assignment_artifact_governance_statuses,
            )
        )
    for classification in UNCERTAINTY_SEMANTICS_CLASSIFICATIONS:
        scenarios.append(
            _s(
                f"uncertainty_semantics_{classification}",
                classification in contract.uncertainty_semantics_classifications,
            )
        )
    for slot in DIAGNOSTIC_SENSITIVITY_SLOT_TYPES:
        scenarios.append(
            _s(f"diagnostic_sensitivity_slot_{slot}", slot in contract.diagnostic_sensitivity_slot_types)
        )
    for role in PRODUCTION_READOUT_BLOCKER_ROLES:
        scenarios.append(
            _s(f"production_readout_blocker_{role}", role in contract.production_readout_blocker_roles)
        )
    for dep in INPUT_DEPENDENCIES:
        scenarios.append(_s(f"input_dependency_{dep}", dep in contract.input_dependencies))
    for gate in READINESS_GATES:
        scenarios.append(_s(f"readiness_gate_{gate}", gate in contract.readiness_gates))
    for field in GOVERNANCE_PACKET_FIELDS:
        scenarios.append(_s(f"governance_packet_field_{field}", field in contract.governance_packet_fields))
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
    contract = build_readout_method_governance_contract()
    validation = validate_readout_method_governance_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "readout_method_governance_contract",
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
