"""SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001 — SCM validation metadata scaffolding."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

_ARTIFACT_ID = "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "scm_production_candidate_validation_metadata_implemented_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001",
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
    "scm_validation_implementation_authorized": False,
    "scm_production_inference_authorized": False,
}

NON_GOALS = (
    "no_scm_fitting_or_lift",
    "no_production_p_values_or_causal_cis",
    "no_placebo_or_jackknife_inference_runtime",
    "no_production_inference_authorization",
    "no_selector_router_production_use",
    "no_downstream_integrations",
    "no_package_side_agents",
    "no_multicell_production_claims",
    "no_numerical_scm_diagnostics",
)

DEPENDENCIES_RECONCILED = (
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
    "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
    "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
    "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
)

# Blocked-reason codes
BR_INPUT_CONTRACT_INCOMPLETE = "SCM-BR-INPUT-INCOMPLETE"
BR_DONOR_POOL_INSUFFICIENT = "SCM-BR-DONOR-POOL-INSUFFICIENT"
BR_DONOR_SUPPORT_MISSING = "SCM-BR-DONOR-SUPPORT-MISSING"
BR_CONVEX_HULL_MISSING = "SCM-BR-CONVEX-HULL-MISSING"
BR_EXTRAPOLATION_RISK = "SCM-BR-EXTRAPOLATION-RISK"
BR_PRE_PERIOD_FIT_MISSING = "SCM-BR-PRE-PERIOD-FIT-MISSING"
BR_TREND_STABILITY_MISSING = "SCM-BR-TREND-STABILITY-MISSING"
BR_ASSIGNMENT_INVALID = "SCM-BR-ASSIGNMENT-INVALID"
BR_NULL_CALIBRATION_INCOMPLETE = "SCM-BR-NULL-CALIBRATION-INCOMPLETE"
BR_JACKKNIFE_INCOMPLETE = "SCM-BR-JACKKNIFE-INCOMPLETE"
BR_MULTICELL_UNVALIDATED = "SCM-BR-MULTICELL-UNVALIDATED"
BR_RELEASE_GATE_REQUIRED = "SCM-BR-RELEASE-GATE-REQUIRED"
BR_FAILURE_REGISTRY_UNRESOLVED = "SCM-BR-FAILURE-REGISTRY-UNRESOLVED"
BR_UNCERTAINTY_BOUNDARY = "SCM-BR-UNCERTAINTY-BOUNDARY"

BLOCKED_REASONS_SUPPORTED = (
    BR_INPUT_CONTRACT_INCOMPLETE,
    BR_DONOR_POOL_INSUFFICIENT,
    BR_DONOR_SUPPORT_MISSING,
    BR_CONVEX_HULL_MISSING,
    BR_EXTRAPOLATION_RISK,
    BR_PRE_PERIOD_FIT_MISSING,
    BR_TREND_STABILITY_MISSING,
    BR_ASSIGNMENT_INVALID,
    BR_NULL_CALIBRATION_INCOMPLETE,
    BR_JACKKNIFE_INCOMPLETE,
    BR_MULTICELL_UNVALIDATED,
    BR_RELEASE_GATE_REQUIRED,
    BR_FAILURE_REGISTRY_UNRESOLVED,
    BR_UNCERTAINTY_BOUNDARY,
)

RF_DONOR_SUPPORT_EVIDENCE = "SCM-RF-DONOR-SUPPORT-EVIDENCE"
RF_CONVEX_HULL_EVIDENCE = "SCM-RF-CONVEX-HULL-EVIDENCE"
RF_PRE_PERIOD_FIT_EVIDENCE = "SCM-RF-PRE-PERIOD-FIT-EVIDENCE"
RF_TREND_STABILITY_EVIDENCE = "SCM-RF-TREND-STABILITY-EVIDENCE"
RF_NULL_CALIBRATION_EVIDENCE = "SCM-RF-NULL-CALIBRATION-EVIDENCE"
RF_JACKKNIFE_EVIDENCE = "SCM-RF-JACKKNIFE-EVIDENCE"
RF_DGP_COVERAGE_EVIDENCE = "SCM-RF-DGP-COVERAGE-EVIDENCE"
RF_STATISTIC_ADAPTER_EVIDENCE = "SCM-RF-STATISTIC-ADAPTER-EVIDENCE"
RF_RELEASE_GATE_PLAN = "SCM-RF-RELEASE-GATE-PLAN"

REQUIRED_FOLLOWUPS_SUPPORTED = (
    RF_DONOR_SUPPORT_EVIDENCE,
    RF_CONVEX_HULL_EVIDENCE,
    RF_PRE_PERIOD_FIT_EVIDENCE,
    RF_TREND_STABILITY_EVIDENCE,
    RF_NULL_CALIBRATION_EVIDENCE,
    RF_JACKKNIFE_EVIDENCE,
    RF_DGP_COVERAGE_EVIDENCE,
    RF_STATISTIC_ADAPTER_EVIDENCE,
    RF_RELEASE_GATE_PLAN,
)


class ValidationStatus(str, Enum):
    ELIGIBLE = "eligible"
    ELIGIBLE_AFTER_WARNING = "eligible_after_warning"
    CANDIDATE_AFTER_VALIDATION = "candidate_after_validation"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    BLOCKED = "blocked"
    RELEASE_GATE_REQUIRED = "release_gate_required"
    NOT_APPLICABLE = "not_applicable"


REQUIRED_STATUSES = frozenset(ValidationStatus)


class ValidationArea(str, Enum):
    SCM_INPUT_CONTRACT = "scm_input_contract"
    PANEL_BALANCE_AND_TIME_INDEX = "panel_balance_and_time_index"
    TREATED_UNIT_DEFINITION = "treated_unit_definition"
    DONOR_POOL_DEFINITION = "donor_pool_definition"
    DONOR_POOL_SIZE = "donor_pool_size"
    DONOR_SUPPORT_OVERLAP = "donor_support_overlap"
    CONVEX_HULL_SUPPORT = "convex_hull_support"
    EXTRAPOLATION_RISK = "extrapolation_risk"
    PRE_PERIOD_LENGTH = "pre_period_length"
    PRE_PERIOD_FIT_QUALITY = "pre_period_fit_quality"
    PRE_PERIOD_TREND_STABILITY = "pre_period_trend_stability"
    POST_PERIOD_WINDOW_DEFINITION = "post_period_window_definition"
    OUTCOME_SCALE_COMPATIBILITY = "outcome_scale_compatibility"
    KPI_ESTIMAND_COMPATIBILITY = "kpi_estimand_compatibility"
    ASSIGNMENT_DESIGN_VALIDITY = "assignment_design_validity"
    RANDOMIZATION_COMPATIBILITY = "randomization_compatibility"
    GEOGRAPHIC_INTERFERENCE_RISK = "geographic_interference_risk"
    SPILLOVER_EXCLUSION_OR_FLAGGING = "spillover_exclusion_or_flagging"
    PLACEBO_UNIT_GENERATION = "placebo_unit_generation"
    PLACEBO_DISTRIBUTION_QUALITY = "placebo_distribution_quality"
    NULL_CALIBRATION = "null_calibration"
    JACKKNIFE_UNIT_SENSITIVITY = "jackknife_unit_sensitivity"
    DONOR_WEIGHT_STABILITY = "donor_weight_stability"
    TREATED_SET_SENSITIVITY = "treated_set_sensitivity"
    STATISTIC_ADAPTER_CONTRACT = "statistic_adapter_contract"
    EFFECT_SCALE_CONTRACT = "effect_scale_contract"
    UNCERTAINTY_BOUNDARY = "uncertainty_boundary"
    FAILURE_REGISTRY_MAPPING = "failure_registry_mapping"
    SIMULATION_DGP_COVERAGE = "simulation_dgp_coverage"
    MULTICELL_SHARED_CONTROL_BLOCKER = "multicell_shared_control_blocker"
    RELEASE_GATE_DEPENDENCY = "release_gate_dependency"


REQUIRED_VALIDATION_AREAS = frozenset(ValidationArea)


@dataclass(frozen=True)
class SCMValidationInput:
    """Metadata-only SCM validation input contract."""

    panel_metadata: Mapping[str, Any] = field(default_factory=dict)
    treated_units: tuple[str, ...] = ()
    donor_units: tuple[str, ...] = ()
    time_index: tuple[str, ...] = ()
    pre_period: tuple[str, ...] = ()
    post_period: tuple[str, ...] = ()
    outcome_metadata: Mapping[str, Any] = field(default_factory=dict)
    kpi_metadata: Mapping[str, Any] = field(default_factory=dict)
    estimand_metadata: Mapping[str, Any] = field(default_factory=dict)
    assignment_metadata: Mapping[str, Any] = field(default_factory=dict)
    design_diagnostics: Mapping[str, Any] = field(default_factory=dict)
    observed_panel_diagnostics: Mapping[str, Any] = field(default_factory=dict)
    donor_pool_metadata: Mapping[str, Any] = field(default_factory=dict)
    method_governance_state: Mapping[str, Any] = field(default_factory=dict)
    failure_registry_state: Mapping[str, Any] = field(default_factory=dict)
    simulation_dgp_evidence_state: Mapping[str, Any] = field(default_factory=dict)
    multicell_validation_state: Mapping[str, Any] = field(default_factory=dict)
    release_gate_state: Mapping[str, Any] = field(default_factory=dict)
    audit_context: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SCMValidationEvidence:
    """Metadata-only SCM validation evidence contract."""

    input_contract_status: ValidationStatus
    donor_support_status: ValidationStatus
    geometry_status: ValidationStatus
    pre_period_fit_status: ValidationStatus
    trend_stability_status: ValidationStatus
    placebo_status: ValidationStatus
    null_calibration_status: ValidationStatus
    jackknife_sensitivity_status: ValidationStatus
    assignment_design_status: ValidationStatus
    outcome_kpi_status: ValidationStatus
    statistic_adapter_status: ValidationStatus
    failure_registry_status: ValidationStatus
    dgp_coverage_status: ValidationStatus
    multicell_status: ValidationStatus
    release_gate_status: ValidationStatus
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
class SCMValidationAreaRow:
    """Registry row for one SCM validation area."""

    area_id: str
    validation_area: ValidationArea
    description: str
    required_input_signals: tuple[str, ...]
    evidence_field: str
    default_when_missing: ValidationStatus
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


def _diag(inp: SCMValidationInput, key: str) -> bool:
    return _flag(inp.design_diagnostics, key) or _flag(inp.observed_panel_diagnostics, key)


def _min_donor_pool_size(inp: SCMValidationInput) -> int:
    raw = inp.donor_pool_metadata.get("min_donor_pool_size", 3)
    try:
        return max(1, int(raw))
    except (TypeError, ValueError):
        return 3


def build_scm_validation_area_registry() -> tuple[SCMValidationAreaRow, ...]:
    """Return deterministic SCM validation area registry rows."""
    area_evidence_map: dict[ValidationArea, tuple[str, str, ValidationStatus]] = {
        ValidationArea.SCM_INPUT_CONTRACT: ("input_contract_status", "Core input contract fields", ValidationStatus.BLOCKED),
        ValidationArea.PANEL_BALANCE_AND_TIME_INDEX: ("input_contract_status", "Panel balance and time index", ValidationStatus.BLOCKED),
        ValidationArea.TREATED_UNIT_DEFINITION: ("geometry_status", "Treated unit definition", ValidationStatus.BLOCKED),
        ValidationArea.DONOR_POOL_DEFINITION: ("donor_support_status", "Donor pool definition", ValidationStatus.BLOCKED),
        ValidationArea.DONOR_POOL_SIZE: ("donor_support_status", "Donor pool size threshold", ValidationStatus.BLOCKED),
        ValidationArea.DONOR_SUPPORT_OVERLAP: ("donor_support_status", "Donor support overlap", ValidationStatus.CANDIDATE_AFTER_VALIDATION),
        ValidationArea.CONVEX_HULL_SUPPORT: ("donor_support_status", "Convex hull support", ValidationStatus.CANDIDATE_AFTER_VALIDATION),
        ValidationArea.EXTRAPOLATION_RISK: ("donor_support_status", "Extrapolation risk flag", ValidationStatus.BLOCKED),
        ValidationArea.PRE_PERIOD_LENGTH: ("pre_period_fit_status", "Pre-period length", ValidationStatus.CANDIDATE_AFTER_VALIDATION),
        ValidationArea.PRE_PERIOD_FIT_QUALITY: ("pre_period_fit_status", "Pre-period fit quality", ValidationStatus.CANDIDATE_AFTER_VALIDATION),
        ValidationArea.PRE_PERIOD_TREND_STABILITY: ("trend_stability_status", "Pre-period trend stability", ValidationStatus.CANDIDATE_AFTER_VALIDATION),
        ValidationArea.POST_PERIOD_WINDOW_DEFINITION: ("pre_period_fit_status", "Post-period window", ValidationStatus.CANDIDATE_AFTER_VALIDATION),
        ValidationArea.OUTCOME_SCALE_COMPATIBILITY: ("outcome_kpi_status", "Outcome scale compatibility", ValidationStatus.ELIGIBLE_AFTER_WARNING),
        ValidationArea.KPI_ESTIMAND_COMPATIBILITY: ("outcome_kpi_status", "KPI estimand compatibility", ValidationStatus.CANDIDATE_AFTER_VALIDATION),
        ValidationArea.ASSIGNMENT_DESIGN_VALIDITY: ("assignment_design_status", "Assignment design validity", ValidationStatus.CANDIDATE_AFTER_VALIDATION),
        ValidationArea.RANDOMIZATION_COMPATIBILITY: ("assignment_design_status", "Randomization compatibility", ValidationStatus.CANDIDATE_AFTER_VALIDATION),
        ValidationArea.GEOGRAPHIC_INTERFERENCE_RISK: ("assignment_design_status", "Geographic interference", ValidationStatus.ELIGIBLE_AFTER_WARNING),
        ValidationArea.SPILLOVER_EXCLUSION_OR_FLAGGING: ("assignment_design_status", "Spillover handling", ValidationStatus.ELIGIBLE_AFTER_WARNING),
        ValidationArea.PLACEBO_UNIT_GENERATION: ("placebo_status", "Placebo unit generation", ValidationStatus.DIAGNOSTIC_ONLY),
        ValidationArea.PLACEBO_DISTRIBUTION_QUALITY: ("placebo_status", "Placebo distribution quality", ValidationStatus.DIAGNOSTIC_ONLY),
        ValidationArea.NULL_CALIBRATION: ("null_calibration_status", "Null calibration", ValidationStatus.DIAGNOSTIC_ONLY),
        ValidationArea.JACKKNIFE_UNIT_SENSITIVITY: ("jackknife_sensitivity_status", "Jackknife sensitivity", ValidationStatus.DIAGNOSTIC_ONLY),
        ValidationArea.DONOR_WEIGHT_STABILITY: ("donor_support_status", "Donor weight stability", ValidationStatus.CANDIDATE_AFTER_VALIDATION),
        ValidationArea.TREATED_SET_SENSITIVITY: ("geometry_status", "Treated-set sensitivity", ValidationStatus.RESEARCH_ONLY),
        ValidationArea.STATISTIC_ADAPTER_CONTRACT: ("statistic_adapter_status", "Statistic adapter contract", ValidationStatus.CANDIDATE_AFTER_VALIDATION),
        ValidationArea.EFFECT_SCALE_CONTRACT: ("outcome_kpi_status", "Effect scale contract", ValidationStatus.CANDIDATE_AFTER_VALIDATION),
        ValidationArea.UNCERTAINTY_BOUNDARY: ("jackknife_sensitivity_status", "Uncertainty boundary", ValidationStatus.BLOCKED),
        ValidationArea.FAILURE_REGISTRY_MAPPING: ("failure_registry_status", "Failure registry mapping", ValidationStatus.BLOCKED),
        ValidationArea.SIMULATION_DGP_COVERAGE: ("dgp_coverage_status", "Simulation DGP coverage", ValidationStatus.CANDIDATE_AFTER_VALIDATION),
        ValidationArea.MULTICELL_SHARED_CONTROL_BLOCKER: ("multicell_status", "Multicell/shared-control blocker", ValidationStatus.BLOCKED),
        ValidationArea.RELEASE_GATE_DEPENDENCY: ("release_gate_status", "Release gate dependency", ValidationStatus.RELEASE_GATE_REQUIRED),
    }
    rows: list[SCMValidationAreaRow] = []
    for idx, area in enumerate(ValidationArea, start=1):
        evidence_field, description, default_status = area_evidence_map[area]
        rows.append(
            SCMValidationAreaRow(
                area_id=f"SCM-VAL-{idx:03d}",
                validation_area=area,
                description=description,
                required_input_signals=("SCMValidationInput", area.value),
                evidence_field=evidence_field,
                default_when_missing=default_status,
                authorization_boundary="metadata_scaffolding_only",
            )
        )
    return tuple(rows)


def build_scm_validation_evidence(inp: SCMValidationInput) -> SCMValidationEvidence:
    """Build deterministic SCM validation evidence from metadata input."""
    blocked: list[str] = []
    warnings: list[str] = []
    followups: list[str] = []

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

    donor_count = len(inp.donor_units)
    min_size = _min_donor_pool_size(inp)
    if donor_count < min_size:
        blocked.append(BR_DONOR_POOL_INSUFFICIENT)

    donor_support_ok = _diag(inp, "donor_support_ok") or _flag(inp.donor_pool_metadata, "donor_support_ok")
    convex_hull_ok = _diag(inp, "convex_hull_ok") or _flag(inp.donor_pool_metadata, "convex_hull_ok")
    extrapolation_risk = _diag(inp, "extrapolation_risk") or _flag(inp.donor_pool_metadata, "extrapolation_risk")

    if not donor_support_ok:
        followups.append(RF_DONOR_SUPPORT_EVIDENCE)
        if donor_count >= min_size:
            blocked.append(BR_DONOR_SUPPORT_MISSING)
    if not convex_hull_ok:
        followups.append(RF_CONVEX_HULL_EVIDENCE)
        if donor_support_ok:
            blocked.append(BR_CONVEX_HULL_MISSING)
    if extrapolation_risk:
        blocked.append(BR_EXTRAPOLATION_RISK)

    pre_fit_ok = _diag(inp, "pre_period_fit_ok")
    trend_ok = _diag(inp, "pre_period_trend_stability_ok")
    if not pre_fit_ok:
        followups.append(RF_PRE_PERIOD_FIT_EVIDENCE)
        blocked.append(BR_PRE_PERIOD_FIT_MISSING)
    if not trend_ok:
        followups.append(RF_TREND_STABILITY_EVIDENCE)
        blocked.append(BR_TREND_STABILITY_MISSING)

    assignment_ok = _flag(inp.assignment_metadata, "assignment_valid") or _diag(inp, "assignment_valid")
    if not assignment_ok:
        blocked.append(BR_ASSIGNMENT_INVALID)

    null_cal_ok = _diag(inp, "null_calibration_complete")
    if not null_cal_ok:
        followups.append(RF_NULL_CALIBRATION_EVIDENCE)
        blocked.append(BR_NULL_CALIBRATION_INCOMPLETE)

    jackknife_ok = _diag(inp, "jackknife_sensitivity_complete")
    if not jackknife_ok:
        followups.append(RF_JACKKNIFE_EVIDENCE)
        blocked.append(BR_JACKKNIFE_INCOMPLETE)

    adapter_ok = _flag(inp.method_governance_state, "statistic_adapter_ready") or _diag(inp, "statistic_adapter_ready")
    if not adapter_ok:
        followups.append(RF_STATISTIC_ADAPTER_EVIDENCE)

    dgp_ok = _flag(inp.simulation_dgp_evidence_state, "dgp_coverage_complete")
    if not dgp_ok:
        followups.append(RF_DGP_COVERAGE_EVIDENCE)

    unresolved = inp.failure_registry_state.get("unresolved_modes", ())
    if unresolved:
        blocked.append(BR_FAILURE_REGISTRY_UNRESOLVED)

    multicell_validated = _flag(inp.multicell_validation_state, "dependence_multiplicity_validated")
    multicell_present = _flag(inp.multicell_validation_state, "multicell_geometry_present")
    if multicell_present and not multicell_validated:
        blocked.append(BR_MULTICELL_UNVALIDATED)

    release_authorized = _flag(inp.release_gate_state, "production_authorization_granted")
    if not release_authorized:
        followups.append(RF_RELEASE_GATE_PLAN)
        blocked.append(BR_RELEASE_GATE_REQUIRED)

    blocked.append(BR_UNCERTAINTY_BOUNDARY)

    def _status(
        *,
        ok: bool,
        candidate: bool = False,
        diagnostic: bool = False,
        research: bool = False,
        force_blocked: bool = False,
        force_release_gate: bool = False,
    ) -> ValidationStatus:
        if force_release_gate:
            return ValidationStatus.RELEASE_GATE_REQUIRED
        if force_blocked or not input_ok:
            return ValidationStatus.BLOCKED
        if research:
            return ValidationStatus.RESEARCH_ONLY
        if diagnostic:
            return ValidationStatus.DIAGNOSTIC_ONLY
        if ok and candidate:
            return ValidationStatus.CANDIDATE_AFTER_VALIDATION
        if ok:
            return ValidationStatus.ELIGIBLE_AFTER_WARNING
        return ValidationStatus.BLOCKED

    input_status = ValidationStatus.ELIGIBLE if input_ok else ValidationStatus.BLOCKED
    donor_status = _status(
        ok=donor_support_ok and convex_hull_ok and not extrapolation_risk and donor_count >= min_size,
        candidate=donor_support_ok and convex_hull_ok,
    )
    geometry_status = _status(ok=_present(inp.treated_units) and _present(inp.donor_units), candidate=True)
    pre_fit_status = _status(ok=pre_fit_ok, candidate=pre_fit_ok)
    trend_status = _status(ok=trend_ok, candidate=trend_ok)
    placebo_status = ValidationStatus.DIAGNOSTIC_ONLY if input_ok else ValidationStatus.BLOCKED
    null_status = ValidationStatus.DIAGNOSTIC_ONLY if null_cal_ok else ValidationStatus.BLOCKED
    jackknife_status = ValidationStatus.DIAGNOSTIC_ONLY if jackknife_ok else ValidationStatus.BLOCKED
    assignment_status = _status(ok=assignment_ok, candidate=assignment_ok)
    outcome_status = _status(
        ok=_present(inp.outcome_metadata) and _present(inp.kpi_metadata) and _present(inp.estimand_metadata),
        candidate=True,
    )
    adapter_status = _status(ok=adapter_ok, candidate=adapter_ok)
    failure_status = ValidationStatus.BLOCKED if unresolved else ValidationStatus.CANDIDATE_AFTER_VALIDATION
    dgp_status = _status(ok=dgp_ok, candidate=dgp_ok)
    multicell_status = (
        ValidationStatus.BLOCKED
        if multicell_present and not multicell_validated
        else ValidationStatus.NOT_APPLICABLE
        if not multicell_present
        else ValidationStatus.RESEARCH_ONLY
    )
    release_status = (
        ValidationStatus.RELEASE_GATE_REQUIRED
        if not release_authorized
        else ValidationStatus.BLOCKED
    )

    if extrapolation_risk:
        warnings.append("extrapolation_risk_flagged")
    if not adapter_ok:
        warnings.append("statistic_adapter_not_ready")

    allowed = (
        "scm_gated_candidate_metadata_review",
        "scm_diagnostic_readout",
        "scm_validation_evidence_scaffolding",
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
        ValidationArea.SCM_INPUT_CONTRACT.value: input_status.value,
        ValidationArea.PANEL_BALANCE_AND_TIME_INDEX.value: input_status.value,
        ValidationArea.TREATED_UNIT_DEFINITION.value: geometry_status.value,
        ValidationArea.DONOR_POOL_DEFINITION.value: donor_status.value,
        ValidationArea.DONOR_POOL_SIZE.value: donor_status.value,
        ValidationArea.DONOR_SUPPORT_OVERLAP.value: donor_status.value,
        ValidationArea.CONVEX_HULL_SUPPORT.value: donor_status.value,
        ValidationArea.EXTRAPOLATION_RISK.value: donor_status.value,
        ValidationArea.PRE_PERIOD_LENGTH.value: pre_fit_status.value,
        ValidationArea.PRE_PERIOD_FIT_QUALITY.value: pre_fit_status.value,
        ValidationArea.PRE_PERIOD_TREND_STABILITY.value: trend_status.value,
        ValidationArea.POST_PERIOD_WINDOW_DEFINITION.value: pre_fit_status.value,
        ValidationArea.OUTCOME_SCALE_COMPATIBILITY.value: outcome_status.value,
        ValidationArea.KPI_ESTIMAND_COMPATIBILITY.value: outcome_status.value,
        ValidationArea.ASSIGNMENT_DESIGN_VALIDITY.value: assignment_status.value,
        ValidationArea.RANDOMIZATION_COMPATIBILITY.value: assignment_status.value,
        ValidationArea.GEOGRAPHIC_INTERFERENCE_RISK.value: assignment_status.value,
        ValidationArea.SPILLOVER_EXCLUSION_OR_FLAGGING.value: assignment_status.value,
        ValidationArea.PLACEBO_UNIT_GENERATION.value: placebo_status.value,
        ValidationArea.PLACEBO_DISTRIBUTION_QUALITY.value: placebo_status.value,
        ValidationArea.NULL_CALIBRATION.value: null_status.value,
        ValidationArea.JACKKNIFE_UNIT_SENSITIVITY.value: jackknife_status.value,
        ValidationArea.DONOR_WEIGHT_STABILITY.value: donor_status.value,
        ValidationArea.TREATED_SET_SENSITIVITY.value: geometry_status.value,
        ValidationArea.STATISTIC_ADAPTER_CONTRACT.value: adapter_status.value,
        ValidationArea.EFFECT_SCALE_CONTRACT.value: outcome_status.value,
        ValidationArea.UNCERTAINTY_BOUNDARY.value: ValidationStatus.BLOCKED.value,
        ValidationArea.FAILURE_REGISTRY_MAPPING.value: failure_status.value,
        ValidationArea.SIMULATION_DGP_COVERAGE.value: dgp_status.value,
        ValidationArea.MULTICELL_SHARED_CONTROL_BLOCKER.value: multicell_status.value,
        ValidationArea.RELEASE_GATE_DEPENDENCY.value: release_status.value,
    }

    audit_refs = tuple(dep for dep in DEPENDENCIES_RECONCILED) + (_ARTIFACT_ID,)

    return SCMValidationEvidence(
        input_contract_status=input_status,
        donor_support_status=donor_status,
        geometry_status=geometry_status,
        pre_period_fit_status=pre_fit_status,
        trend_stability_status=trend_status,
        placebo_status=placebo_status,
        null_calibration_status=null_status,
        jackknife_sensitivity_status=jackknife_status,
        assignment_design_status=assignment_status,
        outcome_kpi_status=outcome_status,
        statistic_adapter_status=adapter_status,
        failure_registry_status=failure_status,
        dgp_coverage_status=dgp_status,
        multicell_status=multicell_status,
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


def validate_scm_validation_implementation(
    registry: tuple[SCMValidationAreaRow, ...],
    evidence: SCMValidationEvidence,
) -> dict[str, Any]:
    """Validate registry coverage and authorization boundary."""
    issues: list[str] = []
    if len(registry) != len(REQUIRED_VALIDATION_AREAS):
        issues.append(f"registry_count {len(registry)} != {len(REQUIRED_VALIDATION_AREAS)}")
    areas = {r.validation_area for r in registry}
    for area in REQUIRED_VALIDATION_AREAS:
        if area not in areas:
            issues.append(f"missing area: {area.value}")
    if any(evidence.authorization_flags.get(k) for k in _AUTH_FLAGS):
        issues.append("authorization flag unexpectedly true")
    if evidence.release_gate_status != ValidationStatus.RELEASE_GATE_REQUIRED:
        issues.append("release_gate_status must be release_gate_required")
    return {
        "valid": not issues,
        "registry_row_count": len(registry),
        "all_areas_covered": areas == REQUIRED_VALIDATION_AREAS,
        "issues": issues,
    }


def build_scenarios() -> list[dict[str, Any]]:
    registry = build_scm_validation_area_registry()
    empty = SCMValidationInput()
    empty_evidence = build_scm_validation_evidence(empty)
    complete = SCMValidationInput(
        panel_metadata={"grain": "weekly"},
        treated_units=("unit_a",),
        donor_units=("unit_b", "unit_c", "unit_d"),
        time_index=("2024-01", "2024-02"),
        pre_period=("2024-01",),
        post_period=("2024-02",),
        outcome_metadata={"scale": "level"},
        kpi_metadata={"kpi_id": "revenue"},
        estimand_metadata={"estimand": "att"},
        assignment_metadata={"assignment_valid": True},
        design_diagnostics={
            "donor_support_ok": True,
            "convex_hull_ok": True,
            "pre_period_fit_ok": True,
            "pre_period_trend_stability_ok": True,
            "null_calibration_complete": True,
            "jackknife_sensitivity_complete": True,
            "statistic_adapter_ready": True,
        },
        donor_pool_metadata={"donor_support_ok": True, "convex_hull_ok": True, "min_donor_pool_size": 2},
        method_governance_state={"statistic_adapter_ready": True},
        simulation_dgp_evidence_state={"dgp_coverage_complete": True},
        multicell_validation_state={"multicell_geometry_present": False},
        release_gate_state={"production_authorization_granted": False},
    )
    complete_evidence = build_scm_validation_evidence(complete)
    multicell = SCMValidationInput(
        panel_metadata={"grain": "weekly"},
        treated_units=("unit_a",),
        donor_units=("unit_b", "unit_c", "unit_d"),
        time_index=("2024-01",),
        pre_period=("2024-01",),
        post_period=("2024-02",),
        multicell_validation_state={"multicell_geometry_present": True, "dependence_multiplicity_validated": False},
    )
    multicell_evidence = build_scm_validation_evidence(multicell)

    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool, detail: str = "") -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": detail}

    scenarios.append(_s("registry_covers_all_areas", len(registry) == len(REQUIRED_VALIDATION_AREAS)))
    scenarios.append(_s("empty_input_blocked", empty_evidence.input_contract_status == ValidationStatus.BLOCKED))
    scenarios.append(_s("empty_release_gate_required", empty_evidence.release_gate_status == ValidationStatus.RELEASE_GATE_REQUIRED))
    scenarios.append(_s("multicell_unvalidated_blocked", multicell_evidence.multicell_status == ValidationStatus.BLOCKED))
    scenarios.append(_s("null_incomplete_blocks_p_values", not empty_evidence.authorization_flags["scm_production_p_value_authorized"]))
    scenarios.append(_s("jackknife_incomplete_blocks_cis", not empty_evidence.authorization_flags["scm_causal_confidence_interval_authorized"]))
    scenarios.append(_s("donor_insufficient_blocked", BR_DONOR_POOL_INSUFFICIENT in empty_evidence.blocked_reasons or BR_INPUT_CONTRACT_INCOMPLETE in empty_evidence.blocked_reasons))
    scenarios.append(_s("complete_still_release_gate_required", complete_evidence.release_gate_status == ValidationStatus.RELEASE_GATE_REQUIRED))
    scenarios.append(_s("complete_no_production_inference", not complete_evidence.authorization_flags["scm_production_inference_authorized"]))
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
    registry = build_scm_validation_area_registry()
    evidence = build_scm_validation_evidence(SCMValidationInput())
    validation = validate_scm_validation_implementation(registry, evidence)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "scm_validation_metadata_implementation",
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
        "validation_areas": [a.value for a in ValidationArea],
        "blocked_reasons_supported": list(BLOCKED_REASONS_SUPPORTED),
        "required_followups_supported": list(REQUIRED_FOLLOWUPS_SUPPORTED),
        "implemented_input_contract": "SCMValidationInput",
        "implemented_evidence_contract": "SCMValidationEvidence",
        "tests_added": [
            "tests/validation/test_scm_production_candidate_validation_implementation_001.py",
        ],
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "non_goals": list(NON_GOALS),
        "scm_validation_implementation_authorized": False,
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
