"""TBRRIDGE_KFOLD_COVERAGE_VALIDATION_CONTRACT_001 — KFold coverage validation contract."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

_ARTIFACT_ID = "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "tbrridge_kfold_coverage_validation_contract_defined_no_runtime_or_uncertainty"
_VERDICT = "tbrridge_kfold_coverage_validation_contract_defined_no_runtime_or_uncertainty"
_RECOMMENDED_NEXT = "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001"
_ALTERNATIVE_NEXT = "AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001"
_DEFERRED = "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_KFOLD_COVERAGE_VALIDATION_CONTRACT_001_summary.json"
)

DEPENDS_ON = (
    "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001",
    "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001",
    "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001",
)

METHOD_ID = "TBRRidge"
INSTRUMENT_ID = "TBRRidge_Kfold"
ESTIMATOR_FAMILY = "TBRRidge"
INFERENCE_FAMILY = "KFold"

COVERAGE_VALIDATION_STATUSES = (
    "COVERAGE_VALIDATION_NOT_EVALUATED",
    "COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW",
    "COVERAGE_VALIDATION_READY_WITH_RESTRICTIONS",
    "COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK",
    "COVERAGE_VALIDATION_BLOCKED_BY_PLACEBO_MISCALIBRATION",
    "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS",
    "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_SIMULATION_DESIGN",
    "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_NULL_CONTROL",
    "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_POSITIVE_CONTROL",
    "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_REGIME_COVERAGE",
    "COVERAGE_VALIDATION_REQUIRES_METHOD_REVIEW",
)

COVERAGE_RISK_TYPES = (
    "INTERVAL_SEMANTICS_UNDEFINED",
    "NOMINAL_EMPIRICAL_COVERAGE_MISMATCH",
    "UNDERCOVERAGE_RISK",
    "OVERCOVERAGE_UNINFORMATIVE_INTERVAL_RISK",
    "NULL_FALSE_POSITIVE_RISK",
    "DIRECTIONAL_FALSE_SIGNAL_RISK",
    "POSITIVE_CONTROL_RECOVERY_FAILURE",
    "PLACEBO_CALIBRATED_TAIL_MISMATCH",
    "FOLD_GEOMETRY_SENSITIVITY",
    "SAMPLE_SIZE_SENSITIVITY",
    "DONOR_POOL_SENSITIVITY",
    "REGULARIZATION_SENSITIVITY",
    "OUTLIER_WEEK_SENSITIVITY",
    "TEMPORAL_LEAKAGE_DEPENDENCY",
    "PLACEBO_MISCALIBRATION_DEPENDENCY",
    "AGGREGATE_POOLED_MISUSE_RISK",
    "METRIC_ESTIMAND_MISMATCH",
)

REQUIRED_EVIDENCE = (
    "leakage_diagnostic_report",
    "placebo_calibration_diagnostic_report",
    "interval_semantics_report",
    "simulation_design_manifest",
    "null_control_manifest",
    "positive_control_manifest",
    "synthetic_effect_injection_manifest",
    "fold_geometry_regime_manifest",
    "sample_size_regime_manifest",
    "regularization_grid_manifest",
    "donor_pool_sensitivity_report",
    "outlier_sensitivity_report",
    "empirical_coverage_report",
    "false_positive_rate_report",
    "directional_error_report",
    "placebo_calibrated_tail_report",
    "failure_packet_manifest",
    "lineage_provenance_manifest",
)

VALIDATION_PACKET_FIELDS = (
    "validation_id",
    "validation_status",
    "method_id",
    "instrument_id",
    "estimator_family",
    "inference_family",
    "interval_semantics",
    "nominal_coverage_target",
    "empirical_coverage_summary",
    "validation_regimes_evaluated",
    "coverage_risks_evaluated",
    "detected_coverage_risks",
    "required_evidence",
    "missing_evidence",
    "blockers",
    "restrictions",
    "allowed_surfaces",
    "prohibited_surfaces",
    "failure_packet",
    "lineage_manifest",
    "provenance_hash",
    "policy_version",
)

ALLOWED_SURFACES = (
    "DIAGNOSTIC_ONLY",
    "RESEARCH_OR_REVIEW_ONLY",
    "COVERAGE_VALIDATION_SUMMARY",
    "FALSE_CONFIDENCE_RISK_SUMMARY",
    "REGIME_SENSITIVITY_SUMMARY",
    "UNCERTAINTY_CANDIDATE_EVIDENCE_SUMMARY",
)

PROHIBITED_SURFACES = (
    "COVERAGE_APPROVAL_CLAIM",
    "CONFIDENCE_INTERVAL_CLAIM",
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "P_VALUE_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "ROI_CLAIM",
    "PRODUCTION_READOUT",
    "METHOD_PROMOTION_NOTICE",
    "UNCERTAINTY_AUTHORIZATION_NOTICE",
)

FAILURE_PACKET_FIELDS = (
    "failure_code",
    "failure_reason",
    "detected_coverage_risks",
    "missing_evidence",
    "required_remediation",
    "retry_category",
)

FAILURE_CODES = (
    "MISSING_LEAKAGE_DIAGNOSTIC_REPORT",
    "MISSING_PLACEBO_CALIBRATION_DIAGNOSTIC_REPORT",
    "MISSING_INTERVAL_SEMANTICS_REPORT",
    "MISSING_SIMULATION_DESIGN_MANIFEST",
    "MISSING_NULL_CONTROL_MANIFEST",
    "MISSING_POSITIVE_CONTROL_MANIFEST",
    "MISSING_REGIME_MANIFEST",
    "LEAKAGE_DIAGNOSTIC_BLOCKING",
    "PLACEBO_CALIBRATION_BLOCKING",
    "INTERVAL_SEMANTICS_UNDEFINED",
    "NULL_FALSE_POSITIVE_RISK_UNCHARACTERIZED",
    "POSITIVE_CONTROL_RECOVERY_UNCHARACTERIZED",
    "DIRECTIONAL_ERROR_UNCHARACTERIZED",
    "COVERAGE_APPROVAL_SURFACE_BLOCKED",
)

RETRY_CATEGORIES = (
    "ADD_LEAKAGE_DIAGNOSTIC_REPORT",
    "ADD_PLACEBO_CALIBRATION_DIAGNOSTIC_REPORT",
    "ADD_INTERVAL_SEMANTICS_REPORT",
    "ADD_SIMULATION_DESIGN_MANIFEST",
    "ADD_NULL_CONTROL_MANIFEST",
    "ADD_POSITIVE_CONTROL_MANIFEST",
    "ADD_REGIME_MANIFESTS",
    "RESTRICT_TO_DIAGNOSTIC_ONLY",
    "REDESIGN_COVERAGE_VALIDATION",
    "BLOCK_UNCERTAINTY_SURFACE",
    "REQUIRE_METHOD_REVIEW",
)

INTERVAL_SEMANTICS_REQUIREMENTS = (
    "interval_centering_must_be_declared_before_coverage_measurement",
    "interval_width_construction_must_be_declared",
    "estimand_alignment_must_match_point_readout_and_simulation_truth",
    "symmetry_or_asymmetry_semantics_must_be_documented",
    "fold_dispersion_must_not_be_treated_as_causal_ci_without_contract",
    "level_percent_truth_must_not_mismatch_readout_scale",
)

SIMULATION_DESIGN_REQUIREMENTS = (
    "simulation_design_manifest_must_declare_world_and_regime_grid",
    "null_and_positive_control_worlds_must_be_explicit",
    "synthetic_effect_injection_must_align_with_estimand",
    "coverage_validation_must_not_compute_intervals_in_contract_or_runtime_gate",
    "aggregate_pooled_claims_blocked_without_pooled_estimand_semantics",
)

NULL_CONTROL_REQUIREMENTS = (
    "null_control_manifest_must_declare_null_worlds_and_truth",
    "false_positive_rate_report_must_characterize_null_behavior",
    "empirical_coverage_report_must_attach_to_null_worlds",
    "null_false_positive_risk_must_be_flagged_from_supplied_reports",
)

POSITIVE_CONTROL_REQUIREMENTS = (
    "positive_control_manifest_must_declare_effect_injection_regimes",
    "positive_control_recovery_must_be_characterized_from_supplied_reports",
    "synthetic_effect_injection_manifest_must_align_with_positive_controls",
    "recovery_failure_risk_must_be_flagged_without_authorizing_uncertainty",
)

REGIME_REQUIREMENTS = (
    "fold_geometry_regime_manifest_required",
    "sample_size_regime_manifest_required",
    "regularization_grid_manifest_required",
    "donor_pool_sensitivity_report_required",
    "outlier_sensitivity_report_required",
    "coverage_must_be_evaluated_across_all_regime_dimensions",
)

FUTURE_RUNTIME_TESTS = (
    "blocks_without_leakage_diagnostic_report",
    "blocks_when_leakage_diagnostic_is_blocking",
    "blocks_without_placebo_calibration_diagnostic_report",
    "blocks_when_placebo_calibration_is_blocking",
    "blocks_without_interval_semantics",
    "blocks_without_simulation_design_manifest",
    "blocks_without_null_control_manifest",
    "blocks_without_positive_control_manifest",
    "blocks_without_fold_geometry_sample_size_regularization_regime_manifests",
    "documents_empirical_coverage_evidence_without_computing_intervals",
    "flags_undercoverage_overcoverage_false_positive_directional_error_positive_control_risks",
    "blocks_confidence_interval_p_value_significance_causal_lift_roi_production_promotion_uncertainty_surfaces",
    "emits_deterministic_validation_id_and_provenance_hash",
    "all_forbidden_computation_authorization_flags_false",
)

_AUTH_FLAGS = {
    "coverage_runtime_implemented": False,
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
    "coverage_validation_contract_defined": True,
    "coverage_validation_statuses_defined": True,
    "coverage_risk_taxonomy_defined": True,
    "interval_semantics_requirements_defined": True,
    "simulation_design_requirements_defined": True,
    "null_control_requirements_defined": True,
    "positive_control_requirements_defined": True,
    "regime_requirements_defined": True,
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


class CoverageValidationStatus(str, Enum):
    COVERAGE_VALIDATION_NOT_EVALUATED = "COVERAGE_VALIDATION_NOT_EVALUATED"
    COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW = "COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW"
    COVERAGE_VALIDATION_READY_WITH_RESTRICTIONS = "COVERAGE_VALIDATION_READY_WITH_RESTRICTIONS"
    COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK = "COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK"
    COVERAGE_VALIDATION_BLOCKED_BY_PLACEBO_MISCALIBRATION = (
        "COVERAGE_VALIDATION_BLOCKED_BY_PLACEBO_MISCALIBRATION"
    )
    COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS = (
        "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS"
    )
    COVERAGE_VALIDATION_BLOCKED_BY_MISSING_SIMULATION_DESIGN = (
        "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_SIMULATION_DESIGN"
    )
    COVERAGE_VALIDATION_BLOCKED_BY_MISSING_NULL_CONTROL = "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_NULL_CONTROL"
    COVERAGE_VALIDATION_BLOCKED_BY_MISSING_POSITIVE_CONTROL = (
        "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_POSITIVE_CONTROL"
    )
    COVERAGE_VALIDATION_BLOCKED_BY_MISSING_REGIME_COVERAGE = "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_REGIME_COVERAGE"
    COVERAGE_VALIDATION_REQUIRES_METHOD_REVIEW = "COVERAGE_VALIDATION_REQUIRES_METHOD_REVIEW"


class CoverageRiskType(str, Enum):
    INTERVAL_SEMANTICS_UNDEFINED = "INTERVAL_SEMANTICS_UNDEFINED"
    NOMINAL_EMPIRICAL_COVERAGE_MISMATCH = "NOMINAL_EMPIRICAL_COVERAGE_MISMATCH"
    UNDERCOVERAGE_RISK = "UNDERCOVERAGE_RISK"
    OVERCOVERAGE_UNINFORMATIVE_INTERVAL_RISK = "OVERCOVERAGE_UNINFORMATIVE_INTERVAL_RISK"
    NULL_FALSE_POSITIVE_RISK = "NULL_FALSE_POSITIVE_RISK"
    DIRECTIONAL_FALSE_SIGNAL_RISK = "DIRECTIONAL_FALSE_SIGNAL_RISK"
    POSITIVE_CONTROL_RECOVERY_FAILURE = "POSITIVE_CONTROL_RECOVERY_FAILURE"
    PLACEBO_CALIBRATED_TAIL_MISMATCH = "PLACEBO_CALIBRATED_TAIL_MISMATCH"
    FOLD_GEOMETRY_SENSITIVITY = "FOLD_GEOMETRY_SENSITIVITY"
    SAMPLE_SIZE_SENSITIVITY = "SAMPLE_SIZE_SENSITIVITY"
    DONOR_POOL_SENSITIVITY = "DONOR_POOL_SENSITIVITY"
    REGULARIZATION_SENSITIVITY = "REGULARIZATION_SENSITIVITY"
    OUTLIER_WEEK_SENSITIVITY = "OUTLIER_WEEK_SENSITIVITY"
    TEMPORAL_LEAKAGE_DEPENDENCY = "TEMPORAL_LEAKAGE_DEPENDENCY"
    PLACEBO_MISCALIBRATION_DEPENDENCY = "PLACEBO_MISCALIBRATION_DEPENDENCY"
    AGGREGATE_POOLED_MISUSE_RISK = "AGGREGATE_POOLED_MISUSE_RISK"
    METRIC_ESTIMAND_MISMATCH = "METRIC_ESTIMAND_MISMATCH"


@dataclass(frozen=True)
class TbrridgeKfoldCoverageValidationContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    coverage_validation_contract_defined: bool
    coverage_validation_statuses_defined: bool
    coverage_risk_taxonomy_defined: bool
    interval_semantics_requirements_defined: bool
    simulation_design_requirements_defined: bool
    null_control_requirements_defined: bool
    positive_control_requirements_defined: bool
    regime_requirements_defined: bool
    failure_packet_semantics_defined: bool
    future_runtime_tests_documented: bool
    coverage_validation_statuses: tuple[str, ...]
    coverage_risk_types: tuple[str, ...]
    required_evidence: tuple[str, ...]
    validation_packet_fields: tuple[str, ...]
    allowed_surfaces: tuple[str, ...]
    prohibited_surfaces: tuple[str, ...]
    failure_packet_fields: tuple[str, ...]
    failure_codes: tuple[str, ...]
    retry_categories: tuple[str, ...]
    interval_semantics_requirements: tuple[str, ...]
    simulation_design_requirements: tuple[str, ...]
    null_control_requirements: tuple[str, ...]
    positive_control_requirements: tuple[str, ...]
    regime_requirements: tuple[str, ...]
    future_runtime_tests: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    deferred_artifact: str
    final_verdict: str


@dataclass(frozen=True)
class CoverageValidationEvaluationResult:
    validation_status: str
    authorized_for_diagnostic_summary: bool
    detected_coverage_risks: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    failure_code: str | None
    failure_reason: str | None
    retry_category: str | None

    def to_failure_packet(self) -> dict[str, Any] | None:
        if self.failure_code is None:
            return None
        return {
            "failure_code": self.failure_code,
            "failure_reason": self.failure_reason,
            "detected_coverage_risks": list(self.detected_coverage_risks),
            "missing_evidence": list(self.missing_evidence),
            "required_remediation": self.retry_category,
            "retry_category": self.retry_category,
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_tbrridge_kfold_coverage_validation_contract() -> TbrridgeKfoldCoverageValidationContract:
    return TbrridgeKfoldCoverageValidationContract(
        artifact_id=_ARTIFACT_ID,
        scope=_SCOPE,
        depends_on=DEPENDS_ON,
        coverage_validation_contract_defined=True,
        coverage_validation_statuses_defined=True,
        coverage_risk_taxonomy_defined=True,
        interval_semantics_requirements_defined=True,
        simulation_design_requirements_defined=True,
        null_control_requirements_defined=True,
        positive_control_requirements_defined=True,
        regime_requirements_defined=True,
        failure_packet_semantics_defined=True,
        future_runtime_tests_documented=True,
        coverage_validation_statuses=COVERAGE_VALIDATION_STATUSES,
        coverage_risk_types=COVERAGE_RISK_TYPES,
        required_evidence=REQUIRED_EVIDENCE,
        validation_packet_fields=VALIDATION_PACKET_FIELDS,
        allowed_surfaces=ALLOWED_SURFACES,
        prohibited_surfaces=PROHIBITED_SURFACES,
        failure_packet_fields=FAILURE_PACKET_FIELDS,
        failure_codes=FAILURE_CODES,
        retry_categories=RETRY_CATEGORIES,
        interval_semantics_requirements=INTERVAL_SEMANTICS_REQUIREMENTS,
        simulation_design_requirements=SIMULATION_DESIGN_REQUIREMENTS,
        null_control_requirements=NULL_CONTROL_REQUIREMENTS,
        positive_control_requirements=POSITIVE_CONTROL_REQUIREMENTS,
        regime_requirements=REGIME_REQUIREMENTS,
        future_runtime_tests=FUTURE_RUNTIME_TESTS,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=_RECOMMENDED_NEXT,
        alternative_next_artifact=_ALTERNATIVE_NEXT,
        deferred_artifact=_DEFERRED,
        final_verdict=_VERDICT,
    )


def _missing_evidence(required: tuple[str, ...], evidence: Mapping[str, bool]) -> tuple[str, ...]:
    return tuple(req for req in required if not evidence.get(req, False))


def evaluate_coverage_validation(
    *,
    evidence: Mapping[str, bool] | None = None,
    detected_risks: tuple[str, ...] | None = None,
    requested_surface: str | None = None,
    leakage_diagnostic_status: str | None = None,
    placebo_calibration_status: str | None = None,
) -> CoverageValidationEvaluationResult:
    """Contract gate: evaluate coverage validation readiness from evidence flags."""
    ev = dict(evidence or {})
    detected = tuple(detected_risks or ())
    surface = requested_surface or "COVERAGE_VALIDATION_SUMMARY"

    if surface in PROHIBITED_SURFACES:
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_REQUIRES_METHOD_REVIEW.value,
            authorized_for_diagnostic_summary=False,
            detected_coverage_risks=detected,
            missing_evidence=(),
            failure_code="COVERAGE_APPROVAL_SURFACE_BLOCKED",
            failure_reason="Coverage approval/CI/p-value/significance/lift/ROI/production/uncertainty surfaces blocked",
            retry_category="BLOCK_UNCERTAINTY_SURFACE",
        )

    if not ev.get("leakage_diagnostic_report"):
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK.value,
            authorized_for_diagnostic_summary=False,
            detected_coverage_risks=detected + ("TEMPORAL_LEAKAGE_DEPENDENCY",),
            missing_evidence=("leakage_diagnostic_report",),
            failure_code="MISSING_LEAKAGE_DIAGNOSTIC_REPORT",
            failure_reason="Leakage diagnostic report required before coverage validation",
            retry_category="ADD_LEAKAGE_DIAGNOSTIC_REPORT",
        )

    if leakage_diagnostic_status in _LEAKAGE_BLOCKING_STATUSES:
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK.value,
            authorized_for_diagnostic_summary=False,
            detected_coverage_risks=detected + ("TEMPORAL_LEAKAGE_DEPENDENCY",),
            missing_evidence=(),
            failure_code="LEAKAGE_DIAGNOSTIC_BLOCKING",
            failure_reason=f"Leakage diagnostic blocking: {leakage_diagnostic_status}",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    if not ev.get("placebo_calibration_diagnostic_report"):
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_BLOCKED_BY_PLACEBO_MISCALIBRATION.value,
            authorized_for_diagnostic_summary=False,
            detected_coverage_risks=detected + ("PLACEBO_MISCALIBRATION_DEPENDENCY",),
            missing_evidence=("placebo_calibration_diagnostic_report",),
            failure_code="MISSING_PLACEBO_CALIBRATION_DIAGNOSTIC_REPORT",
            failure_reason="Placebo calibration diagnostic report required before coverage validation",
            retry_category="ADD_PLACEBO_CALIBRATION_DIAGNOSTIC_REPORT",
        )

    if placebo_calibration_status in _PLACEBO_BLOCKING_STATUSES:
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_BLOCKED_BY_PLACEBO_MISCALIBRATION.value,
            authorized_for_diagnostic_summary=False,
            detected_coverage_risks=detected + ("PLACEBO_MISCALIBRATION_DEPENDENCY",),
            missing_evidence=(),
            failure_code="PLACEBO_CALIBRATION_BLOCKING",
            failure_reason=f"Placebo calibration blocking: {placebo_calibration_status}",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    if not ev.get("interval_semantics_report"):
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS.value,
            authorized_for_diagnostic_summary=False,
            detected_coverage_risks=detected + ("INTERVAL_SEMANTICS_UNDEFINED",),
            missing_evidence=("interval_semantics_report",),
            failure_code="MISSING_INTERVAL_SEMANTICS_REPORT",
            failure_reason="Interval semantics must be defined before coverage measurement",
            retry_category="ADD_INTERVAL_SEMANTICS_REPORT",
        )

    if "INTERVAL_SEMANTICS_UNDEFINED" in detected:
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS.value,
            authorized_for_diagnostic_summary=False,
            detected_coverage_risks=detected,
            missing_evidence=(),
            failure_code="INTERVAL_SEMANTICS_UNDEFINED",
            failure_reason="Interval semantics undefined for TBRRidge KFold",
            retry_category="ADD_INTERVAL_SEMANTICS_REPORT",
        )

    if not ev.get("simulation_design_manifest"):
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_BLOCKED_BY_MISSING_SIMULATION_DESIGN.value,
            authorized_for_diagnostic_summary=False,
            detected_coverage_risks=detected,
            missing_evidence=("simulation_design_manifest",),
            failure_code="MISSING_SIMULATION_DESIGN_MANIFEST",
            failure_reason="Simulation design manifest required for coverage validation",
            retry_category="ADD_SIMULATION_DESIGN_MANIFEST",
        )

    null_required = ("null_control_manifest", "false_positive_rate_report", "empirical_coverage_report")
    missing_null = _missing_evidence(null_required, ev)
    if missing_null:
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_BLOCKED_BY_MISSING_NULL_CONTROL.value,
            authorized_for_diagnostic_summary=False,
            detected_coverage_risks=detected + ("NULL_FALSE_POSITIVE_RISK",),
            missing_evidence=missing_null,
            failure_code="MISSING_NULL_CONTROL_MANIFEST",
            failure_reason=f"Null-control evidence missing: {', '.join(missing_null)}",
            retry_category="ADD_NULL_CONTROL_MANIFEST",
        )

    positive_required = ("positive_control_manifest", "synthetic_effect_injection_manifest")
    missing_positive = _missing_evidence(positive_required, ev)
    if missing_positive:
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_BLOCKED_BY_MISSING_POSITIVE_CONTROL.value,
            authorized_for_diagnostic_summary=False,
            detected_coverage_risks=detected + ("POSITIVE_CONTROL_RECOVERY_FAILURE",),
            missing_evidence=missing_positive,
            failure_code="MISSING_POSITIVE_CONTROL_MANIFEST",
            failure_reason=f"Positive-control evidence missing: {', '.join(missing_positive)}",
            retry_category="ADD_POSITIVE_CONTROL_MANIFEST",
        )

    regime_required = (
        "fold_geometry_regime_manifest",
        "sample_size_regime_manifest",
        "regularization_grid_manifest",
    )
    missing_regime = _missing_evidence(regime_required, ev)
    if missing_regime:
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_BLOCKED_BY_MISSING_REGIME_COVERAGE.value,
            authorized_for_diagnostic_summary=False,
            detected_coverage_risks=detected,
            missing_evidence=missing_regime,
            failure_code="MISSING_REGIME_MANIFEST",
            failure_reason=f"Regime manifests missing: {', '.join(missing_regime)}",
            retry_category="ADD_REGIME_MANIFESTS",
        )

    if "NULL_FALSE_POSITIVE_RISK" in detected and not ev.get("false_positive_rate_report"):
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_BLOCKED_BY_MISSING_NULL_CONTROL.value,
            authorized_for_diagnostic_summary=False,
            detected_coverage_risks=detected,
            missing_evidence=("false_positive_rate_report",),
            failure_code="NULL_FALSE_POSITIVE_RISK_UNCHARACTERIZED",
            failure_reason="Null false-positive risk uncharacterized",
            retry_category="ADD_NULL_CONTROL_MANIFEST",
        )

    if "POSITIVE_CONTROL_RECOVERY_FAILURE" in detected:
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_READY_WITH_RESTRICTIONS.value,
            authorized_for_diagnostic_summary=True,
            detected_coverage_risks=detected,
            missing_evidence=(),
            failure_code="POSITIVE_CONTROL_RECOVERY_UNCHARACTERIZED",
            failure_reason="Positive-control recovery failure flagged from supplied reports",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    if "DIRECTIONAL_FALSE_SIGNAL_RISK" in detected and not ev.get("directional_error_report"):
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_BLOCKED_BY_MISSING_NULL_CONTROL.value,
            authorized_for_diagnostic_summary=False,
            detected_coverage_risks=detected,
            missing_evidence=("directional_error_report",),
            failure_code="DIRECTIONAL_ERROR_UNCHARACTERIZED",
            failure_reason="Directional false-signal behavior uncharacterized",
            retry_category="ADD_NULL_CONTROL_MANIFEST",
        )

    risk_flags = [
        rt
        for rt in detected
        if rt
        in (
            "UNDERCOVERAGE_RISK",
            "OVERCOVERAGE_UNINFORMATIVE_INTERVAL_RISK",
            "NOMINAL_EMPIRICAL_COVERAGE_MISMATCH",
            "PLACEBO_CALIBRATED_TAIL_MISMATCH",
            "FOLD_GEOMETRY_SENSITIVITY",
            "SAMPLE_SIZE_SENSITIVITY",
            "DONOR_POOL_SENSITIVITY",
            "REGULARIZATION_SENSITIVITY",
            "OUTLIER_WEEK_SENSITIVITY",
            "AGGREGATE_POOLED_MISUSE_RISK",
            "METRIC_ESTIMAND_MISMATCH",
        )
    ]
    if risk_flags:
        return CoverageValidationEvaluationResult(
            validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_READY_WITH_RESTRICTIONS.value,
            authorized_for_diagnostic_summary=True,
            detected_coverage_risks=detected,
            missing_evidence=(),
            failure_code=None,
            failure_reason=f"Coverage risk flagged: {risk_flags[0]}",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    return CoverageValidationEvaluationResult(
        validation_status=CoverageValidationStatus.COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW.value,
        authorized_for_diagnostic_summary=True,
        detected_coverage_risks=detected,
        missing_evidence=(),
        failure_code=None,
        failure_reason=None,
        retry_category=None,
    )


def validate_tbrridge_kfold_coverage_validation_contract(
    contract: TbrridgeKfoldCoverageValidationContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if len(contract.coverage_validation_statuses) < 10:
        issues.append("coverage_validation_statuses incomplete")
    if "INTERVAL_SEMANTICS_UNDEFINED" not in contract.coverage_risk_types:
        issues.append("coverage_risk_types incomplete")
    if "leakage_diagnostic_report" not in contract.required_evidence:
        issues.append("required_evidence incomplete")
    if "COVERAGE_APPROVAL_CLAIM" not in contract.prohibited_surfaces:
        issues.append("prohibited_surfaces incomplete")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        if not getattr(contract, key, False):
            issues.append(f"contract positive flag {key} must be {expected}")
    return {"valid": not issues, "issues": issues}


def get_tbrridge_kfold_coverage_validation_contract_metadata() -> dict[str, Any]:
    contract = build_tbrridge_kfold_coverage_validation_contract()
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


def list_coverage_validation_statuses() -> tuple[str, ...]:
    return COVERAGE_VALIDATION_STATUSES


def list_coverage_risk_types() -> tuple[str, ...]:
    return COVERAGE_RISK_TYPES


def list_future_runtime_tests() -> tuple[str, ...]:
    return FUTURE_RUNTIME_TESTS


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    validation = validate_tbrridge_kfold_coverage_validation_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in COVERAGE_VALIDATION_STATUSES:
        scenarios.append(_s(f"status_{status}", status in contract.coverage_validation_statuses))
    for risk in COVERAGE_RISK_TYPES:
        scenarios.append(_s(f"risk_{risk}", risk in contract.coverage_risk_types))

    full_evidence = {req: True for req in REQUIRED_EVIDENCE}
    ready = evaluate_coverage_validation(
        evidence=full_evidence,
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
    )
    scenarios.append(_s("diagnostic_ready_with_full_evidence", ready.authorized_for_diagnostic_summary))

    blocked_ci = evaluate_coverage_validation(
        evidence=full_evidence,
        requested_surface="CONFIDENCE_INTERVAL_CLAIM",
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
    )
    scenarios.append(_s("blocks_confidence_interval_surface", not blocked_ci.authorized_for_diagnostic_summary))

    missing_leakage = evaluate_coverage_validation(evidence={})
    scenarios.append(_s("blocks_without_leakage_report", not missing_leakage.authorized_for_diagnostic_summary))

    blocking_leakage = evaluate_coverage_validation(
        evidence={"leakage_diagnostic_report": True},
        leakage_diagnostic_status="KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE",
    )
    scenarios.append(_s("blocks_blocking_leakage_status", not blocking_leakage.authorized_for_diagnostic_summary))

    missing_interval = evaluate_coverage_validation(
        evidence={
            "leakage_diagnostic_report": True,
            "placebo_calibration_diagnostic_report": True,
        },
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
    )
    scenarios.append(_s("blocks_without_interval_semantics", not missing_interval.authorized_for_diagnostic_summary))

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
    contract = build_tbrridge_kfold_coverage_validation_contract()
    validation = validate_tbrridge_kfold_coverage_validation_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "tbrridge_kfold_coverage_validation_contract",
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
