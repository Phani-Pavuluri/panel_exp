"""Tests for POWER_MDE_DIAGNOSTICS_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.geo_kpi_spend_data_profiler_001 import ProfilerStatus
from panel_exp.validation.power_mde_diagnostics_runtime_001 import (
    MdeScope,
    PowerMdeDiagnosticsConfig,
    PowerMdeMode,
    PowerMdeStatus,
    evaluate_power_mde_diagnostics,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/POWER_MDE_DIAGNOSTICS_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/POWER_MDE_DIAGNOSTICS_RUNTIME_001_REPORT.md"


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
    kpi: float = 100.0,
    **extra: object,
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for i in range(1, geo_count + 1):
        for w in weeks:
            row: dict[str, object] = {
                "geo_unit_id": f"DMA_{i:03d}",
                "date": w,
                "kpi_value": kpi + i,
            }
            row.update(extra)
            out.append(row)
    return out


def _cfg(**kwargs: object) -> PowerMdeDiagnosticsConfig:
    base = {
        "profiler_status": ProfilerStatus.PASS.value,
        "geo_feasibility_status": "PASS",
    }
    base.update(kwargs)
    return PowerMdeDiagnosticsConfig(**base)


def _ready_cfg(**kwargs: object) -> PowerMdeDiagnosticsConfig:
    base: dict[str, object] = {
        "spend_handoff_status": "SPEND_HANDOFF_READY_FOR_POWER_DIAGNOSTICS",
        "required_spend_delta": 500.0,
        "required_spend_delta_source": "REQUIRED_SPEND_DELTA_SUPPLIED",
        "kpi_unit": "conversions",
        "absolute_mde": 500.0,
        "mde_scope": MdeScope.CELL_LEVEL,
    }
    base.update(kwargs)
    return _cfg(**base)


def test_blocked_profiler_blocks_runtime() -> None:
    report = evaluate_power_mde_diagnostics(_rows(), _cfg(profiler_status=ProfilerStatus.BLOCKED.value))
    assert report.status == PowerMdeStatus.POWER_MDE_BLOCKED_BY_DATA_READINESS
    assert report.mode == PowerMdeMode.NOT_EVALUATED


def test_blocked_geo_feasibility_blocks_runtime() -> None:
    report = evaluate_power_mde_diagnostics(_rows(), _cfg(geo_feasibility_status="BLOCKED"))
    assert report.status == PowerMdeStatus.POWER_MDE_BLOCKED_BY_GEO_FEASIBILITY
    assert report.mode == PowerMdeMode.NOT_EVALUATED


def test_blocked_spend_handoff_blocks_spend_confirmed_mode() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(),
        _ready_cfg(spend_handoff_status="SPEND_HANDOFF_BLOCKED_BY_SPEND_DATA"),
    )
    assert not report.spend_compatibility_report.spend_confirmed_mode_allowed
    assert report.mode != PowerMdeMode.SPEND_CONFIRMED_SENSITIVITY


def test_missing_spend_handoff_allows_kpi_only_when_configured() -> None:
    report = evaluate_power_mde_diagnostics(_rows(), _cfg(allow_kpi_only_when_spend_handoff_missing=True))
    assert report.mode == PowerMdeMode.KPI_ONLY_SENSITIVITY
    assert report.noise_history_report.kpi_history_valid


def test_required_spend_unknown_prevents_spend_confirmed_mode() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(),
        _ready_cfg(
            spend_handoff_status="SPEND_HANDOFF_READY_FOR_POWER_DIAGNOSTICS",
            required_spend_delta_source="REQUIRED_SPEND_DELTA_UNKNOWN",
        ),
    )
    assert not report.spend_compatibility_report.spend_confirmed_mode_allowed


def test_missing_kpi_blocks_runtime() -> None:
    rows = [{"geo_unit_id": "DMA_001", "date": "2025-01-01"}]
    report = evaluate_power_mde_diagnostics(rows, _cfg())
    assert report.status == PowerMdeStatus.POWER_MDE_BLOCKED_BY_DATA_READINESS
    assert report.noise_history_report.missing_kpi_count >= 1


def test_missing_kpi_not_treated_as_zero() -> None:
    rows = [{"geo_unit_id": "DMA_001", "date": "2025-01-01", "kpi_value": None}]
    report = evaluate_power_mde_diagnostics(rows, _cfg())
    assert report.noise_history_report.missing_kpi_count == 1
    assert report.noise_history_report.zero_kpi_count == 0


def test_zero_kpi_counted_separately() -> None:
    rows = _rows()
    for r in rows:
        r["kpi_value"] = 0.0
    report = evaluate_power_mde_diagnostics(rows, _cfg())
    assert report.noise_history_report.zero_kpi_count > 0
    assert report.noise_history_report.missing_kpi_count == 0


def test_negative_kpi_blocked_by_default() -> None:
    rows = _rows(kpi=-5.0)
    report = evaluate_power_mde_diagnostics(rows, _cfg())
    assert report.noise_history_report.negative_kpi_count > 0
    assert any(i.code == "negative_kpi_not_allowed" for i in report.issues)


def test_minimum_pre_period_length_checked() -> None:
    short_weeks = ("2025-01-01", "2025-01-08")
    report = evaluate_power_mde_diagnostics(_rows(weeks=short_weeks), _cfg(minimum_pre_period_count=8))
    assert not report.noise_history_report.minimum_pre_period_length_met
    assert any(i.code == "minimum_pre_period_not_met" for i in report.issues)


def test_baseline_descriptive_stats_computed() -> None:
    report = evaluate_power_mde_diagnostics(_rows(), _cfg())
    n = report.noise_history_report
    assert n.baseline_kpi_mean is not None
    assert n.baseline_kpi_median is not None
    assert n.baseline_kpi_std is not None
    assert n.baseline_kpi_variance is not None
    assert n.baseline_kpi_p10 is not None
    assert n.baseline_kpi_p90 is not None
    assert n.coefficient_of_variation is not None


def test_time_geo_balance_summarized() -> None:
    report = evaluate_power_mde_diagnostics(_rows(), _cfg())
    assert report.noise_history_report.time_balance_status in {"balanced", "imbalanced", "unknown"}
    assert report.noise_history_report.geo_balance_status in {"balanced", "imbalanced", "unknown"}


def test_kpi_unit_preserved() -> None:
    report = evaluate_power_mde_diagnostics(_rows(), _ready_cfg(kpi_unit="conversions"))
    assert report.mde_representation_report.kpi_unit_preserved
    assert report.mde_representation_report.kpi_unit == "conversions"


def test_absolute_mde_preserved() -> None:
    report = evaluate_power_mde_diagnostics(_rows(), _ready_cfg(absolute_mde=500.0))
    assert report.mde_representation_report.absolute_mde_present


def test_relative_mde_preserved() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(), _ready_cfg(relative_mde=0.03, absolute_mde=None, baseline_kpi_level=1000.0)
    )
    assert report.mde_representation_report.relative_mde_present


def test_relative_mde_without_baseline_warns() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(), _ready_cfg(relative_mde=0.03, absolute_mde=None, baseline_kpi_level=None)
    )
    assert any(i.code == "relative_mde_without_baseline" for i in report.mde_representation_report.issues)


def test_absolute_relative_conflict_flagged() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(), _ready_cfg(absolute_mde=500.0, relative_mde=0.05, baseline_kpi_level=1000.0)
    )
    assert report.mde_representation_report.absolute_relative_conflict


def test_cell_level_vs_aggregate_conflict_warned() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(), _ready_cfg(mde_scope=MdeScope.UNKNOWN, absolute_mde=500.0, relative_mde=0.05)
    )
    assert any(i.code == "mde_scope_unknown" for i in report.mde_representation_report.issues)


def test_no_final_mde_computed() -> None:
    report = evaluate_power_mde_diagnostics(_rows(), _ready_cfg())
    assert not report.claim_boundary_report.mde_computed
    assert not report.claim_boundary_report.power_computed


def test_missing_cell_structure_prevents_design_cell_mode() -> None:
    report = evaluate_power_mde_diagnostics(_rows(), _ready_cfg())
    assert report.cell_structure_report.cell_structure_status == "missing"
    assert report.mode != PowerMdeMode.DESIGN_CELL_SENSITIVITY


def test_cell_ids_and_roles_detected() -> None:
    rows = _rows(cell_id="cell_a", cell_role="treated")
    rows += _rows(cell_id="cell_b", cell_role="control")
    report = evaluate_power_mde_diagnostics(rows, _ready_cfg())
    assert report.cell_structure_report.cell_ids_present
    assert report.cell_structure_report.cell_roles_present


def test_single_treated_control_detected() -> None:
    rows: list[dict[str, object]] = []
    for w in (
        "2025-01-01", "2025-01-08", "2025-01-15", "2025-01-22",
        "2025-01-29", "2025-02-05", "2025-02-12", "2025-02-19",
    ):
        rows.append({"geo_unit_id": "DMA_001", "date": w, "kpi_value": 100.0, "cell_id": "t", "cell_role": "treated"})
        rows.append({"geo_unit_id": "DMA_002", "date": w, "kpi_value": 90.0, "cell_id": "c", "cell_role": "control"})
    report = evaluate_power_mde_diagnostics(rows, _ready_cfg())
    assert report.cell_structure_report.treated_cell_count >= 1
    assert report.cell_structure_report.control_cell_count >= 1


def test_multi_cell_detected() -> None:
    rows: list[dict[str, object]] = []
    for w in (
        "2025-01-01", "2025-01-08", "2025-01-15", "2025-01-22",
        "2025-01-29", "2025-02-05", "2025-02-12", "2025-02-19",
    ):
        for cid, role in (("t1", "treated"), ("t2", "treated"), ("c1", "control")):
            rows.append({"geo_unit_id": cid, "date": w, "kpi_value": 100.0, "cell_id": cid, "cell_role": role})
    report = evaluate_power_mde_diagnostics(rows, _ready_cfg())
    assert report.cell_structure_report.multi_cell_detected


def test_common_control_detected() -> None:
    rows: list[dict[str, object]] = []
    for w in (
        "2025-01-01", "2025-01-08", "2025-01-15", "2025-01-22",
        "2025-01-29", "2025-02-05", "2025-02-12", "2025-02-19",
    ):
        for cid, role in (("t1", "treated"), ("t2", "treated"), ("c1", "control")):
            rows.append({"geo_unit_id": cid, "date": w, "kpi_value": 100.0, "cell_id": cid, "cell_role": role})
    report = evaluate_power_mde_diagnostics(rows, _ready_cfg())
    assert report.cell_structure_report.common_control_detected


def test_dosage_design_detected() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(design_type="dosage_contrast"),
        _ready_cfg(dosage_contrast_estimand_required=True),
    )
    assert report.cell_structure_report.dosage_design_detected


def test_difference_in_policy_detected() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(design_type="difference_in_policy"),
        _ready_cfg(difference_in_policy_required=True),
    )
    assert report.cell_structure_report.difference_in_policy_detected


def test_required_spend_delta_source_preserved() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(),
        _ready_cfg(required_spend_delta_source="MMM_RESPONSE_CURVE", mmm_advisory_used=True),
    )
    assert report.spend_compatibility_report.required_spend_delta_source == "MMM_RESPONSE_CURVE"
    assert report.spend_compatibility_report.mmm_advisory_used


def test_proxy_provenance_preserved() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(),
        _ready_cfg(response_bridge_source="PROXY_RESPONSE_CURVE", proxy_response_used=True),
    )
    assert report.spend_compatibility_report.proxy_response_used


def test_back_of_napkin_provenance_preserved() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(),
        _cfg(back_of_napkin_assumption_used=True, allow_exploratory_back_of_napkin=True),
    )
    assert report.spend_compatibility_report.back_of_napkin_assumption_used
    assert report.mode == PowerMdeMode.EXPLORATORY_BACK_OF_NAPKIN


def test_business_response_risk_preserved() -> None:
    report = evaluate_power_mde_diagnostics(_rows(), _ready_cfg(business_response_risk=True))
    assert report.spend_compatibility_report.business_response_risk


def test_candidate_manipulation_options_preserved() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(),
        _ready_cfg(candidate_manipulation_options=("HEAVY_UP", "GO_DARK")),
    )
    assert report.spend_compatibility_report.candidate_manipulation_options == ("HEAVY_UP", "GO_DARK")


def test_spend_feasibility_not_treated_as_power() -> None:
    report = evaluate_power_mde_diagnostics(_rows(), _ready_cfg(ready_for_downstream_power_diagnostics=True))
    assert report.spend_compatibility_report.ready_for_downstream_power_diagnostics
    assert not report.claim_boundary_report.power_computed


def test_dosage_contrast_routes_to_dosage_mode() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(cell_id="c1", cell_role="treated"),
        _ready_cfg(dosage_contrast_estimand_required=True),
    )
    assert report.mode == PowerMdeMode.DOSAGE_CONTRAST_SENSITIVITY


def test_difference_in_policy_routes_to_dosage_mode() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(),
        _ready_cfg(difference_in_policy_required=True),
    )
    assert report.mode == PowerMdeMode.DOSAGE_CONTRAST_SENSITIVITY


def test_control_contamination_blocks_standard_go_dark() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(),
        _ready_cfg(control_contamination_flags=("CONTROL_CELL_MANIPULATED",)),
    )
    assert report.estimand_compatibility_report.blocked_standard_go_dark_interpretation
    assert not report.estimand_compatibility_report.standard_go_dark_interpretation_allowed


def test_method_suitability_review_required_status() -> None:
    report = evaluate_power_mde_diagnostics(
        _rows(cell_id="c1", cell_role="treated"),
        _ready_cfg(method_suitability_review_required=True, dosage_contrast_estimand_required=True),
    )
    assert report.status == PowerMdeStatus.POWER_MDE_REQUIRES_METHOD_SUITABILITY_REVIEW


def test_ready_for_runtime_not_powered() -> None:
    rows: list[dict[str, object]] = []
    for w in (
        "2025-01-01", "2025-01-08", "2025-01-15", "2025-01-22",
        "2025-01-29", "2025-02-05", "2025-02-12", "2025-02-19",
    ):
        rows.append({"geo_unit_id": "DMA_001", "date": w, "kpi_value": 100.0, "cell_id": "t", "cell_role": "treated"})
        rows.append({"geo_unit_id": "DMA_002", "date": w, "kpi_value": 90.0, "cell_id": "c", "cell_role": "control"})
    report = evaluate_power_mde_diagnostics(rows, _ready_cfg())
    assert report.status in {
        PowerMdeStatus.POWER_MDE_READY_FOR_DIAGNOSTIC_RUNTIME,
        PowerMdeStatus.POWER_MDE_READY_WITH_WARNINGS,
        PowerMdeStatus.POWER_MDE_REQUIRES_METHOD_SUITABILITY_REVIEW,
    }
    cb = report.claim_boundary_report
    assert not cb.power_computed
    assert not cb.mde_computed
    assert not cb.p_value_computed
    assert not cb.confidence_interval_computed
    assert not cb.lift_computed
    assert not cb.roi_computed
    assert not cb.budget_optimization_authorized
    assert not cb.candidate_design_authorized
    assert not cb.treatment_control_assignment_authorized
    assert not cb.estimator_inference_authorized
    assert not cb.mmm_runtime_calls_implemented
    assert not cb.mmm_calibration_authorized
    assert not cb.production_authorization_granted
    assert not cb.llm_decisioning_authorized


def test_claim_boundary_flags() -> None:
    report = evaluate_power_mde_diagnostics(_rows(), _cfg())
    cb = report.claim_boundary_report
    assert cb.runtime_power_mde_diagnostics_implemented
    assert cb.readiness_diagnostics_implemented
    assert cb.descriptive_noise_summary_implemented
    assert not cb.power_computed
    assert not cb.mde_computed


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "POWER_MDE_DIAGNOSTICS_RUNTIME_001"
    assert data["runtime_power_mde_diagnostics_implemented"] is True
    assert data["power_computed"] is False
    assert data["mde_computed"] is False
    assert data["recommended_next_artifact"] == "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001"
