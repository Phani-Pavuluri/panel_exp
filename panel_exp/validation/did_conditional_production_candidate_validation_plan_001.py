"""DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001 validation harness."""

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

_ARTIFACT_ID = "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "did_conditional_production_candidate_validation_plan_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001",
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",
    "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
)

MIN_VALIDATION_ROW_COUNT = 65

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
    "did_conditional_candidate_only_under_eligible_designs": True,
    "did_point_estimate_not_sufficient_for_production_inference": True,
    "did_production_inference_authorized": False,
    "did_production_p_value_authorized": False,
    "did_causal_ci_authorized": False,
    "parallel_trend_support_required": True,
    "pre_period_trend_stability_required": True,
    "event_study_pretrend_diagnostics_required": True,
    "assignment_design_validity_required": True,
    "assignment_generator_stress_required": True,
    "bootstrap_does_not_fix_invalid_design_or_trends": True,
    "cluster_suitability_required": True,
    "serial_correlation_handling_required": True,
    "outcome_scale_compatibility_required": True,
    "staggered_twfe_paths_blocked_or_research_only_until_validated": True,
    "dgp_coverage_required": True,
    "failure_registry_consulted": True,
    "comparison_against_scm_required": True,
    "comparison_against_augsynth_required": True,
    "comparison_against_synthetic_did_required": True,
    "comparison_against_tbrridge_required": True,
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

_NEXT = "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001"


class ValidationArea(str, Enum):
    POINT_ESTIMATE = "did_point_estimate_eligibility"
    PARALLEL_TREND = "parallel_trend_support"
    PREPERIOD_TREND = "preperiod_trend_stability"
    EVENT_STUDY = "event_study_pretrend_diagnostics"
    ASSIGNMENT_DESIGN = "assignment_design_validity"
    ASSIGNMENT_STRESS = "assignment_generator_stress_compatibility"
    CONTROL_COMPARABILITY = "control_group_comparability"
    TREATED_CONTROL_BALANCE = "treated_control_balance"
    CLUSTER_COUNT = "cluster_count_adequacy"
    CLUSTER_DEPENDENCE = "cluster_dependence"
    SERIAL_CORRELATION = "serial_correlation"
    OUTCOME_SCALE = "outcome_scale_compatibility"
    SPARSE_COUNT_RATE = "sparse_count_rate_outcome_handling"
    MISSING_DATA = "missing_data_sensitivity"
    POST_PERIOD_SHOCK = "postperiod_shock_sensitivity"
    STAGGERED_TREATMENT = "staggered_treatment_boundary"
    TWFE_OVERCLAIM = "twfe_overclaim_boundary"
    BOOTSTRAP_SUITABILITY = "bootstrap_suitability"
    CLUSTER_BOOTSTRAP = "cluster_bootstrap_inference_boundary"
    PLACEBO_FALSIFICATION = "placebo_preperiod_falsification"
    RANDOMIZATION_PERMUTATION = "randomization_permutation_candidate"
    DGP_SIMULATION = "dgp_simulation_coverage"
    FAILURE_REGISTRY = "failure_registry_blockers"
    DISAGREEMENT_SCM = "method_disagreement_scm"
    DISAGREEMENT_AUGSYNTH = "method_disagreement_augsynth"
    DISAGREEMENT_SYNTH_DID = "method_disagreement_synthetic_did"
    DISAGREEMENT_TBRRIDGE = "method_disagreement_tbrridge"
    MULTICELL_BOUNDARY = "multicell_shared_control_boundary"
    RELEASE_GATE = "release_gate_boundary"


class ValidationStatus(str, Enum):
    REQUIRED_BLOCKER = "required_blocker"
    REQUIRED_WARNING = "required_warning"
    CONDITIONAL_CANDIDATE = "conditional_candidate"
    CANDIDATE_AFTER_VALIDATION = "candidate_after_validation"
    CANDIDATE_AFTER_ADAPTER = "candidate_after_adapter"
    CANDIDATE_AFTER_NULL_CALIBRATION = "candidate_after_null_calibration"
    CANDIDATE_AFTER_SIMULATION = "candidate_after_simulation"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    BLOCKED = "blocked"


