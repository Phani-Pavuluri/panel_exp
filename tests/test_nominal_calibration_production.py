"""Production-scale nominal calibration runner (small n in CI)."""

from __future__ import annotations

import pytest

from panel_exp.validation.calibration_report import MIN_REPLICATIONS_FOR_STABLE_CALIBRATION
from panel_exp.validation.nominal_calibration import NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS
from panel_exp.validation.did_interval_policy import (
    DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED,
)
from panel_exp.validation.production_nominal_calibration import (
    BELOW_PRODUCTION_REPLICATION_WARNING,
    evaluate_coverage_aggregate_status,
    evaluate_fpr_aggregate_status,
    evaluate_power_aggregate_status,
    evaluate_stability_aggregate_status,
    run_production_nominal_calibration,
)
from panel_exp.validation.recovery_intervals import INTERVAL_ESTIMAND_RELATIVE_ATT_POST


def test_distribution_stats_aggregation_unit():
    from panel_exp.validation.production_nominal_calibration import _distribution_stats

    stats = _distribution_stats([0.9, 0.95, 1.0])
    assert stats["mean"] == pytest.approx(0.95)
    assert stats["min"] == pytest.approx(0.9)
    assert stats["max"] == pytest.approx(1.0)
    assert stats["std"] == pytest.approx(0.05, rel=0.01)


@pytest.mark.parametrize(
    "mean,available,expected",
    [
        (0.92, True, "pass"),
        (0.85, True, "warn"),
        (0.75, True, "fail"),
        (float("nan"), False, "unavailable"),
    ],
)
def test_coverage_status_rules(mean: float, available: bool, expected: str):
    assert evaluate_coverage_aggregate_status(mean, per_seed_available=available) == expected


@pytest.mark.parametrize(
    "mean,available,expected",
    [
        (0.08, True, "pass"),
        (0.12, True, "warn"),
        (0.20, True, "fail"),
        (float("nan"), False, "unavailable"),
    ],
)
def test_fpr_status_rules(mean: float, available: bool, expected: str):
    assert evaluate_fpr_aggregate_status(mean, per_seed_available=available) == expected


@pytest.mark.parametrize(
    "mean,available,expected",
    [
        (0.85, True, "pass"),
        (0.70, True, "warn"),
        (0.50, True, "fail"),
        (float("nan"), False, "unavailable"),
    ],
)
def test_power_status_rules(mean: float, available: bool, expected: str):
    assert evaluate_power_aggregate_status(mean, per_seed_available=available) == expected


def test_stability_status_warn_on_high_std():
    assert (
        evaluate_stability_aggregate_status(
            coverage_std=0.06,
            fpr_std=0.01,
            power_std=0.01,
            mean_failure_rate=0.01,
        )
        == "warn"
    )
    assert (
        evaluate_stability_aggregate_status(
            coverage_std=0.01,
            fpr_std=0.01,
            power_std=0.01,
            mean_failure_rate=0.10,
        )
        == "warn"
    )
    assert (
        evaluate_stability_aggregate_status(
            coverage_std=0.01,
            fpr_std=0.01,
            power_std=0.01,
            mean_failure_rate=0.01,
        )
        == "pass"
    )


def test_below_production_warning_when_small_n():
    out = run_production_nominal_calibration(
        estimator_configs=("SCM_UnitJackKnife",),
        scenarios=("recovery_null_effect",),
        n_simulations=5,
        random_seeds=(0,),
    )
    assert out["n_simulations"] < MIN_REPLICATIONS_FOR_STABLE_CALIBRATION
    assert BELOW_PRODUCTION_REPLICATION_WARNING in out["global_warnings"]


@pytest.mark.slow
def test_eligible_config_produces_eligible_aggregate():
    out = run_production_nominal_calibration(
        estimator_configs=("SCM_UnitJackKnife",),
        scenarios=("recovery_null_effect",),
        n_simulations=3,
        random_seeds=(0, 1),
    )
    agg = out["aggregates"][0]
    assert agg["eligible_for_nominal_calibration"] is True
    assert agg["interval_estimand"] == INTERVAL_ESTIMAND_RELATIVE_ATT_POST
    assert agg["interval_aligned"] is True
    assert "coverage" in agg
    assert set(agg["coverage"]) >= {"mean", "std", "min", "max"}
    assert len(agg["per_seed_runs"]) == 2
    for run in agg["per_seed_runs"]:
        assert run["eligible_for_nominal_calibration"] is True
        assert "failure_rate" in run
        assert "failure_types" in run


@pytest.mark.slow
def test_did_bootstrap_ineligible_interval_mismatch():
    out = run_production_nominal_calibration(
        estimator_configs=("DID_Bootstrap",),
        scenarios=("recovery_null_effect",),
        n_simulations=3,
        random_seeds=(0,),
    )
    assert out["per_seed_runs"] == []
    assert len(out["skipped"]) >= 1
    did = out["skipped"][0]
    assert did["eligible_for_nominal_calibration"] is False
    assert did["ineligible_reason"] == DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED
    agg = out["aggregates"][0]
    assert agg["eligible_for_nominal_calibration"] is False


@pytest.mark.slow
def test_point_estimate_config_skipped_without_run():
    out = run_production_nominal_calibration(
        estimator_configs=("SCM",),
        scenarios=("recovery_null_effect",),
        n_simulations=3,
        random_seeds=(0,),
    )
    assert out["per_seed_runs"] == []
    skip = out["skipped"][0]
    assert skip["ineligible_reason"] == "intervals_not_expected"
    assert skip.get("skipped") is True


@pytest.mark.slow
def test_deterministic_for_fixed_seeds():
    kwargs = dict(
        estimator_configs=("TBRRidge_Kfold",),
        scenarios=("recovery_null_effect",),
        n_simulations=3,
        random_seeds=(0, 1),
    )
    a = run_production_nominal_calibration(**kwargs)
    b = run_production_nominal_calibration(**kwargs)
    assert a["per_seed_runs"] == b["per_seed_runs"]


@pytest.mark.slow
@pytest.mark.parametrize(
    "config",
    ["SCM_UnitJackKnife", "TBRRidge_BlockResidualBootstrap"],
)
def test_eligible_configs_smoke_on_recovery_null(config: str):
    out = run_production_nominal_calibration(
        estimator_configs=(config,),
        scenarios=("recovery_null_effect",),
        n_simulations=3,
        random_seeds=(0,),
    )
    assert len(out["aggregates"]) == 1
    assert out["aggregates"][0]["eligible_for_nominal_calibration"] is True


def test_tbrridge_kfold_in_eligible_registry():
    assert "TBRRidge_Kfold" in NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS


def test_default_n_is_production_oriented():
    from panel_exp.validation.production_nominal_calibration import (
        PRODUCTION_N_SIMULATIONS_DEFAULT,
        PRODUCTION_RANDOM_SEEDS_DEFAULT,
    )

    assert PRODUCTION_N_SIMULATIONS_DEFAULT >= MIN_REPLICATIONS_FOR_STABLE_CALIBRATION
    assert len(PRODUCTION_RANDOM_SEEDS_DEFAULT) == 3
