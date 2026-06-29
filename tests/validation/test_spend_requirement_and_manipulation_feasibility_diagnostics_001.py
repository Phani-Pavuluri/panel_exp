"""Tests for SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.geo_kpi_spend_data_profiler_001 import (
    GeoKpiSpendProfilerInput,
    profile_geo_kpi_spend_data,
)
from panel_exp.validation.spend_requirement_and_manipulation_feasibility_diagnostics_001 import (
    AdvisoryFlag,
    FeasibilityStatus,
    ManipulationFeasibilityOutcome,
    ManipulationOption,
    ResponseBridgeSource,
    ResponseBridgeStatus,
    SpendRequirementManipulationFeasibilityConfig,
    evaluate_spend_manipulation_feasibility,
    evaluate_spend_requirement_and_manipulation_feasibility,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO / "docs/track_d/archives/SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001_REPORT.md"


def _rows(
    geo_count: int = 5,
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
    spend: float = 1000.0,
    **extra: object,
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for i in range(1, geo_count + 1):
        for w in weeks:
            row: dict[str, object] = {
                "geo_unit_id": f"DMA_{i:03d}",
                "date": w,
                "kpi_value": float(i),
                "spend_value": spend + i,
            }
            row.update(extra)
            out.append(row)
    return out


def _cfg(**kwargs: object) -> SpendRequirementManipulationFeasibilityConfig:
    return SpendRequirementManipulationFeasibilityConfig(**kwargs)


def test_missing_spend_blocks_or_warns() -> None:
    rows = [{"geo_unit_id": "DMA_001", "date": "2025-01-01", "kpi_value": 1.0}]
    report = evaluate_spend_requirement_and_manipulation_feasibility(rows)
    assert report.spend_data_readiness.missing_spend_count >= 1
    assert any(c.outcome == ManipulationFeasibilityOutcome.BLOCKED_MISSING_SPEND for c in report.manipulation_feasibility.candidates)


def test_zero_spend_not_treated_as_missing() -> None:
    rows = _rows()
    for r in rows:
        r["spend_value"] = 0.0
    report = evaluate_spend_requirement_and_manipulation_feasibility(rows, _cfg(required_spend_delta=10.0))
    assert report.spend_data_readiness.zero_spend_count > 0
    assert report.spend_data_readiness.missing_spend_count == 0


def test_missing_spend_not_treated_as_zero() -> None:
    rows = [{"geo_unit_id": "DMA_001", "date": "2025-01-01", "kpi_value": 1.0, "spend_value": None}]
    report = evaluate_spend_requirement_and_manipulation_feasibility(rows)
    assert report.spend_data_readiness.missing_spend_count == 1
    assert report.spend_data_readiness.zero_spend_count == 0


def test_negative_spend_flagged() -> None:
    rows = _rows(spend=-50.0)
    report = evaluate_spend_requirement_and_manipulation_feasibility(rows)
    assert report.spend_data_readiness.negative_spend_count > 0
    assert any(i.code == "negative_spend_without_credit_flag" for i in report.spend_data_readiness.issues)


def test_planned_observed_not_silently_mixed() -> None:
    rows = _rows()
    rows[0]["is_planned"] = True
    rows[1]["is_observed"] = True
    report = evaluate_spend_requirement_and_manipulation_feasibility(rows)
    assert any(i.code == "planned_observed_mixed" for i in report.spend_data_readiness.issues)


def test_sample_schema_not_final_readiness() -> None:
    profile = profile_geo_kpi_spend_data(
        GeoKpiSpendProfilerInput(sample_schema_columns=["geo_unit_id", "date", "spend_value"])
    )
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        [], _cfg(profile_report=profile, required_spend_delta=100.0)
    )
    assert report.spend_data_readiness.sample_schema_mode
    assert report.feasibility_status == FeasibilityStatus.PROVISIONAL
    assert not report.planning_boundary.ready_for_downstream_power_diagnostics


def test_ballpark_provisional_only() -> None:
    profile = profile_geo_kpi_spend_data(GeoKpiSpendProfilerInput(ballpark={"historical_weeks_available": 20}))
    report = evaluate_spend_requirement_and_manipulation_feasibility([], _cfg(profile_report=profile))
    assert report.spend_data_readiness.ballpark_mode
    assert report.feasibility_status == FeasibilityStatus.PROVISIONAL


def test_baseline_from_explicit_window() -> None:
    rows = _rows()
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        rows,
        _cfg(
            baseline_window_start="2025-01-01",
            baseline_window_end="2025-01-29",
            required_spend_delta=100.0,
        ),
    )
    overall = next(s for s in report.baseline_spend_inventory.summaries if s.level == "overall")
    assert report.baseline_spend_inventory.baseline_window_derived
    assert overall.baseline_mean_weekly_spend is not None


def test_baseline_from_pre_period_before_planned_start() -> None:
    rows = _rows()
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        rows, _cfg(planned_test_start_date="2025-02-01", required_spend_delta=100.0)
    )
    assert report.baseline_spend_inventory.baseline_window_derived
    assert report.spend_data_readiness.baseline_window_status == "pre_period_before_planned_test_start"


def test_max_reducible_equals_baseline_floored_at_zero() -> None:
    rows = _rows(spend=500.0)
    report = evaluate_spend_requirement_and_manipulation_feasibility(rows, _cfg(required_spend_delta=10.0))
    overall = next(s for s in report.baseline_spend_inventory.summaries if s.level == "overall")
    assert overall.max_reducible_spend is not None
    assert overall.max_reducible_spend >= 0


def test_cell_channel_summaries_when_fields_exist() -> None:
    rows = _rows()
    for r in rows:
        r["cell_id"] = "cell_a"
        r["channel"] = "search"
    report = evaluate_spend_requirement_and_manipulation_feasibility(rows, _cfg(required_spend_delta=50.0))
    levels = {s.level for s in report.baseline_spend_inventory.summaries}
    assert "cell" in levels
    assert "channel" in levels


def test_required_spend_delta_supplied() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        _rows(), _cfg(required_spend_delta=250.0, response_bridge_source=ResponseBridgeSource.USER_PROVIDED_REQUIRED_SPEND_DELTA)
    )
    assert report.response_bridge.response_bridge_status == ResponseBridgeStatus.REQUIRED_SPEND_DELTA_SUPPLIED
    assert AdvisoryFlag.REQUIRED_SPEND_DELTA_SUPPLIED in report.advisory_flags


def test_kpi_mde_advisory_translation() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        _rows(),
        _cfg(
            kpi_mde=500.0,
            kpi_unit="conversions",
            expected_kpi_per_dollar=0.005,
            response_bridge_source=ResponseBridgeSource.BACK_OF_NAPKIN_USER_ASSUMPTION,
        ),
    )
    assert report.response_bridge.required_spend_delta == 100000.0
    assert AdvisoryFlag.BACK_OF_NAPKIN_ASSUMPTION_USED in report.advisory_flags


def test_mmm_response_curve_advisory_flag() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        _rows(),
        _cfg(
            kpi_mde=100.0,
            expected_kpi_per_dollar=0.01,
            response_bridge_source=ResponseBridgeSource.MMM_RESPONSE_CURVE,
        ),
    )
    assert AdvisoryFlag.MMM_ADVISORY_SIGNAL_USED in report.advisory_flags


def test_mmm_roms_advisory_flag() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        _rows(),
        _cfg(
            kpi_mde=100.0,
            expected_kpi_per_dollar=0.01,
            response_bridge_source=ResponseBridgeSource.MMM_ROMS,
        ),
    )
    assert AdvisoryFlag.MMM_ADVISORY_SIGNAL_USED in report.advisory_flags


def test_proxy_level_mismatch_flag() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        _rows(),
        _cfg(
            kpi_mde=100.0,
            expected_kpi_per_dollar=0.01,
            response_bridge_source=ResponseBridgeSource.PROXY_RESPONSE_CURVE,
            proxy_level="national",
            requested_test_level="dma",
        ),
    )
    assert AdvisoryFlag.PROXY_RESPONSE_USED in report.advisory_flags
    assert AdvisoryFlag.PROXY_LEVEL_MISMATCH in report.advisory_flags


def test_out_of_mmm_support_flag() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        _rows(),
        _cfg(
            kpi_mde=500.0,
            expected_kpi_per_dollar=0.001,
            response_bridge_source=ResponseBridgeSource.MMM_RESPONSE_CURVE,
            mmm_curve_support_max_spend=1000.0,
        ),
    )
    assert AdvisoryFlag.OUT_OF_MMM_SUPPORT in report.advisory_flags


def test_business_response_risk_when_expected_below_mde() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        _rows(),
        _cfg(
            kpi_mde=500.0,
            expected_kpi_per_dollar=0.005,
            advisory_expected_kpi_response=180.0,
            response_bridge_source=ResponseBridgeSource.MMM_RESPONSE_CURVE,
        ),
    )
    assert AdvisoryFlag.BUSINESS_RESPONSE_RISK in report.advisory_flags


def test_required_spend_unknown_without_bridge() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(_rows())
    assert report.response_bridge.response_bridge_status == ResponseBridgeStatus.REQUIRED_SPEND_DELTA_UNKNOWN
    assert AdvisoryFlag.REQUIRED_SPEND_DELTA_UNKNOWN in report.advisory_flags


def test_go_dark_feasible_when_max_reducible_sufficient() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(_rows(spend=2000.0), _cfg(required_spend_delta=100.0))
    go_dark = next(c for c in report.manipulation_feasibility.candidates if c.manipulation_option == ManipulationOption.GO_DARK)
    assert go_dark.outcome == ManipulationFeasibilityOutcome.GO_DARK_FEASIBLE


def test_go_dark_insufficient_when_required_exceeds_max() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(_rows(spend=50.0), _cfg(required_spend_delta=50000.0))
    go_dark = next(c for c in report.manipulation_feasibility.candidates if c.manipulation_option == ManipulationOption.GO_DARK)
    assert go_dark.outcome == ManipulationFeasibilityOutcome.GO_DARK_INSUFFICIENT_BASELINE_SPEND


def test_heavy_up_multiplier_computed() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(_rows(spend=1000.0), _cfg(required_spend_delta=1000.0))
    heavy = next(c for c in report.manipulation_feasibility.candidates if c.manipulation_option == ManipulationOption.HEAVY_UP)
    assert heavy.required_heavy_up_spend is not None
    assert heavy.required_heavy_up_multiplier is not None
    assert heavy.required_heavy_up_multiplier > 1.0


def test_heavy_up_out_of_historical_support() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        _rows(spend=100.0),
        _cfg(required_spend_delta=100000.0, far_above_historical_max_multiplier=1.1),
    )
    heavy = next(c for c in report.manipulation_feasibility.candidates if c.manipulation_option == ManipulationOption.HEAVY_UP)
    assert heavy.outcome == ManipulationFeasibilityOutcome.HEAVY_UP_OUT_OF_HISTORICAL_SUPPORT


def test_go_live_feasible_from_near_zero() -> None:
    rows = _rows()
    for r in rows:
        r["spend_value"] = 0.0
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        rows, _cfg(required_spend_delta=500.0, go_live_baseline_near_zero_threshold=1.0)
    )
    live = next(c for c in report.manipulation_feasibility.candidates if c.manipulation_option == ManipulationOption.GO_LIVE)
    assert live.outcome == ManipulationFeasibilityOutcome.GO_LIVE_FEASIBLE


def test_go_live_conflicts_with_substantial_baseline() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(_rows(spend=5000.0), _cfg(required_spend_delta=100.0))
    live = next(c for c in report.manipulation_feasibility.candidates if c.manipulation_option == ManipulationOption.GO_LIVE)
    assert live.outcome == ManipulationFeasibilityOutcome.GO_LIVE_CONFLICTS_WITH_EXISTING_BASELINE_SPEND


def test_budget_reallocation_mapping_required() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(_rows(), _cfg(required_spend_delta=100.0))
    realloc = next(
        c for c in report.manipulation_feasibility.candidates if c.manipulation_option == ManipulationOption.BUDGET_REALLOCATION
    )
    assert realloc.outcome == ManipulationFeasibilityOutcome.BUDGET_REALLOCATION_MAPPING_INCOMPLETE


def test_budget_reallocation_feasible_with_mapping() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        _rows(),
        _cfg(
            required_spend_delta=100.0,
            budget_source_channel="search",
            budget_destination_channel="social",
        ),
    )
    realloc = next(
        c for c in report.manipulation_feasibility.candidates if c.manipulation_option == ManipulationOption.BUDGET_REALLOCATION
    )
    assert realloc.outcome == ManipulationFeasibilityOutcome.BUDGET_REALLOCATION_FEASIBLE


def test_dosage_contrast_feasible() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        _rows(),
        _cfg(required_spend_delta=200.0, low_spend_policy=500.0, high_spend_policy=1000.0),
    )
    dosage = next(c for c in report.manipulation_feasibility.candidates if c.manipulation_option == ManipulationOption.DOSAGE_CONTRAST)
    assert dosage.outcome == ManipulationFeasibilityOutcome.DOSAGE_CONTRAST_FEASIBLE


def test_control_contamination_and_estimand_shift() -> None:
    rows = _rows()
    rows[0]["cell_role"] = "control"
    rows[0]["period_role"] = "treatment"
    report = evaluate_spend_requirement_and_manipulation_feasibility(
        rows, _cfg(required_spend_delta=100.0, control_manipulated=True)
    )
    assert AdvisoryFlag.CONTROL_CONTAMINATION_RISK in report.advisory_flags
    assert AdvisoryFlag.ESTIMAND_SHIFT_REQUIRED in report.advisory_flags
    assert not report.planning_boundary.standard_go_dark_interpretation_allowed


def test_alias_evaluate_spend_manipulation_feasibility() -> None:
    report = evaluate_spend_manipulation_feasibility(_rows(), _cfg(required_spend_delta=10.0))
    assert report.artifact_id == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001"


def test_no_unauthorized_claims() -> None:
    report = evaluate_spend_requirement_and_manipulation_feasibility(_rows(), _cfg(required_spend_delta=50.0))
    pb = report.planning_boundary
    assert not pb.runtime_power_authorized
    assert not pb.mde_authorized
    assert not pb.p_value_authorized
    assert not pb.confidence_interval_authorized
    assert not pb.lift_authorized
    assert not pb.roi_authorized
    assert not pb.budget_optimization_authorized
    assert not pb.candidate_design_authorized
    assert not pb.treatment_control_assignment_authorized
    assert not pb.estimator_inference_authorized
    assert not pb.mmm_calibration_authorized
    assert not pb.production_authorization_granted
    assert not pb.llm_decisioning_authorized
    assert not pb.final_design_recommendation_authorized


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001"
    assert data["failed_scenarios"] == []
    assert data["mmm_runtime_calls_implemented"] is False
    assert data["final_verdict"] == (
        "spend_requirement_and_manipulation_feasibility_diagnostics_implemented_no_power_design_roi_or_production_authorization"
    )
