"""SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001 deterministic diagnostics."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from panel_exp.validation.geo_kpi_spend_data_profiler_001 import (
    GeoKpiSpendDataProfileReport,
    GeoKpiSpendProfilerConfig,
    GeoKpiSpendProfilerInput,
    InputMode,
    ProfilerStatus,
    profile_geo_kpi_spend_data,
)

_ARTIFACT_ID = "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "spend_requirement_and_manipulation_feasibility_diagnostics_implemented_no_power_design_roi_or_production_authorization"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001_summary.json"
)
RECOMMENDED_NEXT_ARTIFACT = "POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001"


class ManipulationOption(str, Enum):
    GO_DARK = "GO_DARK"
    HEAVY_UP = "HEAVY_UP"
    GO_LIVE = "GO_LIVE"
    BUDGET_REALLOCATION = "BUDGET_REALLOCATION"
    DOSAGE_CONTRAST = "DOSAGE_CONTRAST"
    DIFFERENCE_IN_POLICY = "DIFFERENCE_IN_POLICY"
    UNKNOWN = "UNKNOWN"


class ResponseBridgeSource(str, Enum):
    NONE = "NONE"
    USER_PROVIDED_REQUIRED_SPEND_DELTA = "USER_PROVIDED_REQUIRED_SPEND_DELTA"
    POWER_LAYER_REQUIRED_SPEND_DELTA = "POWER_LAYER_REQUIRED_SPEND_DELTA"
    MMM_RESPONSE_CURVE = "MMM_RESPONSE_CURVE"
    MMM_ROMS = "MMM_ROMS"
    PRIOR_EXPERIMENT = "PRIOR_EXPERIMENT"
    PROXY_RESPONSE_CURVE = "PROXY_RESPONSE_CURVE"
    BACK_OF_NAPKIN_USER_ASSUMPTION = "BACK_OF_NAPKIN_USER_ASSUMPTION"


class ResponseBridgeStatus(str, Enum):
    REQUIRED_SPEND_DELTA_SUPPLIED = "REQUIRED_SPEND_DELTA_SUPPLIED"
    REQUIRED_SPEND_DELTA_ESTIMATED_ADVISORY = "REQUIRED_SPEND_DELTA_ESTIMATED_ADVISORY"
    REQUIRED_SPEND_DELTA_UNKNOWN = "REQUIRED_SPEND_DELTA_UNKNOWN"
    OUT_OF_SUPPORT = "OUT_OF_SUPPORT"
    BLOCKED_MISSING_RESPONSE_BRIDGE = "BLOCKED_MISSING_RESPONSE_BRIDGE"


class HistoricalSupportStatus(str, Enum):
    WITHIN_HISTORICAL_SUPPORT = "WITHIN_HISTORICAL_SUPPORT"
    NEAR_UPPER_HISTORICAL_SUPPORT = "NEAR_UPPER_HISTORICAL_SUPPORT"
    ABOVE_HISTORICAL_SUPPORT = "ABOVE_HISTORICAL_SUPPORT"
    FAR_ABOVE_HISTORICAL_SUPPORT = "FAR_ABOVE_HISTORICAL_SUPPORT"
    UNKNOWN_HISTORICAL_SUPPORT = "UNKNOWN_HISTORICAL_SUPPORT"


class FeasibilityStatus(str, Enum):
    READY_FOR_DOWNSTREAM_POWER_DIAGNOSTICS = "READY_FOR_DOWNSTREAM_POWER_DIAGNOSTICS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    PROVISIONAL = "PROVISIONAL"
    BLOCKED = "BLOCKED"
    NOT_EVALUATED = "NOT_EVALUATED"


class ManipulationFeasibilityOutcome(str, Enum):
    GO_DARK_FEASIBLE = "GO_DARK_FEASIBLE"
    GO_DARK_INSUFFICIENT_BASELINE_SPEND = "GO_DARK_INSUFFICIENT_BASELINE_SPEND"
    HEAVY_UP_FEASIBLE = "HEAVY_UP_FEASIBLE"
    HEAVY_UP_OUT_OF_HISTORICAL_SUPPORT = "HEAVY_UP_OUT_OF_HISTORICAL_SUPPORT"
    HEAVY_UP_MULTIPLIER_HIGH = "HEAVY_UP_MULTIPLIER_HIGH"
    GO_LIVE_FEASIBLE = "GO_LIVE_FEASIBLE"
    GO_LIVE_CONFLICTS_WITH_EXISTING_BASELINE_SPEND = "GO_LIVE_CONFLICTS_WITH_EXISTING_BASELINE_SPEND"
    BUDGET_REALLOCATION_FEASIBLE = "BUDGET_REALLOCATION_FEASIBLE"
    BUDGET_REALLOCATION_MAPPING_INCOMPLETE = "BUDGET_REALLOCATION_MAPPING_INCOMPLETE"
    DOSAGE_CONTRAST_FEASIBLE = "DOSAGE_CONTRAST_FEASIBLE"
    DOSAGE_CONTRAST_ESTIMAND_REQUIRED = "DOSAGE_CONTRAST_ESTIMAND_REQUIRED"
    INSUFFICIENT_CONTRAST = "INSUFFICIENT_CONTRAST"
    BLOCKED_MISSING_SPEND = "BLOCKED_MISSING_SPEND"
    PROVISIONAL_REQUIRED_SPEND_UNKNOWN = "PROVISIONAL_REQUIRED_SPEND_UNKNOWN"


class AdvisoryFlag(str, Enum):
    MMM_ADVISORY_SIGNAL_USED = "MMM_ADVISORY_SIGNAL_USED"
    MMM_OUT_OF_SUPPORT = "MMM_OUT_OF_SUPPORT"
    OUT_OF_MMM_SUPPORT = "OUT_OF_MMM_SUPPORT"
    MMM_CALIBRATION_WEAK = "MMM_CALIBRATION_WEAK"
    PROXY_RESPONSE_USED = "PROXY_RESPONSE_USED"
    PROXY_LEVEL_MISMATCH = "PROXY_LEVEL_MISMATCH"
    BACK_OF_NAPKIN_ASSUMPTION_USED = "BACK_OF_NAPKIN_ASSUMPTION_USED"
    BUSINESS_RESPONSE_RISK = "BUSINESS_RESPONSE_RISK"
    REQUIRED_SPEND_DELTA_UNKNOWN = "REQUIRED_SPEND_DELTA_UNKNOWN"
    REQUIRED_SPEND_DELTA_ESTIMATED_ADVISORY = "REQUIRED_SPEND_DELTA_ESTIMATED_ADVISORY"
    REQUIRED_SPEND_DELTA_SUPPLIED = "REQUIRED_SPEND_DELTA_SUPPLIED"
    CONTROL_CELL_MANIPULATED = "CONTROL_CELL_MANIPULATED"
    CONTROL_CONTAMINATION_RISK = "CONTROL_CONTAMINATION_RISK"
    BUSINESS_AS_USUAL_CONTROL_NOT_PRESERVED = "BUSINESS_AS_USUAL_CONTROL_NOT_PRESERVED"
    ESTIMAND_SHIFT_REQUIRED = "ESTIMAND_SHIFT_REQUIRED"
    STANDARD_GO_DARK_INTERPRETATION_NOT_ALLOWED = "STANDARD_GO_DARK_INTERPRETATION_NOT_ALLOWED"
    METHOD_SUITABILITY_REVIEW_REQUIRED = "METHOD_SUITABILITY_REVIEW_REQUIRED"


class IssueSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"


@dataclass(frozen=True)
class SpendDiagnosticsColumnMapping:
    geo_unit_id: str = "geo_unit_id"
    date: str = "date"
    spend: str = "spend_value"
    cell_id: str = "cell_id"
    cell_role: str = "cell_role"
    channel: str = "channel"
    campaign: str = "campaign"
    platform: str = "platform"
    currency: str = "currency"
    period_role: str = "period_role"
    is_planned: str = "is_planned"
    is_observed: str = "is_observed"
    spend_source: str = "spend_source"
    source_channel: str = "source_channel"
    destination_channel: str = "destination_channel"


@dataclass(frozen=True)
class SpendRequirementManipulationFeasibilityConfig:
    columns: SpendDiagnosticsColumnMapping = field(default_factory=SpendDiagnosticsColumnMapping)
    near_upper_support_quantile: float = 0.95
    high_multiplier_warning_threshold: float = 2.0
    far_above_historical_max_multiplier: float = 1.25
    go_live_baseline_near_zero_threshold: float = 0.0
    business_response_risk_ratio_threshold: float = 1.0
    manipulation_type: ManipulationOption | None = None
    planned_test_start_date: str | None = None
    baseline_window_start: str | None = None
    baseline_window_end: str | None = None
    test_window_start: str | None = None
    test_window_end: str | None = None
    required_spend_delta: float | None = None
    kpi_mde: float | None = None
    kpi_unit: str | None = None
    available_test_budget: float | None = None
    response_bridge_source: ResponseBridgeSource = ResponseBridgeSource.NONE
    expected_kpi_per_dollar: float | None = None
    mmm_curve_support_min_spend: float | None = None
    mmm_curve_support_max_spend: float | None = None
    mmm_calibration_status: str | None = None
    proxy_level: str | None = None
    requested_test_level: str | None = None
    back_of_napkin_assumption_label: str | None = None
    advisory_expected_kpi_response: float | None = None
    low_spend_policy: float | None = None
    high_spend_policy: float | None = None
    budget_source_channel: str | None = None
    budget_destination_channel: str | None = None
    control_manipulated: bool = False
    spend_credit_flag_present: bool = False
    profile_report: GeoKpiSpendDataProfileReport | None = None
    profiler_config: GeoKpiSpendProfilerConfig | None = None


@dataclass(frozen=True)
class SpendDiagnosticsIssue:
    code: str
    message: str
    severity: IssueSeverity
    field: str | None = None


@dataclass(frozen=True)
class SpendDataReadinessReport:
    has_required_columns: bool
    spend_column_present: bool
    geo_column_present: bool
    time_column_present: bool
    valid_spend_values: int
    missing_spend_count: int
    zero_spend_count: int
    negative_spend_count: int
    duplicate_geo_time_rows: int
    grain_status: str
    planned_observed_status: str
    currency_status: str
    baseline_window_status: str
    test_window_status: str
    sample_schema_mode: bool
    ballpark_mode: bool
    issues: tuple[SpendDiagnosticsIssue, ...]


@dataclass(frozen=True)
class BaselineSpendSummary:
    level: str
    key: str | None
    baseline_mean_weekly_spend: float | None
    baseline_median_weekly_spend: float | None
    baseline_total_spend: float | None
    baseline_p10_weekly_spend: float | None
    baseline_p90_weekly_spend: float | None
    historical_p95_spend: float | None
    historical_max_spend: float | None
    nonzero_weeks: int
    missing_weeks: int
    max_reducible_spend: float | None


@dataclass(frozen=True)
class BaselineSpendInventoryReport:
    baseline_window_derived: bool
    summaries: tuple[BaselineSpendSummary, ...]
    issues: tuple[SpendDiagnosticsIssue, ...]


@dataclass(frozen=True)
class ResponseBridgeReport:
    response_bridge_source: ResponseBridgeSource
    response_bridge_status: ResponseBridgeStatus
    kpi_mde: float | None
    kpi_unit: str | None
    required_spend_delta: float | None
    statistical_required_spend_contrast: float | None
    business_response_required_spend: float | None
    expected_kpi_at_required_spend: float | None
    advisory_flags: tuple[AdvisoryFlag, ...]
    issues: tuple[SpendDiagnosticsIssue, ...]


@dataclass(frozen=True)
class ManipulationCandidate:
    manipulation_option: ManipulationOption
    outcome: ManipulationFeasibilityOutcome
    historical_support: HistoricalSupportStatus
    go_dark_max_delta: float | None = None
    required_heavy_up_spend: float | None = None
    required_heavy_up_multiplier: float | None = None
    dosage_delta: float | None = None
    budget_gap: float | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ManipulationFeasibilityReport:
    candidates: tuple[ManipulationCandidate, ...]
    advisory_flags: tuple[AdvisoryFlag, ...]
    issues: tuple[SpendDiagnosticsIssue, ...]


@dataclass(frozen=True)
class PlanningBoundaryReport:
    standard_go_dark_interpretation_allowed: bool
    dosage_contrast_estimand_required: bool
    method_suitability_review_required: bool
    business_as_usual_control_preserved: bool
    mmm_advisory_used: bool
    proxy_response_used: bool
    back_of_napkin_assumption_used: bool
    ready_for_downstream_power_diagnostics: bool = False
    final_design_recommendation_authorized: bool = False
    runtime_power_authorized: bool = False
    mde_authorized: bool = False
    p_value_authorized: bool = False
    confidence_interval_authorized: bool = False
    lift_authorized: bool = False
    roi_authorized: bool = False
    budget_optimization_authorized: bool = False
    candidate_design_authorized: bool = False
    treatment_control_assignment_authorized: bool = False
    estimator_inference_authorized: bool = False
    mmm_calibration_authorized: bool = False
    production_authorization_granted: bool = False
    llm_decisioning_authorized: bool = False


@dataclass(frozen=True)
class SpendRequirementManipulationFeasibilityReport:
    artifact_id: str
    feasibility_status: FeasibilityStatus
    spend_data_readiness: SpendDataReadinessReport
    baseline_spend_inventory: BaselineSpendInventoryReport
    response_bridge: ResponseBridgeReport
    manipulation_feasibility: ManipulationFeasibilityReport
    planning_boundary: PlanningBoundaryReport
    issues: tuple[SpendDiagnosticsIssue, ...]
    advisory_flags: tuple[AdvisoryFlag, ...]
    final_verdict: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
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


def _parse_date(value: Any) -> date | None:
    if _is_missing(value):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except ValueError:
        return None


def _normalize_rows(input_data: list[dict[str, Any]] | Any) -> list[dict[str, Any]]:
    if isinstance(input_data, list):
        return input_data
    if hasattr(input_data, "to_dict"):
        return input_data.to_dict("records")
    if isinstance(input_data, GeoKpiSpendProfilerInput):
        return list(input_data.rows or [])
    raise TypeError("input_data must be list[dict], pandas DataFrame, or GeoKpiSpendProfilerInput")


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


def _weekly_spend_totals(
    rows: list[dict[str, Any]],
    cfg: SpendRequirementManipulationFeasibilityConfig,
    *,
    window_start: date | None = None,
    window_end: date | None = None,
    group_key: str | None = None,
    group_value: str | None = None,
) -> tuple[list[float], int]:
    cols = cfg.columns
    weekly: dict[str, float] = defaultdict(float)
    missing_weeks = 0
    seen_weeks: set[str] = set()

    for row in rows:
        if group_key and str(row.get(group_key, "")) != group_value:
            continue
        dt = _parse_date(row.get(cols.date))
        if dt is None:
            continue
        if window_start and dt < window_start:
            continue
        if window_end and dt > window_end:
            continue
        week_key = dt.isoformat()
        seen_weeks.add(week_key)
        spend = _to_float(row.get(cols.spend))
        if spend is None:
            missing_weeks += 1
            continue
        weekly[week_key] += spend

    return list(weekly.values()), missing_weeks


def _summarize_weekly(level: str, key: str | None, weekly: list[float], missing_weeks: int) -> BaselineSpendSummary:
    if not weekly:
        return BaselineSpendSummary(level, key, None, None, None, None, None, None, None, 0, missing_weeks, None)
    mean_w = statistics.mean(weekly)
    median_w = statistics.median(weekly)
    total = sum(weekly)
    p10 = _percentile(weekly, 0.10)
    p90 = _percentile(weekly, 0.90)
    p95 = _percentile(weekly, 0.95)
    max_s = max(weekly)
    nonzero = sum(1 for v in weekly if v > 0)
    max_reducible = max(mean_w, 0.0)
    return BaselineSpendSummary(
        level=level,
        key=key,
        baseline_mean_weekly_spend=mean_w,
        baseline_median_weekly_spend=median_w,
        baseline_total_spend=total,
        baseline_p10_weekly_spend=p10,
        baseline_p90_weekly_spend=p90,
        historical_p95_spend=p95,
        historical_max_spend=max_s,
        nonzero_weeks=nonzero,
        missing_weeks=missing_weeks,
        max_reducible_spend=max_reducible,
    )


def _derive_baseline_window(
    rows: list[dict[str, Any]], cfg: SpendRequirementManipulationFeasibilityConfig
) -> tuple[date | None, date | None, str]:
    if cfg.baseline_window_start and cfg.baseline_window_end:
        start = _parse_date(cfg.baseline_window_start)
        end = _parse_date(cfg.baseline_window_end)
        return start, end, "explicit_baseline_window"
    if cfg.planned_test_start_date:
        planned = _parse_date(cfg.planned_test_start_date)
        if planned:
            dates = [_parse_date(r.get(cfg.columns.date)) for r in rows]
            dates = [d for d in dates if d and d < planned]
            if dates:
                return min(dates), max(dates), "pre_period_before_planned_test_start"
    dates = [_parse_date(r.get(cfg.columns.date)) for r in rows]
    dates = [d for d in dates if d]
    if dates:
        return min(dates), max(dates), "full_observed_range"
    return None, None, "missing_baseline_window"


def _build_readiness(
    rows: list[dict[str, Any]],
    profile: GeoKpiSpendDataProfileReport,
    cfg: SpendRequirementManipulationFeasibilityConfig,
) -> SpendDataReadinessReport:
    cols = cfg.columns
    issues: list[SpendDiagnosticsIssue] = []
    spend_col = cols.spend
    geo_col = cols.geo_unit_id
    date_col = cols.date

    missing_spend = zero_spend = negative_spend = valid_spend = 0
    has_planned = has_observed = False
    mixed_planned_observed = False
    currencies: set[str] = set()
    geo_time_pairs: list[tuple[str, str]] = []

    for row in rows:
        geo_time_pairs.append((str(row.get(geo_col, "")), str(row.get(date_col, ""))))
        spend = _to_float(row.get(spend_col))
        if spend is None:
            missing_spend += 1
        else:
            valid_spend += 1
            if spend == 0:
                zero_spend += 1
            elif spend < 0:
                negative_spend += 1
        planned_flag = row.get(cols.is_planned)
        observed_flag = row.get(cols.is_observed)
        role = str(row.get(cols.period_role, "")).lower()
        if planned_flag is True or role == "planned":
            has_planned = True
        if observed_flag is True or role in {"observed", "actual", "baseline", "treatment", "post"}:
            has_observed = True
        if not _is_missing(row.get(cols.currency)):
            currencies.add(str(row.get(cols.currency)))

    dup_count = sum(1 for _, c in Counter(geo_time_pairs).items() if c > 1)
    if has_planned and has_observed:
        mixed_planned_observed = True
        issues.append(
            SpendDiagnosticsIssue(
                "planned_observed_mixed",
                "Planned and observed spend labels both present; do not silently mix",
                IssueSeverity.WARNING,
            )
        )
    if negative_spend > 0 and not cfg.spend_credit_flag_present:
        issues.append(
            SpendDiagnosticsIssue(
                "negative_spend_without_credit_flag",
                f"{negative_spend} negative spend values without correction/credit flag",
                IssueSeverity.WARNING if negative_spend < valid_spend else IssueSeverity.BLOCKING,
            )
        )
    if missing_spend > 0:
        issues.append(
            SpendDiagnosticsIssue(
                "missing_spend_present",
                f"{missing_spend} missing spend values; missing is not zero",
                IssueSeverity.WARNING,
            )
        )

    _, _, baseline_status = _derive_baseline_window(rows, cfg)
    test_status = "explicit" if cfg.test_window_start else "not_specified"
    currency_status = "single" if len(currencies) <= 1 else "mixed_currency"
    if len(currencies) > 1:
        issues.append(
            SpendDiagnosticsIssue("currency_mismatch", "Multiple currencies without mapping", IssueSeverity.WARNING)
        )

    input_mode = profile.input_mode_report.input_mode
    sample_schema = input_mode == InputMode.SAMPLE_SCHEMA
    ballpark = input_mode == InputMode.BALLPARK
    if sample_schema:
        issues.append(
            SpendDiagnosticsIssue(
                "sample_schema_mode",
                "Sample schema cannot produce final spend readiness",
                IssueSeverity.WARNING,
            )
        )
    if ballpark:
        issues.append(
            SpendDiagnosticsIssue("ballpark_mode", "Ballpark mode is provisional only", IssueSeverity.WARNING)
        )

    spend_present = profile.column_mapping_report.spend_present or spend_col in (rows[0] if rows else {})
    geo_present = profile.column_mapping_report.geo_present or geo_col in (rows[0] if rows else {})
    time_present = profile.column_mapping_report.date_present or date_col in (rows[0] if rows else {})

    return SpendDataReadinessReport(
        has_required_columns=bool(spend_present and geo_present and time_present),
        spend_column_present=bool(spend_present),
        geo_column_present=bool(geo_present),
        time_column_present=bool(time_present),
        valid_spend_values=valid_spend,
        missing_spend_count=missing_spend,
        zero_spend_count=zero_spend,
        negative_spend_count=negative_spend,
        duplicate_geo_time_rows=dup_count,
        grain_status=profile.time_grain_report.inferred_time_grain.value,
        planned_observed_status="mixed" if mixed_planned_observed else ("planned" if has_planned else "observed"),
        currency_status=currency_status,
        baseline_window_status=baseline_status,
        test_window_status=test_status,
        sample_schema_mode=sample_schema,
        ballpark_mode=ballpark,
        issues=tuple(issues),
    )


def _build_baseline_inventory(
    rows: list[dict[str, Any]], cfg: SpendRequirementManipulationFeasibilityConfig
) -> BaselineSpendInventoryReport:
    issues: list[SpendDiagnosticsIssue] = []
    start, end, status = _derive_baseline_window(rows, cfg)
    if start is None or end is None:
        issues.append(
            SpendDiagnosticsIssue(
                "baseline_window_missing",
                "Cannot derive baseline window",
                IssueSeverity.BLOCKING,
            )
        )
        return BaselineSpendInventoryReport(False, (), tuple(issues))

    cols = cfg.columns
    summaries: list[BaselineSpendSummary] = []
    overall_weekly, missing = _weekly_spend_totals(rows, cfg, window_start=start, window_end=end)
    summaries.append(_summarize_weekly("overall", None, overall_weekly, missing))

    geos = sorted({str(r.get(cols.geo_unit_id)) for r in rows if not _is_missing(r.get(cols.geo_unit_id))})
    for geo in geos[:20]:
        w, m = _weekly_spend_totals(rows, cfg, window_start=start, window_end=end, group_key=cols.geo_unit_id, group_value=geo)
        summaries.append(_summarize_weekly("geo", geo, w, m))

    cells = sorted({str(r.get(cols.cell_id)) for r in rows if not _is_missing(r.get(cols.cell_id))})
    for cell in cells[:20]:
        w, m = _weekly_spend_totals(rows, cfg, window_start=start, window_end=end, group_key=cols.cell_id, group_value=cell)
        summaries.append(_summarize_weekly("cell", cell, w, m))

    channels = sorted({str(r.get(cols.channel)) for r in rows if not _is_missing(r.get(cols.channel))})
    for ch in channels[:20]:
        w, m = _weekly_spend_totals(rows, cfg, window_start=start, window_end=end, group_key=cols.channel, group_value=ch)
        summaries.append(_summarize_weekly("channel", ch, w, m))

    for geo in geos[:5]:
        for ch in channels[:5]:
            weekly: dict[str, float] = defaultdict(float)
            miss = 0
            for row in rows:
                if str(row.get(cols.geo_unit_id)) != geo or str(row.get(cols.channel)) != ch:
                    continue
                dt = _parse_date(row.get(cols.date))
                if dt is None or dt < start or dt > end:
                    continue
                spend = _to_float(row.get(cols.spend))
                if spend is None:
                    miss += 1
                else:
                    weekly[dt.isoformat()] += spend
            if weekly:
                summaries.append(_summarize_weekly("geo_x_channel", f"{geo}|{ch}", list(weekly.values()), miss))

    return BaselineSpendInventoryReport(True, tuple(summaries), tuple(issues))


def _build_response_bridge(cfg: SpendRequirementManipulationFeasibilityConfig) -> ResponseBridgeReport:
    issues: list[SpendDiagnosticsIssue] = []
    flags: list[AdvisoryFlag] = []
    source = cfg.response_bridge_source
    required_delta: float | None = None
    status = ResponseBridgeStatus.REQUIRED_SPEND_DELTA_UNKNOWN
    statistical: float | None = None
    business: float | None = None
    expected_kpi: float | None = None

    if cfg.required_spend_delta is not None:
        required_delta = cfg.required_spend_delta
        statistical = required_delta
        status = ResponseBridgeStatus.REQUIRED_SPEND_DELTA_SUPPLIED
        flags.append(AdvisoryFlag.REQUIRED_SPEND_DELTA_SUPPLIED)
        if source in {ResponseBridgeSource.NONE, ResponseBridgeSource.USER_PROVIDED_REQUIRED_SPEND_DELTA}:
            source = ResponseBridgeSource.USER_PROVIDED_REQUIRED_SPEND_DELTA
    elif cfg.kpi_mde is not None and cfg.expected_kpi_per_dollar is not None and cfg.expected_kpi_per_dollar > 0:
        required_delta = cfg.kpi_mde / cfg.expected_kpi_per_dollar
        business = required_delta
        status = ResponseBridgeStatus.REQUIRED_SPEND_DELTA_ESTIMATED_ADVISORY
        flags.append(AdvisoryFlag.REQUIRED_SPEND_DELTA_ESTIMATED_ADVISORY)
        expected_kpi = cfg.expected_kpi_per_dollar * required_delta
        if source == ResponseBridgeSource.NONE:
            source = ResponseBridgeSource.BACK_OF_NAPKIN_USER_ASSUMPTION
        if source == ResponseBridgeSource.BACK_OF_NAPKIN_USER_ASSUMPTION:
            flags.append(AdvisoryFlag.BACK_OF_NAPKIN_ASSUMPTION_USED)
        if source == ResponseBridgeSource.MMM_RESPONSE_CURVE:
            flags.append(AdvisoryFlag.MMM_ADVISORY_SIGNAL_USED)
        if source == ResponseBridgeSource.MMM_ROMS:
            flags.append(AdvisoryFlag.MMM_ADVISORY_SIGNAL_USED)
        if source == ResponseBridgeSource.PROXY_RESPONSE_CURVE:
            flags.append(AdvisoryFlag.PROXY_RESPONSE_USED)
        if cfg.proxy_level and cfg.requested_test_level and cfg.proxy_level != cfg.requested_test_level:
            flags.append(AdvisoryFlag.PROXY_LEVEL_MISMATCH)
        if cfg.mmm_calibration_status and cfg.mmm_calibration_status.lower() in {"weak", "stale", "unvalidated"}:
            flags.append(AdvisoryFlag.MMM_CALIBRATION_WEAK)
        if required_delta is not None and cfg.mmm_curve_support_max_spend is not None:
            if required_delta > cfg.mmm_curve_support_max_spend or (
                cfg.mmm_curve_support_min_spend is not None and required_delta < cfg.mmm_curve_support_min_spend
            ):
                flags.append(AdvisoryFlag.OUT_OF_MMM_SUPPORT)
                flags.append(AdvisoryFlag.MMM_OUT_OF_SUPPORT)
                status = ResponseBridgeStatus.OUT_OF_SUPPORT
        if cfg.advisory_expected_kpi_response is not None and cfg.kpi_mde is not None:
            expected_kpi = cfg.advisory_expected_kpi_response
        elif required_delta is not None and cfg.expected_kpi_per_dollar is not None:
            expected_kpi = cfg.expected_kpi_per_dollar * required_delta
        if cfg.kpi_mde is not None and expected_kpi is not None and expected_kpi < cfg.kpi_mde * cfg.business_response_risk_ratio_threshold:
            flags.append(AdvisoryFlag.BUSINESS_RESPONSE_RISK)
            issues.append(
                SpendDiagnosticsIssue(
                    "business_response_risk",
                    "Expected response at advisory spend delta is below KPI MDE",
                    IssueSeverity.WARNING,
                )
            )
    else:
        flags.append(AdvisoryFlag.REQUIRED_SPEND_DELTA_UNKNOWN)
        issues.append(
            SpendDiagnosticsIssue(
                "required_spend_delta_unknown",
                "No response bridge supplied for required spend delta",
                IssueSeverity.INFO,
            )
        )

    return ResponseBridgeReport(
        response_bridge_source=source,
        response_bridge_status=status,
        kpi_mde=cfg.kpi_mde,
        kpi_unit=cfg.kpi_unit,
        required_spend_delta=required_delta,
        statistical_required_spend_contrast=statistical,
        business_response_required_spend=business,
        expected_kpi_at_required_spend=expected_kpi,
        advisory_flags=tuple(flags),
        issues=tuple(issues),
    )


def _historical_support(
    required_spend: float | None,
    baseline: BaselineSpendSummary | None,
    cfg: SpendRequirementManipulationFeasibilityConfig,
) -> HistoricalSupportStatus:
    if required_spend is None or baseline is None or baseline.historical_max_spend is None:
        return HistoricalSupportStatus.UNKNOWN_HISTORICAL_SUPPORT
    p95 = baseline.historical_p95_spend or baseline.historical_max_spend
    if required_spend <= (baseline.baseline_mean_weekly_spend or 0):
        return HistoricalSupportStatus.WITHIN_HISTORICAL_SUPPORT
    if p95 and required_spend <= p95:
        return HistoricalSupportStatus.NEAR_UPPER_HISTORICAL_SUPPORT
    if required_spend <= baseline.historical_max_spend:
        return HistoricalSupportStatus.ABOVE_HISTORICAL_SUPPORT
    if required_spend > baseline.historical_max_spend * cfg.far_above_historical_max_multiplier:
        return HistoricalSupportStatus.FAR_ABOVE_HISTORICAL_SUPPORT
    return HistoricalSupportStatus.ABOVE_HISTORICAL_SUPPORT


def _detect_control_manipulation(rows: list[dict[str, Any]], cfg: SpendRequirementManipulationFeasibilityConfig) -> bool:
    if cfg.control_manipulated:
        return True
    cols = cfg.columns
    for row in rows:
        role = str(row.get(cols.cell_role, "")).lower()
        if role in {"control", "holdout"} and str(row.get(cols.period_role, "")).lower() in {
            "treatment",
            "planned",
            "test",
        }:
            return True
    return False


def _build_manipulation_feasibility(
    rows: list[dict[str, Any]],
    cfg: SpendRequirementManipulationFeasibilityConfig,
    readiness: SpendDataReadinessReport,
    baseline: BaselineSpendInventoryReport,
    bridge: ResponseBridgeReport,
) -> ManipulationFeasibilityReport:
    issues: list[SpendDiagnosticsIssue] = []
    flags: list[AdvisoryFlag] = list(bridge.advisory_flags)
    candidates: list[ManipulationCandidate] = []

    if not readiness.spend_column_present or readiness.valid_spend_values == 0:
        issues.append(
            SpendDiagnosticsIssue("blocked_missing_spend", "Spend data missing", IssueSeverity.BLOCKING)
        )
        return ManipulationFeasibilityReport(
            (ManipulationCandidate(ManipulationOption.UNKNOWN, ManipulationFeasibilityOutcome.BLOCKED_MISSING_SPEND, HistoricalSupportStatus.UNKNOWN_HISTORICAL_SUPPORT),),
            tuple(flags),
            tuple(issues),
        )

    overall = next((s for s in baseline.summaries if s.level == "overall"), None)
    baseline_spend = overall.baseline_mean_weekly_spend if overall else None
    max_reducible = overall.max_reducible_spend if overall else None
    required_delta = bridge.required_spend_delta

    control_manipulated = _detect_control_manipulation(rows, cfg)
    if control_manipulated:
        flags.extend(
            [
                AdvisoryFlag.CONTROL_CELL_MANIPULATED,
                AdvisoryFlag.CONTROL_CONTAMINATION_RISK,
                AdvisoryFlag.BUSINESS_AS_USUAL_CONTROL_NOT_PRESERVED,
                AdvisoryFlag.ESTIMAND_SHIFT_REQUIRED,
                AdvisoryFlag.STANDARD_GO_DARK_INTERPRETATION_NOT_ALLOWED,
                AdvisoryFlag.METHOD_SUITABILITY_REVIEW_REQUIRED,
            ]
        )

    # GO_DARK
    if required_delta is None:
        candidates.append(
            ManipulationCandidate(
                ManipulationOption.GO_DARK,
                ManipulationFeasibilityOutcome.PROVISIONAL_REQUIRED_SPEND_UNKNOWN,
                HistoricalSupportStatus.UNKNOWN_HISTORICAL_SUPPORT,
                go_dark_max_delta=max_reducible,
            )
        )
    elif max_reducible is not None and max_reducible >= required_delta:
        outcome = ManipulationFeasibilityOutcome.GO_DARK_FEASIBLE
        if control_manipulated:
            outcome = ManipulationFeasibilityOutcome.DOSAGE_CONTRAST_ESTIMAND_REQUIRED
        candidates.append(
            ManipulationCandidate(
                ManipulationOption.GO_DARK,
                outcome,
                _historical_support(max_reducible, overall, cfg),
                go_dark_max_delta=max_reducible,
            )
        )
    else:
        candidates.append(
            ManipulationCandidate(
                ManipulationOption.GO_DARK,
                ManipulationFeasibilityOutcome.GO_DARK_INSUFFICIENT_BASELINE_SPEND,
                HistoricalSupportStatus.UNKNOWN_HISTORICAL_SUPPORT,
                go_dark_max_delta=max_reducible,
            )
        )

    # HEAVY_UP
    if baseline_spend and baseline_spend > 0 and required_delta is not None:
        req_heavy = baseline_spend + required_delta
        multiplier = req_heavy / baseline_spend
        hist = _historical_support(req_heavy, overall, cfg)
        if hist in {
            HistoricalSupportStatus.FAR_ABOVE_HISTORICAL_SUPPORT,
            HistoricalSupportStatus.ABOVE_HISTORICAL_SUPPORT,
        }:
            outcome = ManipulationFeasibilityOutcome.HEAVY_UP_OUT_OF_HISTORICAL_SUPPORT
        elif multiplier >= cfg.high_multiplier_warning_threshold:
            outcome = ManipulationFeasibilityOutcome.HEAVY_UP_MULTIPLIER_HIGH
            issues.append(
                SpendDiagnosticsIssue(
                    "heavy_up_multiplier_high",
                    f"Required heavy-up multiplier {multiplier:.2f} exceeds warning threshold",
                    IssueSeverity.WARNING,
                )
            )
        else:
            outcome = ManipulationFeasibilityOutcome.HEAVY_UP_FEASIBLE
        candidates.append(
            ManipulationCandidate(
                ManipulationOption.HEAVY_UP,
                outcome,
                hist,
                required_heavy_up_spend=req_heavy,
                required_heavy_up_multiplier=multiplier,
            )
        )
    elif required_delta is None:
        candidates.append(
            ManipulationCandidate(
                ManipulationOption.HEAVY_UP,
                ManipulationFeasibilityOutcome.PROVISIONAL_REQUIRED_SPEND_UNKNOWN,
                HistoricalSupportStatus.UNKNOWN_HISTORICAL_SUPPORT,
            )
        )

    # GO_LIVE
    near_zero = cfg.go_live_baseline_near_zero_threshold
    if baseline_spend is not None and baseline_spend <= near_zero and required_delta is not None and required_delta > 0:
        candidates.append(
            ManipulationCandidate(
                ManipulationOption.GO_LIVE,
                ManipulationFeasibilityOutcome.GO_LIVE_FEASIBLE,
                HistoricalSupportStatus.WITHIN_HISTORICAL_SUPPORT,
                required_heavy_up_spend=required_delta,
            )
        )
    elif baseline_spend is not None and baseline_spend > near_zero:
        candidates.append(
            ManipulationCandidate(
                ManipulationOption.GO_LIVE,
                ManipulationFeasibilityOutcome.GO_LIVE_CONFLICTS_WITH_EXISTING_BASELINE_SPEND,
                HistoricalSupportStatus.UNKNOWN_HISTORICAL_SUPPORT,
            )
        )

    # BUDGET_REALLOCATION
    if cfg.budget_source_channel and cfg.budget_destination_channel:
        candidates.append(
            ManipulationCandidate(
                ManipulationOption.BUDGET_REALLOCATION,
                ManipulationFeasibilityOutcome.BUDGET_REALLOCATION_FEASIBLE,
                HistoricalSupportStatus.UNKNOWN_HISTORICAL_SUPPORT,
                notes=(f"source={cfg.budget_source_channel}", f"destination={cfg.budget_destination_channel}"),
            )
        )
    else:
        candidates.append(
            ManipulationCandidate(
                ManipulationOption.BUDGET_REALLOCATION,
                ManipulationFeasibilityOutcome.BUDGET_REALLOCATION_MAPPING_INCOMPLETE,
                HistoricalSupportStatus.UNKNOWN_HISTORICAL_SUPPORT,
            )
        )

    # DOSAGE / DIFFERENCE_IN_POLICY
    if cfg.low_spend_policy is not None and cfg.high_spend_policy is not None:
        dosage_delta = cfg.high_spend_policy - cfg.low_spend_policy
        if required_delta is not None and dosage_delta >= required_delta:
            candidates.append(
                ManipulationCandidate(
                    ManipulationOption.DOSAGE_CONTRAST,
                    ManipulationFeasibilityOutcome.DOSAGE_CONTRAST_FEASIBLE,
                    HistoricalSupportStatus.WITHIN_HISTORICAL_SUPPORT,
                    dosage_delta=dosage_delta,
                )
            )
            candidates.append(
                ManipulationCandidate(
                    ManipulationOption.DIFFERENCE_IN_POLICY,
                    ManipulationFeasibilityOutcome.DOSAGE_CONTRAST_FEASIBLE,
                    HistoricalSupportStatus.WITHIN_HISTORICAL_SUPPORT,
                    dosage_delta=dosage_delta,
                )
            )
        else:
            candidates.append(
                ManipulationCandidate(
                    ManipulationOption.DOSAGE_CONTRAST,
                    ManipulationFeasibilityOutcome.INSUFFICIENT_CONTRAST,
                    HistoricalSupportStatus.UNKNOWN_HISTORICAL_SUPPORT,
                    dosage_delta=dosage_delta,
                )
            )
    if control_manipulated:
        candidates.append(
            ManipulationCandidate(
                ManipulationOption.DIFFERENCE_IN_POLICY,
                ManipulationFeasibilityOutcome.DOSAGE_CONTRAST_ESTIMAND_REQUIRED,
                HistoricalSupportStatus.UNKNOWN_HISTORICAL_SUPPORT,
            )
        )

    if cfg.available_test_budget is not None and required_delta is not None:
        gap = required_delta - cfg.available_test_budget
        for i, cand in enumerate(candidates):
            if cand.budget_gap is None:
                candidates[i] = ManipulationCandidate(
                    cand.manipulation_option,
                    cand.outcome,
                    cand.historical_support,
                    cand.go_dark_max_delta,
                    cand.required_heavy_up_spend,
                    cand.required_heavy_up_multiplier,
                    cand.dosage_delta,
                    gap,
                    cand.notes,
                )

    return ManipulationFeasibilityReport(tuple(candidates), tuple(flags), tuple(issues))


def _build_planning_boundary(
    readiness: SpendDataReadinessReport,
    manipulation: ManipulationFeasibilityReport,
    bridge: ResponseBridgeReport,
    status: FeasibilityStatus,
) -> PlanningBoundaryReport:
    flags = set(manipulation.advisory_flags) | set(bridge.advisory_flags)
    control_manipulated = AdvisoryFlag.CONTROL_CELL_MANIPULATED in flags
    dosage_required = AdvisoryFlag.ESTIMAND_SHIFT_REQUIRED in flags or any(
        c.manipulation_option in {ManipulationOption.DOSAGE_CONTRAST, ManipulationOption.DIFFERENCE_IN_POLICY}
        for c in manipulation.candidates
    )
    ready = status == FeasibilityStatus.READY_FOR_DOWNSTREAM_POWER_DIAGNOSTICS
    return PlanningBoundaryReport(
        standard_go_dark_interpretation_allowed=not control_manipulated and not readiness.ballpark_mode,
        dosage_contrast_estimand_required=dosage_required or control_manipulated,
        method_suitability_review_required=AdvisoryFlag.METHOD_SUITABILITY_REVIEW_REQUIRED in flags,
        business_as_usual_control_preserved=not control_manipulated,
        mmm_advisory_used=AdvisoryFlag.MMM_ADVISORY_SIGNAL_USED in flags,
        proxy_response_used=AdvisoryFlag.PROXY_RESPONSE_USED in flags,
        back_of_napkin_assumption_used=AdvisoryFlag.BACK_OF_NAPKIN_ASSUMPTION_USED in flags,
        ready_for_downstream_power_diagnostics=ready,
    )


def _aggregate_status(
    readiness: SpendDataReadinessReport,
    baseline: BaselineSpendInventoryReport,
    bridge: ResponseBridgeReport,
    manipulation: ManipulationFeasibilityReport,
) -> FeasibilityStatus:
    if readiness.sample_schema_mode or readiness.ballpark_mode:
        return FeasibilityStatus.PROVISIONAL
    if any(i.severity == IssueSeverity.BLOCKING for i in readiness.issues):
        return FeasibilityStatus.BLOCKED
    if any(c.outcome == ManipulationFeasibilityOutcome.BLOCKED_MISSING_SPEND for c in manipulation.candidates):
        return FeasibilityStatus.BLOCKED
    if bridge.response_bridge_status == ResponseBridgeStatus.REQUIRED_SPEND_DELTA_UNKNOWN:
        return FeasibilityStatus.PROVISIONAL
    if not baseline.baseline_window_derived:
        return FeasibilityStatus.PROVISIONAL
    has_warning = any(
        i.severity == IssueSeverity.WARNING
        for group in (readiness.issues, baseline.issues, bridge.issues, manipulation.issues)
        for i in group
    ) or any(
        c.outcome
        in {
            ManipulationFeasibilityOutcome.HEAVY_UP_MULTIPLIER_HIGH,
            ManipulationFeasibilityOutcome.HEAVY_UP_OUT_OF_HISTORICAL_SUPPORT,
            ManipulationFeasibilityOutcome.GO_LIVE_CONFLICTS_WITH_EXISTING_BASELINE_SPEND,
        }
        for c in manipulation.candidates
    )
    if has_warning:
        return FeasibilityStatus.PASS_WITH_WARNINGS
    if bridge.required_spend_delta is not None and readiness.has_required_columns:
        return FeasibilityStatus.READY_FOR_DOWNSTREAM_POWER_DIAGNOSTICS
    return FeasibilityStatus.PROVISIONAL


def evaluate_spend_requirement_and_manipulation_feasibility(
    input_data: list[dict[str, Any]] | GeoKpiSpendProfilerInput | Any,
    config: SpendRequirementManipulationFeasibilityConfig | None = None,
) -> SpendRequirementManipulationFeasibilityReport:
    """Evaluate spend requirement and manipulation feasibility. Side-effect free."""
    cfg = config or SpendRequirementManipulationFeasibilityConfig()
    rows = _normalize_rows(input_data)
    profiler_cfg = cfg.profiler_config or GeoKpiSpendProfilerConfig(spend_coverage_requested=True)
    if cfg.planned_test_start_date and profiler_cfg.planned_test_start_date is None:
        profiler_cfg = GeoKpiSpendProfilerConfig(
            spend_coverage_requested=True,
            planned_test_start_date=cfg.planned_test_start_date,
            aggregation_rule=profiler_cfg.aggregation_rule,
            max_sample_geo_units=profiler_cfg.max_sample_geo_units,
            week_start_day=profiler_cfg.week_start_day,
        )
    profile = cfg.profile_report or profile_geo_kpi_spend_data(GeoKpiSpendProfilerInput(rows=rows), profiler_cfg)

    readiness = _build_readiness(rows, profile, cfg)
    baseline = _build_baseline_inventory(rows, cfg)
    bridge = _build_response_bridge(cfg)
    manipulation = _build_manipulation_feasibility(rows, cfg, readiness, baseline, bridge)
    status = _aggregate_status(readiness, baseline, bridge, manipulation)
    planning = _build_planning_boundary(readiness, manipulation, bridge, status)

    all_issues = (
        *readiness.issues,
        *baseline.issues,
        *bridge.issues,
        *manipulation.issues,
    )
    all_flags = tuple(sorted(set(bridge.advisory_flags) | set(manipulation.advisory_flags), key=lambda f: f.value))

    return SpendRequirementManipulationFeasibilityReport(
        artifact_id=_ARTIFACT_ID,
        feasibility_status=status,
        spend_data_readiness=readiness,
        baseline_spend_inventory=baseline,
        response_bridge=bridge,
        manipulation_feasibility=manipulation,
        planning_boundary=planning,
        issues=all_issues,
        advisory_flags=all_flags,
        final_verdict=_VERDICT,
    )


evaluate_spend_manipulation_feasibility = evaluate_spend_requirement_and_manipulation_feasibility


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    weeks = ("2025-01-01", "2025-01-08", "2025-01-15", "2025-01-22", "2025-01-29", "2025-02-05", "2025-02-12", "2025-02-19")
    rows = [
        {"geo_unit_id": f"DMA_{i:03d}", "date": w, "kpi_value": float(i), "spend_value": 1000.0 + i * 10}
        for i in range(1, 6)
        for w in weeks
    ]
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        rows,
        SpendRequirementManipulationFeasibilityConfig(
            planned_test_start_date="2025-02-01",
            required_spend_delta=500.0,
            response_bridge_source=ResponseBridgeSource.USER_PROVIDED_REQUIRED_SPEND_DELTA,
        ),
    )
    failed: list[str] = []
    if report.feasibility_status not in {
        FeasibilityStatus.READY_FOR_DOWNSTREAM_POWER_DIAGNOSTICS,
        FeasibilityStatus.PASS_WITH_WARNINGS,
    }:
        failed.append("smoke_feasibility_status")
    if report.planning_boundary.runtime_power_authorized:
        failed.append("smoke_no_power_auth")
    if report.planning_boundary.mde_authorized:
        failed.append("smoke_no_mde_auth")

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "spend_requirement_and_manipulation_feasibility_diagnostics",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": "deterministic_spend_requirement_and_manipulation_feasibility_diagnostics",
        "depends_on": [
            "GEO_KPI_SPEND_DATA_PROFILER_001",
            "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
            "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001",
        ],
        "public_api": "evaluate_spend_requirement_and_manipulation_feasibility",
        "spend_data_readiness_implemented": True,
        "baseline_spend_inventory_implemented": True,
        "response_bridge_implemented": True,
        "manipulation_feasibility_implemented": True,
        "planning_boundary_implemented": True,
        "supported_manipulation_options": [m.value for m in ManipulationOption],
        "response_bridge_sources_supported": [s.value for s in ResponseBridgeSource],
        "kpi_mde_to_advisory_spend_translation_implemented": True,
        "mmm_advisory_runtime_calls_implemented": False,
        "mmm_proxy_use_advisory_only": True,
        "dosage_contrast_first_class_option": True,
        "required_heavy_up_multiplier_implemented": True,
        "historical_support_check_implemented": True,
        "control_contamination_warning_implemented": True,
        "estimand_shift_flag_implemented": True,
        "candidate_manipulation_options_emitted": True,
        "ready_for_downstream_power_diagnostics_allowed": True,
        "runtime_power_authorized": False,
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
        "generated_at": datetime.now().isoformat(),
        "git_commit": _git_commit(),
        "failed_scenarios": failed,
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
