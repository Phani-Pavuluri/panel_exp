"""Tests for RecoveryRunner reproducibility and metric bounds."""

from __future__ import annotations

import pytest

from panel_exp.validation.recovery_runner import (
    RecoveryRunner,
    merge_validation_metadata,
    run_recovery_battery,
)
from panel_exp.validation.synthetic_scenarios import get_recovery_scenario


@pytest.mark.parametrize("estimator", ["SCM", "DID", "TBR"])
def test_same_seed_identical_metrics(estimator):
    scenario = get_recovery_scenario("recovery_positive_effect")
    r1 = RecoveryRunner(
        estimator, scenario, n_simulations=2, random_state=42
    ).run()
    r2 = RecoveryRunner(
        estimator, scenario, n_simulations=2, random_state=42
    ).run()
    assert r1["bias"] == r2["bias"]
    assert r1["absolute_bias"] == r2["absolute_bias"]
    assert r1["recovery_success_rate"] == r2["recovery_success_rate"]


def test_null_scenario_fpr_in_unit_interval():
    payload = RecoveryRunner(
        "DID",
        "recovery_null_effect",
        n_simulations=6,
        random_state=7,
    ).run()
    fpr = payload["false_positive_rate"]
    if fpr == fpr:
        assert 0.0 <= fpr <= 1.0


def test_metric_bounds():
    payload = RecoveryRunner(
        "SCM",
        "scm_low_signal",
        n_simulations=3,
        random_state=0,
    ).run()
    for key in ("coverage", "power", "recovery_success_rate", "false_positive_rate"):
        val = payload[key]
        if val == val:
            assert 0.0 <= val <= 1.0
    assert payload["runtime_seconds"] >= 0.0
    assert payload["n_simulations"] == 3
    assert payload["estimator"] == "SCM"
    assert payload["scenario"] == "scm_low_signal"


def test_output_schema_keys():
    payload = RecoveryRunner(
        "TBR",
        "recovery_positive_effect",
        n_simulations=1,
        random_state=1,
    ).run()
    for key in (
        "estimator",
        "scenario",
        "bias",
        "absolute_bias",
        "coverage",
        "false_positive_rate",
        "power",
        "runtime_seconds",
        "recovery_success_rate",
        "failure_rate",
        "failure_types",
        "scored_target_estimand",
        "point_estimand",
        "interval_estimand",
        "interval_scale",
        "recovery_config",
    ):
        assert key in payload


def test_merge_validation_metadata_additive():
    results = {"times": [], "y": [], "y_hat": [], "inference_metadata": {"alpha": 0.05}}
    payloads = [
        RecoveryRunner("SCM", "recovery_null_effect", n_simulations=1, random_state=0).run(),
        RecoveryRunner("SCM", "recovery_positive_effect", n_simulations=1, random_state=1).run(),
    ]
    merge_validation_metadata(results, payloads)
    vm = results["validation_metadata"]
    assert "validation_scenarios_run" in vm
    assert len(vm["validation_scenarios_run"]) == 2
    assert "validation_bias" in vm
    assert "validation_coverage" in vm
    assert "validation_fpr" in vm
    assert "validation_power" in vm
    assert results["inference_metadata"]["alpha"] == 0.05


def test_recovery_battery_lists_scenarios():
    batch = run_recovery_battery("DID", n_simulations=1, random_state=3)
    assert len(batch) == 2
    names = {b["scenario"] for b in batch}
    assert "did_parallel_trends_holds" in names


@pytest.mark.slow
def test_trop_recovery_smoke():
    payload = RecoveryRunner(
        "TROP",
        "trop_sparse_donors",
        n_simulations=1,
        random_state=11,
    ).run()
    assert payload["estimator"] == "TROP"
    assert payload["n_simulations"] == 1