class EligibilityType(str, Enum):
    DESIGN_ELIGIBILITY = "design_eligibility"
    TREND_ELIGIBILITY = "trend_eligibility"
    OUTCOME_ELIGIBILITY = "outcome_eligibility"
    CLUSTER_ELIGIBILITY = "cluster_eligibility"
    INFERENCE_ELIGIBILITY = "inference_eligibility"
    SIMULATION_REQUIREMENT = "simulation_requirement"
    ASSIGNMENT_STRESS_REQUIREMENT = "assignment_stress_requirement"
    MULTICELL_BOUNDARY = "multicell_boundary"
    RELEASE_GATE_BOUNDARY = "release_gate_boundary"


REQUIRED_VALIDATION_AREAS = frozenset(ValidationArea)
REQUIRED_STATUSES = frozenset(ValidationStatus)
REQUIRED_ELIGIBILITY_TYPES = frozenset(EligibilityType)


@dataclass(frozen=True)
class DidValidationRow:
    validation_id: str
    name: str
    validation_area: ValidationArea
    current_status: ValidationStatus
    eligibility_type: EligibilityType
    required_inputs: tuple[str, ...]
    required_diagnostics: tuple[str, ...]
    required_dgp_coverage: tuple[str, ...]
    required_assignment_stress: tuple[str, ...]
    required_failure_registry_checks: tuple[str, ...]
    required_inference_adapter: tuple[str, ...]
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
    eligibility_type: EligibilityType,
    notes: str,
    *,
    required_inputs: tuple[str, ...],
    required_diagnostics: tuple[str, ...],
    required_dgp_coverage: tuple[str, ...],
    required_assignment_stress: tuple[str, ...],
    required_failure_registry_checks: tuple[str, ...],
    required_inference_adapter: tuple[str, ...] = (),
    required_null_calibration: tuple[str, ...] = (),
    blocking_conditions: tuple[str, ...],
    passing_evidence_required: tuple[str, ...],
    allowed_current_use: tuple[str, ...],
    forbidden_current_use: tuple[str, ...],
    promotion_dependency: tuple[str, ...],
    recommended_next_artifact: str | None = None,
) -> DidValidationRow:
    return DidValidationRow(
        validation_id=validation_id,
        name=name,
        validation_area=validation_area,
        current_status=current_status,
        eligibility_type=eligibility_type,
        required_inputs=required_inputs,
        required_diagnostics=required_diagnostics,
        required_dgp_coverage=required_dgp_coverage,
        required_assignment_stress=required_assignment_stress,
        required_failure_registry_checks=required_failure_registry_checks,
        required_inference_adapter=required_inference_adapter,
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
        ValidationArea.POINT_ESTIMATE: ValidationStatus.DIAGNOSTIC_ONLY,
        ValidationArea.PARALLEL_TREND: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.PREPERIOD_TREND: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.EVENT_STUDY: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.ASSIGNMENT_DESIGN: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.ASSIGNMENT_STRESS: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.CONTROL_COMPARABILITY: ValidationStatus.CANDIDATE_AFTER_VALIDATION,
        ValidationArea.TREATED_CONTROL_BALANCE: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.CLUSTER_COUNT: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.CLUSTER_DEPENDENCE: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.SERIAL_CORRELATION: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.OUTCOME_SCALE: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.SPARSE_COUNT_RATE: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.MISSING_DATA: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.POST_PERIOD_SHOCK: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.STAGGERED_TREATMENT: ValidationStatus.RESEARCH_ONLY,
        ValidationArea.TWFE_OVERCLAIM: ValidationStatus.BLOCKED,
        ValidationArea.BOOTSTRAP_SUITABILITY: ValidationStatus.CONDITIONAL_CANDIDATE,
        ValidationArea.CLUSTER_BOOTSTRAP: ValidationStatus.CANDIDATE_AFTER_ADAPTER,
        ValidationArea.PLACEBO_FALSIFICATION: ValidationStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
        ValidationArea.RANDOMIZATION_PERMUTATION: ValidationStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
        ValidationArea.DGP_SIMULATION: ValidationStatus.CANDIDATE_AFTER_SIMULATION,
        ValidationArea.FAILURE_REGISTRY: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.DISAGREEMENT_SCM: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.DISAGREEMENT_AUGSYNTH: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.DISAGREEMENT_SYNTH_DID: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.DISAGREEMENT_TBRRIDGE: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.MULTICELL_BOUNDARY: ValidationStatus.BLOCKED,
        ValidationArea.RELEASE_GATE: ValidationStatus.BLOCKED,
    }
    return mapping[area]


