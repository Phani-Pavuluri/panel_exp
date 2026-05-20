"""Tests for validation metric aggregation."""

import json

import numpy as np
import pytest

from panel_exp.validation.metrics import (
    ReplicationRecord,
    ValidationResult,
    aggregate_replications,
)
from panel_exp.validation.report import EstimatorValidationReport


def test_bias_and_rmse():
    records = [
        ReplicationRecord(estimate=0.11, truth=0.10),
        ReplicationRecord(estimate=0.09, truth=0.10),
    ]
    result = aggregate_replications(
        estimator_name="SCM",
        scenario_name="constant_positive_10pct",
        records=records,
    )
    assert abs(result.bias - 0.0) < 1e-12
    assert result.rmse < 0.02


def test_coverage_computation():
    records = [
        ReplicationRecord(
            estimate=0.10, truth=0.10, ci_lower=0.05, ci_upper=0.15
        ),
        ReplicationRecord(
            estimate=0.10, truth=0.10, ci_lower=0.11, ci_upper=0.20
        ),
    ]
    result = aggregate_replications(
        estimator_name="DID",
        scenario_name="aa_zero_effect",
        records=records,
    )
    assert result.coverage == 0.5
    assert result.interval_width == pytest.approx(0.095, rel=0.01)


def test_false_positive_rate_aa():
    records = [
        ReplicationRecord(estimate=0.0, truth=0.0, significant=True),
        ReplicationRecord(estimate=0.0, truth=0.0, significant=False),
    ]
    result = aggregate_replications(
        estimator_name="DID",
        scenario_name="aa_zero_effect",
        records=records,
    )
    assert result.false_positive_rate == 0.5


def test_report_serializes():
    result = ValidationResult(
        estimator_name="SCM",
        scenario_name="aa_zero_effect",
        bias=0.0,
        rmse=0.0,
        coverage=0.9,
        false_positive_rate=0.05,
        false_negative_rate=0.1,
        power=0.9,
        interval_width=0.2,
        n_replications=10,
        truth=0.0,
    )
    report = EstimatorValidationReport.build(
        scenario_names=["aa_zero_effect"],
        results=[result],
    )
    payload = report.to_dict()
    round_trip = json.loads(json.dumps(payload))
    assert round_trip["evidence_version"]
    assert round_trip["results"][0]["estimator_name"] == "SCM"
    assert "recovery_statement" in round_trip
