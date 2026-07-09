"""Tests for GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001."""

from __future__ import annotations

from datetime import date

import pytest

from panel_exp.validation.post_test_spend_readiness_adapter_runtime_001 import (
    PostTestExperimentType,
    PostTestSpendInput,
    PostTestSpendReadinessStatus,
    build_post_test_spend_evidence,
    build_trusted_readout_spend_handoff,
)


def _base_rows() -> list[dict]:
    return [
        {
            "geo_unit_id": "g1",
            "date": "2025-03-01",
            "spend_value": 100.0,
            "cell_id": "T1",
            "cell_role": "treatment",
            "channel": "search",
            "campaign": "c1",
            "currency": "USD",
        },
        {
            "geo_unit_id": "g1",
            "date": "2025-03-08",
            "spend_value": 50.0,
            "cell_id": "T1",
            "cell_role": "treatment",
            "channel": "search",
            "campaign": "c1",
            "currency": "USD",
        },
        {
            "geo_unit_id": "g2",
            "date": "2025-03-15",
            "spend_value": 80.0,
            "cell_id": "C1",
            "cell_role": "control",
            "channel": "search",
            "campaign": "c1",
            "currency": "USD",
        },
        {
            "geo_unit_id": "g3",
            "date": "2025-02-01",
            "spend_value": 999.0,
            "cell_id": "T1",
            "cell_role": "treatment",
            "channel": "search",
            "campaign": "c1",
            "currency": "USD",
        },
    ]


def _assignment_rows() -> list[dict]:
    return [
        {"geo_unit_id": "g1", "cell_id": "T1", "cell_role": "treatment"},
        {"geo_unit_id": "g2", "cell_id": "C1", "cell_role": "control"},
        {"geo_unit_id": "g3", "cell_id": "T1", "cell_role": "treatment"},
    ]


def _input(**overrides):
    defaults = {
        "experiment_id": "exp-001",
        "spend_rows": _base_rows(),
        "post_period_start": "2025-03-01",
        "post_period_end": "2025-03-31",
        "experiment_type": PostTestExperimentType.HOLDOUT,
        "assignment_rows": _assignment_rows(),
        "experiment_geo_scope": ("g1", "g2", "g3"),
        "source_dataset_ref": "spend://test",
        "source_lineage": {"profiler": "GEO_KPI_SPEND_DATA_PROFILER_001"},
    }
    defaults.update(overrides)
    return PostTestSpendInput(**defaults)


def test_go_dark_computes_bau_minus_actual() -> None:
    evidence = build_post_test_spend_evidence(
        _input(
            experiment_type=PostTestExperimentType.GO_DARK,
            counterfactual_or_bau_spend=300.0,
        )
    )
    assert evidence.actual_treatment_spend == 150.0
    assert evidence.spend_delta == 150.0
    assert evidence.readiness_status == PostTestSpendReadinessStatus.READY


def test_heavy_up_computes_actual_minus_bau() -> None:
    evidence = build_post_test_spend_evidence(
        _input(
            experiment_type=PostTestExperimentType.HEAVY_UP,
            counterfactual_or_bau_spend=100.0,
        )
    )
    assert evidence.spend_delta == 50.0
    assert evidence.readiness_status == PostTestSpendReadinessStatus.READY


def test_holdout_computes_treatment_minus_control() -> None:
    evidence = build_post_test_spend_evidence(_input(experiment_type=PostTestExperimentType.HOLDOUT))
    assert evidence.actual_treatment_spend == 150.0
    assert evidence.actual_control_or_baseline_spend == 80.0
    assert evidence.spend_delta == 70.0
    assert evidence.readiness_status == PostTestSpendReadinessStatus.READY


def test_dosage_computes_cell_minus_baseline_cell() -> None:
    rows = [
        {
            "geo_unit_id": "g1",
            "date": "2025-03-01",
            "spend_value": 120.0,
            "cell_id": "high",
            "cell_role": "treatment",
        },
        {
            "geo_unit_id": "g2",
            "date": "2025-03-01",
            "spend_value": 40.0,
            "cell_id": "low",
            "cell_role": "control",
        },
    ]
    evidence = build_post_test_spend_evidence(
        _input(
            spend_rows=rows,
            experiment_type=PostTestExperimentType.DOSAGE,
            treatment_cell_values=("high",),
            control_cell_values=("low",),
            assignment_rows=[],
            experiment_geo_scope=None,
        )
    )
    assert evidence.spend_delta == 80.0
    assert evidence.readiness_status == PostTestSpendReadinessStatus.READY