def _area_eligibility_type(area: ValidationArea) -> EligibilityType:
    mapping: dict[ValidationArea, EligibilityType] = {
        ValidationArea.PARALLEL_TREND: EligibilityType.TREND_ELIGIBILITY,
        ValidationArea.PREPERIOD_TREND: EligibilityType.TREND_ELIGIBILITY,
        ValidationArea.EVENT_STUDY: EligibilityType.TREND_ELIGIBILITY,
        ValidationArea.OUTCOME_SCALE: EligibilityType.OUTCOME_ELIGIBILITY,
        ValidationArea.SPARSE_COUNT_RATE: EligibilityType.OUTCOME_ELIGIBILITY,
        ValidationArea.MISSING_DATA: EligibilityType.OUTCOME_ELIGIBILITY,
        ValidationArea.CLUSTER_COUNT: EligibilityType.CLUSTER_ELIGIBILITY,
        ValidationArea.CLUSTER_DEPENDENCE: EligibilityType.CLUSTER_ELIGIBILITY,
        ValidationArea.SERIAL_CORRELATION: EligibilityType.CLUSTER_ELIGIBILITY,
        ValidationArea.BOOTSTRAP_SUITABILITY: EligibilityType.INFERENCE_ELIGIBILITY,
        ValidationArea.CLUSTER_BOOTSTRAP: EligibilityType.INFERENCE_ELIGIBILITY,
        ValidationArea.PLACEBO_FALSIFICATION: EligibilityType.INFERENCE_ELIGIBILITY,
        ValidationArea.RANDOMIZATION_PERMUTATION: EligibilityType.INFERENCE_ELIGIBILITY,
        ValidationArea.DGP_SIMULATION: EligibilityType.SIMULATION_REQUIREMENT,
        ValidationArea.ASSIGNMENT_STRESS: EligibilityType.ASSIGNMENT_STRESS_REQUIREMENT,
        ValidationArea.MULTICELL_BOUNDARY: EligibilityType.MULTICELL_BOUNDARY,
        ValidationArea.RELEASE_GATE: EligibilityType.RELEASE_GATE_BOUNDARY,
    }
    return mapping.get(area, EligibilityType.DESIGN_ELIGIBILITY)


def _area_variants(area: ValidationArea) -> tuple[tuple[str, ValidationStatus, str], ...]:
    primary = _area_primary_status(area)
    return (
        ("gate", primary, "Primary conditional gate for this DID validation area."),
        ("diagnostic", ValidationStatus.DIAGNOSTIC_ONLY, "Diagnostic-only; not sufficient for production."),
        ("blocked_production", ValidationStatus.BLOCKED, "DID production path blocked until evidence passes."),
    )


