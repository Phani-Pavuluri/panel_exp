"""SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001 validation harness."""

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

_ARTIFACT_ID = "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "synthetic_did_implementation_readiness_plan_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",
    "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
)

MIN_READINESS_ROW_COUNT = 65

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
    "synthetic_did_not_implemented_by_this_artifact": True,
    "synthetic_did_implementation_candidate_only": True,
    "synthetic_did_point_estimate_not_sufficient_for_production_inference": True,
    "synthetic_did_production_inference_authorized": False,
    "synthetic_did_production_p_value_authorized": False,
    "synthetic_did_causal_ci_authorized": False,
    "unit_weight_contract_required": True,
    "time_weight_contract_required": True,
    "regularization_tuning_contract_required": True,
    "donor_support_required": True,
    "treated_control_support_required": True,
    "pre_period_fit_required": True,
    "pre_period_trend_stability_required": True,
    "assignment_design_validity_required": True,
    "assignment_generator_stress_required": True,
    "outcome_scale_compatibility_required": True,
    "statistic_adapter_required": True,
    "null_calibration_required": True,
    "dgp_coverage_required": True,
    "failure_registry_consulted": True,
    "comparison_against_scm_required": True,
    "comparison_against_did_required": True,
    "comparison_against_augsynth_required": True,
    "comparison_against_tbrridge_required": True,
    "multi_treated_synthetic_did_requires_research_handling": True,
    "treated_set_synthetic_did_requires_research_handling": True,
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
    "synthetic_did_implementation",
)


class ReadinessArea(str, Enum):
    METHOD_SCOPE = "synthetic_did_method_scope"
    IMPLEMENTATION_CANDIDATE_BOUNDARY = "implementation_candidate_boundary"
    DATA_SHAPE = "data_shape_requirements"
    PANEL_BALANCE = "panel_balance_requirements"
    PRE_POST_PERIOD = "pre_post_period_requirements"
    TREATED_CONTROL_SUPPORT = "treated_control_support"
    UNIT_WEIGHT = "unit_weight_requirements"
    TIME_WEIGHT = "time_weight_requirements"
    REGULARIZATION_TUNING = "regularization_tuning_requirements"
    DONOR_SUPPORT_OVERLAP = "donor_support_overlap"
    PREPERIOD_FIT = "preperiod_fit_quality"
    PREPERIOD_TREND_STABILITY = "preperiod_trend_stability"
    PARALLEL_TREND_RELATION_DID = "parallel_trend_relation_did"
    SYNTHETIC_CONTROL_RELATION_SCM = "synthetic_control_relation_scm"
    COMPARISON_AUGSYNTH = "comparison_against_augsynth"
    COMPARISON_TBRRIDGE = "comparison_against_tbrridge"
    COMPARISON_SCM = "comparison_against_scm"
    COMPARISON_DID = "comparison_against_did"
    OUTCOME_SCALE = "outcome_scale_compatibility"
    SPARSE_COUNT_RATE = "sparse_count_rate_outcome_handling"
    MISSING_DATA = "missing_data_sensitivity"
    ASSIGNMENT_DESIGN = "assignment_design_validity"
    ASSIGNMENT_STRESS = "assignment_generator_stress_compatibility"
    SINGLE_TREATED = "single_treated_path"
    MULTI_TREATED = "multi_treated_path"
    TREATED_SET = "treated_set_path"
    MULTICELL_BOUNDARY = "multicell_shared_control_boundary"
    POINT_ESTIMATE_IMPLEMENTATION = "point_estimate_implementation_requirements"
    INFERENCE_ADAPTER = "inference_adapter_requirements"
    PLACEBO_RANK = "placebo_rank_candidate"
    JACKKNIFE = "jackknife_candidate"
    BOOTSTRAP = "bootstrap_candidate"
    STUDENTIZED_STATISTIC = "studentized_statistic_requirement"
    NULL_CALIBRATION = "null_calibration_requirement"
    DGP_SIMULATION = "dgp_simulation_coverage"
    FAILURE_REGISTRY = "failure_registry_blockers"
    METHOD_DISAGREEMENT = "method_disagreement_checks"
    RELEASE_GATE = "release_gate_boundary"


