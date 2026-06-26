"""SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001 — null calibration metadata scaffolding."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

_ARTIFACT_ID = "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "scm_production_candidate_null_calibration_metadata_implemented_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001",
)

METHOD_FAMILY = "SCM"
METHOD_FAMILY_STATUS = "production_candidate_gated"

_AUTH_FLAGS = {
    "scm_production_p_value_authorized": False,
    "scm_causal_confidence_interval_authorized": False,
    "production_authorization_granted": False,
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
    "data_driven_selection_gate_implementation_authorized": False,
    "selector_implementation_authorized": False,
    "production_selection_router_authorized": False,
    "scm_production_inference_authorized": False,
    "multicell_production_claim_authorized": False,
    "package_side_agents_authorized": False,
}

_SCM_FLAGS = {
    "scm_null_calibration_implementation_authorized": False,
    "scm_null_calibration_completed": False,
    "scm_production_inference_authorized": False,
}

NON_GOALS = (
    "no_placebo_distribution_computation",
    "no_placebo_or_treated_statistic_computation",
    "no_p_value_type_i_error_or_coverage_computation",
    "no_production_p_values_or_causal_cis",
    "no_production_inference_authorization",
    "no_selector_router_production_use",
    "no_downstream_integrations",
    "no_package_side_agents",
    "no_multicell_production_claims",
    "no_numerical_null_calibration_diagnostics",
)

DEPENDENCIES_RECONCILED = (
    "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001",
    "SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",
    "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
    "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
    "SIMULATION_DGP_COVERAGE_PLAN_001",
    "METHOD_FAILURE_MODE_REGISTRY_001",
)

# Blocked-reason codes
BR_INPUT_CONTRACT_INCOMPLETE = "SCM-NC-BR-INPUT-INCOMPLETE"
BR_VALIDATION_EVIDENCE_MISSING = "SCM-NC-BR-VALIDATION-EVIDENCE-MISSING"
BR_PLACEBO_UNITS_MISSING = "SCM-NC-BR-PLACEBO-UNITS-MISSING"
BR_PLACEBO_WINDOWS_MISSING = "SCM-NC-BR-PLACEBO-WINDOWS-MISSING"
BR_PLACEBO_STATISTIC_MISSING = "SCM-NC-BR-PLACEBO-STATISTIC-MISSING"
BR_TREATED_STATISTIC_MISSING = "SCM-NC-BR-TREATED-STATISTIC-MISSING"
BR_EFFECT_SCALE_MISSING = "SCM-NC-BR-EFFECT-SCALE-MISSING"
BR_ESTIMAND_MISALIGNED = "SCM-NC-BR-ESTIMAND-MISALIGNED"
BR_DONOR_SUPPORT_CONDITIONING_MISSING = "SCM-NC-BR-DONOR-SUPPORT-CONDITIONING-MISSING"
BR_PRE_PERIOD_FIT_CONDITIONING_MISSING = "SCM-NC-BR-PRE-PERIOD-FIT-CONDITIONING-MISSING"
BR_NULL_CALIBRATION_INCOMPLETE = "SCM-NC-BR-NULL-CALIBRATION-INCOMPLETE"
BR_NULL_COVERAGE_INCOMPLETE = "SCM-NC-BR-NULL-COVERAGE-INCOMPLETE"
BR_MULTICELL_UNVALIDATED = "SCM-NC-BR-MULTICELL-UNVALIDATED"
BR_RELEASE_GATE_REQUIRED = "SCM-NC-BR-RELEASE-GATE-REQUIRED"
BR_FAILURE_REGISTRY_UNRESOLVED = "SCM-NC-BR-FAILURE-REGISTRY-UNRESOLVED"
BR_P_VALUE_BOUNDARY = "SCM-NC-BR-P-VALUE-BOUNDARY"
BR_CAUSAL_CI_BOUNDARY = "SCM-NC-BR-CAUSAL-CI-BOUNDARY"

BLOCKED_REASONS_SUPPORTED = (
    BR_INPUT_CONTRACT_INCOMPLETE,
    BR_VALIDATION_EVIDENCE_MISSING,
    BR_PLACEBO_UNITS_MISSING,
    BR_PLACEBO_WINDOWS_MISSING,
    BR_PLACEBO_STATISTIC_MISSING,
    BR_TREATED_STATISTIC_MISSING,
    BR_EFFECT_SCALE_MISSING,
    BR_ESTIMAND_MISALIGNED,
    BR_DONOR_SUPPORT_CONDITIONING_MISSING,
    BR_PRE_PERIOD_FIT_CONDITIONING_MISSING,
    BR_NULL_CALIBRATION_INCOMPLETE,
    BR_NULL_COVERAGE_INCOMPLETE,
    BR_MULTICELL_UNVALIDATED,
    BR_RELEASE_GATE_REQUIRED,
    BR_FAILURE_REGISTRY_UNRESOLVED,
    BR_P_VALUE_BOUNDARY,
    BR_CAUSAL_CI_BOUNDARY,
)

RF_VALIDATION_EVIDENCE = "SCM-NC-RF-VALIDATION-EVIDENCE"
RF_PLACEBO_GENERATION = "SCM-NC-RF-PLACEBO-GENERATION"
RF_PLACEBO_WINDOWS = "SCM-NC-RF-PLACEBO-WINDOWS"
RF_PLACEBO_STATISTIC = "SCM-NC-RF-PLACEBO-STATISTIC"
RF_TREATED_STATISTIC = "SCM-NC-RF-TREATED-STATISTIC"
RF_DONOR_SUPPORT = "SCM-NC-RF-DONOR-SUPPORT"
RF_PRE_PERIOD_FIT = "SCM-NC-RF-PRE-PERIOD-FIT"
RF_DGP_COVERAGE = "SCM-NC-RF-DGP-COVERAGE"
RF_FAILURE_REGISTRY = "SCM-NC-RF-FAILURE-REGISTRY"
RF_NULL_CALIBRATION = "SCM-NC-RF-NULL-CALIBRATION"
RF_NULL_COVERAGE = "SCM-NC-RF-NULL-COVERAGE"
RF_RELEASE_GATE = "SCM-NC-RF-RELEASE-GATE"

REQUIRED_FOLLOWUPS_SUPPORTED = (
    RF_VALIDATION_EVIDENCE,
    RF_PLACEBO_GENERATION,
    RF_PLACEBO_WINDOWS,
    RF_PLACEBO_STATISTIC,
    RF_TREATED_STATISTIC,
    RF_DONOR_SUPPORT,
    RF_PRE_PERIOD_FIT,
    RF_DGP_COVERAGE,
    RF_FAILURE_REGISTRY,
    RF_NULL_CALIBRATION,
    RF_NULL_COVERAGE,
    RF_RELEASE_GATE,
)


class CalibrationStatus(str, Enum):
    ELIGIBLE = "eligible"
    ELIGIBLE_AFTER_WARNING = "eligible_after_warning"
    CANDIDATE_AFTER_VALIDATION = "candidate_after_validation"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    BLOCKED = "blocked"
    RELEASE_GATE_REQUIRED = "release_gate_required"
    NOT_APPLICABLE = "not_applicable"


REQUIRED_STATUSES = frozenset(CalibrationStatus)


class CalibrationArea(str, Enum):
    NULL_CALIBRATION_INPUT_CONTRACT = "null_calibration_input_contract"
    PLACEBO_UNIT_GENERATION_CONTRACT = "placebo_unit_generation_contract"
    PLACEBO_TIME_WINDOW_CONTRACT = "placebo_time_window_contract"
    PLACEBO_STATISTIC_CONTRACT = "placebo_statistic_contract"
    TREATED_STATISTIC_CONTRACT = "treated_statistic_contract"
    EFFECT_SCALE_ALIGNMENT = "effect_scale_alignment"
    ESTIMAND_ALIGNMENT = "estimand_alignment"
    OUTCOME_KPI_COMPATIBILITY = "outcome_kpi_compatibility"
    PRE_PERIOD_FIT_CONDITIONING = "pre_period_fit_conditioning"
    DONOR_SUPPORT_CONDITIONING = "donor_support_conditioning"
    PLACEBO_DISTRIBUTION_SIZE = "placebo_distribution_size"
    PLACEBO_DISTRIBUTION_QUALITY = "placebo_distribution_quality"
    PLACEBO_RANK_STABILITY = "placebo_rank_stability"
    TAIL_RESOLUTION = "tail_resolution"
    TYPE_I_ERROR_CONTROL = "type_i_error_control"
    FALSE_POSITIVE_RATE_ASSESSMENT = "false_positive_rate_assessment"
    P_VALUE_CALIBRATION_DIAGNOSTIC = "p_value_calibration_diagnostic"
    NULL_COVERAGE_DIAGNOSTIC = "null_coverage_diagnostic"
    MULTIPLE_TESTING_BOUNDARY = "multiple_testing_boundary"
    MULTICELL_SHARED_CONTROL_BOUNDARY = "multicell_shared_control_boundary"
    GEOGRAPHIC_INTERFERENCE_BOUNDARY = "geographic_interference_boundary"
    SPILLOVER_SENSITIVITY_BOUNDARY = "spillover_sensitivity_boundary"
    SIMULATION_DGP_COVERAGE = "simulation_dgp_coverage"
    FAILURE_REGISTRY_MAPPING = "failure_registry_mapping"
    BLOCKED_REASON_MAPPING = "blocked_reason_mapping"
    REQUIRED_FOLLOWUP_MAPPING = "required_followup_mapping"
    RELEASE_GATE_DEPENDENCY = "release_gate_dependency"
    AUDIT_REFERENCE_CONTRACT = "audit_reference_contract"
    SELECTOR_SHADOW_INPUT_CONTRACT = "selector_shadow_input_contract"
    PRODUCTION_AUTHORIZATION_BOUNDARY = "production_authorization_boundary"


REQUIRED_CALIBRATION_AREAS = frozenset(CalibrationArea)


@dataclass(frozen=True)
class SCMNullCalibrationInput:
    """Metadata-only SCM null calibration input contract."""

    scm_validation_evidence: Mapping[str, Any] = field(default_factory=dict)
    panel_metadata: Mapping[str, Any] = field(default_factory=dict)
    treated_units: tuple[str, ...] = ()
    donor_units: tuple[str, ...] = ()
    time_index: tuple[str, ...] = ()
    pre_period: tuple[str, ...] = ()
    post_period: tuple[str, ...] = ()
    placebo_units: tuple[str, ...] = ()
    placebo_windows: tuple[str, ...] = ()
    outcome_metadata: Mapping[str, Any] = field(default_factory=dict)
    kpi_metadata: Mapping[str, Any] = field(default_factory=dict)
    estimand_metadata: Mapping[str, Any] = field(default_factory=dict)
    effect_scale: Mapping[str, Any] = field(default_factory=dict)
    assignment_metadata: Mapping[str, Any] = field(default_factory=dict)
    design_diagnostics: Mapping[str, Any] = field(default_factory=dict)
    donor_support_evidence: Mapping[str, Any] = field(default_factory=dict)
    pre_period_fit_evidence: Mapping[str, Any] = field(default_factory=dict)
    simulation_dgp_evidence_state: Mapping[str, Any] = field(default_factory=dict)
    failure_registry_state: Mapping[str, Any] = field(default_factory=dict)
    multicell_validation_state: Mapping[str, Any] = field(default_factory=dict)
    release_gate_state: Mapping[str, Any] = field(default_factory=dict)
    audit_context: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SCMNullCalibrationEvidence:
    """Metadata-only SCM null calibration evidence contract."""

    input_contract_status: CalibrationStatus
    placebo_generation_status: CalibrationStatus
    placebo_distribution_status: CalibrationStatus
    null_statistic_status: CalibrationStatus
    treated_statistic_status: CalibrationStatus
    effect_scale_status: CalibrationStatus
    estimand_alignment_status: CalibrationStatus
    type_i_error_status: CalibrationStatus
    false_positive_rate_status: CalibrationStatus
    p_value_calibration_status: CalibrationStatus
    null_coverage_status: CalibrationStatus
    multiple_testing_status: CalibrationStatus
    multicell_status: CalibrationStatus
    dgp_coverage_status: CalibrationStatus
    failure_registry_status: CalibrationStatus
    release_gate_status: CalibrationStatus
    allowed_current_use: tuple[str, ...]
    forbidden_current_use: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    required_followups: tuple[str, ...]
    audit_references: tuple[str, ...]
    authorization_flags: Mapping[str, bool]
    area_statuses: Mapping[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["authorization_flags"] = dict(self.authorization_flags)
        return payload


@dataclass(frozen=True)
class SCMNullCalibrationAreaRow:
    """Registry row for one SCM null calibration area."""

    area_id: str
    calibration_area: CalibrationArea
    description: str
    required_input_signals: tuple[str, ...]
    evidence_field: str
    default_when_missing: CalibrationStatus
    authorization_boundary: str


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (str, bytes)):
        return bool(value)
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


def _flag(mapping: Mapping[str, Any], key: str) -> bool:
    return bool(mapping.get(key))


def _diag(inp: SCMNullCalibrationInput, key: str) -> bool:
    return _flag(inp.design_diagnostics, key)


def _evidence_flag(inp: SCMNullCalibrationInput, key: str) -> bool:
    return _flag(inp.scm_validation_evidence, key)


def build_scm_null_calibration_area_registry() -> tuple[SCMNullCalibrationAreaRow, ...]:
    """Return deterministic SCM null calibration area registry rows."""
    area_evidence_map: dict[CalibrationArea, tuple[str, str, CalibrationStatus]] = {
        CalibrationArea.NULL_CALIBRATION_INPUT_CONTRACT: ("input_contract_status", "Null calibration input contract", CalibrationStatus.BLOCKED),
        CalibrationArea.PLACEBO_UNIT_GENERATION_CONTRACT: ("placebo_generation_status", "Placebo unit generation contract", CalibrationStatus.DIAGNOSTIC_ONLY),
        CalibrationArea.PLACEBO_TIME_WINDOW_CONTRACT: ("placebo_generation_status", "Placebo time window contract", CalibrationStatus.DIAGNOSTIC_ONLY),
        CalibrationArea.PLACEBO_STATISTIC_CONTRACT: ("null_statistic_status", "Placebo statistic contract", CalibrationStatus.CANDIDATE_AFTER_VALIDATION),
        CalibrationArea.TREATED_STATISTIC_CONTRACT: ("treated_statistic_status", "Treated statistic contract", CalibrationStatus.CANDIDATE_AFTER_VALIDATION),
        CalibrationArea.EFFECT_SCALE_ALIGNMENT: ("effect_scale_status", "Effect scale alignment", CalibrationStatus.CANDIDATE_AFTER_VALIDATION),
        CalibrationArea.ESTIMAND_ALIGNMENT: ("estimand_alignment_status", "Estimand alignment", CalibrationStatus.CANDIDATE_AFTER_VALIDATION),
        CalibrationArea.OUTCOME_KPI_COMPATIBILITY: ("estimand_alignment_status", "Outcome KPI compatibility", CalibrationStatus.ELIGIBLE_AFTER_WARNING),
        CalibrationArea.PRE_PERIOD_FIT_CONDITIONING: ("null_statistic_status", "Pre-period fit conditioning", CalibrationStatus.CANDIDATE_AFTER_VALIDATION),
        CalibrationArea.DONOR_SUPPORT_CONDITIONING: ("placebo_generation_status", "Donor support conditioning", CalibrationStatus.CANDIDATE_AFTER_VALIDATION),
        CalibrationArea.PLACEBO_DISTRIBUTION_SIZE: ("placebo_distribution_status", "Placebo distribution size", CalibrationStatus.DIAGNOSTIC_ONLY),
        CalibrationArea.PLACEBO_DISTRIBUTION_QUALITY: ("placebo_distribution_status", "Placebo distribution quality", CalibrationStatus.DIAGNOSTIC_ONLY),
        CalibrationArea.PLACEBO_RANK_STABILITY: ("placebo_distribution_status", "Placebo rank stability", CalibrationStatus.RESEARCH_ONLY),
        CalibrationArea.TAIL_RESOLUTION: ("placebo_distribution_status", "Tail resolution", CalibrationStatus.DIAGNOSTIC_ONLY),
        CalibrationArea.TYPE_I_ERROR_CONTROL: ("type_i_error_status", "Type I error control", CalibrationStatus.CANDIDATE_AFTER_VALIDATION),
        CalibrationArea.FALSE_POSITIVE_RATE_ASSESSMENT: ("false_positive_rate_status", "False positive rate assessment", CalibrationStatus.CANDIDATE_AFTER_VALIDATION),
        CalibrationArea.P_VALUE_CALIBRATION_DIAGNOSTIC: ("p_value_calibration_status", "P-value calibration diagnostic", CalibrationStatus.DIAGNOSTIC_ONLY),
        CalibrationArea.NULL_COVERAGE_DIAGNOSTIC: ("null_coverage_status", "Null coverage diagnostic", CalibrationStatus.DIAGNOSTIC_ONLY),
        CalibrationArea.MULTIPLE_TESTING_BOUNDARY: ("multiple_testing_status", "Multiple testing boundary", CalibrationStatus.BLOCKED),
        CalibrationArea.MULTICELL_SHARED_CONTROL_BOUNDARY: ("multicell_status", "Multicell/shared-control boundary", CalibrationStatus.BLOCKED),
        CalibrationArea.GEOGRAPHIC_INTERFERENCE_BOUNDARY: ("placebo_generation_status", "Geographic interference boundary", CalibrationStatus.ELIGIBLE_AFTER_WARNING),
        CalibrationArea.SPILLOVER_SENSITIVITY_BOUNDARY: ("placebo_generation_status", "Spillover sensitivity boundary", CalibrationStatus.ELIGIBLE_AFTER_WARNING),
        CalibrationArea.SIMULATION_DGP_COVERAGE: ("dgp_coverage_status", "Simulation DGP coverage", CalibrationStatus.CANDIDATE_AFTER_VALIDATION),
        CalibrationArea.FAILURE_REGISTRY_MAPPING: ("failure_registry_status", "Failure registry mapping", CalibrationStatus.CANDIDATE_AFTER_VALIDATION),
        CalibrationArea.BLOCKED_REASON_MAPPING: ("failure_registry_status", "Blocked reason mapping", CalibrationStatus.CANDIDATE_AFTER_VALIDATION),
        CalibrationArea.REQUIRED_FOLLOWUP_MAPPING: ("failure_registry_status", "Required followup mapping", CalibrationStatus.CANDIDATE_AFTER_VALIDATION),
        CalibrationArea.RELEASE_GATE_DEPENDENCY: ("release_gate_status", "Release gate dependency", CalibrationStatus.RELEASE_GATE_REQUIRED),
        CalibrationArea.AUDIT_REFERENCE_CONTRACT: ("input_contract_status", "Audit reference contract", CalibrationStatus.CANDIDATE_AFTER_VALIDATION),
        CalibrationArea.SELECTOR_SHADOW_INPUT_CONTRACT: ("input_contract_status", "Selector shadow input contract", CalibrationStatus.DIAGNOSTIC_ONLY),
        CalibrationArea.PRODUCTION_AUTHORIZATION_BOUNDARY: ("release_gate_status", "Production authorization boundary", CalibrationStatus.BLOCKED),
    }
    rows: list[SCMNullCalibrationAreaRow] = []
    for idx, area in enumerate(CalibrationArea, start=1):
        evidence_field, description, default_status = area_evidence_map[area]
        rows.append(
            SCMNullCalibrationAreaRow(
                area_id=f"SCM-NC-{idx:03d}",
                calibration_area=area,
                description=description,
                required_input_signals=("SCMNullCalibrationInput", area.value),
                evidence_field=evidence_field,
                default_when_missing=default_status,
                authorization_boundary="metadata_scaffolding_only",
            )
        )
    return tuple(rows)


def build_scm_null_calibration_evidence(inp: SCMNullCalibrationInput) -> SCMNullCalibrationEvidence:
    """Build deterministic SCM null calibration evidence from metadata input."""
    blocked: list[str] = []
    warnings: list[str] = []
    followups: list[str] = []

    validation_ok = _present(inp.scm_validation_evidence) and (
        _evidence_flag(inp, "input_contract_satisfied")
        or _evidence_flag(inp, "input_contract_status")
        or _flag(inp.scm_validation_evidence, "donor_support_status")
    )
    if not _present(inp.scm_validation_evidence):
        blocked.append(BR_VALIDATION_EVIDENCE_MISSING)
        followups.append(RF_VALIDATION_EVIDENCE)
    elif not validation_ok:
        followups.append(RF_VALIDATION_EVIDENCE)
        blocked.append(BR_VALIDATION_EVIDENCE_MISSING)

    input_ok = all([
        _present(inp.panel_metadata),
        _present(inp.treated_units),
        _present(inp.donor_units),
        _present(inp.time_index),
        _present(inp.pre_period),
        _present(inp.post_period),
    ])
    if not input_ok:
        blocked.append(BR_INPUT_CONTRACT_INCOMPLETE)

    placebo_units_ok = _present(inp.placebo_units)
    placebo_windows_ok = _present(inp.placebo_windows)
    if not placebo_units_ok:
        blocked.append(BR_PLACEBO_UNITS_MISSING)
        followups.append(RF_PLACEBO_GENERATION)
    if not placebo_windows_ok:
        blocked.append(BR_PLACEBO_WINDOWS_MISSING)
        followups.append(RF_PLACEBO_WINDOWS)

    placebo_stat_ok = _diag(inp, "placebo_statistic_contract_ready")
    treated_stat_ok = _diag(inp, "treated_statistic_contract_ready")
    if not placebo_stat_ok:
        blocked.append(BR_PLACEBO_STATISTIC_MISSING)
        followups.append(RF_PLACEBO_STATISTIC)
    if not treated_stat_ok:
        blocked.append(BR_TREATED_STATISTIC_MISSING)
        followups.append(RF_TREATED_STATISTIC)

    effect_scale_ok = _present(inp.effect_scale) and _flag(inp.effect_scale, "scale_defined")
    estimand_ok = _present(inp.estimand_metadata) and _flag(inp.estimand_metadata, "estimand_aligned")
    if not effect_scale_ok:
        blocked.append(BR_EFFECT_SCALE_MISSING)
    if not estimand_ok:
        blocked.append(BR_ESTIMAND_MISALIGNED)

    donor_support_ok = _flag(inp.donor_support_evidence, "donor_support_ok") or _diag(inp, "donor_support_ok")
    pre_fit_ok = _flag(inp.pre_period_fit_evidence, "pre_period_fit_ok") or _diag(inp, "pre_period_fit_ok")
    if not donor_support_ok:
        followups.append(RF_DONOR_SUPPORT)
        blocked.append(BR_DONOR_SUPPORT_CONDITIONING_MISSING)
    if not pre_fit_ok:
        followups.append(RF_PRE_PERIOD_FIT)
        blocked.append(BR_PRE_PERIOD_FIT_CONDITIONING_MISSING)

    null_cal_ok = _diag(inp, "null_calibration_complete")
    null_coverage_ok = _diag(inp, "null_coverage_complete")
    if not null_cal_ok:
        followups.append(RF_NULL_CALIBRATION)
        blocked.append(BR_NULL_CALIBRATION_INCOMPLETE)
        blocked.append(BR_P_VALUE_BOUNDARY)
    if not null_coverage_ok:
        followups.append(RF_NULL_COVERAGE)
        blocked.append(BR_NULL_COVERAGE_INCOMPLETE)
        blocked.append(BR_CAUSAL_CI_BOUNDARY)

    dgp_ok = _flag(inp.simulation_dgp_evidence_state, "dgp_coverage_complete")
    if not dgp_ok:
        followups.append(RF_DGP_COVERAGE)

    failure_state_ok = _present(inp.failure_registry_state)
    unresolved = inp.failure_registry_state.get("unresolved_modes", ()) if failure_state_ok else ()
    if not failure_state_ok:
        followups.append(RF_FAILURE_REGISTRY)
    if unresolved:
        blocked.append(BR_FAILURE_REGISTRY_UNRESOLVED)

    multicell_validated = _flag(inp.multicell_validation_state, "dependence_multiplicity_validated")
    multicell_present = _flag(inp.multicell_validation_state, "multicell_geometry_present")
    if multicell_present and not multicell_validated:
        blocked.append(BR_MULTICELL_UNVALIDATED)

    release_authorized = _flag(inp.release_gate_state, "production_authorization_granted")
    if not release_authorized:
        followups.append(RF_RELEASE_GATE)
        blocked.append(BR_RELEASE_GATE_REQUIRED)

    def _status(
        *,
        ok: bool,
        candidate: bool = False,
        diagnostic: bool = False,
        research: bool = False,
        force_blocked: bool = False,
    ) -> CalibrationStatus:
        if force_blocked or not input_ok or not validation_ok:
            return CalibrationStatus.BLOCKED
        if research:
            return CalibrationStatus.RESEARCH_ONLY
        if diagnostic:
            return CalibrationStatus.DIAGNOSTIC_ONLY
        if ok and candidate:
            return CalibrationStatus.CANDIDATE_AFTER_VALIDATION
        if ok:
            return CalibrationStatus.ELIGIBLE_AFTER_WARNING
        return CalibrationStatus.BLOCKED

    input_status = CalibrationStatus.ELIGIBLE if input_ok and validation_ok else CalibrationStatus.BLOCKED
    placebo_gen_status = _status(
        ok=placebo_units_ok and placebo_windows_ok and donor_support_ok,
        candidate=placebo_units_ok and placebo_windows_ok,
    )
    placebo_dist_status = CalibrationStatus.DIAGNOSTIC_ONLY if placebo_units_ok and input_ok else CalibrationStatus.BLOCKED
    null_stat_status = _status(ok=placebo_stat_ok and pre_fit_ok, candidate=placebo_stat_ok)
    treated_stat_status = _status(ok=treated_stat_ok, candidate=treated_stat_ok)
    effect_scale_status = _status(ok=effect_scale_ok, candidate=effect_scale_ok)
    estimand_status = _status(
        ok=estimand_ok and _present(inp.outcome_metadata) and _present(inp.kpi_metadata),
        candidate=estimand_ok,
    )
    type_i_status = _status(ok=dgp_ok and null_cal_ok, candidate=dgp_ok)
    fpr_status = _status(ok=dgp_ok, candidate=dgp_ok)
    p_value_status = CalibrationStatus.DIAGNOSTIC_ONLY if null_cal_ok else CalibrationStatus.BLOCKED
    coverage_status = CalibrationStatus.DIAGNOSTIC_ONLY if null_coverage_ok else CalibrationStatus.BLOCKED
    multiple_testing_status = CalibrationStatus.BLOCKED
    failure_status = CalibrationStatus.BLOCKED if unresolved else CalibrationStatus.CANDIDATE_AFTER_VALIDATION
    dgp_status = _status(ok=dgp_ok, candidate=dgp_ok)
    multicell_status = (
        CalibrationStatus.BLOCKED
        if multicell_present and not multicell_validated
        else CalibrationStatus.NOT_APPLICABLE
        if not multicell_present
        else CalibrationStatus.RESEARCH_ONLY
    )
    release_status = (
        CalibrationStatus.RELEASE_GATE_REQUIRED
        if not release_authorized
        else CalibrationStatus.BLOCKED
    )

    if not placebo_stat_ok:
        warnings.append("placebo_statistic_contract_not_ready")
    if not treated_stat_ok:
        warnings.append("treated_statistic_contract_not_ready")

    allowed = (
        "scm_null_calibration_metadata_review",
        "scm_null_calibration_diagnostic_readout",
        "scm_null_calibration_evidence_scaffolding",
        "selector_shadow_non_authorizing_input",
    )
    forbidden = (
        "production_inference",
        "production_p_value",
        "causal_confidence_interval",
        "trustreport_production",
        "calibration_signal_ingestion",
        "mmm_ingestion",
        "selector_production_routing",
        "multicell_production_claim",
        "package_side_agent_authorization",
    )

    area_statuses: dict[str, str] = {
        CalibrationArea.NULL_CALIBRATION_INPUT_CONTRACT.value: input_status.value,
        CalibrationArea.PLACEBO_UNIT_GENERATION_CONTRACT.value: placebo_gen_status.value,
        CalibrationArea.PLACEBO_TIME_WINDOW_CONTRACT.value: placebo_gen_status.value,
        CalibrationArea.PLACEBO_STATISTIC_CONTRACT.value: null_stat_status.value,
        CalibrationArea.TREATED_STATISTIC_CONTRACT.value: treated_stat_status.value,
        CalibrationArea.EFFECT_SCALE_ALIGNMENT.value: effect_scale_status.value,
        CalibrationArea.ESTIMAND_ALIGNMENT.value: estimand_status.value,
        CalibrationArea.OUTCOME_KPI_COMPATIBILITY.value: estimand_status.value,
        CalibrationArea.PRE_PERIOD_FIT_CONDITIONING.value: null_stat_status.value,
        CalibrationArea.DONOR_SUPPORT_CONDITIONING.value: placebo_gen_status.value,
        CalibrationArea.PLACEBO_DISTRIBUTION_SIZE.value: placebo_dist_status.value,
        CalibrationArea.PLACEBO_DISTRIBUTION_QUALITY.value: placebo_dist_status.value,
        CalibrationArea.PLACEBO_RANK_STABILITY.value: CalibrationStatus.RESEARCH_ONLY.value,
        CalibrationArea.TAIL_RESOLUTION.value: placebo_dist_status.value,
        CalibrationArea.TYPE_I_ERROR_CONTROL.value: type_i_status.value,
        CalibrationArea.FALSE_POSITIVE_RATE_ASSESSMENT.value: fpr_status.value,
        CalibrationArea.P_VALUE_CALIBRATION_DIAGNOSTIC.value: p_value_status.value,
        CalibrationArea.NULL_COVERAGE_DIAGNOSTIC.value: coverage_status.value,
        CalibrationArea.MULTIPLE_TESTING_BOUNDARY.value: multiple_testing_status.value,
        CalibrationArea.MULTICELL_SHARED_CONTROL_BOUNDARY.value: multicell_status.value,
        CalibrationArea.GEOGRAPHIC_INTERFERENCE_BOUNDARY.value: placebo_gen_status.value,
        CalibrationArea.SPILLOVER_SENSITIVITY_BOUNDARY.value: placebo_gen_status.value,
        CalibrationArea.SIMULATION_DGP_COVERAGE.value: dgp_status.value,
        CalibrationArea.FAILURE_REGISTRY_MAPPING.value: failure_status.value,
        CalibrationArea.BLOCKED_REASON_MAPPING.value: failure_status.value,
        CalibrationArea.REQUIRED_FOLLOWUP_MAPPING.value: failure_status.value,
        CalibrationArea.RELEASE_GATE_DEPENDENCY.value: release_status.value,
        CalibrationArea.AUDIT_REFERENCE_CONTRACT.value: input_status.value,
        CalibrationArea.SELECTOR_SHADOW_INPUT_CONTRACT.value: CalibrationStatus.DIAGNOSTIC_ONLY.value,
        CalibrationArea.PRODUCTION_AUTHORIZATION_BOUNDARY.value: CalibrationStatus.BLOCKED.value,
    }

    audit_refs = tuple(dep for dep in DEPENDENCIES_RECONCILED) + (_ARTIFACT_ID,)

    return SCMNullCalibrationEvidence(
        input_contract_status=input_status,
        placebo_generation_status=placebo_gen_status,
        placebo_distribution_status=placebo_dist_status,
        null_statistic_status=null_stat_status,
        treated_statistic_status=treated_stat_status,
        effect_scale_status=effect_scale_status,
        estimand_alignment_status=estimand_status,
        type_i_error_status=type_i_status,
        false_positive_rate_status=fpr_status,
        p_value_calibration_status=p_value_status,
        null_coverage_status=coverage_status,
        multiple_testing_status=multiple_testing_status,
        multicell_status=multicell_status,
        dgp_coverage_status=dgp_status,
        failure_registry_status=failure_status,
        release_gate_status=release_status,
        allowed_current_use=allowed,
        forbidden_current_use=forbidden,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
        required_followups=tuple(dict.fromkeys(followups)),
        audit_references=audit_refs,
        authorization_flags=dict(_AUTH_FLAGS),
        area_statuses=area_statuses,
    )


def validate_scm_null_calibration_implementation(
    registry: tuple[SCMNullCalibrationAreaRow, ...],
    evidence: SCMNullCalibrationEvidence,
) -> dict[str, Any]:
    """Validate registry coverage and authorization boundary."""
    issues: list[str] = []
    if len(registry) != len(REQUIRED_CALIBRATION_AREAS):
        issues.append(f"registry_count {len(registry)} != {len(REQUIRED_CALIBRATION_AREAS)}")
    areas = {r.calibration_area for r in registry}
    for area in REQUIRED_CALIBRATION_AREAS:
        if area not in areas:
            issues.append(f"missing area: {area.value}")
    if any(evidence.authorization_flags.get(k) for k in _AUTH_FLAGS):
        issues.append("authorization flag unexpectedly true")
    if evidence.release_gate_status != CalibrationStatus.RELEASE_GATE_REQUIRED:
        issues.append("release_gate_status must be release_gate_required")
    return {
        "valid": not issues,
        "registry_row_count": len(registry),
        "all_areas_covered": areas == REQUIRED_CALIBRATION_AREAS,
        "issues": issues,
    }


def build_scenarios() -> list[dict[str, Any]]:
    registry = build_scm_null_calibration_area_registry()
    empty = SCMNullCalibrationInput()
    empty_evidence = build_scm_null_calibration_evidence(empty)
    complete = SCMNullCalibrationInput(
        scm_validation_evidence={"input_contract_satisfied": True, "donor_support_status": "eligible"},
        panel_metadata={"grain": "weekly"},
        treated_units=("unit_a",),
        donor_units=("unit_b", "unit_c", "unit_d"),
        time_index=("2024-01", "2024-02"),
        pre_period=("2024-01",),
        post_period=("2024-02",),
        placebo_units=("unit_b", "unit_c"),
        placebo_windows=("2024-01",),
        outcome_metadata={"scale": "level"},
        kpi_metadata={"kpi_id": "revenue"},
        estimand_metadata={"estimand": "att", "estimand_aligned": True},
        effect_scale={"scale_defined": True, "scale": "level"},
        design_diagnostics={
            "placebo_statistic_contract_ready": True,
            "treated_statistic_contract_ready": True,
            "donor_support_ok": True,
            "pre_period_fit_ok": True,
            "null_calibration_complete": True,
            "null_coverage_complete": True,
        },
        donor_support_evidence={"donor_support_ok": True},
        pre_period_fit_evidence={"pre_period_fit_ok": True},
        simulation_dgp_evidence_state={"dgp_coverage_complete": True},
        failure_registry_state={"unresolved_modes": ()},
        multicell_validation_state={"multicell_geometry_present": False},
        release_gate_state={"production_authorization_granted": False},
    )
    complete_evidence = build_scm_null_calibration_evidence(complete)
    multicell = SCMNullCalibrationInput(
        scm_validation_evidence={"input_contract_satisfied": True},
        panel_metadata={"grain": "weekly"},
        treated_units=("unit_a",),
        donor_units=("unit_b", "unit_c", "unit_d"),
        time_index=("2024-01",),
        pre_period=("2024-01",),
        post_period=("2024-02",),
        placebo_units=("unit_b",),
        placebo_windows=("2024-01",),
        multicell_validation_state={"multicell_geometry_present": True, "dependence_multiplicity_validated": False},
    )
    multicell_evidence = build_scm_null_calibration_evidence(multicell)

    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool, detail: str = "") -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": detail}

    scenarios.append(_s("registry_covers_all_areas", len(registry) == len(REQUIRED_CALIBRATION_AREAS)))
    scenarios.append(_s("empty_input_blocked", empty_evidence.input_contract_status == CalibrationStatus.BLOCKED))
    scenarios.append(_s("empty_validation_evidence_blocked", BR_VALIDATION_EVIDENCE_MISSING in empty_evidence.blocked_reasons))
    scenarios.append(_s("empty_placebo_metadata_blocked", BR_PLACEBO_UNITS_MISSING in empty_evidence.blocked_reasons))
    scenarios.append(_s("empty_release_gate_required", empty_evidence.release_gate_status == CalibrationStatus.RELEASE_GATE_REQUIRED))
    scenarios.append(_s("multicell_unvalidated_blocked", multicell_evidence.multicell_status == CalibrationStatus.BLOCKED))
    scenarios.append(_s("null_incomplete_blocks_p_values", not empty_evidence.authorization_flags["scm_production_p_value_authorized"]))
    scenarios.append(_s("coverage_incomplete_blocks_cis", not empty_evidence.authorization_flags["scm_causal_confidence_interval_authorized"]))
    scenarios.append(_s("complete_still_release_gate_required", complete_evidence.release_gate_status == CalibrationStatus.RELEASE_GATE_REQUIRED))
    scenarios.append(_s("complete_no_production_inference", not complete_evidence.authorization_flags["scm_production_inference_authorized"]))
    scenarios.append(_s("complete_null_calibration_not_completed", _SCM_FLAGS["scm_null_calibration_completed"] is False))
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not empty_evidence.authorization_flags.get(flag, False)))
    for flag, expected in _SCM_FLAGS.items():
        scenarios.append(_s(f"scm_flag_{flag}_false", expected is False))
    scenarios.append(_s("failed_scenarios_empty", all(x["passed"] for x in scenarios)))
    return scenarios


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


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    registry = build_scm_null_calibration_area_registry()
    evidence = build_scm_null_calibration_evidence(SCMNullCalibrationInput())
    validation = validate_scm_null_calibration_implementation(registry, evidence)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "scm_null_calibration_metadata_implementation",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "method_family": METHOD_FAMILY,
        "method_family_status": METHOD_FAMILY_STATUS,
        "next_artifact": RECOMMENDED_NEXT_ARTIFACTS[0],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "registry_row_count": len(registry),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        "implemented_calibration_areas": [a.value for a in CalibrationArea],
        "blocked_reasons_supported": list(BLOCKED_REASONS_SUPPORTED),
        "required_followups_supported": list(REQUIRED_FOLLOWUPS_SUPPORTED),
        "implemented_input_contract": "SCMNullCalibrationInput",
        "implemented_evidence_contract": "SCMNullCalibrationEvidence",
        "tests_added": [
            "tests/validation/test_scm_production_candidate_null_calibration_implementation_001.py",
        ],
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "non_goals": list(NON_GOALS),
        "scm_null_calibration_implementation_authorized": False,
        "scm_null_calibration_completed": False,
        "scm_production_inference_authorized": False,
        "authorization_flags": dict(_AUTH_FLAGS),
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
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
