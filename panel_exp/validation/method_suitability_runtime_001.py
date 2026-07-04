"""METHOD_SUITABILITY_RUNTIME_001 conservative method-family review suitability evaluation."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from panel_exp.validation.production_catalog_blocklist_001 import (
    evaluate_production_catalog_status,
    production_catalog_overlay_for_matrix,
)
from panel_exp.validation.statistical_promotion_thresholds_001 import (
    MATURITY_RESTRICTED_EXPERT_REVIEW,
    evaluate_statistical_promotion_thresholds,
    statistical_promotion_overlay_for_matrix,
)

_ARTIFACT_ID = "METHOD_SUITABILITY_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "method_suitability_runtime_implemented_review_classification_only_no_estimator_or_inference_authorization"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/METHOD_SUITABILITY_RUNTIME_001_summary.json"
RECOMMENDED_NEXT_ARTIFACT = "DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001"
ALTERNATIVE_NEXT_ARTIFACT = "READOUT_METHOD_GOVERNANCE_CONTRACT_001"

_BLOCKED_TOKENS = frozenset({"BLOCKED", "NOT_EVALUATED"})
_READY_TOKENS = frozenset({"PASS", "READY", "READY_FOR_DOWNSTREAM", "COMPLETE", "COMPLETED"})
_SUPPORTED_DESIGN_TYPES = frozenset({
    "SINGLE_TREATMENT_CONTROL", "MULTI_CELL_COMMON_CONTROL", "MULTI_CELL_SPLIT_CONTROL",
    "MATCHED_PAIR", "RERANDOMIZED_BLOCK", "THINNING_DESIGN", "QUICK_BLOCK",
    "DOSAGE_CONTRAST", "DIFFERENCE_IN_POLICY", "BUDGET_REALLOCATION", "GO_LIVE",
})
_DOSAGE_ESTIMANDS = frozenset({"DOSAGE_CONTRAST", "DOSAGE_LOW_VS_HIGH", "DOSAGE"})
_DIP_ESTIMANDS = frozenset({"DIFFERENCE_IN_POLICY", "DIFFERENCE_IN_POLICY_CONTRAST", "DIP"})
_BUDGET_ESTIMANDS = frozenset({"BUDGET_REALLOCATION", "SOURCE_DESTINATION_REALLOCATION"})
_GO_LIVE_ESTIMANDS = frozenset({"GO_LIVE", "GO_LIVE_VS_NO_OR_LOW_SPEND"})
_STANDARD_ESTIMANDS = frozenset({
    "GO_DARK_VS_BAU", "HEAVY_UP_VS_BAU", "STANDARD_INCREMENTALITY", "INCREMENTALITY",
})
_ALL_METHOD_FAMILIES = (
    "SCM_FAMILY", "AUGSYNTH_FAMILY", "TBR_RIDGE_FAMILY", "DID_FAMILY",
    "MATCHED_PAIR_FAMILY", "BLOCKED_RANDOMIZATION_FAMILY", "RERANDOMIZATION_FAMILY",
    "PLACEBO_INFERENCE_FAMILY", "JACKKNIFE_INFERENCE_FAMILY", "BOOTSTRAP_INFERENCE_FAMILY",
    "CONFORMAL_INFERENCE_FAMILY", "AB_TEST_FAMILY", "UNKNOWN_METHOD_FAMILY",
)
_DEFAULT_FALLBACK_INSTRUMENT_IDS = (
    "SCM_UNIT_JACKKNIFE",
    "SCM_PLACEBO",
    "TBR_RIDGE_BRB",
    "TBR_RIDGE_KFOLD",
    "TBR_RIDGE_PLACEBO",
    "DID_2X2_POINT_ESTIMATE",
    "DID_BOOTSTRAP",
    "AUGSYNTH_JACKKNIFE",
    "MATCHED_PAIR_RANDOMIZATION",
    "AB_STANDARD_INFERENCE",
)
_COMPAT_PASS = "PASS"
_COMPAT_BLOCKED = "BLOCKED"
_COMPAT_RESTRICTED = "RESTRICTED"
_COMPAT_NOT_EVALUATED = "NOT_EVALUATED"
_COMPAT_PROVISIONAL = "PROVISIONAL"


class MethodHandoffStatus(str, Enum):
    METHOD_HANDOFF_READY_FOR_SUITABILITY_REVIEW = "METHOD_HANDOFF_READY_FOR_SUITABILITY_REVIEW"
    METHOD_HANDOFF_READY_WITH_WARNINGS = "METHOD_HANDOFF_READY_WITH_WARNINGS"
    METHOD_HANDOFF_PROVISIONAL = "METHOD_HANDOFF_PROVISIONAL"
    METHOD_HANDOFF_BLOCKED_BY_DATA_READINESS = "METHOD_HANDOFF_BLOCKED_BY_DATA_READINESS"
    METHOD_HANDOFF_BLOCKED_BY_GEO_FEASIBILITY = "METHOD_HANDOFF_BLOCKED_BY_GEO_FEASIBILITY"
    METHOD_HANDOFF_BLOCKED_BY_DESIGN_STRUCTURE = "METHOD_HANDOFF_BLOCKED_BY_DESIGN_STRUCTURE"
    METHOD_HANDOFF_BLOCKED_BY_SCENARIO_POLICY = "METHOD_HANDOFF_BLOCKED_BY_SCENARIO_POLICY"
    METHOD_HANDOFF_BLOCKED_BY_ASSIGNMENT_FEASIBILITY = "METHOD_HANDOFF_BLOCKED_BY_ASSIGNMENT_FEASIBILITY"
    METHOD_HANDOFF_BLOCKED_BY_POWER_MDE_READINESS = "METHOD_HANDOFF_BLOCKED_BY_POWER_MDE_READINESS"
    METHOD_HANDOFF_BLOCKED_BY_MISSING_ESTIMAND = "METHOD_HANDOFF_BLOCKED_BY_MISSING_ESTIMAND"
    METHOD_HANDOFF_BLOCKED_BY_UNSUPPORTED_DESIGN = "METHOD_HANDOFF_BLOCKED_BY_UNSUPPORTED_DESIGN"
    METHOD_HANDOFF_REQUIRES_DOSAGE_REVIEW = "METHOD_HANDOFF_REQUIRES_DOSAGE_REVIEW"
    METHOD_HANDOFF_REQUIRES_DIFFERENCE_IN_POLICY_REVIEW = "METHOD_HANDOFF_REQUIRES_DIFFERENCE_IN_POLICY_REVIEW"
    METHOD_HANDOFF_REQUIRES_BUDGET_REALLOCATION_REVIEW = "METHOD_HANDOFF_REQUIRES_BUDGET_REALLOCATION_REVIEW"
    METHOD_HANDOFF_REQUIRES_REDESIGN_RECHECK = "METHOD_HANDOFF_REQUIRES_REDESIGN_RECHECK"
    METHOD_HANDOFF_NOT_EVALUATED = "METHOD_HANDOFF_NOT_EVALUATED"


class MethodFamilySuitabilityStatus(str, Enum):
    METHOD_FAMILY_ELIGIBLE_FOR_REVIEW = "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW"
    METHOD_FAMILY_ELIGIBLE_WITH_WARNINGS = "METHOD_FAMILY_ELIGIBLE_WITH_WARNINGS"
    METHOD_FAMILY_RESTRICTED = "METHOD_FAMILY_RESTRICTED"
    METHOD_FAMILY_DIAGNOSTIC_ONLY = "METHOD_FAMILY_DIAGNOSTIC_ONLY"
    METHOD_FAMILY_BLOCKED = "METHOD_FAMILY_BLOCKED"
    METHOD_FAMILY_NOT_EVALUATED = "METHOD_FAMILY_NOT_EVALUATED"


class ReviewRequirementType(str, Enum):
    STANDARD_INCREMENTALITY_REVIEW = "STANDARD_INCREMENTALITY_REVIEW"
    DOSAGE_CONTRAST_REVIEW = "DOSAGE_CONTRAST_REVIEW"
    DIFFERENCE_IN_POLICY_REVIEW = "DIFFERENCE_IN_POLICY_REVIEW"
    BUDGET_REALLOCATION_REVIEW = "BUDGET_REALLOCATION_REVIEW"
    GO_LIVE_REVIEW = "GO_LIVE_REVIEW"
    COMMON_CONTROL_REVIEW = "COMMON_CONTROL_REVIEW"
    SPLIT_CONTROL_REDESIGN_REVIEW = "SPLIT_CONTROL_REDESIGN_REVIEW"
    MATCHED_PAIR_REVIEW = "MATCHED_PAIR_REVIEW"
    BLOCKED_OR_CLUSTERED_DESIGN_REVIEW = "BLOCKED_OR_CLUSTERED_DESIGN_REVIEW"
    RERANDOMIZATION_REVIEW = "RERANDOMIZATION_REVIEW"
    INTERFERENCE_RISK_REVIEW = "INTERFERENCE_RISK_REVIEW"
    LOW_POWER_OR_HIGH_MDE_REVIEW = "LOW_POWER_OR_HIGH_MDE_REVIEW"
    OUT_OF_HISTORICAL_SUPPORT_REVIEW = "OUT_OF_HISTORICAL_SUPPORT_REVIEW"
    ASSIGNMENT_FEASIBILITY_REVIEW = "ASSIGNMENT_FEASIBILITY_REVIEW"
    METHOD_GOVERNANCE_REVIEW = "METHOD_GOVERNANCE_REVIEW"


class IssueSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"


@dataclass(frozen=True)
class MethodSuitabilityConfig:
    block_scenario_policy_blocked: bool = True
    block_assignment_feasibility_blocked: bool = True
    block_power_mde_blocked: bool = False
    missing_estimand_is_blocking: bool = True
    missing_governance_is_blocking: bool = False
    diagnostic_only_blocks_production: bool = True
    unknown_method_family_not_evaluated: bool = True
    enforce_production_catalog_blocklist: bool = True
    enforce_statistical_promotion_thresholds: bool = True


@dataclass(frozen=True)
class SuitabilityIssue:
    code: str
    message: str
    severity: IssueSeverity
    field: str | None = None


@dataclass(frozen=True)
class MethodSuitabilityReadinessReport:
    profiler_gate: str
    geo_feasibility_gate: str
    spend_feasibility_gate: str
    power_mde_readiness_gate: str
    design_cell_structure_gate: str
    scenario_policy_gate: str
    assignment_feasibility_gate: str
    estimand_declaration_gate: str
    governance_catalog_gate: str
    all_hard_gates_pass: bool


@dataclass(frozen=True)
class EstimandGateReport:
    estimand_labels_present: bool
    standard_incrementality_allowed: bool
    dosage_estimand_required: bool
    difference_in_policy_required: bool
    budget_reallocation_required: bool
    go_live_required: bool
    bau_control_preserved: bool
    manipulated_control_detected: bool
    status: str


@dataclass(frozen=True)
class ReviewRequirementReport:
    requirements: tuple[str, ...]
    preserved_upstream_flags: bool


@dataclass(frozen=True)
class MethodFamilySuitabilityEntry:
    method_family: str
    suitability_status: MethodFamilySuitabilityStatus
    review_requirements: tuple[str, ...]
    restrictions: tuple[str, ...]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    governance_stance: str | None


@dataclass(frozen=True)
class InstrumentSpec:
    instrument_id: str
    estimator_family: str
    inference_family: str
    instrument_family_label: str
    design_requirements: tuple[str, ...] = ()
    disallowed_designs: tuple[str, ...] = ()
    estimand_requirements: tuple[str, ...] = ()
    requires_bau_control: bool = False
    requires_assignment_feasible: bool = False
    requires_matched_pair_metadata: bool = False
    requires_block_randomization_metadata: bool = False
    requires_individual_randomized_ab: bool = False
    dosage_compatible: bool = False
    diagnostic_only: bool = False
    governance_status: str | None = None


@dataclass(frozen=True)
class InstrumentSuitabilityEntry:
    instrument_id: str
    estimator_family: str
    inference_family: str
    instrument_family_label: str
    design_compatibility_status: str
    estimand_compatibility_status: str
    assignment_compatibility_status: str
    power_mde_compatibility_status: str
    scenario_policy_compatibility_status: str
    governance_status: str
    suitability_status: MethodFamilySuitabilityStatus
    review_requirements: tuple[str, ...]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    diagnostic_only_reason: str | None
    restricted_reason: str | None


@dataclass(frozen=True)
class GovernanceHandoffReport:
    instrument_catalog_status: str | None
    method_roadmap_status: str | None
    governed_methods: tuple[str, ...]
    restricted_methods: tuple[str, ...]
    diagnostic_only_methods: tuple[str, ...]
    blocked_methods: tuple[str, ...]
    governance_complete: bool
    preserved_status: str | None


@dataclass(frozen=True)
class ScenarioPolicyHandoffReport:
    scenario_policy_status: str | None
    shared_control_conflict: bool
    spend_contrast_status: str | None
    historical_support_status: str | None
    preserved_status: str | None


@dataclass(frozen=True)
class AssignmentHandoffReport:
    assignment_feasibility_status: str | None
    redesign_recheck_required: bool
    preserved_status: str | None


@dataclass(frozen=True)
class PowerMdeHandoffReport:
    power_mde_status: str | None
    power_mde_blocked: bool
    inference_ready_claim_allowed: bool
    preserved_status: str | None


@dataclass(frozen=True)
class SpendHandoffReport:
    spend_feasibility_status: str | None
    historical_support_status: str | None
    out_of_support_warning: bool
    preserved_status: str | None


@dataclass(frozen=True)
class DesignCompatibilityReport:
    design_structure_type: str | None
    supported_design: bool
    contrast_count: int


@dataclass(frozen=True)
class MethodSuitabilityClaimBoundaryReport:
    runtime_method_suitability_implemented: bool = True
    method_family_review_classification_implemented: bool = True
    instrument_suitability_matrix_implemented: bool = True
    estimator_inference_instrument_classification_implemented: bool = True
    review_requirement_detection_implemented: bool = True
    governance_stance_preservation_implemented: bool = True
    estimand_gate_implemented: bool = True
    handoff_readiness_gate_implemented: bool = True
    method_family_only_classification: bool = False
    method_winner_selected: bool = False
    primary_readout_stack_selected: bool = False
    sensitivity_stack_selected: bool = False
    diagnostic_stack_selected: bool = False
    method_family_selected: bool = False
    estimator_selected: bool = False
    inference_method_selected: bool = False
    method_promotion_authorized: bool = False
    method_production_compatibility_authorized: bool = False
    geo_assignment_computed: bool = False
    matched_pairs_generated: bool = False
    blocks_generated: bool = False
    randomization_computed: bool = False
    rerandomization_computed: bool = False
    thinning_design_generated: bool = False
    matching_optimization_computed: bool = False
    balance_optimization_computed: bool = False
    scenario_policy_feasibility_computed: bool = False
    assignment_feasibility_computed: bool = False
    power_computed: bool = False
    mde_computed: bool = False
    p_value_computed: bool = False
    confidence_interval_computed: bool = False
    lift_computed: bool = False
    roi_computed: bool = False
    budget_optimization_authorized: bool = False
    candidate_design_authorized: bool = False
    treatment_control_assignment_authorized: bool = False
    estimator_inference_authorized: bool = False
    mmm_runtime_calls_implemented: bool = False
    mmm_calibration_authorized: bool = False
    production_authorization_granted: bool = False
    llm_decisioning_authorized: bool = False


@dataclass(frozen=True)
class MethodSuitabilityPacketReport:
    design_id: str
    handoff_status: MethodHandoffStatus
    secondary_statuses: tuple[MethodHandoffStatus, ...]
    overall_suitability_summary: str
    review_requirements: tuple[str, ...]
    method_family_suitability_reports: tuple[MethodFamilySuitabilityEntry, ...]
    readiness_report: MethodSuitabilityReadinessReport
    estimand_gate_report: EstimandGateReport
    design_compatibility_report: DesignCompatibilityReport
    scenario_policy_handoff_report: ScenarioPolicyHandoffReport
    assignment_handoff_report: AssignmentHandoffReport
    power_mde_handoff_report: PowerMdeHandoffReport
    spend_handoff_report: SpendHandoffReport
    governance_handoff_report: GovernanceHandoffReport
    claim_boundary_report: MethodSuitabilityClaimBoundaryReport
    issues: tuple[SuitabilityIssue, ...]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    instrument_suitability_reports: tuple[InstrumentSuitabilityEntry, ...] = ()
    instrument_suitability_matrix: tuple[dict[str, Any], ...] = ()
    candidate_instrument_count: int = 0
    eligible_instrument_count: int = 0
    restricted_instrument_count: int = 0
    diagnostic_only_instrument_count: int = 0
    blocked_instrument_count: int = 0
    not_evaluated_instrument_count: int = 0


@dataclass(frozen=True)
class MethodSuitabilityReport:
    artifact_id: str
    design_id: str | None
    handoff_status: MethodHandoffStatus | None
    secondary_statuses: tuple[MethodHandoffStatus, ...] = ()
    overall_suitability_summary: str | None = None
    review_requirements: tuple[str, ...] = ()
    design_reports: tuple[MethodSuitabilityPacketReport, ...] = ()
    aggregate_summary: str | None = None
    method_family_suitability_reports: tuple[MethodFamilySuitabilityEntry, ...] = ()
    instrument_suitability_reports: tuple[InstrumentSuitabilityEntry, ...] = ()
    instrument_suitability_matrix: tuple[dict[str, Any], ...] = ()
    candidate_instrument_count: int = 0
    eligible_instrument_count: int = 0
    restricted_instrument_count: int = 0
    diagnostic_only_instrument_count: int = 0
    blocked_instrument_count: int = 0
    not_evaluated_instrument_count: int = 0
    estimand_gate_report: EstimandGateReport | None = None
    design_compatibility_report: DesignCompatibilityReport | None = None
    scenario_policy_handoff_report: ScenarioPolicyHandoffReport | None = None
    assignment_handoff_report: AssignmentHandoffReport | None = None
    power_mde_handoff_report: PowerMdeHandoffReport | None = None
    spend_handoff_report: SpendHandoffReport | None = None
    governance_handoff_report: GovernanceHandoffReport | None = None
    claim_boundary_report: MethodSuitabilityClaimBoundaryReport = field(
        default_factory=MethodSuitabilityClaimBoundaryReport
    )
    issues: tuple[SuitabilityIssue, ...] = ()
    warnings: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()
    final_verdict: str = _VERDICT


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: getattr(obj, f.name) for f in fields(obj)}
    return {}


def _token(value: Any) -> str:
    return str(value).strip().upper() if value is not None else ""


def _is_blocked(value: Any) -> bool:
    t = _token(value)
    if not t:
        return False
    if t in _BLOCKED_TOKENS:
        return True
    if t.startswith("BLOCKED"):
        return True
    if t.endswith("_BLOCKED"):
        return True
    return "_BLOCKED_BY_" in t


def _is_ready(value: Any) -> bool:
    t = _token(value)
    return bool(t) and (t in _READY_TOKENS or "READY" in t or t == "PASS")


def _gate_status(value: Any) -> str:
    if _is_blocked(value):
        return "BLOCKED"
    if _is_ready(value):
        return "PASS"
    t = _token(value)
    if t in ("WARNING", "PROVISIONAL"):
        return t
    if not t:
        return "NOT_EVALUATED"
    return "PASS" if "READY" in t or "FEASIBLE" in t else t


def _normalize_packets(input_data: Any) -> list[dict[str, Any]]:
    if isinstance(input_data, list):
        if input_data and all(isinstance(x, dict) for x in input_data):
            if "design_id" in input_data[0] or "handoff_status" in input_data[0]:
                return [dict(x) for x in input_data]
    data = _to_dict(input_data)
    if "packets" in data and isinstance(data["packets"], list):
        return [dict(p) for p in data["packets"] if isinstance(p, dict)]
    if "design_id" in data or "handoff_status" in data:
        return [data]
    return [data] if data else [{"design_id": "design_unspecified"}]


def _contrast_summaries(packet: dict[str, Any]) -> list[dict[str, Any]]:
    raw = packet.get("contrast_summaries") or packet.get("contrasts") or []
    if isinstance(raw, list):
        return [dict(c) for c in raw if isinstance(c, dict)]
    return []


def _estimand_summaries(packet: dict[str, Any], contrasts: list[dict[str, Any]]) -> list[str]:
    raw = packet.get("estimand_summaries")
    labels: list[str] = []
    if isinstance(raw, list):
        labels.extend(str(e) for e in raw if e)
    for c in contrasts:
        el = c.get("estimand_label")
        if el:
            labels.append(str(el))
    return list(dict.fromkeys(labels))


def _governance(packet: dict[str, Any]) -> dict[str, Any]:
    gov = packet.get("governance_summary") or {}
    return dict(gov) if isinstance(gov, dict) else {}


def _upstream(packet: dict[str, Any]) -> dict[str, Any]:
    up = packet.get("upstream_statuses") or {}
    return dict(up) if isinstance(up, dict) else {}


def _scenario_summary(packet: dict[str, Any]) -> dict[str, Any]:
    s = packet.get("scenario_policy_summary") or {}
    return dict(s) if isinstance(s, dict) else {}


def _assignment_summary(packet: dict[str, Any]) -> dict[str, Any]:
    a = packet.get("assignment_feasibility_summary") or {}
    return dict(a) if isinstance(a, dict) else {}


def _power_summary(packet: dict[str, Any]) -> dict[str, Any]:
    p = packet.get("power_mde_summary") or {}
    return dict(p) if isinstance(p, dict) else {}


def _spend_summary(packet: dict[str, Any]) -> dict[str, Any]:
    s = packet.get("spend_summary") or {}
    return dict(s) if isinstance(s, dict) else {}


def _family_list(gov: dict[str, Any], key: str) -> frozenset[str]:
    val = gov.get(key)
    if isinstance(val, list):
        return frozenset(_token(x) for x in val)
    return frozenset()


def _default_instrument_catalog() -> dict[str, InstrumentSpec]:
    return {
        "SCM_UNIT_JACKKNIFE": InstrumentSpec(
            instrument_id="SCM_UNIT_JACKKNIFE",
            estimator_family="SCM_FAMILY",
            inference_family="JACKKNIFE_INFERENCE_FAMILY",
            instrument_family_label="SCM + UnitJackknife",
            design_requirements=("SINGLE_TREATMENT_CONTROL", "SINGLE_TREATED_OR_RESTRICTED"),
            disallowed_designs=("MULTI_CELL_COMMON_CONTROL",),
            estimand_requirements=("standard_incrementality",),
            requires_bau_control=True,
        ),
        "SCM_PLACEBO": InstrumentSpec(
            instrument_id="SCM_PLACEBO",
            estimator_family="SCM_FAMILY",
            inference_family="PLACEBO_INFERENCE_FAMILY",
            instrument_family_label="SCM + Placebo",
            design_requirements=("SINGLE_TREATMENT_CONTROL", "SINGLE_TREATED_OR_RESTRICTED"),
            estimand_requirements=("standard_incrementality",),
            requires_bau_control=True,
            diagnostic_only=True,
        ),
        "TBR_RIDGE_BRB": InstrumentSpec(
            instrument_id="TBR_RIDGE_BRB",
            estimator_family="TBR_RIDGE_FAMILY",
            inference_family="BOOTSTRAP_INFERENCE_FAMILY",
            instrument_family_label="TBRRidge + BRB",
            design_requirements=("SINGLE_TREATMENT_CONTROL", "MULTI_CELL_COMMON_CONTROL", "MULTI_CELL_SPLIT_CONTROL"),
            estimand_requirements=("standard_incrementality",),
            requires_bau_control=True,
        ),
        "TBR_RIDGE_KFOLD": InstrumentSpec(
            instrument_id="TBR_RIDGE_KFOLD",
            estimator_family="TBR_RIDGE_FAMILY",
            inference_family="BOOTSTRAP_INFERENCE_FAMILY",
            instrument_family_label="TBRRidge + KFold",
            design_requirements=("SINGLE_TREATMENT_CONTROL",),
            estimand_requirements=("standard_incrementality",),
            requires_bau_control=True,
            diagnostic_only=True,
        ),
        "TBR_RIDGE_PLACEBO": InstrumentSpec(
            instrument_id="TBR_RIDGE_PLACEBO",
            estimator_family="TBR_RIDGE_FAMILY",
            inference_family="PLACEBO_INFERENCE_FAMILY",
            instrument_family_label="TBRRidge + Placebo",
            design_requirements=("SINGLE_TREATMENT_CONTROL",),
            estimand_requirements=("standard_incrementality",),
            requires_bau_control=True,
            diagnostic_only=True,
        ),
        "DID_2X2_POINT_ESTIMATE": InstrumentSpec(
            instrument_id="DID_2X2_POINT_ESTIMATE",
            estimator_family="DID_FAMILY",
            inference_family="POINT_ESTIMATE_ONLY",
            instrument_family_label="DID 2x2 Point Estimate",
            design_requirements=("SINGLE_TREATMENT_CONTROL", "MULTI_CELL_COMMON_CONTROL", "MULTI_CELL_SPLIT_CONTROL"),
            estimand_requirements=("standard_incrementality",),
            requires_bau_control=True,
            requires_assignment_feasible=True,
        ),
        "DID_BOOTSTRAP": InstrumentSpec(
            instrument_id="DID_BOOTSTRAP",
            estimator_family="DID_FAMILY",
            inference_family="BOOTSTRAP_INFERENCE_FAMILY",
            instrument_family_label="DID Bootstrap Inference (not governed point estimate)",
            design_requirements=("SINGLE_TREATMENT_CONTROL", "MULTI_CELL_COMMON_CONTROL", "MULTI_CELL_SPLIT_CONTROL"),
            estimand_requirements=("standard_incrementality",),
            requires_bau_control=True,
            requires_assignment_feasible=True,
        ),
        "AUGSYNTH_JACKKNIFE": InstrumentSpec(
            instrument_id="AUGSYNTH_JACKKNIFE",
            estimator_family="AUGSYNTH_FAMILY",
            inference_family="JACKKNIFE_INFERENCE_FAMILY",
            instrument_family_label="AugSynth + Jackknife",
            design_requirements=("SINGLE_TREATMENT_CONTROL",),
            estimand_requirements=("standard_incrementality",),
            requires_bau_control=True,
            diagnostic_only=True,
        ),
        "MATCHED_PAIR_RANDOMIZATION": InstrumentSpec(
            instrument_id="MATCHED_PAIR_RANDOMIZATION",
            estimator_family="MATCHED_PAIR_FAMILY",
            inference_family="BOOTSTRAP_INFERENCE_FAMILY",
            instrument_family_label="MatchedPair + RandomizationInference",
            design_requirements=("MATCHED_PAIR",),
            estimand_requirements=("standard_incrementality",),
            requires_matched_pair_metadata=True,
            requires_assignment_feasible=True,
        ),
        "AB_STANDARD_INFERENCE": InstrumentSpec(
            instrument_id="AB_STANDARD_INFERENCE",
            estimator_family="AB_TEST_FAMILY",
            inference_family="CONFORMAL_INFERENCE_FAMILY",
            instrument_family_label="A/B + StandardInference",
            design_requirements=("INDIVIDUAL_RANDOMIZED_AB",),
            estimand_requirements=("standard_incrementality",),
            requires_individual_randomized_ab=True,
        ),
    }


def _instrument_list(gov: dict[str, Any], key: str) -> frozenset[str]:
    val = gov.get(key)
    if isinstance(val, list):
        return frozenset(_token(x) for x in val)
    return frozenset()


def _parse_instrument_spec(item: Any, catalog: dict[str, InstrumentSpec]) -> InstrumentSpec | None:
    if isinstance(item, str):
        iid = _token(item)
        if iid in catalog:
            return catalog[iid]
        return InstrumentSpec(
            instrument_id=iid,
            estimator_family="UNKNOWN_METHOD_FAMILY",
            inference_family="UNKNOWN_METHOD_FAMILY",
            instrument_family_label=iid,
        )
    if isinstance(item, dict):
        iid = _token(item.get("instrument_id"))
        if not iid:
            return None
        base = catalog.get(iid)
        est = _token(item.get("estimator_family") or (base.estimator_family if base else ""))
        inf = _token(item.get("inference_family") or (base.inference_family if base else ""))
        label = str(item.get("instrument_family_label") or (base.instrument_family_label if base else f"{est} + {inf}"))
        design_reqs = item.get("design_requirements") or (base.design_requirements if base else ())
        estimand_reqs = item.get("estimand_requirements") or (base.estimand_requirements if base else ())
        disallowed = item.get("disallowed_designs") or (base.disallowed_designs if base else ())
        return InstrumentSpec(
            instrument_id=iid,
            estimator_family=est or "UNKNOWN_METHOD_FAMILY",
            inference_family=inf or "UNKNOWN_METHOD_FAMILY",
            instrument_family_label=label,
            design_requirements=tuple(_token(x) for x in design_reqs) if design_reqs else (),
            disallowed_designs=tuple(_token(x) for x in disallowed) if disallowed else (),
            estimand_requirements=tuple(_token(x) for x in estimand_reqs) if estimand_reqs else (),
            requires_bau_control=bool(item.get("requires_bau_control", base.requires_bau_control if base else False)),
            requires_assignment_feasible=bool(
                item.get("requires_assignment_feasible", base.requires_assignment_feasible if base else False)
            ),
            requires_matched_pair_metadata=bool(
                item.get("requires_matched_pair_metadata", base.requires_matched_pair_metadata if base else False)
            ),
            requires_block_randomization_metadata=bool(
                item.get("requires_block_randomization_metadata", base.requires_block_randomization_metadata if base else False)
            ),
            requires_individual_randomized_ab=bool(
                item.get("requires_individual_randomized_ab", base.requires_individual_randomized_ab if base else False)
            ),
            dosage_compatible=bool(item.get("dosage_compatible", base.dosage_compatible if base else False)),
            diagnostic_only=bool(item.get("diagnostic_only", base.diagnostic_only if base else False)),
            governance_status=str(item["governance_status"]) if item.get("governance_status") else (
                base.governance_status if base else None
            ),
        )
    return None


def _resolve_candidate_instruments(packet: dict[str, Any], gov: dict[str, Any]) -> list[InstrumentSpec]:
    catalog = _default_instrument_catalog()
    gov_catalog = gov.get("governed_instruments") or gov.get("instrument_catalog")
    if isinstance(gov_catalog, list):
        for entry in gov_catalog:
            spec = _parse_instrument_spec(entry, catalog)
            if spec:
                catalog[spec.instrument_id] = spec

    raw_instruments = packet.get("candidate_instrument_review_targets")
    if isinstance(raw_instruments, list) and raw_instruments:
        specs: list[InstrumentSpec] = []
        for item in raw_instruments:
            spec = _parse_instrument_spec(item, catalog)
            if spec:
                specs.append(spec)
        return specs

    families_raw = packet.get("candidate_method_family_review_targets")
    if isinstance(families_raw, list) and families_raw:
        family_tokens = {_token(f) for f in families_raw}
        return [
            catalog[iid] for iid in catalog
            if _token(catalog[iid].estimator_family) in family_tokens
        ]

    return [catalog[iid] for iid in _DEFAULT_FALLBACK_INSTRUMENT_IDS if iid in catalog]


def _resolve_instrument_governance(
    spec: InstrumentSpec,
    gov_report: GovernanceHandoffReport,
    gov: dict[str, Any],
) -> tuple[str, str | None, str | None]:
    iid = spec.instrument_id
    est = _token(spec.estimator_family)

    if spec.governance_status:
        gs = _token(spec.governance_status)
    elif iid in _instrument_list(gov, "blocked_instruments") or iid in gov_report.blocked_methods:
        gs = "BLOCKED"
    elif iid in _instrument_list(gov, "diagnostic_only_instruments") or spec.diagnostic_only:
        gs = "DIAGNOSTIC_ONLY"
    elif iid in _instrument_list(gov, "restricted_instruments") or est in gov_report.restricted_methods:
        gs = "RESTRICTED"
    elif iid in _instrument_list(gov, "governed_instruments") or est in gov_report.governed_methods:
        gs = "GOVERNED"
    elif est in gov_report.diagnostic_only_methods:
        gs = "DIAGNOSTIC_ONLY"
    elif est in gov_report.blocked_methods:
        gs = "BLOCKED"
    elif est in gov_report.restricted_methods:
        gs = "RESTRICTED"
    else:
        gs = "CHARACTERIZED"

    diag_reason: str | None = None
    restr_reason: str | None = None
    if gs == "DIAGNOSTIC_ONLY":
        diag_reason = "governance diagnostic-only instrument"
    elif gs == "RESTRICTED":
        restr_reason = "governance restricted instrument"
    elif gs == "BLOCKED":
        restr_reason = "governance blocked instrument"
    return gs, diag_reason, restr_reason


def _design_matches_requirement(design_type: str, requirement: str) -> bool:
    if requirement == "SINGLE_TREATED_OR_RESTRICTED":
        return design_type in (
            "SINGLE_TREATMENT_CONTROL", "MULTI_CELL_SPLIT_CONTROL", "MATCHED_PAIR",
        )
    if requirement == "INDIVIDUAL_RANDOMIZED_AB":
        return design_type == "INDIVIDUAL_RANDOMIZED_AB"
    return design_type == requirement


def _evaluate_instrument_design_compat(
    spec: InstrumentSpec,
    design_type: str,
    design_compat: DesignCompatibilityReport,
) -> tuple[str, list[str], list[str]]:
    warnings: list[str] = []
    blocking: list[str] = []
    if not design_type:
        return _COMPAT_NOT_EVALUATED, warnings, blocking
    if design_type in spec.disallowed_designs:
        blocking.append(f"design {design_type} not supported for {spec.instrument_id}")
        return _COMPAT_BLOCKED, warnings, blocking
    if spec.requires_individual_randomized_ab and design_type != "INDIVIDUAL_RANDOMIZED_AB":
        blocking.append("requires individual randomized A/B design; geo-panel design incompatible")
        return _COMPAT_BLOCKED, warnings, blocking
    if spec.design_requirements:
        if not any(_design_matches_requirement(design_type, req) for req in spec.design_requirements):
            if spec.requires_matched_pair_metadata and design_type != "MATCHED_PAIR":
                blocking.append("requires matched-pair design metadata")
                return _COMPAT_RESTRICTED, warnings, blocking
            if spec.requires_block_randomization_metadata and design_type not in (
                "QUICK_BLOCK", "RERANDOMIZED_BLOCK",
            ):
                blocking.append("requires block/randomization metadata")
                return _COMPAT_RESTRICTED, warnings, blocking
            blocking.append(f"design {design_type} incompatible with instrument requirements")
            return _COMPAT_BLOCKED, warnings, blocking
    if not design_compat.supported_design:
        blocking.append("unsupported design structure type")
        return _COMPAT_BLOCKED, warnings, blocking
    if design_type == "MULTI_CELL_COMMON_CONTROL" and spec.estimator_family == "SCM_FAMILY":
        blocking.append("multi-cell common-control production inference unsupported for SCM instruments")
        return _COMPAT_BLOCKED, warnings, blocking
    return _COMPAT_PASS, warnings, blocking


def _evaluate_instrument_estimand_compat(
    spec: InstrumentSpec,
    estimand_gate: EstimandGateReport,
) -> tuple[str, list[str], list[str], list[str]]:
    warnings: list[str] = []
    blocking: list[str] = []
    review_additions: list[str] = []

    if not estimand_gate.estimand_labels_present:
        blocking.append("missing estimand label")
        return _COMPAT_BLOCKED, warnings, blocking, review_additions

    needs_standard = "STANDARD_INCREMENTALITY" in spec.estimand_requirements
    needs_dosage = spec.dosage_compatible or "DOSAGE" in spec.estimand_requirements

    if estimand_gate.dosage_estimand_required and needs_standard and not needs_dosage:
        blocking.append("dosage design blocks standard incrementality instrument interpretation")
        return _COMPAT_BLOCKED, warnings, blocking, review_additions

    if estimand_gate.difference_in_policy_required and needs_standard:
        if spec.requires_bau_control and not estimand_gate.bau_control_preserved:
            blocking.append("difference-in-policy estimand incompatible with BAU-required instrument")
            review_additions.append(ReviewRequirementType.DIFFERENCE_IN_POLICY_REVIEW.value)
            return _COMPAT_BLOCKED, warnings, blocking, review_additions
        if estimand_gate.manipulated_control_detected:
            blocking.append("manipulated control blocks standard incrementality instrument")
            review_additions.append(ReviewRequirementType.DIFFERENCE_IN_POLICY_REVIEW.value)
            return _COMPAT_RESTRICTED, warnings, blocking, review_additions

    if spec.requires_bau_control and not estimand_gate.bau_control_preserved:
        blocking.append("instrument requires BAU control preservation")
        review_additions.append(ReviewRequirementType.DIFFERENCE_IN_POLICY_REVIEW.value)
        return _COMPAT_RESTRICTED, warnings, blocking, review_additions

    if needs_standard and not estimand_gate.standard_incrementality_allowed:
        if estimand_gate.dosage_estimand_required:
            blocking.append("standard incrementality instrument not dosage-compatible")
        else:
            blocking.append("standard incrementality interpretation not allowed for declared estimand")
        return _COMPAT_BLOCKED, warnings, blocking, review_additions

    if estimand_gate.dosage_estimand_required and needs_dosage:
        review_additions.append(ReviewRequirementType.DOSAGE_CONTRAST_REVIEW.value)

    return _COMPAT_PASS, warnings, blocking, review_additions


def _evaluate_instrument_assignment_compat(
    spec: InstrumentSpec,
    readiness: MethodSuitabilityReadinessReport,
    assignment: AssignmentHandoffReport,
    packet: dict[str, Any],
) -> tuple[str, list[str], list[str]]:
    warnings: list[str] = []
    blocking: list[str] = []
    if not spec.requires_assignment_feasible:
        return _COMPAT_PASS, warnings, blocking
    if readiness.assignment_feasibility_gate == "BLOCKED":
        blocking.append("assignment feasibility blocked")
        return _COMPAT_BLOCKED, warnings, blocking
    if assignment.redesign_recheck_required:
        warnings.append("assignment redesign/recheck required")
        return _COMPAT_RESTRICTED, warnings, blocking
    if spec.requires_matched_pair_metadata:
        pair_meta = packet.get("matched_pair_metadata") or _assignment_summary(packet).get("matched_pair_metadata")
        if not pair_meta:
            blocking.append("matched-pair metadata missing")
            return _COMPAT_NOT_EVALUATED, warnings, blocking
    if spec.requires_block_randomization_metadata:
        block_meta = packet.get("block_randomization_metadata") or _assignment_summary(packet).get("block_metadata")
        if not block_meta:
            blocking.append("block/randomization metadata missing")
            return _COMPAT_NOT_EVALUATED, warnings, blocking
    return _COMPAT_PASS, warnings, blocking


def _evaluate_instrument_power_compat(
    spec: InstrumentSpec,
    power: PowerMdeHandoffReport,
    packet: dict[str, Any],
) -> tuple[str, list[str], list[str]]:
    warnings: list[str] = []
    blocking: list[str] = []
    if power.power_mde_blocked or not power.inference_ready_claim_allowed:
        warnings.append("power/MDE readiness blocked or provisional")
        if spec.inference_family not in ("UNKNOWN_METHOD_FAMILY",):
            return _COMPAT_RESTRICTED, warnings, blocking
    parallel_trends = _token(packet.get("parallel_trends_warning_status") or packet.get("parallel_trends_status"))
    if parallel_trends in ("WARNING", "UNKNOWN", "VIOLATED", "PROVISIONAL"):
        warnings.append("parallel-trends or pre-trend compatibility warning")
    return _COMPAT_PASS, warnings, blocking


def _evaluate_instrument_scenario_compat(
    spec: InstrumentSpec,
    scenario: ScenarioPolicyHandoffReport,
    readiness: MethodSuitabilityReadinessReport,
) -> tuple[str, list[str], list[str]]:
    warnings: list[str] = []
    blocking: list[str] = []
    if readiness.scenario_policy_gate == "BLOCKED":
        blocking.append("scenario policy blocked")
        return _COMPAT_BLOCKED, warnings, blocking
    if scenario.shared_control_conflict:
        warnings.append("shared-control conflict present")
        return _COMPAT_RESTRICTED, warnings, blocking
    return _COMPAT_PASS, warnings, blocking


def _classify_instrument(
    spec: InstrumentSpec,
    handoff_blocked: bool,
    estimand_present: bool,
    design_type: str,
    design_compat: DesignCompatibilityReport,
    estimand_gate: EstimandGateReport,
    readiness: MethodSuitabilityReadinessReport,
    assignment: AssignmentHandoffReport,
    power: PowerMdeHandoffReport,
    scenario: ScenarioPolicyHandoffReport,
    gov_report: GovernanceHandoffReport,
    gov: dict[str, Any],
    base_review_reqs: tuple[str, ...],
    has_handoff_warnings: bool,
    cfg: MethodSuitabilityConfig,
    packet: dict[str, Any],
) -> InstrumentSuitabilityEntry:
    governance_status, diag_reason, restr_reason = _resolve_instrument_governance(spec, gov_report, gov)
    warnings: list[str] = []
    blocking: list[str] = []
    review_reqs = list(base_review_reqs)

    if spec.instrument_id == "DID_BOOTSTRAP":
        blocking.append("DID_BOOTSTRAP is bootstrap inference alias; use DID_2X2_POINT_ESTIMATE for governed point estimate")
        return InstrumentSuitabilityEntry(
            instrument_id=spec.instrument_id,
            estimator_family=spec.estimator_family,
            inference_family=spec.inference_family,
            instrument_family_label=spec.instrument_family_label,
            design_compatibility_status=_COMPAT_NOT_EVALUATED,
            estimand_compatibility_status=_COMPAT_BLOCKED,
            assignment_compatibility_status=_COMPAT_BLOCKED,
            power_mde_compatibility_status=_COMPAT_BLOCKED,
            scenario_policy_compatibility_status=_COMPAT_BLOCKED,
            governance_status=governance_status,
            suitability_status=MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED,
            review_requirements=tuple(review_reqs),
            warnings=tuple(dict.fromkeys(warnings)),
            blocking_reasons=tuple(dict.fromkeys(blocking)),
            diagnostic_only_reason=None,
            restricted_reason="bootstrap_inference_not_implemented",
        )

    design_status, dw, db = _evaluate_instrument_design_compat(spec, design_type, design_compat)
    warnings.extend(dw)
    blocking.extend(db)

    estimand_status, ew, eb, er = _evaluate_instrument_estimand_compat(spec, estimand_gate)
    warnings.extend(ew)
    blocking.extend(eb)
    for r in er:
        if r not in review_reqs:
            review_reqs.append(r)

    assign_status, aw, ab = _evaluate_instrument_assignment_compat(spec, readiness, assignment, packet)
    warnings.extend(aw)
    blocking.extend(ab)

    power_status, pw, pb = _evaluate_instrument_power_compat(spec, power, packet)
    warnings.extend(pw)
    blocking.extend(pb)

    scenario_status, sw, sb = _evaluate_instrument_scenario_compat(spec, scenario, readiness)
    warnings.extend(sw)
    blocking.extend(sb)

    if governance_status == "BLOCKED":
        return InstrumentSuitabilityEntry(
            instrument_id=spec.instrument_id,
            estimator_family=spec.estimator_family,
            inference_family=spec.inference_family,
            instrument_family_label=spec.instrument_family_label,
            design_compatibility_status=design_status,
            estimand_compatibility_status=estimand_status,
            assignment_compatibility_status=assign_status,
            power_mde_compatibility_status=power_status,
            scenario_policy_compatibility_status=scenario_status,
            governance_status=governance_status,
            suitability_status=MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED,
            review_requirements=tuple(review_reqs),
            warnings=tuple(dict.fromkeys(warnings)),
            blocking_reasons=("governance blocked instrument",),
            diagnostic_only_reason=None,
            restricted_reason=restr_reason,
        )

    if governance_status == "DIAGNOSTIC_ONLY" or spec.diagnostic_only:
        if cfg.diagnostic_only_blocks_production:
            warnings.append("diagnostic-only instrument; not production-authorized")
        return InstrumentSuitabilityEntry(
            instrument_id=spec.instrument_id,
            estimator_family=spec.estimator_family,
            inference_family=spec.inference_family,
            instrument_family_label=spec.instrument_family_label,
            design_compatibility_status=design_status,
            estimand_compatibility_status=estimand_status,
            assignment_compatibility_status=assign_status,
            power_mde_compatibility_status=power_status,
            scenario_policy_compatibility_status=scenario_status,
            governance_status="DIAGNOSTIC_ONLY",
            suitability_status=MethodFamilySuitabilityStatus.METHOD_FAMILY_DIAGNOSTIC_ONLY,
            review_requirements=tuple(review_reqs),
            warnings=tuple(dict.fromkeys(warnings)),
            blocking_reasons=(),
            diagnostic_only_reason=diag_reason or "diagnostic-only instrument",
            restricted_reason=None,
        )

    if handoff_blocked:
        status = MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED
        blocking.append("handoff blocked")
    elif not estimand_present:
        status = MethodFamilySuitabilityStatus.METHOD_FAMILY_NOT_EVALUATED
        blocking.append("missing estimand")
    elif _COMPAT_BLOCKED in (design_status, estimand_status, assign_status, scenario_status):
        status = MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED
    elif _COMPAT_NOT_EVALUATED in (design_status, estimand_status, assign_status):
        status = MethodFamilySuitabilityStatus.METHOD_FAMILY_NOT_EVALUATED
    elif governance_status == "RESTRICTED" or _COMPAT_RESTRICTED in (
        design_status, estimand_status, assign_status, power_status, scenario_status,
    ):
        status = MethodFamilySuitabilityStatus.METHOD_FAMILY_RESTRICTED
        restr_reason = restr_reason or "compatibility restricted"
    elif warnings or has_handoff_warnings or review_reqs:
        status = MethodFamilySuitabilityStatus.METHOD_FAMILY_ELIGIBLE_WITH_WARNINGS
    else:
        status = MethodFamilySuitabilityStatus.METHOD_FAMILY_ELIGIBLE_FOR_REVIEW

    return InstrumentSuitabilityEntry(
        instrument_id=spec.instrument_id,
        estimator_family=spec.estimator_family,
        inference_family=spec.inference_family,
        instrument_family_label=spec.instrument_family_label,
        design_compatibility_status=design_status,
        estimand_compatibility_status=estimand_status,
        assignment_compatibility_status=assign_status,
        power_mde_compatibility_status=power_status,
        scenario_policy_compatibility_status=scenario_status,
        governance_status=governance_status,
        suitability_status=status,
        review_requirements=tuple(dict.fromkeys(review_reqs)),
        warnings=tuple(dict.fromkeys(warnings)),
        blocking_reasons=tuple(dict.fromkeys(blocking)),
        diagnostic_only_reason=None,
        restricted_reason=restr_reason,
    )


def _production_catalog_overlay(
    entry: InstrumentSuitabilityEntry,
    cfg: MethodSuitabilityConfig,
) -> dict[str, Any]:
    if not cfg.enforce_production_catalog_blocklist:
        return {}
    report = evaluate_production_catalog_status(
        {
            "instrument_id": entry.instrument_id,
            "method_family": entry.estimator_family,
            "estimator_family": entry.estimator_family,
            "inference_family": entry.inference_family,
            "production_context": "review",
            "requested_role": "GOVERNED_POINT_ESTIMATE",
        }
    )
    return production_catalog_overlay_for_matrix(report)


def _statistical_promotion_overlay(
    entry: InstrumentSuitabilityEntry,
    cfg: MethodSuitabilityConfig,
) -> dict[str, Any]:
    if not cfg.enforce_statistical_promotion_thresholds:
        return {}
    report = evaluate_statistical_promotion_thresholds(
        {
            "instrument_id": entry.instrument_id,
            "method_family": entry.estimator_family,
            "estimator_family": entry.estimator_family,
            "inference_family": entry.inference_family,
            "requested_maturity_state": MATURITY_RESTRICTED_EXPERT_REVIEW,
            "production_context": "review",
            "requested_role": "GOVERNED_POINT_ESTIMATE",
        }
    )
    if isinstance(report, list):
        return {}
    return statistical_promotion_overlay_for_matrix(report)


def _instrument_entry_to_matrix_row(
    entry: InstrumentSuitabilityEntry,
    cfg: MethodSuitabilityConfig | None = None,
) -> dict[str, Any]:
    row = {
        "instrument_id": entry.instrument_id,
        "estimator_family": entry.estimator_family,
        "inference_family": entry.inference_family,
        "instrument_family_label": entry.instrument_family_label,
        "design_compatibility_status": entry.design_compatibility_status,
        "estimand_compatibility_status": entry.estimand_compatibility_status,
        "assignment_compatibility_status": entry.assignment_compatibility_status,
        "power_mde_compatibility_status": entry.power_mde_compatibility_status,
        "scenario_policy_compatibility_status": entry.scenario_policy_compatibility_status,
        "governance_status": entry.governance_status,
        "suitability_status": entry.suitability_status.value,
        "review_requirements": list(entry.review_requirements),
        "warnings": list(entry.warnings),
        "blocking_reasons": list(entry.blocking_reasons),
        "diagnostic_only_reason": entry.diagnostic_only_reason,
        "restricted_reason": entry.restricted_reason,
    }
    if cfg is not None:
        row.update(_production_catalog_overlay(entry, cfg))
        row.update(_statistical_promotion_overlay(entry, cfg))
    return row


def _count_instruments(entries: tuple[InstrumentSuitabilityEntry, ...]) -> dict[str, int]:
    eligible = sum(
        1 for e in entries
        if e.suitability_status in (
            MethodFamilySuitabilityStatus.METHOD_FAMILY_ELIGIBLE_FOR_REVIEW,
            MethodFamilySuitabilityStatus.METHOD_FAMILY_ELIGIBLE_WITH_WARNINGS,
        )
    )
    return {
        "candidate_instrument_count": len(entries),
        "eligible_instrument_count": eligible,
        "restricted_instrument_count": sum(
            1 for e in entries if e.suitability_status == MethodFamilySuitabilityStatus.METHOD_FAMILY_RESTRICTED
        ),
        "diagnostic_only_instrument_count": sum(
            1 for e in entries if e.suitability_status == MethodFamilySuitabilityStatus.METHOD_FAMILY_DIAGNOSTIC_ONLY
        ),
        "blocked_instrument_count": sum(
            1 for e in entries if e.suitability_status == MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED
        ),
        "not_evaluated_instrument_count": sum(
            1 for e in entries if e.suitability_status == MethodFamilySuitabilityStatus.METHOD_FAMILY_NOT_EVALUATED
        ),
    }


def _evaluate_readiness(
    packet: dict[str, Any],
    upstream: dict[str, Any],
    estimand_present: bool,
    gov: dict[str, Any],
    cfg: MethodSuitabilityConfig,
) -> MethodSuitabilityReadinessReport:
    profiler = _gate_status(upstream.get("profiler_status"))
    geo = _gate_status(upstream.get("geo_feasibility_status"))
    spend = _gate_status(upstream.get("spend_feasibility_status"))
    power = _gate_status(upstream.get("power_mde_status") or _power_summary(packet).get("power_mde_status"))
    design = _gate_status(
        upstream.get("design_cell_structure_status")
        or packet.get("design_structure_status")
    )
    scenario = _gate_status(
        upstream.get("scenario_policy_feasibility_status")
        or _scenario_summary(packet).get("scenario_policy_status")
    )
    assignment = _gate_status(
        upstream.get("assignment_feasibility_status")
        or _assignment_summary(packet).get("assignment_feasibility_status")
        or packet.get("assignment_feasibility_status")
    )
    estimand_gate = "PASS" if estimand_present else "BLOCKED"
    gov_complete = bool(
        gov.get("instrument_catalog_status") or gov.get("method_roadmap_status")
        or gov.get("governed_methods") or gov.get("method_family_governance")
    )
    governance_gate = "PASS" if gov_complete else ("BLOCKED" if cfg.missing_governance_is_blocking else "PROVISIONAL")

    hard_pass = all(
        g == "PASS"
        for g in (profiler, geo, design, estimand_gate)
    ) and governance_gate != "BLOCKED"

    return MethodSuitabilityReadinessReport(
        profiler_gate=profiler,
        geo_feasibility_gate=geo,
        spend_feasibility_gate=spend,
        power_mde_readiness_gate=power,
        design_cell_structure_gate=design,
        scenario_policy_gate=scenario,
        assignment_feasibility_gate=assignment,
        estimand_declaration_gate=estimand_gate,
        governance_catalog_gate=governance_gate,
        all_hard_gates_pass=hard_pass,
    )


def _evaluate_estimand_gate(
    packet: dict[str, Any],
    contrasts: list[dict[str, Any]],
    estimand_labels: list[str],
    issues: list[SuitabilityIssue],
    cfg: MethodSuitabilityConfig,
) -> EstimandGateReport:
    design_type = _token(packet.get("design_structure_type"))
    labels_upper = {_token(l) for l in estimand_labels}

    manipulated = any(
        c.get("manipulated_control") or c.get("bau_control_preserved") is False
        for c in contrasts
    )
    bau_preserved = all(
        c.get("bau_control_preserved", True) is not False for c in contrasts
    ) if contrasts else True

    dosage_required = (
        design_type in ("DOSAGE_CONTRAST",)
        or bool(labels_upper & _DOSAGE_ESTIMANDS)
        or any(_token(c.get("contrast_type")) == "DOSAGE_LOW_VS_HIGH" for c in contrasts)
    )
    dip_required = (
        design_type in ("DIFFERENCE_IN_POLICY",)
        or bool(labels_upper & _DIP_ESTIMANDS)
        or manipulated
    )
    budget_required = (
        design_type in ("BUDGET_REALLOCATION",)
        or bool(labels_upper & _BUDGET_ESTIMANDS)
    )
    go_live_required = (
        design_type in ("GO_LIVE",)
        or bool(labels_upper & _GO_LIVE_ESTIMANDS)
    )

    present = bool(estimand_labels)
    if not present and cfg.missing_estimand_is_blocking:
        issues.append(SuitabilityIssue(
            code="MISSING_ESTIMAND",
            message="estimand label missing",
            severity=IssueSeverity.BLOCKING,
            field="estimand_summaries",
        ))

    standard_allowed = (
        present
        and bau_preserved
        and not manipulated
        and not dosage_required
        and not dip_required
        and not budget_required
    )

    if manipulated:
        issues.append(SuitabilityIssue(
            code="MANIPULATED_CONTROL",
            message="manipulated control blocks standard incrementality",
            severity=IssueSeverity.WARNING,
        ))

    status = "PASS" if present else ("BLOCKED" if cfg.missing_estimand_is_blocking else "PROVISIONAL")

    return EstimandGateReport(
        estimand_labels_present=present,
        standard_incrementality_allowed=standard_allowed,
        dosage_estimand_required=dosage_required,
        difference_in_policy_required=dip_required,
        budget_reallocation_required=budget_required,
        go_live_required=go_live_required,
        bau_control_preserved=bau_preserved,
        manipulated_control_detected=manipulated,
        status=status,
    )


def _detect_review_requirements(
    packet: dict[str, Any],
    contrasts: list[dict[str, Any]],
    estimand_gate: EstimandGateReport,
    scenario: ScenarioPolicyHandoffReport,
    assignment: AssignmentHandoffReport,
    power: PowerMdeHandoffReport,
    spend: SpendHandoffReport,
    gov: GovernanceHandoffReport,
    readiness: MethodSuitabilityReadinessReport,
) -> ReviewRequirementReport:
    reqs: list[str] = []
    preserved = False

    upstream_reqs = packet.get("review_requirements")
    if isinstance(upstream_reqs, list):
        reqs.extend(str(r) for r in upstream_reqs)
        preserved = True

    for c in contrasts:
        if c.get("method_suitability_review_required"):
            preserved = True
            if ReviewRequirementType.METHOD_GOVERNANCE_REVIEW.value not in reqs:
                reqs.append(ReviewRequirementType.METHOD_GOVERNANCE_REVIEW.value)

    if estimand_gate.standard_incrementality_allowed:
        reqs.append(ReviewRequirementType.STANDARD_INCREMENTALITY_REVIEW.value)
    if estimand_gate.dosage_estimand_required:
        reqs.append(ReviewRequirementType.DOSAGE_CONTRAST_REVIEW.value)
    if estimand_gate.difference_in_policy_required:
        reqs.append(ReviewRequirementType.DIFFERENCE_IN_POLICY_REVIEW.value)
    if estimand_gate.budget_reallocation_required:
        reqs.append(ReviewRequirementType.BUDGET_REALLOCATION_REVIEW.value)
    if estimand_gate.go_live_required:
        reqs.append(ReviewRequirementType.GO_LIVE_REVIEW.value)

    if scenario.shared_control_conflict:
        reqs.append(ReviewRequirementType.COMMON_CONTROL_REVIEW.value)
    if assignment.redesign_recheck_required:
        reqs.append(ReviewRequirementType.SPLIT_CONTROL_REDESIGN_REVIEW.value)
        reqs.append(ReviewRequirementType.ASSIGNMENT_FEASIBILITY_REVIEW.value)

    design_type = _token(packet.get("design_structure_type"))
    if design_type == "MATCHED_PAIR":
        reqs.append(ReviewRequirementType.MATCHED_PAIR_REVIEW.value)
    if design_type in ("RERANDOMIZED_BLOCK", "THINNING_DESIGN"):
        reqs.append(ReviewRequirementType.RERANDOMIZATION_REVIEW.value)
    if design_type in ("QUICK_BLOCK", "RERANDOMIZED_BLOCK"):
        reqs.append(ReviewRequirementType.BLOCKED_OR_CLUSTERED_DESIGN_REVIEW.value)

    if spend.out_of_support_warning:
        reqs.append(ReviewRequirementType.OUT_OF_HISTORICAL_SUPPORT_REVIEW.value)
    if power.power_mde_blocked or not power.inference_ready_claim_allowed:
        reqs.append(ReviewRequirementType.LOW_POWER_OR_HIGH_MDE_REVIEW.value)

    interference = _token(
        packet.get("interference_risk_status")
        or _assignment_summary(packet).get("interference_risk_status")
    )
    if interference in ("HIGH", "UNKNOWN", "UNCHARACTERIZED", "BLOCKING"):
        reqs.append(ReviewRequirementType.INTERFERENCE_RISK_REVIEW.value)

    if not gov.governance_complete:
        reqs.append(ReviewRequirementType.METHOD_GOVERNANCE_REVIEW.value)

    if readiness.assignment_feasibility_gate == "BLOCKED":
        reqs.append(ReviewRequirementType.ASSIGNMENT_FEASIBILITY_REVIEW.value)

    return ReviewRequirementReport(
        requirements=tuple(dict.fromkeys(reqs)),
        preserved_upstream_flags=preserved,
    )


def _classify_family(
    family: str,
    handoff_blocked: bool,
    estimand_present: bool,
    gov: GovernanceHandoffReport,
    has_warnings: bool,
    cfg: MethodSuitabilityConfig,
    review_reqs: tuple[str, ...],
) -> MethodFamilySuitabilityEntry:
    fam_token = _token(family)
    restrictions: list[str] = []
    warnings: list[str] = []
    blocking: list[str] = []
    stance: str | None = None

    if fam_token in gov.blocked_methods or fam_token.replace("_FAMILY", "") in {
        m.replace("_FAMILY", "") for m in gov.blocked_methods
    }:
        return MethodFamilySuitabilityEntry(
            method_family=family,
            suitability_status=MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED,
            review_requirements=review_reqs,
            restrictions=("governance_blocked",),
            warnings=(),
            blocking_reasons=("method family blocked in governance summary",),
            governance_stance="BLOCKED",
        )

    if fam_token in gov.diagnostic_only_methods or fam_token.replace("_FAMILY", "") in {
        m.replace("_FAMILY", "") for m in gov.diagnostic_only_methods
    }:
        stance = "DIAGNOSTIC_ONLY"
        if cfg.diagnostic_only_blocks_production:
            restrictions.append("diagnostic_only_not_production")
        return MethodFamilySuitabilityEntry(
            method_family=family,
            suitability_status=MethodFamilySuitabilityStatus.METHOD_FAMILY_DIAGNOSTIC_ONLY,
            review_requirements=review_reqs,
            restrictions=tuple(restrictions),
            warnings=("diagnostic-only method family; not production-authorized",),
            blocking_reasons=(),
            governance_stance=stance,
        )

    if fam_token in gov.restricted_methods:
        stance = "RESTRICTED"
        return MethodFamilySuitabilityEntry(
            method_family=family,
            suitability_status=MethodFamilySuitabilityStatus.METHOD_FAMILY_RESTRICTED,
            review_requirements=review_reqs,
            restrictions=("governance_restricted",),
            warnings=(),
            blocking_reasons=(),
            governance_stance=stance,
        )

    if fam_token == "UNKNOWN_METHOD_FAMILY" and cfg.unknown_method_family_not_evaluated:
        return MethodFamilySuitabilityEntry(
            method_family=family,
            suitability_status=MethodFamilySuitabilityStatus.METHOD_FAMILY_NOT_EVALUATED,
            review_requirements=review_reqs,
            restrictions=(),
            warnings=("unknown method family",),
            blocking_reasons=(),
            governance_stance=None,
        )

    if handoff_blocked or not estimand_present:
        status = MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED if handoff_blocked else (
            MethodFamilySuitabilityStatus.METHOD_FAMILY_NOT_EVALUATED
        )
        if handoff_blocked:
            blocking.append("handoff blocked")
        if not estimand_present:
            blocking.append("missing estimand")
        return MethodFamilySuitabilityEntry(
            method_family=family,
            suitability_status=status,
            review_requirements=review_reqs,
            restrictions=tuple(restrictions),
            warnings=tuple(warnings),
            blocking_reasons=tuple(blocking),
            governance_stance=stance or ("GOVERNED" if fam_token in gov.governed_methods else None),
        )

    if has_warnings or review_reqs:
        status = MethodFamilySuitabilityStatus.METHOD_FAMILY_ELIGIBLE_WITH_WARNINGS
        if review_reqs:
            warnings.append(f"review requirements: {', '.join(review_reqs[:3])}")
    else:
        status = MethodFamilySuitabilityStatus.METHOD_FAMILY_ELIGIBLE_FOR_REVIEW

    return MethodFamilySuitabilityEntry(
        method_family=family,
        suitability_status=status,
        review_requirements=review_reqs,
        restrictions=tuple(restrictions),
        warnings=tuple(warnings),
        blocking_reasons=tuple(blocking),
        governance_stance=stance or ("GOVERNED" if fam_token in gov.governed_methods else "CHARACTERIZED"),
    )


def _evaluate_governance(packet: dict[str, Any], cfg: MethodSuitabilityConfig) -> GovernanceHandoffReport:
    gov = _governance(packet)
    catalog = gov.get("instrument_catalog_status")
    roadmap = gov.get("method_roadmap_status")
    complete = bool(catalog or roadmap or gov.get("governed_methods") or gov.get("method_family_governance"))

    def _list(key: str) -> tuple[str, ...]:
        val = gov.get(key)
        if isinstance(val, list):
            return tuple(str(x) for x in val)
        return ()

    return GovernanceHandoffReport(
        instrument_catalog_status=str(catalog) if catalog else None,
        method_roadmap_status=str(roadmap) if roadmap else None,
        governed_methods=_list("governed_methods"),
        restricted_methods=_list("restricted_methods"),
        diagnostic_only_methods=_list("diagnostic_only_methods"),
        blocked_methods=_list("blocked_methods"),
        governance_complete=complete,
        preserved_status=str(gov.get("method_family_governance")) if gov.get("method_family_governance") else None,
    )


def _evaluate_scenario(packet: dict[str, Any], contrasts: list[dict[str, Any]]) -> ScenarioPolicyHandoffReport:
    scen = _scenario_summary(packet)
    status = scen.get("scenario_policy_status") or scen.get("status")
    conflict = bool(scen.get("shared_control_conflict")) or any(
        c.get("shared_control_conflict") for c in contrasts
    )
    spend_status = scen.get("required_vs_achieved_spend_contrast_status")
    hist = scen.get("historical_support_status")
    for c in contrasts:
        if c.get("historical_support_status"):
            hist = c.get("historical_support_status")
        if c.get("required_vs_achieved_spend_contrast_status"):
            spend_status = c.get("required_vs_achieved_spend_contrast_status")
    return ScenarioPolicyHandoffReport(
        scenario_policy_status=str(status) if status else None,
        shared_control_conflict=conflict,
        spend_contrast_status=str(spend_status) if spend_status else None,
        historical_support_status=str(hist) if hist else None,
        preserved_status=str(status) if status else None,
    )


def _evaluate_assignment(packet: dict[str, Any]) -> AssignmentHandoffReport:
    assign = _assignment_summary(packet)
    status = assign.get("assignment_feasibility_status") or packet.get("assignment_feasibility_status")
    redesign = bool(
        assign.get("redesign_recheck_required")
        or assign.get("split_control_required")
        or _token(status).find("REDESIGN") >= 0
        or _token(status).find("RECHECK") >= 0
    )
    return AssignmentHandoffReport(
        assignment_feasibility_status=str(status) if status else None,
        redesign_recheck_required=redesign,
        preserved_status=str(status) if status else None,
    )


def _evaluate_power(packet: dict[str, Any], cfg: MethodSuitabilityConfig) -> PowerMdeHandoffReport:
    power = _power_summary(packet)
    status = power.get("power_mde_status")
    blocked = _is_blocked(status)
    inference_ready = not blocked
    return PowerMdeHandoffReport(
        power_mde_status=str(status) if status else None,
        power_mde_blocked=blocked,
        inference_ready_claim_allowed=inference_ready,
        preserved_status=str(status) if status else None,
    )


def _evaluate_spend(packet: dict[str, Any], contrasts: list[dict[str, Any]]) -> SpendHandoffReport:
    spend = _spend_summary(packet)
    status = spend.get("spend_feasibility_status")
    hist = spend.get("historical_support_status")
    out_of_support = False
    hist_token = _token(hist)
    if hist_token in ("OUT_OF_HISTORICAL_SUPPORT", "POLICY_OUT_OF_HISTORICAL_SUPPORT", "BELOW_HISTORICAL_SUPPORT"):
        out_of_support = True
    for c in contrasts:
        ht = _token(c.get("historical_support_status"))
        if ht in ("OUT_OF_HISTORICAL_SUPPORT", "POLICY_OUT_OF_HISTORICAL_SUPPORT"):
            out_of_support = True
    return SpendHandoffReport(
        spend_feasibility_status=str(status) if status else None,
        historical_support_status=str(hist) if hist else None,
        out_of_support_warning=out_of_support,
        preserved_status=str(status) if status else None,
    )


def _select_handoff_status(
    readiness: MethodSuitabilityReadinessReport,
    estimand_gate: EstimandGateReport,
    review_report: ReviewRequirementReport,
    assignment: AssignmentHandoffReport,
    power: PowerMdeHandoffReport,
    design_compat: DesignCompatibilityReport,
    warnings: list[str],
    cfg: MethodSuitabilityConfig,
) -> tuple[MethodHandoffStatus, tuple[MethodHandoffStatus, ...], str]:
    secondary: list[MethodHandoffStatus] = []
    reqs = set(review_report.requirements)

    if readiness.profiler_gate == "BLOCKED":
        return (MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_DATA_READINESS, (), "Blocked by data readiness")
    if readiness.geo_feasibility_gate == "BLOCKED":
        return (MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_GEO_FEASIBILITY, (), "Blocked by geo feasibility")
    if readiness.design_cell_structure_gate == "BLOCKED":
        return (MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_DESIGN_STRUCTURE, (), "Blocked by design structure")

    scenario_blocked = readiness.scenario_policy_gate == "BLOCKED"
    if scenario_blocked and cfg.block_scenario_policy_blocked:
        return (MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_SCENARIO_POLICY, (), "Blocked by scenario policy")
    if scenario_blocked:
        secondary.append(MethodHandoffStatus.METHOD_HANDOFF_PROVISIONAL)

    assignment_blocked = readiness.assignment_feasibility_gate == "BLOCKED"
    if assignment_blocked and cfg.block_assignment_feasibility_blocked:
        return (
            MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_ASSIGNMENT_FEASIBILITY,
            tuple(secondary),
            "Blocked by assignment feasibility",
        )
    if assignment_blocked:
        secondary.append(MethodHandoffStatus.METHOD_HANDOFF_PROVISIONAL)

    if power.power_mde_blocked and cfg.block_power_mde_blocked:
        return (
            MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_POWER_MDE_READINESS,
            tuple(secondary),
            "Blocked by power/MDE readiness",
        )
    if power.power_mde_blocked:
        secondary.append(MethodHandoffStatus.METHOD_HANDOFF_PROVISIONAL)

    if not estimand_gate.estimand_labels_present and cfg.missing_estimand_is_blocking:
        return (
            MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_MISSING_ESTIMAND,
            tuple(secondary),
            "Blocked by missing estimand",
        )

    if not design_compat.supported_design and design_compat.design_structure_type:
        return (
            MethodHandoffStatus.METHOD_HANDOFF_BLOCKED_BY_UNSUPPORTED_DESIGN,
            tuple(secondary),
            "Blocked by unsupported design type",
        )

    if assignment.redesign_recheck_required or ReviewRequirementType.SPLIT_CONTROL_REDESIGN_REVIEW.value in reqs:
        sec = MethodHandoffStatus.METHOD_HANDOFF_REQUIRES_REDESIGN_RECHECK
        return (sec, tuple(s for s in secondary if s != sec), "Requires redesign/recheck")

    if ReviewRequirementType.DOSAGE_CONTRAST_REVIEW.value in reqs or estimand_gate.dosage_estimand_required:
        sec = MethodHandoffStatus.METHOD_HANDOFF_REQUIRES_DOSAGE_REVIEW
        secondary.append(sec)

    if ReviewRequirementType.DIFFERENCE_IN_POLICY_REVIEW.value in reqs or estimand_gate.difference_in_policy_required:
        sec = MethodHandoffStatus.METHOD_HANDOFF_REQUIRES_DIFFERENCE_IN_POLICY_REVIEW
        secondary.append(sec)

    if ReviewRequirementType.BUDGET_REALLOCATION_REVIEW.value in reqs or estimand_gate.budget_reallocation_required:
        sec = MethodHandoffStatus.METHOD_HANDOFF_REQUIRES_BUDGET_REALLOCATION_REVIEW
        secondary.append(sec)

    soft_provisional = (
        (scenario_blocked and not cfg.block_scenario_policy_blocked)
        or (assignment_blocked and not cfg.block_assignment_feasibility_blocked)
        or (power.power_mde_blocked and not cfg.block_power_mde_blocked)
    )
    has_provisional = (
        readiness.governance_catalog_gate in ("PROVISIONAL", "BLOCKED")
        or not estimand_gate.estimand_labels_present
        or secondary
    )
    has_warnings = bool(warnings) or bool(review_report.requirements)

    primary_secondary = tuple(dict.fromkeys(secondary))

    if soft_provisional:
        return (
            MethodHandoffStatus.METHOD_HANDOFF_PROVISIONAL,
            primary_secondary,
            "Provisional handoff; upstream gate blocked but config allows continuation",
        )

    if secondary and not has_warnings:
        return (secondary[0], primary_secondary[1:], f"Handoff requires: {secondary[0].value}")

    if has_provisional and not has_warnings:
        return (
            MethodHandoffStatus.METHOD_HANDOFF_PROVISIONAL,
            primary_secondary,
            "Provisional handoff; incomplete clarity",
        )

    if has_warnings or review_report.requirements:
        return (
            MethodHandoffStatus.METHOD_HANDOFF_READY_WITH_WARNINGS,
            primary_secondary,
            "Ready for method-family review with warnings",
        )

    return (
        MethodHandoffStatus.METHOD_HANDOFF_READY_FOR_SUITABILITY_REVIEW,
        primary_secondary,
        "Ready for method-family suitability review",
    )


def _handoff_is_blocked(status: MethodHandoffStatus) -> bool:
    return status.value.startswith("METHOD_HANDOFF_BLOCKED_")


def _evaluate_single_packet(
    packet: dict[str, Any],
    cfg: MethodSuitabilityConfig,
) -> MethodSuitabilityPacketReport:
    design_id = str(packet.get("design_id", "design_unspecified"))
    issues: list[SuitabilityIssue] = []
    warnings: list[str] = []

    upstream = _upstream(packet)
    contrasts = _contrast_summaries(packet)
    estimand_labels = _estimand_summaries(packet, contrasts)
    estimand_present = bool(estimand_labels)

    design_type = packet.get("design_structure_type")
    design_compat = DesignCompatibilityReport(
        design_structure_type=str(design_type) if design_type else None,
        supported_design=not design_type or _token(design_type) in _SUPPORTED_DESIGN_TYPES,
        contrast_count=len(contrasts),
    )
    if design_type and not design_compat.supported_design:
        issues.append(SuitabilityIssue(
            code="UNSUPPORTED_DESIGN",
            message=f"unsupported design structure type: {design_type}",
            severity=IssueSeverity.BLOCKING,
        ))

    gov_report = _evaluate_governance(packet, cfg)
    readiness = _evaluate_readiness(packet, upstream, estimand_present, _governance(packet), cfg)
    estimand_gate = _evaluate_estimand_gate(packet, contrasts, estimand_labels, issues, cfg)
    scenario_report = _evaluate_scenario(packet, contrasts)
    assignment_report = _evaluate_assignment(packet)
    power_report = _evaluate_power(packet, cfg)
    spend_report = _evaluate_spend(packet, contrasts)

    review_report = _detect_review_requirements(
        packet, contrasts, estimand_gate, scenario_report,
        assignment_report, power_report, spend_report, gov_report, readiness,
    )

    handoff_status, secondary, summary = _select_handoff_status(
        readiness, estimand_gate, review_report, assignment_report,
        power_report, design_compat, warnings, cfg,
    )

    targets_raw = packet.get("candidate_method_family_review_targets")
    if isinstance(targets_raw, list) and targets_raw:
        families = [str(f) for f in targets_raw]
    else:
        families = list(_ALL_METHOD_FAMILIES)

    handoff_blocked = _handoff_is_blocked(handoff_status)
    has_warnings = bool(warnings) or bool(review_report.requirements)
    design_type_token = _token(design_type)
    gov_dict = _governance(packet)

    instrument_specs = _resolve_candidate_instruments(packet, gov_dict)
    instrument_reports = tuple(
        _classify_instrument(
            spec, handoff_blocked, estimand_present, design_type_token, design_compat,
            estimand_gate, readiness, assignment_report, power_report, scenario_report,
            gov_report, gov_dict, review_report.requirements, has_warnings, cfg, packet,
        )
        for spec in instrument_specs
    )
    instrument_matrix = tuple(_instrument_entry_to_matrix_row(e, cfg) for e in instrument_reports)
    instrument_counts = _count_instruments(instrument_reports)

    family_reports = tuple(
        _classify_family(
            fam, handoff_blocked, estimand_present, gov_report,
            has_warnings, cfg, review_report.requirements,
        )
        for fam in families
    )

    blocking_reasons = tuple(
        i.message for i in issues if i.severity == IssueSeverity.BLOCKING
    )

    return MethodSuitabilityPacketReport(
        design_id=design_id,
        handoff_status=handoff_status,
        secondary_statuses=secondary,
        overall_suitability_summary=summary,
        review_requirements=review_report.requirements,
        method_family_suitability_reports=family_reports,
        readiness_report=readiness,
        estimand_gate_report=estimand_gate,
        design_compatibility_report=design_compat,
        scenario_policy_handoff_report=scenario_report,
        assignment_handoff_report=assignment_report,
        power_mde_handoff_report=power_report,
        spend_handoff_report=spend_report,
        governance_handoff_report=gov_report,
        claim_boundary_report=MethodSuitabilityClaimBoundaryReport(),
        issues=tuple(issues),
        warnings=tuple(dict.fromkeys(warnings)),
        blocking_reasons=blocking_reasons,
        instrument_suitability_reports=instrument_reports,
        instrument_suitability_matrix=instrument_matrix,
        **instrument_counts,
    )


def evaluate_method_suitability(
    input_data: Any,
    config: MethodSuitabilityConfig | None = None,
) -> MethodSuitabilityReport:
    """Evaluate method-family review suitability from handoff packets. Does not run estimators."""
    cfg = config or MethodSuitabilityConfig()
    packets = _normalize_packets(input_data)
    reports = [_evaluate_single_packet(p, cfg) for p in packets]

    all_issues: list[SuitabilityIssue] = []
    all_warnings: list[str] = []
    all_blocking: list[str] = []
    for r in reports:
        all_issues.extend(r.issues)
        all_warnings.extend(r.warnings)
        all_blocking.extend(r.blocking_reasons)

    if len(reports) == 1:
        r = reports[0]
        return MethodSuitabilityReport(
            artifact_id=_ARTIFACT_ID,
            design_id=r.design_id,
            handoff_status=r.handoff_status,
            secondary_statuses=r.secondary_statuses,
            overall_suitability_summary=r.overall_suitability_summary,
            review_requirements=r.review_requirements,
            design_reports=(r,),
            aggregate_summary=None,
            method_family_suitability_reports=r.method_family_suitability_reports,
            instrument_suitability_reports=r.instrument_suitability_reports,
            instrument_suitability_matrix=r.instrument_suitability_matrix,
            candidate_instrument_count=r.candidate_instrument_count,
            eligible_instrument_count=r.eligible_instrument_count,
            restricted_instrument_count=r.restricted_instrument_count,
            diagnostic_only_instrument_count=r.diagnostic_only_instrument_count,
            blocked_instrument_count=r.blocked_instrument_count,
            not_evaluated_instrument_count=r.not_evaluated_instrument_count,
            estimand_gate_report=r.estimand_gate_report,
            design_compatibility_report=r.design_compatibility_report,
            scenario_policy_handoff_report=r.scenario_policy_handoff_report,
            assignment_handoff_report=r.assignment_handoff_report,
            power_mde_handoff_report=r.power_mde_handoff_report,
            spend_handoff_report=r.spend_handoff_report,
            governance_handoff_report=r.governance_handoff_report,
            claim_boundary_report=r.claim_boundary_report,
            issues=r.issues,
            warnings=r.warnings,
            blocking_reasons=r.blocking_reasons,
        )

    return MethodSuitabilityReport(
        artifact_id=_ARTIFACT_ID,
        design_id=None,
        handoff_status=None,
        design_reports=tuple(reports),
        aggregate_summary=f"Evaluated {len(reports)} method-suitability handoff packets without ranking",
        claim_boundary_report=MethodSuitabilityClaimBoundaryReport(),
        issues=tuple(all_issues),
        warnings=tuple(dict.fromkeys(all_warnings)),
        blocking_reasons=tuple(dict.fromkeys(all_blocking)),
    )


evaluate_method_family_suitability = evaluate_method_suitability


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    packet = {
        "design_id": "smoke_go_dark",
        "design_structure_type": "SINGLE_TREATMENT_CONTROL",
        "upstream_statuses": {
            "profiler_status": "PASS",
            "geo_feasibility_status": "PASS",
            "spend_feasibility_status": "PASS",
            "power_mde_status": "PASS",
            "design_cell_structure_status": "PASS",
            "scenario_policy_feasibility_status": "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE",
            "assignment_feasibility_status": "ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME",
        },
        "contrast_summaries": [{
            "contrast_id": "T1_vs_C0",
            "contrast_type": "GO_DARK_VS_BAU",
            "estimand_label": "GO_DARK_VS_BAU",
            "bau_control_preserved": True,
            "manipulation_policy": "GO_DARK",
        }],
        "estimand_summaries": ["GO_DARK_VS_BAU"],
        "governance_summary": {
            "instrument_catalog_status": "AVAILABLE",
            "method_roadmap_status": "CURRENT",
            "governed_methods": ["TBR_RIDGE_FAMILY", "DID_FAMILY"],
        },
        "candidate_method_family_review_targets": ["TBR_RIDGE_FAMILY", "DID_FAMILY", "SCM_FAMILY"],
        "assignment_feasibility_summary": {
            "assignment_feasibility_status": "ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME",
        },
        "power_mde_summary": {"power_mde_status": "PASS"},
        "spend_summary": {"spend_feasibility_status": "PASS"},
        "scenario_policy_summary": {"scenario_policy_status": "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE"},
    }
    report = evaluate_method_suitability(packet)
    failed: list[str] = []
    if report.handoff_status not in (
        MethodHandoffStatus.METHOD_HANDOFF_READY_FOR_SUITABILITY_REVIEW,
        MethodHandoffStatus.METHOD_HANDOFF_READY_WITH_WARNINGS,
    ):
        failed.append("smoke_status")
    if report.claim_boundary_report.estimator_selected:
        failed.append("smoke_no_estimator")
    if not report.method_family_suitability_reports:
        failed.append("smoke_no_family_reports")
    if not report.instrument_suitability_reports:
        failed.append("smoke_no_instrument_reports")
    if report.claim_boundary_report.method_winner_selected:
        failed.append("smoke_no_winner")

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "method_suitability_runtime",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": "runtime_classifies_method_family_review_suitability_no_estimator_or_inference_authorization",
        "depends_on": [
            "GEO_KPI_SPEND_DATA_PROFILER_001",
            "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
            "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
            "POWER_MDE_DIAGNOSTICS_RUNTIME_001",
            "DESIGN_CELL_STRUCTURE_RUNTIME_001",
            "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001",
            "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001",
            "METHOD_SUITABILITY_HANDOFF_CONTRACT_001",
        ],
        "public_api": "evaluate_method_suitability",
        "runtime_method_suitability_implemented": True,
        "method_family_review_classification_implemented": True,
        "review_requirement_detection_implemented": True,
        "governance_stance_preservation_implemented": True,
        "estimand_gate_implemented": True,
        "handoff_readiness_gate_implemented": True,
        "instrument_suitability_matrix_implemented": True,
        "estimator_inference_instrument_classification_implemented": True,
        "method_family_only_classification": False,
        "method_winner_selected": False,
        "primary_readout_stack_selected": False,
        "sensitivity_stack_selected": False,
        "diagnostic_stack_selected": False,
        "method_family_selected": False,
        "estimator_selected": False,
        "inference_method_selected": False,
        "method_promotion_authorized": False,
        "method_production_compatibility_authorized": False,
        "geo_assignment_computed": False,
        "matched_pairs_generated": False,
        "blocks_generated": False,
        "randomization_computed": False,
        "rerandomization_computed": False,
        "thinning_design_generated": False,
        "matching_optimization_computed": False,
        "balance_optimization_computed": False,
        "scenario_policy_feasibility_computed": False,
        "assignment_feasibility_computed": False,
        "power_computed": False,
        "mde_computed": False,
        "p_value_computed": False,
        "confidence_interval_computed": False,
        "lift_computed": False,
        "roi_computed": False,
        "budget_optimization_authorized": False,
        "candidate_design_authorized": False,
        "treatment_control_assignment_authorized": False,
        "estimator_inference_authorized": False,
        "mmm_runtime_calls_implemented": False,
        "mmm_calibration_authorized": False,
        "production_authorization_granted": False,
        "llm_decisioning_authorized": False,
        "recommended_next_artifact": RECOMMENDED_NEXT_ARTIFACT,
        "alternative_next_artifact": ALTERNATIVE_NEXT_ARTIFACT,
        "failed_scenarios": failed,
        "smoke_handoff_status": report.handoff_status.value if report.handoff_status else None,
        "smoke_candidate_instrument_count": report.candidate_instrument_count,
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