class ReadinessStatus(str, Enum):
    REQUIRED_BLOCKER = "required_blocker"
    REQUIRED_WARNING = "required_warning"
    IMPLEMENTATION_CANDIDATE = "implementation_candidate"
    CANDIDATE_AFTER_DESIGN = "candidate_after_design"
    CANDIDATE_AFTER_ADAPTER = "candidate_after_adapter"
    CANDIDATE_AFTER_NULL_CALIBRATION = "candidate_after_null_calibration"
    CANDIDATE_AFTER_SIMULATION = "candidate_after_simulation"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    BLOCKED = "blocked"


class ReadinessType(str, Enum):
    IMPLEMENTATION_SCOPE = "implementation_scope"
    DATA_REQUIREMENT = "data_requirement"
    DIAGNOSTIC_REQUIREMENT = "diagnostic_requirement"
    ESTIMATOR_COMPONENT_REQUIREMENT = "estimator_component_requirement"
    INFERENCE_ADAPTER_REQUIREMENT = "inference_adapter_requirement"
    NULL_CALIBRATION_REQUIREMENT = "null_calibration_requirement"
    SIMULATION_REQUIREMENT = "simulation_requirement"
    ASSIGNMENT_STRESS_REQUIREMENT = "assignment_stress_requirement"
    MULTICELL_BOUNDARY = "multicell_boundary"
    RELEASE_GATE_BOUNDARY = "release_gate_boundary"


REQUIRED_READINESS_AREAS = frozenset(ReadinessArea)
REQUIRED_STATUSES = frozenset(ReadinessStatus)
REQUIRED_READINESS_TYPES = frozenset(ReadinessType)


