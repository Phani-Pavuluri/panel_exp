"""PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001 — metadata-only production compatibility review contract."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "production_compatibility_promotion_review_contract_defined_no_runtime_or_authorization"
_VERDICT = "production_compatibility_promotion_review_contract_defined_no_runtime_or_authorization"
_RECOMMENDED_NEXT = "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001"
_ALTERNATIVE_NEXT = "PRODUCTION_READINESS_GOVERNANCE_PACKET_CONTRACT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001_summary.json"
)

DEPENDS_ON = (
    "METHOD_PROMOTION_REVIEW_RUNTIME_001",
    "METHOD_PROMOTION_REVIEW_CONTRACT_001",
    "TRUSTED_READOUT_REPORT_RUNTIME_001",
    "CLAIM_AUTHORIZATION_RUNTIME_001",
    "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001",
    "ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001",
    "SRM_BALANCE_READOUT_DIAGNOSTIC_001",
    "PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001",
    "GOVERNED_RANDOMIZATION_RUNTIME_001",
    "READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001",
)

FUTURE_CONTRACT_CONCEPTS = (
    "ProductionCompatibilityPromotionReviewContract",
    "ProductionCompatibilityReviewPacket",
    "ProductionCompatibilityEvidenceBundle",
    "ProductionCompatibilityCandidateVerdict",
    "ProductionCompatibilityFailurePacket",
    "ProductionCompatibilityLineageManifest",
    "ProductionCompatibilityReviewConfig",
    "ProductionCompatibilityReviewInput",
    "ProductionCompatibilityBoundaryReport",
)

PRODUCTION_COMPATIBILITY_STATUSES = (
    "PRODUCTION_COMPATIBILITY_NOT_EVALUATED",
    "PRODUCTION_COMPATIBILITY_REVIEW_READY",
    "PRODUCTION_COMPATIBILITY_REVIEW_READY_WITH_RESTRICTIONS",
    "PRODUCTION_COMPATIBILITY_BLOCKED_BY_METHOD_PROMOTION_REVIEW",
    "PRODUCTION_COMPATIBILITY_BLOCKED_BY_PRODUCTION_CATALOG",
    "PRODUCTION_COMPATIBILITY_BLOCKED_BY_MISSING_TRUSTED_READOUT",
    "PRODUCTION_COMPATIBILITY_BLOCKED_BY_CLAIM_AUTHORIZATION",
    "PRODUCTION_COMPATIBILITY_BLOCKED_BY_STATISTICAL_PROMOTION",
    "PRODUCTION_COMPATIBILITY_BLOCKED_BY_ASSIGNMENT_INTEGRITY",
    "PRODUCTION_COMPATIBILITY_BLOCKED_BY_SRM_BALANCE",
    "PRODUCTION_COMPATIBILITY_BLOCKED_BY_GOVERNANCE",
    "PRODUCTION_COMPATIBILITY_REQUIRES_HUMAN_APPROVAL",
    "PRODUCTION_COMPATIBILITY_CONTRACT_ONLY",
)

CANDIDATE_VERDICTS = (
    "NOT_REVIEWED",
    "BLOCKED",
    "INSUFFICIENT_EVIDENCE",
    "REQUIRES_HUMAN_GOVERNANCE",
    "ELIGIBLE_FOR_PRODUCTION_COMPATIBILITY_REVIEW",
    "ELIGIBLE_FOR_RESTRICTED_PRODUCTION_COMPATIBILITY_REVIEW",
)

EVIDENCE_BUNDLE_REQUIREMENTS = (
    "method_promotion_review_report",
    "trusted_readout_report",
    "claim_authorization_report",
    "production_catalog_report",
    "method_suitability_report",
    "statistical_promotion_report",
    "assignment_panel_integrity_report",
    "srm_balance_diagnostic_report",
    "governed_randomization_report",
    "diagnostics_sensitivity_report",
    "execution_readout_provenance",
    "audit_registry_references",
    "limitations_blockers",
    "human_governance_requirement_record",
    "lineage_provenance_manifest",
)

SCOPE_EVIDENCE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "RESTRICTED_PRODUCTION_COMPATIBILITY_REVIEW": (
        "method_promotion_review_report",
        "trusted_readout_report",
        "claim_authorization_report",
        "production_catalog_report",
        "method_suitability_report",
        "statistical_promotion_report",
        "limitations_blockers",
        "human_governance_requirement_record",
    ),
    "PRODUCTION_COMPATIBILITY_REVIEW": (
        "method_promotion_review_report",
        "trusted_readout_report",
        "claim_authorization_report",
        "production_catalog_report",
        "method_suitability_report",
        "statistical_promotion_report",
        "assignment_panel_integrity_report",
        "srm_balance_diagnostic_report",
        "governed_randomization_report",
        "diagnostics_sensitivity_report",
        "execution_readout_provenance",
        "audit_registry_references",
        "limitations_blockers",
        "human_governance_requirement_record",
        "lineage_provenance_manifest",
    ),
}

COMPATIBILITY_PACKET_FIELDS = (
    "compatibility_review_id",
    "compatibility_status",
    "candidate_verdict",
    "method_id",
    "instrument_id",
    "estimator_family",
    "inference_family",
    "current_catalog_status",
    "requested_compatibility_scope",
    "upstream_method_promotion_review_id",
    "trusted_readout_report_id",
    "claim_authorization_report_id",
    "evidence_bundle",
    "missing_evidence",
    "failed_evidence",
    "blockers",
    "restrictions",
    "required_caveats",
    "required_human_governance_gates",
    "eligible_surfaces",
    "prohibited_surfaces",
    "production_candidate_surface",
    "lineage_manifest",
    "provenance_hash",
    "policy_version",
    "failure_packet",
    "authorization_boundary_report",
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

ALLOWED_SURFACES = (
    "DIAGNOSTIC_ONLY",
    "RESEARCH_OR_REVIEW_ONLY",
    "RESTRICTED_USE_REVIEW",
    "PRODUCTION_COMPATIBILITY_CANDIDATE_REVIEW",
)

PROHIBITED_SURFACES = (
    "PRODUCTION_APPROVAL",
    "PRODUCTION_RECOMMENDATION",
    "BUDGET_SCALING_RECOMMENDATION",
    "ROI_CLAIM",
    "CAUSAL_CLAIM",
    "INCREMENTAL_LIFT_CLAIM",
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "CONFIDENCE_INTERVAL_CLAIM",
    "METHOD_PROMOTION_NOTICE",
    "CATALOG_UNBLOCK_NOTICE",
)

HARD_BLOCKERS = (
    "method_promotion_review_missing",
    "method_promotion_review_blocked",
    "method_promotion_review_only_insufficient_evidence",
    "production_catalog_blocked",
    "trusted_readout_missing_or_blocked",
    "claim_authorization_missing_or_blocked_for_required_surfaces",
    "statistical_promotion_failed",
    "assignment_integrity_failed",
    "srm_balance_failed",
    "governed_randomization_failed",
    "required_diagnostics_missing",
    "human_governance_gate_missing",
)

FAILURE_CODES = (
    "MISSING_METHOD_PROMOTION_REVIEW",
    "METHOD_PROMOTION_REVIEW_BLOCKED",
    "PRODUCTION_CATALOG_BLOCKED",
    "MISSING_TRUSTED_READOUT_REPORT",
    "TRUSTED_READOUT_BLOCKED",
    "CLAIM_AUTHORIZATION_BLOCKED",
    "STATISTICAL_PROMOTION_BLOCKED",
    "ASSIGNMENT_INTEGRITY_BLOCKED",
    "SRM_BALANCE_BLOCKED",
    "GOVERNED_RANDOMIZATION_BLOCKED",
    "DIAGNOSTICS_MISSING",
    "HUMAN_GOVERNANCE_REQUIRED",
    "PRODUCTION_COMPATIBILITY_BLOCKED_BY_POLICY",
)

RETRY_CATEGORIES = (
    "ADD_METHOD_PROMOTION_REVIEW",
    "ADD_TRUSTED_READOUT_REPORT",
    "ADD_CLAIM_AUTHORIZATION_REPORT",
    "ADD_REQUIRED_DIAGNOSTICS",
    "ADD_ASSIGNMENT_INTEGRITY_EVIDENCE",
    "ADD_SRM_BALANCE_DIAGNOSTIC",
    "FIX_PRODUCTION_CATALOG_BLOCKER",
    "REQUEST_RESTRICTED_COMPATIBILITY_SCOPE",
    "REQUIRE_HUMAN_GOVERNANCE_REVIEW",
    "BLOCK_PRODUCTION_COMPATIBILITY_REVIEW",
)

COMPATIBILITY_BOUNDARY_RULES = (
    "production_compatibility_stricter_than_method_promotion_eligibility",
    "method_promotion_review_prerequisite_required",
    "no_production_approval_from_compatibility_verdict",
    "no_method_promotion_from_compatibility_packet",
    "no_production_catalog_loosening_from_compatibility_review",
    "no_method_unblock_from_compatibility_review",
    "eligible_for_production_compatibility_review_is_not_production_approval",
    "human_governance_required_before_production_compatibility",
    "blocked_catalog_status_preserved_in_compatibility_review",
    "trusted_readout_and_claim_authorization_must_bind",
    "statistical_promotion_thresholds_not_relaxed_by_compatibility_review",
)

FUTURE_RUNTIME_TESTS = (
    "production_compatibility_blocks_without_method_promotion_review",
    "production_compatibility_blocks_when_method_promotion_review_blocked",
    "production_compatibility_blocks_when_production_catalog_blocks_method",
    "production_compatibility_blocks_without_trusted_readout_report",
    "production_compatibility_blocks_when_trusted_readout_has_blocked_required_surfaces",
    "production_compatibility_propagates_claim_authorization_prohibited_surfaces",
    "production_compatibility_blocks_on_statistical_promotion_failure",
    "production_compatibility_blocks_on_assignment_integrity_failure",
    "production_compatibility_blocks_on_srm_balance_failure",
    "production_compatibility_requires_human_governance_for_production_compatibility",
    "production_compatibility_emits_eligibility_only_not_production_authorization",
    "production_compatibility_preserves_current_catalog_status",
    "production_compatibility_deterministic_compatibility_review_id_and_provenance_hash",
    "production_compatibility_all_forbidden_production_promotion_computation_flags_false",
    "no_fixture_specific_branching",
)

NON_GOALS = (
    "no_production_compatibility_runtime",
    "no_production_compatibility_packet_generation",
    "no_method_promotion",
    "no_method_unblocking",
    "no_production_catalog_loosening",
    "no_production_authorization",
    "no_production_readout_authorization",
    "no_trusted_business_recommendation_authorization",
    "no_authorized_claim_text_generation",
    "no_polished_narrative_generation",
    "no_estimator_execution",
    "no_inference_execution",
    "no_uncertainty_computation",
    "no_p_values_or_confidence_intervals",
    "no_mmm_runtime_calls",
    "no_llm_decisioning",
)

_AUTH_FLAGS = {
    "production_compatibility_runtime_implemented": False,
    "production_compatibility_packet_generated": False,
    "method_promoted": False,
    "method_unblocked": False,
    "production_catalog_unblocked": False,
    "production_authorization_granted": False,
    "production_readout_authorized": False,
    "trusted_business_recommendation_authorized": False,
    "authorized_claim_text_generated": False,
    "polished_narrative_generated": False,
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
    "production_compatibility_promotion_review_contract_defined": True,
    "production_compatibility_status_taxonomy_defined": True,
    "production_compatibility_verdict_taxonomy_defined": True,
    "production_compatibility_packet_fields_defined": True,
    "production_compatibility_evidence_requirements_defined": True,
    "production_compatibility_blockers_defined": True,
    "production_compatibility_failure_packet_semantics_defined": True,
    "production_compatibility_future_runtime_tests_documented": True,
    "production_authorization_boundary_defined": True,
}


@dataclass(frozen=True)
class ProductionCompatibilityPromotionReviewContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    production_compatibility_promotion_review_contract_defined: bool
    production_compatibility_status_taxonomy_defined: bool
    production_compatibility_verdict_taxonomy_defined: bool
    production_compatibility_packet_fields_defined: bool
    production_compatibility_evidence_requirements_defined: bool
    production_compatibility_blockers_defined: bool
    production_compatibility_failure_packet_semantics_defined: bool
    production_compatibility_future_runtime_tests_documented: bool
    production_authorization_boundary_defined: bool
    production_compatibility_statuses: tuple[str, ...]
    candidate_verdicts: tuple[str, ...]
    evidence_bundle_requirements: tuple[str, ...]
    scope_evidence_requirements: dict[str, tuple[str, ...]]
    compatibility_packet_fields: tuple[str, ...]
    failure_packet_fields: tuple[str, ...]
    allowed_surfaces: tuple[str, ...]
    prohibited_surfaces: tuple[str, ...]
    hard_blockers: tuple[str, ...]
    failure_codes: tuple[str, ...]
    retry_categories: tuple[str, ...]
    compatibility_boundary_rules: tuple[str, ...]
    future_contract_concepts: tuple[str, ...]
    future_runtime_tests: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


def build_production_compatibility_promotion_review_contract() -> ProductionCompatibilityPromotionReviewContract:
    return ProductionCompatibilityPromotionReviewContract(
        artifact_id=_ARTIFACT_ID,
        scope=_SCOPE,
        depends_on=DEPENDS_ON,
        production_compatibility_promotion_review_contract_defined=True,
        production_compatibility_status_taxonomy_defined=True,
        production_compatibility_verdict_taxonomy_defined=True,
        production_compatibility_packet_fields_defined=True,
        production_compatibility_evidence_requirements_defined=True,
        production_compatibility_blockers_defined=True,
        production_compatibility_failure_packet_semantics_defined=True,
        production_compatibility_future_runtime_tests_documented=True,
        production_authorization_boundary_defined=True,
        production_compatibility_statuses=PRODUCTION_COMPATIBILITY_STATUSES,
        candidate_verdicts=CANDIDATE_VERDICTS,
        evidence_bundle_requirements=EVIDENCE_BUNDLE_REQUIREMENTS,
        scope_evidence_requirements=SCOPE_EVIDENCE_REQUIREMENTS,
        compatibility_packet_fields=COMPATIBILITY_PACKET_FIELDS,
        failure_packet_fields=FAILURE_PACKET_FIELDS,
        allowed_surfaces=ALLOWED_SURFACES,
        prohibited_surfaces=PROHIBITED_SURFACES,
        hard_blockers=HARD_BLOCKERS,
        failure_codes=FAILURE_CODES,
        retry_categories=RETRY_CATEGORIES,
        compatibility_boundary_rules=COMPATIBILITY_BOUNDARY_RULES,
        future_contract_concepts=FUTURE_CONTRACT_CONCEPTS,
        future_runtime_tests=FUTURE_RUNTIME_TESTS,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=_RECOMMENDED_NEXT,
        alternative_next_artifact=_ALTERNATIVE_NEXT,
        final_verdict=_VERDICT,
    )


def validate_production_compatibility_promotion_review_contract(
    contract: ProductionCompatibilityPromotionReviewContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.production_compatibility_promotion_review_contract_defined:
        issues.append("production_compatibility_promotion_review_contract_defined must be true")
    if len(contract.production_compatibility_statuses) < 12:
        issues.append("production_compatibility_statuses incomplete")
    if len(contract.candidate_verdicts) < 6:
        issues.append("candidate_verdicts incomplete")
    forbidden_verdicts = {
        "PRODUCTION_APPROVED",
        "PRODUCTION_SAFE",
        "METHOD_PROMOTED",
        "METHOD_UNBLOCKED",
        "CATALOG_UPDATED",
    }
    for verdict in forbidden_verdicts:
        if verdict in contract.candidate_verdicts:
            issues.append(f"candidate_verdicts must not include {verdict}")
    if "method_promotion_review_report" not in contract.evidence_bundle_requirements:
        issues.append("method_promotion_review_report missing from evidence bundle")
    if "trusted_readout_report" not in contract.evidence_bundle_requirements:
        issues.append("trusted_readout_report missing from evidence bundle")
    if "compatibility_review_id" not in contract.compatibility_packet_fields:
        issues.append("compatibility_packet_fields incomplete")
    if len(contract.hard_blockers) < 10:
        issues.append("hard_blockers incomplete")
    if "PRODUCTION_APPROVAL" not in contract.prohibited_surfaces:
        issues.append("prohibited_surfaces incomplete")
    if "PRODUCTION_COMPATIBILITY_CANDIDATE_REVIEW" not in contract.allowed_surfaces:
        issues.append("allowed_surfaces incomplete")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        if not getattr(contract, key, False):
            issues.append(f"contract positive flag {key} must be {expected}")
    if not contract.production_authorization_boundary_defined:
        issues.append("production_authorization_boundary must be defined")
    return {"valid": not issues, "issues": issues}


def get_production_compatibility_promotion_review_contract_metadata() -> dict[str, Any]:
    contract = build_production_compatibility_promotion_review_contract()
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


def list_production_compatibility_statuses() -> tuple[str, ...]:
    return PRODUCTION_COMPATIBILITY_STATUSES


def list_production_compatibility_verdicts() -> tuple[str, ...]:
    return CANDIDATE_VERDICTS


def list_production_compatibility_evidence_requirements() -> dict[str, tuple[str, ...]]:
    return dict(SCOPE_EVIDENCE_REQUIREMENTS)


def list_production_compatibility_future_tests() -> tuple[str, ...]:
    return FUTURE_RUNTIME_TESTS


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_production_compatibility_promotion_review_contract()
    validation = validate_production_compatibility_promotion_review_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in PRODUCTION_COMPATIBILITY_STATUSES:
        scenarios.append(
            _s(f"compatibility_status_{status}", status in contract.production_compatibility_statuses)
        )
    for verdict in CANDIDATE_VERDICTS:
        scenarios.append(_s(f"candidate_verdict_{verdict}", verdict in contract.candidate_verdicts))
    for req in EVIDENCE_BUNDLE_REQUIREMENTS:
        scenarios.append(_s(f"evidence_bundle_{req}", req in contract.evidence_bundle_requirements))
    for scope, reqs in SCOPE_EVIDENCE_REQUIREMENTS.items():
        scenarios.append(_s(f"scope_evidence_{scope}", scope in contract.scope_evidence_requirements))
        scenarios.append(_s(f"scope_evidence_nonempty_{scope}", len(reqs) > 0))
    for field in COMPATIBILITY_PACKET_FIELDS:
        scenarios.append(
            _s(f"compatibility_packet_field_{field}", field in contract.compatibility_packet_fields)
        )
    for field in FAILURE_PACKET_FIELDS:
        scenarios.append(_s(f"failure_packet_field_{field}", field in contract.failure_packet_fields))
    for surface in ALLOWED_SURFACES:
        scenarios.append(_s(f"allowed_surface_{surface}", surface in contract.allowed_surfaces))
    for surface in PROHIBITED_SURFACES:
        scenarios.append(_s(f"prohibited_surface_{surface}", surface in contract.prohibited_surfaces))
    for blocker in HARD_BLOCKERS:
        scenarios.append(_s(f"hard_blocker_{blocker[:40]}", blocker in contract.hard_blockers))
    for code in FAILURE_CODES:
        scenarios.append(_s(f"failure_code_{code}", code in contract.failure_codes))
    for category in RETRY_CATEGORIES:
        scenarios.append(_s(f"retry_category_{category}", category in contract.retry_categories))
    for rule in COMPATIBILITY_BOUNDARY_RULES:
        scenarios.append(_s(f"boundary_rule_{rule[:40]}", rule in contract.compatibility_boundary_rules))
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
    contract = build_production_compatibility_promotion_review_contract()
    validation = validate_production_compatibility_promotion_review_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "production_compatibility_promotion_review_contract",
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
