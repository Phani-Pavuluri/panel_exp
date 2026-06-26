"""GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001 deterministic unit/market feasibility."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from panel_exp.validation.geo_kpi_spend_data_profiler_001 import (
    ClaimBoundary,
    GeoKpiSpendDataProfileReport,
    GeoKpiSpendProfilerConfig,
    GeoKpiSpendProfilerInput,
    InputMode,
    ProfilerStatus,
    profile_geo_kpi_spend_data,
)

_ARTIFACT_ID = "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "geo_unit_market_feasibility_diagnostics_implemented_no_design_inference_or_production_authorization"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001_summary.json"
)
RECOMMENDED_NEXT_ARTIFACT = "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001"


class GeoUnitFeasibilityStatus(str, Enum):
    READY_FOR_DOWNSTREAM_DESIGN_DIAGNOSTICS = "READY_FOR_DOWNSTREAM_DESIGN_DIAGNOSTICS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    PROVISIONAL = "PROVISIONAL"
    BLOCKED = "BLOCKED"


class GeoMarketFeasibilityStatus(str, Enum):
    READY = "READY"
    WARNING = "WARNING"
    PROVISIONAL = "PROVISIONAL"
    BLOCKED = "BLOCKED"


class GeoUnitFeasibilitySeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"


class GeoUnitMarketClaimBoundary(str, Enum):
    UNIT_MARKET_DIAGNOSTIC_ONLY = "UNIT_MARKET_DIAGNOSTIC_ONLY"
    READY_FOR_DOWNSTREAM_DESIGN_DIAGNOSTICS = "READY_FOR_DOWNSTREAM_DESIGN_DIAGNOSTICS"
    PROVISIONAL_ONLY = "PROVISIONAL_ONLY"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class GeoUnitMarketFeasibilityConfig:
    min_geo_units_for_downstream_diagnostics: int = 2
    recommended_min_geo_units_warning: int = 10
    min_time_periods_for_downstream_diagnostics: int = 4
    recommended_min_time_periods_warning: int = 8
    coverage_imbalance_ratio_threshold: float = 0.5
    rows_for_coverage_balance: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class GeoUnitFeasibilityIssue:
    code: str
    message: str
    severity: GeoUnitFeasibilitySeverity
    field: str | None = None


@dataclass(frozen=True)
class GeoUnitMarketClaimBoundaryReport:
    claim_boundary: GeoUnitMarketClaimBoundary
    ready_for_downstream_design_diagnostics: bool = False
    final_experiment_feasibility_authorized: bool = False
    candidate_design_authorized: bool = False
    treatment_control_assignment_authorized: bool = False
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
class GeoUnitEligibilitySummary:
    geo_unit_count: int
    eligible_geo_unit_count: int
    missing_geo_unit_count: int
    sample_geo_units: tuple[str, ...]
    geo_unit_type: str | None


@dataclass(frozen=True)
class GeoHistoryAvailabilityReport:
    time_period_count: int
    historical_period_count: int
    coverage_completeness_ratio: float | None
    missing_geo_time_signals: int


@dataclass(frozen=True)
class GeoCoverageBalanceReport:
    min_periods_per_geo: int | None
    max_periods_per_geo: int | None
    imbalance_ratio: float | None
    materially_imbalanced: bool
    missing_geo_time_cells: int


@dataclass(frozen=True)
class GeoMarketStructureReport:
    provided_geo_level: str | None
    unique_market_count: int
    market_feasibility_status: GeoMarketFeasibilityStatus
    single_aggregate_warning: bool
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class GeoUnitMarketFeasibilityReport:
    artifact_id: str
    feasibility_status: GeoUnitFeasibilityStatus
    unit_eligibility_summary: GeoUnitEligibilitySummary
    history_availability_report: GeoHistoryAvailabilityReport
    coverage_balance_report: GeoCoverageBalanceReport
    market_structure_report: GeoMarketStructureReport
    issues: tuple[GeoUnitFeasibilityIssue, ...]
    claim_boundary: GeoUnitMarketClaimBoundaryReport
    profiler_status_acknowledged: ProfilerStatus
    profiler_input_mode_acknowledged: InputMode
    duplicate_rows_acknowledged: int = 0


def _blocked_claim() -> GeoUnitMarketClaimBoundaryReport:
    return GeoUnitMarketClaimBoundaryReport(claim_boundary=GeoUnitMarketClaimBoundary.BLOCKED)


def _provisional_claim() -> GeoUnitMarketClaimBoundaryReport:
    return GeoUnitMarketClaimBoundaryReport(
        claim_boundary=GeoUnitMarketClaimBoundary.PROVISIONAL_ONLY,
    )


def _diagnostic_only_claim() -> GeoUnitMarketClaimBoundaryReport:
    return GeoUnitMarketClaimBoundaryReport(
        claim_boundary=GeoUnitMarketClaimBoundary.UNIT_MARKET_DIAGNOSTIC_ONLY,
    )


def _ready_claim() -> GeoUnitMarketClaimBoundaryReport:
    return GeoUnitMarketClaimBoundaryReport(
        claim_boundary=GeoUnitMarketClaimBoundary.READY_FOR_DOWNSTREAM_DESIGN_DIAGNOSTICS,
        ready_for_downstream_design_diagnostics=True,
    )


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


def _compute_balance(
    profile_report: GeoKpiSpendDataProfileReport,
    config: GeoUnitMarketFeasibilityConfig,
) -> GeoCoverageBalanceReport:
    rows = config.rows_for_coverage_balance
    geo_col = profile_report.column_mapping_report.geo_column
    date_col = profile_report.column_mapping_report.date_column
    kpi_col = profile_report.column_mapping_report.kpi_column

    if not rows or not geo_col or not date_col:
        missing_cells = profile_report.missingness_report.missing_geo_count + (
            profile_report.missingness_report.missing_date_count
        )
        return GeoCoverageBalanceReport(None, None, None, False, missing_cells)

    periods_by_geo: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        geo = row.get(geo_col)
        dt = row.get(date_col)
        if _is_missing(geo) or _is_missing(dt):
            continue
        periods_by_geo[str(geo)].add(str(dt))

    if not periods_by_geo:
        return GeoCoverageBalanceReport(0, 0, None, False, 0)

    counts = [len(periods) for periods in periods_by_geo.values()]
    min_p, max_p = min(counts), max(counts)
    ratio = (min_p / max_p) if max_p else None
    materially_imbalanced = ratio is not None and ratio < config.coverage_imbalance_ratio_threshold

    missing_cells = 0
    if kpi_col:
        for row in rows:
            if not _is_missing(row.get(geo_col)) and not _is_missing(row.get(date_col)) and _is_missing(row.get(kpi_col)):
                missing_cells += 1

    return GeoCoverageBalanceReport(min_p, max_p, ratio, materially_imbalanced, missing_cells)


def _compute_eligibility(
    profile_report: GeoKpiSpendDataProfileReport,
    config: GeoUnitMarketFeasibilityConfig,
) -> GeoUnitEligibilitySummary:
    inventory = profile_report.geo_unit_inventory_report
    rows = config.rows_for_coverage_balance
    geo_col = profile_report.column_mapping_report.geo_column
    kpi_col = profile_report.column_mapping_report.kpi_column
    date_col = profile_report.column_mapping_report.date_column

    eligible_count = 0
    if rows and geo_col and kpi_col and date_col:
        geo_periods_with_kpi: dict[str, int] = defaultdict(int)
        for row in rows:
            geo = row.get(geo_col)
            if _is_missing(geo):
                continue
            if not _is_missing(row.get(date_col)) and not _is_missing(row.get(kpi_col)):
                geo_periods_with_kpi[str(geo)] += 1
        eligible_count = sum(1 for count in geo_periods_with_kpi.values() if count > 0)
    else:
        if (
            inventory.geo_unit_count > 0
            and profile_report.kpi_coverage_report.non_missing_count > 0
            and profile_report.geo_time_coverage_report.distinct_period_count > 0
            and inventory.missing_geo_count == 0
        ):
            eligible_count = inventory.geo_unit_count

    return GeoUnitEligibilitySummary(
        geo_unit_count=inventory.geo_unit_count,
        eligible_geo_unit_count=eligible_count,
        missing_geo_unit_count=inventory.missing_geo_count,
        sample_geo_units=inventory.sample_geo_units,
        geo_unit_type=inventory.geo_unit_type,
    )


def evaluate_geo_unit_market_feasibility(
    profile_report: GeoKpiSpendDataProfileReport,
    config: GeoUnitMarketFeasibilityConfig | None = None,
) -> GeoUnitMarketFeasibilityReport:
    """Evaluate geo unit/market feasibility from profiler output. Side-effect free."""
    cfg = config or GeoUnitMarketFeasibilityConfig()
    issues: list[GeoUnitFeasibilityIssue] = []

    input_mode = profile_report.input_mode_report.input_mode
    profiler_status = profile_report.profiler_status
    inventory = profile_report.geo_unit_inventory_report
    coverage = profile_report.geo_time_coverage_report
    duplicates = profile_report.duplicate_row_report.duplicate_geo_time_count

    if duplicates > 0:
        issues.append(
            GeoUnitFeasibilityIssue(
                "duplicate_geo_time_rows",
                f"Profiler reported {duplicates} duplicate geo/time row groups",
                GeoUnitFeasibilitySeverity.BLOCKING if profiler_status == ProfilerStatus.BLOCKED else GeoUnitFeasibilitySeverity.WARNING,
            )
        )

    if input_mode == InputMode.BALLPARK:
        return GeoUnitMarketFeasibilityReport(
            artifact_id=_ARTIFACT_ID,
            feasibility_status=GeoUnitFeasibilityStatus.PROVISIONAL,
            unit_eligibility_summary=GeoUnitEligibilitySummary(
                inventory.geo_unit_count, 0, 0, inventory.sample_geo_units, inventory.geo_unit_type
            ),
            history_availability_report=GeoHistoryAvailabilityReport(0, 0, None, 0),
            coverage_balance_report=GeoCoverageBalanceReport(None, None, None, False, 0),
            market_structure_report=GeoMarketStructureReport(
                inventory.geo_unit_type, inventory.geo_unit_count, GeoMarketFeasibilityStatus.PROVISIONAL, False
            ),
            issues=tuple(issues),
            claim_boundary=_provisional_claim(),
            profiler_status_acknowledged=profiler_status,
            profiler_input_mode_acknowledged=input_mode,
            duplicate_rows_acknowledged=duplicates,
        )

    if input_mode == InputMode.SAMPLE_SCHEMA:
        issues.append(
            GeoUnitFeasibilityIssue(
                "sample_schema_only",
                "Sample schema input cannot be upgraded to downstream design diagnostics readiness",
                GeoUnitFeasibilitySeverity.WARNING,
            )
        )
        return GeoUnitMarketFeasibilityReport(
            artifact_id=_ARTIFACT_ID,
            feasibility_status=GeoUnitFeasibilityStatus.PROVISIONAL,
            unit_eligibility_summary=GeoUnitEligibilitySummary(0, 0, 0, (), inventory.geo_unit_type),
            history_availability_report=GeoHistoryAvailabilityReport(0, 0, None, 0),
            coverage_balance_report=GeoCoverageBalanceReport(None, None, None, False, 0),
            market_structure_report=GeoMarketStructureReport(
                inventory.geo_unit_type, 0, GeoMarketFeasibilityStatus.PROVISIONAL, False,
                ("schema_only_no_row_level_coverage",),
            ),
            issues=tuple(issues),
            claim_boundary=_diagnostic_only_claim(),
            profiler_status_acknowledged=profiler_status,
            profiler_input_mode_acknowledged=input_mode,
            duplicate_rows_acknowledged=duplicates,
        )

    if profiler_status == ProfilerStatus.BLOCKED or not profile_report.claim_boundary.ready_for_downstream_diagnostics:
        issues.append(
            GeoUnitFeasibilityIssue(
                "profiler_blocked",
                "Blocked profiler output cannot be upgraded by unit/market diagnostics",
                GeoUnitFeasibilitySeverity.BLOCKING,
            )
        )
        return GeoUnitMarketFeasibilityReport(
            artifact_id=_ARTIFACT_ID,
            feasibility_status=GeoUnitFeasibilityStatus.BLOCKED,
            unit_eligibility_summary=_compute_eligibility(profile_report, cfg),
            history_availability_report=GeoHistoryAvailabilityReport(
                coverage.distinct_period_count, coverage.distinct_period_count, None, 0
            ),
            coverage_balance_report=_compute_balance(profile_report, cfg),
            market_structure_report=GeoMarketStructureReport(
                inventory.geo_unit_type, inventory.geo_unit_count, GeoMarketFeasibilityStatus.BLOCKED, False
            ),
            issues=tuple(issues),
            claim_boundary=_blocked_claim(),
            profiler_status_acknowledged=profiler_status,
            profiler_input_mode_acknowledged=input_mode,
            duplicate_rows_acknowledged=duplicates,
        )

    eligibility = _compute_eligibility(profile_report, cfg)
    balance = _compute_balance(profile_report, cfg)
    time_period_count = coverage.distinct_period_count
    geo_count = inventory.geo_unit_count

    completeness = None
    if geo_count > 0 and time_period_count > 0:
        observed_cells = profile_report.kpi_coverage_report.non_missing_count
        expected_cells = geo_count * time_period_count
        if expected_cells > 0:
            completeness = round(observed_cells / expected_cells, 4)

    history_report = GeoHistoryAvailabilityReport(
        time_period_count=time_period_count,
        historical_period_count=time_period_count,
        coverage_completeness_ratio=completeness,
        missing_geo_time_signals=balance.missing_geo_time_cells
        + profile_report.missingness_report.missing_geo_count
        + profile_report.missingness_report.missing_date_count,
    )

    geo_type = (inventory.geo_unit_type or "").lower()
    single_aggregate = geo_type in {"country", "country_region_aggregate", "country_aggregate"} and geo_count == 1
    market_notes: list[str] = [
        "DMAs within the same state are valid distinct units when geo IDs are mutually exclusive. "
        "Evaluate at the provided geo level without silent upgrade or downgrade.",
    ]
    if single_aggregate:
        market_notes.append("single_country_aggregate_not_randomized_geo_planning_ready")
        issues.append(
            GeoUnitFeasibilityIssue(
                "country_aggregate_single_unit",
                "Single country/region aggregate does not imply randomized geo planning readiness",
                GeoUnitFeasibilitySeverity.INFO,
            )
        )
    if geo_type in {"custom_cluster", "custom"} and geo_count > 0:
        market_notes.append("custom_cluster_accepted_at_provided_geo_level")

    market_report = GeoMarketStructureReport(
        provided_geo_level=inventory.geo_unit_type,
        unique_market_count=geo_count,
        market_feasibility_status=GeoMarketFeasibilityStatus.READY,
        single_aggregate_warning=single_aggregate,
        notes=tuple(market_notes),
    )

    if geo_count == 0:
        issues.append(
            GeoUnitFeasibilityIssue("zero_geo_units", "No geo units available", GeoUnitFeasibilitySeverity.BLOCKING)
        )
    elif geo_count == 1:
        issues.append(
            GeoUnitFeasibilityIssue(
                "one_geo_unit_randomized_geo_planning",
                "One geo unit is insufficient for randomized geo planning diagnostics readiness",
                GeoUnitFeasibilitySeverity.BLOCKING,
            )
        )
    elif geo_count < cfg.min_geo_units_for_downstream_diagnostics:
        issues.append(
            GeoUnitFeasibilityIssue(
                "too_few_geo_units",
                f"Geo unit count {geo_count} below minimum {cfg.min_geo_units_for_downstream_diagnostics}",
                GeoUnitFeasibilitySeverity.BLOCKING,
            )
        )
    elif geo_count < cfg.recommended_min_geo_units_warning:
        issues.append(
            GeoUnitFeasibilityIssue(
                "low_geo_unit_count_warning",
                f"Geo unit count {geo_count} below recommended {cfg.recommended_min_geo_units_warning}",
                GeoUnitFeasibilitySeverity.WARNING,
            )
        )

    if time_period_count < cfg.min_time_periods_for_downstream_diagnostics:
        issues.append(
            GeoUnitFeasibilityIssue(
                "insufficient_time_periods",
                f"Time period count {time_period_count} below minimum {cfg.min_time_periods_for_downstream_diagnostics}",
                GeoUnitFeasibilitySeverity.BLOCKING,
            )
        )
    elif time_period_count < cfg.recommended_min_time_periods_warning:
        issues.append(
            GeoUnitFeasibilityIssue(
                "low_time_period_coverage_warning",
                f"Time period count {time_period_count} below recommended {cfg.recommended_min_time_periods_warning}",
                GeoUnitFeasibilitySeverity.WARNING,
            )
        )

    if balance.materially_imbalanced:
        issues.append(
            GeoUnitFeasibilityIssue(
                "coverage_imbalance",
                "Geo/time coverage is materially imbalanced across units",
                GeoUnitFeasibilitySeverity.WARNING,
            )
        )

    if balance.missing_geo_time_cells > 0:
        issues.append(
            GeoUnitFeasibilityIssue(
                "missing_geo_time_coverage",
                f"Missing geo/time KPI coverage in {balance.missing_geo_time_cells} cells",
                GeoUnitFeasibilitySeverity.WARNING,
            )
        )

    blocking = any(i.severity == GeoUnitFeasibilitySeverity.BLOCKING for i in issues)
    warnings = any(i.severity == GeoUnitFeasibilitySeverity.WARNING for i in issues)

    if blocking or single_aggregate and geo_count == 1:
        status = GeoUnitFeasibilityStatus.BLOCKED
        claim = _blocked_claim()
        market_report = GeoMarketStructureReport(
            market_report.provided_geo_level,
            market_report.unique_market_count,
            GeoMarketFeasibilityStatus.BLOCKED,
            market_report.single_aggregate_warning,
            market_report.notes,
        )
    elif warnings or profiler_status == ProfilerStatus.PASS_WITH_WARNINGS:
        status = GeoUnitFeasibilityStatus.PASS_WITH_WARNINGS
        claim = _ready_claim()
        market_report = GeoMarketStructureReport(
            market_report.provided_geo_level,
            market_report.unique_market_count,
            GeoMarketFeasibilityStatus.WARNING,
            market_report.single_aggregate_warning,
            market_report.notes,
        )
    else:
        status = GeoUnitFeasibilityStatus.READY_FOR_DOWNSTREAM_DESIGN_DIAGNOSTICS
        claim = _ready_claim()

    return GeoUnitMarketFeasibilityReport(
        artifact_id=_ARTIFACT_ID,
        feasibility_status=status,
        unit_eligibility_summary=eligibility,
        history_availability_report=history_report,
        coverage_balance_report=balance,
        market_structure_report=market_report,
        issues=tuple(issues),
        claim_boundary=claim,
        profiler_status_acknowledged=profiler_status,
        profiler_input_mode_acknowledged=input_mode,
        duplicate_rows_acknowledged=duplicates,
    )


def evaluate_geo_unit_market_feasibility_from_panel(
    input_data: GeoKpiSpendProfilerInput | list[dict[str, Any]] | Any,
    profiler_config: GeoKpiSpendProfilerConfig | None = None,
    feasibility_config: GeoUnitMarketFeasibilityConfig | None = None,
) -> GeoUnitMarketFeasibilityReport:
    """Profile panel data then evaluate unit/market feasibility."""
    profile_report = profile_geo_kpi_spend_data(input_data, profiler_config)
    cfg = feasibility_config or GeoUnitMarketFeasibilityConfig()
    if cfg.rows_for_coverage_balance is None and isinstance(input_data, list):
        cfg = GeoUnitMarketFeasibilityConfig(
            min_geo_units_for_downstream_diagnostics=cfg.min_geo_units_for_downstream_diagnostics,
            recommended_min_geo_units_warning=cfg.recommended_min_geo_units_warning,
            min_time_periods_for_downstream_diagnostics=cfg.min_time_periods_for_downstream_diagnostics,
            recommended_min_time_periods_warning=cfg.recommended_min_time_periods_warning,
            coverage_imbalance_ratio_threshold=cfg.coverage_imbalance_ratio_threshold,
            rows_for_coverage_balance=input_data,
        )
    elif cfg.rows_for_coverage_balance is None and isinstance(input_data, GeoKpiSpendProfilerInput) and input_data.rows:
        cfg = GeoUnitMarketFeasibilityConfig(
            min_geo_units_for_downstream_diagnostics=cfg.min_geo_units_for_downstream_diagnostics,
            recommended_min_geo_units_warning=cfg.recommended_min_geo_units_warning,
            min_time_periods_for_downstream_diagnostics=cfg.min_time_periods_for_downstream_diagnostics,
            recommended_min_time_periods_warning=cfg.recommended_min_time_periods_warning,
            coverage_imbalance_ratio_threshold=cfg.coverage_imbalance_ratio_threshold,
            rows_for_coverage_balance=input_data.rows,
        )
    return evaluate_geo_unit_market_feasibility(profile_report, cfg)


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    weeks = (
        "2025-01-01",
        "2025-01-08",
        "2025-01-15",
        "2025-01-22",
        "2025-01-29",
        "2025-02-05",
        "2025-02-12",
        "2025-02-19",
    )
    rows = [
        {"geo_unit_id": f"DMA_{i:03d}", "date": week, "kpi_value": float(i)}
        for i in range(1, 12)
        for week in weeks
    ]
    profile = profile_geo_kpi_spend_data(rows)
    report = evaluate_geo_unit_market_feasibility_from_panel(rows)
    failed: list[str] = []
    if report.feasibility_status != GeoUnitFeasibilityStatus.READY_FOR_DOWNSTREAM_DESIGN_DIAGNOSTICS:
        failed.append("smoke_ready_status")
    if not report.claim_boundary.ready_for_downstream_design_diagnostics:
        failed.append("smoke_ready_claim")
    if report.claim_boundary.final_experiment_feasibility_authorized:
        failed.append("smoke_no_final_feasibility")

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "deterministic_geo_unit_market_feasibility_diagnostics",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "implementation_scope": "deterministic_unit_market_coverage_diagnostics_only",
        "public_api": "evaluate_geo_unit_market_feasibility",
        "depends_on": ["GEO_KPI_SPEND_DATA_PROFILER_001"],
        "input_contract": "GeoKpiSpendDataProfileReport",
        "diagnostic_statuses": [s.value for s in GeoUnitFeasibilityStatus],
        "claim_boundaries": [c.value for c in GeoUnitMarketClaimBoundary],
        "unit_inventory_diagnostics_implemented": True,
        "historical_coverage_diagnostics_implemented": True,
        "geo_time_balance_diagnostics_implemented": True,
        "market_structure_notes_implemented": True,
        "sample_schema_not_upgraded": True,
        "ballpark_not_upgraded": True,
        "blocked_profiler_not_upgraded": True,
        "design_feasibility_computed": False,
        "candidate_design_computed": False,
        "treatment_control_assignment_computed": False,
        "spend_contrast_feasibility_computed": False,
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
        "tests_added": [
            "test_valid_full_panel_ready_for_downstream_design_diagnostics",
            "test_blocked_profiler_report_remains_blocked",
            "test_sample_schema_not_upgraded",
            "test_ballpark_remains_provisional",
            "test_one_geo_unit_blocks_randomized_geo_readiness",
            "test_too_few_geo_units_threshold_behavior",
            "test_insufficient_time_periods_threshold_behavior",
            "test_coverage_imbalance_warning",
            "test_missing_geo_time_coverage_issue",
            "test_duplicate_rows_acknowledged",
            "test_dma_same_state_not_blocked_when_geo_units_distinct",
            "test_country_aggregate_one_unit_no_randomized_geo_readiness_claim",
            "test_custom_cluster_unique_ids_accepted_as_provided_units",
            "test_no_unauthorized_design_inference_or_production_claims",
            "test_no_fixture_specific_branching",
            "test_configurable_thresholds_work",
        ],
        "recommended_next_artifact": RECOMMENDED_NEXT_ARTIFACT,
        "generated_at": datetime.now().isoformat(),
        "git_commit": _git_commit(),
        "failed_scenarios": failed,
        "profiler_smoke_status": profile.profiler_status.value,
        "feasibility_smoke_status": report.feasibility_status.value,
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