def test_reallocation_requires_added_and_removed_scope() -> None:
    rows = [
        {
            "geo_unit_id": "g1",
            "date": "2025-03-01",
            "spend_value": 60.0,
            "channel": "search",
            "cell_id": "T1",
            "cell_role": "treatment",
        },
        {
            "geo_unit_id": "g1",
            "date": "2025-03-01",
            "spend_value": 20.0,
            "channel": "social",
            "cell_id": "T1",
            "cell_role": "treatment",
        },
    ]
    blocked = build_post_test_spend_evidence(
        _input(
            spend_rows=rows,
            experiment_type=PostTestExperimentType.REALLOCATION,
            assignment_rows=[],
            experiment_geo_scope=None,
        )
    )
    assert blocked.readiness_status in {
        PostTestSpendReadinessStatus.BLOCKED_MISSING_SPEND_BASELINE,
        PostTestSpendReadinessStatus.PARTIAL_DIAGNOSTIC_ONLY,
    }

    ready = build_post_test_spend_evidence(
        _input(
            spend_rows=rows,
            experiment_type=PostTestExperimentType.REALLOCATION,
            added_spend_scope="search",
            removed_spend_scope="social",
            assignment_rows=[],
            experiment_geo_scope=None,
        )
    )
    assert ready.spend_delta == 40.0
    assert ready.readiness_status == PostTestSpendReadinessStatus.READY


def test_filters_post_period_and_excludes_pre_period() -> None:
    evidence = build_post_test_spend_evidence(_input())
    assert evidence.actual_treatment_spend == 150.0
    assert "2025-02-01" not in evidence.spend_window_start


def test_filters_experiment_geo_scope() -> None:
    evidence = build_post_test_spend_evidence(
        _input(experiment_geo_scope=("g1",), experiment_type=PostTestExperimentType.HOLDOUT)
    )
    assert evidence.actual_treatment_spend == 150.0
    assert evidence.actual_control_or_baseline_spend is None


def test_joins_assignment_correctly() -> None:
    rows = [
        {"geo_unit_id": "g1", "date": "2025-03-01", "spend_value": 10.0},
        {"geo_unit_id": "g2", "date": "2025-03-01", "spend_value": 20.0},
    ]
    evidence = build_post_test_spend_evidence(
        _input(
            spend_rows=rows,
            spend_cell_column=None,
            spend_cell_role_column=None,
            experiment_type=PostTestExperimentType.HOLDOUT,
            experiment_geo_scope=None,
        )
    )
    assert evidence.actual_treatment_spend == 10.0
    assert evidence.actual_control_or_baseline_spend == 20.0


def test_aggregates_multiple_rows() -> None:
    evidence = build_post_test_spend_evidence(_input())
    assert evidence.actual_treatment_spend == 150.0


def test_preserves_source_lineage() -> None:
    evidence = build_post_test_spend_evidence(_input())
    assert evidence.source_dataset_ref == "spend://test"
    assert evidence.source_lineage["profiler"] == "GEO_KPI_SPEND_DATA_PROFILER_001"


def test_currency_warning_when_column_missing() -> None:
    rows = [{"geo_unit_id": "g1", "date": "2025-03-01", "spend_value": 10.0, "cell_role": "treatment"}]
    evidence = build_post_test_spend_evidence(
        _input(
            spend_rows=rows,
            currency_column=None,
            assignment_rows=[],
            experiment_geo_scope=None,
            experiment_type=PostTestExperimentType.GO_DARK,
            counterfactual_or_bau_spend=20.0,
        )
    )
    assert "CURRENCY_COLUMN_NOT_DECLARED" in evidence.warnings


def test_blocked_missing_spend_df() -> None:
    evidence = build_post_test_spend_evidence(_input(spend_rows=[]))
    assert evidence.readiness_status == PostTestSpendReadinessStatus.BLOCKED_MISSING_SPEND_SOURCE


def test_blocked_missing_required_columns() -> None:
    evidence = build_post_test_spend_evidence(
        _input(spend_rows=[{"geo_unit_id": "g1"}], spend_date_column="date")
    )
    assert any("BLOCKED_MISSING_COLUMN" in b for b in evidence.blocking_reasons)


