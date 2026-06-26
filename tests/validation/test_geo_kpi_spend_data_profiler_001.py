"""Tests for GEO_KPI_SPEND_DATA_PROFILER_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.geo_kpi_spend_data_profiler_001 import (
    ClaimBoundary,
    GeoKpiSpendProfilerConfig,
    GeoKpiSpendProfilerInput,
    InputMode,
    ProfilerStatus,
    profile_geo_kpi_spend_data,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/GEO_KPI_SPEND_DATA_PROFILER_001_summary.json"
_REPORT = _REPO / "docs/track_d/GEO_KPI_SPEND_DATA_PROFILER_001_REPORT.md"


def _minimal_rows(**overrides: object) -> list[dict[str, object]]:
    base = [
        {"geo_unit_id": "DMA_001", "date": "2025-01-01", "kpi_value": 10.0, "spend_value": 100.0},
        {"geo_unit_id": "DMA_002", "date": "2025-01-01", "kpi_value": 12.0, "spend_value": 80.0},
        {"geo_unit_id": "DMA_001", "date": "2025-01-08", "kpi_value": 11.0, "spend_value": 90.0},
        {"geo_unit_id": "DMA_002", "date": "2025-01-08", "kpi_value": 13.0, "spend_value": 70.0},
    ]
    if overrides:
        base[0] = {**base[0], **overrides}
    return base


def test_full_panel_valid_minimal_data_ready_for_downstream_diagnostics() -> None:
    report = profile_geo_kpi_spend_data(_minimal_rows())
    assert report.profiler_status == ProfilerStatus.PASS
    assert report.claim_boundary.ready_for_downstream_diagnostics
    assert report.claim_boundary.claim_boundary == ClaimBoundary.READY_FOR_DOWNSTREAM_DIAGNOSTICS
    assert report.geo_unit_inventory_report.geo_unit_count == 2


def test_missing_kpi_blocks() -> None:
    rows = [{"geo_unit_id": "DMA_001", "date": "2025-01-01", "spend_value": 1.0}]
    report = profile_geo_kpi_spend_data(rows)
    assert report.profiler_status == ProfilerStatus.BLOCKED
    assert not report.claim_boundary.ready_for_downstream_diagnostics


def test_missing_geo_blocks() -> None:
    rows = [{"date": "2025-01-01", "kpi_value": 1.0}]
    report = profile_geo_kpi_spend_data(rows)
    assert report.profiler_status == ProfilerStatus.BLOCKED


def test_missing_date_blocks() -> None:
    rows = [{"geo_unit_id": "DMA_001", "kpi_value": 1.0}]
    report = profile_geo_kpi_spend_data(rows)
    assert report.profiler_status == ProfilerStatus.BLOCKED


def test_sample_schema_mode_schema_only_no_final_claims() -> None:
    report = profile_geo_kpi_spend_data(
        GeoKpiSpendProfilerInput(sample_schema_columns=["geo_unit_id", "date", "kpi_value"])
    )
    assert report.input_mode_report.input_mode == InputMode.SAMPLE_SCHEMA
    assert report.claim_boundary.schema_feedback_available
    assert not report.claim_boundary.ready_for_downstream_diagnostics
    assert report.claim_boundary.claim_boundary == ClaimBoundary.SCHEMA_ONLY


def test_ballpark_mode_provisional_only_no_final_claims() -> None:
    report = profile_geo_kpi_spend_data(
        GeoKpiSpendProfilerInput(
            ballpark={
                "number_of_geo_units": 50,
                "time_grain": "weekly",
                "historical_weeks_available": 52,
                "rough_kpi_volume": 1000,
                "rough_spend": 50000,
                "planned_duration": 8,
            }
        )
    )
    assert report.input_mode_report.input_mode == InputMode.BALLPARK
    assert report.claim_boundary.provisional_planning_input_available
    assert not report.claim_boundary.ready_for_downstream_diagnostics
    assert report.profiler_status == ProfilerStatus.PROVISIONAL


def test_missing_spend_not_treated_as_zero() -> None:
    rows = [
        {"geo_unit_id": "DMA_001", "date": "2025-01-01", "kpi_value": 10.0},
        {"geo_unit_id": "DMA_002", "date": "2025-01-01", "kpi_value": 12.0},
    ]
    report = profile_geo_kpi_spend_data(rows)
    assert not report.spend_coverage_report.spend_present
    assert report.missingness_report.missing_spend_treated_as_zero is False
    assert report.spend_coverage_report.non_missing_count == 0


def test_zero_spend_counted_separately_from_missing() -> None:
    rows = [
        {"geo_unit_id": "DMA_001", "date": "2025-01-01", "kpi_value": 10.0, "spend_value": 0.0},
        {"geo_unit_id": "DMA_002", "date": "2025-01-01", "kpi_value": 12.0, "spend_value": None},
    ]
    report = profile_geo_kpi_spend_data(rows)
    assert report.spend_coverage_report.zero_count == 1
    assert report.spend_coverage_report.missing_count == 1


def test_duplicate_geo_time_rows_reported() -> None:
    rows = [
        {"geo_unit_id": "DMA_001", "date": "2025-01-01", "kpi_value": 10.0},
        {"geo_unit_id": "DMA_001", "date": "2025-01-01", "kpi_value": 11.0},
    ]
    report = profile_geo_kpi_spend_data(rows)
    assert report.duplicate_row_report.duplicate_geo_time_count == 1
    assert report.profiler_status == ProfilerStatus.BLOCKED


def test_planned_test_start_date_flags_overlapping_historical_rows() -> None:
    rows = [
        {"geo_unit_id": "DMA_001", "date": "2025-02-01", "kpi_value": 10.0},
        {"geo_unit_id": "DMA_002", "date": "2025-02-08", "kpi_value": 12.0, "period_type": "planned"},
    ]
    config = GeoKpiSpendProfilerConfig(planned_test_start_date="2025-02-01")
    report = profile_geo_kpi_spend_data(rows, config)
    assert report.geo_time_coverage_report.rows_on_or_after_planned_start == 1
    assert report.geo_time_coverage_report.planned_future_labeled_rows == 1
    assert any(i.code == "planned_test_start_overlap" for i in report.data_quality_issues)


def test_no_unauthorized_design_inference_or_production_claims() -> None:
    report = profile_geo_kpi_spend_data(_minimal_rows())
    boundary = report.claim_boundary
    assert not boundary.design_feasibility_authorized
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


def test_rate_kpi_note_does_not_block_by_default() -> None:
    rows = [
        {"geo_unit_id": "DMA_001", "date": "2025-01-01", "conversion_rate": 0.05},
        {"geo_unit_id": "DMA_002", "date": "2025-01-08", "conversion_rate": 0.06},
    ]
    report = profile_geo_kpi_spend_data(
        GeoKpiSpendProfilerInput(rows=rows, column_mapping={"kpi": "conversion_rate"}),
    )
    assert report.profiler_status in {ProfilerStatus.PASS, ProfilerStatus.PASS_WITH_WARNINGS}
    assert report.kpi_note is not None
    assert any(i.code == "rate_kpi_diagnostic_note" for i in report.data_quality_issues)


def test_dma_same_state_not_blocked_when_geo_units_distinct() -> None:
    rows = [
        {"geo_unit_id": "DMA_001", "state": "CA", "date": "2025-01-01", "kpi_value": 10.0},
        {"geo_unit_id": "DMA_002", "state": "CA", "date": "2025-01-01", "kpi_value": 12.0},
        {"geo_unit_id": "DMA_001", "state": "CA", "date": "2025-01-08", "kpi_value": 11.0},
        {"geo_unit_id": "DMA_002", "state": "CA", "date": "2025-01-08", "kpi_value": 13.0},
    ]
    report = profile_geo_kpi_spend_data(
        GeoKpiSpendProfilerInput(rows=rows, geo_unit_type="DMA"),
    )
    assert report.profiler_status == ProfilerStatus.PASS
    assert report.geo_unit_inventory_report.geo_unit_count == 2


def test_country_aggregate_one_unit_no_randomized_design_readiness_claim() -> None:
    rows = [{"geo_unit_id": "US", "date": "2025-01-01", "kpi_value": 100.0}]
    report = profile_geo_kpi_spend_data(
        GeoKpiSpendProfilerInput(rows=rows, geo_unit_type="country_region_aggregate"),
    )
    assert not report.claim_boundary.design_feasibility_authorized
    assert any(i.code == "country_aggregate_single_unit" for i in report.data_quality_issues)


def test_no_fixture_specific_branching() -> None:
    source = Path(_REPO / "panel_exp/validation/geo_kpi_spend_data_profiler_001.py").read_text(encoding="utf-8")
    assert "fixture_id" not in source
    assert "GP-001" not in source
    assert "BP-001" not in source


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "GEO_KPI_SPEND_DATA_PROFILER_001"
    assert data["failed_scenarios"] == []
    assert data["final_verdict"] == (
        "geo_kpi_spend_data_profiler_implemented_no_design_inference_or_production_authorization"
    )