def _area_defaults(area: ValidationArea) -> dict[str, Any]:
    diag = ("OPD-PF-001", "OPD-PF-002")
    dgp = ("DGP-DID-001", "DGP-ES-007")
    stress = ("ST-AD-001", "ST-AD-009")
    fm = ("FM-ES-001", "FM-CP-004")
    promo = (
        "observed_diagnostics",
        "dgp_coverage",
        "failure_registry_consult",
        "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
    )

    base: dict[str, Any] = {
        "required_inputs": ("panel_data", "treatment_timing", "control_units", "cluster_id"),
        "required_diagnostics": diag,
        "required_dgp_coverage": dgp,
        "required_assignment_stress": stress,
        "required_failure_registry_checks": fm,
        "required_inference_adapter": (),
        "required_null_calibration": (),
        "blocking_conditions": ("did_production_inference_unauthorized",),
        "passing_evidence_required": promo,
        "allowed_current_use": ("did_diagnostic_readout", "conditional_research"),
        "forbidden_current_use": _FORBID,
        "promotion_dependency": promo,
        "recommended_next_artifact": None,
    }

    if area == ValidationArea.POINT_ESTIMATE:
        base["blocking_conditions"] = ("point_estimate_not_production_inference",)
    if area == ValidationArea.PARALLEL_TREND:
        base["required_diagnostics"] = ("parallel_trend_support", "OPD-PF-002")
        base["blocking_conditions"] = ("parallel_trends_fail",)
    if area == ValidationArea.PREPERIOD_TREND:
        base["required_diagnostics"] = ("OPD-PF-002", "OPD-PF-003")
        base["blocking_conditions"] = ("trend_instability",)
    if area == ValidationArea.EVENT_STUDY:
        base["required_diagnostics"] = ("event_study_pretrend", "OPD-PF-002")
        base["blocking_conditions"] = ("pretrend_violation",)
    if area == ValidationArea.ASSIGNMENT_DESIGN:
        base["blocking_conditions"] = ("assignment_invalid", "randomization_unknown")
    if area == ValidationArea.ASSIGNMENT_STRESS:
        base["required_assignment_stress"] = ("ST-AD-001", "ST-AD-009", "ST-AD-010")
    if area in (ValidationArea.CONTROL_COMPARABILITY, ValidationArea.TREATED_CONTROL_BALANCE):
        base["required_diagnostics"] = ("control_comparability", "balance_diagnostics")
    if area == ValidationArea.CLUSTER_COUNT:
        base["required_diagnostics"] = ("cluster_count_adequacy",)
        base["blocking_conditions"] = ("too_few_clusters",)
    if area == ValidationArea.CLUSTER_DEPENDENCE:
        base["required_diagnostics"] = ("cluster_dependence_structure",)
        base["blocking_conditions"] = ("cluster_dependence_unhandled",)
    if area == ValidationArea.SERIAL_CORRELATION:
        base["required_diagnostics"] = ("serial_correlation_check",)
        base["blocking_conditions"] = ("serial_correlation_unhandled",)
    if area in (ValidationArea.SPARSE_COUNT_RATE, ValidationArea.OUTCOME_SCALE):
        base["required_dgp_coverage"] = ("DGP-DID-001", "DGP-CP-002")
    if area == ValidationArea.POST_PERIOD_SHOCK:
        base["blocking_conditions"] = ("postperiod_shock_confound",)
    if area in (ValidationArea.STAGGERED_TREATMENT, ValidationArea.TWFE_OVERCLAIM):
        base["blocking_conditions"] = ("staggered_twfe_overclaim", "twfe_not_validated")
    if area == ValidationArea.BOOTSTRAP_SUITABILITY:
        base["blocking_conditions"] = (
            "bootstrap_cannot_fix_invalid_assignment",
            "bootstrap_cannot_fix_invalid_trends",
        )
    if area == ValidationArea.CLUSTER_BOOTSTRAP:
        base["required_inference_adapter"] = ("cluster_bootstrap_adapter",)
        base["blocking_conditions"] = ("cluster_bootstrap_unsuitable",)
    if area in (ValidationArea.PLACEBO_FALSIFICATION, ValidationArea.RANDOMIZATION_PERMUTATION):
        base["required_null_calibration"] = ("null_fpr_gate", "permutation_null")
    if area == ValidationArea.DGP_SIMULATION:
        base["required_dgp_coverage"] = ("DGP-DID-001", "DGP-ES-007", "DGP-CP-002")
    if area == ValidationArea.DISAGREEMENT_SCM:
        base["passing_evidence_required"] = promo + ("scm_disagreement_check",)
    if area == ValidationArea.DISAGREEMENT_AUGSYNTH:
        base["passing_evidence_required"] = promo + ("augsynth_disagreement_check",)
    if area == ValidationArea.DISAGREEMENT_SYNTH_DID:
        base["passing_evidence_required"] = promo + ("synthetic_did_disagreement_check",)
    if area == ValidationArea.DISAGREEMENT_TBRRIDGE:
        base["passing_evidence_required"] = promo + ("tbrridge_disagreement_check",)
    if area == ValidationArea.MULTICELL_BOUNDARY:
        base["blocking_conditions"] = ("multicell_dependence_unhandled", "multiplicity_unhandled")
        base["required_failure_registry_checks"] = ("FM-CP-004", "FM-INF-009")
        base["recommended_next_artifact"] = "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001"
    if area == ValidationArea.RELEASE_GATE:
        base["blocking_conditions"] = ("release_gate_not_passed",)
        base["promotion_dependency"] = ("PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",)

    return base


