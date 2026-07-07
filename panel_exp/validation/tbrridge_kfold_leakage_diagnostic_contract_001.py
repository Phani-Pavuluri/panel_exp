"""TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001 — KFold leakage diagnostic contract."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

_ARTIFACT_ID = "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "tbrridge_kfold_leakage_diagnostic_contract_defined_no_runtime_or_inference"
_VERDICT = "tbrridge_kfold_leakage_diagnostic_contract_defined_no_runtime_or_inference"
_RECOMMENDED_NEXT = "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001"
_ALTERNATIVE_NEXT = "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001_summary.json"
)

DEPENDS_ON = (
    "TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001",
    "SOPHISTICATED_METHOD_EVIDENCE_LADDER_001",
    "MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001",
)

METHOD_ID = "TBRRidge"
INSTRUMENT_ID = "TBRRidge_Kfold"
ESTIMATOR_FAMILY = "TBRRidge"
INFERENCE_FAMILY = "KFold"

DIAGNOSTIC_STATUSES = (
    "KFOLD_LEAKAGE_NOT_EVALUATED",
    "KFOLD_LEAKAGE_DIAGNOSTIC_READY",
    "KFOLD_LEAKAGE_DIAGNOSTIC_READY_WITH_RESTRICTIONS",
    "KFOLD_LEAKAGE_BLOCKED_BY_UNSUPPORTED_GEOMETRY",
    "KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE",
    "KFOLD_LEAKAGE_BLOCKED_BY_FOLD_OVERLAP",
    "KFOLD_LEAKAGE_BLOCKED_BY_TREATED_CONTROL_CONTAMINATION",
    "KFOLD_LEAKAGE_BLOCKED_BY_SMALL_SAMPLE_GEOMETRY",
    "KFOLD_LEAKAGE_BLOCKED_BY_MISSING_EVIDENCE",
    "KFOLD_LEAKAGE_REQUIRES_METHOD_REVIEW",
)

LEAKAGE_TYPES = (
    "TEMPORAL_LEAKAGE",
    "POST_PERIOD_LEAKAGE",
    "PRE_POST_BOUNDARY_LEAKAGE",
    "TREATED_CONTROL_CONTAMINATION",
    "UNIT_OVERLAP_LEAKAGE",
    "SHARED_CONTROL_FOLD_LEAKAGE",
    "MULTI_TREATED_GEOMETRY_UNSUPPORTED",
    "FOLD_ASSIGNMENT_INSTABILITY",
    "SMALL_SAMPLE_FOLD_DEGENERACY",
    "FEATURE_CONSTRUCTION_LEAKAGE",
    "HYPERPARAMETER_SELECTION_LEAKAGE",
    "OUTLIER_INFLUENCE_LEAKAGE",
)

REQUIRED_EVIDENCE = (
    "fold_assignment_manifest",
    "treated_unit_manifest",
    "control_unit_manifest",
    "pre_period_window",
    "post_period_window",
    "feature_construction_manifest",
    "hyperparameter_selection_manifest",
    "geometry_support_report",
    "temporal_split_report",
    "fold_overlap_report",
    "treated_control_separation_report",
    "sample_size_by_fold",
    "shared_control_family_report",
    "multicell_family_contrast_packet",
    "lineage_provenance_manifest",
)

DIAGNOSTIC_PACKET_FIELDS = (
    "diagnostic_id",
    "diagnostic_status",
    "method_id",
    "instrument_id",
    "estimator_family",
    "inference_family",
    "fold_scheme",
    "treated_geometry",
    "control_geometry",
    "leakage_types_evaluated",
    "detected_leakage_types",
    "unsupported_geometries",
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
    "FOLD_GEOMETRY_DIAGNOSTIC",
    "LEAKAGE_RISK_SUMMARY",
)

PROHIBITED_SURFACES = (
    "KFOLD_UNCERTAINTY_CLAIM",
    "CONFIDENCE_INTERVAL_CLAIM",
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "COVERAGE_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "PRODUCTION_READOUT",
    "METHOD_PROMOTION_NOTICE",
)

FAILURE_PACKET_FIELDS = (
    "failure_code",
    "failure_reason",
    "detected_leakage_types",
    "unsupported_geometries",
    "missing_evidence",
    "required_remediation",
    "retry_category",
)

FAILURE_CODES = (
    "MISSING_FOLD_ASSIGNMENT_MANIFEST",
    "MISSING_TEMPORAL_SPLIT_REPORT",
    "MISSING_GEOMETRY_SUPPORT_REPORT",
    "TEMPORAL_LEAKAGE_DETECTED",
    "TREATED_CONTROL_CONTAMINATION_DETECTED",
    "FOLD_OVERLAP_DETECTED",
    "MULTI_TREATED_GEOMETRY_UNSUPPORTED",
    "SMALL_SAMPLE_FOLD_DEGENERACY",
    "FEATURE_CONSTRUCTION_LEAKAGE_RISK",
    "HYPERPARAMETER_SELECTION_LEAKAGE_RISK",
    "KFOLD_UNCERTAINTY_SURFACE_BLOCKED",
)

RETRY_CATEGORIES = (
    "ADD_FOLD_ASSIGNMENT_MANIFEST",
    "ADD_TEMPORAL_SPLIT_REPORT",
    "ADD_GEOMETRY_SUPPORT_REPORT",
    "ADD_TREATED_CONTROL_SEPARATION_REPORT",
    "RESTRICT_TO_DIAGNOSTIC_ONLY",
    "REDESIGN_FOLD_SCHEME",
    "BLOCK_KFOLD_UNCERTAINTY_SURFACE",
    "REQUIRE_METHOD_REVIEW",
)

UNSUPPORTED_GEOMETRY_RULES = (
    "multi_treated_geometry_requires_explicit_policy_or_block",
    "kfold_multi_treated_unsupported_run001_remains_terminal_until_remediated",
    "shared_control_folds_require_shared_control_family_report",
    "multicell_kfold_requires_multicell_family_contrast_packet",
    "single_treated_default_only_after_geometry_support_passes",
)

TEMPORAL_LEAKAGE_RULES = (
    "post_period_features_must_not_enter_pre_period_folds",
    "pre_post_boundary_must_be_declared_in_temporal_split_report",
    "future_information_must_not_leak_into_training_folds",
    "hyperparameter_selection_must_not_use_post_period_outcomes",
)

FOLD_OVERLAP_RULES = (
    "treated_and_control_units_must_not_share_fold_assignments_when_separated",
    "unit_overlap_across_folds_must_be_reported_in_fold_overlap_report",
    "shared_control_units_must_not_create_implicit_double_counting",
    "fold_assignment_instability_blocks_uncertainty_surfaces",
)

FUTURE_RUNTIME_TESTS = (
    "blocks_without_fold_assignment_manifest",
    "blocks_without_temporal_split_report",
    "blocks_unsupported_multi_treated_geometry",
    "detects_pre_post_boundary_leakage",
    "detects_treated_control_contamination",
    "detects_fold_overlap",
    "blocks_small_sample_fold_degeneracy",
    "flags_feature_construction_leakage_risk",
    "flags_hyperparameter_selection_leakage_risk",
    "permits_diagnostic_only_leakage_summary_when_evidence_present",
    "blocks_kfold_uncertainty_ci_significance_coverage_surfaces",
    "deterministic_diagnostic_id_and_provenance_hash",
    "all_forbidden_computation_authorization_flags_false",
)

_AUTH_FLAGS = {
    "kfold_leakage_runtime_implemented": False,
    "kfold_inference_implemented": False,
    "estimator_implemented": False,
    "inference_implemented": False,
    "bootstrap_inference_implemented": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "coverage_computed": False,
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
    "kfold_leakage_diagnostic_contract_defined": True,
    "leakage_type_taxonomy_defined": True,
    "unsupported_geometry_rules_defined": True,
    "temporal_leakage_rules_defined": True,
    "fold_overlap_rules_defined": True,
    "required_evidence_defined": True,
    "failure_packet_semantics_defined": True,
    "future_runtime_tests_documented": True,
}


class KfoldLeakageDiagnosticStatus(str, Enum):
    KFOLD_LEAKAGE_NOT_EVALUATED = "KFOLD_LEAKAGE_NOT_EVALUATED"
    KFOLD_LEAKAGE_DIAGNOSTIC_READY = "KFOLD_LEAKAGE_DIAGNOSTIC_READY"
    KFOLD_LEAKAGE_DIAGNOSTIC_READY_WITH_RESTRICTIONS = "KFOLD_LEAKAGE_DIAGNOSTIC_READY_WITH_RESTRICTIONS"
    KFOLD_LEAKAGE_BLOCKED_BY_UNSUPPORTED_GEOMETRY = "KFOLD_LEAKAGE_BLOCKED_BY_UNSUPPORTED_GEOMETRY"
    KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE = "KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE"
    KFOLD_LEAKAGE_BLOCKED_BY_FOLD_OVERLAP = "KFOLD_LEAKAGE_BLOCKED_BY_FOLD_OVERLAP"
    KFOLD_LEAKAGE_BLOCKED_BY_TREATED_CONTROL_CONTAMINATION = "KFOLD_LEAKAGE_BLOCKED_BY_TREATED_CONTROL_CONTAMINATION"
    KFOLD_LEAKAGE_BLOCKED_BY_SMALL_SAMPLE_GEOMETRY = "KFOLD_LEAKAGE_BLOCKED_BY_SMALL_SAMPLE_GEOMETRY"
    KFOLD_LEAKAGE_BLOCKED_BY_MISSING_EVIDENCE = "KFOLD_LEAKAGE_BLOCKED_BY_MISSING_EVIDENCE"
    KFOLD_LEAKAGE_REQUIRES_METHOD_REVIEW = "KFOLD_LEAKAGE_REQUIRES_METHOD_REVIEW"


class LeakageType(str, Enum):
    TEMPORAL_LEAKAGE = "TEMPORAL_LEAKAGE"
    POST_PERIOD_LEAKAGE = "POST_PERIOD_LEAKAGE"
    PRE_POST_BOUNDARY_LEAKAGE = "PRE_POST_BOUNDARY_LEAKAGE"
    TREATED_CONTROL_CONTAMINATION = "TREATED_CONTROL_CONTAMINATION"
    UNIT_OVERLAP_LEAKAGE = "UNIT_OVERLAP_LEAKAGE"
    SHARED_CONTROL_FOLD_LEAKAGE = "SHARED_CONTROL_FOLD_LEAKAGE"
    MULTI_TREATED_GEOMETRY_UNSUPPORTED = "MULTI_TREATED_GEOMETRY_UNSUPPORTED"
    FOLD_ASSIGNMENT_INSTABILITY = "FOLD_ASSIGNMENT_INSTABILITY"
    SMALL_SAMPLE_FOLD_DEGENERACY = "SMALL_SAMPLE_FOLD_DEGENERACY"
    FEATURE_CONSTRUCTION_LEAKAGE = "FEATURE_CONSTRUCTION_LEAKAGE"
    HYPERPARAMETER_SELECTION_LEAKAGE = "HYPERPARAMETER_SELECTION_LEAKAGE"
    OUTLIER_INFLUENCE_LEAKAGE = "OUTLIER_INFLUENCE_LEAKAGE"


@dataclass(frozen=True)
class TbrridgeKfoldLeakageDiagnosticContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    kfold_leakage_diagnostic_contract_defined: bool
    leakage_type_taxonomy_defined: bool
    unsupported_geometry_rules_defined: bool
    temporal_leakage_rules_defined: bool
    fold_overlap_rules_defined: bool
    required_evidence_defined: bool
    failure_packet_semantics_defined: bool
    future_runtime_tests_documented: bool
    diagnostic_statuses: tuple[str, ...]
    leakage_types: tuple[str, ...]
    required_evidence: tuple[str, ...]
    diagnostic_packet_fields: tuple[str, ...]
    allowed_surfaces: tuple[str, ...]
    prohibited_surfaces: tuple[str, ...]
    failure_packet_fields: tuple[str, ...]
    failure_codes: tuple[str, ...]
    retry_categories: tuple[str, ...]
    unsupported_geometry_rules: tuple[str, ...]
    temporal_leakage_rules: tuple[str, ...]
    fold_overlap_rules: tuple[str, ...]
    future_runtime_tests: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


@dataclass(frozen=True)
class KfoldLeakageEvaluationResult:
    diagnostic_status: str
    authorized_for_diagnostic_summary: bool
    detected_leakage_types: tuple[str, ...]
    unsupported_geometries: tuple[str, ...]
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
            "detected_leakage_types": list(self.detected_leakage_types),
            "unsupported_geometries": list(self.unsupported_geometries),
            "missing_evidence": list(self.missing_evidence),
            "required_remediation": self.retry_category,
            "retry_category": self.retry_category,
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_tbrridge_kfold_leakage_diagnostic_contract() -> TbrridgeKfoldLeakageDiagnosticContract:
    return TbrridgeKfoldLeakageDiagnosticContract(
        artifact_id=_ARTIFACT_ID,
        scope=_SCOPE,
        depends_on=DEPENDS_ON,
        kfold_leakage_diagnostic_contract_defined=True,
        leakage_type_taxonomy_defined=True,
        unsupported_geometry_rules_defined=True,
        temporal_leakage_rules_defined=True,
        fold_overlap_rules_defined=True,
        required_evidence_defined=True,
        failure_packet_semantics_defined=True,
        future_runtime_tests_documented=True,
        diagnostic_statuses=DIAGNOSTIC_STATUSES,
        leakage_types=LEAKAGE_TYPES,
        required_evidence=REQUIRED_EVIDENCE,
        diagnostic_packet_fields=DIAGNOSTIC_PACKET_FIELDS,
        allowed_surfaces=ALLOWED_SURFACES,
        prohibited_surfaces=PROHIBITED_SURFACES,
        failure_packet_fields=FAILURE_PACKET_FIELDS,
        failure_codes=FAILURE_CODES,
        retry_categories=RETRY_CATEGORIES,
        unsupported_geometry_rules=UNSUPPORTED_GEOMETRY_RULES,
        temporal_leakage_rules=TEMPORAL_LEAKAGE_RULES,
        fold_overlap_rules=FOLD_OVERLAP_RULES,
        future_runtime_tests=FUTURE_RUNTIME_TESTS,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=_RECOMMENDED_NEXT,
        alternative_next_artifact=_ALTERNATIVE_NEXT,
        final_verdict=_VERDICT,
    )


def _missing_evidence(required: tuple[str, ...], evidence: Mapping[str, bool]) -> tuple[str, ...]:
    return tuple(req for req in required if not evidence.get(req, False))


def evaluate_kfold_leakage_diagnostic(
    *,
    evidence: Mapping[str, bool] | None = None,
    treated_geometry: str | None = None,
    detected_leakage: tuple[str, ...] | None = None,
    requested_surface: str | None = None,
) -> KfoldLeakageEvaluationResult:
    """Contract gate: evaluate KFold leakage diagnostic readiness from evidence flags."""
    ev = dict(evidence or {})
    detected = tuple(detected_leakage or ())
    surface = requested_surface or "LEAKAGE_RISK_SUMMARY"

    core_required = (
        "fold_assignment_manifest",
        "temporal_split_report",
        "geometry_support_report",
        "treated_control_separation_report",
        "sample_size_by_fold",
    )
    missing = _missing_evidence(core_required, ev)

    if surface in PROHIBITED_SURFACES:
        return KfoldLeakageEvaluationResult(
            diagnostic_status=KfoldLeakageDiagnosticStatus.KFOLD_LEAKAGE_REQUIRES_METHOD_REVIEW.value,
            authorized_for_diagnostic_summary=False,
            detected_leakage_types=detected,
            unsupported_geometries=(),
            missing_evidence=missing,
            failure_code="KFOLD_UNCERTAINTY_SURFACE_BLOCKED",
            failure_reason="KFold uncertainty/CI/significance/coverage surfaces blocked by contract",
            retry_category="BLOCK_KFOLD_UNCERTAINTY_SURFACE",
        )

    if missing:
        return KfoldLeakageEvaluationResult(
            diagnostic_status=KfoldLeakageDiagnosticStatus.KFOLD_LEAKAGE_BLOCKED_BY_MISSING_EVIDENCE.value,
            authorized_for_diagnostic_summary=False,
            detected_leakage_types=detected,
            unsupported_geometries=(),
            missing_evidence=missing,
            failure_code=_failure_code_for_missing(missing),
            failure_reason=f"Missing required evidence: {', '.join(missing)}",
            retry_category=_retry_for_missing(missing),
        )

    if treated_geometry == "multi_treated" and not ev.get("geometry_support_report_multi_treated_policy"):
        return KfoldLeakageEvaluationResult(
            diagnostic_status=KfoldLeakageDiagnosticStatus.KFOLD_LEAKAGE_BLOCKED_BY_UNSUPPORTED_GEOMETRY.value,
            authorized_for_diagnostic_summary=False,
            detected_leakage_types=detected + ("MULTI_TREATED_GEOMETRY_UNSUPPORTED",),
            unsupported_geometries=("multi_treated",),
            missing_evidence=(),
            failure_code="MULTI_TREATED_GEOMETRY_UNSUPPORTED",
            failure_reason="kfold_multi_treated_unsupported_run001 lineage; geometry policy required",
            retry_category="REQUIRE_METHOD_REVIEW",
        )

    if "MULTI_TREATED_GEOMETRY_UNSUPPORTED" in detected:
        return KfoldLeakageEvaluationResult(
            diagnostic_status=KfoldLeakageDiagnosticStatus.KFOLD_LEAKAGE_BLOCKED_BY_UNSUPPORTED_GEOMETRY.value,
            authorized_for_diagnostic_summary=False,
            detected_leakage_types=detected,
            unsupported_geometries=("multi_treated",),
            missing_evidence=(),
            failure_code="MULTI_TREATED_GEOMETRY_UNSUPPORTED",
            failure_reason="Multi-treated geometry unsupported for KFold",
            retry_category="REQUIRE_METHOD_REVIEW",
        )

    if "TEMPORAL_LEAKAGE" in detected or "POST_PERIOD_LEAKAGE" in detected or "PRE_POST_BOUNDARY_LEAKAGE" in detected:
        return KfoldLeakageEvaluationResult(
            diagnostic_status=KfoldLeakageDiagnosticStatus.KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE.value,
            authorized_for_diagnostic_summary=False,
            detected_leakage_types=detected,
            unsupported_geometries=(),
            missing_evidence=(),
            failure_code="TEMPORAL_LEAKAGE_DETECTED",
            failure_reason="Temporal or pre/post boundary leakage detected",
            retry_category="REDESIGN_FOLD_SCHEME",
        )

    if "TREATED_CONTROL_CONTAMINATION" in detected or "UNIT_OVERLAP_LEAKAGE" in detected:
        return KfoldLeakageEvaluationResult(
            diagnostic_status=KfoldLeakageDiagnosticStatus.KFOLD_LEAKAGE_BLOCKED_BY_TREATED_CONTROL_CONTAMINATION.value,
            authorized_for_diagnostic_summary=False,
            detected_leakage_types=detected,
            unsupported_geometries=(),
            missing_evidence=(),
            failure_code="TREATED_CONTROL_CONTAMINATION_DETECTED",
            failure_reason="Treated/control contamination or unit overlap detected",
            retry_category="ADD_TREATED_CONTROL_SEPARATION_REPORT",
        )

    if "SHARED_CONTROL_FOLD_LEAKAGE" in detected or "FOLD_ASSIGNMENT_INSTABILITY" in detected:
        code = "FOLD_OVERLAP_DETECTED"
        return KfoldLeakageEvaluationResult(
            diagnostic_status=KfoldLeakageDiagnosticStatus.KFOLD_LEAKAGE_BLOCKED_BY_FOLD_OVERLAP.value,
            authorized_for_diagnostic_summary=False,
            detected_leakage_types=detected,
            unsupported_geometries=(),
            missing_evidence=(),
            failure_code=code,
            failure_reason="Fold overlap or shared-control fold leakage detected",
            retry_category="REDESIGN_FOLD_SCHEME",
        )

    if "SMALL_SAMPLE_FOLD_DEGENERACY" in detected:
        return KfoldLeakageEvaluationResult(
            diagnostic_status=KfoldLeakageDiagnosticStatus.KFOLD_LEAKAGE_BLOCKED_BY_SMALL_SAMPLE_GEOMETRY.value,
            authorized_for_diagnostic_summary=False,
            detected_leakage_types=detected,
            unsupported_geometries=(),
            missing_evidence=(),
            failure_code="SMALL_SAMPLE_FOLD_DEGENERACY",
            failure_reason="Small-sample fold degeneracy detected",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    risk_flags = [lt for lt in detected if lt in ("FEATURE_CONSTRUCTION_LEAKAGE", "HYPERPARAMETER_SELECTION_LEAKAGE")]
    if risk_flags:
        return KfoldLeakageEvaluationResult(
            diagnostic_status=KfoldLeakageDiagnosticStatus.KFOLD_LEAKAGE_DIAGNOSTIC_READY_WITH_RESTRICTIONS.value,
            authorized_for_diagnostic_summary=True,
            detected_leakage_types=detected,
            unsupported_geometries=(),
            missing_evidence=(),
            failure_code=_risk_failure_code(risk_flags[0]),
            failure_reason=f"Leakage risk flagged: {risk_flags[0]}",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    if ev.get("shared_control_family_report") and not ev.get("multicell_family_contrast_packet"):
        return KfoldLeakageEvaluationResult(
            diagnostic_status=KfoldLeakageDiagnosticStatus.KFOLD_LEAKAGE_DIAGNOSTIC_READY_WITH_RESTRICTIONS.value,
            authorized_for_diagnostic_summary=True,
            detected_leakage_types=detected,
            unsupported_geometries=(),
            missing_evidence=("multicell_family_contrast_packet",),
            failure_code=None,
            failure_reason=None,
            retry_category=None,
        )

    return KfoldLeakageEvaluationResult(
        diagnostic_status=KfoldLeakageDiagnosticStatus.KFOLD_LEAKAGE_DIAGNOSTIC_READY.value,
        authorized_for_diagnostic_summary=True,
        detected_leakage_types=detected,
        unsupported_geometries=(),
        missing_evidence=(),
        failure_code=None,
        failure_reason=None,
        retry_category=None,
    )


def _failure_code_for_missing(missing: tuple[str, ...]) -> str:
    if "fold_assignment_manifest" in missing:
        return "MISSING_FOLD_ASSIGNMENT_MANIFEST"
    if "temporal_split_report" in missing:
        return "MISSING_TEMPORAL_SPLIT_REPORT"
    if "geometry_support_report" in missing:
        return "MISSING_GEOMETRY_SUPPORT_REPORT"
    return "MISSING_FOLD_ASSIGNMENT_MANIFEST"


def _retry_for_missing(missing: tuple[str, ...]) -> str:
    if "fold_assignment_manifest" in missing:
        return "ADD_FOLD_ASSIGNMENT_MANIFEST"
    if "temporal_split_report" in missing:
        return "ADD_TEMPORAL_SPLIT_REPORT"
    if "geometry_support_report" in missing:
        return "ADD_GEOMETRY_SUPPORT_REPORT"
    if "treated_control_separation_report" in missing:
        return "ADD_TREATED_CONTROL_SEPARATION_REPORT"
    return "ADD_FOLD_ASSIGNMENT_MANIFEST"


def _risk_failure_code(leakage_type: str) -> str:
    if leakage_type == "FEATURE_CONSTRUCTION_LEAKAGE":
        return "FEATURE_CONSTRUCTION_LEAKAGE_RISK"
    return "HYPERPARAMETER_SELECTION_LEAKAGE_RISK"


def validate_tbrridge_kfold_leakage_diagnostic_contract(
    contract: TbrridgeKfoldLeakageDiagnosticContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if len(contract.diagnostic_statuses) < 8:
        issues.append("diagnostic_statuses incomplete")
    if "MULTI_TREATED_GEOMETRY_UNSUPPORTED" not in contract.leakage_types:
        issues.append("leakage_types incomplete")
    if "fold_assignment_manifest" not in contract.required_evidence:
        issues.append("required_evidence incomplete")
    if "KFOLD_UNCERTAINTY_CLAIM" not in contract.prohibited_surfaces:
        issues.append("prohibited_surfaces incomplete")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        if not getattr(contract, key, False):
            issues.append(f"contract positive flag {key} must be {expected}")
    return {"valid": not issues, "issues": issues}


def get_tbrridge_kfold_leakage_diagnostic_contract_metadata() -> dict[str, Any]:
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
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


def list_diagnostic_statuses() -> tuple[str, ...]:
    return DIAGNOSTIC_STATUSES


def list_leakage_types() -> tuple[str, ...]:
    return LEAKAGE_TYPES


def list_future_runtime_tests() -> tuple[str, ...]:
    return FUTURE_RUNTIME_TESTS


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    validation = validate_tbrridge_kfold_leakage_diagnostic_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in DIAGNOSTIC_STATUSES:
        scenarios.append(_s(f"status_{status}", status in contract.diagnostic_statuses))
    for lt in LEAKAGE_TYPES:
        scenarios.append(_s(f"leakage_{lt}", lt in contract.leakage_types))

    full_evidence = {req: True for req in REQUIRED_EVIDENCE}
    ready = evaluate_kfold_leakage_diagnostic(evidence=full_evidence, treated_geometry="single_treated")
    scenarios.append(_s("diagnostic_ready_with_full_evidence", ready.authorized_for_diagnostic_summary))

    blocked_unc = evaluate_kfold_leakage_diagnostic(
        evidence=full_evidence,
        requested_surface="CONFIDENCE_INTERVAL_CLAIM",
    )
    scenarios.append(_s("blocks_uncertainty_surface", not blocked_unc.authorized_for_diagnostic_summary))

    multi = evaluate_kfold_leakage_diagnostic(
        evidence=full_evidence,
        treated_geometry="multi_treated",
    )
    scenarios.append(_s("blocks_multi_treated_without_policy", not multi.authorized_for_diagnostic_summary))

    temporal = evaluate_kfold_leakage_diagnostic(
        evidence=full_evidence,
        detected_leakage=("TEMPORAL_LEAKAGE",),
    )
    scenarios.append(_s("blocks_temporal_leakage", not temporal.authorized_for_diagnostic_summary))

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
    contract = build_tbrridge_kfold_leakage_diagnostic_contract()
    validation = validate_tbrridge_kfold_leakage_diagnostic_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "tbrridge_kfold_leakage_diagnostic_contract",
        "base_commit": _git_commit(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": list(DEPENDS_ON),
        "failed_scenarios": failed,
        "validation": validation,
        "final_verdict": _VERDICT,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
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
