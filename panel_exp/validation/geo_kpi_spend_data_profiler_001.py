"""GEO_KPI_SPEND_DATA_PROFILER_001 deterministic geo KPI/spend data profiler."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

_ARTIFACT_ID = "GEO_KPI_SPEND_DATA_PROFILER_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "geo_kpi_spend_data_profiler_implemented_no_design_inference_or_production_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/GEO_KPI_SPEND_DATA_PROFILER_001_summary.json"
RECOMMENDED_NEXT_ARTIFACT = "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001"

PROFILER_IMPLEMENTATION_NOTES_APPLIED = (
    "prefer_additive_kpis_for_future_calibration_rates_are_diagnostic_without_numerator_denominator",
    "design_at_provided_geo_level_no_silent_geo_level_upgrade_or_downgrade",
    "planned_test_start_date_check_supported",
    "profiler_reports_coverage_and_schema_readiness_only_no_design_power_mde_inference",
    "no_hidden_zero_fill_or_hidden_imputation",
)

_GEO_CANDIDATES = ("geo_unit_id", "geo_unit", "dma", "geo", "market", "region")
_DATE_CANDIDATES = ("date", "week", "date_or_week", "week_start", "period", "time_period")
_KPI_CANDIDATES = ("kpi_value", "kpi", "conversions", "revenue", "orders", "trials", "installs")
_SPEND_CANDIDATES = ("spend_value", "spend", "media_spend", "cost", "total_spend")
_PERIOD_TYPE_CANDIDATES = ("period_type", "row_type", "data_period_type")
_RATE_KPI_HINTS = ("rate", "ratio", "ctr", "cpc", "percent", "pct", "roas")


class InputMode(str, Enum):
    FULL_PANEL = "FULL_PANEL"
    SAMPLE_SCHEMA = "SAMPLE_SCHEMA"
    BALLPARK = "BALLPARK"
    UNKNOWN = "UNKNOWN"


class ProfilerStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    PROVISIONAL = "PROVISIONAL"
    BLOCKED = "BLOCKED"


class DataQualitySeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"


class ClaimBoundary(str, Enum):
    SCHEMA_ONLY = "SCHEMA_ONLY"
    PROFILE_ONLY = "PROFILE_ONLY"
    PROVISIONAL_ONLY = "PROVISIONAL_ONLY"
    READY_FOR_DOWNSTREAM_DIAGNOSTICS = "READY_FOR_DOWNSTREAM_DIAGNOSTICS"
    BLOCKED = "BLOCKED"


class TimeGrain(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DataQualityIssue:
    code: str
    message: str
    severity: DataQualitySeverity
    field: str | None = None


@dataclass(frozen=True)
class ProfilerClaimBoundary:
    claim_boundary: ClaimBoundary
    ready_for_downstream_diagnostics: bool = False
    schema_feedback_available: bool = False
    provisional_planning_input_available: bool = False
    design_feasibility_authorized: bool = False
    spend_contrast_feasibility_authorized: bool = False
    power_authorized: bool = False
    mde_authorized: bool = False
    p_value_authorized: bool = False
    confidence_interval_authorized: bool = False
    lift_authorized: bool = False
    roi_authorized: bool = False
    method_recommendation_authorized: bool = False
    portfolio_tiering_authorized: bool = False
    mmm_calibration_authorized: bool = False
    production_authorization_granted: bool = False
    llm_decisioning_authorized: bool = False


@dataclass(frozen=True)
class ColumnMappingReport:
    geo_column: str | None
    date_column: str | None
    kpi_column: str | None
    spend_column: str | None
    period_type_column: str | None
    geo_present: bool
    date_present: bool
    kpi_present: bool
    spend_present: bool


@dataclass(frozen=True)
class InputModeReport:
    input_mode: InputMode
    classification_reason: str


@dataclass(frozen=True)
class TimeGrainReport:
    declared_time_grain: str | None
    inferred_time_grain: TimeGrain
    mixed_grain_detected: bool
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class GeoUnitInventoryReport:
    geo_unit_column: str | None
    geo_unit_type: str | None
    geo_unit_count: int
    sample_geo_units: tuple[str, ...]
    missing_geo_count: int


@dataclass(frozen=True)
class GeoTimeCoverageReport:
    min_date: str | None
    max_date: str | None
    distinct_period_count: int
    rows_on_or_after_planned_start: int
    planned_future_labeled_rows: int


@dataclass(frozen=True)
class KpiCoverageReport:
    kpi_column: str | None
    non_missing_count: int
    missing_count: int
    zero_count: int
    negative_count: int
    numeric_summary: dict[str, float | int] | None


@dataclass(frozen=True)
class SpendCoverageReport:
    spend_column: str | None
    spend_present: bool
    non_missing_count: int
    missing_count: int
    zero_count: int
    negative_count: int
    numeric_summary: dict[str, float | int] | None


@dataclass(frozen=True)
class MissingnessReport:
    missing_kpi_count: int
    missing_spend_count: int
    missing_geo_count: int
    missing_date_count: int
    missing_kpi_treated_as_zero: bool = False
    missing_spend_treated_as_zero: bool = False
    hidden_imputation_applied: bool = False


@dataclass(frozen=True)
class DuplicateRowReport:
    duplicate_geo_time_count: int
    duplicate_examples: tuple[tuple[str, str], ...]
    aggregation_rule_declared: bool
    silently_aggregated: bool = False


@dataclass(frozen=True)
class GeoKpiSpendProfilerInput:
    rows: list[dict[str, Any]] | None = None
    sample_schema_columns: list[str] | None = None
    ballpark: dict[str, Any] | None = None
    column_mapping: dict[str, str] | None = None
    declared_input_mode: InputMode | None = None
    geo_unit_type: str | None = None
    time_grain: str | None = None


@dataclass(frozen=True)
class GeoKpiSpendProfilerConfig:
    spend_coverage_requested: bool = False
    planned_test_start_date: date | str | None = None
    aggregation_rule: str | None = None
    max_sample_geo_units: int = 10
    week_start_day: str | None = None


@dataclass(frozen=True)
class GeoKpiSpendDataProfileReport:
    artifact_id: str
    profiler_status: ProfilerStatus
    input_mode_report: InputModeReport
    column_mapping_report: ColumnMappingReport
    time_grain_report: TimeGrainReport
    geo_unit_inventory_report: GeoUnitInventoryReport
    geo_time_coverage_report: GeoTimeCoverageReport
    kpi_coverage_report: KpiCoverageReport
    spend_coverage_report: SpendCoverageReport
    missingness_report: MissingnessReport
    duplicate_row_report: DuplicateRowReport
    data_quality_issues: tuple[DataQualityIssue, ...]
    claim_boundary: ProfilerClaimBoundary
    kpi_note: str | None = None
    geo_note: str | None = None
    ballpark_summary: dict[str, Any] | None = None
    schema_checklist: tuple[str, ...] = ()


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
    text = str(value).strip()
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _parse_planned_start(value: date | str | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return _parse_date(value)


def _resolve_column(columns: Sequence[str], mapping: Mapping[str, str] | None, key: str, candidates: Sequence[str]) -> str | None:
    if mapping and key in mapping and mapping[key] in columns:
        return mapping[key]
    lower_map = {c.lower(): c for c in columns}
    for candidate in candidates:
        if candidate in lower_map:
            return lower_map[candidate]
    return None


def _normalize_profiler_input(input_data: GeoKpiSpendProfilerInput | list[dict[str, Any]] | Any) -> GeoKpiSpendProfilerInput:
    if isinstance(input_data, GeoKpiSpendProfilerInput):
        return input_data
    if isinstance(input_data, list):
        return GeoKpiSpendProfilerInput(rows=input_data)
    if hasattr(input_data, "to_dict"):
        records = input_data.to_dict("records")
        return GeoKpiSpendProfilerInput(rows=records)
    raise TypeError("input_data must be GeoKpiSpendProfilerInput, list[dict], or pandas DataFrame")


def _classify_input_mode(profiler_input: GeoKpiSpendProfilerInput) -> InputModeReport:
    if profiler_input.declared_input_mode is not None:
        return InputModeReport(
            input_mode=profiler_input.declared_input_mode,
            classification_reason="declared_input_mode",
        )
    if profiler_input.ballpark:
        return InputModeReport(input_mode=InputMode.BALLPARK, classification_reason="ballpark_fields_present")
    if profiler_input.sample_schema_columns and not profiler_input.rows:
        return InputModeReport(input_mode=InputMode.SAMPLE_SCHEMA, classification_reason="schema_columns_only")
    if profiler_input.rows:
        return InputModeReport(input_mode=InputMode.FULL_PANEL, classification_reason="row_level_geo_time_data")
    return InputModeReport(input_mode=InputMode.UNKNOWN, classification_reason="insufficient_structure")


def _blocked_claim_boundary() -> ProfilerClaimBoundary:
    return ProfilerClaimBoundary(claim_boundary=ClaimBoundary.BLOCKED)


def _schema_claim_boundary() -> ProfilerClaimBoundary:
    return ProfilerClaimBoundary(
        claim_boundary=ClaimBoundary.SCHEMA_ONLY,
        schema_feedback_available=True,
    )


def _provisional_claim_boundary() -> ProfilerClaimBoundary:
    return ProfilerClaimBoundary(
        claim_boundary=ClaimBoundary.PROVISIONAL_ONLY,
        provisional_planning_input_available=True,
    )


def _ready_claim_boundary() -> ProfilerClaimBoundary:
    return ProfilerClaimBoundary(
        claim_boundary=ClaimBoundary.READY_FOR_DOWNSTREAM_DIAGNOSTICS,
        ready_for_downstream_diagnostics=True,
    )


def _numeric_summary(values: list[float]) -> dict[str, float | int] | None:
    if not values:
        return None
    ordered = sorted(values)
    n = len(ordered)
    return {
        "count": n,
        "min": ordered[0],
        "max": ordered[-1],
        "mean": sum(ordered) / n,
        "median": ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2,
    }


def _infer_time_grain(dates: list[date]) -> TimeGrainReport:
    if len(dates) < 2:
        return TimeGrainReport(
            declared_time_grain=None,
            inferred_time_grain=TimeGrain.UNKNOWN,
            mixed_grain_detected=False,
            notes=("insufficient_dates_for_grain_inference",),
        )
    unique_sorted = sorted(set(dates))
    deltas = [(unique_sorted[i + 1] - unique_sorted[i]).days for i in range(len(unique_sorted) - 1)]
    if not deltas:
        return TimeGrainReport(None, TimeGrain.UNKNOWN, False)
    common_delta = Counter(deltas).most_common(1)[0][0]
    mixed = len(set(deltas)) > 1
    if common_delta == 1:
        grain = TimeGrain.DAILY
    elif 6 <= common_delta <= 8:
        grain = TimeGrain.WEEKLY
    elif 27 <= common_delta <= 31:
        grain = TimeGrain.MONTHLY
    else:
        grain = TimeGrain.UNKNOWN
    notes: list[str] = ()
    if mixed:
        notes = ("mixed_date_spacing_detected",)
    return TimeGrainReport(None, grain, mixed, tuple(notes))


def _profile_sample_schema(
    profiler_input: GeoKpiSpendProfilerInput,
    config: GeoKpiSpendProfilerConfig,
) -> GeoKpiSpendDataProfileReport:
    columns = list(profiler_input.sample_schema_columns or [])
    mapping = profiler_input.column_mapping or {}
    column_report = ColumnMappingReport(
        geo_column=_resolve_column(columns, mapping, "geo_unit", _GEO_CANDIDATES),
        date_column=_resolve_column(columns, mapping, "date", _DATE_CANDIDATES),
        kpi_column=_resolve_column(columns, mapping, "kpi", _KPI_CANDIDATES),
        spend_column=_resolve_column(columns, mapping, "spend", _SPEND_CANDIDATES),
        period_type_column=_resolve_column(columns, mapping, "period_type", _PERIOD_TYPE_CANDIDATES),
        geo_present=_resolve_column(columns, mapping, "geo_unit", _GEO_CANDIDATES) is not None,
        date_present=_resolve_column(columns, mapping, "date", _DATE_CANDIDATES) is not None,
        kpi_present=_resolve_column(columns, mapping, "kpi", _KPI_CANDIDATES) is not None,
        spend_present=_resolve_column(columns, mapping, "spend", _SPEND_CANDIDATES) is not None,
    )
    checklist = tuple(
        item
        for item, present in (
            ("geo_unit_column", column_report.geo_present),
            ("date_or_week_column", column_report.date_present),
            ("kpi_column", column_report.kpi_present),
            ("spend_column_optional_unless_requested", column_report.spend_present or not config.spend_coverage_requested),
        )
        if not present
    )
    issues: list[DataQualityIssue] = []
    status = ProfilerStatus.PROVISIONAL
    if not column_report.kpi_present or not column_report.geo_present or not column_report.date_present:
        status = ProfilerStatus.BLOCKED
        if not column_report.geo_present:
            issues.append(DataQualityIssue("missing_geo_column", "Sample schema missing geo unit column", DataQualitySeverity.BLOCKING, "geo_unit"))
        if not column_report.date_present:
            issues.append(DataQualityIssue("missing_date_column", "Sample schema missing date/week column", DataQualitySeverity.BLOCKING, "date"))
        if not column_report.kpi_present:
            issues.append(DataQualityIssue("missing_kpi_column", "Sample schema missing KPI column", DataQualitySeverity.BLOCKING, "kpi"))
    if config.spend_coverage_requested and not column_report.spend_present:
        issues.append(DataQualityIssue("missing_spend_column", "Spend column missing for requested spend coverage", DataQualitySeverity.BLOCKING, "spend"))
        status = ProfilerStatus.BLOCKED
    return GeoKpiSpendDataProfileReport(
        artifact_id=_ARTIFACT_ID,
        profiler_status=status,
        input_mode_report=InputModeReport(InputMode.SAMPLE_SCHEMA, "schema_columns_only"),
        column_mapping_report=column_report,
        time_grain_report=TimeGrainReport(profiler_input.time_grain, TimeGrain.UNKNOWN, False),
        geo_unit_inventory_report=GeoUnitInventoryReport(None, profiler_input.geo_unit_type, 0, (), 0),
        geo_time_coverage_report=GeoTimeCoverageReport(None, None, 0, 0, 0),
        kpi_coverage_report=KpiCoverageReport(column_report.kpi_column, 0, 0, 0, 0, None),
        spend_coverage_report=SpendCoverageReport(column_report.spend_column, column_report.spend_present, 0, 0, 0, 0, None),
        missingness_report=MissingnessReport(0, 0, 0, 0),
        duplicate_row_report=DuplicateRowReport(0, (), bool(config.aggregation_rule)),
        data_quality_issues=tuple(issues),
        claim_boundary=_schema_claim_boundary() if status != ProfilerStatus.BLOCKED else _blocked_claim_boundary(),
        schema_checklist=checklist,
    )


def _profile_ballpark(profiler_input: GeoKpiSpendProfilerInput) -> GeoKpiSpendDataProfileReport:
    ballpark = dict(profiler_input.ballpark or {})
    return GeoKpiSpendDataProfileReport(
        artifact_id=_ARTIFACT_ID,
        profiler_status=ProfilerStatus.PROVISIONAL,
        input_mode_report=InputModeReport(InputMode.BALLPARK, "ballpark_fields_present"),
        column_mapping_report=ColumnMappingReport(None, None, None, None, None, False, False, False, False),
        time_grain_report=TimeGrainReport(str(ballpark.get("time_grain")) if ballpark.get("time_grain") else None, TimeGrain.UNKNOWN, False),
        geo_unit_inventory_report=GeoUnitInventoryReport(
            None,
            profiler_input.geo_unit_type,
            int(ballpark.get("number_of_geo_units", 0) or 0),
            (),
            0,
        ),
        geo_time_coverage_report=GeoTimeCoverageReport(None, None, int(ballpark.get("historical_weeks_available", 0) or 0), 0, 0),
        kpi_coverage_report=KpiCoverageReport(None, 0, 0, 0, 0, None),
        spend_coverage_report=SpendCoverageReport(None, "rough_spend" in ballpark, 0, 0, 0, 0, None),
        missingness_report=MissingnessReport(0, 0, 0, 0),
        duplicate_row_report=DuplicateRowReport(0, (), False),
        data_quality_issues=(),
        claim_boundary=_provisional_claim_boundary(),
        ballpark_summary=ballpark,
    )


def _profile_full_panel(
    profiler_input: GeoKpiSpendProfilerInput,
    config: GeoKpiSpendProfilerConfig,
) -> GeoKpiSpendDataProfileReport:
    rows = list(profiler_input.rows or [])
    if not rows:
        return GeoKpiSpendDataProfileReport(
            artifact_id=_ARTIFACT_ID,
            profiler_status=ProfilerStatus.BLOCKED,
            input_mode_report=InputModeReport(InputMode.FULL_PANEL, "no_rows"),
            column_mapping_report=ColumnMappingReport(None, None, None, None, None, False, False, False, False),
            time_grain_report=TimeGrainReport(None, TimeGrain.UNKNOWN, False),
            geo_unit_inventory_report=GeoUnitInventoryReport(None, None, 0, (), 0),
            geo_time_coverage_report=GeoTimeCoverageReport(None, None, 0, 0, 0),
            kpi_coverage_report=KpiCoverageReport(None, 0, 0, 0, 0, None),
            spend_coverage_report=SpendCoverageReport(None, False, 0, 0, 0, 0, None),
            missingness_report=MissingnessReport(0, 0, 0, 0),
            duplicate_row_report=DuplicateRowReport(0, (), bool(config.aggregation_rule)),
            data_quality_issues=(
                DataQualityIssue("no_rows", "Full panel mode requires at least one row", DataQualitySeverity.BLOCKING),
            ),
            claim_boundary=_blocked_claim_boundary(),
        )

    columns = sorted({key for row in rows for key in row.keys()})
    mapping = profiler_input.column_mapping or {}
    geo_col = _resolve_column(columns, mapping, "geo_unit", _GEO_CANDIDATES)
    date_col = _resolve_column(columns, mapping, "date", _DATE_CANDIDATES)
    kpi_col = _resolve_column(columns, mapping, "kpi", _KPI_CANDIDATES)
    spend_col = _resolve_column(columns, mapping, "spend", _SPEND_CANDIDATES)
    period_col = _resolve_column(columns, mapping, "period_type", _PERIOD_TYPE_CANDIDATES)

    column_report = ColumnMappingReport(
        geo_column=geo_col,
        date_column=date_col,
        kpi_column=kpi_col,
        spend_column=spend_col,
        period_type_column=period_col,
        geo_present=geo_col is not None,
        date_present=date_col is not None,
        kpi_present=kpi_col is not None,
        spend_present=spend_col is not None,
    )

    issues: list[DataQualityIssue] = []
    if not geo_col:
        issues.append(DataQualityIssue("missing_geo_column", "Geo unit column missing", DataQualitySeverity.BLOCKING, "geo_unit"))
    if not date_col:
        issues.append(DataQualityIssue("missing_date_column", "Date/week column missing", DataQualitySeverity.BLOCKING, "date"))
    if not kpi_col:
        issues.append(DataQualityIssue("missing_kpi_column", "KPI column missing", DataQualitySeverity.BLOCKING, "kpi"))
    if config.spend_coverage_requested and not spend_col:
        issues.append(DataQualityIssue("missing_spend_column", "Spend column missing for requested spend coverage", DataQualitySeverity.BLOCKING, "spend"))

    if issues:
        return GeoKpiSpendDataProfileReport(
            artifact_id=_ARTIFACT_ID,
            profiler_status=ProfilerStatus.BLOCKED,
            input_mode_report=InputModeReport(InputMode.FULL_PANEL, "row_level_geo_time_data"),
            column_mapping_report=column_report,
            time_grain_report=TimeGrainReport(profiler_input.time_grain, TimeGrain.UNKNOWN, False),
            geo_unit_inventory_report=GeoUnitInventoryReport(geo_col, profiler_input.geo_unit_type, 0, (), 0),
            geo_time_coverage_report=GeoTimeCoverageReport(None, None, 0, 0, 0),
            kpi_coverage_report=KpiCoverageReport(kpi_col, 0, 0, 0, 0, None),
            spend_coverage_report=SpendCoverageReport(spend_col, spend_col is not None, 0, 0, 0, 0, None),
            missingness_report=MissingnessReport(0, 0, 0, 0),
            duplicate_row_report=DuplicateRowReport(0, (), bool(config.aggregation_rule)),
            data_quality_issues=tuple(issues),
            claim_boundary=_blocked_claim_boundary(),
        )

    assert geo_col and date_col and kpi_col

    geo_values: list[str] = []
    dates: list[date] = []
    kpi_values: list[float] = []
    spend_values: list[float] = []
    missing_geo = missing_date = missing_kpi = missing_spend = 0
    zero_kpi = zero_spend = negative_kpi = negative_spend = 0
    geo_time_pairs: list[tuple[str, str]] = []
    planned_start = _parse_planned_start(config.planned_test_start_date)
    rows_on_or_after_planned = 0
    planned_future_labeled = 0

    for row in rows:
        geo_raw = row.get(geo_col)
        date_raw = row.get(date_col)
        kpi_raw = row.get(kpi_col)
        spend_raw = row.get(spend_col) if spend_col else None

        if _is_missing(geo_raw):
            missing_geo += 1
        else:
            geo_values.append(str(geo_raw))

        parsed_date = _parse_date(date_raw)
        if parsed_date is None:
            missing_date += 1
        else:
            dates.append(parsed_date)
            if planned_start and parsed_date >= planned_start:
                period_label = str(row.get(period_col, "")).lower() if period_col else ""
                if period_label in {"planned", "future", "planning"}:
                    planned_future_labeled += 1
                else:
                    rows_on_or_after_planned += 1

        kpi_num = _to_float(kpi_raw)
        if kpi_num is None:
            missing_kpi += 1
        else:
            kpi_values.append(kpi_num)
            if kpi_num == 0:
                zero_kpi += 1
            elif kpi_num < 0:
                negative_kpi += 1

        if spend_col:
            spend_num = _to_float(spend_raw)
            if spend_num is None:
                missing_spend += 1
            else:
                spend_values.append(spend_num)
                if spend_num == 0:
                    zero_spend += 1
                elif spend_num < 0:
                    negative_spend += 1

        if not _is_missing(geo_raw) and not _is_missing(date_raw):
            geo_time_pairs.append((str(geo_raw), str(date_raw)))

    duplicate_counter = Counter(geo_time_pairs)
    duplicate_examples = tuple(pair for pair, count in duplicate_counter.items() if count > 1)[:5]
    duplicate_count = sum(1 for count in duplicate_counter.values() if count > 1)

    if duplicate_count and not config.aggregation_rule:
        issues.append(
            DataQualityIssue(
                "duplicate_geo_time_rows",
                "Duplicate geo/time rows detected without aggregation rule",
                DataQualitySeverity.BLOCKING,
            )
        )

    if planned_start and rows_on_or_after_planned:
        issues.append(
            DataQualityIssue(
                "planned_test_start_overlap",
                "Historical rows exist on or after planned_test_start_date without planned/future label",
                DataQualitySeverity.WARNING,
                "planned_test_start_date",
            )
        )

    declared_grain = profiler_input.time_grain
    if declared_grain:
        try:
            inferred = TimeGrain(declared_grain.lower())
            time_report = TimeGrainReport(declared_grain, inferred, False)
        except ValueError:
            time_report = TimeGrainReport(declared_grain, TimeGrain.UNKNOWN, False)
    else:
        time_report = _infer_time_grain(dates)
        if time_report.mixed_grain_detected:
            issues.append(
                DataQualityIssue("mixed_grain", "Mixed time grain spacing detected", DataQualitySeverity.BLOCKING)
            )

    distinct_geos = sorted(set(geo_values))
    geo_report = GeoUnitInventoryReport(
        geo_unit_column=geo_col,
        geo_unit_type=profiler_input.geo_unit_type,
        geo_unit_count=len(distinct_geos),
        sample_geo_units=tuple(distinct_geos[: config.max_sample_geo_units]),
        missing_geo_count=missing_geo,
    )

    min_date = min(dates).isoformat() if dates else None
    max_date = max(dates).isoformat() if dates else None
    coverage_report = GeoTimeCoverageReport(
        min_date=min_date,
        max_date=max_date,
        distinct_period_count=len(set(d.isoformat() for d in dates)),
        rows_on_or_after_planned_start=rows_on_or_after_planned,
        planned_future_labeled_rows=planned_future_labeled,
    )

    kpi_report = KpiCoverageReport(
        kpi_column=kpi_col,
        non_missing_count=len(kpi_values),
        missing_count=missing_kpi,
        zero_count=zero_kpi,
        negative_count=negative_kpi,
        numeric_summary=_numeric_summary(kpi_values),
    )
    spend_report = SpendCoverageReport(
        spend_column=spend_col,
        spend_present=spend_col is not None,
        non_missing_count=len(spend_values),
        missing_count=missing_spend,
        zero_count=zero_spend,
        negative_count=negative_spend,
        numeric_summary=_numeric_summary(spend_values),
    )
    missingness_report = MissingnessReport(
        missing_kpi_count=missing_kpi,
        missing_spend_count=missing_spend,
        missing_geo_count=missing_geo,
        missing_date_count=missing_date,
    )
    duplicate_report = DuplicateRowReport(
        duplicate_geo_time_count=duplicate_count,
        duplicate_examples=duplicate_examples,
        aggregation_rule_declared=bool(config.aggregation_rule),
    )

    kpi_note = None
    if kpi_col and any(hint in kpi_col.lower() for hint in _RATE_KPI_HINTS):
        kpi_note = (
            "Rate/ratio KPI detected. Preferred calibration KPIs are additive outcomes "
            "(conversions, revenue, orders, trials, installs, units, ARR, GNARR). "
            "Rate/ratio-only KPIs are diagnostic unless numerator/denominator are provided."
        )
        issues.append(DataQualityIssue("rate_kpi_diagnostic_note", kpi_note, DataQualitySeverity.INFO, kpi_col))

    geo_note = (
        "Profiler reports at the provided geo level. DMAs within the same state are valid "
        "distinct units when rows are mutually exclusive. Do not silently upgrade state to DMA "
        "or decompose one country aggregate into many geo units."
    )
    geo_type = (profiler_input.geo_unit_type or "").lower()
    if geo_type in {"country", "country_region_aggregate", "country_aggregate"} and geo_report.geo_unit_count == 1:
        issues.append(
            DataQualityIssue(
                "country_aggregate_single_unit",
                "Single country/region aggregate does not imply randomized geo design readiness",
                DataQualitySeverity.INFO,
            )
        )

    blocking = any(i.severity == DataQualitySeverity.BLOCKING for i in issues)
    if blocking:
        status = ProfilerStatus.BLOCKED
        claim = _blocked_claim_boundary()
    elif any(i.severity == DataQualitySeverity.WARNING for i in issues):
        status = ProfilerStatus.PASS_WITH_WARNINGS
        claim = _ready_claim_boundary()
    else:
        status = ProfilerStatus.PASS
        claim = _ready_claim_boundary()

    return GeoKpiSpendDataProfileReport(
        artifact_id=_ARTIFACT_ID,
        profiler_status=status,
        input_mode_report=InputModeReport(InputMode.FULL_PANEL, "row_level_geo_time_data"),
        column_mapping_report=column_report,
        time_grain_report=time_report,
        geo_unit_inventory_report=geo_report,
        geo_time_coverage_report=coverage_report,
        kpi_coverage_report=kpi_report,
        spend_coverage_report=spend_report,
        missingness_report=missingness_report,
        duplicate_row_report=duplicate_report,
        data_quality_issues=tuple(issues),
        claim_boundary=claim,
        kpi_note=kpi_note,
        geo_note=geo_note,
    )


def profile_geo_kpi_spend_data(
    input_data: GeoKpiSpendProfilerInput | list[dict[str, Any]] | Any,
    config: GeoKpiSpendProfilerConfig | None = None,
) -> GeoKpiSpendDataProfileReport:
    """Profile geo KPI/spend input deterministically. Side-effect free."""
    profiler_input = _normalize_profiler_input(input_data)
    cfg = config or GeoKpiSpendProfilerConfig()
    mode_report = _classify_input_mode(profiler_input)

    if mode_report.input_mode == InputMode.BALLPARK:
        return _profile_ballpark(profiler_input)
    if mode_report.input_mode == InputMode.SAMPLE_SCHEMA:
        return _profile_sample_schema(profiler_input, cfg)
    if mode_report.input_mode == InputMode.FULL_PANEL:
        return _profile_full_panel(profiler_input, cfg)

    return GeoKpiSpendDataProfileReport(
        artifact_id=_ARTIFACT_ID,
        profiler_status=ProfilerStatus.BLOCKED,
        input_mode_report=mode_report,
        column_mapping_report=ColumnMappingReport(None, None, None, None, None, False, False, False, False),
        time_grain_report=TimeGrainReport(None, TimeGrain.UNKNOWN, False),
        geo_unit_inventory_report=GeoUnitInventoryReport(None, None, 0, (), 0),
        geo_time_coverage_report=GeoTimeCoverageReport(None, None, 0, 0, 0),
        kpi_coverage_report=KpiCoverageReport(None, 0, 0, 0, 0, None),
        spend_coverage_report=SpendCoverageReport(None, False, 0, 0, 0, 0, None),
        missingness_report=MissingnessReport(0, 0, 0, 0),
        duplicate_row_report=DuplicateRowReport(0, (), False),
        data_quality_issues=(
            DataQualityIssue("unknown_input_mode", "Insufficient input structure", DataQualitySeverity.BLOCKING),
        ),
        claim_boundary=_blocked_claim_boundary(),
    )


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    sample_rows = [
        {"geo_unit_id": "DMA_001", "date": "2025-01-01", "kpi_value": 10.0, "spend_value": 100.0},
        {"geo_unit_id": "DMA_002", "date": "2025-01-01", "kpi_value": 12.0, "spend_value": 80.0},
    ]
    report = profile_geo_kpi_spend_data(sample_rows)
    failed: list[str] = []
    if report.profiler_status != ProfilerStatus.PASS:
        failed.append("smoke_full_panel_pass")
    if not report.claim_boundary.ready_for_downstream_diagnostics:
        failed.append("smoke_ready_for_downstream")
    if report.claim_boundary.design_feasibility_authorized:
        failed.append("smoke_no_design_feasibility")

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "deterministic_geo_kpi_spend_data_profiler",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "implementation_scope": "deterministic_schema_coverage_profile_only",
        "public_api": "profile_geo_kpi_spend_data",
        "input_modes_supported": [m.value for m in InputMode if m != InputMode.UNKNOWN],
        "profiler_statuses": [s.value for s in ProfilerStatus],
        "claim_boundaries": [c.value for c in ClaimBoundary],
        "missing_spend_treated_as_zero": False,
        "missing_kpi_treated_as_zero": False,
        "hidden_imputation_allowed": False,
        "duplicate_rows_silently_aggregated": False,
        "spend_contrast_feasibility_computed": False,
        "design_feasibility_computed": False,
        "power_computed": False,
        "mde_computed": False,
        "p_value_computed": False,
        "confidence_interval_computed": False,
        "lift_computed": False,
        "roi_computed": False,
        "method_recommendation_computed": False,
        "portfolio_tiering_computed": False,
        "mmm_calibration_authorized": False,
        "production_authorization_granted": False,
        "llm_decisioning_authorized": False,
        "profiler_implementation_notes_applied": list(PROFILER_IMPLEMENTATION_NOTES_APPLIED),
        "tests_added": [
            "test_full_panel_valid_minimal_data_ready_for_downstream_diagnostics",
            "test_missing_kpi_blocks",
            "test_missing_geo_blocks",
            "test_missing_date_blocks",
            "test_sample_schema_mode_schema_only_no_final_claims",
            "test_ballpark_mode_provisional_only_no_final_claims",
            "test_missing_spend_not_treated_as_zero",
            "test_zero_spend_counted_separately_from_missing",
            "test_duplicate_geo_time_rows_reported",
            "test_planned_test_start_date_flags_overlapping_historical_rows",
            "test_no_unauthorized_design_inference_or_production_claims",
            "test_rate_kpi_note_does_not_block_by_default",
            "test_dma_same_state_not_blocked_when_geo_units_distinct",
            "test_country_aggregate_one_unit_no_randomized_design_readiness_claim",
            "test_no_fixture_specific_branching",
        ],
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