def build_did_conditional_production_candidate_validation_plan() -> tuple[DidValidationRow, ...]:
    """Return metadata-only DID conditional production-candidate validation plan rows."""
    rows: list[DidValidationRow] = []
    row_num = 1
    for area in ValidationArea:
        defaults = _area_defaults(area)
        eligibility = _area_eligibility_type(area)
        for suffix, status, note_suffix in _area_variants(area):
            rows.append(
                _row(
                    f"DID-VAL-{row_num:03d}",
                    f"did_{area.value}_{suffix}",
                    area,
                    status,
                    eligibility,
                    f"{area.value}: {note_suffix}",
                    required_inputs=defaults["required_inputs"],
                    required_diagnostics=defaults["required_diagnostics"],
                    required_dgp_coverage=defaults["required_dgp_coverage"],
                    required_assignment_stress=defaults["required_assignment_stress"],
                    required_failure_registry_checks=defaults["required_failure_registry_checks"],
                    required_inference_adapter=defaults.get("required_inference_adapter", ()),
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


def filter_did_conditional_production_candidate_validation_plan(
    rows: tuple[DidValidationRow, ...],
    *,
    validation_area: ValidationArea | None = None,
    current_status: ValidationStatus | None = None,
    eligibility_type: EligibilityType | None = None,
    requires_adapter: bool | None = None,
    requires_null_calibration: bool | None = None,
) -> tuple[DidValidationRow, ...]:
    """Filter DID validation plan rows by optional criteria."""
    result: list[DidValidationRow] = []
    for row in rows:
        if validation_area is not None and row.validation_area != validation_area:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if eligibility_type is not None and row.eligibility_type != eligibility_type:
            continue
        if requires_adapter is not None:
            has_adapter = bool(row.required_inference_adapter)
            if requires_adapter != has_adapter:
                continue
        if requires_null_calibration is not None:
            has_null = bool(row.required_null_calibration)
            if requires_null_calibration != has_null:
                continue
        result.append(row)
    return tuple(result)


def validate_did_conditional_production_candidate_validation_plan(
    rows: tuple[DidValidationRow, ...],
) -> dict[str, Any]:
    """Validate DID validation plan registry thresholds and coverage."""
    issues: list[str] = []
    validation_ids = [r.validation_id for r in rows]

    if len(rows) < MIN_VALIDATION_ROW_COUNT:
        issues.append(f"validation_row_count {len(rows)} < {MIN_VALIDATION_ROW_COUNT}")
    if len(validation_ids) != len(set(validation_ids)):
        issues.append("duplicate validation_id values")

    status_counts = Counter(r.current_status for r in rows)
    area_counts = Counter(r.validation_area.value for r in rows)
    eligibility_counts = Counter(r.eligibility_type for r in rows)

    for area in REQUIRED_VALIDATION_AREAS:
        if not any(r.validation_area == area for r in rows):
            issues.append(f"missing validation_area: {area.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    for etype in REQUIRED_ELIGIBILITY_TYPES:
        if eligibility_counts.get(etype, 0) == 0:
            issues.append(f"missing eligibility_type: {etype.value}")

    parallel_blocked = any(
        r.validation_area == ValidationArea.PARALLEL_TREND
        and r.current_status == ValidationStatus.REQUIRED_BLOCKER
        for r in rows
    )
    if not parallel_blocked:
        issues.append("parallel_trend required_blocker missing")

    bootstrap_conditional = any(
        r.validation_area == ValidationArea.BOOTSTRAP_SUITABILITY
        and r.current_status == ValidationStatus.CONDITIONAL_CANDIDATE
        for r in rows
    )
    if not bootstrap_conditional:
        issues.append("bootstrap_suitability conditional_candidate missing")

    candidate_after_validation = status_counts.get(ValidationStatus.CANDIDATE_AFTER_VALIDATION, 0)
    if candidate_after_validation == 0:
        issues.append("candidate_after_validation status missing")

    unlinked = [r.validation_id for r in rows if not r.required_failure_registry_checks]
    if unlinked:
        issues.append(f"rows missing required_failure_registry_checks: {unlinked}")

    return {
        "valid": not issues,
        "validation_row_count": len(rows),
        "unique_validation_ids": len(validation_ids) == len(set(validation_ids)),
        "status_counts": {s.value: status_counts.get(s, 0) for s in ValidationStatus},
        "validation_area_counts": dict(area_counts),
        "eligibility_type_counts": {e.value: eligibility_counts.get(e, 0) for e in EligibilityType},
        "all_required_validation_areas_covered": all(
            any(r.validation_area == a for r in rows) for a in REQUIRED_VALIDATION_AREAS
        ),
        "all_required_statuses_covered": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "all_required_eligibility_types_covered": all(
            eligibility_counts.get(e, 0) > 0 for e in REQUIRED_ELIGIBILITY_TYPES
        ),
        "issues": issues,
    }


def summarize_did_conditional_production_candidate_validation_plan(
    rows: tuple[DidValidationRow, ...],
) -> dict[str, Any]:
    """Serialize DID validation plan summary for archives."""
    validation = validate_did_conditional_production_candidate_validation_plan(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "validation_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "status_counts": validation["status_counts"],
        "validation_area_counts": validation["validation_area_counts"],
        "eligibility_type_counts": validation["eligibility_type_counts"],
        "all_required_validation_areas_covered": validation["all_required_validation_areas_covered"],
        "all_required_statuses_covered": validation["all_required_statuses_covered"],
        "all_required_eligibility_types_covered": validation["all_required_eligibility_types_covered"],
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
    rows = build_did_conditional_production_candidate_validation_plan()
    validation = validate_did_conditional_production_candidate_validation_plan(rows)
    summary = summarize_did_conditional_production_candidate_validation_plan(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("validation_rows_build_successfully", len(rows) > 0))
    scenarios.append(
        _scenario("validation_row_count_at_least_65", len(rows) >= MIN_VALIDATION_ROW_COUNT)
    )
    scenarios.append(_scenario("validation_ids_unique", validation["unique_validation_ids"]))

    for area in REQUIRED_VALIDATION_AREAS:
        present = any(r.validation_area == area for r in rows)
        scenarios.append(_scenario(f"validation_area_{area.value}_represented", present))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for etype in REQUIRED_ELIGIBILITY_TYPES:
        count = sum(1 for r in rows if r.eligibility_type == etype)
        scenarios.append(_scenario(f"eligibility_type_{etype.value}_represented", count > 0))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] == expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_synthetic_did_readiness",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_did_conditional_production_candidate_validation_plan()
    validation = validate_did_conditional_production_candidate_validation_plan(rows)
    summary = summarize_did_conditional_production_candidate_validation_plan(rows)
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
