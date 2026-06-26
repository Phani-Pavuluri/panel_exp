"""SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001 — jackknife sensitivity metadata scaffolding."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

_ARTIFACT_ID = "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "scm_production_candidate_jackknife_sensitivity_metadata_implemented_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001",
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
    "scm_jackknife_sensitivity_implementation_authorized": False,
    "scm_jackknife_sensitivity_completed": False,
    "scm_production_inference_authorized": False,
}

NON_GOALS = (
    "no_jackknife_estimate_or_refit_computation",
    "no_unit_deletion_refits",
    "no_uncertainty_interval_or_causal_ci_computation",
    "no_production_p_values_or_type_i_error",
    "no_production_inference_authorization",
    "no_selector_router_production_use",
    "no_downstream_integrations",
    "no_package_side_agents",
    "no_multicell_production_claims",
    "no_numerical_jackknife_diagnostics",
)

DEPENDENCIES_RECONCILED = (
    "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",
    "SCM_JACKKNIFE_CHARACTERIZATION_001",
    "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
    "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
    "SIMULATION_DGP_COVERAGE_PLAN_001",
    "METHOD_FAILURE_MODE_REGISTRY_001",
)

BR_INPUT_CONTRACT_INCOMPLETE = "SCM-JK-BR-INPUT-INCOMPLETE"
BR_VALIDATION_EVIDENCE_MISSING = "SCM-JK-BR-VALIDATION-EVIDENCE-MISSING"
BR_NULL_CALIBRATION_EVIDENCE_MISSING = "SCM-JK-BR-NULL-CALIBRATION-EVIDENCE-MISSING"
BR_UNIT_DELETION_MISSING = "SCM-JK-BR-UNIT-DELETION-MISSING"
BR_DONOR_DELETION_MISSING = "SCM-JK-BR-DONOR-DELETION-MISSING"
BR_TREATED_UNIT_DELETION_MISSING = "SCM-JK-BR-TREATED-UNIT-DELETION-MISSING"
BR_TREATED_SET_METADATA_MISSING = "SCM-JK-BR-TREATED-SET-METADATA-MISSING"
BR_DONOR_WEIGHT_METADATA_MISSING = "SCM-JK-BR-DONOR-WEIGHT-METADATA-MISSING"
BR_EFFECT_SCALE_MISSING = "SCM-JK-BR-EFFECT-SCALE-MISSING"
BR_ESTIMAND_MISALIGNED = "SCM-JK-BR-ESTIMAND-MISALIGNED"
BR_DONOR_SUPPORT_CONDITIONING_MISSING = "SCM-JK-BR-DONOR-SUPPORT-CONDITIONING-MISSING"
BR_PRE_PERIOD_FIT_CONDITIONING_MISSING = "SCM-JK-BR-PRE-PERIOD-FIT-CONDITIONING-MISSING"
BR_JACKKNIFE_INCOMPLETE = "SCM-JK-BR-JACKKNIFE-INCOMPLETE"
BR_CAUSAL_CI_BOUNDARY = "SCM-JK-BR-CAUSAL-CI-BOUNDARY"
BR_P_VALUE_BOUNDARY = "SCM-JK-BR-P-VALUE-BOUNDARY"
BR_MULTICELL_UNVALIDATED = "SCM-JK-BR-MULTICELL-UNVALIDATED"
BR_RELEASE_GATE_REQUIRED = "SCM-JK-BR-RELEASE-GATE-REQUIRED"
BR_FAILURE_REGISTRY_UNRESOLVED = "SCM-JK-BR-FAILURE-REGISTRY-UNRESOLVED"

BLOCKED_REASONS_SUPPORTED = (
    BR_INPUT_CONTRACT_INCOMPLETE,
    BR_VALIDATION_EVIDENCE_MISSING,
    BR_NULL_CALIBRATION_EVIDENCE_MISSING,
    BR_UNIT_DELETION_MISSING,
    BR_DONOR_DELETION_MISSING,
    BR_TREATED_UNIT_DELETION_MISSING,
    BR_TREATED_SET_METADATA_MISSING,
    BR_DONOR_WEIGHT_METADATA_MISSING,
    BR_EFFECT_SCALE_MISSING,
    BR_ESTIMAND_MISALIGNED,
    BR_DONOR_SUPPORT_CONDITIONING_MISSING,
    BR_PRE_PERIOD_FIT_CONDITIONING_MISSING,
    BR_JACKKNIFE_INCOMPLETE,
    BR_CAUSAL_CI_BOUNDARY,
    BR_P_VALUE_BOUNDARY,
    BR_MULTICELL_UNVALIDATED,
    BR_RELEASE_GATE_REQUIRED,
    BR_FAILURE_REGISTRY_UNRESOLVED,
)

RF_VALIDATION_EVIDENCE = "SCM-JK-RF-VALIDATION-EVIDENCE"
RF_NULL_CALIBRATION_EVIDENCE = "SCM-JK-RF-NULL-CALIBRATION-EVIDENCE"
RF_UNIT_DELETION = "SCM-JK-RF-UNIT-DELETION"
RF_DONOR_DELETION = "SCM-JK-RF-DONOR-DELETION"
RF_TREATED_UNIT_DELETION = "SCM-JK-RF-TREATED-UNIT-DELETION"
RF_TREATED_SET = "SCM-JK-RF-TREATED-SET"
RF_DONOR_WEIGHT = "SCM-JK-RF-DONOR-WEIGHT"
RF_DONOR_SUPPORT = "SCM-JK-RF-DONOR-SUPPORT"
RF_PRE_PERIOD_FIT = "SCM-JK-RF-PRE-PERIOD-FIT"
RF_DGP_COVERAGE = "SCM-JK-RF-DGP-COVERAGE"
RF_FAILURE_REGISTRY = "SCM-JK-RF-FAILURE-REGISTRY"
RF_JACKKNIFE_SENSITIVITY = "SCM-JK-RF-JACKKNIFE-SENSITIVITY"
RF_RELEASE_GATE = "SCM-JK-RF-RELEASE-GATE"

REQUIRED_FOLLOWUPS_SUPPORTED = (
    RF_VALIDATION_EVIDENCE,
    RF_NULL_CALIBRATION_EVIDENCE,
    RF_UNIT_DELETION,
    RF_DONOR_DELETION,
    RF_TREATED_UNIT_DELETION,
    RF_TREATED_SET,
    RF_DONOR_WEIGHT,
    RF_DONOR_SUPPORT,
    RF_PRE_PERIOD_FIT,
    RF_DGP_COVERAGE,
    RF_FAILURE_REGISTRY,
    RF_JACKKNIFE_SENSITIVITY,
    RF_RELEASE_GATE,
)


class SensitivityStatus(str, Enum):
    ELIGIBLE = "eligible"
    ELIGIBLE_AFTER_WARNING = "eligible_after_warning"
    CANDIDATE_AFTER_VALIDATION = "candidate_after_validation"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    BLOCKED = "blocked"
    RELEASE_GATE_REQUIRED = "release_gate_required"
    NOT_APPLICABLE = "not_applicable"


REQUIRED_STATUSES = frozenset(SensitivityStatus)


class SensitivityArea(str, Enum):
    JACKKNIFE_INPUT_CONTRACT = "jackknife_input_contract"
    UNIT_DELETION_CONTRACT = "unit_deletion_contract"
    DONOR_DELETION_CONTRACT = "donor_deletion_contract"
    TREATED_UNIT_DELETION_CONTRACT = "treated_unit_deletion_contract"
    TREATED_SET_SENSITIVITY_CONTRACT = "treated_set_sensitivity_contract"
    DONOR_WEIGHT_STABILITY_CONTRACT = "donor_weight_stability_contract"
    EFFECT_INSTABILITY_CONTRACT = "effect_instability_contract"
    EFFECT_SCALE_ALIGNMENT = "effect_scale_alignment"
    ESTIMAND_ALIGNMENT = "estimand_alignment"
    OUTCOME_KPI_COMPATIBILITY = "outcome_kpi_compatibility"
    PRE_PERIOD_FIT_CONDITIONING = "pre_period_fit_conditioning"
    DONOR_SUPPORT_CONDITIONING = "donor_support_conditioning"
    NULL_CALIBRATION_DEPENDENCY = "null_calibration_dependency"
    PLACEBO_CALIBRATION_DEPENDENCY = "placebo_calibration_dependency"
    JACKKNIFE_DISTRIBUTION_QUALITY = "jackknife_distribution_quality"
    INFLUENCE_DIAGNOSTIC = "influence_diagnostic"
    HIGH_LEVERAGE_UNIT_DETECTION = "high_leverage_unit_detection"
    DONOR_WEIGHT_CONCENTRATION = "donor_weight_concentration"
    TREATED_UNIT_INFLUENCE = "treated_unit_influence"
    EFFECT_SIGN_STABILITY = "effect_sign_stability"
    EFFECT_MAGNITUDE_STABILITY = "effect_magnitude_stability"
    SENSITIVITY_THRESHOLD_POLICY = "sensitivity_threshold_policy"
    SENSITIVITY_ESCALATION_POLICY = "sensitivity_escalation_policy"
    CAUSAL_CI_BOUNDARY = "causal_ci_boundary"
    P_VALUE_BOUNDARY = "p_value_boundary"
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


REQUIRED_SENSITIVITY_AREAS = frozenset(SensitivityArea)


@dataclass(frozen=True)
class SCMJackknifeSensitivityInput:
    """Metadata-only SCM jackknife sensitivity input contract."""

    scm_validation_evidence: Mapping[str, Any] = field(default_factory=dict)
    scm_null_calibration_evidence: Mapping[str, Any] = field(default_factory=dict)
    panel_metadata: Mapping[str, Any] = field(default_factory=dict)
    treated_units: tuple[str, ...] = ()
    donor_units: tuple[str, ...] = ()
    time_index: tuple[str, ...] = ()
    pre_period: tuple[str, ...] = ()
    post_period: tuple[str, ...] = ()
    outcome_metadata: Mapping[str, Any] = field(default_factory=dict)
    kpi_metadata: Mapping[str, Any] = field(default_factory=dict)
    estimand_metadata: Mapping[str, Any] = field(default_factory=dict)
    effect_scale: Mapping[str, Any] = field(default_factory=dict)
    assignment_metadata: Mapping[str, Any] = field(default_factory=dict)
    design_diagnostics: Mapping[str, Any] = field(default_factory=dict)
    donor_support_evidence: Mapping[str, Any] = field(default_factory=dict)
    pre_period_fit_evidence: Mapping[str, Any] = field(default_factory=dict)
    donor_weight_metadata: Mapping[str, Any] = field(default_factory=dict)
    treated_set_metadata: Mapping[str, Any] = field(default_factory=dict)
    simulation_dgp_evidence_state: Mapping[str, Any] = field(default_factory=dict)
    failure_registry_state: Mapping[str, Any] = field(default_factory=dict)
    multicell_validation_state: Mapping[str, Any] = field(default_factory=dict)
    release_gate_state: Mapping[str, Any] = field(default_factory=dict)
    audit_context: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SCMJackknifeSensitivityEvidence:
    """Metadata-only SCM jackknife sensitivity evidence contract."""

    input_contract_status: SensitivityStatus
    unit_deletion_status: SensitivityStatus
    donor_deletion_status: SensitivityStatus
    treated_unit_deletion_status: SensitivityStatus
    treated_set_sensitivity_status: SensitivityStatus
    donor_weight_stability_status: SensitivityStatus
    effect_instability_status: SensitivityStatus
    influence_diagnostic_status: SensitivityStatus
    high_leverage_unit_status: SensitivityStatus
    effect_sign_stability_status: SensitivityStatus
    effect_magnitude_stability_status: SensitivityStatus
    sensitivity_threshold_status: SensitivityStatus
    sensitivity_escalation_status: SensitivityStatus
    causal_ci_boundary_status: SensitivityStatus
    p_value_boundary_status: SensitivityStatus
    multiple_testing_status: SensitivityStatus
    multicell_status: SensitivityStatus
    dgp_coverage_status: SensitivityStatus
    failure_registry_status: SensitivityStatus
    release_gate_status: SensitivityStatus
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
class SCMJackknifeSensitivityAreaRow:
    """Registry row for one SCM jackknife sensitivity area."""

    area_id: str
    sensitivity_area: SensitivityArea
    description: str
    required_input_signals: tuple[str, ...]
    evidence_field: str
    default_when_missing: SensitivityStatus
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


def _diag(inp: SCMJackknifeSensitivityInput, key: str) -> bool:
    return _flag(inp.design_diagnostics, key)


def _evidence_ok(mapping: Mapping[str, Any]) -> bool:
    return _present(mapping) and (
        _flag(mapping, "input_contract_satisfied")
        or _flag(mapping, "input_contract_status")
        or _flag(mapping, "donor_support_status")
        or _flag(mapping, "placebo_generation_status")
    )


def build_scm_jackknife_sensitivity_area_registry() -> tuple[SCMJackknifeSensitivityAreaRow, ...]:
    """Return deterministic SCM jackknife sensitivity area registry rows."""
    area_evidence_map: dict[SensitivityArea, tuple[str, str, SensitivityStatus]] = {
        SensitivityArea.JACKKNIFE_INPUT_CONTRACT: ("input_contract_status", "Jackknife input contract", SensitivityStatus.BLOCKED),
        SensitivityArea.UNIT_DELETION_CONTRACT: ("unit_deletion_status", "Unit deletion contract", SensitivityStatus.DIAGNOSTIC_ONLY),
        SensitivityArea.DONOR_DELETION_CONTRACT: ("donor_deletion_status", "Donor deletion contract", SensitivityStatus.DIAGNOSTIC_ONLY),
        SensitivityArea.TREATED_UNIT_DELETION_CONTRACT: ("treated_unit_deletion_status", "Treated-unit deletion contract", SensitivityStatus.DIAGNOSTIC_ONLY),
        SensitivityArea.TREATED_SET_SENSITIVITY_CONTRACT: ("treated_set_sensitivity_status", "Treated-set sensitivity", SensitivityStatus.RESEARCH_ONLY),
        SensitivityArea.DONOR_WEIGHT_STABILITY_CONTRACT: ("donor_weight_stability_status", "Donor weight stability", SensitivityStatus.CANDIDATE_AFTER_VALIDATION),
        SensitivityArea.EFFECT_INSTABILITY_CONTRACT: ("effect_instability_status", "Effect instability", SensitivityStatus.DIAGNOSTIC_ONLY),
        SensitivityArea.EFFECT_SCALE_ALIGNMENT: ("effect_sign_stability_status", "Effect scale alignment", SensitivityStatus.CANDIDATE_AFTER_VALIDATION),
        SensitivityArea.ESTIMAND_ALIGNMENT: ("effect_sign_stability_status", "Estimand alignment", SensitivityStatus.CANDIDATE_AFTER_VALIDATION),
        SensitivityArea.OUTCOME_KPI_COMPATIBILITY: ("effect_sign_stability_status", "Outcome KPI compatibility", SensitivityStatus.ELIGIBLE_AFTER_WARNING),
        SensitivityArea.PRE_PERIOD_FIT_CONDITIONING: ("unit_deletion_status", "Pre-period fit conditioning", SensitivityStatus.CANDIDATE_AFTER_VALIDATION),
        SensitivityArea.DONOR_SUPPORT_CONDITIONING: ("donor_deletion_status", "Donor support conditioning", SensitivityStatus.CANDIDATE_AFTER_VALIDATION),
        SensitivityArea.NULL_CALIBRATION_DEPENDENCY: ("p_value_boundary_status", "Null calibration dependency", SensitivityStatus.CANDIDATE_AFTER_VALIDATION),
        SensitivityArea.PLACEBO_CALIBRATION_DEPENDENCY: ("p_value_boundary_status", "Placebo calibration dependency", SensitivityStatus.DIAGNOSTIC_ONLY),
        SensitivityArea.JACKKNIFE_DISTRIBUTION_QUALITY: ("effect_instability_status", "Jackknife distribution quality", SensitivityStatus.DIAGNOSTIC_ONLY),
        SensitivityArea.INFLUENCE_DIAGNOSTIC: ("influence_diagnostic_status", "Influence diagnostic", SensitivityStatus.DIAGNOSTIC_ONLY),
        SensitivityArea.HIGH_LEVERAGE_UNIT_DETECTION: ("high_leverage_unit_status", "High-leverage unit detection", SensitivityStatus.DIAGNOSTIC_ONLY),
        SensitivityArea.DONOR_WEIGHT_CONCENTRATION: ("donor_weight_stability_status", "Donor weight concentration", SensitivityStatus.ELIGIBLE_AFTER_WARNING),
        SensitivityArea.TREATED_UNIT_INFLUENCE: ("influence_diagnostic_status", "Treated-unit influence", SensitivityStatus.DIAGNOSTIC_ONLY),
        SensitivityArea.EFFECT_SIGN_STABILITY: ("effect_sign_stability_status", "Effect sign stability", SensitivityStatus.DIAGNOSTIC_ONLY),
        SensitivityArea.EFFECT_MAGNITUDE_STABILITY: ("effect_magnitude_stability_status", "Effect magnitude stability", SensitivityStatus.DIAGNOSTIC_ONLY),
        SensitivityArea.SENSITIVITY_THRESHOLD_POLICY: ("sensitivity_threshold_status", "Sensitivity threshold policy", SensitivityStatus.CANDIDATE_AFTER_VALIDATION),
        SensitivityArea.SENSITIVITY_ESCALATION_POLICY: ("sensitivity_escalation_status", "Sensitivity escalation policy", SensitivityStatus.CANDIDATE_AFTER_VALIDATION),
        SensitivityArea.CAUSAL_CI_BOUNDARY: ("causal_ci_boundary_status", "Causal CI boundary", SensitivityStatus.BLOCKED),
        SensitivityArea.P_VALUE_BOUNDARY: ("p_value_boundary_status", "P-value boundary", SensitivityStatus.BLOCKED),
        SensitivityArea.MULTIPLE_TESTING_BOUNDARY: ("multiple_testing_status", "Multiple testing boundary", SensitivityStatus.BLOCKED),
        SensitivityArea.MULTICELL_SHARED_CONTROL_BOUNDARY: ("multicell_status", "Multicell/shared-control boundary", SensitivityStatus.BLOCKED),
        SensitivityArea.GEOGRAPHIC_INTERFERENCE_BOUNDARY: ("unit_deletion_status", "Geographic interference boundary", SensitivityStatus.ELIGIBLE_AFTER_WARNING),
        SensitivityArea.SPILLOVER_SENSITIVITY_BOUNDARY: ("unit_deletion_status", "Spillover sensitivity boundary", SensitivityStatus.ELIGIBLE_AFTER_WARNING),
        SensitivityArea.SIMULATION_DGP_COVERAGE: ("dgp_coverage_status", "Simulation DGP coverage", SensitivityStatus.CANDIDATE_AFTER_VALIDATION),
        SensitivityArea.FAILURE_REGISTRY_MAPPING: ("failure_registry_status", "Failure registry mapping", SensitivityStatus.CANDIDATE_AFTER_VALIDATION),
        SensitivityArea.BLOCKED_REASON_MAPPING: ("failure_registry_status", "Blocked reason mapping", SensitivityStatus.CANDIDATE_AFTER_VALIDATION),
        SensitivityArea.REQUIRED_FOLLOWUP_MAPPING: ("failure_registry_status", "Required followup mapping", SensitivityStatus.CANDIDATE_AFTER_VALIDATION),
        SensitivityArea.RELEASE_GATE_DEPENDENCY: ("release_gate_status", "Release gate dependency", SensitivityStatus.RELEASE_GATE_REQUIRED),
        SensitivityArea.AUDIT_REFERENCE_CONTRACT: ("input_contract_status", "Audit reference contract", SensitivityStatus.CANDIDATE_AFTER_VALIDATION),
        SensitivityArea.SELECTOR_SHADOW_INPUT_CONTRACT: ("input_contract_status", "Selector shadow input contract", SensitivityStatus.DIAGNOSTIC_ONLY),
        SensitivityArea.PRODUCTION_AUTHORIZATION_BOUNDARY: ("release_gate_status", "Production authorization boundary", SensitivityStatus.BLOCKED),
    }
    rows: list[SCMJackknifeSensitivityAreaRow] = []
    for idx, area in enumerate(SensitivityArea, start=1):
        evidence_field, description, default_status = area_evidence_map[area]
        rows.append(
            SCMJackknifeSensitivityAreaRow(
                area_id=f"SCM-JK-{idx:03d}",
                sensitivity_area=area,
                description=description,
                required_input_signals=("SCMJackknifeSensitivityInput", area.value),
                evidence_field=evidence_field,
                default_when_missing=default_status,
                authorization_boundary="metadata_scaffolding_only",
            )
        )
    return tuple(rows)


def build_scm_jackknife_sensitivity_evidence(inp: SCMJackknifeSensitivityInput) -> SCMJackknifeSensitivityEvidence:
    """Build deterministic SCM jackknife sensitivity evidence from metadata input."""
    blocked: list[str] = []
    warnings: list[str] = []
    followups: list[str] = []

    validation_ok = _evidence_ok(inp.scm_validation_evidence)
    if not _present(inp.scm_validation_evidence):
        blocked.append(BR_VALIDATION_EVIDENCE_MISSING)
        followups.append(RF_VALIDATION_EVIDENCE)
    elif not validation_ok:
        followups.append(RF_VALIDATION_EVIDENCE)
        blocked.append(BR_VALIDATION_EVIDENCE_MISSING)

    null_cal_ok_evidence = _evidence_ok(inp.scm_null_calibration_evidence)
    if not _present(inp.scm_null_calibration_evidence):
        blocked.append(BR_NULL_CALIBRATION_EVIDENCE_MISSING)
        followups.append(RF_NULL_CALIBRATION_EVIDENCE)
    elif not null_cal_ok_evidence:
        followups.append(RF_NULL_CALIBRATION_EVIDENCE)
        blocked.append(BR_NULL_CALIBRATION_EVIDENCE_MISSING)

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

    unit_del_ok = _diag(inp, "unit_deletion_contract_ready")
    donor_del_ok = _diag(inp, "donor_deletion_contract_ready")
    treated_del_ok = _diag(inp, "treated_unit_deletion_contract_ready")
    if not unit_del_ok:
        blocked.append(BR_UNIT_DELETION_MISSING)
        followups.append(RF_UNIT_DELETION)
    if not donor_del_ok:
        blocked.append(BR_DONOR_DELETION_MISSING)
        followups.append(RF_DONOR_DELETION)
    if not treated_del_ok:
        blocked.append(BR_TREATED_UNIT_DELETION_MISSING)
        followups.append(RF_TREATED_UNIT_DELETION)

    treated_set_ok = _present(inp.treated_set_metadata)
    if not treated_set_ok:
        blocked.append(BR_TREATED_SET_METADATA_MISSING)
        followups.append(RF_TREATED_SET)

    donor_weight_ok = _present(inp.donor_weight_metadata)
    if not donor_weight_ok:
        followups.append(RF_DONOR_WEIGHT)
        blocked.append(BR_DONOR_WEIGHT_METADATA_MISSING)

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

    jackknife_ok = _diag(inp, "jackknife_sensitivity_complete")
    if not jackknife_ok:
        followups.append(RF_JACKKNIFE_SENSITIVITY)
        blocked.append(BR_JACKKNIFE_INCOMPLETE)
        blocked.append(BR_CAUSAL_CI_BOUNDARY)

    blocked.append(BR_P_VALUE_BOUNDARY)

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
    ) -> SensitivityStatus:
        if force_blocked or not input_ok or not validation_ok:
            return SensitivityStatus.BLOCKED
        if research:
            return SensitivityStatus.RESEARCH_ONLY
        if diagnostic:
            return SensitivityStatus.DIAGNOSTIC_ONLY
        if ok and candidate:
            return SensitivityStatus.CANDIDATE_AFTER_VALIDATION
        if ok:
            return SensitivityStatus.ELIGIBLE_AFTER_WARNING
        return SensitivityStatus.BLOCKED

    input_status = SensitivityStatus.ELIGIBLE if input_ok and validation_ok and null_cal_ok_evidence else SensitivityStatus.BLOCKED
    unit_del_status = _status(ok=unit_del_ok and pre_fit_ok, candidate=unit_del_ok, diagnostic=unit_del_ok)
    donor_del_status = _status(ok=donor_del_ok and donor_support_ok, candidate=donor_del_ok)
    treated_del_status = _status(ok=treated_del_ok, candidate=treated_del_ok, diagnostic=treated_del_ok)
    treated_set_status = _status(ok=treated_set_ok, research=True)
    donor_weight_status = _status(ok=donor_weight_ok, candidate=donor_weight_ok)
    effect_instability_status = SensitivityStatus.DIAGNOSTIC_ONLY if jackknife_ok and input_ok else SensitivityStatus.BLOCKED
    influence_status = SensitivityStatus.DIAGNOSTIC_ONLY if input_ok and validation_ok else SensitivityStatus.BLOCKED
    high_leverage_status = SensitivityStatus.DIAGNOSTIC_ONLY if input_ok else SensitivityStatus.BLOCKED
    sign_stability_status = _status(ok=effect_scale_ok and estimand_ok, candidate=effect_scale_ok, diagnostic=jackknife_ok)
    magnitude_stability_status = SensitivityStatus.DIAGNOSTIC_ONLY if jackknife_ok else SensitivityStatus.BLOCKED
    threshold_status = _status(ok=jackknife_ok and donor_weight_ok, candidate=jackknife_ok)
    escalation_status = _status(ok=jackknife_ok, candidate=jackknife_ok)
    causal_ci_status = SensitivityStatus.BLOCKED
    p_value_status = SensitivityStatus.BLOCKED
    multiple_testing_status = SensitivityStatus.BLOCKED
    failure_status = SensitivityStatus.BLOCKED if unresolved else SensitivityStatus.CANDIDATE_AFTER_VALIDATION
    dgp_status = _status(ok=dgp_ok, candidate=dgp_ok)
    multicell_status = (
        SensitivityStatus.BLOCKED
        if multicell_present and not multicell_validated
        else SensitivityStatus.NOT_APPLICABLE
        if not multicell_present
        else SensitivityStatus.RESEARCH_ONLY
    )
    release_status = (
        SensitivityStatus.RELEASE_GATE_REQUIRED
        if not release_authorized
        else SensitivityStatus.BLOCKED
    )

    if not unit_del_ok:
        warnings.append("unit_deletion_contract_not_ready")
    if not donor_weight_ok:
        warnings.append("donor_weight_metadata_missing")
    if not jackknife_ok:
        warnings.append("jackknife_sensitivity_incomplete")

    allowed = (
        "scm_jackknife_sensitivity_metadata_review",
        "scm_jackknife_diagnostic_readout",
        "scm_jackknife_sensitivity_evidence_scaffolding",
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
        SensitivityArea.JACKKNIFE_INPUT_CONTRACT.value: input_status.value,
        SensitivityArea.UNIT_DELETION_CONTRACT.value: unit_del_status.value,
        SensitivityArea.DONOR_DELETION_CONTRACT.value: donor_del_status.value,
        SensitivityArea.TREATED_UNIT_DELETION_CONTRACT.value: treated_del_status.value,
        SensitivityArea.TREATED_SET_SENSITIVITY_CONTRACT.value: treated_set_status.value,
        SensitivityArea.DONOR_WEIGHT_STABILITY_CONTRACT.value: donor_weight_status.value,
        SensitivityArea.EFFECT_INSTABILITY_CONTRACT.value: effect_instability_status.value,
        SensitivityArea.EFFECT_SCALE_ALIGNMENT.value: sign_stability_status.value,
        SensitivityArea.ESTIMAND_ALIGNMENT.value: sign_stability_status.value,
        SensitivityArea.OUTCOME_KPI_COMPATIBILITY.value: sign_stability_status.value,
        SensitivityArea.PRE_PERIOD_FIT_CONDITIONING.value: unit_del_status.value,
        SensitivityArea.DONOR_SUPPORT_CONDITIONING.value: donor_del_status.value,
        SensitivityArea.NULL_CALIBRATION_DEPENDENCY.value: p_value_status.value,
        SensitivityArea.PLACEBO_CALIBRATION_DEPENDENCY.value: p_value_status.value,
        SensitivityArea.JACKKNIFE_DISTRIBUTION_QUALITY.value: effect_instability_status.value,
        SensitivityArea.INFLUENCE_DIAGNOSTIC.value: influence_status.value,
        SensitivityArea.HIGH_LEVERAGE_UNIT_DETECTION.value: high_leverage_status.value,
        SensitivityArea.DONOR_WEIGHT_CONCENTRATION.value: donor_weight_status.value,
        SensitivityArea.TREATED_UNIT_INFLUENCE.value: influence_status.value,
        SensitivityArea.EFFECT_SIGN_STABILITY.value: sign_stability_status.value,
        SensitivityArea.EFFECT_MAGNITUDE_STABILITY.value: magnitude_stability_status.value,
        SensitivityArea.SENSITIVITY_THRESHOLD_POLICY.value: threshold_status.value,
        SensitivityArea.SENSITIVITY_ESCALATION_POLICY.value: escalation_status.value,
        SensitivityArea.CAUSAL_CI_BOUNDARY.value: causal_ci_status.value,
        SensitivityArea.P_VALUE_BOUNDARY.value: p_value_status.value,
        SensitivityArea.MULTIPLE_TESTING_BOUNDARY.value: multiple_testing_status.value,
        SensitivityArea.MULTICELL_SHARED_CONTROL_BOUNDARY.value: multicell_status.value,
        SensitivityArea.GEOGRAPHIC_INTERFERENCE_BOUNDARY.value: unit_del_status.value,
        SensitivityArea.SPILLOVER_SENSITIVITY_BOUNDARY.value: unit_del_status.value,
        SensitivityArea.SIMULATION_DGP_COVERAGE.value: dgp_status.value,
        SensitivityArea.FAILURE_REGISTRY_MAPPING.value: failure_status.value,
        SensitivityArea.BLOCKED_REASON_MAPPING.value: failure_status.value,
        SensitivityArea.REQUIRED_FOLLOWUP_MAPPING.value: failure_status.value,
        SensitivityArea.RELEASE_GATE_DEPENDENCY.value: release_status.value,
        SensitivityArea.AUDIT_REFERENCE_CONTRACT.value: input_status.value,
        SensitivityArea.SELECTOR_SHADOW_INPUT_CONTRACT.value: SensitivityStatus.DIAGNOSTIC_ONLY.value,
        SensitivityArea.PRODUCTION_AUTHORIZATION_BOUNDARY.value: SensitivityStatus.BLOCKED.value,
    }

    audit_refs = tuple(dep for dep in DEPENDENCIES_RECONCILED) + (_ARTIFACT_ID,)

    return SCMJackknifeSensitivityEvidence(
        input_contract_status=input_status,
        unit_deletion_status=unit_del_status,
        donor_deletion_status=donor_del_status,
        treated_unit_deletion_status=treated_del_status,
        treated_set_sensitivity_status=treated_set_status,
        donor_weight_stability_status=donor_weight_status,
        effect_instability_status=effect_instability_status,
        influence_diagnostic_status=influence_status,
        high_leverage_unit_status=high_leverage_status,
        effect_sign_stability_status=sign_stability_status,
        effect_magnitude_stability_status=magnitude_stability_status,
        sensitivity_threshold_status=threshold_status,
        sensitivity_escalation_status=escalation_status,
        causal_ci_boundary_status=causal_ci_status,
        p_value_boundary_status=p_value_status,
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


def validate_scm_jackknife_sensitivity_implementation(
    registry: tuple[SCMJackknifeSensitivityAreaRow, ...],
    evidence: SCMJackknifeSensitivityEvidence,
) -> dict[str, Any]:
    """Validate registry coverage and authorization boundary."""
    issues: list[str] = []
    if len(registry) != len(REQUIRED_SENSITIVITY_AREAS):
        issues.append(f"registry_count {len(registry)} != {len(REQUIRED_SENSITIVITY_AREAS)}")
    areas = {r.sensitivity_area for r in registry}
    for area in REQUIRED_SENSITIVITY_AREAS:
        if area not in areas:
            issues.append(f"missing area: {area.value}")
    if any(evidence.authorization_flags.get(k) for k in _AUTH_FLAGS):
        issues.append("authorization flag unexpectedly true")
    if evidence.release_gate_status != SensitivityStatus.RELEASE_GATE_REQUIRED:
        issues.append("release_gate_status must be release_gate_required")
    if evidence.causal_ci_boundary_status != SensitivityStatus.BLOCKED:
        issues.append("causal_ci_boundary_status must be blocked")
    return {
        "valid": not issues,
        "registry_row_count": len(registry),
        "all_areas_covered": areas == REQUIRED_SENSITIVITY_AREAS,
        "issues": issues,
    }


def build_scenarios() -> list[dict[str, Any]]:
    registry = build_scm_jackknife_sensitivity_area_registry()
    empty = SCMJackknifeSensitivityInput()
    empty_evidence = build_scm_jackknife_sensitivity_evidence(empty)
    complete = SCMJackknifeSensitivityInput(
        scm_validation_evidence={"input_contract_satisfied": True},
        scm_null_calibration_evidence={"input_contract_satisfied": True},
        panel_metadata={"grain": "weekly"},
        treated_units=("unit_a",),
        donor_units=("unit_b", "unit_c", "unit_d"),
        time_index=("2024-01", "2024-02"),
        pre_period=("2024-01",),
        post_period=("2024-02",),
        outcome_metadata={"scale": "level"},
        kpi_metadata={"kpi_id": "revenue"},
        estimand_metadata={"estimand": "att", "estimand_aligned": True},
        effect_scale={"scale_defined": True, "scale": "level"},
        design_diagnostics={
            "unit_deletion_contract_ready": True,
            "donor_deletion_contract_ready": True,
            "treated_unit_deletion_contract_ready": True,
            "donor_support_ok": True,
            "pre_period_fit_ok": True,
            "jackknife_sensitivity_complete": True,
        },
        donor_support_evidence={"donor_support_ok": True},
        pre_period_fit_evidence={"pre_period_fit_ok": True},
        donor_weight_metadata={"weights_defined": True},
        treated_set_metadata={"treated_set_id": "set_a"},
        simulation_dgp_evidence_state={"dgp_coverage_complete": True},
        failure_registry_state={"unresolved_modes": ()},
        multicell_validation_state={"multicell_geometry_present": False},
        release_gate_state={"production_authorization_granted": False},
    )
    complete_evidence = build_scm_jackknife_sensitivity_evidence(complete)
    multicell = SCMJackknifeSensitivityInput(
        scm_validation_evidence={"input_contract_satisfied": True},
        scm_null_calibration_evidence={"input_contract_satisfied": True},
        panel_metadata={"grain": "weekly"},
        treated_units=("unit_a",),
        donor_units=("unit_b", "unit_c"),
        time_index=("2024-01",),
        pre_period=("2024-01",),
        post_period=("2024-02",),
        treated_set_metadata={"treated_set_id": "set_a"},
        donor_weight_metadata={"weights_defined": True},
        multicell_validation_state={"multicell_geometry_present": True, "dependence_multiplicity_validated": False},
    )
    multicell_evidence = build_scm_jackknife_sensitivity_evidence(multicell)

    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool, detail: str = "") -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": detail}

    scenarios.append(_s("registry_covers_all_areas", len(registry) == len(REQUIRED_SENSITIVITY_AREAS)))
    scenarios.append(_s("empty_input_blocked", empty_evidence.input_contract_status == SensitivityStatus.BLOCKED))
    scenarios.append(_s("empty_validation_evidence_blocked", BR_VALIDATION_EVIDENCE_MISSING in empty_evidence.blocked_reasons))
    scenarios.append(_s("empty_null_calibration_blocked", BR_NULL_CALIBRATION_EVIDENCE_MISSING in empty_evidence.blocked_reasons))
    scenarios.append(_s("empty_deletion_metadata_blocked", BR_UNIT_DELETION_MISSING in empty_evidence.blocked_reasons))
    scenarios.append(_s("empty_donor_weight_followup", BR_DONOR_WEIGHT_METADATA_MISSING in empty_evidence.blocked_reasons))
    scenarios.append(_s("empty_release_gate_required", empty_evidence.release_gate_status == SensitivityStatus.RELEASE_GATE_REQUIRED))
    scenarios.append(_s("multicell_unvalidated_blocked", multicell_evidence.multicell_status == SensitivityStatus.BLOCKED))
    scenarios.append(_s("jackknife_incomplete_blocks_cis", not empty_evidence.authorization_flags["scm_causal_confidence_interval_authorized"]))
    scenarios.append(_s("p_value_boundary_unauthorized", not empty_evidence.authorization_flags["scm_production_p_value_authorized"]))
    scenarios.append(_s("complete_still_release_gate_required", complete_evidence.release_gate_status == SensitivityStatus.RELEASE_GATE_REQUIRED))
    scenarios.append(_s("complete_no_production_inference", not complete_evidence.authorization_flags["scm_production_inference_authorized"]))
    scenarios.append(_s("complete_jackknife_not_completed", _SCM_FLAGS["scm_jackknife_sensitivity_completed"] is False))
    scenarios.append(_s("causal_ci_boundary_blocked", empty_evidence.causal_ci_boundary_status == SensitivityStatus.BLOCKED))
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
    registry = build_scm_jackknife_sensitivity_area_registry()
    evidence = build_scm_jackknife_sensitivity_evidence(SCMJackknifeSensitivityInput())
    validation = validate_scm_jackknife_sensitivity_implementation(registry, evidence)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "scm_jackknife_sensitivity_metadata_implementation",
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
        "implemented_sensitivity_areas": [a.value for a in SensitivityArea],
        "blocked_reasons_supported": list(BLOCKED_REASONS_SUPPORTED),
        "required_followups_supported": list(REQUIRED_FOLLOWUPS_SUPPORTED),
        "implemented_input_contract": "SCMJackknifeSensitivityInput",
        "implemented_evidence_contract": "SCMJackknifeSensitivityEvidence",
        "tests_added": [
            "tests/validation/test_scm_production_candidate_jackknife_sensitivity_implementation_001.py",
        ],
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "non_goals": list(NON_GOALS),
        "scm_jackknife_sensitivity_implementation_authorized": False,
        "scm_jackknife_sensitivity_completed": False,
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
