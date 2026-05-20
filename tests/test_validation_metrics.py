"""Tests for validation metric aggregation."""

import math

import pytest

from panel_exp.validation.metrics import ReplicationOutcome, aggregate_outcomes


def test_bias_and_rmse():
    outcomes = [
        ReplicationOutcome(estimate=0.11, truth=0.10),
        ReplicationOutcome(estimate=0.09, truth=0.10),
    ]
    m = aggregate_outcomes(
        estimator_name="SCM",
        scenario_name="positive_relative_lift",
        outcomes=outcomes,
    )
    assert abs(m.bias) < 1e-12
    assert m.rmse < 0.02


def test_coverage_computation():
    outcomes = [
        ReplicationOutcome(
            estimate=0.10,
            truth=0.10,
            ci_lower=0.05,
            ci_upper=0.15,
            significant=False,
        ),
        ReplicationOutcome(
            estimate=0.10,
            truth=0.10,
            ci_lower=0.11,
            ci_upper=0.20,
            significant=True,
        ),
    ]
    m = aggregate_outcomes(
        estimator_name="DID",
        scenario_name="aa_null",
        outcomes=outcomes,
    )
    assert m.coverage == 0.5
    assert m.mean_interval_width == pytest.approx(0.095, rel=0.01)


def test_fpr_power_only_with_intervals():
    with_intervals = [
        ReplicationOutcome(
            estimate=0.0,
            truth=0.0,
            ci_lower=-0.1,
            ci_upper=0.1,
            significant=True,
        ),
        ReplicationOutcome(
            estimate=0.0,
            truth=0.0,
            ci_lower=-0.1,
            ci_upper=0.1,
            significant=False,
        ),
    ]
    m = aggregate_outcomes(
        estimator_name="DID",
        scenario_name="aa_null",
        outcomes=with_intervals,
    )
    assert m.false_positive_rate == 0.5

    without_intervals = [
        ReplicationOutcome(estimate=0.0, truth=0.0, significant=True),
        ReplicationOutcome(estimate=0.0, truth=0.0, significant=False),
    ]
    m2 = aggregate_outcomes(
        estimator_name="SCM",
        scenario_name="aa_null",
        outcomes=without_intervals,
    )
    assert m2.false_positive_rate is None
    assert m2.power is None
    assert m2.coverage is None


def test_failure_rate():
    outcomes = [
        ReplicationOutcome(estimate=0.1, truth=0.1, failed=False),
        ReplicationOutcome(estimate=float("nan"), truth=0.1, failed=True),
    ]
    m = aggregate_outcomes(
        estimator_name="SCM",
        scenario_name="aa_null",
        outcomes=outcomes,
    )
    assert m.failure_rate == 0.5
    assert not math.isnan(m.bias)
