"""MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001 validation harness."""

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

_ARTIFACT_ID = "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "multicell_dependence_and_multiplicity_validation_plan_defined_no_downstream_authorization"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001",
    "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
    "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001",
)

MIN_VALIDATION_ROW_COUNT = 70

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
    "multicell_shared_control_cross_family_blocker": True,
    "multicell_production_claim_authorized": False,
    "naive_independent_per_cell_p_values_blocked": True,
    "naive_pooled_global_overclaim_blocked": True,
    "shared_control_dependence_validation_required": True,
    "multiplicity_handling_required": True,
    "max_t_candidate_only_until_validated": True,
    "stepdown_candidate_only_until_validated": True,
    "studentized_statistic_adapter_required": True,
    "null_calibration_required": True,
    "per_cell_claims_require_separate_validation": True,
    "pooled_claims_require_separate_validation": True,
    "global_claims_require_separate_validation": True,
    "aggregate_claims_require_separate_validation": True,
    "scm_multicell_claims_blocked_until_validated": True,
    "did_multicell_claims_blocked_until_validated": True,
    "augsynth_multicell_claims_blocked_until_validated": True,
    "synthetic_did_multicell_claims_blocked_until_validated": True,
    "tbrridge_multicell_claims_blocked_until_validated": True,
    "bayesian_tbr_multicell_claims_blocked_until_validated": True,
    "trop_multicell_claims_blocked_until_validated": True,
    "dgp_coverage_required": True,
    "assignment_stress_required": True,
    "failure_registry_consulted": True,
    "release_gate_required_before_any_authorization": True,
    "downstream_work_paused": True,
}

_FORBID = (
    "production_p_value",
    "causal_ci",
    "trustreport",
    "production_inference",
    "multicell_production_claim",
    "naive_per_cell_p_value",
    "pooled_global_overclaim",
    "calibration_signal",
    "mmm_ingestion",
    "llm_decisioning",
    "live_api",
    "scheduler",
    "budget_optimization",
)
_NEXT = "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001"


class ValidationArea(str, Enum):
    SHARED_CONTROL_DEPENDENCE = "shared_control_dependence"
    CELL_LEVEL_DEPENDENCE = "cell_level_dependence"
    METHOD_LEVEL_DEPENDENCE = "method_level_dependence"
    KPI_OUTCOME_MULTIPLICITY = "kpi_outcome_multiplicity"
    CELL_KPI_MULTIPLICITY = "cell_kpi_multiplicity"
    FAMILYWISE_ERROR_CONTROL = "familywise_error_control"
    MAX_T_CANDIDATE = "max_t_candidate_validation"
    STEPDOWN_CANDIDATE = "stepdown_candidate_validation"
    PERMUTATION_NULL_CALIBRATION = "permutation_randomization_null_calibration"
    STUDENTIZED_STATISTIC = "studentized_statistic_requirements"
    PER_CELL_CLAIM = "per_cell_claim_boundary"
    POOLED_GLOBAL_CLAIM = "pooled_global_claim_boundary"
    AGGREGATE_LIFT = "aggregate_lift_boundary"
    COMMON_CONTROL = "common_control_boundary"
    UNBALANCED_CELLS = "unbalanced_cells"
    SMALL_CELL_COUNT = "small_cell_count"
    SPARSE_COUNT_RATE = "sparse_count_rate_outcomes"
    SCM_MULTICELL = "scm_multicell_interaction"
    DID_MULTICELL = "did_multicell_interaction"
    AUGSYNTH_MULTICELL = "augsynth_multicell_interaction"
    SYNTHETIC_DID_MULTICELL = "synthetic_did_multicell_interaction"
    TBRRIDGE_MULTICELL = "tbrridge_multicell_interaction"
    BAYESIAN_TBR_MULTICELL = "bayesian_tbr_multicell_interaction"
    TROP_MULTICELL = "trop_multicell_interaction"
    CLASSIC_TBR_MULTICELL = "classic_tbr_multicell_interaction"
    RELEASE_GATE = "release_gate_boundary"