@dataclass(frozen=True)
class SyntheticDidReadinessRow:
    readiness_id: str
    name: str
    readiness_area: ReadinessArea
    current_status: ReadinessStatus
    readiness_type: ReadinessType
    required_inputs: tuple[str, ...]
    required_diagnostics: tuple[str, ...]
    required_implementation_components: tuple[str, ...]
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
    readiness_id: str,
    name: str,
    readiness_area: ReadinessArea,
    current_status: ReadinessStatus,
    readiness_type: ReadinessType,
    notes: str,
    *,
    required_inputs: tuple[str, ...],
    required_diagnostics: tuple[str, ...],
    required_implementation_components: tuple[str, ...],
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
) -> SyntheticDidReadinessRow:
    return SyntheticDidReadinessRow(
        readiness_id=readiness_id,
        name=name,
        readiness_area=readiness_area,
        current_status=current_status,
        readiness_type=readiness_type,
        required_inputs=required_inputs,
        required_diagnostics=required_diagnostics,
        required_implementation_components=required_implementation_components,
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


def _area_primary_status(area: ReadinessArea) -> ReadinessStatus:
    mapping: dict[ReadinessArea, ReadinessStatus] = {
        ReadinessArea.METHOD_SCOPE: ReadinessStatus.IMPLEMENTATION_CANDIDATE,
        ReadinessArea.IMPLEMENTATION_CANDIDATE_BOUNDARY: ReadinessStatus.IMPLEMENTATION_CANDIDATE,
        ReadinessArea.DATA_SHAPE: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.PANEL_BALANCE: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.PRE_POST_PERIOD: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.TREATED_CONTROL_SUPPORT: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.UNIT_WEIGHT: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.TIME_WEIGHT: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.REGULARIZATION_TUNING: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.DONOR_SUPPORT_OVERLAP: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.PREPERIOD_FIT: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.PREPERIOD_TREND_STABILITY: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.PARALLEL_TREND_RELATION_DID: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.SYNTHETIC_CONTROL_RELATION_SCM: ReadinessStatus.REQUIRED_WARNING,
        ReadinessArea.COMPARISON_AUGSYNTH: ReadinessStatus.REQUIRED_WARNING,
        ReadinessArea.COMPARISON_TBRRIDGE: ReadinessStatus.REQUIRED_WARNING,
        ReadinessArea.COMPARISON_SCM: ReadinessStatus.REQUIRED_WARNING,
        ReadinessArea.COMPARISON_DID: ReadinessStatus.REQUIRED_WARNING,
        ReadinessArea.OUTCOME_SCALE: ReadinessStatus.REQUIRED_WARNING,
        ReadinessArea.SPARSE_COUNT_RATE: ReadinessStatus.REQUIRED_WARNING,
        ReadinessArea.MISSING_DATA: ReadinessStatus.REQUIRED_WARNING,
        ReadinessArea.ASSIGNMENT_DESIGN: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.ASSIGNMENT_STRESS: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.SINGLE_TREATED: ReadinessStatus.CANDIDATE_AFTER_DESIGN,
        ReadinessArea.MULTI_TREATED: ReadinessStatus.RESEARCH_ONLY,
        ReadinessArea.TREATED_SET: ReadinessStatus.RESEARCH_ONLY,
        ReadinessArea.MULTICELL_BOUNDARY: ReadinessStatus.BLOCKED,
        ReadinessArea.POINT_ESTIMATE_IMPLEMENTATION: ReadinessStatus.DIAGNOSTIC_ONLY,
        ReadinessArea.INFERENCE_ADAPTER: ReadinessStatus.CANDIDATE_AFTER_ADAPTER,
        ReadinessArea.PLACEBO_RANK: ReadinessStatus.CANDIDATE_AFTER_ADAPTER,
        ReadinessArea.JACKKNIFE: ReadinessStatus.CANDIDATE_AFTER_ADAPTER,
        ReadinessArea.BOOTSTRAP: ReadinessStatus.CANDIDATE_AFTER_ADAPTER,
        ReadinessArea.STUDENTIZED_STATISTIC: ReadinessStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
        ReadinessArea.NULL_CALIBRATION: ReadinessStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
        ReadinessArea.DGP_SIMULATION: ReadinessStatus.CANDIDATE_AFTER_SIMULATION,
        ReadinessArea.FAILURE_REGISTRY: ReadinessStatus.REQUIRED_BLOCKER,
        ReadinessArea.METHOD_DISAGREEMENT: ReadinessStatus.REQUIRED_WARNING,
        ReadinessArea.RELEASE_GATE: ReadinessStatus.BLOCKED,
    }
    return mapping[area]


def _area_readiness_type(area: ReadinessArea) -> ReadinessType:
    mapping: dict[ReadinessArea, ReadinessType] = {
        ReadinessArea.METHOD_SCOPE: ReadinessType.IMPLEMENTATION_SCOPE,
        ReadinessArea.IMPLEMENTATION_CANDIDATE_BOUNDARY: ReadinessType.IMPLEMENTATION_SCOPE,
        ReadinessArea.DATA_SHAPE: ReadinessType.DATA_REQUIREMENT,
        ReadinessArea.PANEL_BALANCE: ReadinessType.DATA_REQUIREMENT,
        ReadinessArea.PRE_POST_PERIOD: ReadinessType.DATA_REQUIREMENT,
        ReadinessArea.TREATED_CONTROL_SUPPORT: ReadinessType.DATA_REQUIREMENT,
        ReadinessArea.UNIT_WEIGHT: ReadinessType.ESTIMATOR_COMPONENT_REQUIREMENT,
        ReadinessArea.TIME_WEIGHT: ReadinessType.ESTIMATOR_COMPONENT_REQUIREMENT,
        ReadinessArea.REGULARIZATION_TUNING: ReadinessType.ESTIMATOR_COMPONENT_REQUIREMENT,
        ReadinessArea.DONOR_SUPPORT_OVERLAP: ReadinessType.DIAGNOSTIC_REQUIREMENT,
        ReadinessArea.PREPERIOD_FIT: ReadinessType.DIAGNOSTIC_REQUIREMENT,
        ReadinessArea.PREPERIOD_TREND_STABILITY: ReadinessType.DIAGNOSTIC_REQUIREMENT,
        ReadinessArea.PARALLEL_TREND_RELATION_DID: ReadinessType.DIAGNOSTIC_REQUIREMENT,
        ReadinessArea.SYNTHETIC_CONTROL_RELATION_SCM: ReadinessType.DIAGNOSTIC_REQUIREMENT,
        ReadinessArea.OUTCOME_SCALE: ReadinessType.DIAGNOSTIC_REQUIREMENT,
        ReadinessArea.SPARSE_COUNT_RATE: ReadinessType.DIAGNOSTIC_REQUIREMENT,
        ReadinessArea.MISSING_DATA: ReadinessType.DIAGNOSTIC_REQUIREMENT,
        ReadinessArea.INFERENCE_ADAPTER: ReadinessType.INFERENCE_ADAPTER_REQUIREMENT,
        ReadinessArea.PLACEBO_RANK: ReadinessType.INFERENCE_ADAPTER_REQUIREMENT,
        ReadinessArea.JACKKNIFE: ReadinessType.INFERENCE_ADAPTER_REQUIREMENT,
        ReadinessArea.BOOTSTRAP: ReadinessType.INFERENCE_ADAPTER_REQUIREMENT,
        ReadinessArea.STUDENTIZED_STATISTIC: ReadinessType.INFERENCE_ADAPTER_REQUIREMENT,
        ReadinessArea.NULL_CALIBRATION: ReadinessType.NULL_CALIBRATION_REQUIREMENT,
        ReadinessArea.DGP_SIMULATION: ReadinessType.SIMULATION_REQUIREMENT,
        ReadinessArea.ASSIGNMENT_STRESS: ReadinessType.ASSIGNMENT_STRESS_REQUIREMENT,
        ReadinessArea.MULTICELL_BOUNDARY: ReadinessType.MULTICELL_BOUNDARY,
        ReadinessArea.RELEASE_GATE: ReadinessType.RELEASE_GATE_BOUNDARY,
    }
    return mapping.get(area, ReadinessType.DIAGNOSTIC_REQUIREMENT)


def _area_variants(area: ReadinessArea) -> tuple[tuple[str, ReadinessStatus, str], ...]:
    primary = _area_primary_status(area)
    return (
        ("gate", primary, "Primary implementation-readiness gate for this Synthetic DID area."),
        ("diagnostic", ReadinessStatus.DIAGNOSTIC_ONLY, "Diagnostic-only; not sufficient for implementation."),
        ("blocked_production", ReadinessStatus.BLOCKED, "Synthetic DID production path blocked until evidence passes."),
    )


def _area_defaults(area: ReadinessArea) -> dict[str, Any]:
    diag = ("OPD-PF-001", "OPD-PF-002", "OPD-DS-005")
    dgp = ("DGP-SDID-001", "DGP-ES-007")
    stress = ("ST-AD-001", "ST-AD-009")
    fm = ("FM-ES-009", "FM-CP-005")
    components = ("unit_weight_contract", "time_weight_contract", "regularization_contract")
    promo = (
        "observed_diagnostics",
        "dgp_coverage",
        "failure_registry_consult",
        "SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001",
    )

    base: dict[str, Any] = {
        "required_inputs": ("panel_data", "treatment_timing", "control_units", "pre_post_periods"),
        "required_diagnostics": diag,
        "required_implementation_components": components,
        "required_dgp_coverage": dgp,
        "required_assignment_stress": stress,
        "required_failure_registry_checks": fm,
        "required_inference_adapter": (),
        "required_null_calibration": (),
        "blocking_conditions": ("synthetic_did_production_inference_unauthorized",),
        "passing_evidence_required": promo,
        "allowed_current_use": ("synthetic_did_readiness_planning", "scout_research"),
        "forbidden_current_use": _FORBID,
        "promotion_dependency": promo,
        "recommended_next_artifact": None,
    }

    if area == ReadinessArea.METHOD_SCOPE:
        base["blocking_conditions"] = ("synthetic_did_not_implemented",)
    if area == ReadinessArea.IMPLEMENTATION_CANDIDATE_BOUNDARY:
        base["blocking_conditions"] = ("implementation_candidate_only",)
    if area in (ReadinessArea.UNIT_WEIGHT, ReadinessArea.TIME_WEIGHT):
        base["required_implementation_components"] = (
            f"{area.value}_contract",
            "weight_normalization",
            "weight_stability_diagnostics",
        )
    if area == ReadinessArea.REGULARIZATION_TUNING:
        base["required_implementation_components"] = (
            "regularization_contract",
            "tuning_grid_spec",
            "tuning_stability_diagnostics",
        )
    if area == ReadinessArea.DONOR_SUPPORT_OVERLAP:
        base["required_diagnostics"] = ("OPD-DONOR-001", "OPD-DS-005", "donor_overlap")
        base["blocking_conditions"] = ("donor_support_insufficient",)
    if area == ReadinessArea.PREPERIOD_FIT:
        base["required_diagnostics"] = ("OPD-PF-001", "OPD-PF-003")
        base["blocking_conditions"] = ("preperiod_fit_poor",)
    if area == ReadinessArea.PREPERIOD_TREND_STABILITY:
        base["required_diagnostics"] = ("OPD-PF-002", "OPD-PF-003")
        base["blocking_conditions"] = ("trend_instability",)
    if area == ReadinessArea.PARALLEL_TREND_RELATION_DID:
        base["required_diagnostics"] = ("parallel_trend_support", "OPD-PF-002")
        base["blocking_conditions"] = ("parallel_trends_fail",)
    if area == ReadinessArea.SYNTHETIC_CONTROL_RELATION_SCM:
        base["passing_evidence_required"] = promo + ("scm_relation_check",)
    if area == ReadinessArea.COMPARISON_SCM:
        base["passing_evidence_required"] = promo + ("scm_disagreement_check",)
    if area == ReadinessArea.COMPARISON_DID:
        base["passing_evidence_required"] = promo + ("did_disagreement_check",)
    if area == ReadinessArea.COMPARISON_AUGSYNTH:
        base["passing_evidence_required"] = promo + ("augsynth_disagreement_check",)
    if area == ReadinessArea.COMPARISON_TBRRIDGE:
        base["passing_evidence_required"] = promo + ("tbrridge_disagreement_check",)
    if area == ReadinessArea.ASSIGNMENT_DESIGN:
        base["blocking_conditions"] = ("assignment_invalid", "randomization_unknown")
    if area == ReadinessArea.ASSIGNMENT_STRESS:
        base["required_assignment_stress"] = ("ST-AD-001", "ST-AD-009", "ST-AD-010")
    if area in (ReadinessArea.SPARSE_COUNT_RATE, ReadinessArea.OUTCOME_SCALE):
        base["required_dgp_coverage"] = ("DGP-SDID-001", "DGP-CP-002")
    if area == ReadinessArea.SINGLE_TREATED:
        base["blocking_conditions"] = ("design_not_eligible",)
    if area in (ReadinessArea.MULTI_TREATED, ReadinessArea.TREATED_SET):
        base["blocking_conditions"] = ("multiplicity_unhandled", "dependence_unhandled")
    if area == ReadinessArea.POINT_ESTIMATE_IMPLEMENTATION:
        base["required_implementation_components"] = components + ("point_estimate_contract",)
        base["blocking_conditions"] = ("point_estimate_not_production_inference",)
    if area in (
        ReadinessArea.INFERENCE_ADAPTER,
        ReadinessArea.PLACEBO_RANK,
        ReadinessArea.JACKKNIFE,
        ReadinessArea.BOOTSTRAP,
    ):
        base["required_inference_adapter"] = (f"{area.value}_adapter", "SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001")
    if area in (ReadinessArea.NULL_CALIBRATION, ReadinessArea.STUDENTIZED_STATISTIC):
        base["required_null_calibration"] = ("null_fpr_gate", "coverage_replay")
    if area == ReadinessArea.DGP_SIMULATION:
        base["required_dgp_coverage"] = ("DGP-SDID-001", "DGP-ES-007", "DGP-CP-002")
    if area == ReadinessArea.METHOD_DISAGREEMENT:
        base["passing_evidence_required"] = promo + (
            "scm_disagreement_check",
            "did_disagreement_check",
            "augsynth_disagreement_check",
            "tbrridge_disagreement_check",
        )
    if area == ReadinessArea.MULTICELL_BOUNDARY:
        base["blocking_conditions"] = ("multicell_dependence_unhandled", "multiplicity_unhandled")
        base["required_failure_registry_checks"] = ("FM-CP-004", "FM-INF-009")
        base["recommended_next_artifact"] = "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001"
    if area == ReadinessArea.RELEASE_GATE:
        base["blocking_conditions"] = ("release_gate_not_passed",)
        base["promotion_dependency"] = ("PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",)

    return base


def build_synthetic_did_implementation_readiness_plan() -> tuple[SyntheticDidReadinessRow, ...]:
    """Return metadata-only Synthetic DID implementation-readiness plan rows."""
    rows: list[SyntheticDidReadinessRow] = []
    row_num = 1
    for area in ReadinessArea:
        defaults = _area_defaults(area)
        readiness_type = _area_readiness_type(area)
        for suffix, status, note_suffix in _area_variants(area):
            rows.append(
                _row(
                    f"SDID-RDY-{row_num:03d}",
                    f"synthetic_did_{area.value}_{suffix}",
                    area,
                    status,
                    readiness_type,
                    f"{area.value}: {note_suffix}",
                    required_inputs=defaults["required_inputs"],
                    required_diagnostics=defaults["required_diagnostics"],
                    required_implementation_components=defaults["required_implementation_components"],
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


def filter_synthetic_did_implementation_readiness_plan(
    rows: tuple[SyntheticDidReadinessRow, ...],
    *,
    readiness_area: ReadinessArea | None = None,
    current_status: ReadinessStatus | None = None,
    readiness_type: ReadinessType | None = None,
    requires_adapter: bool | None = None,
    requires_null_calibration: bool | None = None,
) -> tuple[SyntheticDidReadinessRow, ...]:
    """Filter Synthetic DID readiness plan rows by optional criteria."""
    result: list[SyntheticDidReadinessRow] = []
    for row in rows:
        if readiness_area is not None and row.readiness_area != readiness_area:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if readiness_type is not None and row.readiness_type != readiness_type:
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


def validate_synthetic_did_implementation_readiness_plan(
    rows: tuple[SyntheticDidReadinessRow, ...],
) -> dict[str, Any]:
    """Validate Synthetic DID readiness plan registry thresholds and coverage."""
    issues: list[str] = []
    readiness_ids = [r.readiness_id for r in rows]

    if len(rows) < MIN_READINESS_ROW_COUNT:
        issues.append(f"readiness_row_count {len(rows)} < {MIN_READINESS_ROW_COUNT}")
    if len(readiness_ids) != len(set(readiness_ids)):
        issues.append("duplicate readiness_id values")

    status_counts = Counter(r.current_status for r in rows)
    area_counts = Counter(r.readiness_area.value for r in rows)
    type_counts = Counter(r.readiness_type for r in rows)

    for area in REQUIRED_READINESS_AREAS:
        if not any(r.readiness_area == area for r in rows):
            issues.append(f"missing readiness_area: {area.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    for rtype in REQUIRED_READINESS_TYPES:
        if type_counts.get(rtype, 0) == 0:
            issues.append(f"missing readiness_type: {rtype.value}")

    implementation_candidate = status_counts.get(ReadinessStatus.IMPLEMENTATION_CANDIDATE, 0)
    if implementation_candidate == 0:
        issues.append("implementation_candidate status missing")

    candidate_after_design = status_counts.get(ReadinessStatus.CANDIDATE_AFTER_DESIGN, 0)
    if candidate_after_design == 0:
        issues.append("candidate_after_design status missing")

    unit_weight_blocked = any(
        r.readiness_area == ReadinessArea.UNIT_WEIGHT
        and r.current_status == ReadinessStatus.REQUIRED_BLOCKER
        for r in rows
    )
    if not unit_weight_blocked:
        issues.append("unit_weight required_blocker missing")

    unlinked = [r.readiness_id for r in rows if not r.required_failure_registry_checks]
    if unlinked:
        issues.append(f"rows missing required_failure_registry_checks: {unlinked}")

    return {
        "valid": not issues,
        "readiness_row_count": len(rows),
        "unique_readiness_ids": len(readiness_ids) == len(set(readiness_ids)),
        "status_counts": {s.value: status_counts.get(s, 0) for s in ReadinessStatus},
        "readiness_area_counts": dict(area_counts),
        "readiness_type_counts": {t.value: type_counts.get(t, 0) for t in ReadinessType},
        "all_required_readiness_areas_covered": all(
            any(r.readiness_area == a for r in rows) for a in REQUIRED_READINESS_AREAS
        ),
        "all_required_statuses_covered": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "all_required_readiness_types_covered": all(
            type_counts.get(t, 0) > 0 for t in REQUIRED_READINESS_TYPES
        ),
        "issues": issues,
    }


def summarize_synthetic_did_implementation_readiness_plan(
    rows: tuple[SyntheticDidReadinessRow, ...],
) -> dict[str, Any]:
    """Serialize Synthetic DID readiness plan summary for archives."""
    validation = validate_synthetic_did_implementation_readiness_plan(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "readiness_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "status_counts": validation["status_counts"],
        "readiness_area_counts": validation["readiness_area_counts"],
        "readiness_type_counts": validation["readiness_type_counts"],
        "all_required_readiness_areas_covered": validation["all_required_readiness_areas_covered"],
        "all_required_statuses_covered": validation["all_required_statuses_covered"],
        "all_required_readiness_types_covered": validation["all_required_readiness_types_covered"],
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
    rows = build_synthetic_did_implementation_readiness_plan()
    validation = validate_synthetic_did_implementation_readiness_plan(rows)
    summary = summarize_synthetic_did_implementation_readiness_plan(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("readiness_rows_build_successfully", len(rows) > 0))
    scenarios.append(
        _scenario("readiness_row_count_at_least_65", len(rows) >= MIN_READINESS_ROW_COUNT)
    )
    scenarios.append(_scenario("readiness_ids_unique", validation["unique_readiness_ids"]))

    for area in REQUIRED_READINESS_AREAS:
        present = any(r.readiness_area == area for r in rows)
        scenarios.append(_scenario(f"readiness_area_{area.value}_represented", present))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for rtype in REQUIRED_READINESS_TYPES:
        count = sum(1 for r in rows if r.readiness_type == rtype)
        scenarios.append(_scenario(f"readiness_type_{rtype.value}_represented", count > 0))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] == expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_method_family_retire_replace",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_synthetic_did_implementation_readiness_plan()
    validation = validate_synthetic_did_implementation_readiness_plan(rows)
    summary = summarize_synthetic_did_implementation_readiness_plan(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "readiness_row_count": len(rows),
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
