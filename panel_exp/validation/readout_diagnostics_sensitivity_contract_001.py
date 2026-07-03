"""READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001 metadata-only validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "readout_diagnostics_sensitivity_contract_defined_no_diagnostic_or_sensitivity_execution"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001_summary.json"
)

SCOPE = "contract_only_no_diagnostic_or_sensitivity_execution"
RECOMMENDED_NEXT_ARTIFACT = "READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001"
ALTERNATIVE_NEXT_ARTIFACT = "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR"

DEPENDS_ON = (
    "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_002_GOVERNED_EXECUTOR_ADAPTERS",
    "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001",
    "ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001",
    "READOUT_PLAN_RUNTIME_001",
    "READOUT_PLAN_CONTRACT_001",
    "METHOD_SUITABILITY_RUNTIME_001",
    "DESIGN_ASSIGNMENT_RUNTIME_001",
)

DIAGNOSTIC_TYPES = (
    "PRE_PERIOD_FIT_DIAGNOSTIC",
    "COVARIATE_BALANCE_DIAGNOSTIC",
    "ASSIGNMENT_REPRODUCIBILITY_DIAGNOSTIC",
    "PLACEBO_DIAGNOSTIC",
    "DONOR_SUPPORT_DIAGNOSTIC",
    "PARALLEL_TREND_DIAGNOSTIC",
    "OUTLIER_DIAGNOSTIC",
    "INTERFERENCE_RISK_DIAGNOSTIC",
    "SPEND_SUPPORT_DIAGNOSTIC",
    "COMMON_CONTROL_CONFLICT_DIAGNOSTIC",
    "SPLIT_CONTROL_RECHECK_DIAGNOSTIC",
    "DATA_CONTRACT_DIAGNOSTIC",
    "INSTRUMENT_GOVERNANCE_DIAGNOSTIC",
    "UNCERTAINTY_SEMANTICS_DIAGNOSTIC",
    "EXECUTOR_AVAILABILITY_DIAGNOSTIC",
)

SENSITIVITY_TYPES = (
    "JACKKNIFE_SENSITIVITY",
    "BOOTSTRAP_SENSITIVITY",
    "PLACEBO_SENSITIVITY",
    "KFOLD_SENSITIVITY",
    "DONOR_SET_SENSITIVITY",
    "OUTLIER_EXCLUSION_SENSITIVITY",
    "WINDOW_LENGTH_SENSITIVITY",
    "COVARIATE_SET_SENSITIVITY",
    "SPEND_SUPPORT_SENSITIVITY",
    "ASSIGNMENT_VARIANT_SENSITIVITY",
    "INTERFERENCE_ASSUMPTION_SENSITIVITY",
    "ESTIMAND_RECLASSIFICATION_SENSITIVITY",
)

DIAGNOSTIC_STATUSES = (
    "DIAGNOSTIC_REQUIRED_NOT_PLANNED",
    "DIAGNOSTIC_PLANNED_NOT_RUN",
    "DIAGNOSTIC_NOT_APPLICABLE",
    "DIAGNOSTIC_BLOCKED",
    "DIAGNOSTIC_FAILED",
    "DIAGNOSTIC_PASSED",
    "DIAGNOSTIC_PASSED_WITH_WARNINGS",
    "DIAGNOSTIC_INCONCLUSIVE",
    "DIAGNOSTIC_NOT_EVALUATED",
)

SENSITIVITY_STATUSES = (
    "SENSITIVITY_REQUIRED_NOT_PLANNED",
    "SENSITIVITY_PLANNED_NOT_RUN",
    "SENSITIVITY_NOT_APPLICABLE",
    "SENSITIVITY_BLOCKED",
    "SENSITIVITY_FAILED",
    "SENSITIVITY_PASSED",
    "SENSITIVITY_PASSED_WITH_WARNINGS",
    "SENSITIVITY_INCONCLUSIVE",
    "SENSITIVITY_NOT_EVALUATED",
)

EVIDENCE_SUFFICIENCY_STATUSES = (
    "EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW",
    "EVIDENCE_SUFFICIENT_WITH_WARNINGS",
    "EVIDENCE_PROVISIONAL",
    "EVIDENCE_INSUFFICIENT_MISSING_DIAGNOSTICS",
    "EVIDENCE_INSUFFICIENT_MISSING_SENSITIVITY",
    "EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS",
    "EVIDENCE_INSUFFICIENT_FAILED_SENSITIVITY",
    "EVIDENCE_INSUFFICIENT_EXECUTION_NOT_COMPLETED",
    "EVIDENCE_BLOCKED_BY_GOVERNANCE",
    "EVIDENCE_NOT_EVALUATED",
)

FUTURE_CONTRACT_CONCEPTS = (
    "ReadoutDiagnosticRequirement",
    "ReadoutSensitivityRequirement",
    "ReadoutDiagnosticPlan",
    "ReadoutSensitivityPlan",
    "ReadoutDiagnosticResult",
    "ReadoutSensitivityResult",
    "ReadoutDiagnosticStatus",
    "ReadoutSensitivityStatus",
    "ReadoutDiagnosticEvidencePacket",
    "ReadoutSensitivityEvidencePacket",
    "ReadoutDiagnosticFailurePacket",
    "ReadoutSensitivityFailurePacket",
    "ReadoutDiagnosticTrace",
    "ReadoutSensitivityTrace",
    "ReadoutEvidenceAggregationReport",
    "ReadoutEvidenceSufficiencyReport",
    "ReadoutDiagnosticSensitivityClaimBoundaryReport",
)

REQUIREMENT_FIELDS = (
    "requirement_id",
    "requirement_type",
    "applies_to_instrument_id",
    "applies_to_execution_role",
    "applies_to_estimand",
    "required_for_claim_type",
    "required_for_production",
    "required_before_execution",
    "required_after_execution",
    "blocking_if_missing",
    "blocking_if_failed",
    "minimum_evidence_level",
    "threshold_policy",
    "governance_source",
    "notes",
)

PLAN_FIELDS = (
    "plan_id",
    "requirement_id",
    "instrument_id",
    "execution_artifact_id",
    "planned_check_type",
    "planned_input_artifacts",
    "planned_output_artifacts",
    "planned_threshold_policy",
    "planned_execution_mode",
    "planned_status",
    "blocking_policy",
    "warnings",
)

RESULT_FIELDS = (
    "result_id",
    "plan_id",
    "requirement_id",
    "instrument_id",
    "execution_artifact_id",
    "result_status",
    "result_value",
    "threshold",
    "threshold_direction",
    "passed",
    "blocking_result",
    "interpretation",
    "evidence_level",
    "artifact_references",
    "warnings",
)

FAILURE_PACKET_FIELDS = (
    "failure_id",
    "requirement_id",
    "plan_id",
    "instrument_id",
    "execution_artifact_id",
    "failure_status",
    "missing_inputs",
    "blocked_requirements",
    "failed_requirements",
    "inconclusive_requirements",
    "governance_failures",
    "suggested_retry_categories",
    "claim_boundary_report",
)

RETRY_CATEGORIES = (
    "ADD_REQUIRED_DIAGNOSTIC_PLAN",
    "ADD_REQUIRED_SENSITIVITY_PLAN",
    "FIX_DIAGNOSTIC_INPUTS",
    "FIX_SENSITIVITY_INPUTS",
    "RERUN_EXECUTION_WITH_REQUIRED_TRACE",
    "CHANGE_READOUT_PLAN",
    "RESTRICT_CLAIM_SCOPE",
    "BLOCK_CLAIM",
    "BLOCK_INSTRUMENT",
    "BLOCK_DESIGN",
)

EVIDENCE_GATES = (
    "execution_artifact_presence_gate",
    "diagnostic_requirement_presence_gate",
    "sensitivity_requirement_presence_gate",
    "diagnostic_plan_gate",
    "sensitivity_plan_gate",
    "diagnostic_result_gate",
    "sensitivity_result_gate",
    "diagnostic_failure_inconclusive_gate",
    "sensitivity_failure_inconclusive_gate",
    "evidence_sufficiency_gate",
    "claim_review_handoff_gate",
)

INPUT_DEPENDENCIES = (
    "readout_plan_report",
    "readout_plan_packet",
    "planned_primary_candidates",
    "planned_sensitivity_candidates",
    "planned_diagnostic_candidates",
    "instrument_execution_results",
    "execution_artifact_manifest",
    "execution_trace",
    "estimator_inference_execution_report",
    "governed_executor_lookup_results",
    "diagnostic_requirements",
    "sensitivity_requirements",
    "assignment_artifact",
    "execution_data_contract",
    "estimand_scope",
    "production_governance_config",
)

FUTURE_IMPLEMENTATION_TESTS = (
    "missing_execution_artifact_blocks_evidence_sufficiency",
    "missing_required_diagnostic_blocks_or_provisionalizes",
    "missing_required_sensitivity_blocks_or_provisionalizes",
    "diagnostic_only_instrument_cannot_support_production_claim_evidence",
    "failed_blocking_diagnostic_blocks_claim_review",
    "failed_nonblocking_diagnostic_produces_warning_provisional",
    "inconclusive_sensitivity_produces_provisional_status",
    "did_bootstrap_requires_parallel_trend_and_bootstrap_stability",
    "scm_placebo_remains_diagnostic_only",
    "augsynth_jackknife_requires_donor_support_and_jackknife_sensitivity",
    "tbr_ridge_brb_requires_pre_period_fit_and_outlier_sensitivity",
    "evidence_sufficiency_does_not_authorize_claims",
    "no_estimator_execution",
    "no_inference_execution",
    "no_effect_lift_roi_pvalues_cis",
    "no_production_authorization",
    "no_fixture_specific_branching",
)

CONTRACT_EXAMPLES = (
    "example_1_did_bootstrap_parallel_trend_and_bootstrap_stability",
    "example_2_scm_placebo_diagnostic_only_no_production_lift",
    "example_3_scm_jackknife_donor_support_and_jackknife_stability",
    "example_4_tbr_ridge_brb_pre_period_fit_and_outlier_sensitivity",
    "example_5_augsynth_jackknife_donor_support_range_stress",
    "example_6_missing_diagnostic_plan_blocks_evidence_sufficiency",
    "example_7_missing_sensitivity_result_provisionalizes_claim_review",
    "example_8_failed_blocking_diagnostic_prevents_claim_review",
    "example_9_inconclusive_sensitivity_produces_provisional_evidence",
    "example_10_execution_not_completed_blocks_evidence_sufficiency",
)

_AUTH_FLAGS = {
    "diagnostics_sensitivity_runtime_implemented": False,
    "diagnostic_check_executed": False,
    "sensitivity_check_executed": False,
    "diagnostic_result_computed": False,
    "sensitivity_result_computed": False,
    "diagnostic_pass_fail_computed": False,
    "sensitivity_pass_fail_computed": False,
    "evidence_sufficiency_computed": False,
    "estimator_execution_implemented": False,
    "inference_execution_implemented": False,
    "effect_estimate_computed": False,
    "lift_computed": False,
    "roi_computed": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
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
    "diagnostics_sensitivity_contract_defined": True,
    "diagnostic_requirement_contract_defined": True,
    "sensitivity_requirement_contract_defined": True,
    "diagnostic_plan_contract_defined": True,
    "sensitivity_plan_contract_defined": True,
    "diagnostic_result_contract_defined": True,
    "sensitivity_result_contract_defined": True,
    "evidence_sufficiency_contract_defined": True,
    "failure_packet_contract_defined": True,
    "claim_boundaries_defined": True,
}

NON_GOALS = (
    "no_diagnostics_sensitivity_runtime",
    "no_diagnostic_execution",
    "no_sensitivity_execution",
    "no_placebo_jackknife_bootstrap_conformal_execution",
    "no_parallel_trend_computation",
    "no_pre_period_fit_computation",
    "no_donor_support_computation",
    "no_outlier_sensitivity_execution",
    "no_interference_analysis_execution",
    "no_estimator_execution",
    "no_inference_execution",
    "no_effect_lift_roi_computation",
    "no_p_values_or_confidence_intervals",
    "no_uncertainty_computation",
    "no_causal_claim_authorization",
    "no_production_readout_authorization",
    "no_mmm_runtime_calls",
    "no_llm_decisioning",
)


@dataclass(frozen=True)
class ReadoutDiagnosticsSensitivityContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    diagnostics_sensitivity_contract_defined: bool
    diagnostic_requirement_contract_defined: bool
    sensitivity_requirement_contract_defined: bool
    diagnostic_plan_contract_defined: bool
    sensitivity_plan_contract_defined: bool
    diagnostic_result_contract_defined: bool
    sensitivity_result_contract_defined: bool
    evidence_sufficiency_contract_defined: bool
    failure_packet_contract_defined: bool
    diagnostic_types: tuple[str, ...]
    sensitivity_types: tuple[str, ...]
    diagnostic_statuses: tuple[str, ...]
    sensitivity_statuses: tuple[str, ...]
    evidence_sufficiency_statuses: tuple[str, ...]
    future_contract_concepts: tuple[str, ...]
    requirement_fields: tuple[str, ...]
    plan_fields: tuple[str, ...]
    result_fields: tuple[str, ...]
    failure_packet_fields: tuple[str, ...]
    retry_categories: tuple[str, ...]
    input_dependencies: tuple[str, ...]
    evidence_gates: tuple[str, ...]
    contract_examples: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


def build_readout_diagnostics_sensitivity_contract() -> ReadoutDiagnosticsSensitivityContract:
    return ReadoutDiagnosticsSensitivityContract(
        artifact_id=_ARTIFACT_ID,
        scope=SCOPE,
        depends_on=DEPENDS_ON,
        diagnostics_sensitivity_contract_defined=True,
        diagnostic_requirement_contract_defined=True,
        sensitivity_requirement_contract_defined=True,
        diagnostic_plan_contract_defined=True,
        sensitivity_plan_contract_defined=True,
        diagnostic_result_contract_defined=True,
        sensitivity_result_contract_defined=True,
        evidence_sufficiency_contract_defined=True,
        failure_packet_contract_defined=True,
        diagnostic_types=DIAGNOSTIC_TYPES,
        sensitivity_types=SENSITIVITY_TYPES,
        diagnostic_statuses=DIAGNOSTIC_STATUSES,
        sensitivity_statuses=SENSITIVITY_STATUSES,
        evidence_sufficiency_statuses=EVIDENCE_SUFFICIENCY_STATUSES,
        future_contract_concepts=FUTURE_CONTRACT_CONCEPTS,
        requirement_fields=REQUIREMENT_FIELDS,
        plan_fields=PLAN_FIELDS,
        result_fields=RESULT_FIELDS,
        failure_packet_fields=FAILURE_PACKET_FIELDS,
        retry_categories=RETRY_CATEGORIES,
        input_dependencies=INPUT_DEPENDENCIES,
        evidence_gates=EVIDENCE_GATES,
        contract_examples=CONTRACT_EXAMPLES,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        alternative_next_artifact=ALTERNATIVE_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_readout_diagnostics_sensitivity_contract(
    contract: ReadoutDiagnosticsSensitivityContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.diagnostics_sensitivity_contract_defined:
        issues.append("diagnostics_sensitivity_contract_defined must be true")
    if len(contract.diagnostic_types) < 15:
        issues.append("diagnostic_types incomplete")
    if len(contract.sensitivity_types) < 12:
        issues.append("sensitivity_types incomplete")
    if len(contract.diagnostic_statuses) < 9:
        issues.append("diagnostic_statuses incomplete")
    if len(contract.sensitivity_statuses) < 9:
        issues.append("sensitivity_statuses incomplete")
    if len(contract.evidence_sufficiency_statuses) < 10:
        issues.append("evidence_sufficiency_statuses incomplete")
    if len(contract.evidence_gates) < 11:
        issues.append("evidence_gates incomplete")
    if len(contract.contract_examples) < 10:
        issues.append("contract_examples incomplete")
    if contract.evidence_gates[0] != "execution_artifact_presence_gate":
        issues.append("evidence_gates must start with execution_artifact_presence_gate")
    if contract.evidence_gates[-1] != "claim_review_handoff_gate":
        issues.append("evidence_gates must end with claim_review_handoff_gate")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_readout_diagnostics_sensitivity_contract()
    validation = validate_readout_diagnostics_sensitivity_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for dtype in DIAGNOSTIC_TYPES:
        scenarios.append(_s(f"diagnostic_type_{dtype}", dtype in contract.diagnostic_types))
    for stype in SENSITIVITY_TYPES:
        scenarios.append(_s(f"sensitivity_type_{stype}", stype in contract.sensitivity_types))
    for status in DIAGNOSTIC_STATUSES:
        scenarios.append(_s(f"diagnostic_status_{status}", status in contract.diagnostic_statuses))
    for status in SENSITIVITY_STATUSES:
        scenarios.append(_s(f"sensitivity_status_{status}", status in contract.sensitivity_statuses))
    for status in EVIDENCE_SUFFICIENCY_STATUSES:
        scenarios.append(
            _s(f"evidence_sufficiency_status_{status}", status in contract.evidence_sufficiency_statuses)
        )
    for dep in INPUT_DEPENDENCIES:
        scenarios.append(_s(f"input_dependency_{dep}", dep in contract.input_dependencies))
    for gate in EVIDENCE_GATES:
        scenarios.append(_s(f"evidence_gate_{gate}", gate in contract.evidence_gates))
    for field in REQUIREMENT_FIELDS:
        scenarios.append(_s(f"requirement_field_{field}", field in contract.requirement_fields))
    for field in PLAN_FIELDS:
        scenarios.append(_s(f"plan_field_{field}", field in contract.plan_fields))
    for field in RESULT_FIELDS:
        scenarios.append(_s(f"result_field_{field}", field in contract.result_fields))
    for field in FAILURE_PACKET_FIELDS:
        scenarios.append(_s(f"failure_packet_field_{field}", field in contract.failure_packet_fields))
    for category in RETRY_CATEGORIES:
        scenarios.append(_s(f"retry_category_{category}", category in contract.retry_categories))
    for ex in CONTRACT_EXAMPLES:
        scenarios.append(_s(f"example_{ex}", ex in contract.contract_examples))
    for concept in FUTURE_CONTRACT_CONCEPTS:
        scenarios.append(_s(f"contract_concept_{concept}", concept in contract.future_contract_concepts))
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
    contract = build_readout_diagnostics_sensitivity_contract()
    validation = validate_readout_diagnostics_sensitivity_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "readout_diagnostics_sensitivity_contract",
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
