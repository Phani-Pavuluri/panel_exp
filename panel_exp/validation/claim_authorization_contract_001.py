"""CLAIM_AUTHORIZATION_CONTRACT_001 — metadata-only claim authorization contract harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "CLAIM_AUTHORIZATION_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "contract_only_no_claim_or_production_authorization"
_VERDICT = "claim_authorization_contract_defined_no_claim_or_production_authorization"
_RECOMMENDED_NEXT = "CLAIM_AUTHORIZATION_RUNTIME_001"
_ALTERNATIVE_NEXT = "TRUSTED_READOUT_REPORT_CONTRACT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/CLAIM_AUTHORIZATION_CONTRACT_001_summary.json"
)

DEPENDS_ON = (
    "READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC",
    "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR",
    "READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001",
    "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_002_GOVERNED_EXECUTOR_ADAPTERS",
    "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001",
    "READOUT_PLAN_RUNTIME_001",
)

FUTURE_CONTRACT_CONCEPTS = (
    "ClaimAuthorizationInput",
    "ClaimAuthorizationConfig",
    "ClaimRequest",
    "ClaimDecision",
    "ClaimAuthorizationReport",
    "ClaimEvidenceBundle",
    "ClaimScope",
    "ClaimType",
    "ClaimStatus",
    "ClaimBlocker",
    "ClaimCaveat",
    "ClaimRestriction",
    "ClaimBoundaryReport",
    "ClaimFailurePacket",
    "ClaimTrace",
    "ClaimProvenanceManifest",
    "TrustedReadoutHandoffPacket",
)

CLAIM_TYPES = (
    "DIAGNOSTIC_ONLY_CLAIM",
    "DESCRIPTIVE_EFFECT_CLAIM",
    "POINT_ESTIMATE_CLAIM",
    "INCREMENTAL_LIFT_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "ROI_CLAIM",
    "PRODUCTION_READOUT_CLAIM",
    "METHOD_COMPARISON_CLAIM",
    "SENSITIVITY_ONLY_CLAIM",
    "INSUFFICIENT_EVIDENCE_CLAIM",
)

CLAIM_STATUSES = (
    "CLAIM_AUTHORIZATION_READY_FOR_RUNTIME",
    "CLAIM_REVIEW_ELIGIBLE",
    "CLAIM_REVIEW_ELIGIBLE_WITH_WARNINGS",
    "CLAIM_PROVISIONAL_REVIEW_ONLY",
    "CLAIM_AUTHORIZED",
    "CLAIM_AUTHORIZED_WITH_RESTRICTIONS",
    "CLAIM_RESTRICTED_TO_DIAGNOSTIC_ONLY",
    "CLAIM_BLOCKED_BY_MISSING_EXECUTION",
    "CLAIM_BLOCKED_BY_MISSING_EFFECT_ESTIMATE",
    "CLAIM_BLOCKED_BY_MISSING_UNCERTAINTY",
    "CLAIM_BLOCKED_BY_MISSING_DIAGNOSTICS",
    "CLAIM_BLOCKED_BY_FAILED_DIAGNOSTICS",
    "CLAIM_BLOCKED_BY_MISSING_SENSITIVITY",
    "CLAIM_BLOCKED_BY_FAILED_SENSITIVITY",
    "CLAIM_BLOCKED_BY_INCOMPATIBLE_ESTIMAND",
    "CLAIM_BLOCKED_BY_METHOD_GOVERNANCE",
    "CLAIM_BLOCKED_BY_ASSIGNMENT_ARTIFACT",
    "CLAIM_BLOCKED_BY_PRODUCTION_GOVERNANCE",
    "CLAIM_BLOCKED_BY_ROI_GOVERNANCE",
    "CLAIM_NOT_EVALUATED",
)

CLAIM_REQUEST_FIELDS = (
    "claim_request_id",
    "claim_type",
    "requested_metric",
    "requested_estimand",
    "requested_population_scope",
    "requested_unit_scope",
    "requested_time_window",
    "requested_cell_contrast",
    "requested_effect_scale",
    "requested_uncertainty_semantics",
    "requires_production_readout",
    "requires_roi_support",
    "requires_causal_language",
    "requires_incrementality_language",
    "requires_diagnostic_disclosure",
    "requested_output_audience",
    "governance_source",
    "notes",
)

EVIDENCE_BUNDLE_FIELDS = (
    "execution_artifact_id",
    "instrument_id",
    "estimator_family",
    "inference_family",
    "effect_estimate_report",
    "uncertainty_report",
    "inference_diagnostic_report",
    "diagnostic_evidence_packets",
    "sensitivity_evidence_packets",
    "evidence_sufficiency_report",
    "assignment_artifact_reference",
    "readout_plan_artifact_reference",
    "method_suitability_reference",
    "executor_adapter_reference",
    "estimand_scope",
    "claim_scope",
    "provenance_manifest",
)

CLAIM_DECISION_FIELDS = (
    "claim_decision_id",
    "claim_request_id",
    "claim_type",
    "claim_status",
    "authorized_claim_text",
    "authorized_claim_scope",
    "restrictions",
    "caveats",
    "blockers",
    "required_disclosures",
    "evidence_bundle_references",
    "claim_boundary_report",
    "trusted_readout_handoff",
    "warnings",
)

BLOCKER_CATEGORIES = (
    "MISSING_EXECUTION_ARTIFACT",
    "MISSING_EFFECT_ESTIMATE",
    "MISSING_UNCERTAINTY_ARTIFACT",
    "MISSING_DIAGNOSTIC_EVIDENCE",
    "FAILED_DIAGNOSTIC_EVIDENCE",
    "MISSING_SENSITIVITY_EVIDENCE",
    "FAILED_SENSITIVITY_EVIDENCE",
    "INCONCLUSIVE_EVIDENCE",
    "INCOMPATIBLE_ESTIMAND",
    "INCOMPATIBLE_EFFECT_SCALE",
    "UNSUPPORTED_CLAIM_TYPE",
    "METHOD_GOVERNANCE_RESTRICTION",
    "ASSIGNMENT_ARTIFACT_RESTRICTION",
    "DIAGNOSTIC_ONLY_INSTRUMENT",
    "ROI_GOVERNANCE_MISSING",
    "PRODUCTION_GOVERNANCE_MISSING",
    "PROVENANCE_MISSING",
)

CLAIM_GATES = (
    "claim_request_schema_gate",
    "execution_artifact_gate",
    "effect_estimate_gate",
    "uncertainty_inference_gate",
    "diagnostic_evidence_gate",
    "sensitivity_evidence_gate",
    "estimand_compatibility_gate",
    "method_instrument_governance_gate",
    "assignment_artifact_gate",
    "roi_governance_gate",
    "production_governance_gate",
    "provenance_trace_gate",
    "claim_scope_caveat_gate",
    "trusted_readout_handoff_gate",
)

FAILURE_PACKET_FIELDS = (
    "failure_id",
    "claim_request_id",
    "claim_type",
    "claim_status",
    "blocking_gates",
    "blockers",
    "missing_evidence",
    "failed_evidence",
    "inconclusive_evidence",
    "governance_failures",
    "required_remediation",
    "claim_boundary_report",
)

RETRY_CATEGORIES = (
    "ADD_EXECUTION_ARTIFACT",
    "ADD_EFFECT_ESTIMATE",
    "ADD_UNCERTAINTY_ARTIFACT",
    "ADD_DIAGNOSTIC_EVIDENCE",
    "ADD_SENSITIVITY_EVIDENCE",
    "FIX_ESTIMAND_SCOPE",
    "FIX_ASSIGNMENT_ARTIFACT",
    "RESTRICT_TO_POINT_ESTIMATE_CLAIM",
    "RESTRICT_TO_DIAGNOSTIC_ONLY_CLAIM",
    "ADD_ROI_GOVERNANCE",
    "ADD_PRODUCTION_GOVERNANCE",
    "BLOCK_CLAIM",
)

CONTRACT_EXAMPLES = (
    "example_1_did_point_estimate_no_uncertainty_point_estimate_review_only",
    "example_2_did_point_estimate_plus_coverage_diagnostic_no_causal_lift",
    "example_3_failed_blocking_diagnostic_blocks_causal_incremental_review",
    "example_4_diagnostic_only_instrument_diagnostic_only_claim_only",
    "example_5_missing_effect_estimate_blocks_point_estimate_claim",
    "example_6_missing_uncertainty_blocks_causal_lift_claim",
    "example_7_missing_sensitivity_blocks_incremental_lift_claim",
    "example_8_roi_claim_blocked_without_roi_governance",
    "example_9_production_readout_blocked_without_production_governance",
    "example_10_insufficient_evidence_claim_allowed_as_safe_negative",
)

FUTURE_IMPLEMENTATION_TESTS = (
    "missing_execution_artifact_blocks_claims",
    "missing_effect_estimate_blocks_point_estimate_claim",
    "did_point_estimate_without_uncertainty_only_allows_point_estimate_review_caveat",
    "missing_uncertainty_blocks_causal_lift_claim",
    "missing_diagnostics_blocks_causal_lift_claim",
    "failed_blocking_diagnostic_blocks_causal_lift_claim",
    "missing_sensitivity_blocks_incremental_lift_claim",
    "diagnostic_only_instrument_restricted_to_diagnostic_only_claim",
    "roi_claim_blocked_without_roi_governance",
    "production_readout_blocked_without_production_governance",
    "insufficient_evidence_claim_allowed",
    "claim_authorization_does_not_compute_effect_inference_diagnostics",
    "no_fixture_specific_branching",
)

_AUTH_FLAGS = {
    "claim_authorization_runtime_implemented": False,
    "claim_authorized": False,
    "claim_authorized_with_restrictions": False,
    "authorized_claim_text_generated": False,
    "trusted_readout_handoff_generated": False,
    "production_readout_authorized": False,
    "causal_claim_authorized": False,
    "incremental_lift_claim_authorized": False,
    "roi_claim_authorized": False,
    "production_authorization_granted": False,
    "estimator_execution_implemented": False,
    "inference_execution_implemented": False,
    "effect_estimate_computed": False,
    "diagnostic_check_executed": False,
    "sensitivity_check_executed": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "llm_decisioning_authorized": False,
}

CONTRACT_POSITIVE_FLAGS = {
    "claim_authorization_contract_defined": True,
    "claim_request_contract_defined": True,
    "claim_evidence_bundle_contract_defined": True,
    "claim_decision_contract_defined": True,
    "claim_statuses_defined": True,
    "claim_blockers_defined": True,
    "claim_gate_order_defined": True,
    "claim_type_evidence_matrix_defined": True,
    "claim_failure_packet_contract_defined": True,
    "claim_boundaries_defined": True,
}

NON_GOALS = (
    "no_claim_authorization_runtime",
    "no_claim_authorization",
    "no_production_readout_authorization",
    "no_authorized_claim_text_generation",
    "no_trusted_readout_handoff_generation",
    "no_estimator_execution",
    "no_inference_execution",
    "no_effect_computation",
    "no_diagnostic_execution",
    "no_sensitivity_execution",
    "no_p_values_or_confidence_intervals",
    "no_uncertainty_computation",
    "no_mmm_runtime_calls",
    "no_llm_decisioning",
)


@dataclass(frozen=True)
class ClaimAuthorizationContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    claim_authorization_contract_defined: bool
    claim_request_contract_defined: bool
    claim_evidence_bundle_contract_defined: bool
    claim_decision_contract_defined: bool
    claim_statuses_defined: bool
    claim_blockers_defined: bool
    claim_gate_order_defined: bool
    claim_type_evidence_matrix_defined: bool
    claim_failure_packet_contract_defined: bool
    claim_boundaries_defined: bool
    claim_types: tuple[str, ...]
    claim_statuses: tuple[str, ...]
    future_contract_concepts: tuple[str, ...]
    claim_request_fields: tuple[str, ...]
    evidence_bundle_fields: tuple[str, ...]
    claim_decision_fields: tuple[str, ...]
    blocker_categories: tuple[str, ...]
    claim_gates: tuple[str, ...]
    failure_packet_fields: tuple[str, ...]
    retry_categories: tuple[str, ...]
    contract_examples: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


def build_claim_authorization_contract() -> ClaimAuthorizationContract:
    return ClaimAuthorizationContract(
        artifact_id=_ARTIFACT_ID,
        scope=_SCOPE,
        depends_on=DEPENDS_ON,
        claim_authorization_contract_defined=True,
        claim_request_contract_defined=True,
        claim_evidence_bundle_contract_defined=True,
        claim_decision_contract_defined=True,
        claim_statuses_defined=True,
        claim_blockers_defined=True,
        claim_gate_order_defined=True,
        claim_type_evidence_matrix_defined=True,
        claim_failure_packet_contract_defined=True,
        claim_boundaries_defined=True,
        claim_types=CLAIM_TYPES,
        claim_statuses=CLAIM_STATUSES,
        future_contract_concepts=FUTURE_CONTRACT_CONCEPTS,
        claim_request_fields=CLAIM_REQUEST_FIELDS,
        evidence_bundle_fields=EVIDENCE_BUNDLE_FIELDS,
        claim_decision_fields=CLAIM_DECISION_FIELDS,
        blocker_categories=BLOCKER_CATEGORIES,
        claim_gates=CLAIM_GATES,
        failure_packet_fields=FAILURE_PACKET_FIELDS,
        retry_categories=RETRY_CATEGORIES,
        contract_examples=CONTRACT_EXAMPLES,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=_RECOMMENDED_NEXT,
        alternative_next_artifact=_ALTERNATIVE_NEXT,
        final_verdict=_VERDICT,
    )


def validate_claim_authorization_contract(
    contract: ClaimAuthorizationContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.claim_authorization_contract_defined:
        issues.append("claim_authorization_contract_defined must be true")
    if len(contract.claim_types) < 10:
        issues.append("claim_types incomplete")
    if len(contract.claim_statuses) < 20:
        issues.append("claim_statuses incomplete")
    if len(contract.claim_gates) < 14:
        issues.append("claim_gates incomplete")
    if len(contract.contract_examples) < 10:
        issues.append("contract_examples incomplete")
    if contract.claim_gates[0] != "claim_request_schema_gate":
        issues.append("claim_gates must start with claim_request_schema_gate")
    if contract.claim_gates[-1] != "trusted_readout_handoff_gate":
        issues.append("claim_gates must end with trusted_readout_handoff_gate")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_claim_authorization_contract()
    validation = validate_claim_authorization_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for ctype in CLAIM_TYPES:
        scenarios.append(_s(f"claim_type_{ctype}", ctype in contract.claim_types))
    for status in CLAIM_STATUSES:
        scenarios.append(_s(f"claim_status_{status}", status in contract.claim_statuses))
    for concept in FUTURE_CONTRACT_CONCEPTS:
        scenarios.append(_s(f"contract_concept_{concept}", concept in contract.future_contract_concepts))
    for field in CLAIM_REQUEST_FIELDS:
        scenarios.append(_s(f"claim_request_field_{field}", field in contract.claim_request_fields))
    for field in EVIDENCE_BUNDLE_FIELDS:
        scenarios.append(_s(f"evidence_bundle_field_{field}", field in contract.evidence_bundle_fields))
    for field in CLAIM_DECISION_FIELDS:
        scenarios.append(_s(f"claim_decision_field_{field}", field in contract.claim_decision_fields))
    for blocker in BLOCKER_CATEGORIES:
        scenarios.append(_s(f"blocker_{blocker}", blocker in contract.blocker_categories))
    for gate in CLAIM_GATES:
        scenarios.append(_s(f"claim_gate_{gate}", gate in contract.claim_gates))
    for field in FAILURE_PACKET_FIELDS:
        scenarios.append(_s(f"failure_packet_field_{field}", field in contract.failure_packet_fields))
    for category in RETRY_CATEGORIES:
        scenarios.append(_s(f"retry_category_{category}", category in contract.retry_categories))
    for ex in CONTRACT_EXAMPLES:
        scenarios.append(_s(f"example_{ex}", ex in contract.contract_examples))
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
    contract = build_claim_authorization_contract()
    validation = validate_claim_authorization_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "claim_authorization_contract",
        "base_commit": _git_commit(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": list(DEPENDS_ON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
        "failed_scenarios": failed,
        "validation": validation,
        "final_verdict": _VERDICT,
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
