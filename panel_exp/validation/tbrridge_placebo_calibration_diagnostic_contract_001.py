"""TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001 — placebo calibration diagnostic contract."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

_ARTIFACT_ID = "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "tbrridge_placebo_calibration_diagnostic_contract_defined_no_runtime_or_inference"
_VERDICT = "tbrridge_placebo_calibration_diagnostic_contract_defined_no_runtime_or_inference"
_RECOMMENDED_NEXT = "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001"
_ALTERNATIVE_NEXT = "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001_summary.json"
)

DEPENDS_ON = (
    "TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001",
    "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001",
    "SOPHISTICATED_METHOD_EVIDENCE_LADDER_001",
)

METHOD_ID = "TBRRidge"
INSTRUMENT_ID = "TBRRidge_Placebo"
ESTIMATOR_FAMILY = "TBRRidge"
INFERENCE_FAMILY = "Placebo"

DIAGNOSTIC_STATUSES = (
    "PLACEBO_CALIBRATION_NOT_EVALUATED",
    "PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
    "PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS",
    "PLACEBO_CALIBRATION_BLOCKED_BY_MISSING_PLACEBO_MANIFEST",
    "PLACEBO_CALIBRATION_BLOCKED_BY_INVALID_NULL_CONSTRUCTION",
    "PLACEBO_CALIBRATION_BLOCKED_BY_INSUFFICIENT_PLACEBOS",
    "PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION",
    "PLACEBO_CALIBRATION_BLOCKED_BY_DIRECTIONAL_INSTABILITY",
    "PLACEBO_CALIBRATION_BLOCKED_BY_OUTLIER_INFLUENCE",
    "PLACEBO_CALIBRATION_REQUIRES_METHOD_REVIEW",
)

PLACEBO_RISK_TYPES = (
    "INVALID_NULL_PERIOD",
    "PSEUDO_TREATED_CONTAMINATION",
    "PLACEBO_DONOR_OVERLAP",
    "INSUFFICIENT_PLACEBO_COUNT",
    "UNBALANCED_PLACEBO_GEOMETRY",
    "PLACEBO_TAIL_INSTABILITY",
    "PLACEBO_RANK_INSTABILITY",
    "DIRECTIONAL_SIGN_INSTABILITY",
    "OUTLIER_PLACEBO_INFLUENCE",
    "PRE_PERIOD_FIT_OVERCONFIDENCE",
    "REGULARIZATION_MASKED_PLACEBO_FAILURE",
    "PLACEBO_METRIC_MISMATCH",
)

REQUIRED_EVIDENCE = (
    "placebo_assignment_manifest",
    "pseudo_treated_unit_manifest",
    "placebo_control_unit_manifest",
    "null_period_definition",
    "placebo_window_manifest",
    "placebo_metric_manifest",
    "placebo_geometry_report",
    "placebo_contamination_report",
    "placebo_count_report",
    "placebo_rank_tail_report",
    "placebo_directionality_report",
    "placebo_outlier_influence_report",
    "regularization_sensitivity_report",
    "kfold_leakage_diagnostic_report",
    "lineage_provenance_manifest",
)

DIAGNOSTIC_PACKET_FIELDS = (
    "diagnostic_id",
    "diagnostic_status",
    "method_id",
    "instrument_id",
    "estimator_family",
    "inference_family",
    "placebo_scheme",
    "pseudo_treated_geometry",
    "placebo_control_geometry",
    "placebo_risk_types_evaluated",
    "detected_placebo_risks",
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
    "PLACEBO_CALIBRATION_SUMMARY",
    "FALSE_CONFIDENCE_RISK_SUMMARY",
    "PLACEBO_GEOMETRY_DIAGNOSTIC",
)

PROHIBITED_SURFACES = (
    "PLACEBO_P_VALUE_CLAIM",
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "CONFIDENCE_INTERVAL_CLAIM",
    "COVERAGE_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "ROI_CLAIM",
    "PRODUCTION_READOUT",
    "METHOD_PROMOTION_NOTICE",
)

FAILURE_PACKET_FIELDS = (
    "failure_code",
    "failure_reason",
    "detected_placebo_risks",
    "missing_evidence",
    "required_remediation",
    "retry_category",
)

FAILURE_CODES = (
    "MISSING_PLACEBO_ASSIGNMENT_MANIFEST",
    "MISSING_NULL_PERIOD_DEFINITION",
    "INVALID_NULL_CONSTRUCTION",
    "INSUFFICIENT_PLACEBO_COUNT",
    "PLACEBO_CONTAMINATION_DETECTED",
    "DIRECTIONAL_INSTABILITY_DETECTED",
    "OUTLIER_PLACEBO_INFLUENCE_DETECTED",
    "PLACEBO_TAIL_RANK_INSTABILITY",
    "PRE_PERIOD_FIT_OVERCONFIDENCE_RISK",
    "REGULARIZATION_MASKED_PLACEBO_FAILURE_RISK",
    "PLACEBO_INFERENCE_SURFACE_BLOCKED",
)

RETRY_CATEGORIES = (
    "ADD_PLACEBO_ASSIGNMENT_MANIFEST",
    "ADD_NULL_PERIOD_DEFINITION",
    "ADD_PLACEBO_GEOMETRY_REPORT",
    "ADD_PLACEBO_CONTAMINATION_REPORT",
    "ADD_PLACEBO_COUNT_REPORT",
    "RESTRICT_TO_DIAGNOSTIC_ONLY",
    "REDESIGN_PLACEBO_SCHEME",
    "BLOCK_PLACEBO_INFERENCE_SURFACE",
    "REQUIRE_METHOD_REVIEW",
)

NULL_CONSTRUCTION_RULES = (
    "null_period_must_be_pre_treatment_or_declared_counterfactual",
    "pseudo_treated_units_must_not_overlap_true_treated_units",
    "placebo_window_must_not_include_post_treatment_outcome_leakage",
    "placebo_metric_must_align_with_estimand_under_test",
    "multi_treated_placebo_requires_explicit_geometry_policy",
)

PLACEBO_CONTAMINATION_RULES = (
    "pseudo_treated_must_not_share_donors_with_true_treated_controls",
    "placebo_donor_overlap_must_be_reported_in_contamination_report",
    "placebo_controls_must_not_include_future_treated_units",
    "shared_control_placebo_families_require_geometry_declaration",
)

PLACEBO_RANK_TAIL_RULES = (
    "placebo_rank_distribution_must_be_reported_before_inference_claims",
    "tail_mass_instability_blocks_placebo_p_value_surfaces",
    "rank_instability_across_placebos_blocks_significance_claims",
    "studentized_or_normalized_ranks_require_documented_null_reference",
)

DIRECTIONAL_INSTABILITY_RULES = (
    "directional_sign_flips_across_placebos_require_review",
    "asymmetric_placebo_geometry_blocks_directional_lift_claims",
    "outlier_driven_directionality_blocks_production_readout",
    "pre_period_fit_strength_must_not_substitute_for_placebo_pass",
)

FUTURE_RUNTIME_TESTS = (
    "blocks_without_placebo_assignment_manifest",
    "blocks_without_null_period_definition",
    "blocks_invalid_null_construction",
    "blocks_insufficient_placebo_count",
    "detects_placebo_contamination",
    "detects_directional_instability",
    "detects_outlier_placebo_influence",
    "flags_pre_period_fit_overconfidence_risk",
    "flags_regularization_masked_placebo_failure_risk",
    "permits_diagnostic_only_placebo_summary_when_evidence_present",
    "blocks_placebo_p_value_ci_significance_coverage_surfaces",
    "deterministic_diagnostic_id_and_provenance_hash",
    "all_forbidden_computation_authorization_flags_false",
)

_AUTH_FLAGS = {
    "placebo_calibration_runtime_implemented": False,
    "placebo_inference_implemented": False,
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
    "placebo_calibration_diagnostic_contract_defined": True,
    "placebo_risk_taxonomy_defined": True,
    "null_construction_rules_defined": True,
    "placebo_contamination_rules_defined": True,
    "placebo_rank_tail_rules_defined": True,
    "directional_instability_rules_defined": True,
    "required_evidence_defined": True,
    "failure_packet_semantics_defined": True,
    "future_runtime_tests_documented": True,
}


class PlaceboCalibrationDiagnosticStatus(str, Enum):
    PLACEBO_CALIBRATION_NOT_EVALUATED = "PLACEBO_CALIBRATION_NOT_EVALUATED"
    PLACEBO_CALIBRATION_DIAGNOSTIC_READY = "PLACEBO_CALIBRATION_DIAGNOSTIC_READY"
    PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS = (
        "PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS"
    )
    PLACEBO_CALIBRATION_BLOCKED_BY_MISSING_PLACEBO_MANIFEST = (
        "PLACEBO_CALIBRATION_BLOCKED_BY_MISSING_PLACEBO_MANIFEST"
    )
    PLACEBO_CALIBRATION_BLOCKED_BY_INVALID_NULL_CONSTRUCTION = (
        "PLACEBO_CALIBRATION_BLOCKED_BY_INVALID_NULL_CONSTRUCTION"
    )
    PLACEBO_CALIBRATION_BLOCKED_BY_INSUFFICIENT_PLACEBOS = (
        "PLACEBO_CALIBRATION_BLOCKED_BY_INSUFFICIENT_PLACEBOS"
    )
    PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION = (
        "PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION"
    )
    PLACEBO_CALIBRATION_BLOCKED_BY_DIRECTIONAL_INSTABILITY = (
        "PLACEBO_CALIBRATION_BLOCKED_BY_DIRECTIONAL_INSTABILITY"
    )
    PLACEBO_CALIBRATION_BLOCKED_BY_OUTLIER_INFLUENCE = (
        "PLACEBO_CALIBRATION_BLOCKED_BY_OUTLIER_INFLUENCE"
    )
    PLACEBO_CALIBRATION_REQUIRES_METHOD_REVIEW = "PLACEBO_CALIBRATION_REQUIRES_METHOD_REVIEW"


class PlaceboRiskType(str, Enum):
    INVALID_NULL_PERIOD = "INVALID_NULL_PERIOD"
    PSEUDO_TREATED_CONTAMINATION = "PSEUDO_TREATED_CONTAMINATION"
    PLACEBO_DONOR_OVERLAP = "PLACEBO_DONOR_OVERLAP"
    INSUFFICIENT_PLACEBO_COUNT = "INSUFFICIENT_PLACEBO_COUNT"
    UNBALANCED_PLACEBO_GEOMETRY = "UNBALANCED_PLACEBO_GEOMETRY"
    PLACEBO_TAIL_INSTABILITY = "PLACEBO_TAIL_INSTABILITY"
    PLACEBO_RANK_INSTABILITY = "PLACEBO_RANK_INSTABILITY"
    DIRECTIONAL_SIGN_INSTABILITY = "DIRECTIONAL_SIGN_INSTABILITY"
    OUTLIER_PLACEBO_INFLUENCE = "OUTLIER_PLACEBO_INFLUENCE"
    PRE_PERIOD_FIT_OVERCONFIDENCE = "PRE_PERIOD_FIT_OVERCONFIDENCE"
    REGULARIZATION_MASKED_PLACEBO_FAILURE = "REGULARIZATION_MASKED_PLACEBO_FAILURE"
    PLACEBO_METRIC_MISMATCH = "PLACEBO_METRIC_MISMATCH"


@dataclass(frozen=True)
class TbrridgePlaceboCalibrationDiagnosticContract:
    artifact_id: str
    scope: str
    depends_on: tuple[str, ...]
    placebo_calibration_diagnostic_contract_defined: bool
    placebo_risk_taxonomy_defined: bool
    null_construction_rules_defined: bool
    placebo_contamination_rules_defined: bool
    placebo_rank_tail_rules_defined: bool
    directional_instability_rules_defined: bool
    required_evidence_defined: bool
    failure_packet_semantics_defined: bool
    future_runtime_tests_documented: bool
    diagnostic_statuses: tuple[str, ...]
    placebo_risk_types: tuple[str, ...]
    required_evidence: tuple[str, ...]
    diagnostic_packet_fields: tuple[str, ...]
    allowed_surfaces: tuple[str, ...]
    prohibited_surfaces: tuple[str, ...]
    failure_packet_fields: tuple[str, ...]
    failure_codes: tuple[str, ...]
    retry_categories: tuple[str, ...]
    null_construction_rules: tuple[str, ...]
    placebo_contamination_rules: tuple[str, ...]
    placebo_rank_tail_rules: tuple[str, ...]
    directional_instability_rules: tuple[str, ...]
    future_runtime_tests: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    alternative_next_artifact: str
    final_verdict: str


@dataclass(frozen=True)
class PlaceboCalibrationEvaluationResult:
    diagnostic_status: str
    authorized_for_diagnostic_summary: bool
    detected_placebo_risks: tuple[str, ...]
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
            "detected_placebo_risks": list(self.detected_placebo_risks),
            "missing_evidence": list(self.missing_evidence),
            "required_remediation": self.retry_category,
            "retry_category": self.retry_category,
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_tbrridge_placebo_calibration_diagnostic_contract() -> TbrridgePlaceboCalibrationDiagnosticContract:
    return TbrridgePlaceboCalibrationDiagnosticContract(
        artifact_id=_ARTIFACT_ID,
        scope=_SCOPE,
        depends_on=DEPENDS_ON,
        placebo_calibration_diagnostic_contract_defined=True,
        placebo_risk_taxonomy_defined=True,
        null_construction_rules_defined=True,
        placebo_contamination_rules_defined=True,
        placebo_rank_tail_rules_defined=True,
        directional_instability_rules_defined=True,
        required_evidence_defined=True,
        failure_packet_semantics_defined=True,
        future_runtime_tests_documented=True,
        diagnostic_statuses=DIAGNOSTIC_STATUSES,
        placebo_risk_types=PLACEBO_RISK_TYPES,
        required_evidence=REQUIRED_EVIDENCE,
        diagnostic_packet_fields=DIAGNOSTIC_PACKET_FIELDS,
        allowed_surfaces=ALLOWED_SURFACES,
        prohibited_surfaces=PROHIBITED_SURFACES,
        failure_packet_fields=FAILURE_PACKET_FIELDS,
        failure_codes=FAILURE_CODES,
        retry_categories=RETRY_CATEGORIES,
        null_construction_rules=NULL_CONSTRUCTION_RULES,
        placebo_contamination_rules=PLACEBO_CONTAMINATION_RULES,
        placebo_rank_tail_rules=PLACEBO_RANK_TAIL_RULES,
        directional_instability_rules=DIRECTIONAL_INSTABILITY_RULES,
        future_runtime_tests=FUTURE_RUNTIME_TESTS,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=_RECOMMENDED_NEXT,
        alternative_next_artifact=_ALTERNATIVE_NEXT,
        final_verdict=_VERDICT,
    )


def _missing_evidence(required: tuple[str, ...], evidence: Mapping[str, bool]) -> tuple[str, ...]:
    return tuple(req for req in required if not evidence.get(req, False))


def evaluate_placebo_calibration_diagnostic(
    *,
    evidence: Mapping[str, bool] | None = None,
    detected_risks: tuple[str, ...] | None = None,
    requested_surface: str | None = None,
    kfold_path_requested: bool = False,
) -> PlaceboCalibrationEvaluationResult:
    """Contract gate: evaluate placebo calibration diagnostic readiness from evidence flags."""
    ev = dict(evidence or {})
    detected = tuple(detected_risks or ())
    surface = requested_surface or "PLACEBO_CALIBRATION_SUMMARY"

    core_required = (
        "placebo_assignment_manifest",
        "null_period_definition",
        "placebo_geometry_report",
        "placebo_count_report",
        "placebo_contamination_report",
    )
    missing = _missing_evidence(core_required, ev)

    if surface in PROHIBITED_SURFACES:
        return PlaceboCalibrationEvaluationResult(
            diagnostic_status=PlaceboCalibrationDiagnosticStatus.PLACEBO_CALIBRATION_REQUIRES_METHOD_REVIEW.value,
            authorized_for_diagnostic_summary=False,
            detected_placebo_risks=detected,
            missing_evidence=missing,
            failure_code="PLACEBO_INFERENCE_SURFACE_BLOCKED",
            failure_reason="Placebo p-value/CI/significance/coverage/lift surfaces blocked by contract",
            retry_category="BLOCK_PLACEBO_INFERENCE_SURFACE",
        )

    if missing:
        return PlaceboCalibrationEvaluationResult(
            diagnostic_status=PlaceboCalibrationDiagnosticStatus.PLACEBO_CALIBRATION_BLOCKED_BY_MISSING_PLACEBO_MANIFEST.value,
            authorized_for_diagnostic_summary=False,
            detected_placebo_risks=detected,
            missing_evidence=missing,
            failure_code=_failure_code_for_missing(missing),
            failure_reason=f"Missing required placebo evidence: {', '.join(missing)}",
            retry_category=_retry_for_missing(missing),
        )

    if "INVALID_NULL_PERIOD" in detected:
        return PlaceboCalibrationEvaluationResult(
            diagnostic_status=PlaceboCalibrationDiagnosticStatus.PLACEBO_CALIBRATION_BLOCKED_BY_INVALID_NULL_CONSTRUCTION.value,
            authorized_for_diagnostic_summary=False,
            detected_placebo_risks=detected,
            missing_evidence=(),
            failure_code="INVALID_NULL_CONSTRUCTION",
            failure_reason="Invalid null period or placebo construction detected",
            retry_category="REDESIGN_PLACEBO_SCHEME",
        )

    if "INSUFFICIENT_PLACEBO_COUNT" in detected:
        return PlaceboCalibrationEvaluationResult(
            diagnostic_status=PlaceboCalibrationDiagnosticStatus.PLACEBO_CALIBRATION_BLOCKED_BY_INSUFFICIENT_PLACEBOS.value,
            authorized_for_diagnostic_summary=False,
            detected_placebo_risks=detected,
            missing_evidence=(),
            failure_code="INSUFFICIENT_PLACEBO_COUNT",
            failure_reason="Insufficient placebo count for calibration diagnostic",
            retry_category="ADD_PLACEBO_COUNT_REPORT",
        )

    if (
        "PSEUDO_TREATED_CONTAMINATION" in detected
        or "PLACEBO_DONOR_OVERLAP" in detected
    ):
        return PlaceboCalibrationEvaluationResult(
            diagnostic_status=PlaceboCalibrationDiagnosticStatus.PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION.value,
            authorized_for_diagnostic_summary=False,
            detected_placebo_risks=detected,
            missing_evidence=(),
            failure_code="PLACEBO_CONTAMINATION_DETECTED",
            failure_reason="Placebo contamination or donor overlap detected",
            retry_category="ADD_PLACEBO_CONTAMINATION_REPORT",
        )

    if (
        "DIRECTIONAL_SIGN_INSTABILITY" in detected
        or "PLACEBO_RANK_INSTABILITY" in detected
        or "PLACEBO_TAIL_INSTABILITY" in detected
    ):
        return PlaceboCalibrationEvaluationResult(
            diagnostic_status=PlaceboCalibrationDiagnosticStatus.PLACEBO_CALIBRATION_BLOCKED_BY_DIRECTIONAL_INSTABILITY.value,
            authorized_for_diagnostic_summary=False,
            detected_placebo_risks=detected,
            missing_evidence=(),
            failure_code="DIRECTIONAL_INSTABILITY_DETECTED",
            failure_reason="Directional, rank, or tail instability detected across placebos",
            retry_category="REQUIRE_METHOD_REVIEW",
        )

    if "OUTLIER_PLACEBO_INFLUENCE" in detected:
        return PlaceboCalibrationEvaluationResult(
            diagnostic_status=PlaceboCalibrationDiagnosticStatus.PLACEBO_CALIBRATION_BLOCKED_BY_OUTLIER_INFLUENCE.value,
            authorized_for_diagnostic_summary=False,
            detected_placebo_risks=detected,
            missing_evidence=(),
            failure_code="OUTLIER_PLACEBO_INFLUENCE_DETECTED",
            failure_reason="Outlier-driven placebo influence detected",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    risk_flags = [
        rt
        for rt in detected
        if rt
        in (
            "PRE_PERIOD_FIT_OVERCONFIDENCE",
            "REGULARIZATION_MASKED_PLACEBO_FAILURE",
            "PLACEBO_METRIC_MISMATCH",
            "UNBALANCED_PLACEBO_GEOMETRY",
        )
    ]
    if risk_flags:
        return PlaceboCalibrationEvaluationResult(
            diagnostic_status=PlaceboCalibrationDiagnosticStatus.PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS.value,
            authorized_for_diagnostic_summary=True,
            detected_placebo_risks=detected,
            missing_evidence=(),
            failure_code=_risk_failure_code(risk_flags[0]),
            failure_reason=f"Placebo risk flagged: {risk_flags[0]}",
            retry_category="RESTRICT_TO_DIAGNOSTIC_ONLY",
        )

    if kfold_path_requested and not ev.get("kfold_leakage_diagnostic_report"):
        return PlaceboCalibrationEvaluationResult(
            diagnostic_status=PlaceboCalibrationDiagnosticStatus.PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS.value,
            authorized_for_diagnostic_summary=True,
            detected_placebo_risks=detected,
            missing_evidence=("kfold_leakage_diagnostic_report",),
            failure_code=None,
            failure_reason=None,
            retry_category=None,
        )

    return PlaceboCalibrationEvaluationResult(
        diagnostic_status=PlaceboCalibrationDiagnosticStatus.PLACEBO_CALIBRATION_DIAGNOSTIC_READY.value,
        authorized_for_diagnostic_summary=True,
        detected_placebo_risks=detected,
        missing_evidence=(),
        failure_code=None,
        failure_reason=None,
        retry_category=None,
    )


def _failure_code_for_missing(missing: tuple[str, ...]) -> str:
    if "placebo_assignment_manifest" in missing:
        return "MISSING_PLACEBO_ASSIGNMENT_MANIFEST"
    if "null_period_definition" in missing:
        return "MISSING_NULL_PERIOD_DEFINITION"
    return "MISSING_PLACEBO_ASSIGNMENT_MANIFEST"


def _retry_for_missing(missing: tuple[str, ...]) -> str:
    if "placebo_assignment_manifest" in missing:
        return "ADD_PLACEBO_ASSIGNMENT_MANIFEST"
    if "null_period_definition" in missing:
        return "ADD_NULL_PERIOD_DEFINITION"
    if "placebo_geometry_report" in missing:
        return "ADD_PLACEBO_GEOMETRY_REPORT"
    if "placebo_contamination_report" in missing:
        return "ADD_PLACEBO_CONTAMINATION_REPORT"
    if "placebo_count_report" in missing:
        return "ADD_PLACEBO_COUNT_REPORT"
    return "ADD_PLACEBO_ASSIGNMENT_MANIFEST"


def _risk_failure_code(risk_type: str) -> str:
    mapping = {
        "PRE_PERIOD_FIT_OVERCONFIDENCE": "PRE_PERIOD_FIT_OVERCONFIDENCE_RISK",
        "REGULARIZATION_MASKED_PLACEBO_FAILURE": "REGULARIZATION_MASKED_PLACEBO_FAILURE_RISK",
        "PLACEBO_METRIC_MISMATCH": "PLACEBO_TAIL_RANK_INSTABILITY",
        "UNBALANCED_PLACEBO_GEOMETRY": "PLACEBO_TAIL_RANK_INSTABILITY",
    }
    return mapping.get(risk_type, "PRE_PERIOD_FIT_OVERCONFIDENCE_RISK")


def validate_tbrridge_placebo_calibration_diagnostic_contract(
    contract: TbrridgePlaceboCalibrationDiagnosticContract,
) -> dict[str, Any]:
    issues: list[str] = []
    if len(contract.diagnostic_statuses) < 8:
        issues.append("diagnostic_statuses incomplete")
    if "INVALID_NULL_PERIOD" not in contract.placebo_risk_types:
        issues.append("placebo_risk_types incomplete")
    if "placebo_assignment_manifest" not in contract.required_evidence:
        issues.append("required_evidence incomplete")
    if "PLACEBO_P_VALUE_CLAIM" not in contract.prohibited_surfaces:
        issues.append("prohibited_surfaces incomplete")
    for flag, expected in _AUTH_FLAGS.items():
        if contract.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        if not getattr(contract, key, False):
            issues.append(f"contract positive flag {key} must be {expected}")
    return {"valid": not issues, "issues": issues}


def get_tbrridge_placebo_calibration_diagnostic_contract_metadata() -> dict[str, Any]:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
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


def list_placebo_risk_types() -> tuple[str, ...]:
    return PLACEBO_RISK_TYPES


def list_future_runtime_tests() -> tuple[str, ...]:
    return FUTURE_RUNTIME_TESTS


def build_scenarios() -> list[dict[str, Any]]:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    validation = validate_tbrridge_placebo_calibration_diagnostic_contract(contract)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for status in DIAGNOSTIC_STATUSES:
        scenarios.append(_s(f"status_{status}", status in contract.diagnostic_statuses))
    for risk in PLACEBO_RISK_TYPES:
        scenarios.append(_s(f"risk_{risk}", risk in contract.placebo_risk_types))

    full_evidence = {req: True for req in REQUIRED_EVIDENCE}
    ready = evaluate_placebo_calibration_diagnostic(evidence=full_evidence)
    scenarios.append(_s("diagnostic_ready_with_full_evidence", ready.authorized_for_diagnostic_summary))

    blocked_p = evaluate_placebo_calibration_diagnostic(
        evidence=full_evidence,
        requested_surface="PLACEBO_P_VALUE_CLAIM",
    )
    scenarios.append(_s("blocks_placebo_p_value_surface", not blocked_p.authorized_for_diagnostic_summary))

    invalid_null = evaluate_placebo_calibration_diagnostic(
        evidence=full_evidence,
        detected_risks=("INVALID_NULL_PERIOD",),
    )
    scenarios.append(_s("blocks_invalid_null_construction", not invalid_null.authorized_for_diagnostic_summary))

    contamination = evaluate_placebo_calibration_diagnostic(
        evidence=full_evidence,
        detected_risks=("PSEUDO_TREATED_CONTAMINATION",),
    )
    scenarios.append(_s("blocks_placebo_contamination", not contamination.authorized_for_diagnostic_summary))

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
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    validation = validate_tbrridge_placebo_calibration_diagnostic_contract(contract)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "tbrridge_placebo_calibration_diagnostic_contract",
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
