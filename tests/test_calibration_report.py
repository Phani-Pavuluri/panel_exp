"""Tests for A/A calibration reporting and readiness diagnostics."""

from __future__ import annotations

import math

import pytest

from panel_exp.evidence import DesignEvidence
from panel_exp.artifacts.experiment_card import build_experiment_card
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import spec_from_geo_design
from panel_exp.validation.calibration_report import (
    MAX_FALSE_POSITIVE_RATE,
    MIN_COVERAGE_UNDER_NULL,
    MIN_POWER_TARGET,
    MIN_REPLICATIONS_FOR_STABLE_CALIBRATION,
    MIN_RECOVERY_SUCCESS_RATE,
    attach_calibration_report,
    build_calibration_report,
)
from panel_exp.validation.recovery_runner import RecoveryRunner
from panel_exp.validation.recovery_metrics import aggregate_recovery_metrics, SimulationRecord


def _aa_calibration_explicit() -> dict:
    return {
        "n_replications": 50,
        "null_replications": 25,
        "positive_replications": 25,
        "false_positive_rate": 0.04,
        "false_negative_rate": 0.1,
        "coverage_under_null": 0.95,
        "coverage_under_lift": 0.92,
        "power": 0.85,
        "mean_interval_width": 0.12,
        "median_interval_width": 0.11,
        "bias_under_null": 0.001,
        "bias_under_lift": 0.02,
        "recovery_success_rate": 0.93,
    }


def test_same_inputs_deterministic_report():
    recovery = [
        {
            "estimator": "DID",
            "scenario": "recovery_null_effect",
            "bias": 0.0,
            "coverage": 0.94,
            "false_positive_rate": 0.05,
            "power": float("nan"),
            "recovery_success_rate": 0.95,
            "n_simulations": 10,
        },
        {
            "estimator": "DID",
            "scenario": "recovery_positive_effect",
            "bias": 0.02,
            "coverage": 0.91,
            "false_positive_rate": float("nan"),
            "power": 0.88,
            "recovery_success_rate": 0.92,
            "n_simulations": 10,
        },
    ]
    r1 = build_calibration_report(recovery_outputs=recovery).to_dict()
    r2 = build_calibration_report(recovery_outputs=recovery).to_dict()
    assert r1["warnings"] == r2["warnings"]
    for key in r1:
        if key == "warnings":
            continue
        v1, v2 = r1[key], r2[key]
        if isinstance(v1, float) and isinstance(v2, float):
            if math.isnan(v1) and math.isnan(v2):
                continue
            assert v1 == v2
        else:
            assert v1 == v2


def test_metric_bounds():
    report = build_calibration_report(aa_calibration=_aa_calibration_explicit())
    for attr in (
        "false_positive_rate",
        "coverage_under_null",
        "coverage_under_lift",
        "power",
        "recovery_success_rate",
    ):
        val = getattr(report, attr)
        assert 0.0 <= val <= 1.0


@pytest.mark.parametrize(
    "field,value,expected_substring",
    [
        ("n_replications", 20, "small simulation count"),
        ("false_positive_rate", MAX_FALSE_POSITIVE_RATE + 0.05, "False positive rate"),
        ("coverage_under_null", MIN_COVERAGE_UNDER_NULL - 0.05, "Coverage below"),
        ("power", MIN_POWER_TARGET - 0.05, "Power below"),
        ("recovery_success_rate", MIN_RECOVERY_SUCCESS_RATE - 0.05, "Recovery instability"),
    ],
)
def test_warning_generation(field, value, expected_substring):
    base = _aa_calibration_explicit()
    base[field] = value
    base["n_replications"] = (
        20 if field == "n_replications" else MIN_REPLICATIONS_FOR_STABLE_CALIBRATION
    )
    report = build_calibration_report(aa_calibration=base)
    assert any(expected_substring in w for w in report.warnings)


def test_missing_optional_fields_do_not_crash():
    report = build_calibration_report()
    assert report.n_replications == 0
    md = report.to_markdown()
    assert "## Calibration Summary" in md
    assert "unknown" in md