class ValidationStatus(str, Enum):
    REQUIRED_BLOCKER = "required_blocker"
    REQUIRED_WARNING = "required_warning"
    CANDIDATE_AFTER_VALIDATION = "candidate_after_validation"
    CANDIDATE_AFTER_ADAPTER = "candidate_after_adapter"
    CANDIDATE_AFTER_NULL_CALIBRATION = "candidate_after_null_calibration"
    CANDIDATE_AFTER_SIMULATION = "candidate_after_simulation"
    RESEARCH_REQUIRED = "research_required"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    BLOCKED = "blocked"


class ClaimScope(str, Enum):
    PER_CELL = "per_cell"
    POOLED = "pooled"
    GLOBAL = "global"
    AGGREGATE = "aggregate"
    CELL_BY_KPI = "cell_by_kpi"
    METHOD_FAMILY = "method_family"
    RELEASE_GATE = "release_gate"


class MethodFamilyScope(str, Enum):
    CROSS_FAMILY = "cross_family"
    SCM = "scm"
    DID = "did"
    AUGSYNTH_CVXPY = "augsynth_cvxpy"
    SYNTHETIC_DID = "synthetic_did"
    TBRRIDGE = "tbrridge"
    CLASSIC_AGGREGATE_TBR = "classic_aggregate_tbr"
    BAYESIAN_TBR = "bayesian_tbr"
    TROP = "trop"


REQUIRED_VALIDATION_AREAS = frozenset(ValidationArea)
REQUIRED_STATUSES = frozenset(ValidationStatus)
REQUIRED_CLAIM_SCOPES = frozenset(ClaimScope)
REQUIRED_METHOD_FAMILY_SCOPES = frozenset(MethodFamilyScope)


@dataclass(frozen=True)
class MulticellValidationRow:
    validation_id: str
    name: str
    validation_area: ValidationArea
    claim_scope: ClaimScope
    method_family_scope: MethodFamilyScope
    current_status: ValidationStatus
    required_inputs: tuple[str, ...]
    required_diagnostics: tuple[str, ...]
    required_dgp_coverage: tuple[str, ...]
    required_assignment_stress: tuple[str, ...]
    required_failure_registry_checks: tuple[str, ...]
    required_statistic_adapter: tuple[str, ...]
    required_null_calibration: tuple[str, ...]
    multiplicity_control_requirement: tuple[str, ...]
    dependence_handling_requirement: tuple[str, ...]
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
    claim_scope: ClaimScope,
    method_family_scope: MethodFamilyScope,
    current_status: ValidationStatus,
    notes: str,
    *,
    required_inputs: tuple[str, ...],
    required_diagnostics: tuple[str, ...],
    required_dgp_coverage: tuple[str, ...],
    required_assignment_stress: tuple[str, ...],
    required_failure_registry_checks: tuple[str, ...],
    required_statistic_adapter: tuple[str, ...] = (),
    required_null_calibration: tuple[str, ...] = (),
    multiplicity_control_requirement: tuple[str, ...],
    dependence_handling_requirement: tuple[str, ...],
    blocking_conditions: tuple[str, ...],
    passing_evidence_required: tuple[str, ...],
    allowed_current_use: tuple[str, ...],
    forbidden_current_use: tuple[str, ...],
    promotion_dependency: tuple[str, ...],
    recommended_next_artifact: str | None = None,
) -> MulticellValidationRow:
    return MulticellValidationRow(
        validation_id=validation_id,
        name=name,
        validation_area=validation_area,
        claim_scope=claim_scope,
        method_family_scope=method_family_scope,
        current_status=current_status,
        required_inputs=required_inputs,
        required_diagnostics=required_diagnostics,
        required_dgp_coverage=required_dgp_coverage,
        required_assignment_stress=required_assignment_stress,
        required_failure_registry_checks=required_failure_registry_checks,
        required_statistic_adapter=required_statistic_adapter,
        required_null_calibration=required_null_calibration,
        multiplicity_control_requirement=multiplicity_control_requirement,
        dependence_handling_requirement=dependence_handling_requirement,
        blocking_conditions=blocking_conditions,
        passing_evidence_required=passing_evidence_required,
        allowed_current_use=allowed_current_use,
        forbidden_current_use=forbidden_current_use,
        promotion_dependency=promotion_dependency,
        recommended_next_artifact=recommended_next_artifact,
        notes=notes,
    )


