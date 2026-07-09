"""TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001 — TBRRidge method promotion review contract."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

_ARTIFACT_ID = "TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "tbrridge_method_promotion_review_contract_defined_no_promotion_or_catalog_unblock"
_VERDICT = "tbrridge_method_promotion_review_contract_defined_no_promotion_or_catalog_unblock"
_RECOMMENDED_NEXT = "TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001"
_ALTERNATIVE_NEXT = "TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001"
_DEFERRED = "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001_summary.json"
)

DEPENDS_ON = (
    "TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001",
    "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001",
    "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001",
    "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001",
    "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001",
    "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001",
)

METHOD_ID = "TBRRidge"
INSTRUMENT_ID = "TBRRidge_Kfold"
CURRENT_CATALOG_RANK = "RANK_0"
CURRENT_CATALOG_STATUS = "BLOCKED"
CURRENT_READINESS_STAGE = "STAGE_2_DIAGNOSTIC_ONLY"
TARGET_REVIEW_STAGE = "STAGE_5_METHOD_PROMOTION_CANDIDATE"

PROMOTION_REVIEW_STATUSES = (
    "METHOD_PROMOTION_REVIEW_NOT_EVALUATED",
    "METHOD_PROMOTION_REVIEW_READY_FOR_RESTRICTED_REVIEW",
    "METHOD_PROMOTION_REVIEW_READY_WITH_RESTRICTIONS",
    "METHOD_PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN",
    "METHOD_PROMOTION_REVIEW_BLOCKED_BY_UNCERTAINTY_CANDIDATE_REVIEW",
    "METHOD_PROMOTION_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS",
    "METHOD_PROMOTION_REVIEW_BLOCKED_BY_FALSE_POSITIVE_EVIDENCE",
    "METHOD_PROMOTION_REVIEW_BLOCKED_BY_DIRECTIONAL_ERROR_EVIDENCE",
    "METHOD_PROMOTION_REVIEW_BLOCKED_BY_POSITIVE_CONTROL_RECOVERY",
    "METHOD_PROMOTION_REVIEW_BLOCKED_BY_REGIME_SENSITIVITY",
    "METHOD_PROMOTION_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH",
    "METHOD_PROMOTION_REVIEW_BLOCKED_BY_AGGREGATE_POOLED_GEOMETRY",
    "METHOD_PROMOTION_REVIEW_BLOCKED_BY_CLAIM_AUTHORIZATION_BOUNDARY",
    "METHOD_PROMOTION_REVIEW_BLOCKED_BY_PRODUCTION_CATALOG_STATUS",
    "METHOD_PROMOTION_REVIEW_REQUIRES_PRODUCTION_COMPATIBILITY_REVIEW",
    "METHOD_PROMOTION_REVIEW_DEFERRED",
)

PROMOTION_RISK_TYPES = (
    "MISSING_EVIDENCE_CHAIN",
    "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING",
    "INTERVAL_SEMANTICS_INCOMPLETE",
    "NULL_CONTROL_FALSE_POSITIVE_INCOMPLETE",
    "DIRECTIONAL_ERROR_EVIDENCE_INCOMPLETE",
    "POSITIVE_CONTROL_RECOVERY_INCOMPLETE",
    "REGIME_SENSITIVITY_INCOMPLETE",
    "DONOR_POOL_SENSITIVITY_INCOMPLETE",
    "REGULARIZATION_SENSITIVITY_INCOMPLETE",
    "OUTLIER_SENSITIVITY_INCOMPLETE",
    "FOLD_GEOMETRY_SENSITIVITY_INCOMPLETE",
    "METRIC_ESTIMAND_MISMATCH",
    "AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED",
    "CLAIM_AUTHORIZATION_BOUNDARY_MISSING",
    "PRODUCTION_CATALOG_BLOCKED",
    "PRODUCTION_COMPATIBILITY_NOT_REVIEWED",
    "DOWNSTREAM_READOUT_SAFETY_INCOMPLETE",
)

REQUIRED_EVIDENCE = (
    "method_promotion_evidence_audit_report",
    "uncertainty_candidate_review_packet",
    "false_confidence_audit_report",
    "leakage_diagnostic_report",
    "placebo_calibration_diagnostic_report",
    "coverage_validation_report",
    "interval_semantics_report",
    "null_control_false_positive_report",
    "directional_error_report",
    "positive_control_recovery_report",
    "regime_sensitivity_report",
    "donor_pool_sensitivity_report",
    "regularization_sensitivity_report",
    "outlier_sensitivity_report",
    "fold_geometry_sensitivity_report",
    "metric_estimand_alignment_report",
    "aggregate_pooled_geometry_blocker_report",
    "claim_authorization_boundary_report",
    "production_catalog_status_report",
    "production_compatibility_boundary_report",
    "downstream_readout_safety_report",
    "lineage_provenance_manifest",
)

PROMOTION_PACKET_FIELDS = (
    "review_id",
    "review_status",
    "method_id",
    "instrument_id",
    "current_catalog_rank",
    "current_catalog_status",
    "current_readiness_stage",
    "target_review_stage",
    "evidence_chain_summary",
    "evidence_components_reviewed",
    "required_evidence",
    "missing_evidence",
    "detected_promotion_risks",
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
    "METHOD_PROMOTION_EVIDENCE_SUMMARY",
    "METHOD_PROMOTION_READINESS_SUMMARY",
    "REMAINING_BLOCKERS_SUMMARY",
    "FUTURE_PROMOTION_RUNTIME_INPUT",
    "PRODUCTION_COMPATIBILITY_REVIEW_INPUT_DESCRIPTION",
)

PROHIBITED_SURFACES = (
    "METHOD_PROMOTION_NOTICE",
    "CATALOG_UNBLOCK_NOTICE",
    "PRODUCTION_COMPATIBILITY_NOTICE",
    "PRODUCTION_AUTHORIZATION_NOTICE",
    "PRODUCTION_READOUT",
    "UNCERTAINTY_APPROVAL_NOTICE",
    "CONFIDENCE_INTERVAL_CLAIM",
    "P_VALUE_CLAIM",
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "ROI_CLAIM",
)

FAILURE_PACKET_FIELDS = (
    "failure_code",
    "failure_reason",
    "detected_promotion_risks",
    "missing_evidence",
    "required_remediation",
    "retry_category",
)

FAILURE_CODES = (
    "MISSING_METHOD_PROMOTION_EVIDENCE_AUDIT",
    "MISSING_UNCERTAINTY_CANDIDATE_REVIEW_PACKET",
    "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING",
    "INTERVAL_SEMANTICS_INCOMPLETE",
    "NULL_CONTROL_FALSE_POSITIVE_INCOMPLETE",
    "DIRECTIONAL_ERROR_EVIDENCE_INCOMPLETE",
    "POSITIVE_CONTROL_RECOVERY_INCOMPLETE",
    "REGIME_SENSITIVITY_INCOMPLETE",
    "METRIC_ESTIMAND_MISMATCH",
    "AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED",
    "CLAIM_AUTHORIZATION_BOUNDARY_MISSING",
    "PRODUCTION_CATALOG_BLOCKED",
    "PRODUCTION_COMPATIBILITY_NOT_REVIEWED",
    "METHOD_PROMOTION_SURFACE_BLOCKED",
)

RETRY_CATEGORIES = (
    "ADD_METHOD_PROMOTION_EVIDENCE_AUDIT",
    "ADD_UNCERTAINTY_CANDIDATE_REVIEW_PACKET",
    "ADD_INTERVAL_SEMANTICS_EVIDENCE",
    "ADD_NULL_CONTROL_FALSE_POSITIVE_EVIDENCE",
    "ADD_DIRECTIONAL_ERROR_EVIDENCE",
    "ADD_POSITIVE_CONTROL_RECOVERY_EVIDENCE",
    "ADD_REGIME_SENSITIVITY_EVIDENCE",
    "ADD_METRIC_ESTIMAND_ALIGNMENT",
    "ADD_CLAIM_AUTHORIZATION_BOUNDARY",
    "RESTRICT_TO_DIAGNOSTIC_ONLY",
    "BLOCK_METHOD_PROMOTION_SURFACE",
    "REQUIRE_PRODUCTION_COMPATIBILITY_REVIEW",
    "DEFER_METHOD_PROMOTION_REVIEW",
)

FUTURE_RUNTIME_TESTS = (
    "blocks_without_method_promotion_evidence_audit",
    "blocks_without_uncertainty_candidate_review_packet",
    "blocks_when_uncertainty_candidate_review_is_blocking",
    "blocks_without_interval_semantics_evidence",
    "blocks_without_null_control_false_positive_evidence",
    "blocks_without_directional_error_evidence",
    "blocks_without_positive_control_recovery_evidence",
    "blocks_without_regime_sensitivity_evidence",
    "blocks_on_metric_estimand_mismatch",
    "blocks_on_unsupported_aggregate_pooled_geometry",
    "blocks_without_claim_authorization_boundary",
    "blocks_production_surfaces_when_production_catalog_remains_blocked",
    "requires_separate_production_compatibility_review_before_production_claims",
    "permits_restricted_method_promotion_readiness_summary_when_evidence_present_and_non_blocking",
    "blocks_method_promotion_catalog_unblock_production_compatibility_uncertainty_ci_p_value_lift_roi_production_surfaces",
    "emits_deterministic_review_id_and_provenance_hash",
    "all_forbidden_computation_authorization_flags_false",
)

_AUTH_FLAGS = {
    "method_promotion_review_runtime_implemented": False,
    "method_promoted": False,
    "method_unblocked": False,
    "method_promotion_authorized": False,
    "production_catalog_unblocked": False,
    "production_compatibility_authorized": False,
    "production_authorization_granted": False,
    "production_readout_authorized": False,
    "uncertainty_candidate_approved": False,
    "uncertainty_authorized": False,
    "confidence_interval_authorized": False,
    "p_value_authorized": False,
    "statistical_significance_authorized": False,
    "coverage_approval_authorized": False,
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
    "mmm_runtime_calls_implemented": False,
    "llm_decisioning_authorized": False,
}

CONTRACT_POSITIVE_FLAGS = {
    "tbrridge_method_promotion_review_contract_defined": True,
    "promotion_review_statuses_defined": True,
    "promotion_risk_taxonomy_defined": True,
    "promotion_required_evidence_defined": True,
    "promotion_failure_packet_semantics_defined": True,
    "promotion_future_runtime_tests_documented": True,
}

_UC_READY_STATUSES = frozenset(
    {
        "UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
        "UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS",
    }
)

_PRODUCTION_COMPAT_SURFACES = frozenset(
    {
        "PRODUCTION_COMPATIBILITY_NOTICE",
        "PRODUCTION_AUTHORIZATION_NOTICE",
        "PRODUCTION_READOUT",
    }
)


class MethodPromotionReviewStatus(str, Enum):
    METHOD_PROMOTION_REVIEW_NOT_EVALUATED = "METHOD_PROMOTION_REVIEW_NOT_EVALUATED"
    METHOD_PROMOTION_REVIEW_READY_FOR_RESTRICTED_REVIEW = (
        "METHOD_PROMOTION_REVIEW_READY_FOR_RESTRICTED_REVIEW"
    )
    METHOD_PROMOTION_REVIEW_READY_WITH_RESTRICTIONS = (
        "METHOD_PROMOTION_REVIEW_READY_WITH_RESTRICTIONS"
    )
    METHOD_PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN = (
        "METHOD_PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN"
    )
    METHOD_PROMOTION_REVIEW_BLOCKED_BY_UNCERTAINTY_CANDIDATE_REVIEW = (
        "METHOD_PROMOTION_REVIEW_BLOCKED_BY_UNCERTAINTY_CANDIDATE_REVIEW"
    )
    METHOD_PROMOTION_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS = (
        "METHOD_PROMOTION_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS"
    )
    METHOD_PROMOTION_REVIEW_BLOCKED_BY_FALSE_POSITIVE_EVIDENCE = (
        "METHOD_PROMOTION_REVIEW_BLOCKED_BY_FALSE_POSITIVE_EVIDENCE"
    )
    METHOD_PROMOTION_REVIEW_BLOCKED_BY_DIRECTIONAL_ERROR_EVIDENCE = (
        "METHOD_PROMOTION_REVIEW_BLOCKED_BY_DIRECTIONAL_ERROR_EVIDENCE"
    )
    METHOD_PROMOTION_REVIEW_BLOCKED_BY_POSITIVE_CONTROL_RECOVERY = (
        "METHOD_PROMOTION_REVIEW_BLOCKED_BY_POSITIVE_CONTROL_RECOVERY"
    )
    METHOD_PROMOTION_REVIEW_BLOCKED_BY_REGIME_SENSITIVITY = (
        "METHOD_PROMOTION_REVIEW_BLOCKED_BY_REGIME_SENSITIVITY"
    )
    METHOD_PROMOTION_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH = (
        "METHOD_PROMOTION_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH"
    )
    METHOD_PROMOTION_REVIEW_BLOCKED_BY_AGGREGATE_POOLED_GEOMETRY = (
        "METHOD_PROMOTION_REVIEW_BLOCKED_BY_AGGREGATE_POOLED_GEOMETRY"
    )
    METHOD_PROMOTION_REVIEW_BLOCKED_BY_CLAIM_AUTHORIZATION_BOUNDARY = (
        "METHOD_PROMOTION_REVIEW_BLOCKED_BY_CLAIM_AUTHORIZATION_BOUNDARY"
    )
    METHOD_PROMOTION_REVIEW_BLOCKED_BY_PRODUCTION_CATALOG_STATUS = (
        "METHOD_PROMOTION_REVIEW_BLOCKED_BY_PRODUCTION_CATALOG_STATUS"
    )
    METHOD_PROMOTION_REVIEW_REQUIRES_PRODUCTION_COMPATIBILITY_REVIEW = (
        "METHOD_PROMOTION_REVIEW_REQUIRES_PRODUCTION_COMPATIBILITY_REVIEW"
    )
    METHOD_PROMOTION_REVIEW_DEFERRED = "METHOD_PROMOTION_REVIEW_DEFERRED"


@dataclass(frozen=True)
class TbrridgeMethodPromotionReviewContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    tbrridge_method_promotion_review_contract_defined: bool
    promotion_review_statuses_defined: bool
    promotion_risk_taxonomy_defined: bool
    promotion_required_evidence_defined: bool
    promotion_failure_packet_semantics_defined: bool
    promotion_future_runtime_tests_documented: bool
    promotion_review_statuses: tuple[str, ...]
    promotion_risk_types: tuple[str, ...]
    required_evidence: tuple[str, ...]
    promotion_packet_fields: tuple[str, ...]
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
class MethodPromotionReviewEvaluationResult:
    review_status: str
    authorized_for_promotion_summary: bool
    detected_promotion_risks: tuple[str, ...]
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
            "detected_promotion_risks": list(self.detected_promotion_risks),
            "missing_evidence": list(self.missing_evidence),
            "required_remediation": self.retry_category,
            "retry_category": self.retry_category,
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_tbrridge_method_promotion_review_contract() -> TbrridgeMethodPromotionReviewContract:
    return TbrridgeMethodPromotionReviewContract(
        artifact_id=_ARTIFACT_ID,
        scope=_SCOPE,
        depends_on=DEPENDS_ON,
        tbrridge_method_promotion_review_contract_defined=True,
        promotion_review_statuses_defined=True,
        promotion_risk_taxonomy_defined=True,
        promotion_required_evidence_defined=True,
        promotion_failure_packet_semantics_defined=True,
        promotion_future_runtime_tests_documented=True,
        promotion_review_statuses=PROMOTION_REVIEW_STATUSES,
        promotion_risk_types=PROMOTION_RISK_TYPES,
        required_evidence=REQUIRED_EVIDENCE,
        promotion_packet_fields=PROMOTION_PACKET_FIELDS,
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


def evaluate_method_promotion_review(
    *,
    evidence: Mapping[str, bool] | None = None,
    detected_risks: tuple[str, ...] | None = None,
    requested_surface: str | None = None,
    uncertainty_candidate_review_status: str | None = None,
    production_catalog_blocked: bool = True,
    production_compatibility_reviewed: bool = False,
    metric_estimand_mismatch: bool = False,
    aggregate_pooled_unsupported: bool = False,
    deferred: bool = False,
) -> MethodPromotionReviewEvaluationResult:
    """Contract gate: evaluate method-promotion review readiness from evidence flags."""
    ev = dict(evidence or {})
    detected = tuple(detected_risks or ())
    surface = requested_surface or "METHOD_PROMOTION_READINESS_SUMMARY"

    if deferred:
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_DEFERRED.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected,
            missing_evidence=(),
            failure_code=None,
            failure_reason="Method promotion review explicitly deferred",
            retry_category="DEFER_METHOD_PROMOTION_REVIEW",
            recommended_next_action="DEFER_METHOD_PROMOTION_REVIEW",
        )

    if surface in _PRODUCTION_COMPAT_SURFACES and not production_compatibility_reviewed:
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_REQUIRES_PRODUCTION_COMPATIBILITY_REVIEW.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected + ("PRODUCTION_COMPATIBILITY_NOT_REVIEWED",),
            missing_evidence=(),
            failure_code="PRODUCTION_COMPATIBILITY_NOT_REVIEWED",
            failure_reason="Production compatibility review required before production surfaces",
            retry_category="REQUIRE_PRODUCTION_COMPATIBILITY_REVIEW",
            recommended_next_action="REQUIRE_PRODUCTION_COMPATIBILITY_REVIEW",
        )

    if surface in PROHIBITED_SURFACES:
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_CLAIM_AUTHORIZATION_BOUNDARY.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected,
            missing_evidence=(),
            failure_code="METHOD_PROMOTION_SURFACE_BLOCKED",
            failure_reason="Method promotion/catalog/CI/p-value/significance/lift/ROI/production surfaces blocked",
            retry_category="BLOCK_METHOD_PROMOTION_SURFACE",
            recommended_next_action="BLOCK_METHOD_PROMOTION_SURFACE",
        )

    if surface in ("PRODUCTION_READOUT", "CATALOG_UNBLOCK_NOTICE") and production_catalog_blocked:
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_PRODUCTION_CATALOG_STATUS.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected + ("PRODUCTION_CATALOG_BLOCKED",),
            missing_evidence=(),
            failure_code="PRODUCTION_CATALOG_BLOCKED",
            failure_reason="Production catalog remains blocked for TBRRidge KFold",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
            recommended_next_action="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    if not ev.get("method_promotion_evidence_audit_report"):
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected + ("MISSING_EVIDENCE_CHAIN",),
            missing_evidence=("method_promotion_evidence_audit_report",),
            failure_code="MISSING_METHOD_PROMOTION_EVIDENCE_AUDIT",
            failure_reason="Method-promotion evidence audit report required",
            retry_category="ADD_METHOD_PROMOTION_EVIDENCE_AUDIT",
            recommended_next_action="ADD_METHOD_PROMOTION_EVIDENCE_AUDIT",
        )

    if not ev.get("uncertainty_candidate_review_packet"):
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected + ("MISSING_EVIDENCE_CHAIN",),
            missing_evidence=("uncertainty_candidate_review_packet",),
            failure_code="MISSING_UNCERTAINTY_CANDIDATE_REVIEW_PACKET",
            failure_reason="Uncertainty-candidate review packet required",
            retry_category="ADD_UNCERTAINTY_CANDIDATE_REVIEW_PACKET",
            recommended_next_action="ADD_UNCERTAINTY_CANDIDATE_REVIEW_PACKET",
        )

    uc_status = uncertainty_candidate_review_status or ""
    if uc_status and uc_status not in _UC_READY_STATUSES:
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_UNCERTAINTY_CANDIDATE_REVIEW.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected + ("UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING",),
            missing_evidence=(),
            failure_code="UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING",
            failure_reason=f"Uncertainty-candidate review blocking: {uc_status}",
            retry_category="ADD_UNCERTAINTY_CANDIDATE_REVIEW_PACKET",
            recommended_next_action="ADD_UNCERTAINTY_CANDIDATE_REVIEW_PACKET",
        )

    for key in (
        "false_confidence_audit_report",
        "leakage_diagnostic_report",
        "placebo_calibration_diagnostic_report",
        "coverage_validation_report",
    ):
        if not ev.get(key):
            return MethodPromotionReviewEvaluationResult(
                review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN.value,
                authorized_for_promotion_summary=False,
                detected_promotion_risks=detected + ("MISSING_EVIDENCE_CHAIN",),
                missing_evidence=(key,),
                failure_code="MISSING_METHOD_PROMOTION_EVIDENCE_AUDIT",
                failure_reason=f"Diagnostic chain evidence missing: {key}",
                retry_category="ADD_METHOD_PROMOTION_EVIDENCE_AUDIT",
                recommended_next_action="ADD_METHOD_PROMOTION_EVIDENCE_AUDIT",
            )

    if not ev.get("interval_semantics_report"):
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected + ("INTERVAL_SEMANTICS_INCOMPLETE",),
            missing_evidence=("interval_semantics_report",),
            failure_code="INTERVAL_SEMANTICS_INCOMPLETE",
            failure_reason="Interval semantics evidence required for promotion review",
            retry_category="ADD_INTERVAL_SEMANTICS_EVIDENCE",
            recommended_next_action="ADD_INTERVAL_SEMANTICS_EVIDENCE",
        )

    if "INTERVAL_SEMANTICS_INCOMPLETE" in detected:
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected,
            missing_evidence=(),
            failure_code="INTERVAL_SEMANTICS_INCOMPLETE",
            failure_reason="Interval semantics incomplete for TBRRidge KFold",
            retry_category="ADD_INTERVAL_SEMANTICS_EVIDENCE",
            recommended_next_action="ADD_INTERVAL_SEMANTICS_EVIDENCE",
        )

    if not ev.get("null_control_false_positive_report"):
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_FALSE_POSITIVE_EVIDENCE.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected + ("NULL_CONTROL_FALSE_POSITIVE_INCOMPLETE",),
            missing_evidence=("null_control_false_positive_report",),
            failure_code="NULL_CONTROL_FALSE_POSITIVE_INCOMPLETE",
            failure_reason="Null-control false-positive evidence required",
            retry_category="ADD_NULL_CONTROL_FALSE_POSITIVE_EVIDENCE",
            recommended_next_action="ADD_NULL_CONTROL_FALSE_POSITIVE_EVIDENCE",
        )

    if not ev.get("directional_error_report"):
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_DIRECTIONAL_ERROR_EVIDENCE.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected + ("DIRECTIONAL_ERROR_EVIDENCE_INCOMPLETE",),
            missing_evidence=("directional_error_report",),
            failure_code="DIRECTIONAL_ERROR_EVIDENCE_INCOMPLETE",
            failure_reason="Directional-error evidence required",
            retry_category="ADD_DIRECTIONAL_ERROR_EVIDENCE",
            recommended_next_action="ADD_DIRECTIONAL_ERROR_EVIDENCE",
        )

    if not ev.get("positive_control_recovery_report"):
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_POSITIVE_CONTROL_RECOVERY.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected + ("POSITIVE_CONTROL_RECOVERY_INCOMPLETE",),
            missing_evidence=("positive_control_recovery_report",),
            failure_code="POSITIVE_CONTROL_RECOVERY_INCOMPLETE",
            failure_reason="Positive-control recovery evidence required",
            retry_category="ADD_POSITIVE_CONTROL_RECOVERY_EVIDENCE",
            recommended_next_action="ADD_POSITIVE_CONTROL_RECOVERY_EVIDENCE",
        )

    if not ev.get("regime_sensitivity_report"):
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_REGIME_SENSITIVITY.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected + ("REGIME_SENSITIVITY_INCOMPLETE",),
            missing_evidence=("regime_sensitivity_report",),
            failure_code="REGIME_SENSITIVITY_INCOMPLETE",
            failure_reason="Regime sensitivity evidence required",
            retry_category="ADD_REGIME_SENSITIVITY_EVIDENCE",
            recommended_next_action="ADD_REGIME_SENSITIVITY_EVIDENCE",
        )

    if metric_estimand_mismatch or "METRIC_ESTIMAND_MISMATCH" in detected:
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected + ("METRIC_ESTIMAND_MISMATCH",),
            missing_evidence=(),
            failure_code="METRIC_ESTIMAND_MISMATCH",
            failure_reason="Metric/estimand mismatch blocks promotion review",
            retry_category="ADD_METRIC_ESTIMAND_ALIGNMENT",
            recommended_next_action="ADD_METRIC_ESTIMAND_ALIGNMENT",
        )

    if aggregate_pooled_unsupported or "AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED" in detected:
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_AGGREGATE_POOLED_GEOMETRY.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected + ("AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED",),
            missing_evidence=(),
            failure_code="AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED",
            failure_reason="Aggregate/pooled geometry unsupported for TBRRidge KFold",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
            recommended_next_action="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    if not ev.get("claim_authorization_boundary_report"):
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_CLAIM_AUTHORIZATION_BOUNDARY.value,
            authorized_for_promotion_summary=False,
            detected_promotion_risks=detected + ("CLAIM_AUTHORIZATION_BOUNDARY_MISSING",),
            missing_evidence=("claim_authorization_boundary_report",),
            failure_code="CLAIM_AUTHORIZATION_BOUNDARY_MISSING",
            failure_reason="Claim authorization boundary report required",
            retry_category="ADD_CLAIM_AUTHORIZATION_BOUNDARY",
            recommended_next_action="ADD_CLAIM_AUTHORIZATION_BOUNDARY",
        )

    optional_missing = _missing_evidence(
        (
            "donor_pool_sensitivity_report",
            "regularization_sensitivity_report",
            "outlier_sensitivity_report",
            "fold_geometry_sensitivity_report",
            "metric_estimand_alignment_report",
            "aggregate_pooled_geometry_blocker_report",
            "production_catalog_status_report",
            "production_compatibility_boundary_report",
            "downstream_readout_safety_report",
        ),
        ev,
    )
    risk_flags = list(detected)
    for item, risk in (
        ("donor_pool_sensitivity_report", "DONOR_POOL_SENSITIVITY_INCOMPLETE"),
        ("regularization_sensitivity_report", "REGULARIZATION_SENSITIVITY_INCOMPLETE"),
        ("outlier_sensitivity_report", "OUTLIER_SENSITIVITY_INCOMPLETE"),
        ("fold_geometry_sensitivity_report", "FOLD_GEOMETRY_SENSITIVITY_INCOMPLETE"),
        ("production_compatibility_boundary_report", "PRODUCTION_COMPATIBILITY_NOT_REVIEWED"),
        ("downstream_readout_safety_report", "DOWNSTREAM_READOUT_SAFETY_INCOMPLETE"),
    ):
        if item in optional_missing and risk not in risk_flags:
            risk_flags.append(risk)
    if production_catalog_blocked and "PRODUCTION_CATALOG_BLOCKED" not in risk_flags:
        risk_flags.append("PRODUCTION_CATALOG_BLOCKED")
    detected = tuple(risk_flags)

    if (
        uc_status == "UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS"
        or optional_missing
        or not production_compatibility_reviewed
    ):
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_READY_WITH_RESTRICTIONS.value,
            authorized_for_promotion_summary=True,
            detected_promotion_risks=detected,
            missing_evidence=optional_missing,
            failure_code=None,
            failure_reason=None,
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
            recommended_next_action="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    if uc_status in _UC_READY_STATUSES:
        return MethodPromotionReviewEvaluationResult(
            review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_READY_FOR_RESTRICTED_REVIEW.value,
            authorized_for_promotion_summary=True,
            detected_promotion_risks=detected,
            missing_evidence=optional_missing,
            failure_code=None,
            failure_reason=None,
            retry_category=None,
            recommended_next_action="PROCEED_TO_RESTRICTED_PROMOTION_SUMMARY",
        )

    return MethodPromotionReviewEvaluationResult(
        review_status=MethodPromotionReviewStatus.METHOD_PROMOTION_REVIEW_BLOCKED_BY_UNCERTAINTY_CANDIDATE_REVIEW.value,
        authorized_for_promotion_summary=False,
        detected_promotion_risks=detected + ("UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING",),
        missing_evidence=(),
        failure_code="UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING",
        failure_reason="Uncertainty-candidate review not ready for promotion review",
        retry_category="ADD_UNCERTAINTY_CANDIDATE_REVIEW_PACKET",
        recommended_next_action="ADD_UNCERTAINTY_CANDIDATE_REVIEW_PACKET",
    )


def validate_tbrridge_method_promotion_review_contract(
    contract: TbrridgeMethodPromotionReviewContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if len(contract.promotion_review_statuses) < 10:
        issues.append("promotion_review_statuses incomplete")
    if "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING" not in contract.promotion_risk_types:
        issues.append("promotion_risk_types incomplete")
    if "method_promotion_evidence_audit_report" not in contract.required_evidence:
        issues.append("required_evidence incomplete")
    if "METHOD_PROMOTION_NOTICE" not in contract.prohibited_surfaces:
        issues.append("prohibited_surfaces incomplete")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        if not getattr(contract, key, False):
            issues.append(f"contract positive flag {key} must be {expected}")
    return {"valid": not issues, "issues": issues}


def get_tbrridge_method_promotion_review_contract_metadata() -> dict[str, Any]:
    contract = build_tbrridge_method_promotion_review_contract()
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


def list_promotion_review_statuses() -> tuple[str, ...]:
    return PROMOTION_REVIEW_STATUSES


def list_promotion_risk_types() -> tuple[str, ...]:
    return PROMOTION_RISK_TYPES


def list_future_runtime_tests() -> tuple[str, ...]:
    return FUTURE_RUNTIME_TESTS


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_tbrridge_method_promotion_review_contract()
    validation = validate_tbrridge_method_promotion_review_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in PROMOTION_REVIEW_STATUSES:
        scenarios.append(_s(f"status_{status}", status in contract.promotion_review_statuses))
    for risk in PROMOTION_RISK_TYPES:
        scenarios.append(_s(f"risk_{risk}", risk in contract.promotion_risk_types))

    full_evidence = {req: True for req in REQUIRED_EVIDENCE}
    ready = evaluate_method_promotion_review(
        evidence=full_evidence,
        uncertainty_candidate_review_status="UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
        production_compatibility_reviewed=True,
    )
    scenarios.append(_s("ready_for_restricted_review", ready.authorized_for_promotion_summary))

    blocked_promotion = evaluate_method_promotion_review(
        evidence=full_evidence,
        requested_surface="METHOD_PROMOTION_NOTICE",
        uncertainty_candidate_review_status="UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
    )
    scenarios.append(_s("blocks_method_promotion_surface", not blocked_promotion.authorized_for_promotion_summary))

    missing_chain = evaluate_method_promotion_review(evidence={})
    scenarios.append(_s("blocks_missing_evidence_chain", not missing_chain.authorized_for_promotion_summary))

    blocking_uc = evaluate_method_promotion_review(
        evidence={"method_promotion_evidence_audit_report": True, "uncertainty_candidate_review_packet": True},
        uncertainty_candidate_review_status="UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_LEAKAGE_DIAGNOSTIC",
    )
    scenarios.append(_s("blocks_blocking_uncertainty_review", not blocking_uc.authorized_for_promotion_summary))

    mismatch = evaluate_method_promotion_review(
        evidence=full_evidence,
        uncertainty_candidate_review_status="UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
        metric_estimand_mismatch=True,
    )
    scenarios.append(_s("blocks_metric_estimand_mismatch", not mismatch.authorized_for_promotion_summary))

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
    contract = build_tbrridge_method_promotion_review_contract()
    validation = validate_tbrridge_method_promotion_review_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "tbrridge_method_promotion_review_contract",
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
