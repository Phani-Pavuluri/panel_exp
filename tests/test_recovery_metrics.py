"""Unit tests for recovery metric aggregation."""

from __future__ import annotations

import numpy as np
import pytest

from panel_exp.validation.recovery_metrics import (
    SimulationRecord,
    aggregate_recovery_metrics,
)


def test_same_records_identical_metrics():
    records = [
        SimulationRecord(
            predicted_effect=0.11,
            true_effect=0.10,
            ci_lower=0.05,
            ci_upper=0.15,
            significant=True,
        ),
        SimulationRecord(
            predicted_effect=0.09,
            true_effect=0.10,
            ci_lower=0.04,
            ci_upper=0.14,
            significant=False,
        ),
    ]
    r1 = aggregate_recovery_metrics(
        estimator="SCM", scenario="test", records=records, recovery_tolerance=0.15
    )
    r2 = aggregate_recovery_metrics(
        estimator="SCM", scenario="test", records=records, recovery_tolerance=0.15
    )
    assert r1.bias == r2.bias
    assert r1.absolute_bias == r2.absolute_bias
    assert r1.coverage == r2.coverage
    assert r1.recovery_success_rate == r2.recovery_success_rate


def test_null_scenario_fpr_bounded():
    records = [
        SimulationRecord(
            predicted_effect=0.01 * i,
            true_effect=0.0,
            significant=(i % 2 == 0),
        )
        for i in range(20)
    ]
    r = aggregate_recovery_metrics(estimator="DID", scenario="null", records=records)
    assert 0.0 <= r.false_positive_rate <= 1.0


def test_bounded_rates_from_aggregation():
    records = [
        SimulationRecord(
            predicted_effect=0.10,
            true_effect=0.10,
            ci_lower=0.0,
            ci_upper=0.20,
            significant=True,
        ),
        SimulationRecord(
            predicted_effect=0.12,
            true_effect=0.0,
            significant=False,
        ),
    ]
    r = aggregate_recovery_metrics(estimator="SCM", scenario="x", records=records)
    for attr in ("coverage", "power", "recovery_success_rate", "false_positive_rate"):
        val = getattr(r, attr)
        if val == val:
            assert 0.0 <= val <= 1.0


def test_absolute_bias_nonnegative():
    records = [
        SimulationRecord(predicted_effect=0.20, true_effect=0.10),
        SimulationRecord(predicted_effect=0.00, true_effect=0.10),
    ]
    r = aggregate_recovery_metrics(estimator="TBR", scenario="x", records=records)
    assert r.absolute_bias >= 0.0
    assert r.bias == pytest.approx(np.mean([0.10, -0.10]))
