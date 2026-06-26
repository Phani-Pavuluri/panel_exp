"""Tests for GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.geo_kpi_spend_data_profiler_001 import (
    GeoKpiSpendProfilerInput,
    InputMode,
    ProfilerStatus,
    profile_geo_kpi_spend_data,
)
from panel_exp.validation.geo_unit_market_feasibility_diagnostics_001 import (
    GeoUnitFeasibilityStatus,
    GeoUnitMarketClaimBoundary,
    GeoUnitMarketFeasibilityConfig,
    evaluate_geo_unit_market_feasibility,
    evaluate_geo_unit_market_feasibility_from_panel,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001_summary.json"
_REPORT = _REPO / "docs/track_d/GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001_REPORT.md"


def _panel_rows(
    geo_count: int = 12,
    weeks: tuple[str, ...] = (
        "2025-01-01",
        "2025-01-08",
        "2025-01-15",
        "2025-01-22",
        "2025-01-29",
        "2025-02-05",
        "2025-02-12",
        "2025-02-19",
    ),
    geo_prefix: str = "DMA",
    extra_fields: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for i in range(1, geo_count + 1):
        for week in weeks:
            row: dict[str, object] = {
                "geo_unit_id": f"{geo_prefix}_{i:03d}",
                "date": week,
                "kpi_value": float(i),
            }
            if extra_fields:
                row.update(extra_fields)
            rows.append(row)
    return rows


def test_valid_full_panel_ready_for_downstream_design_diagnostics() -> None:
    rows = _panel_rows(geo_count=15)
    profile = profile_geo_kpi_spend_data(rows)
    report = evaluate_geo_unit_market_feasibility_from_panel(
        rows,
        feasibility_config=GeoUnitMarketFeasibilityConfig(recommended_min_geo_units_warning=12),
    )
    assert profile.claim_boundary.ready_for_downstream_diagnostics
    assert report.feasibility_status == GeoUnitFeasibilityStatus.READY_FOR_DOWNSTREAM_DESIGN_DIAGNOSTICS
    assert report.claim_boundary.ready_for_downstream_design_diagnostics


def test_blocked_profiler_report_remains_blocked() -> None:
    rows = [{"geo_unit_id": "DMA_001", "date": "2025-01-01"}]
    profile = profile_geo_kpi_spend_data(rows)
    report = evaluate_geo_unit_market_feasibility(profile)
    assert profile.profiler_status == ProfilerStatus.BLOCKED
    assert report.feasibility_status == GeoUnitFeasibilityStatus.BLOCKED
    assert not report.claim_boundary.ready_for_downstream_design_diagnostics


def test_sample_schema_not_upgraded() -> None:
    profile = profile_geo_kpi_spend_data(
        GeoKpiSpendProfilerInput(sample_schema_columns=["geo_unit_id", "date", "kpi_value"])
    )
    report = evaluate_geo_unit_market_feasibility(profile)
    assert profile.input_mode_report.input_mode == InputMode.SAMPLE_SCHEMA
    assert report.feasibility_status == GeoUnitFeasibilityStatus.PROVISIONAL
    assert not report.claim_boundary.ready_for_downstream_design_diagnostics
    assert report.claim_boundary.claim_boundary == GeoUnitMarketClaimBoundary.UNIT_MARKET_DIAGNOSTIC_ONLY


def test_ballpark_remains_provisional() -> None:
    profile = profile_geo_kpi_spend_data(
        GeoKpiSpendProfilerInput(ballpark={"number_of_geo_units": 20, "historical_weeks_available": 52})
    )
    report = evaluate_geo_unit_market_feasibility(profile)
    assert report.feasibility_status == GeoUnitFeasibilityStatus.PROVISIONAL
    assert report.claim_boundary.claim_boundary == GeoUnitMarketClaimBoundary.PROVISIONAL_ONLY


def test_one_geo_unit_blocks_randomized_geo_readiness() -> None:
    rows = _panel_rows(geo_count=1)
    profile = profile_geo_kpi_spend_data(rows)
    report = evaluate_geo_unit_market_feasibility_from_panel(rows)
    assert report.feasibility_status == GeoUnitFeasibilityStatus.BLOCKED
    assert any(i.code == "one_geo_unit_randomized_geo_planning" for i in report.issues)


def test_too_few_geo_units_threshold_behavior() -> None:
    rows = _panel_rows(geo_count=1)
    profile = profile_geo_kpi_spend_data(rows)
    cfg = GeoUnitMarketFeasibilityConfig(min_geo_units_for_downstream_diagnostics=3)
    report = evaluate_geo_unit_market_feasibility(profile, cfg)
    assert report.feasibility_status == GeoUnitFeasibilityStatus.BLOCKED
    assert any(i.code in {"one_geo_unit_randomized_geo_planning", "too_few_geo_units"} for i in report.issues)


def test_insufficient_time_periods_threshold_behavior() -> None:
    rows = _panel_rows(weeks=("2025-01-01", "2025-01-08"))
    profile = profile_geo_kpi_spend_data(rows)
    report = evaluate_geo_unit_market_feasibility_from_panel(
        rows,
        feasibility_config=GeoUnitMarketFeasibilityConfig(min_time_periods_for_downstream_diagnostics=4),
    )
    assert report.feasibility_status == GeoUnitFeasibilityStatus.BLOCKED
    assert any(i.code == "insufficient_time_periods" for i in report.issues)


def test_coverage_imbalance_warning() -> None:
    rows = []
    for week in ("2025-01-01", "2025-01-08", "2025-01-15", "2025-01-22"):
        rows.append({"geo_unit_id": "DMA_001", "date": week, "kpi_value": 1.0})
    for week in ("2025-01-01",):
        rows.append({"geo_unit_id": "DMA_002", "date": week, "kpi_value": 1.0})
    for i in range(3, 12):
        for week in ("2025-01-01", "2025-01-08", "2025-01-15", "2025-01-22"):
            rows.append({"geo_unit_id": f"DMA_{i:03d}", "date": week, "kpi_value": float(i)})
    profile = profile_geo_kpi_spend_data(rows)
    report = evaluate_geo_unit_market_feasibility(
        profile,
        GeoUnitMarketFeasibilityConfig(rows_for_coverage_balance=rows, coverage_imbalance_ratio_threshold=0.5),
    )
    assert report.coverage_balance_report.materially_imbalanced
    assert any(i.code == "coverage_imbalance" for i in report.issues)


def test_missing_geo_time_coverage_issue() -> None:
    rows = _panel_rows(geo_count=4)
    rows[0] = {**rows[0], "kpi_value": None}
    profile = profile_geo_kpi_spend_data(rows)
    report = evaluate_geo_unit_market_feasibility(
        profile,
        GeoUnitMarketFeasibilityConfig(rows_for_coverage_balance=rows),
    )
    assert any(i.code == "missing_geo_time_coverage" for i in report.issues)


def test_duplicate_rows_acknowledged() -> None:
    rows = [
        {"geo_unit_id": "DMA_001", "date": "2025-01-01", "kpi_value": 1.0},
        {"geo_unit_id": "DMA_001", "date": "2025-01-01", "kpi_value": 2.0},
        {"geo_unit_id": "DMA_002", "date": "2025-01-01", "kpi_value": 3.0},
    ]
    profile = profile_geo_kpi_spend_data(rows)
    report = evaluate_geo_unit_market_feasibility(profile)
    assert report.duplicate_rows_acknowledged >= 1
    assert any(i.code == "duplicate_geo_time_rows" for i in report.issues)


def test_dma_same_state_not_blocked_when_geo_units_distinct() -> None:
    rows = _panel_rows(geo_count=12, extra_fields={"state": "CA"})
    profile = profile_geo_kpi_spend_data(GeoKpiSpendProfilerInput(rows=rows, geo_unit_type="DMA"))
    report = evaluate_geo_unit_market_feasibility_from_panel(rows)
    assert report.feasibility_status in {
        GeoUnitFeasibilityStatus.READY_FOR_DOWNSTREAM_DESIGN_DIAGNOSTICS,
        GeoUnitFeasibilityStatus.PASS_WITH_WARNINGS,
    }
    assert not any(i.code == "one_geo_unit_randomized_geo_planning" for i in report.issues)


def test_country_aggregate_one_unit_no_randomized_geo_readiness_claim() -> None:
    rows = _panel_rows(geo_count=1, geo_prefix="US")
    profile = profile_geo_kpi_spend_data(
        GeoKpiSpendProfilerInput(rows=rows, geo_unit_type="country_region_aggregate")
    )
    report = evaluate_geo_unit_market_feasibility(profile)
    assert not report.claim_boundary.ready_for_downstream_design_diagnostics
    assert any(i.code == "country_aggregate_single_unit" for i in report.issues)


def test_custom_cluster_unique_ids_accepted_as_provided_units() -> None:
    rows = _panel_rows(geo_count=8, geo_prefix="CLUSTER")
    profile = profile_geo_kpi_spend_data(
        GeoKpiSpendProfilerInput(rows=rows, geo_unit_type="custom_cluster")
    )
    report = evaluate_geo_unit_market_feasibility(
        profile,
        GeoUnitMarketFeasibilityConfig(rows_for_coverage_balance=rows),
    )
    assert report.unit_eligibility_summary.geo_unit_count == 8
    assert "custom_cluster_accepted_at_provided_geo_level" in report.market_structure_report.notes


def test_no_unauthorized_design_inference_or_production_claims() -> None:
    rows = _panel_rows()
    report = evaluate_geo_unit_market_feasibility_from_panel(rows)
    boundary = report.claim_boundary
    assert not boundary.final_experiment_feasibility_authorized
    assert not boundary.candidate_design_authorized
    assert not boundary.treatment_control_assignment_authorized
    assert not boundary.spend_contrast_feasibility_authorized
    assert not boundary.power_authorized
    assert not boundary.mde_authorized
    assert not boundary.p_value_authorized
    assert not boundary.confidence_interval_authorized
    assert not boundary.lift_authorized
    assert not boundary.roi_authorized
    assert not boundary.method_recommendation_authorized
    assert not boundary.portfolio_tiering_authorized
    assert not boundary.mmm_calibration_authorized
    assert not boundary.production_authorization_granted
    assert not boundary.llm_decisioning_authorized


def test_no_fixture_specific_branching() -> None:
    source = Path(_REPO / "panel_exp/validation/geo_unit_market_feasibility_diagnostics_001.py").read_text(
        encoding="utf-8"
    )
    assert "fixture_id" not in source
    assert "GP-001" not in source
    assert "BP-001" not in source


def test_configurable_thresholds_work() -> None:
    rows = _panel_rows(geo_count=3, weeks=("2025-01-01", "2025-01-08", "2025-01-15", "2025-01-22"))
    profile = profile_geo_kpi_spend_data(rows)
    report = evaluate_geo_unit_market_feasibility(
        profile,
        GeoUnitMarketFeasibilityConfig(
            min_geo_units_for_downstream_diagnostics=2,
            recommended_min_geo_units_warning=20,
            min_time_periods_for_downstream_diagnostics=2,
            rows_for_coverage_balance=rows,
        ),
    )
    assert report.feasibility_status in {
        GeoUnitFeasibilityStatus.READY_FOR_DOWNSTREAM_DESIGN_DIAGNOSTICS,
        GeoUnitFeasibilityStatus.PASS_WITH_WARNINGS,
    }
    assert any(i.code == "low_geo_unit_count_warning" for i in report.issues)


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001"
    assert data["failed_scenarios"] == []
    assert data["final_verdict"] == (
        "geo_unit_market_feasibility_diagnostics_implemented_no_design_inference_or_production_authorization"
    )
