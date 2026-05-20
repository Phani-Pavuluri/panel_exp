"""Tests for validation report serialization."""

import json

from panel_exp.validation.metrics import ValidationMetrics
from panel_exp.validation.report import EstimatorValidationReport
from panel_exp.validation.runner import default_estimator_configs
from panel_exp.validation.scenarios import get_scenario


def test_json_serializes():
    metrics = [
        ValidationMetrics(
            estimator_name="SCM",
            scenario_name="aa_null",
            n_replications=2,
            bias=0.0,
            rmse=0.01,
            coverage=None,
            false_positive_rate=None,
            false_negative_rate=None,
            power=None,
            mean_interval_width=None,
            failure_rate=0.0,
        )
    ]
    report = EstimatorValidationReport.build(
        scenarios=[get_scenario("aa_null")],
        estimator_configs=default_estimator_configs()[:1],
        metrics=metrics,
        failures=[],
        created_at="2026-01-01T00:00:00+00:00",
    )
    payload = json.loads(report.to_json())
    assert payload["report_version"] == "1.0"
    assert payload["metrics"][0]["estimator_name"] == "SCM"
    assert "validated under" in payload["recovery_statement"]


def test_canonical_json_excludes_created_at():
    report = EstimatorValidationReport.build(
        scenarios=[get_scenario("aa_null")],
        estimator_configs=default_estimator_configs()[:1],
        metrics=[],
        created_at="2026-01-01T00:00:00+00:00",
    )
    report_b = EstimatorValidationReport.build(
        scenarios=[get_scenario("aa_null")],
        estimator_configs=default_estimator_configs()[:1],
        metrics=[],
        created_at="2026-06-01T12:00:00+00:00",
    )
    assert report.canonical_json() == report_b.canonical_json()


def test_failures_captured_in_report():
    report = EstimatorValidationReport.build(
        scenarios=[get_scenario("aa_null")],
        estimator_configs=default_estimator_configs()[:1],
        metrics=[],
        failures=[
            {
                "estimator_name": "SCM",
                "scenario_name": "aa_null",
                "replication": "0",
                "error": "boom",
            }
        ],
    )
    assert len(report.failures) == 1
    assert report.failures[0]["error"] == "boom"
