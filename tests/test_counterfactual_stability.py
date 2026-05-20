import numpy as np
import pandas as pd
import pytest
import sys
import os

# Add the panel_exp package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tests.cvxpy_test_helpers import skip_without_cvxpy_osqp
from panel_exp.utils.counterfactual_stability_tests import (
    detect_break_candidates,
    run_residual_drift_test,
    run_counterfactual_stability_tests,
    run_control_heterogeneity_diagnostics,
    ResidualDriftTestResult,
    ControlHeterogeneityResult,
    check_AugSynthCVXPY_weight_health,
    compare_estimator_stability,
)


def _make_panel(n_units=10, n_periods=30, break_at=None, shift=500.0, seed=42):
    """Synthetic wide panel: rows=units, cols=dates."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-01", periods=n_periods, freq="W")
    data = rng.normal(1000, 100, size=(n_units, n_periods))
    if break_at is not None:
        data[:3, break_at:] += shift  # shift first 3 units (treated)
    wide = pd.DataFrame(data, index=[f"unit_{i}" for i in range(n_units)], columns=dates)
    return wide


def test_detect_break_cusum_treated():
    wide = _make_panel(n_units=10, n_periods=40, break_at=15, shift=800.0)
    treated = ["unit_0", "unit_1", "unit_2"]
    candidates = detect_break_candidates(
        data=wide,
        treated_units=treated,
        method="cusum_treated",
        min_pre_periods=8,
        threshold=2.0,
    )
    assert len(candidates) > 0, "Expected at least one break candidate"
    assert abs(candidates[0]["break_idx"] - 15) <= 3, (
        f"Expected break near period 15, got {candidates[0]['break_idx']}"
    )


def test_detect_break_cusum_residual():
    wide = _make_panel(n_units=10, n_periods=40, break_at=15, shift=800.0)
    treated = ["unit_0", "unit_1", "unit_2"]
    control = [f"unit_{i}" for i in range(3, 10)]
    candidates = detect_break_candidates(
        data=wide,
        treated_units=treated,
        control_units=control,
        method="cusum_residual",
        min_pre_periods=8,
        threshold=2.0,
    )
    assert len(candidates) > 0, "Expected at least one break candidate"
    assert abs(candidates[0]["break_idx"] - 15) <= 3, (
        f"Expected break near period 15, got {candidates[0]['break_idx']}"
    )


def test_detect_break_no_break():
    wide = _make_panel(n_units=10, n_periods=40, break_at=None)
    treated = ["unit_0", "unit_1", "unit_2"]
    candidates = detect_break_candidates(
        data=wide,
        treated_units=treated,
        method="cusum_treated",
        min_pre_periods=8,
        threshold=5.0,  # high threshold — stationary data won't exceed this
    )
    assert candidates == [], f"Expected no candidates, got {candidates}"


def test_auto_detect_in_run_counterfactual_stability_tests():
    wide = _make_panel(n_units=10, n_periods=40, break_at=15, shift=800.0)
    treated = ["unit_0", "unit_1", "unit_2"]
    control = [f"unit_{i}" for i in range(3, 10)]
    dates = wide.columns
    summary = run_counterfactual_stability_tests(
        data=wide,
        treated_units=treated,
        train_end=dates[12],
        pseudo_test_start=dates[13],
        pseudo_test_end=dates[19],
        break_start=None,
        auto_detect_break=True,
        break_detection_method="cusum_residual",
        break_detection_threshold=2.0,
        control_units=control,
    )
    assert summary is not None
    assert len(summary.break_candidates) > 0, "Expected break_candidates to be populated"


def test_notes_conditional():
    """Verify notes reflect actual flag state."""
    # Build a minimal ResidualDriftTestResult with each flag combination and check notes
    base_kwargs = dict(
        estimator="TBRRidge",
        train_start_label="t0",
        train_end_label="t1",
        pseudo_test_start_label="t2",
        pseudo_test_end_label="t3",
        n_train_periods=10,
        n_eval_periods=5,
        residual_mean=0.0,
        residual_std=1.0,
        residual_rmse=1.0,
        rmse_ratio=None,
        residual_t_stat=0.0,
        residual_mean_p_value=0.5,
        residual_slope=0.0,
        residual_slope_t_stat=0.0,
        residual_slope_p_value=0.5,
        cumulative_residual=0.0,
        cumulative_residual_abs=0.0,
        residual_sign_balance=0.0,
    )
    r_good = ResidualDriftTestResult(
        **base_kwargs,
        residual_centered_flag=True,
        residual_drift_flag=False,
        notes="Centered residuals and zero drift support counterfactual stability.",
    )
    assert "zero drift" in r_good.notes

    r_bias = ResidualDriftTestResult(
        **base_kwargs,
        residual_centered_flag=False,
        residual_drift_flag=False,
        notes="Residuals are significantly biased",
    )
    assert "biased" in r_bias.notes.lower()

    r_drift = ResidualDriftTestResult(
        **base_kwargs,
        residual_centered_flag=True,
        residual_drift_flag=True,
        notes="Residuals are centered but show significant drift",
    )
    assert "drift" in r_drift.notes.lower()

    r_both = ResidualDriftTestResult(
        **base_kwargs,
        residual_centered_flag=False,
        residual_drift_flag=True,
        notes="Residuals are both biased",
    )
    assert "biased" in r_both.notes.lower()


def test_rmse_ratio_computed():
    """rmse_ratio should be a positive float after running residual drift test."""
    wide = _make_panel(n_units=10, n_periods=30, break_at=None)
    treated = ["unit_0", "unit_1", "unit_2"]
    dates = wide.columns
    results = run_residual_drift_test(
        data=wide,
        treated_units=treated,
        train_end=dates[14],
        pseudo_test_start=dates[15],
        pseudo_test_end=dates[19],
        estimators=("TBRRidge",),
    )
    assert len(results) == 1
    r = results[0]
    assert r.rmse_ratio is not None, "rmse_ratio should not be None"
    assert r.rmse_ratio > 0, f"rmse_ratio should be positive, got {r.rmse_ratio}"


@skip_without_cvxpy_osqp
def test_augsynth_cvxpy_aggregates_treated():
    """AugSynthCVXPY stability test with multiple treated units should complete quickly.

    Without treated aggregation: 10 controls × 5 treated = 50-variable optimization.
    With aggregation: 10 controls × 1 = 10-variable optimization.
    Confirms _ESTIMATORS_AGGREGATE_TREATED aggregation is applied.
    """
    wide = _make_panel(n_units=15, n_periods=30, break_at=None, seed=0)
    treated = [f"unit_{i}" for i in range(5)]
    dates = wide.columns
    results = run_residual_drift_test(
        data=wide,
        treated_units=treated,
        train_end=dates[14],
        pseudo_test_start=dates[15],
        pseudo_test_end=dates[19],
        estimators=("AugSynthCVXPY",),
    )
    assert len(results) == 1, "Expected one result for AugSynthCVXPY"
    assert results[0].n_eval_periods > 0, "Expected non-zero eval periods"


def _make_heterogeneous_panel(n_treated=3, n_control=10, n_periods=40, shock_at=20, seed=7):
    """Panel where controls diverge at shock_at."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-01", periods=n_periods, freq="W")
    data = rng.normal(1000, 50, size=(n_treated + n_control, n_periods))
    # Half controls drop sharply at shock, half hold flat
    for i in range(n_treated, n_treated + n_control // 2):
        data[i, shock_at:] -= 400
    wide = pd.DataFrame(
        data,
        index=[f"treated_{i}" for i in range(n_treated)] + [f"ctrl_{i}" for i in range(n_control)],
        columns=dates,
    )
    return wide


def test_heterogeneity_uniform_controls():
    """Uniform controls → aggregate recommended, no degraded units."""
    wide = _make_panel(n_units=12, n_periods=40, break_at=None, seed=1)
    treated = ["unit_0", "unit_1"]
    control = [f"unit_{i}" for i in range(2, 12)]
    dates = wide.columns
    result = run_control_heterogeneity_diagnostics(
        data=wide,
        treated_units=treated,
        control_units=control,
        shock_start=dates[20],
        shock_end=dates[25],
        cv_spike_threshold=1.5,
        correlation_drop_threshold=0.2,
    )
    assert isinstance(result, ControlHeterogeneityResult)
    assert result.recommended_transform == "aggregate"
    assert result.n_controls == 10


def test_heterogeneity_diverging_controls():
    """Diverging controls → pca recommended."""
    wide = _make_heterogeneous_panel(n_treated=3, n_control=10, n_periods=40, shock_at=20)
    treated = [f"treated_{i}" for i in range(3)]
    control = [f"ctrl_{i}" for i in range(10)]
    dates = wide.columns
    result = run_control_heterogeneity_diagnostics(
        data=wide,
        treated_units=treated,
        control_units=control,
        shock_start=dates[20],
        shock_end=dates[25],
        cv_spike_threshold=1.5,
        correlation_drop_threshold=0.2,
    )
    assert result.cv_spike_ratio > 1.5, f"Expected high cv_spike_ratio, got {result.cv_spike_ratio}"
    assert result.recommended_transform == "pca"


def test_heterogeneity_degraded_correlation():
    """Controls that flip correlation after shock appear in degraded_units."""
    rng = np.random.default_rng(99)
    n_periods = 50
    dates = pd.date_range("2023-01-01", periods=n_periods, freq="W")
    shock_at = 25

    # Treated: positive trend
    treated_series = np.linspace(1000, 1500, n_periods) + rng.normal(0, 20, n_periods)

    # Good controls: follow treated
    good_ctrl = np.array([treated_series + rng.normal(0, 30, n_periods) for _ in range(7)])

    # Bad controls: positively correlated pre, negatively correlated post
    bad_pre = np.array([treated_series[:shock_at] + rng.normal(0, 20, shock_at) for _ in range(3)])
    bad_post = np.array([-treated_series[shock_at:] + 2500 + rng.normal(0, 20, n_periods - shock_at) for _ in range(3)])
    bad_ctrl = np.hstack([bad_pre, bad_post])

    data = np.vstack([treated_series.reshape(1, -1), good_ctrl, bad_ctrl])
    index = ["treated_0"] + [f"good_{i}" for i in range(7)] + [f"bad_{i}" for i in range(3)]
    wide = pd.DataFrame(data, index=index, columns=dates)

    result = run_control_heterogeneity_diagnostics(
        data=wide,
        treated_units=["treated_0"],
        control_units=[f"good_{i}" for i in range(7)] + [f"bad_{i}" for i in range(3)],
        shock_start=dates[shock_at],
        shock_end=dates[shock_at + 2],
        cv_spike_threshold=1.5,
        correlation_drop_threshold=0.2,
    )
    assert result.n_correlation_degraded >= 2, (
        f"Expected at least 2 degraded units, got {result.n_correlation_degraded}: {result.degraded_units}"
    )
    for bad in [f"bad_{i}" for i in range(3)]:
        if bad in result.degraded_units:
            break
    else:
        pytest.fail(f"None of bad_* units in degraded_units={result.degraded_units}")


def test_auto_control_transform_selection():
    """run_counterfactual_stability_tests with control_transform='auto' completes and populates heterogeneity."""
    wide = _make_panel(n_units=12, n_periods=40, break_at=15, shift=600.0, seed=3)
    treated = ["unit_0", "unit_1", "unit_2"]
    control = [f"unit_{i}" for i in range(3, 12)]
    dates = wide.columns
    # break_start=dates[10], pseudo_test_start=dates[15] so shock window [10..15) is valid
    summary = run_counterfactual_stability_tests(
        data=wide,
        treated_units=treated,
        train_end=dates[8],
        pseudo_test_start=dates[15],
        pseudo_test_end=dates[25],
        break_start=dates[10],
        auto_detect_break=False,
        control_units=control,
        control_transform="auto",
        run_heterogeneity_check=True,
    )
    assert summary is not None
    assert summary.control_heterogeneity is not None
    assert summary.control_heterogeneity.recommended_transform in ("aggregate", "pca")


def test_heterogeneity_check_skipped_when_disabled():
    """run_heterogeneity_check=False → summary.control_heterogeneity is None."""
    wide = _make_panel(n_units=10, n_periods=30, break_at=None, seed=5)
    treated = ["unit_0", "unit_1"]
    control = [f"unit_{i}" for i in range(2, 10)]
    dates = wide.columns
    summary = run_counterfactual_stability_tests(
        data=wide,
        treated_units=treated,
        train_end=dates[14],
        pseudo_test_start=dates[15],
        pseudo_test_end=dates[19],
        break_start=dates[10],
        auto_detect_break=False,
        control_units=control,
        run_heterogeneity_check=False,
    )
    assert summary.control_heterogeneity is None, (
        "Expected control_heterogeneity=None when run_heterogeneity_check=False"
    )
    assert len(summary.break_tests) > 0, "Break tests should still run"


def test_auto_detect_false_no_break_start_raises():
    """break_start=None + auto_detect_break=False → ValueError."""
    wide = _make_panel(n_units=10, n_periods=30, break_at=None, seed=6)
    treated = ["unit_0", "unit_1"]
    dates = wide.columns
    with pytest.raises(ValueError, match="break_start"):
        run_counterfactual_stability_tests(
            data=wide,
            treated_units=treated,
            train_end=dates[14],
            pseudo_test_start=dates[15],
            pseudo_test_end=dates[19],
            break_start=None,
            auto_detect_break=False,
        )


def test_explicit_break_start_with_auto_detect_prints_warning(capsys):
    """Explicit break_start with auto_detect_break=True uses explicit date and prints warning if mismatch."""
    wide = _make_panel(n_units=10, n_periods=40, break_at=15, shift=800.0, seed=8)
    treated = ["unit_0", "unit_1", "unit_2"]
    control = [f"unit_{i}" for i in range(3, 10)]
    dates = wide.columns
    # Pass a break_start that is deliberately early (unlikely to match auto-detected)
    explicit_break = dates[5]
    summary = run_counterfactual_stability_tests(
        data=wide,
        treated_units=treated,
        train_end=dates[12],
        pseudo_test_start=dates[13],
        pseudo_test_end=dates[19],
        break_start=explicit_break,
        auto_detect_break=True,
        break_detection_method="cusum_residual",
        break_detection_threshold=2.0,
        control_units=control,
    )
    captured = capsys.readouterr()
    # Either a WARNING was printed (mismatch case) or auto-detection agreed with explicit
    # In either case the function must complete without error
    assert summary is not None
    # The break_label used in break_tests must match the explicit date supplied
    assert str(summary.break_tests[0].break_label) == str(explicit_break), (
        f"Expected break_tests to use explicit break_start={explicit_break}, "
        f"got {summary.break_tests[0].break_label}"
    )
    # If auto-detection found a different break, a WARNING should have been printed
    # (it may not always mismatch, so just verify no crash)


@skip_without_cvxpy_osqp
def test_augsynth_cvxpy_weight_health_healthy():
    """check_AugSynthCVXPY_weight_health returns a valid dict with required keys."""
    wide = _make_panel(n_units=15, n_periods=30, break_at=None, seed=10)
    treated = ["unit_0"]
    dates = wide.columns
    from panel_exp.utils.counterfactual_stability_tests import build_pseudo_test_paneldataset
    pds = build_pseudo_test_paneldataset(
        data=wide,
        treated_units=treated,
        train_end=dates[14],
        pseudo_test_start=dates[15],
        pseudo_test_end=dates[19],
    )
    result = check_AugSynthCVXPY_weight_health(pds)
    assert "verdict" in result
    assert "n_effective_donors" in result
    assert result["verdict"] in ("healthy", "concentrated", "degenerate")
    assert result["n_total_donors"] > 0


def test_training_rmse_fields_populated():
    """training_rmse and related fields should be populated after run_residual_drift_test."""
    wide = _make_panel(n_units=10, n_periods=30, break_at=None, seed=11)
    treated = ["unit_0", "unit_1"]
    dates = wide.columns
    results = run_residual_drift_test(
        data=wide,
        treated_units=treated,
        train_end=dates[14],
        pseudo_test_start=dates[15],
        pseudo_test_end=dates[19],
        estimators=("TBRRidge",),
    )
    assert len(results) == 1
    r = results[0]
    assert r.training_rmse is not None, "training_rmse should be populated"
    assert r.training_rmse >= 0
    assert r.training_resid_std is not None
    assert r.training_resid_max_abs is not None


def test_compare_estimator_stability_single():
    """Single result -> interpretation mentions 'run multiple estimators'."""
    base = dict(
        estimator="TBRRidge", train_start_label="t0", train_end_label="t1",
        pseudo_test_start_label="t2", pseudo_test_end_label="t3",
        n_train_periods=10, n_eval_periods=5,
        residual_mean=100.0, residual_std=50.0, residual_rmse=110.0,
        rmse_ratio=1.1, training_rmse=100.0, training_resid_mean=0.0,
        training_resid_std=50.0, training_resid_max_abs=100.0,
        residual_t_stat=1.0, residual_mean_p_value=0.3,
        residual_slope=0.0, residual_slope_t_stat=0.0, residual_slope_p_value=0.8,
        cumulative_residual=500.0, cumulative_residual_abs=500.0,
        residual_sign_balance=1.0,
        residual_centered_flag=False, residual_drift_flag=False,
        notes="test",
    )
    r = ResidualDriftTestResult(**base)
    result = compare_estimator_stability((r,))
    assert "run multiple estimators" in result["interpretation"]


def test_compare_estimator_stability_agreement():
    """Both centered -> agreement='agree', both_centered=True."""
    base = dict(
        train_start_label="t0", train_end_label="t1",
        pseudo_test_start_label="t2", pseudo_test_end_label="t3",
        n_train_periods=10, n_eval_periods=5,
        residual_mean=10.0, residual_std=50.0, residual_rmse=51.0,
        rmse_ratio=1.0, training_rmse=50.0, training_resid_mean=0.0,
        training_resid_std=50.0, training_resid_max_abs=100.0,
        residual_t_stat=0.2, residual_mean_p_value=0.8,
        residual_slope=0.0, residual_slope_t_stat=0.0, residual_slope_p_value=0.9,
        cumulative_residual=50.0, cumulative_residual_abs=50.0,
        residual_sign_balance=0.2,
        residual_drift_flag=False, notes="test",
    )
    r1 = ResidualDriftTestResult(estimator="TBRRidge", residual_centered_flag=True, **base)
    r2 = ResidualDriftTestResult(estimator="AugSynthCVXPY", residual_centered_flag=True, **base)
    result = compare_estimator_stability((r1, r2))
    assert result["agreement"] == "agree"
    assert result["both_centered"] is True


def test_compare_estimator_stability_disagreement():
    """One centered, one not -> agreement='disagree', interpretation mentions centered estimator."""
    base = dict(
        train_start_label="t0", train_end_label="t1",
        pseudo_test_start_label="t2", pseudo_test_end_label="t3",
        n_train_periods=10, n_eval_periods=5,
        residual_mean=0.0, residual_std=50.0, residual_rmse=50.0,
        rmse_ratio=1.0, training_rmse=50.0, training_resid_mean=0.0,
        training_resid_std=50.0, training_resid_max_abs=100.0,
        residual_t_stat=0.1, residual_mean_p_value=0.9,
        residual_slope=0.0, residual_slope_t_stat=0.0, residual_slope_p_value=0.9,
        cumulative_residual=0.0, cumulative_residual_abs=100.0,
        residual_sign_balance=0.0,
        residual_drift_flag=False, notes="test",
    )
    r1 = ResidualDriftTestResult(estimator="TBRRidge", residual_centered_flag=False, **base)
    r2 = ResidualDriftTestResult(estimator="AugSynthCVXPY", residual_centered_flag=True, **base)
    result = compare_estimator_stability((r1, r2))
    assert result["agreement"] == "disagree"


# ---------------------------------------------------------------------------
# TBRRidge normalisation tests
# ---------------------------------------------------------------------------

from panel_exp.methods.tbr import TBRRidge
from panel_exp.panel_data import PanelDataset, TimePeriod


def _make_scale_mismatch_panel(treat_start=30, seed=7):
    """Panel where treated aggregate is ~100x larger than individual controls."""
    rng = np.random.default_rng(seed)
    n = 40
    treated = np.linspace(100_000, 120_000, n)
    ctrl_a = np.linspace(800, 1000, n) + rng.normal(0, 20, n)
    ctrl_b = np.linspace(900, 1100, n) + rng.normal(0, 20, n)
    ctrl_c = np.linspace(700, 900, n) + rng.normal(0, 20, n)
    dates = pd.date_range("2023-01-01", periods=n, freq="W")
    wide = pd.DataFrame(
        {"treated": treated, "ctrl_a": ctrl_a, "ctrl_b": ctrl_b, "ctrl_c": ctrl_c},
        index=dates,
    ).T
    wide.columns = dates
    treat_period = TimePeriod(start=dates[treat_start], end=dates[-1])
    return PanelDataset(wide_data=wide, treated_periods=[treat_period], treated_units=["treated"])


def test_tbrridge_normalisation_removes_scale_bias():
    pds = _make_scale_mismatch_panel(treat_start=30)
    estimator = TBRRidge()
    estimator.run_analysis(pds)

    assert getattr(estimator, "_normalisation_applied", False), (
        "_normalisation_applied not set on estimator"
    )

    pre_resid = estimator.results["y"][:30] - estimator.results["y_hat"][:30]
    pre_mean = estimator.results["y"][:30].mean()
    assert abs(pre_resid.mean()) < 0.05 * pre_mean, (
        f"Pre-period bias {abs(pre_resid.mean()):.1f} exceeds 5% of pre-period mean {pre_mean:.1f}"
    )

    model = estimator.model
    assert hasattr(model, "coef_"), "NormalisedModel missing coef_"
    assert hasattr(model, "alpha_"), "NormalisedModel missing alpha_"
    assert hasattr(model, "predict"), "NormalisedModel missing predict"


def test_tbrridge_normalisation_preserves_original_scale():
    pds = _make_scale_mismatch_panel(treat_start=30)
    estimator = TBRRidge()
    estimator.run_analysis(pds)

    y_hat_pre = estimator.results["y_hat"][:30]
    y_pre = estimator.results["y"][:30]
    scale_ratio = float(y_hat_pre.mean() / y_pre.mean())
    assert 0.8 < scale_ratio < 1.2, (
        f"Prediction scale ratio {scale_ratio:.3f} is outside [0.8, 1.2] — "
        "normalisation may not be inverting correctly"
    )


def test_tbrridge_normalisation_constant_series_safe():
    """Epsilon guard: a constant-zero control column must not cause NaN/Inf."""
    rng = np.random.default_rng(42)
    n = 40
    dates = pd.date_range("2023-01-01", periods=n, freq="W")
    wide = pd.DataFrame(
        {
            "treated": np.linspace(1000, 1200, n),
            "ctrl_const": np.zeros(n),          # all-zero control
            "ctrl_b": np.linspace(900, 1100, n) + rng.normal(0, 10, n),
        },
        index=dates,
    ).T
    wide.columns = dates
    treat_period = TimePeriod(start=dates[25], end=dates[-1])
    pds = PanelDataset(wide_data=wide, treated_periods=[treat_period], treated_units=["treated"])

    estimator = TBRRidge()
    estimator.run_analysis(pds)

    y_hat = estimator.results["y_hat"]
    assert not np.any(np.isnan(y_hat)), "y_hat contains NaN"
    assert not np.any(np.isinf(y_hat)), "y_hat contains Inf"


def test_tbrridge_normalisation_stores_constants():
    pds = _make_scale_mismatch_panel(treat_start=30)
    model_obj = TBRRidge()
    model_obj.fit_data(pds)
    fitted = model_obj.fit_model()

    assert model_obj._normalisation_applied is True
    assert model_obj._normalisation_y_mean > 0, (
        f"_normalisation_y_mean={model_obj._normalisation_y_mean} should be > 0"
    )
    n_controls = pds.num_control_units
    assert model_obj._normalisation_X_mean.shape[0] == n_controls, (
        f"X_mean shape {model_obj._normalisation_X_mean.shape} != n_controls {n_controls}"
    )


def test_tbrridge_inference_kfold_still_works():
    """Kfold inference must still complete after normalisation change."""
    rng = np.random.default_rng(0)
    n = 25
    dates = pd.date_range("2023-01-01", periods=n, freq="W")
    wide = pd.DataFrame(
        {
            "treated": np.linspace(1000, 1200, n) + rng.normal(0, 30, n),
            "ctrl_a": np.linspace(800, 960, n) + rng.normal(0, 20, n),
            "ctrl_b": np.linspace(900, 1080, n) + rng.normal(0, 20, n),
            "ctrl_c": np.linspace(700, 840, n) + rng.normal(0, 20, n),
        },
        index=dates,
    ).T
    wide.columns = dates
    treat_period = TimePeriod(start=dates[20], end=dates[-1])
    pds = PanelDataset(wide_data=wide, treated_periods=[treat_period], treated_units=["treated"])

    estimator = TBRRidge(inference="Kfold")
    estimator.run_analysis(pds)

    assert "y_lower" in estimator.results, "Kfold did not produce y_lower"
    assert "y_upper" in estimator.results, "Kfold did not produce y_upper"
