"""TRUSTED_READOUT_REPORT_CONTRACT_001 — metadata-only trusted readout report contract."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "TRUSTED_READOUT_REPORT_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "trusted_readout_report_contract_defined_no_runtime_or_report_generation"
_VERDICT = "trusted_readout_report_contract_defined_no_runtime_or_report_generation"
_RECOMMENDED_NEXT = "TRUSTED_READOUT_REPORT_RUNTIME_001"
_ALTERNATIVE_NEXT = "METHOD_PROMOTION_REVIEW_CONTRACT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/TRUSTED_READOUT_REPORT_CONTRACT_001_summary.json"
)

DEPENDS_ON = (
    "CLAIM_AUTHORIZATION_RUNTIME_001",
    "CLAIM_AUTHORIZATION_CONTRACT_001",
    "SRM_BALANCE_READOUT_DIAGNOSTIC_001",
    "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001",
    "ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001",
    "PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001",
    "READOUT_PLAN_RUNTIME_001",
    "READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001",
    "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001",
)

FUTURE_CONTRACT_CONCEPTS = (
    "TrustedReadoutReportContract",
    "TrustedReadoutReportPacket",
    "TrustedReadoutReportSection",
    "TrustedReadoutEvidenceBundle",
    "TrustedReadoutClaimBinding",
    "TrustedReadoutCaveatBinding",
    "TrustedReadoutRedactionPolicy",
    "TrustedReadoutLineageManifest",
    "TrustedReadoutFailurePacket",
    "TrustedReadoutReportConfig",
    "TrustedReadoutReportInput",
    "TrustedReadoutReportBoundaryReport",
)

TRUSTED_REPORT_STATUSES = (
    "TRUSTED_REPORT_READY_FOR_RUNTIME",
    "TRUSTED_REPORT_BLOCKED_BY_CLAIM_AUTHORIZATION",
    "TRUSTED_REPORT_BLOCKED_BY_MISSING_EVIDENCE",
    "TRUSTED_REPORT_BLOCKED_BY_PRODUCTION_CATALOG",
    "TRUSTED_REPORT_BLOCKED_BY_STATISTICAL_PROMOTION",
    "TRUSTED_REPORT_BLOCKED_BY_ASSIGNMENT_INTEGRITY",
    "TRUSTED_REPORT_BLOCKED_BY_SRM_BALANCE",
    "TRUSTED_REPORT_BLOCKED_BY_UNCERTAINTY",
    "TRUSTED_REPORT_BLOCKED_BY_TRUSTED_SURFACE_POLICY",
    "TRUSTED_REPORT_CONTRACT_ONLY",
)

SECTION_STATUSES = (
    "SECTION_ALLOWED",
    "SECTION_ALLOWED_WITH_RESTRICTIONS",
    "SECTION_REDACTED",
    "SECTION_BLOCKED",
    "SECTION_NOT_EVALUATED",
)

REPORT_SECTION_TYPES = (
    "EXECUTIVE_SUMMARY",
    "AUTHORIZED_CLAIMS",
    "RESTRICTED_CLAIMS",
    "BLOCKED_CLAIMS",
    "POINT_ESTIMATE_SUMMARY",
    "UNCERTAINTY_SUMMARY",
    "DIAGNOSTIC_SUMMARY",
    "ASSIGNMENT_INTEGRITY_SUMMARY",
    "RANDOMIZATION_SUMMARY",
    "SRM_BALANCE_SUMMARY",
    "STATISTICAL_PROMOTION_SUMMARY",
    "METHOD_AND_INSTRUMENT_SUMMARY",
    "PRODUCTION_CATALOG_STATUS",
    "CAVEATS_AND_LIMITATIONS",
    "EVIDENCE_TRACE",
    "LINEAGE_AND_PROVENANCE",
    "RECOMMENDATION_SECTION",
    "APPENDIX",
)

EVIDENCE_BUNDLE_REQUIREMENTS = (
    "claim_authorization_report",
    "readout_plan_report",
    "execution_result",
    "execution_artifact_manifest",
    "diagnostics_sensitivity_report",
    "srm_balance_diagnostic_report",
    "assignment_panel_integrity_report",
    "governed_randomization_report",
    "statistical_promotion_report",
    "production_catalog_report",
    "method_suitability_report",
    "did_instrument_contract",
    "evidence_sources",
    "lineage_manifest",
)

SECTION_EVIDENCE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "EXECUTIVE_SUMMARY": ("claim_authorization_report",),
    "AUTHORIZED_CLAIMS": ("claim_authorization_report",),
    "RESTRICTED_CLAIMS": ("claim_authorization_report",),
    "BLOCKED_CLAIMS": ("claim_authorization_report",),
    "POINT_ESTIMATE_SUMMARY": (
        "claim_authorization_report",
        "execution_result",
        "execution_artifact_manifest",
    ),
    "UNCERTAINTY_SUMMARY": (
        "claim_authorization_report",
        "execution_result",
    ),
    "DIAGNOSTIC_SUMMARY": ("diagnostics_sensitivity_report", "claim_authorization_report"),
    "ASSIGNMENT_INTEGRITY_SUMMARY": ("assignment_panel_integrity_report",),
    "RANDOMIZATION_SUMMARY": ("governed_randomization_report",),
    "SRM_BALANCE_SUMMARY": ("srm_balance_diagnostic_report",),
    "STATISTICAL_PROMOTION_SUMMARY": ("statistical_promotion_report",),
    "METHOD_AND_INSTRUMENT_SUMMARY": (
        "method_suitability_report",
        "production_catalog_report",
        "did_instrument_contract",
    ),
    "PRODUCTION_CATALOG_STATUS": ("production_catalog_report", "claim_authorization_report"),
    "CAVEATS_AND_LIMITATIONS": ("claim_authorization_report",),
    "EVIDENCE_TRACE": ("evidence_sources", "lineage_manifest"),
    "LINEAGE_AND_PROVENANCE": ("lineage_manifest",),
    "RECOMMENDATION_SECTION": (
        "claim_authorization_report",
        "trusted_surface_policy",
    ),
    "APPENDIX": ("evidence_sources",),
}

CAVEAT_CODES = (
    "POINT_ESTIMATE_ONLY",
    "NO_UNCERTAINTY",
    "NO_STATISTICAL_SIGNIFICANCE",
    "NO_CONFIDENCE_INTERVAL",
    "NO_CAUSAL_CLAIM",
    "NO_INCREMENTAL_CLAIM",
    "NO_ROI_CLAIM",
    "NO_PRODUCTION_AUTHORIZATION",
    "RESEARCH_OR_REVIEW_ONLY",
    "DIAGNOSTIC_ONLY",
    "METHOD_BLOCKED_FOR_PRODUCTION",
)

REDACTION_RULES = (
    "no_uncertainty_language_without_uncertainty_authorization",
    "no_significance_language_without_significance_authorization",
    "no_causal_language_without_causal_claim_authorization",
    "no_incremental_language_without_incremental_claim_authorization",
    "no_roi_language_without_roi_claim_authorization",
    "no_production_recommendation_without_production_or_trusted_authorization",
    "no_winner_worked_drove_caused_profitable_scale_budget_language_without_matching_claim",
    "executive_summary_limited_to_authorized_or_restricted_claims_and_required_caveats",
    "blocked_claims_shown_as_not_authorized_only",
    "recommendation_section_blocked_without_trusted_surface_policy",
    "uncertainty_summary_redacted_without_governed_uncertainty",
)

CLAIM_BINDING_POLICY_RULES = (
    "each_report_statement_binds_to_claim_authorization_record",
    "each_claim_authorization_binds_to_evidence_ids",
    "missing_claim_authorization_blocks_or_redacts_section",
    "restricted_claims_require_mandatory_caveats_in_section",
    "blocked_claims_may_only_appear_as_not_authorized_summaries",
    "no_statement_without_claim_binding",
)

REPORT_PACKET_FIELDS = (
    "report_id",
    "report_status",
    "report_type",
    "report_scope",
    "experiment_id",
    "design_id",
    "readout_id",
    "generated_from_artifacts",
    "claim_authorization_report_id",
    "sections",
    "redacted_sections",
    "blocked_sections",
    "required_caveats",
    "evidence_bundle",
    "lineage_manifest",
    "provenance_hash",
    "policy_version",
    "failure_packet",
)

SECTION_FIELDS = (
    "section_id",
    "section_type",
    "section_status",
    "required_claim_types",
    "bound_claim_authorization_ids",
    "bound_evidence_ids",
    "allowed_surface",
    "blocked_surface",
    "required_caveats",
    "redaction_reason",
)

FAILURE_PACKET_FIELDS = (
    "failure_code",
    "failure_reason",
    "blocking_sections",
    "blocking_claims",
    "missing_evidence",
    "failed_evidence",
    "required_remediation",
    "retry_category",
)

RETRY_CATEGORIES = (
    "ADD_CLAIM_AUTHORIZATION_REPORT",
    "ADD_REQUIRED_EVIDENCE",
    "ADD_GOVERNED_UNCERTAINTY",
    "ADD_SRM_BALANCE_DIAGNOSTIC",
    "ADD_ASSIGNMENT_INTEGRITY_EVIDENCE",
    "FIX_PRODUCTION_CATALOG_BLOCKER",
    "REQUEST_WEAKER_REPORT_SURFACE",
    "REDACT_UNAUTHORIZED_SECTION",
    "BLOCK_TRUSTED_REPORT",
)

FUTURE_RUNTIME_TESTS = (
    "trusted_report_blocks_without_claim_authorization_report",
    "trusted_report_includes_restricted_point_estimate_only_with_caveats",
    "trusted_report_redacts_uncertainty_section_when_uncertainty_missing",
    "trusted_report_redacts_significance_language_when_p_value_or_ci_missing",
    "trusted_report_blocks_roi_recommendation_without_roi_authorization",
    "trusted_report_binds_every_section_to_claim_authorization_ids",
    "trusted_report_includes_blocked_claims_only_as_not_authorized_summaries",
    "trusted_report_preserves_evidence_trace_and_lineage",
    "trusted_report_deterministic_report_id_and_provenance_hash",
    "trusted_report_never_generates_production_recommendation_without_trusted_authorization",
    "trusted_report_never_generates_final_business_narrative_text",
    "no_fixture_specific_branching",
)

NON_GOALS = (
    "no_trusted_readout_report_runtime",
    "no_trusted_readout_report_generation",
    "no_trusted_readout_handoff_generation",
    "no_authorized_claim_text_generation",
    "no_production_authorization",
    "no_production_readout_authorization",
    "no_estimator_execution",
    "no_inference_execution",
    "no_effect_computation",
    "no_uncertainty_computation",
    "no_p_values_or_confidence_intervals",
    "no_mmm_runtime_calls",
    "no_llm_decisioning",
    "no_method_unblocking",
    "no_production_catalog_loosening",
)

_AUTH_FLAGS = {
    "trusted_readout_report_runtime_implemented": False,
    "trusted_readout_report_generated": False,
    "trusted_readout_handoff_generated": False,
    "authorized_claim_text_generated": False,
    "production_authorization_granted": False,
    "production_readout_authorized": False,
    "causal_claim_authorized": False,
    "incremental_lift_claim_authorized": False,
    "roi_claim_authorized": False,
    "statistical_significance_claim_authorized": False,
    "confidence_interval_claim_authorized": False,
    "method_unblocked": False,
    "production_catalog_unblocked": False,
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
    "trusted_readout_report_contract_defined": True,
    "trusted_report_status_taxonomy_defined": True,
    "trusted_report_section_taxonomy_defined": True,
    "trusted_report_evidence_bundle_requirements_defined": True,
    "trusted_report_claim_binding_policy_defined": True,
    "trusted_report_redaction_policy_defined": True,
    "trusted_report_caveat_policy_defined": True,
    "trusted_report_failure_packet_semantics_defined": True,
    "trusted_report_future_runtime_tests_documented": True,
}


@dataclass(frozen=True)
class TrustedReadoutReportContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    trusted_readout_report_contract_defined: bool
    trusted_report_status_taxonomy_defined: bool
    trusted_report_section_taxonomy_defined: bool
    trusted_report_evidence_bundle_requirements_defined: bool
    trusted_report_claim_binding_policy_defined: bool
    trusted_report_redaction_policy_defined: bool
    trusted_report_caveat_policy_defined: bool
    trusted_report_failure_packet_semantics_defined: bool
    trusted_report_future_runtime_tests_documented: bool
    trusted_report_statuses: tuple[str, ...]
    section_statuses: tuple[str, ...]
    report_section_types: tuple[str, ...]
    evidence_bundle_requirements: tuple[str, ...]
    section_evidence_requirements: dict[str, tuple[str, ...]]
    caveat_codes: tuple[str, ...]
    redaction_rules: tuple[str, ...]
    claim_binding_policy_rules: tuple[str, ...]
    report_packet_fields: tuple[str, ...]
    section_fields: tuple[str, ...]
    failure_packet_fields: tuple[str, ...]
    retry_categories: tuple[str, ...]
    future_contract_concepts: tuple[str, ...]
    future_runtime_tests: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


def build_trusted_readout_report_contract() -> TrustedReadoutReportContract:
    return TrustedReadoutReportContract(
        artifact_id=_ARTIFACT_ID,
        scope=_SCOPE,
        depends_on=DEPENDS_ON,
        trusted_readout_report_contract_defined=True,
        trusted_report_status_taxonomy_defined=True,
        trusted_report_section_taxonomy_defined=True,
        trusted_report_evidence_bundle_requirements_defined=True,
        trusted_report_claim_binding_policy_defined=True,
        trusted_report_redaction_policy_defined=True,
        trusted_report_caveat_policy_defined=True,
        trusted_report_failure_packet_semantics_defined=True,
        trusted_report_future_runtime_tests_documented=True,
        trusted_report_statuses=TRUSTED_REPORT_STATUSES,
        section_statuses=SECTION_STATUSES,
        report_section_types=REPORT_SECTION_TYPES,
        evidence_bundle_requirements=EVIDENCE_BUNDLE_REQUIREMENTS,
        section_evidence_requirements=SECTION_EVIDENCE_REQUIREMENTS,
        caveat_codes=CAVEAT_CODES,
        redaction_rules=REDACTION_RULES,
        claim_binding_policy_rules=CLAIM_BINDING_POLICY_RULES,
        report_packet_fields=REPORT_PACKET_FIELDS,
        section_fields=SECTION_FIELDS,
        failure_packet_fields=FAILURE_PACKET_FIELDS,
        retry_categories=RETRY_CATEGORIES,
        future_contract_concepts=FUTURE_CONTRACT_CONCEPTS,
        future_runtime_tests=FUTURE_RUNTIME_TESTS,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=_RECOMMENDED_NEXT,
        alternative_next_artifact=_ALTERNATIVE_NEXT,
        final_verdict=_VERDICT,
    )


def validate_trusted_readout_report_contract(
    contract: TrustedReadoutReportContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if not contract.trusted_readout_report_contract_defined:
        issues.append("trusted_readout_report_contract_defined must be true")
    if len(contract.trusted_report_statuses) < 10:
        issues.append("trusted_report_statuses incomplete")
    if len(contract.report_section_types) < 18:
        issues.append("report_section_types incomplete")
    if "RECOMMENDATION_SECTION" not in contract.report_section_types:
        issues.append("RECOMMENDATION_SECTION missing")
    if "UNCERTAINTY_SUMMARY" not in contract.report_section_types:
        issues.append("UNCERTAINTY_SUMMARY missing")
    if "claim_authorization_report" not in contract.evidence_bundle_requirements:
        issues.append("claim_authorization_report missing from evidence bundle")
    if "POINT_ESTIMATE_SUMMARY" not in contract.section_evidence_requirements:
        issues.append("section evidence requirements incomplete")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        if not getattr(contract, key, False):
            issues.append(f"contract positive flag {key} must be {expected}")
    if not contract.trusted_report_claim_binding_policy_defined:
        issues.append("claim binding policy must be defined")
    if not contract.trusted_report_redaction_policy_defined:
        issues.append("redaction policy must be defined")
    return {"valid": not issues, "issues": issues}


def get_trusted_readout_report_contract_metadata() -> dict[str, Any]:
    contract = build_trusted_readout_report_contract()
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


def list_trusted_readout_report_sections() -> tuple[str, ...]:
    return REPORT_SECTION_TYPES


def list_trusted_readout_report_statuses() -> tuple[str, ...]:
    return TRUSTED_REPORT_STATUSES


def list_trusted_readout_report_evidence_requirements() -> dict[str, tuple[str, ...]]:
    return dict(SECTION_EVIDENCE_REQUIREMENTS)


def list_trusted_readout_report_future_tests() -> tuple[str, ...]:
    return FUTURE_RUNTIME_TESTS


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_trusted_readout_report_contract()
    validation = validate_trusted_readout_report_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in TRUSTED_REPORT_STATUSES:
        scenarios.append(_s(f"trusted_report_status_{status}", status in contract.trusted_report_statuses))
    for status in SECTION_STATUSES:
        scenarios.append(_s(f"section_status_{status}", status in contract.section_statuses))
    for section in REPORT_SECTION_TYPES:
        scenarios.append(_s(f"report_section_{section}", section in contract.report_section_types))
    for req in EVIDENCE_BUNDLE_REQUIREMENTS:
        scenarios.append(_s(f"evidence_bundle_{req}", req in contract.evidence_bundle_requirements))
    for section, reqs in SECTION_EVIDENCE_REQUIREMENTS.items():
        scenarios.append(_s(f"section_evidence_{section}", section in contract.section_evidence_requirements))
        scenarios.append(_s(f"section_evidence_nonempty_{section}", len(reqs) > 0))
    for code in CAVEAT_CODES:
        scenarios.append(_s(f"caveat_code_{code}", code in contract.caveat_codes))
    for rule in REDACTION_RULES:
        scenarios.append(_s(f"redaction_rule_{rule[:40]}", rule in contract.redaction_rules))
    for rule in CLAIM_BINDING_POLICY_RULES:
        scenarios.append(_s(f"claim_binding_{rule[:40]}", rule in contract.claim_binding_policy_rules))
    for field in REPORT_PACKET_FIELDS:
        scenarios.append(_s(f"report_packet_field_{field}", field in contract.report_packet_fields))
    for field in SECTION_FIELDS:
        scenarios.append(_s(f"section_field_{field}", field in contract.section_fields))
    for field in FAILURE_PACKET_FIELDS:
        scenarios.append(_s(f"failure_packet_field_{field}", field in contract.failure_packet_fields))
    for category in RETRY_CATEGORIES:
        scenarios.append(_s(f"retry_category_{category}", category in contract.retry_categories))
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
    contract = build_trusted_readout_report_contract()
    validation = validate_trusted_readout_report_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "trusted_readout_report_contract",
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
