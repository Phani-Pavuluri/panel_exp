"""TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001 — uncertainty candidate review contract."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

_ARTIFACT_ID = "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "tbrridge_uncertainty_candidate_review_contract_defined_no_runtime_or_uncertainty_approval"
_VERDICT = "tbrridge_uncertainty_candidate_review_contract_defined_no_runtime_or_uncertainty_approval"
_RECOMMENDED_NEXT = "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001"
_ALTERNATIVE_NEXT = "AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001"
_DEFERRED = "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001_summary.json"
)

DEPENDS_ON = (
    "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001",
    "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001",
    "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001",
    "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001",
)

METHOD_ID = "TBRRidge"
INSTRUMENT_ID = "TBRRidge_Kfold"
ESTIMATOR_FAMILY = "TBRRidge"
INFERENCE_FAMILY = "KFold"
CURRENT_READINESS_STAGE = "STAGE_2_DIAGNOSTIC_ONLY"
CANDIDATE_REVIEW_TARGET_STAGE = "STAGE_4_UNCERTAINTY_CANDIDATE"

REVIEW_STATUSES = (
    "UNCERTAINTY_CANDIDATE_REVIEW_NOT_EVALUATED",
    "UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
    "UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS",
    "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN",
    "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_LEAKAGE_DIAGNOSTIC",
    "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_PLACEBO_CALIBRATION",
    "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_COVERAGE_VALIDATION",
    "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS",
    "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH",
    "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_PRODUCTION_CATALOG_STATUS",
    "UNCERTAINTY_CANDIDATE_REVIEW_REQUIRES_METHOD_REVIEW",
    "UNCERTAINTY_CANDIDATE_REVIEW_DEFERRED",
)

REVIEW_RISK_TYPES = (
    "MISSING_EVIDENCE_CHAIN",
    "LEAKAGE_DIAGNOSTIC_BLOCKING",
    "PLACEBO_CALIBRATION_BLOCKING",
    "COVERAGE_VALIDATION_BLOCKING",
    "INTERVAL_SEMANTICS_INCOMPLETE",
    "NULL_CONTROL_EVIDENCE_INCOMPLETE",
    "POSITIVE_CONTROL_EVIDENCE_INCOMPLETE",
    "REGIME_SENSITIVITY_INCOMPLETE",
    "REGULARIZATION_SENSITIVITY_INCOMPLETE",
    "DONOR_POOL_SENSITIVITY_INCOMPLETE",
    "OUTLIER_SENSITIVITY_INCOMPLETE",
    "METRIC_ESTIMAND_MISMATCH",
    "AGGREGATE_POOLED_SURFACE_UNSUPPORTED",
    "CLAIM_AUTHORIZATION_BOUNDARY_MISSING",
    "STATISTICAL_PROMOTION_EVIDENCE_INCOMPLETE",
    "PRODUCTION_CATALOG_BLOCKED",
    "METHOD_PROMOTION_BOUNDARY_MISSING",
)

REQUIRED_EVIDENCE = (
    "false_confidence_audit_report",
    "kfold_leakage_diagnostic_report",
    "placebo_calibration_diagnostic_report",
    "coverage_validation_report",
    "interval_semantics_report",
    "null_control_evidence_report",
    "positive_control_evidence_report",
    "regime_sensitivity_report",
    "regularization_sensitivity_report",
    "donor_pool_sensitivity_report",
    "outlier_sensitivity_report",
    "metric_estimand_alignment_report",
    "aggregate_pooled_surface_blocker_report",
    "statistical_promotion_threshold_report",
    "production_catalog_status_report",
    "claim_authorization_boundary_report",
    "method_promotion_boundary_report",
    "lineage_provenance_manifest",
)

EVIDENCE_CHAIN_REQUIREMENTS = (
    "false_confidence_audit_report_required",
    "kfold_leakage_diagnostic_report_required",
    "placebo_calibration_diagnostic_report_required",
    "coverage_validation_report_required",
    "leakage_diagnostic_must_be_non_blocking_or_restricted",
    "placebo_calibration_must_be_non_blocking_or_restricted",
    "coverage_validation_must_be_diagnostic_review_ready_or_restricted",
    "interval_semantics_must_be_documented",
    "null_and_positive_control_evidence_required",
    "regime_sensitivity_evidence_required",
    "metric_estimand_alignment_required",
    "production_catalog_blocked_for_production_surfaces",
    "claim_and_promotion_boundaries_required",
)

REVIEW_PACKET_FIELDS = (
    "review_id",
    "review_status",
    "method_id",
    "instrument_id",
    "estimator_family",
    "inference_family",
    "current_readiness_stage",
    "candidate_review_target_stage",
    "evidence_chain_summary",
    "evidence_components_reviewed",
    "required_evidence",
    "missing_evidence",
    "detected_review_risks",
    "blockers",
    "restrictions",
    "allowed_surfaces",
    "prohibited_surfaces",
    "failure_packet",
    "recommended_next_action",
    "lineage_manifest",
    "provenance_hash",
    "policy_version",
)

ALLOWED_SURFACES = (
    "DIAGNOSTIC_ONLY",
    "RESEARCH_OR_REVIEW_ONLY",
    "UNCERTAINTY_CANDIDATE_REVIEW_READINESS_SUMMARY",
    "EVIDENCE_SUFFICIENCY_SUMMARY",
    "REMAINING_BLOCKERS_SUMMARY",
    "METHOD_REVIEW_INPUT_PACKET_DESCRIPTION",
)

PROHIBITED_SURFACES = (
    "UNCERTAINTY_APPROVAL_NOTICE",
    "CONFIDENCE_INTERVAL_CLAIM",
    "P_VALUE_CLAIM",
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "COVERAGE_APPROVAL_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "ROI_CLAIM",
    "PRODUCTION_READOUT",
    "METHOD_PROMOTION_NOTICE",
    "PRODUCTION_COMPATIBILITY_NOTICE",
    "CATALOG_UNBLOCK_NOTICE",
)

FAILURE_PACKET_FIELDS = (
    "failure_code",
    "failure_reason",
    "detected_review_risks",
    "missing_evidence",
    "required_remediation",
    "retry_category",
)

FAILURE_CODES = (
    "MISSING_FALSE_CONFIDENCE_AUDIT",
    "MISSING_KFOLD_LEAKAGE_DIAGNOSTIC",
    "MISSING_PLACEBO_CALIBRATION_DIAGNOSTIC",
    "MISSING_COVERAGE_VALIDATION_REPORT",
    "LEAKAGE_DIAGNOSTIC_BLOCKING",
    "PLACEBO_CALIBRATION_BLOCKING",
    "COVERAGE_VALIDATION_BLOCKING",
    "INTERVAL_SEMANTICS_INCOMPLETE",
    "NULL_CONTROL_EVIDENCE_INCOMPLETE",
    "POSITIVE_CONTROL_EVIDENCE_INCOMPLETE",
    "REGIME_SENSITIVITY_INCOMPLETE",
    "METRIC_ESTIMAND_MISMATCH",
    "PRODUCTION_CATALOG_BLOCKED",
    "UNCERTAINTY_APPROVAL_SURFACE_BLOCKED",
)

RETRY_CATEGORIES = (
    "ADD_FALSE_CONFIDENCE_AUDIT",
    "ADD_KFOLD_LEAKAGE_DIAGNOSTIC",
    "ADD_PLACEBO_CALIBRATION_DIAGNOSTIC",
    "ADD_COVERAGE_VALIDATION_REPORT",
    "ADD_INTERVAL_SEMANTICS_REPORT",
    "ADD_NULL_CONTROL_EVIDENCE",
    "ADD_POSITIVE_CONTROL_EVIDENCE",
    "ADD_REGIME_SENSITIVITY_EVIDENCE",
    "ADD_METRIC_ESTIMAND_ALIGNMENT",
    "RESTRICT_TO_DIAGNOSTIC_ONLY",
    "BLOCK_UNCERTAINTY_APPROVAL_SURFACE",
    "REQUIRE_METHOD_REVIEW",
    "DEFER_CANDIDATE_REVIEW",
)

FUTURE_RUNTIME_TESTS = (
    "blocks_without_false_confidence_audit_report",
    "blocks_without_kfold_leakage_diagnostic_report",
    "blocks_when_kfold_leakage_diagnostic_is_blocking",
    "blocks_without_placebo_calibration_diagnostic_report",
    "blocks_when_placebo_calibration_diagnostic_is_blocking",
    "blocks_without_coverage_validation_report",
    "blocks_when_coverage_validation_is_blocking",
    "blocks_without_interval_semantics_evidence",
    "blocks_without_null_control_evidence",
    "blocks_without_positive_control_evidence",
    "blocks_without_regime_sensitivity_evidence",
    "blocks_on_metric_estimand_mismatch",
    "blocks_when_production_catalog_remains_blocked_for_production_surfaces",
    "permits_restricted_review_readiness_summary_when_evidence_chain_present_and_non_blocking",
    "blocks_uncertainty_approval_ci_p_value_significance_lift_roi_production_promotion_compatibility_catalog_surfaces",
    "emits_deterministic_review_id_and_provenance_hash",
    "all_forbidden_computation_authorization_flags_false",
)

_AUTH_FLAGS = {
    "uncertainty_candidate_review_runtime_implemented": False,
    "uncertainty_candidate_approved": False,
    "uncertainty_authorized": False,
    "confidence_interval_authorized": False,
    "p_value_authorized": False,
    "statistical_significance_authorized": False,
    "coverage_approval_authorized": False,
    "method_promotion_authorized": False,
    "production_compatibility_authorized": False,
    "catalog_unblock_authorized": False,
    "coverage_computed": False,
    "interval_computed": False,
    "kfold_inference_implemented": False,
    "placebo_inference_implemented": False,
    "estimator_implemented": False,
    "inference_implemented": False,
    "bootstrap_inference_implemented": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "effect_estimate_computed_new": False,
    "lift_computed_new": False,
    "roi_computed_new": False,
    "method_promoted": False,
    "method_unblocked": False,
    "production_catalog_unblocked": False,
    "production_authorization_granted": False,
    "production_readout_authorized": False,
    "mmm_runtime_calls_implemented": False,
    "llm_decisioning_authorized": False,
}

CONTRACT_POSITIVE_FLAGS = {
    "uncertainty_candidate_review_contract_defined": True,
    "review_statuses_defined": True,
    "review_risk_taxonomy_defined": True,
    "required_evidence_defined": True,
    "evidence_chain_requirements_defined": True,
    "failure_packet_semantics_defined": True,
    "future_runtime_tests_documented": True,
}

_LEAKAGE_BLOCKING_STATUSES = frozenset(
    {
        "KFOLD_LEAKAGE_BLOCKED_BY_UNSUPPORTED_GEOMETRY",
        "KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE",
        "KFOLD_LEAKAGE_BLOCKED_BY_FOLD_OVERLAP",
        "KFOLD_LEAKAGE_BLOCKED_BY_TREATED_CONTROL_CONTAMINATION",
        "KFOLD_LEAKAGE_BLOCKED_BY_SMALL_SAMPLE_GEOMETRY",
        "KFOLD_LEAKAGE_BLOCKED_BY_MISSING_EVIDENCE",
        "KFOLD_LEAKAGE_REQUIRES_METHOD_REVIEW",
    }
)

_PLACEBO_BLOCKING_STATUSES = frozenset(
    {
        "PLACEBO_CALIBRATION_BLOCKED_BY_MISSING_PLACEBO_MANIFEST",
        "PLACEBO_CALIBRATION_BLOCKED_BY_INVALID_NULL_CONSTRUCTION",
        "PLACEBO_CALIBRATION_BLOCKED_BY_INSUFFICIENT_PLACEBOS",
        "PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION",
        "PLACEBO_CALIBRATION_BLOCKED_BY_DIRECTIONAL_INSTABILITY",
        "PLACEBO_CALIBRATION_BLOCKED_BY_OUTLIER_INFLUENCE",
        "PLACEBO_CALIBRATION_REQUIRES_METHOD_REVIEW",
    }
)

_COVERAGE_BLOCKING_STATUSES = frozenset(
    {
        "COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK",
        "COVERAGE_VALIDATION_BLOCKED_BY_PLACEBO_MISCALIBRATION",
        "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS",
        "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_SIMULATION_DESIGN",
        "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_NULL_CONTROL",
        "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_POSITIVE_CONTROL",
        "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_REGIME_COVERAGE",
        "COVERAGE_VALIDATION_REQUIRES_METHOD_REVIEW",
    }
)

_COVERAGE_READY_STATUSES = frozenset(
    {
        "COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW",
        "COVERAGE_VALIDATION_READY_WITH_RESTRICTIONS",
    }
)

_CORE_CHAIN_EVIDENCE = (
    "false_confidence_audit_report",
    "kfold_leakage_diagnostic_report",
    "placebo_calibration_diagnostic_report",
    "coverage_validation_report",
)


class UncertaintyCandidateReviewStatus(str, Enum):
    UNCERTAINTY_CANDIDATE_REVIEW_NOT_EVALUATED = "UNCERTAINTY_CANDIDATE_REVIEW_NOT_EVALUATED"
    UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW = (
        "UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW"
    )
    UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS = (
        "UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS"
    )
    UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN = (
        "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN"
    )
    UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_LEAKAGE_DIAGNOSTIC = (
        "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_LEAKAGE_DIAGNOSTIC"
    )
    UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_PLACEBO_CALIBRATION = (
        "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_PLACEBO_CALIBRATION"
    )
    UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_COVERAGE_VALIDATION = (
        "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_COVERAGE_VALIDATION"
    )
    UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS = (
        "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS"
    )
    UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH = (
        "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH"
    )
    UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_PRODUCTION_CATALOG_STATUS = (
        "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_PRODUCTION_CATALOG_STATUS"
    )
    UNCERTAINTY_CANDIDATE_REVIEW_REQUIRES_METHOD_REVIEW = (
        "UNCERTAINTY_CANDIDATE_REVIEW_REQUIRES_METHOD_REVIEW"
    )
    UNCERTAINTY_CANDIDATE_REVIEW_DEFERRED = "UNCERTAINTY_CANDIDATE_REVIEW_DEFERRED"


class ReviewRiskType(str, Enum):
    MISSING_EVIDENCE_CHAIN = "MISSING_EVIDENCE_CHAIN"
    LEAKAGE_DIAGNOSTIC_BLOCKING = "LEAKAGE_DIAGNOSTIC_BLOCKING"
    PLACEBO_CALIBRATION_BLOCKING = "PLACEBO_CALIBRATION_BLOCKING"
    COVERAGE_VALIDATION_BLOCKING = "COVERAGE_VALIDATION_BLOCKING"
    INTERVAL_SEMANTICS_INCOMPLETE = "INTERVAL_SEMANTICS_INCOMPLETE"
    NULL_CONTROL_EVIDENCE_INCOMPLETE = "NULL_CONTROL_EVIDENCE_INCOMPLETE"
    POSITIVE_CONTROL_EVIDENCE_INCOMPLETE = "POSITIVE_CONTROL_EVIDENCE_INCOMPLETE"
    REGIME_SENSITIVITY_INCOMPLETE = "REGIME_SENSITIVITY_INCOMPLETE"
    REGULARIZATION_SENSITIVITY_INCOMPLETE = "REGULARIZATION_SENSITIVITY_INCOMPLETE"
    DONOR_POOL_SENSITIVITY_INCOMPLETE = "DONOR_POOL_SENSITIVITY_INCOMPLETE"
    OUTLIER_SENSITIVITY_INCOMPLETE = "OUTLIER_SENSITIVITY_INCOMPLETE"
    METRIC_ESTIMAND_MISMATCH = "METRIC_ESTIMAND_MISMATCH"
    AGGREGATE_POOLED_SURFACE_UNSUPPORTED = "AGGREGATE_POOLED_SURFACE_UNSUPPORTED"
    CLAIM_AUTHORIZATION_BOUNDARY_MISSING = "CLAIM_AUTHORIZATION_BOUNDARY_MISSING"
    STATISTICAL_PROMOTION_EVIDENCE_INCOMPLETE = "STATISTICAL_PROMOTION_EVIDENCE_INCOMPLETE"
    PRODUCTION_CATALOG_BLOCKED = "PRODUCTION_CATALOG_BLOCKED"
    METHOD_PROMOTION_BOUNDARY_MISSING = "METHOD_PROMOTION_BOUNDARY_MISSING"


@dataclass(frozen=True)
class TbrridgeUncertaintyCandidateReviewContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    uncertainty_candidate_review_contract_defined: bool
    review_statuses_defined: bool
    review_risk_taxonomy_defined: bool
    required_evidence_defined: bool
    evidence_chain_requirements_defined: bool
    failure_packet_semantics_defined: bool
    future_runtime_tests_documented: bool
    review_statuses: tuple[str, ...]
    review_risk_types: tuple[str, ...]
    required_evidence: tuple[str, ...]
    evidence_chain_requirements: tuple[str, ...]
    review_packet_fields: tuple[str, ...]
    allowed_surfaces: tuple[str, ...]
    prohibited_surfaces: tuple[str, ...]
    failure_packet_fields: tuple[str, ...]
    failure_codes: tuple[str, ...]
    retry_categories: tuple[str, ...]
    future_runtime_tests: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    deferred_artifact: str
    final_verdict: str


@dataclass(frozen=True)
class UncertaintyCandidateReviewEvaluationResult:
    review_status: str
    authorized_for_review_summary: bool
    detected_review_risks: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    failure_code: str | None
    failure_reason: str | None
    retry_category: str | None
    recommended_next_action: str | None

    def to_failure_packet(self) -> dict[str, Any] | None:
        if self.failure_code is None:
            return None
        return {
            "failure_code": self.failure_code,
            "failure_reason": self.failure_reason,
            "detected_review_risks": list(self.detected_review_risks),
            "missing_evidence": list(self.missing_evidence),
            "required_remediation": self.retry_category,
            "retry_category": self.retry_category,
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_tbrridge_uncertainty_candidate_review_contract() -> TbrridgeUncertaintyCandidateReviewContract:
    return TbrridgeUncertaintyCandidateReviewContract(
        artifact_id=_ARTIFACT_ID,
        scope=_SCOPE,
        depends_on=DEPENDS_ON,
        uncertainty_candidate_review_contract_defined=True,
        review_statuses_defined=True,
        review_risk_taxonomy_defined=True,
        required_evidence_defined=True,
        evidence_chain_requirements_defined=True,
        failure_packet_semantics_defined=True,
        future_runtime_tests_documented=True,
        review_statuses=REVIEW_STATUSES,
        review_risk_types=REVIEW_RISK_TYPES,
        required_evidence=REQUIRED_EVIDENCE,
        evidence_chain_requirements=EVIDENCE_CHAIN_REQUIREMENTS,
        review_packet_fields=REVIEW_PACKET_FIELDS,
        allowed_surfaces=ALLOWED_SURFACES,
        prohibited_surfaces=PROHIBITED_SURFACES,
        failure_packet_fields=FAILURE_PACKET_FIELDS,
        failure_codes=FAILURE_CODES,
        retry_categories=RETRY_CATEGORIES,
        future_runtime_tests=FUTURE_RUNTIME_TESTS,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=_RECOMMENDED_NEXT,
        alternative_next_artifact=_ALTERNATIVE_NEXT,
        deferred_artifact=_DEFERRED,
        final_verdict=_VERDICT,
    )


def _missing_evidence(required: tuple[str, ...], evidence: Mapping[str, bool]) -> tuple[str, ...]:
    return tuple(req for req in required if not evidence.get(req, False))


def evaluate_uncertainty_candidate_review(
    *,
    evidence: Mapping[str, bool] | None = None,
    detected_risks: tuple[str, ...] | None = None,
    requested_surface: str | None = None,
    leakage_diagnostic_status: str | None = None,
    placebo_calibration_status: str | None = None,
    coverage_validation_status: str | None = None,
    production_catalog_blocked: bool = True,
    metric_estimand_mismatch: bool = False,
    deferred: bool = False,
) -> UncertaintyCandidateReviewEvaluationResult:
    """Contract gate: evaluate uncertainty-candidate review readiness from evidence flags."""
    ev = dict(evidence or {})
    detected = tuple(detected_risks or ())
    surface = requested_surface or "UNCERTAINTY_CANDIDATE_REVIEW_READINESS_SUMMARY"

    if deferred:
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_DEFERRED.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected,
            missing_evidence=(),
            failure_code=None,
            failure_reason="Candidate review explicitly deferred",
            retry_category="DEFER_CANDIDATE_REVIEW",
            recommended_next_action="DEFER_CANDIDATE_REVIEW",
        )

    if surface in PROHIBITED_SURFACES:
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_REQUIRES_METHOD_REVIEW.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected,
            missing_evidence=(),
            failure_code="UNCERTAINTY_APPROVAL_SURFACE_BLOCKED",
            failure_reason="Uncertainty approval/CI/p-value/significance/coverage/lift/ROI/production/promotion surfaces blocked",
            retry_category="BLOCK_UNCERTAINTY_APPROVAL_SURFACE",
            recommended_next_action="BLOCK_UNCERTAINTY_APPROVAL_SURFACE",
        )

    if surface in ("PRODUCTION_READOUT", "CATALOG_UNBLOCK_NOTICE") and production_catalog_blocked:
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_PRODUCTION_CATALOG_STATUS.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected + ("PRODUCTION_CATALOG_BLOCKED",),
            missing_evidence=(),
            failure_code="PRODUCTION_CATALOG_BLOCKED",
            failure_reason="Production catalog remains blocked for TBRRidge KFold",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
            recommended_next_action="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    if not ev.get("false_confidence_audit_report"):
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected + ("MISSING_EVIDENCE_CHAIN",),
            missing_evidence=("false_confidence_audit_report",),
            failure_code="MISSING_FALSE_CONFIDENCE_AUDIT",
            failure_reason="False-confidence audit report required for candidate review",
            retry_category="ADD_FALSE_CONFIDENCE_AUDIT",
            recommended_next_action="ADD_FALSE_CONFIDENCE_AUDIT",
        )

    if not ev.get("kfold_leakage_diagnostic_report"):
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected + ("MISSING_EVIDENCE_CHAIN",),
            missing_evidence=("kfold_leakage_diagnostic_report",),
            failure_code="MISSING_KFOLD_LEAKAGE_DIAGNOSTIC",
            failure_reason="KFold leakage diagnostic report required for candidate review",
            retry_category="ADD_KFOLD_LEAKAGE_DIAGNOSTIC",
            recommended_next_action="ADD_KFOLD_LEAKAGE_DIAGNOSTIC",
        )

    if leakage_diagnostic_status in _LEAKAGE_BLOCKING_STATUSES:
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_LEAKAGE_DIAGNOSTIC.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected + ("LEAKAGE_DIAGNOSTIC_BLOCKING",),
            missing_evidence=(),
            failure_code="LEAKAGE_DIAGNOSTIC_BLOCKING",
            failure_reason=f"Leakage diagnostic blocking: {leakage_diagnostic_status}",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
            recommended_next_action="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    if not ev.get("placebo_calibration_diagnostic_report"):
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected + ("MISSING_EVIDENCE_CHAIN",),
            missing_evidence=("placebo_calibration_diagnostic_report",),
            failure_code="MISSING_PLACEBO_CALIBRATION_DIAGNOSTIC",
            failure_reason="Placebo calibration diagnostic report required for candidate review",
            retry_category="ADD_PLACEBO_CALIBRATION_DIAGNOSTIC",
            recommended_next_action="ADD_PLACEBO_CALIBRATION_DIAGNOSTIC",
        )

    if placebo_calibration_status in _PLACEBO_BLOCKING_STATUSES:
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_PLACEBO_CALIBRATION.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected + ("PLACEBO_CALIBRATION_BLOCKING",),
            missing_evidence=(),
            failure_code="PLACEBO_CALIBRATION_BLOCKING",
            failure_reason=f"Placebo calibration blocking: {placebo_calibration_status}",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
            recommended_next_action="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    if not ev.get("coverage_validation_report"):
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected + ("MISSING_EVIDENCE_CHAIN",),
            missing_evidence=("coverage_validation_report",),
            failure_code="MISSING_COVERAGE_VALIDATION_REPORT",
            failure_reason="Coverage validation report required for candidate review",
            retry_category="ADD_COVERAGE_VALIDATION_REPORT",
            recommended_next_action="ADD_COVERAGE_VALIDATION_REPORT",
        )

    if coverage_validation_status in _COVERAGE_BLOCKING_STATUSES:
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_COVERAGE_VALIDATION.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected + ("COVERAGE_VALIDATION_BLOCKING",),
            missing_evidence=(),
            failure_code="COVERAGE_VALIDATION_BLOCKING",
            failure_reason=f"Coverage validation blocking: {coverage_validation_status}",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
            recommended_next_action="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    if not ev.get("interval_semantics_report"):
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected + ("INTERVAL_SEMANTICS_INCOMPLETE",),
            missing_evidence=("interval_semantics_report",),
            failure_code="INTERVAL_SEMANTICS_INCOMPLETE",
            failure_reason="Interval semantics evidence required for candidate review",
            retry_category="ADD_INTERVAL_SEMANTICS_REPORT",
            recommended_next_action="ADD_INTERVAL_SEMANTICS_REPORT",
        )

    if "INTERVAL_SEMANTICS_INCOMPLETE" in detected:
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected,
            missing_evidence=(),
            failure_code="INTERVAL_SEMANTICS_INCOMPLETE",
            failure_reason="Interval semantics incomplete for TBRRidge KFold",
            retry_category="ADD_INTERVAL_SEMANTICS_REPORT",
            recommended_next_action="ADD_INTERVAL_SEMANTICS_REPORT",
        )

    if not ev.get("null_control_evidence_report"):
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected + ("NULL_CONTROL_EVIDENCE_INCOMPLETE",),
            missing_evidence=("null_control_evidence_report",),
            failure_code="NULL_CONTROL_EVIDENCE_INCOMPLETE",
            failure_reason="Null-control evidence required for candidate review",
            retry_category="ADD_NULL_CONTROL_EVIDENCE",
            recommended_next_action="ADD_NULL_CONTROL_EVIDENCE",
        )

    if not ev.get("positive_control_evidence_report"):
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected + ("POSITIVE_CONTROL_EVIDENCE_INCOMPLETE",),
            missing_evidence=("positive_control_evidence_report",),
            failure_code="POSITIVE_CONTROL_EVIDENCE_INCOMPLETE",
            failure_reason="Positive-control evidence required for candidate review",
            retry_category="ADD_POSITIVE_CONTROL_EVIDENCE",
            recommended_next_action="ADD_POSITIVE_CONTROL_EVIDENCE",
        )

    if not ev.get("regime_sensitivity_report"):
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected + ("REGIME_SENSITIVITY_INCOMPLETE",),
            missing_evidence=("regime_sensitivity_report",),
            failure_code="REGIME_SENSITIVITY_INCOMPLETE",
            failure_reason="Regime sensitivity evidence required for candidate review",
            retry_category="ADD_REGIME_SENSITIVITY_EVIDENCE",
            recommended_next_action="ADD_REGIME_SENSITIVITY_EVIDENCE",
        )

    if metric_estimand_mismatch or "METRIC_ESTIMAND_MISMATCH" in detected:
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH.value,
            authorized_for_review_summary=False,
            detected_review_risks=detected + ("METRIC_ESTIMAND_MISMATCH",),
            missing_evidence=(),
            failure_code="METRIC_ESTIMAND_MISMATCH",
            failure_reason="Metric/estimand mismatch blocks candidate review",
            retry_category="ADD_METRIC_ESTIMAND_ALIGNMENT",
            recommended_next_action="ADD_METRIC_ESTIMAND_ALIGNMENT",
        )

    # Optional boundary reports — flag risks but may proceed with restrictions
    optional_missing = _missing_evidence(
        (
            "regularization_sensitivity_report",
            "donor_pool_sensitivity_report",
            "outlier_sensitivity_report",
            "metric_estimand_alignment_report",
            "aggregate_pooled_surface_blocker_report",
            "statistical_promotion_threshold_report",
            "production_catalog_status_report",
            "claim_authorization_boundary_report",
            "method_promotion_boundary_report",
        ),
        ev,
    )
    risk_flags = list(detected)
    for item, risk in (
        ("regularization_sensitivity_report", "REGULARIZATION_SENSITIVITY_INCOMPLETE"),
        ("donor_pool_sensitivity_report", "DONOR_POOL_SENSITIVITY_INCOMPLETE"),
        ("outlier_sensitivity_report", "OUTLIER_SENSITIVITY_INCOMPLETE"),
        ("claim_authorization_boundary_report", "CLAIM_AUTHORIZATION_BOUNDARY_MISSING"),
        ("method_promotion_boundary_report", "METHOD_PROMOTION_BOUNDARY_MISSING"),
        ("statistical_promotion_threshold_report", "STATISTICAL_PROMOTION_EVIDENCE_INCOMPLETE"),
    ):
        if item in optional_missing and risk not in risk_flags:
            risk_flags.append(risk)
    if production_catalog_blocked and "PRODUCTION_CATALOG_BLOCKED" not in risk_flags:
        risk_flags.append("PRODUCTION_CATALOG_BLOCKED")
    detected = tuple(risk_flags)

    if coverage_validation_status == "COVERAGE_VALIDATION_READY_WITH_RESTRICTIONS" or optional_missing:
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS.value,
            authorized_for_review_summary=True,
            detected_review_risks=detected,
            missing_evidence=optional_missing,
            failure_code=None,
            failure_reason=None,
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
            recommended_next_action="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    if coverage_validation_status in _COVERAGE_READY_STATUSES:
        return UncertaintyCandidateReviewEvaluationResult(
            review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW.value,
            authorized_for_review_summary=True,
            detected_review_risks=detected,
            missing_evidence=optional_missing,
            failure_code=None,
            failure_reason=None,
            retry_category=None,
            recommended_next_action="PROCEED_TO_RESTRICTED_REVIEW_SUMMARY",
        )

    return UncertaintyCandidateReviewEvaluationResult(
        review_status=UncertaintyCandidateReviewStatus.UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_COVERAGE_VALIDATION.value,
        authorized_for_review_summary=False,
        detected_review_risks=detected + ("COVERAGE_VALIDATION_BLOCKING",),
        missing_evidence=(),
        failure_code="COVERAGE_VALIDATION_BLOCKING",
        failure_reason="Coverage validation not diagnostic-review-ready",
        retry_category="ADD_COVERAGE_VALIDATION_REPORT",
        recommended_next_action="ADD_COVERAGE_VALIDATION_REPORT",
    )


def validate_tbrridge_uncertainty_candidate_review_contract(
    contract: TbrridgeUncertaintyCandidateReviewContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if len(contract.review_statuses) < 10:
        issues.append("review_statuses incomplete")
    if "LEAKAGE_DIAGNOSTIC_BLOCKING" not in contract.review_risk_types:
        issues.append("review_risk_types incomplete")
    if "false_confidence_audit_report" not in contract.required_evidence:
        issues.append("required_evidence incomplete")
    if "UNCERTAINTY_APPROVAL_NOTICE" not in contract.prohibited_surfaces:
        issues.append("prohibited_surfaces incomplete")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        if not getattr(contract, key, False):
            issues.append(f"contract positive flag {key} must be {expected}")
    return {"valid": not issues, "issues": issues}


def get_tbrridge_uncertainty_candidate_review_contract_metadata() -> dict[str, Any]:
    contract = build_tbrridge_uncertainty_candidate_review_contract()
    return {
        "artifact_id": contract.artifact_id,
        "artifact_version": _ARTIFACT_VERSION,
        "scope": contract.scope,
        "depends_on": list(contract.depends_on),
        "final_verdict": contract.final_verdict,
        "recommended_next_artifact": contract.recommended_next_artifact,
        "alternative_next_artifact": contract.alternative_next_artifact,
        "deferred_artifact": contract.deferred_artifact,
        **CONTRACT_POSITIVE_FLAGS,
        **contract.authorization_flags,
    }


def list_review_statuses() -> tuple[str, ...]:
    return REVIEW_STATUSES


def list_review_risk_types() -> tuple[str, ...]:
    return REVIEW_RISK_TYPES


def list_future_runtime_tests() -> tuple[str, ...]:
    return FUTURE_RUNTIME_TESTS


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_tbrridge_uncertainty_candidate_review_contract()
    validation = validate_tbrridge_uncertainty_candidate_review_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in REVIEW_STATUSES:
        scenarios.append(_s(f"status_{status}", status in contract.review_statuses))
    for risk in REVIEW_RISK_TYPES:
        scenarios.append(_s(f"risk_{risk}", risk in contract.review_risk_types))

    full_evidence = {req: True for req in REQUIRED_EVIDENCE}
    ready = evaluate_uncertainty_candidate_review(
        evidence=full_evidence,
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
        coverage_validation_status="COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW",
    )
    scenarios.append(_s("ready_for_restricted_review", ready.authorized_for_review_summary))

    blocked_approval = evaluate_uncertainty_candidate_review(
        evidence=full_evidence,
        requested_surface="UNCERTAINTY_APPROVAL_NOTICE",
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
        coverage_validation_status="COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW",
    )
    scenarios.append(_s("blocks_uncertainty_approval_surface", not blocked_approval.authorized_for_review_summary))

    missing_chain = evaluate_uncertainty_candidate_review(evidence={})
    scenarios.append(_s("blocks_missing_evidence_chain", not missing_chain.authorized_for_review_summary))

    blocking_leakage = evaluate_uncertainty_candidate_review(
        evidence={"kfold_leakage_diagnostic_report": True, "false_confidence_audit_report": True},
        leakage_diagnostic_status="KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE",
    )
    scenarios.append(_s("blocks_blocking_leakage", not blocking_leakage.authorized_for_review_summary))

    mismatch = evaluate_uncertainty_candidate_review(
        evidence=full_evidence,
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
        coverage_validation_status="COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW",
        metric_estimand_mismatch=True,
    )
    scenarios.append(_s("blocks_metric_estimand_mismatch", not mismatch.authorized_for_review_summary))

    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"auth_{flag}_false", not contract.authorization_flags[flag]))
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


def run_validation(*, write_summary: bool = False, summary_path: Path | None = None) -> dict[str, Any]:
    contract = build_tbrridge_uncertainty_candidate_review_contract()
    validation = validate_tbrridge_uncertainty_candidate_review_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "tbrridge_uncertainty_candidate_review_contract",
        "base_commit": _git_commit(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": list(DEPENDS_ON),
        "failed_scenarios": failed,
        "validation": validation,
        "final_verdict": _VERDICT,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
        "deferred_artifact": _DEFERRED,
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
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=args.write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