def test_markdown_renders():
    report = build_calibration_report(aa_calibration=_aa_calibration_explicit())
    md = report.to_markdown()
    assert "## Calibration Summary" in md
    assert "False positive rate" in md
    assert "Coverage under null" in md


def test_attach_calibration_report_additive():
    results = {"y_hat": [1.0], "validation_metadata": {"validation_bias": {}}}
    report = build_calibration_report(aa_calibration=_aa_calibration_explicit())
    attach_calibration_report(results, report)
    assert "calibration_report" in results
    assert results["y_hat"] == [1.0]
    assert "validation_bias" in results["validation_metadata"]


def test_build_from_recovery_runner_outputs():
    null_run = RecoveryRunner(
        "DID", "recovery_null_effect", n_simulations=4, random_state=1
    ).run()
    pos_run = RecoveryRunner(
        "DID", "recovery_positive_effect", n_simulations=4, random_state=2
    ).run()
    report = build_calibration_report(recovery_outputs=[null_run, pos_run])
    assert report.n_replications == 8
    assert report.null_replications == 4
    assert report.positive_replications == 4


def test_same_seed_recovery_metrics_deterministic():
    records = [
        SimulationRecord(predicted_effect=0.01, true_effect=0.0, significant=False),
        SimulationRecord(predicted_effect=0.02, true_effect=0.0, significant=True),
    ]
    r1 = aggregate_recovery_metrics(
        estimator="SCM", scenario="recovery_null_effect", records=records
    )
    r2 = aggregate_recovery_metrics(
        estimator="SCM", scenario="recovery_null_effect", records=records
    )
    assert r1.false_positive_rate == pytest.approx(r2.false_positive_rate, nan_ok=True)
    assert r1.coverage == pytest.approx(r2.coverage, nan_ok=True)


def test_evidence_not_mutated_via_attach_on_results_copy():
    spec = spec_from_geo_design(
        "e1",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
    )
    ev = DesignEvidence.from_assignment(
        spec, {"control": ["a"], "test_0": ["b"]}, created_at="2026-01-01T00:00:00+00:00"
    )
    before = ev.to_json()
    results = {"times": []}
    attach_calibration_report(
        results, build_calibration_report(aa_calibration=_aa_calibration_explicit())
    )
    assert ev.to_json() == before


def test_experiment_card_includes_calibration_when_present():
    spec = spec_from_geo_design(
        "e1",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
    )
    artifacts = {}
    attach_calibration_report(
        artifacts,
        build_calibration_report(
            aa_calibration={
                **_aa_calibration_explicit(),
                "n_replications": MIN_REPLICATIONS_FOR_STABLE_CALIBRATION,
            }
        ),
    )
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["a"], "test_0": ["b"]},
        artifacts=artifacts,
        created_at="2026-01-01T00:00:00+00:00",
    )
    md = build_experiment_card(ev).to_markdown()
    assert "## Calibration Summary" in md


def test_experiment_card_without_calibration_unchanged():
    spec = spec_from_geo_design(
        "e1",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
    )
    ev = DesignEvidence.from_assignment(
        spec, {"control": ["a"], "test_0": ["b"]}, created_at="2026-01-01T00:00:00+00:00"
    )
    md = build_experiment_card(ev).to_markdown()
    assert "## Calibration Summary" not in md


def test_validation_outputs_merge():
    from panel_exp.validation.metrics import ValidationMetrics

    null_v = ValidationMetrics(
        estimator_name="SCM",
        scenario_name="aa_null",
        n_replications=30,
        bias=0.0,
        rmse=0.01,
        coverage=0.93,
        false_positive_rate=0.06,
        false_negative_rate=None,
        power=None,
        mean_interval_width=0.2,
        failure_rate=0.0,
    )
    report = build_calibration_report(validation_outputs=[null_v])
    assert report.null_replications == 30
    assert report.coverage_under_null == pytest.approx(0.93)
    assert report.mean_interval_width == pytest.approx(0.2)
