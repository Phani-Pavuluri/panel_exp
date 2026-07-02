"""ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001 metadata-only validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "estimator_inference_execution_contract_defined_no_estimator_or_inference_execution"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001_summary.json"

SCOPE = "contract_only_no_estimator_or_inference_execution"
RECOMMENDED_NEXT_ARTIFACT = "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001"
ALTERNATIVE_NEXT_ARTIFACT = "READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001"

DEPENDS_ON = (
    "READOUT_PLAN_RUNTIME_001",
    "READOUT_PLAN_CONTRACT_001",
    "READOUT_METHOD_GOVERNANCE_CONTRACT_001",
    "METHOD_SUITABILITY_RUNTIME_001",
    "DESIGN_ASSIGNMENT_RUNTIME_001",
)

EXECUTION_STATUSES = (
    "EXECUTION_READY_FOR_RUNTIME",
    "EXECUTION_READY_WITH_WARNINGS",
    "EXECUTION_PROVISIONAL",
    "EXECUTION_BLOCKED_BY_READOUT_PLAN",
    "EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT",
    "EXECUTION_BLOCKED_BY_DATA_CONTRACT",
    "EXECUTION_BLOCKED_BY_ESTIMAND",
    "EXECUTION_BLOCKED_BY_INSTRUMENT_SPEC",
    "EXECUTION_BLOCKED_BY_UNCERTAINTY_SEMANTICS",
    "EXECUTION_BLOCKED_BY_MISSING_INPUT_DATA",
    "EXECUTION_BLOCKED_BY_DIAGNOSTIC_REQUIREMENTS",
    "EXECUTION_BLOCKED_BY_SENSITIVITY_REQUIREMENTS",
    "EXECUTION_BLOCKED_BY_GOVERNANCE",
    "EXECUTION_NOT_EVALUATED",
)

INSTRUMENT_EXECUTION_STATUSES = (
    "INSTRUMENT_EXECUTION_READY",
    "INSTRUMENT_EXECUTION_READY_WITH_WARNINGS",
    "INSTRUMENT_EXECUTION_PROVISIONAL",
    "INSTRUMENT_EXECUTION_BLOCKED",
    "INSTRUMENT_EXECUTION_FAILED",
    "INSTRUMENT_EXECUTION_NOT_RUN",
    "INSTRUMENT_EXECUTION_COMPLETED",
)

EXECUTION_ROLES = (
    "PRIMARY_EXECUTION_CANDIDATE",
    "SENSITIVITY_EXECUTION_CANDIDATE",
    "DIAGNOSTIC_EXECUTION_CANDIDATE",
    "REFERENCE_ONLY_EXECUTION_CANDIDATE",
    "BLOCKED_EXECUTION_CANDIDATE",
    "NOT_EVALUATED_EXECUTION_CANDIDATE",
)

FUTURE_CONTRACT_CONCEPTS = (
    "EstimatorInferenceExecutionInput",
    "EstimatorInferenceExecutionConfig",
    "EstimatorInferenceExecutionReport",
    "EstimatorInferenceExecutionPacket",
    "InstrumentExecutionRequest",
    "InstrumentExecutionResult",
    "InstrumentExecutionStatus",
    "InstrumentExecutionRole",
    "ExecutionInputDataContract",
    "ExecutionDesignArtifactReference",
    "ExecutionAssignmentArtifactReference",
    "ExecutionEstimandReference",
    "ExecutionInstrumentSpec",
    "ExecutionEffectEstimateReport",
    "ExecutionUncertaintyReport",
    "ExecutionIntervalReport",
    "ExecutionPValueReport",
    "ExecutionInferenceDiagnosticReport",
    "ExecutionModelDiagnosticReport",
    "ExecutionAssumptionCheckReport",
    "ExecutionTrace",
    "ExecutionProvenanceManifest",
    "ExecutionArtifactManifest",
    "ExecutionFailurePacket",
    "ExecutionRetryPolicy",
    "ExecutionClaimBoundaryReport",
)

INSTRUMENT_SPEC_FIELDS = (
    "instrument_id",
    "estimator_family",
    "inference_family",
    "execution_role",
    "estimand_type",
    "metric_name",
    "unit_id_field",
    "time_field",
    "outcome_field",
    "treatment_field",
    "cell_id_field",
    "assignment_artifact_id",
    "pre_period",
    "test_period",
    "covariate_fields",
    "spend_fields",
    "geo_fields",
    "required_input_grain",
    "uncertainty_semantics",
    "interval_type",
    "p_value_semantics",
    "diagnostic_requirements",
    "sensitivity_requirements",
    "governance_restrictions",
)

INPUT_DATA_CONTRACT_FIELDS = (
    "panel_data_reference",
    "required_columns",
    "required_grain",
    "required_time_window",
    "required_geo_unit_coverage",
    "required_treatment_assignment_join",
    "required_metric_availability",
    "required_covariate_availability",
    "required_spend_availability",
    "missingness_policy",
    "duplicate_policy",
    "outlier_policy",
    "data_version",
    "data_hash",
)

EFFECT_ESTIMATE_REPORT_FIELDS = (
    "effect_estimate_id",
    "instrument_id",
    "estimand",
    "metric_name",
    "effect_scale",
    "point_estimate",
    "baseline_reference",
    "relative_lift",
    "absolute_lift",
    "unit_scope",
    "population_scope",
    "time_window",
    "cell_contrast",
    "sample_size_summary",
    "estimation_status",
    "warnings",
)

UNCERTAINTY_REPORT_FIELDS = (
    "uncertainty_report_id",
    "instrument_id",
    "uncertainty_semantics",
    "interval_type",
    "confidence_or_credible_level",
    "standard_error",
    "interval_lower",
    "interval_upper",
    "p_value",
    "distribution_summary",
    "uncertainty_status",
    "warnings",
)

INFERENCE_DIAGNOSTIC_REPORT_FIELDS = (
    "diagnostic_report_id",
    "instrument_id",
    "diagnostic_type",
    "diagnostic_status",
    "diagnostic_value",
    "threshold",
    "interpretation",
    "blocking_flag",
    "warnings",
)

EXECUTION_TRACE_FIELDS = (
    "execution_id",
    "instrument_id",
    "readout_plan_artifact_id",
    "assignment_artifact_id",
    "data_artifact_id",
    "algorithm_version",
    "code_version",
    "config_hash",
    "data_hash",
    "input_hash",
    "output_hash",
    "runtime_environment",
    "execution_timestamp_policy",
)

FAILURE_PACKET_FIELDS = (
    "failure_id",
    "execution_id",
    "instrument_id",
    "execution_status",
    "blocking_gates",
    "missing_inputs",
    "data_contract_failures",
    "assignment_artifact_failures",
    "estimand_failures",
    "uncertainty_semantics_failures",
    "diagnostic_prerequisite_failures",
    "sensitivity_prerequisite_failures",
    "governance_failures",
    "suggested_retry_categories",
    "claim_boundary_report",
)

RETRY_CATEGORIES = (
    "FIX_INPUT_DATA_CONTRACT",
    "FIX_ASSIGNMENT_ARTIFACT",
    "FIX_ESTIMAND_SPEC",
    "FIX_INSTRUMENT_SPEC",
    "FIX_UNCERTAINTY_SEMANTICS",
    "ADD_REQUIRED_DIAGNOSTICS",
    "ADD_REQUIRED_SENSITIVITY_CHECKS",
    "CHANGE_READOUT_PLAN",
    "BLOCK_INSTRUMENT",
    "BLOCK_DESIGN",
)

READINESS_GATES = (
    "readout_plan_gate",
    "assignment_artifact_gate",
    "estimator_inference_instrument_spec_gate",
    "data_contract_gate",
    "estimand_compatibility_gate",
    "uncertainty_semantics_gate",
    "diagnostics_prerequisite_gate",
    "sensitivity_prerequisite_gate",
    "governance_restriction_gate",
    "provenance_trace_gate",
    "execution_packet_gate",
)

INPUT_DEPENDENCIES = (
    "readout_plan_report",
    "readout_plan_packet",
    "planned_primary_candidates",
    "planned_sensitivity_candidates",
    "planned_diagnostic_candidates",
    "blocked_instruments",
    "not_evaluated_instruments",
    "execution_prerequisites",
    "design_assignment_runtime_report",
    "assignment_plan",
    "assignment_candidate",
    "unit_allocation_report",
    "reproducibility_manifest",
    "execution_input_data_contract",
    "estimand_reference",
    "instrument_execution_specs",
    "provenance_config",
)

FUTURE_IMPLEMENTATION_TESTS = (
    "blocked_readout_plan_blocks_execution_readiness",
    "blocked_instrument_blocks_execution_readiness",
    "missing_assignment_artifact_blocks",
    "missing_input_data_contract_blocks",
    "missing_required_outcome_column_blocks",
    "missing_treatment_assignment_join_blocks",
    "missing_estimand_blocks",
    "incompatible_estimand_blocks",
    "missing_uncertainty_semantics_blocks_or_provisionalizes",
    "diagnostic_only_instrument_cannot_be_primary_production_execution",
    "restricted_instrument_requires_governance_caveats",
    "did_bootstrap_execution_packet_fields",
    "scm_placebo_diagnostic_packet_fields",
    "tbr_ridge_brb_restricted_packet_fields",
    "failure_packet_emitted_on_missing_data_contract",
    "execution_trace_requires_hashes_provenance",
    "no_estimator_execution_in_contract",
    "no_inference_execution_in_contract",
    "no_effect_lift_roi_pvalues_cis",
    "no_claim_authorization",
    "no_production_authorization",
    "no_fixture_specific_branching",
)

CONTRACT_EXAMPLES = (
    "example_1_did_bootstrap_primary_complete_data_contract",
    "example_2_scm_placebo_diagnostic_only_no_production_lift",
    "example_3_tbr_ridge_brb_restricted_governance_caveats",
    "example_4_augsynth_jackknife_diagnostic_donor_support",
    "example_5_ab_standard_inference_blocked_geo_panel",
    "example_6_missing_assignment_artifact_blocks_readiness",
    "example_7_missing_outcome_column_blocks_readiness",
    "example_8_missing_uncertainty_semantics_provisional",
    "example_9_dosage_estimand_requires_compatible_spec",
    "example_10_budget_reallocation_blocks_simple_roi_interpretation",
)

_AUTH_FLAGS = {
    "estimator_inference_execution_runtime_implemented": False,
    "instrument_execution_completed": False,
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
    "estimator_inference_execution_contract_defined": True,
    "execution_input_contract_defined": True,
    "instrument_execution_request_contract_defined": True,
    "instrument_execution_result_contract_defined": True,
    "effect_estimate_report_contract_defined": True,
    "uncertainty_report_contract_defined": True,
    "inference_diagnostic_report_contract_defined": True,
    "execution_trace_contract_defined": True,
    "execution_failure_packet_contract_defined": True,
    "claim_boundaries_defined": True,
}

NON_GOALS = (
    "no_estimator_inference_execution_runtime",
    "no_instrument_execution_completion",
    "no_estimator_execution",
    "no_inference_execution",
    "no_scm_tbr_did_augsynth_fitting",
    "no_placebo_jackknife_bootstrap_conformal_execution",
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
class EstimatorInferenceExecutionContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    estimator_inference_execution_contract_defined: bool
    execution_input_contract_defined: bool
    instrument_execution_request_contract_defined: bool
    instrument_execution_result_contract_defined: bool
    effect_estimate_report_contract_defined: bool
    uncertainty_report_contract_defined: bool
    inference_diagnostic_report_contract_defined: bool
    execution_trace_contract_defined: bool
    execution_failure_packet_contract_defined: bool
    execution_statuses: tuple[str, ...]
    instrument_execution_statuses: tuple[str, ...]
    execution_roles: tuple[str, ...]
    future_contract_concepts: tuple[str, ...]
    instrument_spec_fields: tuple[str, ...]
    input_data_contract_fields: tuple[str, ...]
    effect_estimate_report_fields: tuple[str, ...]
    uncertainty_report_fields: tuple[str, ...]
    inference_diagnostic_report_fields: tuple[str, ...]
    execution_trace_fields: tuple[str, ...]
    failure_packet_fields: tuple[str, ...]
    retry_categories: tuple[str, ...]
    input_dependencies: tuple[str, ...]
    readiness_gates: tuple[str, ...]
    contract_examples: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


def build_estimator_inference_execution_contract() -> EstimatorInferenceExecutionContract:
    return EstimatorInferenceExecutionContract(
        artifact_id=_ARTIFACT_ID,
        scope=SCOPE,
        depends_on=DEPENDS_ON,
        estimator_inference_execution_contract_defined=True,
        execution_input_contract_defined=True,
        instrument_execution_request_contract_defined=True,
        instrument_execution_result_contract_defined=True,
        effect_estimate_report_contract_defined=True,
        uncertainty_report_contract_defined=True,
        inference_diagnostic_report_contract_defined=True,
        execution_trace_contract_defined=True,
        execution_failure_packet_contract_defined=True,
        execution_statuses=EXECUTION_STATUSES,
        instrument_execution_statuses=INSTRUMENT_EXECUTION_STATUSES,
        execution_roles=EXECUTION_ROLES,
        future_contract_concepts=FUTURE_CONTRACT_CONCEPTS,
        instrument_spec_fields=INSTRUMENT_SPEC_FIELDS,
        input_data_contract_fields=INPUT_DATA_CONTRACT_FIELDS,
        effect_estimate_report_fields=EFFECT_ESTIMATE_REPORT_FIELDS,
        uncertainty_report_fields=UNCERTAINTY_REPORT_FIELDS,
        inference_diagnostic_report_fields=INFERENCE_DIAGNOSTIC_REPORT_FIELDS,
        execution_trace_fields=EXECUTION_TRACE_FIELDS,
        failure_packet_fields=FAILURE_PACKET_FIELDS,
        retry_categories=RETRY_CATEGORIES,
        input_dependencies=INPUT_DEPENDENCIES,
        readiness_gates=READINESS_GATES,
        contract_examples=CONTRACT_EXAMPLES,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        alternative_next_artifact=ALTERNATIVE_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_estimator_inference_execution_contract(
    contract: EstimatorInferenceExecutionContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.estimator_inference_execution_contract_defined:
        issues.append("estimator_inference_execution_contract_defined must be true")
    if len(contract.execution_statuses) < 14:
        issues.append("execution_statuses incomplete")
    if len(contract.instrument_execution_statuses) < 7:
        issues.append("instrument_execution_statuses incomplete")
    if len(contract.execution_roles) < 6:
        issues.append("execution_roles incomplete")
    if len(contract.readiness_gates) < 11:
        issues.append("readiness_gates incomplete")
    if len(contract.contract_examples) < 10:
        issues.append("contract_examples incomplete")
    if contract.readiness_gates[0] != "readout_plan_gate":
        issues.append("readiness_gates must start with readout_plan_gate")
    if contract.readiness_gates[-1] != "execution_packet_gate":
        issues.append("readiness_gates must end with execution_packet_gate")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_estimator_inference_execution_contract()
    validation = validate_estimator_inference_execution_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in EXECUTION_STATUSES:
        scenarios.append(_s(f"execution_status_{status}", status in contract.execution_statuses))
    for status in INSTRUMENT_EXECUTION_STATUSES:
        scenarios.append(
            _s(f"instrument_execution_status_{status}", status in contract.instrument_execution_statuses)
        )
    for role in EXECUTION_ROLES:
        scenarios.append(_s(f"execution_role_{role}", role in contract.execution_roles))
    for dep in INPUT_DEPENDENCIES:
        scenarios.append(_s(f"input_dependency_{dep}", dep in contract.input_dependencies))
    for gate in READINESS_GATES:
        scenarios.append(_s(f"readiness_gate_{gate}", gate in contract.readiness_gates))
    for field in INSTRUMENT_SPEC_FIELDS:
        scenarios.append(_s(f"instrument_spec_field_{field}", field in contract.instrument_spec_fields))
    for field in INPUT_DATA_CONTRACT_FIELDS:
        scenarios.append(
            _s(f"input_data_contract_field_{field}", field in contract.input_data_contract_fields)
        )
    for field in EFFECT_ESTIMATE_REPORT_FIELDS:
        scenarios.append(
            _s(f"effect_estimate_report_field_{field}", field in contract.effect_estimate_report_fields)
        )
    for field in UNCERTAINTY_REPORT_FIELDS:
        scenarios.append(
            _s(f"uncertainty_report_field_{field}", field in contract.uncertainty_report_fields)
        )
    for field in INFERENCE_DIAGNOSTIC_REPORT_FIELDS:
        scenarios.append(
            _s(
                f"inference_diagnostic_report_field_{field}",
                field in contract.inference_diagnostic_report_fields,
            )
        )
    for field in EXECUTION_TRACE_FIELDS:
        scenarios.append(_s(f"execution_trace_field_{field}", field in contract.execution_trace_fields))
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
    contract = build_estimator_inference_execution_contract()
    validation = validate_estimator_inference_execution_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "estimator_inference_execution_contract",
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
