"""POWER_MDE_DIAGNOSTICS_RUNTIME_001 conservative readiness and descriptive sensitivity diagnostics."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, field, replace
from enum import Enum
from pathlib import Path
from typing import Any

from panel_exp.validation.geo_kpi_spend_data_profiler_001 import (
    GeoKpiSpendProfilerInput,
    ProfilerStatus,
)

_ARTIFACT_ID = "POWER_MDE_DIAGNOSTICS_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "power_mde_diagnostics_runtime_implemented_readiness_and_descriptive_sensitivity_only_no_power_mde_or_production_authorization"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/POWER_MDE_DIAGNOSTICS_RUNTIME_001_summary.json"
RECOMMENDED_NEXT_ARTIFACT = "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001"
ALTERNATIVE_NEXT_ARTIFACT = "POWER_MDE_FORMULA_AND_SIMULATION_METHOD_REGISTRY_001"

_BLOCKED_TOKENS = frozenset({"BLOCKED", "blocked"})
_READY_SPEND_HANDOFF = frozenset(
    {
        "SPEND_HANDOFF_READY_FOR_POWER_DIAGNOSTICS",
        "SPEND_HANDOFF_READY_WITH_WARNINGS",
        "READY_FOR_DOWNSTREAM_POWER_DIAGNOSTICS",
        "PASS_WITH_WARNINGS",
    }
)
_BLOCKED_SPEND_HANDOFF_PREFIXES = (
    "SPEND_HANDOFF_BLOCKED",
    "BLOCKED",
)
_PROVISIONAL_SPEND_HANDOFF = frozenset(
    {
        "SPEND_HANDOFF_PROVISIONAL_RESPONSE_BRIDGE",
        "PROVISIONAL",
        "SPEND_HANDOFF_BLOCKED_BY_REQUIRED_SPEND_UNKNOWN",
        "REQUIRED_SPEND_DELTA_UNKNOWN",
    }
)


class PowerMdeStatus(str, Enum):
    POWER_MDE_READY_FOR_DIAGNOSTIC_RUNTIME = "POWER_MDE_READY_FOR_DIAGNOSTIC_RUNTIME"
    POWER_MDE_READY_WITH_WARNINGS = "POWER_MDE_READY_WITH_WARNINGS"
    POWER_MDE_PROVISIONAL = "POWER_MDE_PROVISIONAL"
    POWER_MDE_BLOCKED_BY_DATA_READINESS = "POWER_MDE_BLOCKED_BY_DATA_READINESS"
    POWER_MDE_BLOCKED_BY_GEO_FEASIBILITY = "POWER_MDE_BLOCKED_BY_GEO_FEASIBILITY"
    POWER_MDE_BLOCKED_BY_SPEND_HANDOFF = "POWER_MDE_BLOCKED_BY_SPEND_HANDOFF"
    POWER_MDE_BLOCKED_BY_CELL_STRUCTURE = "POWER_MDE_BLOCKED_BY_CELL_STRUCTURE"
    POWER_MDE_BLOCKED_BY_ESTIMAND_MISMATCH = "POWER_MDE_BLOCKED_BY_ESTIMAND_MISMATCH"
    POWER_MDE_REQUIRES_METHOD_SUITABILITY_REVIEW = "POWER_MDE_REQUIRES_METHOD_SUITABILITY_REVIEW"
    POWER_MDE_NOT_EVALUATED = "POWER_MDE_NOT_EVALUATED"


class PowerMdeMode(str, Enum):
    KPI_ONLY_SENSITIVITY = "KPI_ONLY_SENSITIVITY"
    SPEND_CONFIRMED_SENSITIVITY = "SPEND_CONFIRMED_SENSITIVITY"
    DESIGN_CELL_SENSITIVITY = "DESIGN_CELL_SENSITIVITY"
    DOSAGE_CONTRAST_SENSITIVITY = "DOSAGE_CONTRAST_SENSITIVITY"
    EXPLORATORY_BACK_OF_NAPKIN = "EXPLORATORY_BACK_OF_NAPKIN"
    NOT_EVALUATED = "NOT_EVALUATED"


class IssueSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"


class MdeScope(str, Enum):
    CELL_LEVEL = "CELL_LEVEL"
    AGGREGATE_PANEL = "AGGREGATE_PANEL"
    GEO_LEVEL = "GEO_LEVEL"
    UNKNOWN = "UNKNOWN"


class DesignType(str, Enum):
    SINGLE_TREATED_VS_CONTROL = "single_treated_cell_vs_control"
    MULTI_CELL = "multi_cell_design"
    COMMON_CONTROL = "common_control_design"
    MATCHED_PAIR = "matched_pair_design"
    DOSAGE_CONTRAST = "dosage_contrast_design"
    DIFFERENCE_IN_POLICY = "difference_in_policy_design"
    BUDGET_REALLOCATION = "budget_reallocation_design"
    UNKNOWN = "unknown"


class GateStatus(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"
    NOT_EVALUATED = "NOT_EVALUATED"
    PROVISIONAL = "PROVISIONAL"


@dataclass(frozen=True)
class PowerMdeColumnMapping:
    geo_unit_id: str = "geo_unit_id"
    date: str = "date"
    kpi: str = "kpi_value"
    cell_id: str = "cell_id"
    cell_role: str = "cell_role"
    design_type: str = "design_type"
    time_grain: str = "time_grain"
    period_role: str = "period_role"


@dataclass(frozen=True)
class PowerMdeDiagnosticsConfig:
    columns: PowerMdeColumnMapping = field(default_factory=PowerMdeColumnMapping)
    minimum_pre_period_count: int = 8
    minimum_geo_count: int = 2
    allow_kpi_only_when_spend_handoff_missing: bool = True
    allow_exploratory_back_of_napkin: bool = True
    allow_negative_kpi: bool = False
    outlier_iqr_multiplier: float = 3.0
    warn_high_coefficient_of_variation: float = 2.0
    require_cell_structure_for_design_mode: bool = True
    profiler_status: str | None = None
    geo_feasibility_status: str | None = None
    spend_readiness_status: str | None = None
    spend_handoff_status: str | None = None
    required_spend_delta: float | None = None
    required_spend_delta_source: str | None = None
    response_bridge_source: str | None = None
    business_response_risk: bool = False
    candidate_manipulation_options: tuple[str, ...] = ()
    dosage_contrast_estimand_required: bool = False
    difference_in_policy_required: bool = False
    control_contamination_flags: tuple[str, ...] = ()
    method_suitability_review_required: bool = False
    ready_for_downstream_power_diagnostics: bool = False
    mmm_advisory_used: bool = False
    proxy_response_used: bool = False
    back_of_napkin_assumption_used: bool = False
    kpi_unit: str | None = None
    absolute_mde: float | None = None
    relative_mde: float | None = None
    kpi_mde: float | None = None
    mde_scope: MdeScope | str | None = None
    baseline_kpi_level: float | None = None
    test_duration: int | None = None
    design_type: str | None = None
    planned_test_start_date: str | None = None
    pre_period_start: str | None = None
    pre_period_end: str | None = None


@dataclass(frozen=True)
class PowerMdeDiagnosticsInput:
    rows: tuple[dict[str, Any], ...] | None = None
    profiler_status: str | None = None
    geo_feasibility_status: str | None = None
    spend_handoff_status: str | None = None
    spend_readiness_status: str | None = None
    required_spend_delta: float | None = None
    required_spend_delta_source: str | None = None
    response_bridge_source: str | None = None
    business_response_risk: bool | None = None
    candidate_manipulation_options: tuple[str, ...] | None = None
    dosage_contrast_estimand_required: bool | None = None
    difference_in_policy_required: bool | None = None
    control_contamination_flags: tuple[str, ...] | None = None
    method_suitability_review_required: bool | None = None
    ready_for_downstream_power_diagnostics: bool | None = None
    mmm_advisory_used: bool | None = None
    proxy_response_used: bool | None = None
    back_of_napkin_assumption_used: bool | None = None
    kpi_unit: str | None = None
    absolute_mde: float | None = None
    relative_mde: float | None = None
    kpi_mde: float | None = None
    mde_scope: MdeScope | str | None = None
    baseline_kpi_level: float | None = None
    test_duration: int | None = None
    design_type: str | None = None


@dataclass(frozen=True)
class PowerMdeIssue:
    code: str
    message: str
    severity: IssueSeverity
    field: str | None = None


@dataclass(frozen=True)
class PowerMdeReadinessReport:
    profiler_gate: GateStatus
    geo_unit_market_feasibility_gate: GateStatus
    spend_handoff_gate: GateStatus
    cell_structure_gate: GateStatus
    kpi_mde_target_gate: GateStatus
    noise_history_gate: GateStatus
    estimand_compatibility_gate: GateStatus
    method_suitability_precheck_gate: GateStatus
    all_gates_passed: bool
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PowerMdeNoiseHistoryReport:
    row_count: int
    geo_count: int
    time_period_count: int
    missing_kpi_count: int
    zero_kpi_count: int
    negative_kpi_count: int
    baseline_kpi_mean: float | None
    baseline_kpi_median: float | None
    baseline_kpi_std: float | None
    baseline_kpi_variance: float | None
    baseline_kpi_p10: float | None
    baseline_kpi_p90: float | None
    coefficient_of_variation: float | None
    minimum_pre_period_length_met: bool
    time_balance_status: str
    geo_balance_status: str
    outlier_summary: str
    kpi_history_valid: bool
    issues: tuple[PowerMdeIssue, ...] = ()


@dataclass(frozen=True)
class PowerMdeRepresentationReport:
    kpi_unit_preserved: bool
    kpi_unit: str | None
    absolute_mde_present: bool
    relative_mde_present: bool
    absolute_relative_conflict: bool
    mde_scope: MdeScope
    cell_vs_aggregate_conflict: bool
    baseline_kpi_level_present: bool
    duration_specific_mde_present: bool
    issues: tuple[PowerMdeIssue, ...] = ()


@dataclass(frozen=True)
class PowerMdeCellStructureReport:
    cell_ids_present: bool
    cell_roles_present: bool
    design_type_present: bool
    cell_count: int
    treated_cell_count: int
    control_cell_count: int
    common_control_detected: bool
    multi_cell_detected: bool
    dosage_design_detected: bool
    difference_in_policy_detected: bool
    inferred_design_type: DesignType
    cell_structure_status: str
    issues: tuple[PowerMdeIssue, ...] = ()


@dataclass(frozen=True)
class PowerMdeSpendCompatibilityReport:
    spend_handoff_status: str | None
    required_spend_delta: float | None
    required_spend_delta_source: str | None
    response_bridge_source: str | None
    business_response_risk: bool
    candidate_manipulation_options: tuple[str, ...]
    mmm_advisory_used: bool
    proxy_response_used: bool
    back_of_napkin_assumption_used: bool
    control_contamination_flags: tuple[str, ...]
    ready_for_downstream_power_diagnostics: bool
    spend_confirmed_mode_allowed: bool
    issues: tuple[PowerMdeIssue, ...] = ()


@dataclass(frozen=True)
class PowerMdeEstimandCompatibilityReport:
    standard_go_dark_interpretation_allowed: bool
    dosage_contrast_estimand_required: bool
    difference_in_policy_required: bool
    control_contamination_present: bool
    business_as_usual_control_preserved: bool
    method_suitability_review_required: bool
    allowed_runtime_mode: PowerMdeMode
    blocked_standard_go_dark_interpretation: bool
    issues: tuple[PowerMdeIssue, ...] = ()


@dataclass(frozen=True)
class PowerMdeClaimBoundaryReport:
    runtime_power_mde_diagnostics_implemented: bool = True
    readiness_diagnostics_implemented: bool = True
    descriptive_noise_summary_implemented: bool = True
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
class PowerMdeDiagnosticsReport:
    artifact_id: str
    status: PowerMdeStatus
    mode: PowerMdeMode
    final_verdict: str
    readiness_report: PowerMdeReadinessReport
    noise_history_report: PowerMdeNoiseHistoryReport
    mde_representation_report: PowerMdeRepresentationReport
    cell_structure_report: PowerMdeCellStructureReport
    spend_compatibility_report: PowerMdeSpendCompatibilityReport
    estimand_compatibility_report: PowerMdeEstimandCompatibilityReport
    claim_boundary_report: PowerMdeClaimBoundaryReport
    issues: tuple[PowerMdeIssue, ...]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


def _to_float(value: Any) -> float | None:
    if _is_missing(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _status_token(status: str | ProfilerStatus | None) -> str | None:
    if status is None:
        return None
    if isinstance(status, Enum):
        return str(status.value)
    return str(status)


def _is_blocked_status(status: str | None) -> bool:
    if status is None:
        return False
    upper = status.upper()
    return upper in _BLOCKED_TOKENS or upper.endswith("_BLOCKED") or upper.startswith("BLOCKED_")


def _is_ready_spend_handoff(status: str | None) -> bool:
    if status is None:
        return False
    upper = status.upper()
    return upper in _READY_SPEND_HANDOFF or "READY_FOR" in upper


def _is_provisional_spend_handoff(status: str | None) -> bool:
    if status is None:
        return True
    upper = status.upper()
    if _is_blocked_status(status):
        return False
    return upper in _PROVISIONAL_SPEND_HANDOFF or "PROVISIONAL" in upper or "UNKNOWN" in upper


def _is_blocked_spend_handoff(status: str | None) -> bool:
    if status is None:
        return False
    upper = status.upper()
    if _is_ready_spend_handoff(status) or _is_provisional_spend_handoff(status):
        return False
    return any(upper.startswith(p) for p in _BLOCKED_SPEND_HANDOFF_PREFIXES) or _is_blocked_status(status)


def _normalize_input(
    input_data: PowerMdeDiagnosticsInput | list[dict[str, Any]] | GeoKpiSpendProfilerInput | Any,
    config: PowerMdeDiagnosticsConfig | None,
) -> tuple[list[dict[str, Any]], PowerMdeDiagnosticsConfig]:
    cfg = config or PowerMdeDiagnosticsConfig()
    rows: list[dict[str, Any]]
    if isinstance(input_data, PowerMdeDiagnosticsInput):
        rows = list(input_data.rows or [])
        cfg = _merge_input_metadata(cfg, input_data)
    elif isinstance(input_data, list):
        rows = input_data
    elif isinstance(input_data, GeoKpiSpendProfilerInput):
        rows = list(input_data.rows or [])
    elif hasattr(input_data, "to_dict"):
        rows = input_data.to_dict("records")
    else:
        raise TypeError("input_data must be PowerMdeDiagnosticsInput, list[dict], GeoKpiSpendProfilerInput, or DataFrame")
    return rows, cfg


def _merge_input_metadata(
    cfg: PowerMdeDiagnosticsConfig, inp: PowerMdeDiagnosticsInput
) -> PowerMdeDiagnosticsConfig:
    updates: dict[str, Any] = {}
    for name in (
        "profiler_status",
        "geo_feasibility_status",
        "spend_handoff_status",
        "spend_readiness_status",
        "required_spend_delta",
        "required_spend_delta_source",
        "response_bridge_source",
        "business_response_risk",
        "candidate_manipulation_options",
        "dosage_contrast_estimand_required",
        "difference_in_policy_required",
        "control_contamination_flags",
        "method_suitability_review_required",
        "ready_for_downstream_power_diagnostics",
        "mmm_advisory_used",
        "proxy_response_used",
        "back_of_napkin_assumption_used",
        "kpi_unit",
        "absolute_mde",
        "relative_mde",
        "kpi_mde",
        "mde_scope",
        "baseline_kpi_level",
        "test_duration",
        "design_type",
    ):
        val = getattr(inp, name)
        if val is not None:
            updates[name] = val
    return replace(cfg, **updates) if updates else cfg


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    idx = (len(ordered) - 1) * q
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return ordered[lo]
    frac = idx - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


def _normalize_role(role: str) -> str:
    return role.strip().lower().replace("-", "_").replace(" ", "_")


def _is_treated_role(role: str) -> bool:
    return _normalize_role(role) in {"treated", "test", "treatment", "variant", "high", "heavy_up"}


def _is_control_role(role: str) -> bool:
    return _normalize_role(role) in {"control", "holdout", "untreated", "low", "business_as_usual", "bau"}


def _build_noise_history(
    rows: list[dict[str, Any]], cfg: PowerMdeDiagnosticsConfig
) -> PowerMdeNoiseHistoryReport:
    cols = cfg.columns
    issues: list[PowerMdeIssue] = []
    missing_kpi = 0
    zero_kpi = 0
    negative_kpi = 0
    kpi_values: list[float] = []
    geos: set[str] = set()
    periods: set[str] = set()
    geo_period_counts: dict[str, int] = defaultdict(int)
    period_geo_counts: dict[str, int] = defaultdict(int)

    for row in rows:
        geo = row.get(cols.geo_unit_id)
        period = row.get(cols.date)
        if not _is_missing(geo):
            geos.add(str(geo))
        if not _is_missing(period):
            periods.add(str(period))
        kpi = _to_float(row.get(cols.kpi))
        if kpi is None:
            missing_kpi += 1
            continue
        if kpi == 0.0:
            zero_kpi += 1
        if kpi < 0:
            negative_kpi += 1
            if not cfg.allow_negative_kpi:
                issues.append(
                    PowerMdeIssue(
                        "negative_kpi_not_allowed",
                        "Negative KPI value detected and allow_negative_kpi is false",
                        IssueSeverity.BLOCKING,
                        cols.kpi,
                    )
                )
            else:
                issues.append(
                    PowerMdeIssue(
                        "negative_kpi_warning",
                        "Negative KPI value detected",
                        IssueSeverity.WARNING,
                        cols.kpi,
                    )
                )
        kpi_values.append(kpi)
        if not _is_missing(geo) and not _is_missing(period):
            g, p = str(geo), str(period)
            geo_period_counts[g] += 1
            period_geo_counts[p] += 1

    row_count = len(rows)
    geo_count = len(geos)
    time_period_count = len(periods)
    minimum_pre_period_length_met = time_period_count >= cfg.minimum_pre_period_count

    if row_count == 0 or not kpi_values:
        issues.append(
            PowerMdeIssue("missing_kpi_history", "KPI history is missing or empty", IssueSeverity.BLOCKING, cols.kpi)
        )
    if geo_count < cfg.minimum_geo_count:
        issues.append(
            PowerMdeIssue(
                "insufficient_geo_count",
                f"Geo count {geo_count} below minimum_geo_count {cfg.minimum_geo_count}",
                IssueSeverity.BLOCKING,
                cols.geo_unit_id,
            )
        )
    if not minimum_pre_period_length_met and row_count > 0:
        issues.append(
            PowerMdeIssue(
                "minimum_pre_period_not_met",
                f"Distinct periods {time_period_count} below minimum_pre_period_count {cfg.minimum_pre_period_count}",
                IssueSeverity.BLOCKING,
                cols.date,
            )
        )

    mean = statistics.mean(kpi_values) if kpi_values else None
    median = statistics.median(kpi_values) if kpi_values else None
    std = statistics.pstdev(kpi_values) if len(kpi_values) > 1 else (0.0 if kpi_values else None)
    variance = statistics.pvariance(kpi_values) if len(kpi_values) > 1 else (0.0 if kpi_values else None)
    p10 = _percentile(kpi_values, 0.10)
    p90 = _percentile(kpi_values, 0.90)
    cv = (std / mean) if mean and std is not None and mean != 0 else None
    if cv is not None and cv > cfg.warn_high_coefficient_of_variation:
        issues.append(
            PowerMdeIssue(
                "high_coefficient_of_variation",
                f"Coefficient of variation {cv:.3f} exceeds warn threshold {cfg.warn_high_coefficient_of_variation}",
                IssueSeverity.WARNING,
                cols.kpi,
            )
        )

    if geo_period_counts:
        counts = list(geo_period_counts.values())
        time_balance_status = "balanced" if len(set(counts)) == 1 else "imbalanced"
    else:
        time_balance_status = "unknown"

    if period_geo_counts:
        counts = list(period_geo_counts.values())
        geo_balance_status = "balanced" if len(set(counts)) == 1 else "imbalanced"
    else:
        geo_balance_status = "unknown"

    outlier_summary = "none_detected"
    if len(kpi_values) >= 4:
        q1 = _percentile(kpi_values, 0.25)
        q3 = _percentile(kpi_values, 0.75)
        if q1 is not None and q3 is not None:
            iqr = q3 - q1
            lower = q1 - cfg.outlier_iqr_multiplier * iqr
            upper = q3 + cfg.outlier_iqr_multiplier * iqr
            outliers = [v for v in kpi_values if v < lower or v > upper]
            if outliers:
                outlier_summary = f"{len(outliers)}_outliers_detected_iqr_{cfg.outlier_iqr_multiplier}"

    blocking = any(i.severity == IssueSeverity.BLOCKING for i in issues)
    kpi_history_valid = bool(kpi_values) and not blocking

    return PowerMdeNoiseHistoryReport(
        row_count=row_count,
        geo_count=geo_count,
        time_period_count=time_period_count,
        missing_kpi_count=missing_kpi,
        zero_kpi_count=zero_kpi,
        negative_kpi_count=negative_kpi,
        baseline_kpi_mean=mean,
        baseline_kpi_median=median,
        baseline_kpi_std=std,
        baseline_kpi_variance=variance,
        baseline_kpi_p10=p10,
        baseline_kpi_p90=p90,
        coefficient_of_variation=cv,
        minimum_pre_period_length_met=minimum_pre_period_length_met,
        time_balance_status=time_balance_status,
        geo_balance_status=geo_balance_status,
        outlier_summary=outlier_summary,
        kpi_history_valid=kpi_history_valid,
        issues=tuple(issues),
    )


def _resolve_mde_scope(cfg: PowerMdeDiagnosticsConfig) -> MdeScope:
    raw = cfg.mde_scope
    if raw is None:
        return MdeScope.UNKNOWN
    if isinstance(raw, MdeScope):
        return raw
    try:
        return MdeScope(str(raw).upper())
    except ValueError:
        return MdeScope.UNKNOWN


def _build_mde_representation(cfg: PowerMdeDiagnosticsConfig) -> PowerMdeRepresentationReport:
    issues: list[PowerMdeIssue] = []
    absolute = cfg.absolute_mde is not None or cfg.kpi_mde is not None
    relative = cfg.relative_mde is not None
    absolute_val = cfg.absolute_mde if cfg.absolute_mde is not None else cfg.kpi_mde
    relative_val = cfg.relative_mde
    scope = _resolve_mde_scope(cfg)

    absolute_relative_conflict = False
    if absolute_val is not None and relative_val is not None:
        absolute_relative_conflict = True
        issues.append(
            PowerMdeIssue(
                "absolute_relative_mde_conflict",
                "Both absolute and relative MDE targets supplied; must not be silently mixed",
                IssueSeverity.WARNING,
                "mde",
            )
        )

    cell_vs_aggregate_conflict = False
    if scope == MdeScope.UNKNOWN and absolute and relative:
        cell_vs_aggregate_conflict = True
    if absolute_val is not None and scope == MdeScope.UNKNOWN:
        issues.append(
            PowerMdeIssue(
                "mde_scope_unknown",
                "MDE target present but mde_scope is UNKNOWN",
                IssueSeverity.WARNING,
                "mde_scope",
            )
        )

    baseline_present = cfg.baseline_kpi_level is not None
    if relative and not baseline_present:
        issues.append(
            PowerMdeIssue(
                "relative_mde_without_baseline",
                "Relative MDE present without baseline_kpi_level",
                IssueSeverity.WARNING,
                "baseline_kpi_level",
            )
        )

    duration_specific = cfg.test_duration is not None and (absolute or relative)

    return PowerMdeRepresentationReport(
        kpi_unit_preserved=cfg.kpi_unit is not None,
        kpi_unit=cfg.kpi_unit,
        absolute_mde_present=absolute,
        relative_mde_present=relative,
        absolute_relative_conflict=absolute_relative_conflict,
        mde_scope=scope,
        cell_vs_aggregate_conflict=cell_vs_aggregate_conflict,
        baseline_kpi_level_present=baseline_present,
        duration_specific_mde_present=duration_specific,
        issues=tuple(issues),
    )


def _build_cell_structure(rows: list[dict[str, Any]], cfg: PowerMdeDiagnosticsConfig) -> PowerMdeCellStructureReport:
    cols = cfg.columns
    issues: list[PowerMdeIssue] = []
    cell_ids: set[str] = set()
    roles: dict[str, str] = {}
    for row in rows:
        cid = row.get(cols.cell_id)
        role = row.get(cols.cell_role)
        if not _is_missing(cid):
            cell_ids.add(str(cid))
        if not _is_missing(cid) and not _is_missing(role):
            roles[str(cid)] = str(role)

    cell_ids_present = bool(cell_ids)
    cell_roles_present = bool(roles)
    design_type_present = cfg.design_type is not None or any(
        not _is_missing(row.get(cols.design_type)) for row in rows
    )

    treated_cells = {c for c, r in roles.items() if _is_treated_role(r)}
    control_cells = {c for c, r in roles.items() if _is_control_role(r)}
    cell_count = len(cell_ids) if cell_ids else len(set(roles.keys()))
    treated_count = len(treated_cells)
    control_count = len(control_cells)
    multi_cell = cell_count > 2 or (treated_count > 1 and control_count >= 1)
    common_control = treated_count > 1 and control_count == 1
    matched_pair = cell_count == 2 and treated_count == 1 and control_count == 1

    dosage_design = cfg.dosage_contrast_estimand_required or (
        cfg.design_type is not None and "dosage" in cfg.design_type.lower()
    ) or any("dosage" in str(row.get(cols.design_type, "")).lower() for row in rows)
    diff_policy = cfg.difference_in_policy_required or (
        cfg.design_type is not None and "difference" in cfg.design_type.lower()
    ) or any("difference" in str(row.get(cols.design_type, "")).lower() for row in rows)
    budget_realloc = cfg.design_type is not None and "budget" in cfg.design_type.lower()

    if dosage_design:
        inferred = DesignType.DOSAGE_CONTRAST
    elif diff_policy:
        inferred = DesignType.DIFFERENCE_IN_POLICY
    elif budget_realloc:
        inferred = DesignType.BUDGET_REALLOCATION
    elif matched_pair:
        inferred = DesignType.MATCHED_PAIR
    elif common_control:
        inferred = DesignType.COMMON_CONTROL
    elif multi_cell:
        inferred = DesignType.MULTI_CELL
    elif treated_count == 1 and control_count >= 1:
        inferred = DesignType.SINGLE_TREATED_VS_CONTROL
    else:
        inferred = DesignType.UNKNOWN

    if not cell_ids_present:
        cell_structure_status = "missing"
        issues.append(
            PowerMdeIssue(
                "cell_structure_missing",
                "Candidate cell structure not supplied",
                IssueSeverity.WARNING,
                cols.cell_id,
            )
        )
    elif not cell_roles_present:
        cell_structure_status = "partial"
        issues.append(
            PowerMdeIssue(
                "cell_roles_missing",
                "Cell IDs present but cell roles are missing or incomplete",
                IssueSeverity.WARNING,
                cols.cell_role,
            )
        )
    else:
        cell_structure_status = "present"

    return PowerMdeCellStructureReport(
        cell_ids_present=cell_ids_present,
        cell_roles_present=cell_roles_present,
        design_type_present=design_type_present,
        cell_count=cell_count,
        treated_cell_count=treated_count,
        control_cell_count=control_count,
        common_control_detected=common_control,
        multi_cell_detected=multi_cell,
        dosage_design_detected=dosage_design,
        difference_in_policy_detected=diff_policy,
        inferred_design_type=inferred,
        cell_structure_status=cell_structure_status,
        issues=tuple(issues),
    )


def _build_spend_compatibility(cfg: PowerMdeDiagnosticsConfig, noise: PowerMdeNoiseHistoryReport) -> PowerMdeSpendCompatibilityReport:
    issues: list[PowerMdeIssue] = []
    handoff = _status_token(cfg.spend_handoff_status)
    spend_confirmed_allowed = False

    if _is_blocked_spend_handoff(handoff):
        issues.append(
            PowerMdeIssue(
                "spend_handoff_blocked",
                f"Spend handoff status {handoff} blocks spend-confirmed sensitivity",
                IssueSeverity.BLOCKING,
                "spend_handoff_status",
            )
        )
    elif _is_ready_spend_handoff(handoff) and noise.kpi_history_valid:
        spend_confirmed_allowed = True
        if cfg.required_spend_delta is None:
            issues.append(
                PowerMdeIssue(
                    "required_spend_delta_missing",
                    "Spend handoff ready but required_spend_delta is missing",
                    IssueSeverity.WARNING,
                    "required_spend_delta",
                )
            )
    elif handoff is None and cfg.allow_kpi_only_when_spend_handoff_missing:
        issues.append(
            PowerMdeIssue(
                "spend_handoff_missing",
                "Spend handoff status missing; KPI-only mode may apply",
                IssueSeverity.INFO,
                "spend_handoff_status",
            )
        )
    elif _is_provisional_spend_handoff(handoff):
        issues.append(
            PowerMdeIssue(
                "spend_handoff_provisional",
                f"Spend handoff status {handoff} is provisional; spend-confirmed mode not allowed",
                IssueSeverity.WARNING,
                "spend_handoff_status",
            )
        )

    if cfg.required_spend_delta_source in (None, "", "REQUIRED_SPEND_DELTA_UNKNOWN", "UNKNOWN"):
        if spend_confirmed_allowed:
            spend_confirmed_allowed = False
            issues.append(
                PowerMdeIssue(
                    "required_spend_delta_unknown",
                    "Required spend delta source unknown; spend-confirmed mode blocked",
                    IssueSeverity.BLOCKING,
                    "required_spend_delta_source",
                )
            )

    return PowerMdeSpendCompatibilityReport(
        spend_handoff_status=handoff,
        required_spend_delta=cfg.required_spend_delta,
        required_spend_delta_source=cfg.required_spend_delta_source,
        response_bridge_source=cfg.response_bridge_source,
        business_response_risk=cfg.business_response_risk,
        candidate_manipulation_options=cfg.candidate_manipulation_options,
        mmm_advisory_used=cfg.mmm_advisory_used,
        proxy_response_used=cfg.proxy_response_used,
        back_of_napkin_assumption_used=cfg.back_of_napkin_assumption_used,
        control_contamination_flags=cfg.control_contamination_flags,
        ready_for_downstream_power_diagnostics=cfg.ready_for_downstream_power_diagnostics,
        spend_confirmed_mode_allowed=spend_confirmed_allowed,
        issues=tuple(issues),
    )


def _build_estimand_compatibility(
    cfg: PowerMdeDiagnosticsConfig,
    cell: PowerMdeCellStructureReport,
    mode: PowerMdeMode,
) -> PowerMdeEstimandCompatibilityReport:
    issues: list[PowerMdeIssue] = []
    contamination = bool(cfg.control_contamination_flags)
    dosage = cfg.dosage_contrast_estimand_required or cell.dosage_design_detected
    diff_policy = cfg.difference_in_policy_required or cell.difference_in_policy_detected
    blocked_go_dark = contamination or dosage or diff_policy or cfg.method_suitability_review_required

    if contamination:
        issues.append(
            PowerMdeIssue(
                "control_contamination_present",
                "Control contamination flags present; standard go-dark interpretation not allowed",
                IssueSeverity.WARNING,
                "control_contamination_flags",
            )
        )
    if dosage or diff_policy:
        issues.append(
            PowerMdeIssue(
                "dosage_or_difference_in_policy_estimand",
                "Dosage or difference-in-policy estimand required",
                IssueSeverity.INFO,
                "estimand",
            )
        )
    if cfg.method_suitability_review_required:
        issues.append(
            PowerMdeIssue(
                "method_suitability_review_required",
                "Method suitability review required before estimator/inference claims",
                IssueSeverity.WARNING,
                "method_suitability_review_required",
            )
        )

    return PowerMdeEstimandCompatibilityReport(
        standard_go_dark_interpretation_allowed=not blocked_go_dark,
        dosage_contrast_estimand_required=dosage,
        difference_in_policy_required=diff_policy,
        control_contamination_present=contamination,
        business_as_usual_control_preserved=not contamination,
        method_suitability_review_required=cfg.method_suitability_review_required,
        allowed_runtime_mode=mode,
        blocked_standard_go_dark_interpretation=blocked_go_dark,
        issues=tuple(issues),
    )


def _gate_from_status(status: str | None, *, missing_ok: bool = False) -> GateStatus:
    if status is None:
        return GateStatus.NOT_EVALUATED if missing_ok else GateStatus.PROVISIONAL
    if _is_blocked_status(status):
        return GateStatus.BLOCKED
    upper = status.upper()
    if "WARNING" in upper or upper == ProfilerStatus.PASS_WITH_WARNINGS.value:
        return GateStatus.WARNING
    if "PROVISIONAL" in upper:
        return GateStatus.PROVISIONAL
    if upper in {ProfilerStatus.PASS.value, "PASS", "READY"} or "READY" in upper:
        return GateStatus.PASS
    return GateStatus.NOT_EVALUATED


def _build_readiness(
    cfg: PowerMdeDiagnosticsConfig,
    noise: PowerMdeNoiseHistoryReport,
    mde: PowerMdeRepresentationReport,
    cell: PowerMdeCellStructureReport,
    spend: PowerMdeSpendCompatibilityReport,
) -> PowerMdeReadinessReport:
    profiler_gate = _gate_from_status(_status_token(cfg.profiler_status), missing_ok=True)
    geo_gate = _gate_from_status(_status_token(cfg.geo_feasibility_status), missing_ok=True)
    spend_gate = GateStatus.BLOCKED if _is_blocked_spend_handoff(spend.spend_handoff_status) else (
        GateStatus.PASS if spend.spend_confirmed_mode_allowed else (
            GateStatus.PROVISIONAL if spend.spend_handoff_status is None else GateStatus.WARNING
        )
    )
    if cell.cell_structure_status == "missing":
        cell_gate = GateStatus.PROVISIONAL if cfg.allow_kpi_only_when_spend_handoff_missing else GateStatus.BLOCKED
    elif cell.cell_structure_status == "partial":
        cell_gate = GateStatus.WARNING
    else:
        cell_gate = GateStatus.PASS

    has_mde_target = mde.absolute_mde_present or mde.relative_mde_present
    kpi_mde_gate = GateStatus.PASS if has_mde_target else GateStatus.PROVISIONAL

    noise_gate = GateStatus.PASS if noise.kpi_history_valid else GateStatus.BLOCKED

    estimand_gate = GateStatus.BLOCKED if mde.absolute_relative_conflict else GateStatus.PASS
    if cfg.dosage_contrast_estimand_required and not cell.dosage_design_detected and cell.cell_structure_status == "missing":
        estimand_gate = GateStatus.WARNING

    method_gate = (
        GateStatus.WARNING if cfg.method_suitability_review_required else GateStatus.PASS
    )

    gates = (
        profiler_gate,
        geo_gate,
        spend_gate,
        cell_gate,
        kpi_mde_gate,
        noise_gate,
        estimand_gate,
        method_gate,
    )
    all_passed = all(g in {GateStatus.PASS, GateStatus.WARNING, GateStatus.PROVISIONAL} for g in gates) and noise_gate != GateStatus.BLOCKED

    notes: list[str] = []
    if profiler_gate == GateStatus.BLOCKED:
        notes.append("profiler_gate_blocked")
    if geo_gate == GateStatus.BLOCKED:
        notes.append("geo_feasibility_gate_blocked")
    if noise_gate == GateStatus.BLOCKED:
        notes.append("noise_history_gate_blocked")

    return PowerMdeReadinessReport(
        profiler_gate=profiler_gate,
        geo_unit_market_feasibility_gate=geo_gate,
        spend_handoff_gate=spend_gate,
        cell_structure_gate=cell_gate,
        kpi_mde_target_gate=kpi_mde_gate,
        noise_history_gate=noise_gate,
        estimand_compatibility_gate=estimand_gate,
        method_suitability_precheck_gate=method_gate,
        all_gates_passed=all_passed,
        notes=tuple(notes),
    )


def _select_mode(
    cfg: PowerMdeDiagnosticsConfig,
    noise: PowerMdeNoiseHistoryReport,
    cell: PowerMdeCellStructureReport,
    spend: PowerMdeSpendCompatibilityReport,
    readiness: PowerMdeReadinessReport,
) -> PowerMdeMode:
    if readiness.profiler_gate == GateStatus.BLOCKED or readiness.noise_history_gate == GateStatus.BLOCKED:
        return PowerMdeMode.NOT_EVALUATED
    if readiness.geo_unit_market_feasibility_gate == GateStatus.BLOCKED:
        return PowerMdeMode.NOT_EVALUATED

    if cfg.back_of_napkin_assumption_used and cfg.allow_exploratory_back_of_napkin:
        return PowerMdeMode.EXPLORATORY_BACK_OF_NAPKIN

    if cfg.dosage_contrast_estimand_required or cfg.difference_in_policy_required or cell.dosage_design_detected:
        if noise.kpi_history_valid:
            return PowerMdeMode.DOSAGE_CONTRAST_SENSITIVITY

    if (
        cell.cell_structure_status == "present"
        and cell.cell_roles_present
        and not _is_blocked_spend_handoff(spend.spend_handoff_status)
    ):
        return PowerMdeMode.DESIGN_CELL_SENSITIVITY

    if spend.spend_confirmed_mode_allowed:
        return PowerMdeMode.SPEND_CONFIRMED_SENSITIVITY

    if noise.kpi_history_valid and (
        spend.spend_handoff_status is None
        or _is_provisional_spend_handoff(spend.spend_handoff_status)
        or cfg.allow_kpi_only_when_spend_handoff_missing
    ):
        return PowerMdeMode.KPI_ONLY_SENSITIVITY

    return PowerMdeMode.NOT_EVALUATED


def _aggregate_status(
    cfg: PowerMdeDiagnosticsConfig,
    mode: PowerMdeMode,
    readiness: PowerMdeReadinessReport,
    cell: PowerMdeCellStructureReport,
    spend: PowerMdeSpendCompatibilityReport,
    all_issues: tuple[PowerMdeIssue, ...],
) -> PowerMdeStatus:
    if readiness.profiler_gate == GateStatus.BLOCKED or readiness.noise_history_gate == GateStatus.BLOCKED:
        return PowerMdeStatus.POWER_MDE_BLOCKED_BY_DATA_READINESS
    if readiness.geo_unit_market_feasibility_gate == GateStatus.BLOCKED:
        return PowerMdeStatus.POWER_MDE_BLOCKED_BY_GEO_FEASIBILITY
    if mode == PowerMdeMode.NOT_EVALUATED:
        if _is_blocked_spend_handoff(spend.spend_handoff_status):
            return PowerMdeStatus.POWER_MDE_BLOCKED_BY_SPEND_HANDOFF
        return PowerMdeStatus.POWER_MDE_NOT_EVALUATED
    if cfg.method_suitability_review_required:
        return PowerMdeStatus.POWER_MDE_REQUIRES_METHOD_SUITABILITY_REVIEW
    if readiness.estimand_compatibility_gate == GateStatus.BLOCKED:
        return PowerMdeStatus.POWER_MDE_BLOCKED_BY_ESTIMAND_MISMATCH
    if (
        mode == PowerMdeMode.DESIGN_CELL_SENSITIVITY
        and cfg.require_cell_structure_for_design_mode
        and cell.cell_structure_status != "present"
    ):
        return PowerMdeStatus.POWER_MDE_BLOCKED_BY_CELL_STRUCTURE
    if mode == PowerMdeMode.EXPLORATORY_BACK_OF_NAPKIN:
        return PowerMdeStatus.POWER_MDE_PROVISIONAL
    if cell.cell_structure_status == "missing" and mode == PowerMdeMode.KPI_ONLY_SENSITIVITY:
        return PowerMdeStatus.POWER_MDE_PROVISIONAL
    if any(i.severity == IssueSeverity.WARNING for i in all_issues):
        return PowerMdeStatus.POWER_MDE_READY_WITH_WARNINGS
    return PowerMdeStatus.POWER_MDE_READY_FOR_DIAGNOSTIC_RUNTIME


def evaluate_power_mde_diagnostics(
    input_data: PowerMdeDiagnosticsInput | list[dict[str, Any]] | GeoKpiSpendProfilerInput | Any,
    config: PowerMdeDiagnosticsConfig | None = None,
) -> PowerMdeDiagnosticsReport:
    """Evaluate conservative power/MDE readiness diagnostics. Side-effect free.

    POWER_MDE_READY_FOR_DIAGNOSTIC_RUNTIME does not mean powered.
    It only means this conservative runtime has enough validated inputs for the allowed diagnostic mode.
    """
    rows, cfg = _normalize_input(input_data, config)
    noise = _build_noise_history(rows, cfg)
    mde = _build_mde_representation(cfg)
    cell = _build_cell_structure(rows, cfg)
    spend = _build_spend_compatibility(cfg, noise)
    readiness = _build_readiness(cfg, noise, mde, cell, spend)
    mode = _select_mode(cfg, noise, cell, spend, readiness)

    estimand = _build_estimand_compatibility(cfg, cell, mode)

    all_issues = (
        *noise.issues,
        *mde.issues,
        *cell.issues,
        *spend.issues,
        *estimand.issues,
    )
    status = _aggregate_status(cfg, mode, readiness, cell, spend, all_issues)
    warnings = tuple(i.message for i in all_issues if i.severity == IssueSeverity.WARNING)
    blocking_reasons = tuple(i.message for i in all_issues if i.severity == IssueSeverity.BLOCKING)

    if status in {
        PowerMdeStatus.POWER_MDE_BLOCKED_BY_DATA_READINESS,
        PowerMdeStatus.POWER_MDE_BLOCKED_BY_GEO_FEASIBILITY,
        PowerMdeStatus.POWER_MDE_BLOCKED_BY_SPEND_HANDOFF,
    }:
        mode = PowerMdeMode.NOT_EVALUATED

    claim = PowerMdeClaimBoundaryReport()

    return PowerMdeDiagnosticsReport(
        artifact_id=_ARTIFACT_ID,
        status=status,
        mode=mode,
        final_verdict=_VERDICT,
        readiness_report=readiness,
        noise_history_report=noise,
        mde_representation_report=mde,
        cell_structure_report=cell,
        spend_compatibility_report=spend,
        estimand_compatibility_report=estimand,
        claim_boundary_report=claim,
        issues=all_issues,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
    )


evaluate_power_mde_readiness = evaluate_power_mde_diagnostics


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    weeks = (
        "2025-01-01", "2025-01-08", "2025-01-15", "2025-01-22",
        "2025-01-29", "2025-02-05", "2025-02-12", "2025-02-19",
    )
    rows = [
        {
            "geo_unit_id": f"DMA_{i:03d}",
            "date": w,
            "kpi_value": 100.0 + i,
            "cell_id": "cell_a" if i <= 2 else "cell_b",
            "cell_role": "treated" if i <= 2 else "control",
        }
        for i in range(1, 6)
        for w in weeks
    ]
    report = evaluate_power_mde_diagnostics(
        rows,
        PowerMdeDiagnosticsConfig(
            profiler_status=ProfilerStatus.PASS.value,
            geo_feasibility_status="PASS",
            spend_handoff_status="SPEND_HANDOFF_READY_FOR_POWER_DIAGNOSTICS",
            required_spend_delta=500.0,
            required_spend_delta_source="REQUIRED_SPEND_DELTA_SUPPLIED",
            kpi_unit="conversions",
            absolute_mde=500.0,
            mde_scope=MdeScope.CELL_LEVEL,
            ready_for_downstream_power_diagnostics=True,
        ),
    )
    failed: list[str] = []
    if report.status not in {
        PowerMdeStatus.POWER_MDE_READY_FOR_DIAGNOSTIC_RUNTIME,
        PowerMdeStatus.POWER_MDE_READY_WITH_WARNINGS,
        PowerMdeStatus.POWER_MDE_REQUIRES_METHOD_SUITABILITY_REVIEW,
    }:
        failed.append("smoke_status")
    if report.claim_boundary_report.power_computed:
        failed.append("smoke_no_power_computed")
    if report.claim_boundary_report.mde_computed:
        failed.append("smoke_no_mde_computed")

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "power_mde_diagnostics_runtime",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": "runtime_readiness_and_descriptive_sensitivity_only",
        "depends_on": [
            "GEO_KPI_SPEND_DATA_PROFILER_001",
            "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
            "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
            "POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001",
            "POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001",
        ],
        "public_api": "evaluate_power_mde_diagnostics",
        "runtime_power_mde_diagnostics_implemented": True,
        "readiness_diagnostics_implemented": True,
        "descriptive_noise_summary_implemented": True,
        "mde_representation_validation_implemented": True,
        "cell_structure_validation_implemented": True,
        "spend_compatibility_validation_implemented": True,
        "estimand_compatibility_validation_implemented": True,
        "runtime_modes_supported": [m.value for m in PowerMdeMode],
        "runtime_statuses_supported": [s.value for s in PowerMdeStatus],
        "kpi_history_readiness_implemented": True,
        "minimum_pre_period_check_implemented": True,
        "absolute_relative_mde_separation_implemented": True,
        "cell_aggregate_mde_separation_implemented": True,
        "response_bridge_provenance_preserved": True,
        "business_response_risk_preserved": True,
        "dosage_sensitivity_mode_implemented": True,
        "control_contamination_preserved": True,
        "method_suitability_review_required_preserved": True,
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
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "failed_scenarios": failed,
        "smoke_status": report.status.value,
        "smoke_mode": report.mode.value,
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
