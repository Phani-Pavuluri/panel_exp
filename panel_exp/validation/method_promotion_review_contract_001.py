"""METHOD_PROMOTION_REVIEW_CONTRACT_001 — metadata-only method promotion review contract."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "METHOD_PROMOTION_REVIEW_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "method_promotion_review_contract_defined_no_runtime_or_promotion"
_VERDICT = "method_promotion_review_contract_defined_no_runtime_or_promotion"
_RECOMMENDED_NEXT = "METHOD_PROMOTION_REVIEW_RUNTIME_001"
_ALTERNATIVE_NEXT = "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/METHOD_PROMOTION_REVIEW_CONTRACT_001_summary.json"
)

DEPENDS_ON = (
    "TRUSTED_READOUT_REPORT_RUNTIME_001",
    "TRUSTED_READOUT_REPORT_CONTRACT_001",
    "CLAIM_AUTHORIZATION_RUNTIME_001",
    "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001",
    "PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001",
    "METHOD_SUITABILITY_RUNTIME_001",
    "ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001",
    "SRM_BALANCE_READOUT_DIAGNOSTIC_001",
    "GOVERNED_RANDOMIZATION_RUNTIME_001",
    "READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001",
)

FUTURE_CONTRACT_CONCEPTS = (
    "MethodPromotionReviewContract",
    "MethodPromotionReviewPacket",
    "MethodPromotionReviewEvidenceBundle",
    "MethodPromotionReviewCandidateVerdict",
    "MethodPromotionReviewFailurePacket",
    "MethodPromotionReviewLineageManifest",
    "MethodPromotionReviewConfig",
    "MethodPromotionReviewInput",
    "MethodPromotionReviewBoundaryReport",
)

PROMOTION_REVIEW_STATUSES = (
    "PROMOTION_REVIEW_NOT_EVALUATED",
    "PROMOTION_REVIEW_READY",
    "PROMOTION_REVIEW_READY_WITH_RESTRICTIONS",
    "PROMOTION_REVIEW_BLOCKED_BY_METHOD_SUITABILITY",
    "PROMOTION_REVIEW_BLOCKED_BY_PRODUCTION_CATALOG",
    "PROMOTION_REVIEW_BLOCKED_BY_STATISTICAL_PROMOTION",
    "PROMOTION_REVIEW_BLOCKED_BY_ASSIGNMENT_INTEGRITY",
    "PROMOTION_REVIEW_BLOCKED_BY_SRM_BALANCE",
    "PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE",
    "PROMOTION_REVIEW_REQUIRES_HUMAN_GOVERNANCE",
    "PROMOTION_REVIEW_CONTRACT_ONLY",
)

CANDIDATE_VERDICTS = (
    "NOT_REVIEWED",
    "BLOCKED",
    "REVIEW_REQUIRED",
    "ELIGIBLE_FOR_RESTRICTED_USE_REVIEW",
    "ELIGIBLE_FOR_PRODUCTION_REVIEW",
    "INSUFFICIENT_EVIDENCE",
)

EVIDENCE_BUNDLE_REQUIREMENTS = (
    "method_instrument_identity",
    "current_production_catalog_status",
    "method_suitability_report",
    "statistical_promotion_report",
    "trusted_readout_report_packet",
    "claim_authorization_report",
    "diagnostics_sensitivity_report",
    "srm_balance_diagnostic_report",
    "assignment_panel_integrity_report",
    "governed_randomization_report",
    "execution_readout_provenance",
    "validation_history_audit_references",
    "known_limitations_and_blockers",
    "lineage_manifest",
)

SCOPE_EVIDENCE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "RESTRICTED_USE_REVIEW": (
        "method_instrument_identity",
        "method_suitability_report",
        "statistical_promotion_report",
        "trusted_readout_report_packet",
        "claim_authorization_report",
        "known_limitations_and_blockers",
    ),
    "PRODUCTION_REVIEW": (
        "method_instrument_identity",
        "current_production_catalog_status",
        "method_suitability_report",
        "statistical_promotion_report",
        "trusted_readout_report_packet",
        "claim_authorization_report",
        "diagnostics_sensitivity_report",
        "srm_balance_diagnostic_report",
        "assignment_panel_integrity_report",
        "governed_randomization_report",
        "execution_readout_provenance",
        "validation_history_audit_references",
        "known_limitations_and_blockers",
        "lineage_manifest",
    ),
}

REVIEW_PACKET_FIELDS = (
    "review_id",
    "review_status",
    "candidate_verdict",
    "method_id",
    "instrument_id",
    "estimator_family",
    "inference_family",
    "current_catalog_status",
    "requested_promotion_scope",
    "evidence_bundle",
    "missing_evidence",
    "blockers",
    "restrictions",
    "required_caveats",
    "eligible_surfaces",
    "prohibited_surfaces",
    "lineage_manifest",
    "provenance_hash",
    "policy_version",
    "failure_packet",
)

FAILURE_PACKET_FIELDS = (
    "failure_code",
    "failure_reason",
    "missing_evidence",
    "failed_evidence",
    "blockers",
    "required_remediation",
    "retry_category",
)

FAILURE_CODES = (
    "MISSING_METHOD_SUITABILITY_REPORT",
    "MISSING_STATISTICAL_PROMOTION_REPORT",
    "MISSING_TRUSTED_READOUT_REPORT",
    "MISSING_CLAIM_AUTHORIZATION_REPORT",
    "MISSING_ASSIGNMENT_INTEGRITY_EVIDENCE",
    "MISSING_SRM_BALANCE_DIAGNOSTIC",
    "PRODUCTION_CATALOG_BLOCKED",
    "STATISTICAL_PROMOTION_FAILED",
    "METHOD_SUITABILITY_BLOCKED",
    "INSUFFICIENT_VALIDATION_HISTORY",
    "HUMAN_GOVERNANCE_REQUIRED",
    "PROMOTION_REVIEW_BLOCKED_BY_POLICY",
)

RETRY_CATEGORIES = (
    "ADD_METHOD_SUITABILITY_REPORT",
    "ADD_STATISTICAL_PROMOTION_REPORT",
    "ADD_TRUSTED_READOUT_REPORT",
    "ADD_ASSIGNMENT_INTEGRITY_EVIDENCE",
    "ADD_SRM_BALANCE_DIAGNOSTIC",
    "FIX_PRODUCTION_CATALOG_BLOCKER",
    "REQUEST_RESTRICTED_SCOPE",
    "REQUIRE_HUMAN_GOVERNANCE_REVIEW",
    "BLOCK_METHOD_PROMOTION_REVIEW",
)

PROMOTION_BOUNDARY_RULES = (
    "promotion_review_collects_evidence_only",
    "no_method_promotion_without_human_governance",
    "no_production_catalog_loosening_from_review",
    "no_method_unblock_from_review_packet",
    "no_production_authorization_from_review_verdict",
    "eligible_for_production_review_is_not_production_approval",
    "candidate_verdict_cannot_grant_production_safe_status",
    "review_packet_must_bind_to_lineage_and_audit_references",
    "blocked_catalog_status_preserved_in_review",
    "statistical_promotion_thresholds_not_relaxed_by_review",
)

PROHIBITED_SURFACES = (
    "PRODUCTION_APPROVED",
    "PRODUCTION_SAFE",
    "METHOD_UNBLOCKED",
    "CATALOG_LOOSENED",
    "CAUSAL_CERTIFIED",
    "INCREMENTAL_LIFT_CERTIFIED",
    "ROI_CERTIFIED",
    "STATISTICAL_SIGNIFICANCE_CERTIFIED",
    "CONFIDENCE_INTERVAL_CERTIFIED",
    "TRUSTED_BUSINESS_RECOMMENDATION",
)

FUTURE_RUNTIME_TESTS = (
    "promotion_review_blocks_without_method_suitability_report",
    "promotion_review_blocks_without_statistical_promotion_report",
    "promotion_review_requires_trusted_readout_report_packet",
    "promotion_review_never_sets_production_safe_status",
    "promotion_review_never_unblocks_production_catalog",
    "promotion_review_never_promotes_method_directly",
    "promotion_review_eligible_for_production_review_requires_human_governance",
    "promotion_review_preserves_blockers_and_restrictions",
    "promotion_review_deterministic_review_id_and_provenance_hash",
    "promotion_review_binds_evidence_and_audit_references",
    "no_fixture_specific_branching",
)

NON_GOALS = (
    "no_method_promotion_review_runtime",
    "no_method_promotion",
    "no_method_unblocking",
    "no_production_catalog_loosening",
    "no_production_authorization",
    "no_production_readout_authorization",
    "no_estimator_execution",
    "no_inference_execution",
    "no_uncertainty_computation",
    "no_p_values_or_confidence_intervals",
    "no_mmm_runtime_calls",
    "no_llm_decisioning",
)

_AUTH_FLAGS = {
    "method_promotion_runtime_implemented": False,
    "method_promoted": False,
    "method_unblocked": False,
    "production_catalog_unblocked": False,
    "production_authorization_granted": False,
    "production_readout_authorized": False,
    "trusted_business_recommendation_authorized": False,
    "estimator_implemented": False,
    "inference_implemented": False,
    "bootstrap_inference_implemented": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "effect_estimate_computed_new": False,
    "lift_computed_new": False,
    "roi_computed_new": False,
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "llm_decisioning_authorized": False,
}

CONTRACT_POSITIVE_FLAGS = {
    "method_promotion_review_contract_defined": True,
    "promotion_review_status_taxonomy_defined": True,
    "promotion_review_candidate_verdict_taxonomy_defined": True,
    "promotion_review_packet_fields_defined": True,
    "promotion_review_evidence_requirements_defined": True,
    "promotion_review_failure_packet_semantics_defined": True,
    "promotion_review_future_runtime_tests_documented": True,
    "production_authorization_boundary_defined": True,
}


@dataclass(frozen=True)
class MethodPromotionReviewContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    method_promotion_review_contract_defined: bool
    promotion_review_status_taxonomy_defined: bool
    promotion_review_candidate_verdict_taxonomy_defined: bool
    promotion_review_packet_fields_defined: bool
    promotion_review_evidence_requirements_defined: bool
    promotion_review_failure_packet_semantics_defined: bool
    promotion_review_future_runtime_tests_documented: bool
    production_authorization_boundary_defined: bool
    promotion_review_statuses: tuple[str, ...]
    candidate_verdicts: tuple[str, ...]
    evidence_bundle_requirements: tuple[str, ...]
    scope_evidence_requirements: dict[str, tuple[str, ...]]
    review_packet_fields: tuple[str, ...]
    failure_packet_fields: tuple[str, ...]
    failure_codes: tuple[str, ...]
    retry_categories: tuple[str, ...]
    promotion_boundary_rules: tuple[str, ...]
    prohibited_surfaces: tuple[str, ...]
    future_contract_concepts: tuple[str, ...]
    future_runtime_tests: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


def build_method_promotion_review_contract() -> MethodPromotionReviewContract:
    return MethodPromotionReviewContract(
        artifact_id=_ARTIFACT_ID,
        scope=_SCOPE,
        depends_on=DEPENDS_ON,
        method_promotion_review_contract_defined=True,
        promotion_review_status_taxonomy_defined=True,
        promotion_review_candidate_verdict_taxonomy_defined=True,
        promotion_review_packet_fields_defined=True,
        promotion_review_evidence_requirements_defined=True,
        promotion_review_failure_packet_semantics_defined=True,
        promotion_review_future_runtime_tests_documented=True,
        production_authorization_boundary_defined=True,
        promotion_review_statuses=PROMOTION_REVIEW_STATUSES,
        candidate_verdicts=CANDIDATE_VERDICTS,
        evidence_bundle_requirements=EVIDENCE_BUNDLE_REQUIREMENTS,
        scope_evidence_requirements=SCOPE_EVIDENCE_REQUIREMENTS,
        review_packet_fields=REVIEW_PACKET_FIELDS,
        failure_packet_fields=FAILURE_PACKET_FIELDS,
        failure_codes=FAILURE_CODES,
        retry_categories=RETRY_CATEGORIES,
        promotion_boundary_rules=PROMOTION_BOUNDARY_RULES,
        prohibited_surfaces=PROHIBITED_SURFACES,
        future_contract_concepts=FUTURE_CONTRACT_CONCEPTS,
        future_runtime_tests=FUTURE_RUNTIME_TESTS,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=_RECOMMENDED_NEXT,
        alternative_next_artifact=_ALTERNATIVE_NEXT,
        final_verdict=_VERDICT,
    )


def validate_method_promotion_review_contract(
    contract: MethodPromotionReviewContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.method_promotion_review_contract_defined:
        issues.append("method_promotion_review_contract_defined must be true")
    if len(contract.promotion_review_statuses) < 10:
        issues.append("promotion_review_statuses incomplete")
    if len(contract.candidate_verdicts) < 6:
        issues.append("candidate_verdicts incomplete")
    if "PRODUCTION_APPROVED" in contract.candidate_verdicts:
        issues.append("candidate_verdicts must not include production approval")
    if "METHOD_PROMOTED" in contract.candidate_verdicts:
        issues.append("candidate_verdicts must not include method promoted")
    if "method_suitability_report" not in contract.evidence_bundle_requirements:
        issues.append("method_suitability_report missing from evidence bundle")
    if "trusted_readout_report_packet" not in contract.evidence_bundle_requirements:
        issues.append("trusted_readout_report_packet missing from evidence bundle")
    if "review_id" not in contract.review_packet_fields:
        issues.append("review_packet_fields incomplete")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        if not getattr(contract, key, False):
            issues.append(f"contract positive flag {key} must be {expected}")
    if not contract.production_authorization_boundary_defined:
        issues.append("production_authorization_boundary must be defined")
    return {"valid": not issues, "issues": issues}


def get_method_promotion_review_contract_metadata() -> dict[str, Any]:
    contract = build_method_promotion_review_contract()
    return {
        "artifact_id": contract.artifact_id,
        "artifact_version": _ARTIFACT_VERSION,
        "scope": contract.scope,
        "depends_on": list(contract.depends_on),
        "final_verdict": contract.final_verdict,
        "recommended_next_artifact": contract.recommended_next_artifact,
        "alternative_next_artifact": contract.alternative_next_artifact,
        **CONTRACT_POSITIVE_FLAGS,
        **contract.authorization_flags,
    }


def list_method_promotion_review_statuses() -> tuple[str, ...]:
    return PROMOTION_REVIEW_STATUSES


def list_method_promotion_review_verdicts() -> tuple[str, ...]:
    return CANDIDATE_VERDICTS


def list_method_promotion_review_evidence_requirements() -> dict[str, tuple[str, ...]]:
    return dict(SCOPE_EVIDENCE_REQUIREMENTS)


def list_method_promotion_review_future_tests() -> tuple[str, ...]:
    return FUTURE_RUNTIME_TESTS


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_method_promotion_review_contract()
    validation = validate_method_promotion_review_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in PROMOTION_REVIEW_STATUSES:
        scenarios.append(_s(f"promotion_review_status_{status}", status in contract.promotion_review_statuses))
    for verdict in CANDIDATE_VERDICTS:
        scenarios.append(_s(f"candidate_verdict_{verdict}", verdict in contract.candidate_verdicts))
    for req in EVIDENCE_BUNDLE_REQUIREMENTS:
        scenarios.append(_s(f"evidence_bundle_{req}", req in contract.evidence_bundle_requirements))
    for scope, reqs in SCOPE_EVIDENCE_REQUIREMENTS.items():
        scenarios.append(_s(f"scope_evidence_{scope}", scope in contract.scope_evidence_requirements))
        scenarios.append(_s(f"scope_evidence_nonempty_{scope}", len(reqs) > 0))
    for field in REVIEW_PACKET_FIELDS:
        scenarios.append(_s(f"review_packet_field_{field}", field in contract.review_packet_fields))
    for field in FAILURE_PACKET_FIELDS:
        scenarios.append(_s(f"failure_packet_field_{field}", field in contract.failure_packet_fields))
    for code in FAILURE_CODES:
        scenarios.append(_s(f"failure_code_{code}", code in contract.failure_codes))
    for category in RETRY_CATEGORIES:
        scenarios.append(_s(f"retry_category_{category}", category in contract.retry_categories))
    for rule in PROMOTION_BOUNDARY_RULES:
        scenarios.append(_s(f"boundary_rule_{rule[:40]}", rule in contract.promotion_boundary_rules))
    for surface in PROHIBITED_SURFACES:
        scenarios.append(_s(f"prohibited_surface_{surface}", surface in contract.prohibited_surfaces))
    for concept in FUTURE_CONTRACT_CONCEPTS:
        scenarios.append(_s(f"future_concept_{concept}", concept in contract.future_contract_concepts))
    for test_id in FUTURE_RUNTIME_TESTS:
        scenarios.append(_s(f"future_test_{test_id}", True))
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not contract.authorization_flags[flag]))
    for key, val in CONTRACT_POSITIVE_FLAGS.items():
        scenarios.append(_s(f"contract_positive_{key}", val))
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
    contract = build_method_promotion_review_contract()
    validation = validate_method_promotion_review_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "method_promotion_review_contract",
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