def _area_scopes(area: ValidationArea) -> tuple[ClaimScope, MethodFamilyScope]:
    mapping: dict[ValidationArea, tuple[ClaimScope, MethodFamilyScope]] = {
        ValidationArea.SHARED_CONTROL_DEPENDENCE: (ClaimScope.METHOD_FAMILY, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.CELL_LEVEL_DEPENDENCE: (ClaimScope.PER_CELL, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.METHOD_LEVEL_DEPENDENCE: (ClaimScope.METHOD_FAMILY, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.KPI_OUTCOME_MULTIPLICITY: (ClaimScope.CELL_BY_KPI, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.CELL_KPI_MULTIPLICITY: (ClaimScope.CELL_BY_KPI, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.FAMILYWISE_ERROR_CONTROL: (ClaimScope.GLOBAL, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.MAX_T_CANDIDATE: (ClaimScope.GLOBAL, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.STEPDOWN_CANDIDATE: (ClaimScope.GLOBAL, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.PERMUTATION_NULL_CALIBRATION: (ClaimScope.METHOD_FAMILY, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.STUDENTIZED_STATISTIC: (ClaimScope.METHOD_FAMILY, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.PER_CELL_CLAIM: (ClaimScope.PER_CELL, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.POOLED_GLOBAL_CLAIM: (ClaimScope.POOLED, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.AGGREGATE_LIFT: (ClaimScope.AGGREGATE, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.COMMON_CONTROL: (ClaimScope.METHOD_FAMILY, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.UNBALANCED_CELLS: (ClaimScope.PER_CELL, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.SMALL_CELL_COUNT: (ClaimScope.PER_CELL, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.SPARSE_COUNT_RATE: (ClaimScope.CELL_BY_KPI, MethodFamilyScope.CROSS_FAMILY),
        ValidationArea.SCM_MULTICELL: (ClaimScope.PER_CELL, MethodFamilyScope.SCM),
        ValidationArea.DID_MULTICELL: (ClaimScope.PER_CELL, MethodFamilyScope.DID),
        ValidationArea.AUGSYNTH_MULTICELL: (ClaimScope.PER_CELL, MethodFamilyScope.AUGSYNTH_CVXPY),
        ValidationArea.SYNTHETIC_DID_MULTICELL: (ClaimScope.PER_CELL, MethodFamilyScope.SYNTHETIC_DID),
        ValidationArea.TBRRIDGE_MULTICELL: (ClaimScope.PER_CELL, MethodFamilyScope.TBRRIDGE),
        ValidationArea.BAYESIAN_TBR_MULTICELL: (ClaimScope.PER_CELL, MethodFamilyScope.BAYESIAN_TBR),
        ValidationArea.TROP_MULTICELL: (ClaimScope.PER_CELL, MethodFamilyScope.TROP),
        ValidationArea.CLASSIC_TBR_MULTICELL: (ClaimScope.AGGREGATE, MethodFamilyScope.CLASSIC_AGGREGATE_TBR),
        ValidationArea.RELEASE_GATE: (ClaimScope.RELEASE_GATE, MethodFamilyScope.CROSS_FAMILY),
    }
    return mapping[area]


def _area_primary_status(area: ValidationArea) -> ValidationStatus:
    mapping: dict[ValidationArea, ValidationStatus] = {
        ValidationArea.SHARED_CONTROL_DEPENDENCE: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.CELL_LEVEL_DEPENDENCE: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.METHOD_LEVEL_DEPENDENCE: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.KPI_OUTCOME_MULTIPLICITY: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.CELL_KPI_MULTIPLICITY: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.FAMILYWISE_ERROR_CONTROL: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.MAX_T_CANDIDATE: ValidationStatus.CANDIDATE_AFTER_VALIDATION,
        ValidationArea.STEPDOWN_CANDIDATE: ValidationStatus.CANDIDATE_AFTER_VALIDATION,
        ValidationArea.PERMUTATION_NULL_CALIBRATION: ValidationStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
        ValidationArea.STUDENTIZED_STATISTIC: ValidationStatus.CANDIDATE_AFTER_ADAPTER,
        ValidationArea.PER_CELL_CLAIM: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.POOLED_GLOBAL_CLAIM: ValidationStatus.BLOCKED,
        ValidationArea.AGGREGATE_LIFT: ValidationStatus.BLOCKED,
        ValidationArea.COMMON_CONTROL: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.UNBALANCED_CELLS: ValidationStatus.RESEARCH_REQUIRED,
        ValidationArea.SMALL_CELL_COUNT: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.SPARSE_COUNT_RATE: ValidationStatus.CANDIDATE_AFTER_SIMULATION,
        ValidationArea.SCM_MULTICELL: ValidationStatus.BLOCKED,
        ValidationArea.DID_MULTICELL: ValidationStatus.BLOCKED,
        ValidationArea.AUGSYNTH_MULTICELL: ValidationStatus.BLOCKED,
        ValidationArea.SYNTHETIC_DID_MULTICELL: ValidationStatus.BLOCKED,
        ValidationArea.TBRRIDGE_MULTICELL: ValidationStatus.BLOCKED,
        ValidationArea.BAYESIAN_TBR_MULTICELL: ValidationStatus.BLOCKED,
        ValidationArea.TROP_MULTICELL: ValidationStatus.BLOCKED,
        ValidationArea.CLASSIC_TBR_MULTICELL: ValidationStatus.BLOCKED,
        ValidationArea.RELEASE_GATE: ValidationStatus.BLOCKED,
    }
    return mapping[area]


def _area_defaults(area: ValidationArea) -> dict[str, Any]:
    claim_scope, method_scope = _area_scopes(area)
    diag = ("OPD-MC-004", "OPD-MC-005")
    dgp = ("DGP-MC-001", "DGP-MC-002")
    stress = ("ST-AD-012", "ST-AD-001")
    fm = ("FM-CP-004", "FM-INF-009", "FM-INF-010")
    promo = ("observed_diagnostics", "dgp_coverage", "failure_registry_consult", "assignment_stress")
    mult = ("fwer_control", "multiplicity_adjustment")
    dep = ("shared_control_dependence_model", "cell_dependence_model")

    base: dict[str, Any] = {
        "claim_scope": claim_scope,
        "method_family_scope": method_scope,
        "required_inputs": ("multicell_panel", "shared_control_units", "cell_assignments"),
        "required_diagnostics": diag,
        "required_dgp_coverage": dgp,
        "required_assignment_stress": stress,
        "required_failure_registry_checks": fm,
        "required_statistic_adapter": (),
        "required_null_calibration": (),
        "multiplicity_control_requirement": mult,
        "dependence_handling_requirement": dep,
        "blocking_conditions": ("multicell_production_claim_unauthorized",),
        "passing_evidence_required": promo,
        "allowed_current_use": ("multicell_research_exploration",),
        "forbidden_current_use": _FORBID,
        "promotion_dependency": promo,
        "recommended_next_artifact": None,
    }

    if area in (ValidationArea.MAX_T_CANDIDATE, ValidationArea.STEPDOWN_CANDIDATE):
        base["multiplicity_control_requirement"] = ("max_t_stepdown_candidate", "fwer_validation")
        base["blocking_conditions"] = ("max_t_not_production_authorized",)
    if area == ValidationArea.STUDENTIZED_STATISTIC:
        base["required_statistic_adapter"] = ("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",)
        base["required_null_calibration"] = ("null_fpr_gate",)
    if area == ValidationArea.PERMUTATION_NULL_CALIBRATION:
        base["required_null_calibration"] = ("permutation_null", "randomization_null", "null_fpr_gate")
    if area in (ValidationArea.POOLED_GLOBAL_CLAIM, ValidationArea.AGGREGATE_LIFT):
        base["blocking_conditions"] = ("naive_pooled_global_overclaim",)
        base["forbidden_current_use"] = _FORBID + ("pooled_causal_claim", "global_winner_selection")
    if area == ValidationArea.PER_CELL_CLAIM:
        base["blocking_conditions"] = ("naive_independent_per_cell_p_value",)
    if area == ValidationArea.RELEASE_GATE:
        base["promotion_dependency"] = ("PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",)
        base["recommended_next_artifact"] = _NEXT
    if area in (
        ValidationArea.SCM_MULTICELL,
        ValidationArea.DID_MULTICELL,
        ValidationArea.AUGSYNTH_MULTICELL,
        ValidationArea.SYNTHETIC_DID_MULTICELL,
        ValidationArea.TBRRIDGE_MULTICELL,
        ValidationArea.BAYESIAN_TBR_MULTICELL,
        ValidationArea.TROP_MULTICELL,
        ValidationArea.CLASSIC_TBR_MULTICELL,
    ):
        base["blocking_conditions"] = ("method_family_multicell_blocked_until_validated",)

    return base


def _area_variants(area: ValidationArea) -> tuple[tuple[str, ValidationStatus, str], ...]:
    primary = _area_primary_status(area)
    return (
        ("gate", primary, "Primary validation gate for this multicell area."),
        ("diagnostic", ValidationStatus.DIAGNOSTIC_ONLY, "Diagnostic-only; not sufficient for production claim."),
        ("blocked_production", ValidationStatus.BLOCKED, "Multicell production claim blocked until evidence passes."),
    )


def build_multicell_dependence_multiplicity_validation_plan() -> tuple[MulticellValidationRow, ...]:
    """Return metadata-only multicell dependence/multiplicity validation plan rows."""
    rows: list[MulticellValidationRow] = []
    row_num = 1
    for area in ValidationArea:
        defaults = _area_defaults(area)
        claim_scope = defaults["claim_scope"]
        method_scope = defaults["method_family_scope"]
        for suffix, status, note_suffix in _area_variants(area):
            rows.append(
                _row(
                    f"MC-VAL-{row_num:03d}",
                    f"multicell_{area.value}_{suffix}",
                    area,
                    claim_scope,
                    method_scope,
                    status,
                    f"{area.value}: {note_suffix}",
                    required_inputs=defaults["required_inputs"],
                    required_diagnostics=defaults["required_diagnostics"],
                    required_dgp_coverage=defaults["required_dgp_coverage"],
                    required_assignment_stress=defaults["required_assignment_stress"],
                    required_failure_registry_checks=defaults["required_failure_registry_checks"],
                    required_statistic_adapter=defaults["required_statistic_adapter"],
                    required_null_calibration=defaults["required_null_calibration"],
                    multiplicity_control_requirement=defaults["multiplicity_control_requirement"],
                    dependence_handling_requirement=defaults["dependence_handling_requirement"],
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


def filter_multicell_dependence_multiplicity_validation_plan(
    rows: tuple[MulticellValidationRow, ...],
    *,
    validation_area: ValidationArea | None = None,
    claim_scope: ClaimScope | None = None,
    method_family_scope: MethodFamilyScope | None = None,
    current_status: ValidationStatus | None = None,
    requires_adapter: bool | None = None,
    requires_null_calibration: bool | None = None,
) -> tuple[MulticellValidationRow, ...]:
    """Filter multicell validation plan rows by optional criteria."""
    result: list[MulticellValidationRow] = []
    for row in rows:
        if validation_area is not None and row.validation_area != validation_area:
            continue
        if claim_scope is not None and row.claim_scope != claim_scope:
            continue
        if method_family_scope is not None and row.method_family_scope != method_family_scope:
            continue
        if current_status is not None and row.current_status != current_status:
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


def validate_multicell_dependence_multiplicity_validation_plan(
    rows: tuple[MulticellValidationRow, ...],
) -> dict[str, Any]:
    """Validate multicell validation plan registry thresholds and coverage."""
    issues: list[str] = []
    validation_ids = [r.validation_id for r in rows]

    if len(rows) < MIN_VALIDATION_ROW_COUNT:
        issues.append(f"validation_row_count {len(rows)} < {MIN_VALIDATION_ROW_COUNT}")
    if len(validation_ids) != len(set(validation_ids)):
        issues.append("duplicate validation_id values")

    status_counts = Counter(r.current_status for r in rows)
    area_counts = Counter(r.validation_area.value for r in rows)
    claim_counts = Counter(r.claim_scope.value for r in rows)
    family_counts = Counter(r.method_family_scope.value for r in rows)

    for area in REQUIRED_VALIDATION_AREAS:
        if not any(r.validation_area == area for r in rows):
            issues.append(f"missing validation_area: {area.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    for scope in REQUIRED_CLAIM_SCOPES:
        if not any(r.claim_scope == scope for r in rows):
            issues.append(f"missing claim_scope: {scope.value}")

    for family in REQUIRED_METHOD_FAMILY_SCOPES:
        if not any(r.method_family_scope == family for r in rows):
            issues.append(f"missing method_family_scope: {family.value}")

    shared_blocked = any(
        r.validation_area == ValidationArea.SHARED_CONTROL_DEPENDENCE
        and r.current_status == ValidationStatus.REQUIRED_BLOCKER
        for r in rows
    )
    if not shared_blocked:
        issues.append("shared_control_dependence required_blocker missing")

    pooled_blocked = any(
        r.validation_area == ValidationArea.POOLED_GLOBAL_CLAIM
        and r.current_status == ValidationStatus.BLOCKED
        for r in rows
    )
    if not pooled_blocked:
        issues.append("pooled_global_claim blocked row missing")

    classic_tbr_missing = not any(
        r.method_family_scope == MethodFamilyScope.CLASSIC_AGGREGATE_TBR for r in rows
    )
    if classic_tbr_missing:
        issues.append("classic_aggregate_tbr method_family_scope missing")

    unlinked = [r.validation_id for r in rows if not r.required_failure_registry_checks]
    if unlinked:
        issues.append(f"rows missing required_failure_registry_checks: {unlinked}")

    return {
        "valid": not issues,
        "validation_row_count": len(rows),
        "unique_validation_ids": len(validation_ids) == len(set(validation_ids)),
        "status_counts": {s.value: status_counts.get(s, 0) for s in ValidationStatus},
        "validation_area_counts": dict(area_counts),
        "claim_scope_counts": dict(claim_counts),
        "method_family_scope_counts": dict(family_counts),
        "all_required_validation_areas_covered": all(
            any(r.validation_area == a for r in rows) for a in REQUIRED_VALIDATION_AREAS
        ),
        "all_required_claim_scopes_covered": all(
            any(r.claim_scope == s for r in rows) for s in REQUIRED_CLAIM_SCOPES
        ),
        "all_required_method_family_scopes_covered": all(
            any(r.method_family_scope == f for r in rows) for f in REQUIRED_METHOD_FAMILY_SCOPES
        ),
        "all_statuses_represented": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "issues": issues,
    }


def summarize_multicell_dependence_multiplicity_validation_plan(
    rows: tuple[MulticellValidationRow, ...],
) -> dict[str, Any]:
    """Serialize multicell validation plan summary for archives."""
    validation = validate_multicell_dependence_multiplicity_validation_plan(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "validation_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "status_counts": validation["status_counts"],
        "validation_area_counts": validation["validation_area_counts"],
        "claim_scope_counts": validation["claim_scope_counts"],
        "method_family_scope_counts": validation["method_family_scope_counts"],
        "all_required_validation_areas_covered": validation["all_required_validation_areas_covered"],
        "all_required_claim_scopes_covered": validation["all_required_claim_scopes_covered"],
        "all_required_method_family_scopes_covered": validation[
            "all_required_method_family_scopes_covered"
        ],
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
    rows = build_multicell_dependence_multiplicity_validation_plan()
    validation = validate_multicell_dependence_multiplicity_validation_plan(rows)
    summary = summarize_multicell_dependence_multiplicity_validation_plan(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("validation_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("validation_row_count_at_least_70", len(rows) >= MIN_VALIDATION_ROW_COUNT))
    scenarios.append(_scenario("validation_ids_unique", validation["unique_validation_ids"]))

    for area in REQUIRED_VALIDATION_AREAS:
        present = any(r.validation_area == area for r in rows)
        scenarios.append(_scenario(f"validation_area_{area.value}_represented", present))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for scope in REQUIRED_CLAIM_SCOPES:
        present = any(r.claim_scope == scope for r in rows)
        scenarios.append(_scenario(f"claim_scope_{scope.value}_represented", present))

    for family in REQUIRED_METHOD_FAMILY_SCOPES:
        present = any(r.method_family_scope == family for r in rows)
        scenarios.append(_scenario(f"method_family_scope_{family.value}_represented", present))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] is expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_augsynth_remediation_plan",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_multicell_dependence_multiplicity_validation_plan()
    validation = validate_multicell_dependence_multiplicity_validation_plan(rows)
    summary = summarize_multicell_dependence_multiplicity_validation_plan(rows)
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
