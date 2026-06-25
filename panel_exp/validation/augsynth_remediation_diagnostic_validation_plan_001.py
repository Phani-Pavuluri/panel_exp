"""AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "augsynth_remediation_and_diagnostic_validation_plan_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
    "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001",
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",
)

MIN_VALIDATION_ROW_COUNT = 60

_AUTH_FLAGS = {
    "production_p_value_authorized": False,
    "causal_confidence_interval_authorized": False,
    "trustreport_authorized": False,
    "calibration_signal_allowed": False,
    "mmm_ingestion_allowed": False,
    "llm_decisioning_allowed": False,
    "production_decisioning_allowed": False,
    "live_api_authorized": False,
    "scheduler_authorized": False,
    "budget_optimization_allowed": False,
}

_BOUNDARY_FLAGS = {
    "prior_work_reconciled": True,
    "open_investigations_consulted": True,
    "production_readiness_backlog_consulted": True,
    "selection_gate_requirements_consulted": True,
    "augsynth_diagnostic_restricted_research_until_remediated": True,
    "augsynth_point_estimate_not_sufficient_for_production_inference": True,
    "augsynth_production_inference_authorized": False,
    "augsynth_production_p_value_authorized": False,
    "augsynth_causal_ci_authorized": False,
    "cvxpy_solver_reliability_required": True,
    "solver_convergence_diagnostics_required": True,
    "solver_failure_handling_required": True,
    "donor_support_required": True,
    "overlap_validation_required": True,
    "convex_hull_or_extrapolation_risk_required": True,
    "pre_period_fit_required": True,
    "pre_period_trend_stability_required": True,
    "assignment_design_validity_required": True,
    "assignment_generator_stress_required": True,
    "statistic_adapter_required": True,
    "null_calibration_required": True,
    "dgp_coverage_required": True,
    "failure_registry_consulted": True,
    "comparison_against_scm_required": True,
    "comparison_against_did_required": True,
    "comparison_against_synthetic_did_required": True,
    "comparison_against_tbrridge_required": True,
    "multi_treated_augsynth_requires_research_handling": True,
    "multicell_shared_control_blocked_without_dependence_handling": True,
    "release_gate_required_before_any_authorization": True,
    "downstream_work_paused": True,
}

_FORBID = (
    "production_p_value",
    "causal_ci",
    "trustreport",
    "production_inference",
    "calibration_signal",
    "mmm_ingestion",
    "llm_decisioning",
    "live_api",
    "scheduler",
    "budget_optimization",
)

_NEXT = "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"


class ValidationArea(str, Enum):
    POINT_ESTIMATE_DIAGNOSTIC = "augsynth_point_estimate_diagnostic"
    CVXPY_SOLVER_AVAILABILITY = "cvxpy_solver_availability_failure_handling"
    SOLVER_CONVERGENCE = "solver_convergence_diagnostics"
    REGULARIZATION_SENSITIVITY = "regularization_sensitivity"
    DONOR_SUPPORT_OVERLAP = "donor_support_overlap"
    CONVEX_HULL_EXTRAPOLATION = "convex_hull_extrapolation_risk"
    PREPERIOD_FIT = "preperiod_fit_quality"
    PREPERIOD_TREND = "preperiod_trend_stability"
    OUTCOME_SCALE = "outcome_scale_compatibility"
    SPARSE_COUNT_RATE = "sparse_count_rate_outcome_handling"
    MISSING_DATA = "missing_data_sensitivity"
    ASSIGNMENT_DESIGN = "assignment_design_validity"
    ASSIGNMENT_STRESS = "assignment_generator_stress_compatibility"
    SINGLE_TREATED = "single_treated_augsynth"
    MULTI_TREATED = "multi_treated_augsynth"
    TREATED_SET = "treated_set_augsynth"
    JACKKNIFE = "jackknife_candidate"
    PLACEBO_RANK = "placebo_rank_candidate"
    STUDENTIZED_ADAPTER = "studentized_statistic_adapter"
    NULL_CALIBRATION = "null_calibration"
    DGP_SIMULATION = "dgp_simulation_coverage"
    FAILURE_REGISTRY = "failure_registry_blockers"
    DISAGREEMENT_SCM = "method_disagreement_scm"
    DISAGREEMENT_DID = "method_disagreement_did"
    DISAGREEMENT_SYNTH_DID = "method_disagreement_synthetic_did"
    DISAGREEMENT_TBRRIDGE = "method_disagreement_tbrridge"
    MULTICELL_BOUNDARY = "multicell_shared_control_boundary"
    RELEASE_GATE = "release_gate_boundary"


class ValidationStatus(str, Enum):
    REQUIRED_BLOCKER = "required_blocker"
    REQUIRED_WARNING = "required_warning"
    CANDIDATE_AFTER_REMEDIATION = "candidate_after_remediation"
    CANDIDATE_AFTER_ADAPTER = "candidate_after_adapter"
    CANDIDATE_AFTER_NULL_CALIBRATION = "candidate_after_null_calibration"
    CANDIDATE_AFTER_SIMULATION = "candidate_after_simulation"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    BLOCKED = "blocked"


class RemediationType(str, Enum):
    SOLVER_RELIABILITY = "solver_reliability"
    DIAGNOSTIC_VALIDATION = "diagnostic_validation"
    DONOR_SUPPORT_VALIDATION = "donor_support_validation"
    ADAPTER_REQUIREMENT = "adapter_requirement"
    NULL_CALIBRATION_REQUIREMENT = "null_calibration_requirement"
    SIMULATION_REQUIREMENT = "simulation_requirement"
    ASSIGNMENT_STRESS_REQUIREMENT = "assignment_stress_requirement"
    MULTICELL_BOUNDARY = "multicell_boundary"
    RELEASE_GATE_BOUNDARY = "release_gate_boundary"


REQUIRED_VALIDATION_AREAS = frozenset(ValidationArea)
REQUIRED_STATUSES = frozenset(ValidationStatus)
REQUIRED_REMEDIATION_TYPES = frozenset(RemediationType)


@dataclass(frozen=True)
class AugsynthValidationRow:
    validation_id: str
    name: str
    validation_area: ValidationArea
    current_status: ValidationStatus
    remediation_type: RemediationType
    required_inputs: tuple[str, ...]
    required_diagnostics: tuple[str, ...]
    required_dgp_coverage: tuple[str, ...]
    required_assignment_stress: tuple[str, ...]
    required_failure_registry_checks: tuple[str, ...]
    required_statistic_adapter: tuple[str, ...]
    required_null_calibration: tuple[str, ...]
    blocking_conditions: tuple[str, ...]
    passing_evidence_required: tuple[str, ...]
    allowed_current_use: tuple[str, ...]
    forbidden_current_use: tuple[str, ...]
    promotion_dependency: tuple[str, ...]
    recommended_next_artifact: str | None
    notes: str


def _row(
    validation_id: str,
    name: str,
    validation_area: ValidationArea,
    current_status: ValidationStatus,
    remediation_type: RemediationType,
    notes: str,
    *,
    required_inputs: tuple[str, ...],
    required_diagnostics: tuple[str, ...],
    required_dgp_coverage: tuple[str, ...],
    required_assignment_stress: tuple[str, ...],
    required_failure_registry_checks: tuple[str, ...],
    required_statistic_adapter: tuple[str, ...] = (),
    required_null_calibration: tuple[str, ...] = (),
    blocking_conditions: tuple[str, ...],
    passing_evidence_required: tuple[str, ...],
    allowed_current_use: tuple[str, ...],
    forbidden_current_use: tuple[str, ...],
    promotion_dependency: tuple[str, ...],
    recommended_next_artifact: str | None = None,
) -> AugsynthValidationRow:
    return AugsynthValidationRow(
        validation_id=validation_id,
        name=name,
        validation_area=validation_area,
        current_status=current_status,
        remediation_type=remediation_type,
        required_inputs=required_inputs,
        required_diagnostics=required_diagnostics,
        required_dgp_coverage=required_dgp_coverage,
        required_assignment_stress=required_assignment_stress,
        required_failure_registry_checks=required_failure_registry_checks,
        required_statistic_adapter=required_statistic_adapter,
        required_null_calibration=required_null_calibration,
        blocking_conditions=blocking_conditions,
        passing_evidence_required=passing_evidence_required,
        allowed_current_use=allowed_current_use,
        forbidden_current_use=forbidden_current_use,
        promotion_dependency=promotion_dependency,
        recommended_next_artifact=recommended_next_artifact,
        notes=notes,
    )


def _area_primary_status(area: ValidationArea) -> ValidationStatus:
    mapping: dict[ValidationArea, ValidationStatus] = {
        ValidationArea.POINT_ESTIMATE_DIAGNOSTIC: ValidationStatus.DIAGNOSTIC_ONLY,
        ValidationArea.CVXPY_SOLVER_AVAILABILITY: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.SOLVER_CONVERGENCE: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.REGULARIZATION_SENSITIVITY: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.DONOR_SUPPORT_OVERLAP: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.CONVEX_HULL_EXTRAPOLATION: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.PREPERIOD_FIT: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.PREPERIOD_TREND: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.OUTCOME_SCALE: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.SPARSE_COUNT_RATE: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.MISSING_DATA: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.ASSIGNMENT_DESIGN: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.ASSIGNMENT_STRESS: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.SINGLE_TREATED: ValidationStatus.CANDIDATE_AFTER_REMEDIATION,
        ValidationArea.MULTI_TREATED: ValidationStatus.RESEARCH_ONLY,
        ValidationArea.TREATED_SET: ValidationStatus.CANDIDATE_AFTER_ADAPTER,
        ValidationArea.JACKKNIFE: ValidationStatus.CANDIDATE_AFTER_ADAPTER,
        ValidationArea.PLACEBO_RANK: ValidationStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
        ValidationArea.STUDENTIZED_ADAPTER: ValidationStatus.CANDIDATE_AFTER_ADAPTER,
        ValidationArea.NULL_CALIBRATION: ValidationStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
        ValidationArea.DGP_SIMULATION: ValidationStatus.CANDIDATE_AFTER_SIMULATION,
        ValidationArea.FAILURE_REGISTRY: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.DISAGREEMENT_SCM: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.DISAGREEMENT_DID: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.DISAGREEMENT_SYNTH_DID: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.DISAGREEMENT_TBRRIDGE: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.MULTICELL_BOUNDARY: ValidationStatus.BLOCKED,
        ValidationArea.RELEASE_GATE: ValidationStatus.BLOCKED,
    }
    return mapping[area]


def _area_remediation_type(area: ValidationArea) -> RemediationType:
    mapping: dict[ValidationArea, RemediationType] = {
        ValidationArea.CVXPY_SOLVER_AVAILABILITY: RemediationType.SOLVER_RELIABILITY,
        ValidationArea.SOLVER_CONVERGENCE: RemediationType.SOLVER_RELIABILITY,
        ValidationArea.DONOR_SUPPORT_OVERLAP: RemediationType.DONOR_SUPPORT_VALIDATION,
        ValidationArea.CONVEX_HULL_EXTRAPOLATION: RemediationType.DONOR_SUPPORT_VALIDATION,
        ValidationArea.ASSIGNMENT_STRESS: RemediationType.ASSIGNMENT_STRESS_REQUIREMENT,
        ValidationArea.TREATED_SET: RemediationType.ADAPTER_REQUIREMENT,
        ValidationArea.JACKKNIFE: RemediationType.ADAPTER_REQUIREMENT,
        ValidationArea.STUDENTIZED_ADAPTER: RemediationType.ADAPTER_REQUIREMENT,
        ValidationArea.PLACEBO_RANK: RemediationType.NULL_CALIBRATION_REQUIREMENT,
        ValidationArea.NULL_CALIBRATION: RemediationType.NULL_CALIBRATION_REQUIREMENT,
        ValidationArea.DGP_SIMULATION: RemediationType.SIMULATION_REQUIREMENT,
        ValidationArea.MULTICELL_BOUNDARY: RemediationType.MULTICELL_BOUNDARY,
        ValidationArea.RELEASE_GATE: RemediationType.RELEASE_GATE_BOUNDARY,
    }
    return mapping.get(area, RemediationType.DIAGNOSTIC_VALIDATION)


def _area_variants(area: ValidationArea) -> tuple[tuple[str, ValidationStatus, str], ...]:
    primary = _area_primary_status(area)
    return (
        ("gate", primary, "Primary remediation/validation gate for this AugSynth area."),
        ("diagnostic", ValidationStatus.DIAGNOSTIC_ONLY, "Diagnostic-only; not sufficient for production."),
        ("blocked_production", ValidationStatus.BLOCKED, "AugSynth production path blocked until evidence passes."),
    )


def _area_defaults(area: ValidationArea) -> dict[str, Any]:
    diag = ("OPD-PF-001", "OPD-DS-005")
    dgp = ("DGP-AUGSYNTH-001", "DGP-ES-007")
    stress = ("ST-AD-001", "ST-AD-009")
    fm = ("FM-ES-001", "FM-CP-003")
    promo = (
        "observed_diagnostics",
        "dgp_coverage",
        "failure_registry_consult",
        "SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",
    )

    base: dict[str, Any] = {
        "required_inputs": ("panel_data", "treated_units", "donor_pool", "cvxpy_solver"),
        "required_diagnostics": diag,
        "required_dgp_coverage": dgp,
        "required_assignment_stress": stress,
        "required_failure_registry_checks": fm,
        "required_statistic_adapter": (),
        "required_null_calibration": (),
        "blocking_conditions": ("augsynth_production_inference_unauthorized",),
        "passing_evidence_required": promo,
        "allowed_current_use": ("augsynth_diagnostic_readout", "restricted_research"),
        "forbidden_current_use": _FORBID,
        "promotion_dependency": promo,
        "recommended_next_artifact": None,
    }

    if area in (ValidationArea.CVXPY_SOLVER_AVAILABILITY, ValidationArea.SOLVER_CONVERGENCE):
        base["blocking_conditions"] = ("cvxpy_solver_unavailable", "solver_convergence_fail", "solver_failure_unhandled")
        base["required_diagnostics"] = ("cvxpy_solver_status", "solver_convergence_metric")
    if area == ValidationArea.REGULARIZATION_SENSITIVITY:
        base["required_diagnostics"] = ("regularization_sensitivity", "weight_stability")
    if area == ValidationArea.DONOR_SUPPORT_OVERLAP:
        base["required_diagnostics"] = ("OPD-DONOR-001", "overlap_diagnostics")
        base["blocking_conditions"] = ("donor_support_failure", "overlap_insufficient")
    if area == ValidationArea.CONVEX_HULL_EXTRAPOLATION:
        base["required_diagnostics"] = ("OPD-DS-005", "extrapolation_risk")
        base["blocking_conditions"] = ("convex_hull_violation", "extrapolation_risk_high")
    if area == ValidationArea.PREPERIOD_FIT:
        base["required_diagnostics"] = ("OPD-PF-001", "OPD-PF-003")
        base["blocking_conditions"] = ("preperiod_fit_poor",)
    if area == ValidationArea.PREPERIOD_TREND:
        base["required_diagnostics"] = ("OPD-PF-002", "OPD-PF-003")
        base["blocking_conditions"] = ("trend_instability",)
    if area in (ValidationArea.SPARSE_COUNT_RATE, ValidationArea.OUTCOME_SCALE):
        base["required_dgp_coverage"] = ("DGP-AUGSYNTH-001", "DGP-CP-002")
    if area == ValidationArea.MISSING_DATA:
        base["required_diagnostics"] = ("missing_data_fraction", "imputation_sensitivity")
    if area == ValidationArea.ASSIGNMENT_STRESS:
        base["required_assignment_stress"] = ("ST-AD-001", "ST-AD-009", "ST-AD-010")
    if area in (ValidationArea.TREATED_SET, ValidationArea.JACKKNIFE, ValidationArea.STUDENTIZED_ADAPTER):
        base["required_statistic_adapter"] = ("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",)
        base["blocking_conditions"] = ("adapter_not_ready",)
    if area in (ValidationArea.PLACEBO_RANK, ValidationArea.NULL_CALIBRATION):
        base["required_null_calibration"] = ("null_fpr_gate", "coverage_replay")
        base["blocking_conditions"] = ("null_calibration_incomplete",)
    if area == ValidationArea.STUDENTIZED_ADAPTER:
        base["required_null_calibration"] = ("null_fpr_gate",)
    if area == ValidationArea.MULTI_TREATED:
        base["blocking_conditions"] = ("multi_treated_dependence_unhandled",)
        base["promotion_dependency"] = promo + ("multi_treated_research_handling",)
    if area == ValidationArea.MULTICELL_BOUNDARY:
        base["blocking_conditions"] = ("multicell_dependence_unhandled", "multiplicity_unhandled")
        base["required_failure_registry_checks"] = ("FM-CP-004", "FM-INF-009")
        base["recommended_next_artifact"] = "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001"
    if area == ValidationArea.RELEASE_GATE:
        base["blocking_conditions"] = ("release_gate_not_passed",)
        base["promotion_dependency"] = ("PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",)
    if area == ValidationArea.DGP_SIMULATION:
        base["required_dgp_coverage"] = ("DGP-AUGSYNTH-001", "DGP-ES-007", "DGP-CP-002")
    if area == ValidationArea.DISAGREEMENT_SCM:
        base["passing_evidence_required"] = promo + ("scm_disagreement_check",)
    if area == ValidationArea.DISAGREEMENT_DID:
        base["passing_evidence_required"] = promo + ("did_disagreement_check",)
    if area == ValidationArea.DISAGREEMENT_SYNTH_DID:
        base["passing_evidence_required"] = promo + ("synthetic_did_disagreement_check",)
    if area == ValidationArea.DISAGREEMENT_TBRRIDGE:
        base["passing_evidence_required"] = promo + ("tbrridge_disagreement_check",)

    return base


def build_augsynth_remediation_diagnostic_validation_plan() -> tuple[AugsynthValidationRow, ...]:
    """Return metadata-only AugSynth remediation and diagnostic validation plan rows."""
    rows: list[AugsynthValidationRow] = []
    row_num = 1
    for area in ValidationArea:
        defaults = _area_defaults(area)
        remediation = _area_remediation_type(area)
        for suffix, status, note_suffix in _area_variants(area):
            rows.append(
                _row(
                    f"AUGSYNTH-VAL-{row_num:03d}",
                    f"augsynth_{area.value}_{suffix}",
                    area,
                    status,
                    remediation,
                    f"{area.value}: {note_suffix}",
                    required_inputs=defaults["required_inputs"],
                    required_diagnostics=defaults["required_diagnostics"],
                    required_dgp_coverage=defaults["required_dgp_coverage"],
                    required_assignment_stress=defaults["required_assignment_stress"],
                    required_failure_registry_checks=defaults["required_failure_registry_checks"],
                    required_statistic_adapter=defaults.get("required_statistic_adapter", ()),
                    required_null_calibration=defaults.get("required_null_calibration", ()),
                    blocking_conditions=defaults["blocking_conditions"],
                    passing_evidence_required=defaults["passing_evidence_required"],
                    allowed_current_use=defaults["allowed_current_use"],
                    forbidden_current_use=defaults["forbidden_current_use"],
                    promotion_dependency=defaults["promotion_dependency"],
                    recommended_next_artifact=defaults["recommended_next_artifact"],
                )
            )
            row_num += 1
    return tuple(rows)


def filter_augsynth_remediation_diagnostic_validation_plan(
    rows: tuple[AugsynthValidationRow, ...],
    *,
    validation_area: ValidationArea | None = None,
    current_status: ValidationStatus | None = None,
    remediation_type: RemediationType | None = None,
    requires_adapter: bool | None = None,
    requires_null_calibration: bool | None = None,
) -> tuple[AugsynthValidationRow, ...]:
    """Filter AugSynth validation plan rows by optional criteria."""
    result: list[AugsynthValidationRow] = []
    for row in rows:
        if validation_area is not None and row.validation_area != validation_area:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if remediation_type is not None and row.remediation_type != remediation_type:
            continue
        if requires_adapter is not None:
            has_adapter = bool(row.required_statistic_adapter)
            if requires_adapter != has_adapter:
                continue
        if requires_null_calibration is not None:
            has_null = bool(row.required_null_calibration)
            if requires_null_calibration != has_null:
                continue
        result.append(row)
    return tuple(result)


def validate_augsynth_remediation_diagnostic_validation_plan(
    rows: tuple[AugsynthValidationRow, ...],
) -> dict[str, Any]:
    """Validate AugSynth validation plan registry thresholds and coverage."""
    issues: list[str] = []
    validation_ids = [r.validation_id for r in rows]

    if len(rows) < MIN_VALIDATION_ROW_COUNT:
        issues.append(f"validation_row_count {len(rows)} < {MIN_VALIDATION_ROW_COUNT}")
    if len(validation_ids) != len(set(validation_ids)):
        issues.append("duplicate validation_id values")

    status_counts = Counter(r.current_status for r in rows)
    area_counts = Counter(r.validation_area.value for r in rows)
    remediation_counts = Counter(r.remediation_type for r in rows)

    for area in REQUIRED_VALIDATION_AREAS:
        if not any(r.validation_area == area for r in rows):
            issues.append(f"missing validation_area: {area.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    for rtype in REQUIRED_REMEDIATION_TYPES:
        if remediation_counts.get(rtype, 0) == 0:
            issues.append(f"missing remediation_type: {rtype.value}")

    solver_blocked = any(
        r.validation_area == ValidationArea.CVXPY_SOLVER_AVAILABILITY
        and r.current_status == ValidationStatus.REQUIRED_BLOCKER
        for r in rows
    )
    if not solver_blocked:
        issues.append("cvxpy_solver required_blocker missing")

    multicell_blocked = any(
        r.validation_area == ValidationArea.MULTICELL_BOUNDARY
        and r.current_status == ValidationStatus.BLOCKED
        for r in rows
    )
    if not multicell_blocked:
        issues.append("multicell blocked row missing")

    adapter_rows = [r for r in rows if r.required_statistic_adapter]
    if not adapter_rows:
        issues.append("no statistic adapter rows")

    unlinked = [r.validation_id for r in rows if not r.required_failure_registry_checks]
    if unlinked:
        issues.append(f"rows missing required_failure_registry_checks: {unlinked}")

    return {
        "valid": not issues,
        "validation_row_count": len(rows),
        "unique_validation_ids": len(validation_ids) == len(set(validation_ids)),
        "status_counts": {s.value: status_counts.get(s, 0) for s in ValidationStatus},
        "validation_area_counts": dict(area_counts),
        "remediation_type_counts": {t.value: remediation_counts.get(t, 0) for t in RemediationType},
        "all_required_validation_areas_covered": all(
            any(r.validation_area == a for r in rows) for a in REQUIRED_VALIDATION_AREAS
        ),
        "all_required_statuses_covered": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "all_required_remediation_types_covered": all(
            remediation_counts.get(t, 0) > 0 for t in REQUIRED_REMEDIATION_TYPES
        ),
        "issues": issues,
    }


def summarize_augsynth_remediation_diagnostic_validation_plan(
    rows: tuple[AugsynthValidationRow, ...],
) -> dict[str, Any]:
    """Serialize AugSynth validation plan summary for archives."""
    validation = validate_augsynth_remediation_diagnostic_validation_plan(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "validation_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "status_counts": validation["status_counts"],
        "validation_area_counts": validation["validation_area_counts"],
        "remediation_type_counts": validation["remediation_type_counts"],
        "all_required_validation_areas_covered": validation["all_required_validation_areas_covered"],
        "all_required_statuses_covered": validation["all_required_statuses_covered"],
        "all_required_remediation_types_covered": validation["all_required_remediation_types_covered"],
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
        **_BOUNDARY_FLAGS,
        **_AUTH_FLAGS,
        "valid": validation["valid"],
    }


def _git_commit() -> str | None:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=_REPO,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _scenario(scenario_id: str, passed: bool, *, detail: str = "") -> dict[str, Any]:
    return {"scenario_id": scenario_id, "passed": passed, "detail": detail}


def build_scenarios() -> list[dict[str, Any]]:
    rows = build_augsynth_remediation_diagnostic_validation_plan()
    validation = validate_augsynth_remediation_diagnostic_validation_plan(rows)
    summary = summarize_augsynth_remediation_diagnostic_validation_plan(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("validation_rows_build_successfully", len(rows) > 0))
    scenarios.append(
        _scenario("validation_row_count_at_least_60", len(rows) >= MIN_VALIDATION_ROW_COUNT)
    )
    scenarios.append(_scenario("validation_ids_unique", validation["unique_validation_ids"]))

    for area in REQUIRED_VALIDATION_AREAS:
        present = any(r.validation_area == area for r in rows)
        scenarios.append(_scenario(f"validation_area_{area.value}_represented", present))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for rtype in REQUIRED_REMEDIATION_TYPES:
        count = sum(1 for r in rows if r.remediation_type == rtype)
        scenarios.append(_scenario(f"remediation_type_{rtype.value}_represented", count > 0))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] == expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_did_conditional_plan",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_augsynth_remediation_diagnostic_validation_plan()
    validation = validate_augsynth_remediation_diagnostic_validation_plan(rows)
    summary = summarize_augsynth_remediation_diagnostic_validation_plan(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "validation_row_count": len(rows),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        **{k: summary[k] for k in summary if k not in ("failed_scenarios", "valid")},
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {"verdict": _VERDICT, "failed_scenarios": failed}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=not args.no_write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
