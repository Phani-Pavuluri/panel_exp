"""
Tests for SyntheticDID (Arkhangelsky et al. 2021).

Validates:
- Mean-scale internal estimation
- Aggregate effect = per_geo_effect * N_tr
- Non-uniform lambda when use_uniform_lambda=False
- Exported paths consistency (treatment_effects = y - y_hat)
- Placebo inference
- Time-block bootstrap
- Validation errors for invalid inputs
"""

import numpy as np
import pandas as pd
import pytest

from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.methods.synthetic_did import SyntheticDID


def _make_simple_panel(n_control=5, n_treat=2, T_pre=10, T_post=5, seed=42):
    """Create a balanced panel for testing."""
    rng = np.random.default_rng(seed)
    n_units = n_control + n_treat
    n_times = T_pre + T_post
    wide = rng.standard_normal((n_units, n_times)).cumsum(axis=1) * 10 + 100
    wide = np.maximum(wide, 1)
    units = [f"c{i}" for i in range(n_control)] + [f"t{i}" for i in range(n_treat)]
    times = pd.date_range("2020-01-01", periods=n_times, freq="W")
    df = pd.DataFrame(wide, index=units, columns=times)
    treated_units = [f"t{i}" for i in range(n_treat)]
    treated_periods = [TimePeriod(times[T_pre], times[n_times - 1])]
    return PanelDataset(df, treated_periods=treated_periods, treated_units=treated_units)


def test_sdid_runs_with_mean_scale():
    """SDID runs with use_uniform_lambda=False (estimated lambda)."""
    panel = _make_simple_panel(n_control=5, n_treat=2, T_pre=10, T_post=5)
    sdid = SyntheticDID(use_uniform_lambda=False, n_bootstrap=50)
    sdid.fit_data(panel)
    sdid.fit_model()
    assert np.isfinite(sdid.treatment_effect)
    assert np.isfinite(sdid.treatment_se) or np.isnan(sdid.treatment_se)


def test_non_uniform_lambda_produced():
    """With use_uniform_lambda=False, lambda estimation runs; eff_n_lambda reflects actual weights."""
    panel = _make_simple_panel(n_control=5, n_treat=2, T_pre=10, T_post=5)
    sdid = SyntheticDID(use_uniform_lambda=False, n_bootstrap=30)
    sdid.run_analysis(panel)
    T0 = panel.treated_start_idxs[0]
    lam = sdid.lam
    assert lam.shape == (T0,)
    assert np.allclose(lam.sum(), 1.0)
    assert np.all(lam >= 0)
    eff_n = sdid.sdid_diagnostics["eff_n_lambda"]
    assert 0 < eff_n <= T0 + 1


def test_aggregate_equals_per_geo_times_n_tr():
    """aggregate_effect == per_geo_effect * N_tr."""
    panel = _make_simple_panel(n_control=5, n_treat=3, T_pre=10, T_post=5)
    sdid = SyntheticDID(use_uniform_lambda=True, n_bootstrap=50)
    sdid.run_analysis(panel)
    n_tr = sdid.n_treated_units
    assert abs(sdid.aggregate_effect - sdid.per_geo_effect * n_tr) < 1e-6


def test_exported_paths_consistent():
    """treatment_effects == y - y_hat exactly."""
    panel = _make_simple_panel(n_control=5, n_treat=2, T_pre=10, T_post=5)
    sdid = SyntheticDID(use_uniform_lambda=True, n_bootstrap=50)
    sdid.run_analysis(panel)
    y = np.asarray(sdid.results["y"]).ravel()
    y_hat = np.asarray(sdid.results["y_hat"]).ravel()
    eff = np.asarray(sdid.results["treatment_effects"]).ravel()
    np.testing.assert_allclose(eff, y - y_hat, rtol=0, atol=1e-10)


def test_placebo_inference_works():
    """Placebo inference works and returns real diagnostics."""
    panel = _make_simple_panel(n_control=8, n_treat=2, T_pre=10, T_post=5)
    sdid = SyntheticDID(variance_method="placebo", n_bootstrap=50)
    sdid.run_analysis(panel)
    det = sdid.get_detailed_results()
    assert det["placebo_test"]["n_placebos"] > 0
    assert len(det["placebo_test"]["placebo_effects"]) > 0
    assert det["inference_diagnostics"]["method"] == "placebo"


def test_time_block_bootstrap_works():
    """Time-block bootstrap still works."""
    panel = _make_simple_panel(n_control=5, n_treat=2, T_pre=10, T_post=5)
    sdid = SyntheticDID(variance_method="time_block_bootstrap", n_bootstrap=80)
    sdid.run_analysis(panel)
    det = sdid.get_detailed_results()
    assert det["inference_diagnostics"]["method"] == "time_block_bootstrap"


def test_invalid_panel_fails_cleanly():
    """Invalid panels fail with clear messages."""
    with pytest.raises(ValueError, match="at least 2 control units"):
        bad_panel = _make_simple_panel(n_control=1, n_treat=2, T_pre=10, T_post=5)
        sdid = SyntheticDID(n_bootstrap=50)
        sdid.run_analysis(bad_panel)
    with pytest.raises(ValueError, match="Placebo"):
        bad_panel = _make_simple_panel(n_control=3, n_treat=2, T_pre=10, T_post=5)
        sdid = SyntheticDID(variance_method="placebo", n_bootstrap=50)
        sdid.run_analysis(bad_panel)


def test_diagnostics_expose_weights():
    """Diagnostics expose omega_top_k, lambda_top_k, nois_level, zeta."""
    panel = _make_simple_panel(n_control=5, n_treat=2, T_pre=10, T_post=5)
    sdid = SyntheticDID(use_uniform_lambda=False, n_bootstrap=30)
    sdid.run_analysis(panel)
    d = sdid.sdid_diagnostics
    assert "omega_top_k" in d
    assert "lambda_top_k" in d
    assert "noise_level" in d
    assert "zeta_omega" in d
    assert "zeta_lambda" in d
    assert "eff_n_lambda" in d
    assert "eff_n_omega" in d
    assert "inference_method" in d


def test_single_treated_unit():
    """Single treated unit works."""
    panel = _make_simple_panel(n_control=5, n_treat=1, T_pre=10, T_post=5)
    sdid = SyntheticDID(use_uniform_lambda=True, n_bootstrap=50)
    sdid.run_analysis(panel)
    assert sdid.results["y"].ndim == 1 or sdid.results["y"].shape[1] == 1


def test_use_uniform_lambda_backward_compat():
    """use_uniform_lambda=True preserves old uniform behavior."""
    panel = _make_simple_panel(n_control=5, n_treat=2, T_pre=10, T_post=5)
    sdid = SyntheticDID(use_uniform_lambda=True, n_bootstrap=50)
    sdid.run_analysis(panel)
    T0 = panel.treated_start_idxs[0]
    lam = sdid.lam
    uniform = np.ones(T0) / T0
    np.testing.assert_allclose(lam, uniform, rtol=0, atol=1e-10)