def test_blocked_no_post_test_rows() -> None:
    evidence = build_post_test_spend_evidence(
        _input(
            spend_rows=[
                {
                    "geo_unit_id": "g1",
                    "date": "2024-01-01",
                    "spend_value": 10.0,
                    "cell_role": "treatment",
                }
            ],
            post_period_start="2025-03-01",
            post_period_end="2025-03-31",
            assignment_rows=[],
            experiment_geo_scope=None,
        )
    )
    assert evidence.readiness_status == PostTestSpendReadinessStatus.BLOCKED_MISSING_POST_TEST_SPEND


def test_blocked_no_matching_geos() -> None:
    evidence = build_post_test_spend_evidence(_input(experiment_geo_scope=("missing",)))
    assert evidence.readiness_status == PostTestSpendReadinessStatus.BLOCKED_SPEND_GEO_SCOPE_MISMATCH


def test_blocked_missing_assignment() -> None:
    rows = [{"geo_unit_id": "g9", "date": "2025-03-01", "spend_value": 10.0}]
    evidence = build_post_test_spend_evidence(
        _input(
            spend_rows=rows,
            spend_cell_column=None,
            spend_cell_role_column=None,
            assignment_rows=_assignment_rows(),
            experiment_geo_scope=None,
            experiment_type=PostTestExperimentType.HOLDOUT,
        )
    )
    assert evidence.readiness_status == PostTestSpendReadinessStatus.BLOCKED_SPEND_CELL_SCOPE_MISMATCH


def test_blocked_missing_bau_for_go_dark() -> None:
    evidence = build_post_test_spend_evidence(
        _input(experiment_type=PostTestExperimentType.GO_DARK, counterfactual_or_bau_spend=None)
    )
    assert PostTestSpendReadinessStatus.BLOCKED_MISSING_SPEND_BASELINE in {
        evidence.readiness_status,
        PostTestSpendReadinessStatus(evidence.blocking_reasons[0])
        if evidence.blocking_reasons
        else evidence.readiness_status,
    }


def test_blocked_unsupported_experiment_type() -> None:
    evidence = build_post_test_spend_evidence(_input(experiment_type="unknown_type"))
    assert evidence.readiness_status == PostTestSpendReadinessStatus.BLOCKED_UNSUPPORTED_EXPERIMENT_TYPE


def test_blocked_missing_baseline_cell_for_dosage() -> None:
    rows = [
        {
            "geo_unit_id": "g1",
            "date": "2025-03-01",
            "spend_value": 120.0,
            "cell_id": "high",
            "cell_role": "treatment",
        }
    ]
    evidence = build_post_test_spend_evidence(
        _input(
            spend_rows=rows,
            experiment_type=PostTestExperimentType.DOSAGE,
            treatment_cell_values=("high",),
            control_cell_values=("low",),
            assignment_rows=[],
            experiment_geo_scope=None,
        )
    )
    assert PostTestSpendReadinessStatus.BLOCKED_MISSING_SPEND_BASELINE in {
        evidence.readiness_status,
        PostTestSpendReadinessStatus(evidence.blocking_reasons[0])
        if evidence.blocking_reasons
        else evidence.readiness_status,
    }


def test_does_not_use_planning_required_spend_delta() -> None:
    evidence = build_post_test_spend_evidence(
        _input(
            experiment_type=PostTestExperimentType.HOLDOUT,
            planning_required_spend_delta=9999.0,
        )
    )
    assert evidence.spend_delta == 70.0
    assert "PLANNING_REQUIRED_SPEND_DELTA_NOT_USED_AS_OBSERVED_SPEND_DELTA" in evidence.warnings


def test_does_not_compute_roi_or_roas() -> None:
    evidence = build_post_test_spend_evidence(_input())
    handoff = build_trusted_readout_spend_handoff(evidence)
    assert handoff["efficiency_metric_readiness"]["roas"] == "NOT_COMPUTED"
    assert handoff["efficiency_metric_readiness"]["profit_roi"] == "NOT_COMPUTED"
    assert handoff["roi_claim_authorization_status"] == "NOT_EVALUATED"


def test_trusted_readout_handoff_shape() -> None:
    evidence = build_post_test_spend_evidence(_input())
    handoff = build_trusted_readout_spend_handoff(evidence)
    assert "spend_readiness_summary" in handoff
    assert "post_test_spend_evidence" in handoff
    assert "blocked_efficiency_metrics" in handoff
    assert "spend_lineage" in handoff
    assert "spend_warnings" in handoff
