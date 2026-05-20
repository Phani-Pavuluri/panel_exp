"""Tests for TROP (Triply Robust Panel Estimator) global and local modes."""

import numpy as np
import pandas as pd

from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.methods.triply_robust_est import TROP


def _make_small_panel(
    n_t=25,
    n_c=4,
    treat_start=15,
    effect=5.0,
    noise_scale=2.0,
    seed=42,
    inject_missing=None,
    n_treated_units=1,
):
    """Create a small panel for testing.

    Args:
        n_t: number of time periods
        n_c: number of control units
        treat_start: first treated period index
        effect: treatment effect size (added to treated cells)
        noise_scale: std of noise
        seed: random seed
        inject_missing: optional list of (row_idx, col_idx) to set to NaN (control cells only)
        n_treated_units: number of treated units (1 = single "treated", >1 = "treated", "treated2", ...)
    """
    np.random.seed(seed)
    treated_names = ["treated"] if n_treated_units == 1 else ["treated"] + [f"treated{i}" for i in range(1, n_treated_units)]
    control_names = [f"c{i}" for i in range(n_c)]
    units = treated_names + control_names
    times = list(range(n_t))
    data = []
    for t in times:
        for u in units:
            y = 10.0 + 0.1 * t + np.random.randn() * noise_scale
            if u in treated_names and t >= treat_start:
                y += effect
            data.append({"time": t, "unit": u, "y": y})
    df = pd.DataFrame(data)
    wide = df.pivot(index="unit", columns="time", values="y")

    if inject_missing is not None:
        wide = wide.copy()
        for ri, ci in inject_missing:
            if ri < len(wide.index) and ci < len(wide.columns):
                wide.iloc[ri, ci] = np.nan

    # PanelDataset requires one TimePeriod per treated unit (same length as treated_names)
    treated_periods = [TimePeriod(treat_start, n_t - 1) for _ in range(len(treated_names))]
    pds = PanelDataset(wide_data=wide, treated_periods=treated_periods, treated_units=treated_names)
    return pds


# -----------------------------------------------------------------------------
# 1. Smoke tests (renamed)
# -----------------------------------------------------------------------------
def test_trop_global_mode_smoke():
    """Global mode runs and produces expected outputs."""
    pds = _make_small_panel()
    trop = TROP(
        method="global",
        lambda_unit_grid=[0.1],
        lambda_time_grid=[0.1],
        lambda_nuclear_grid=[0.05],
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.fit_data(pds)
    wrapper = trop.fit_model()

    assert trop.fit_result_ is not None
    assert trop.fit_result_.method == "global"
    expected_shape = pds.wide_data.shape
    assert trop.fit_result_.counterfactual_matrix.shape == expected_shape
    assert trop.fit_result_.tau_hat_matrix.shape == expected_shape

    summary = trop.summarize_effects()
    assert "ate" in summary
    assert "total_incremental" in summary

    period_df = trop.period_effects()
    assert isinstance(period_df, pd.DataFrame)

    cf = trop.get_counterfactual_matrix()
    assert cf.shape == pds.wide_data.shape

    eff = trop.get_effect_matrix()
    assert eff.shape == pds.wide_data.shape

    comp = trop.get_component_matrices()
    assert "alpha" in comp and "delta" in comp and "low_rank" in comp

    assert wrapper.y_hat_full.ndim == 1
    assert len(wrapper.y_hat_full) == pds.wide_data.shape[1]


def test_trop_local_mode_smoke():
    """Local mode runs and produces expected outputs."""
    pds = _make_small_panel(n_t=20, n_c=3, treat_start=12)
    trop = TROP(
        method="local",
        lambda_unit_grid=[0.1],
        lambda_time_grid=[0.1],
        lambda_nuclear_grid=[0.05],
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.fit_data(pds)
    wrapper = trop.fit_model()

    assert trop.fit_result_ is not None
    assert trop.fit_result_.method == "local"
    expected_shape = pds.wide_data.shape
    assert trop.fit_result_.counterfactual_matrix.shape == expected_shape
    assert trop.fit_result_.tau_hat_matrix.shape == expected_shape

    treated_obs = trop.treated_mask_ & trop.observed_mask_
    cf = trop.fit_result_.counterfactual_matrix
    tau = trop.fit_result_.tau_hat_matrix
    assert np.all(np.isfinite(cf[treated_obs]))
    assert np.all(np.isfinite(tau[treated_obs]))

    assert trop.fit_result_.cell_converged_matrix is not None
    assert trop.fit_result_.cell_iterations_matrix is not None
    assert trop.fit_result_.cell_objective_matrix is not None

    assert wrapper.y_hat_full.ndim == 1


# -----------------------------------------------------------------------------
# 2. Positive-effect recovery tests
# -----------------------------------------------------------------------------
def test_trop_global_positive_effect_recovery():
    """Global mode recovers direction of a known positive effect."""
    pds = _make_small_panel(effect=8.0, noise_scale=1.0)
    trop = TROP(
        method="global",
        lambda_unit_grid=[0.1],
        lambda_time_grid=[0.1],
        lambda_nuclear_grid=[0.05],
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.fit_data(pds)
    trop.fit_model()
    summary = trop.summarize_effects()
    assert summary["ate"] > 0, "ATE should be positive for positive treatment effect"
    assert summary["total_incremental"] > 0, "total_incremental should be positive"


def test_trop_local_positive_effect_recovery():
    """Local mode recovers direction of a known positive effect."""
    pds = _make_small_panel(n_t=20, n_c=4, treat_start=12, effect=8.0, noise_scale=1.0)
    trop = TROP(
        method="local",
        lambda_unit_grid=[0.1],
        lambda_time_grid=[0.1],
        lambda_nuclear_grid=[0.05],
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.fit_data(pds)
    trop.fit_model()
    summary = trop.summarize_effects()
    assert summary["ate"] > 0, "ATE should be positive for positive treatment effect"
    assert summary["total_incremental"] > 0, "total_incremental should be positive"


# -----------------------------------------------------------------------------
# 3. Period-effects sanity test
# -----------------------------------------------------------------------------
def test_trop_period_effects_sanity():
    """Period effects behave sensibly around treatment boundary."""
    treat_start = 12
    pds = _make_small_panel(n_t=25, treat_start=treat_start, effect=6.0, noise_scale=1.0)
    trop = TROP(
        method="global",
        lambda_unit_grid=[0.1],
        lambda_time_grid=[0.1],
        lambda_nuclear_grid=[0.05],
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.fit_data(pds)
    trop.fit_model()
    period_df = trop.period_effects()

    if period_df.empty:
        return

    periods = period_df.index
    if hasattr(periods, "tolist"):
        period_vals = periods.tolist()
    else:
        period_vals = list(periods)

    post_mask = np.array([p >= treat_start for p in period_vals]) if period_vals else np.array([])

    if post_mask.any():
        post_incremental = period_df.iloc[post_mask]["incremental"]
        assert (post_incremental > 0).all() or post_incremental.mean() > 0, (
            "Post-treatment incremental should be positive"
        )


# -----------------------------------------------------------------------------
# 4. Local-mode semantics test
# -----------------------------------------------------------------------------
def test_trop_local_mode_semantics():
    """Local mode contract: tau zero off treated, diagnostics only on treated_obs."""
    pds = _make_small_panel(n_t=20, n_c=3, treat_start=12)
    trop = TROP(
        method="local",
        lambda_unit_grid=[0.1],
        lambda_time_grid=[0.1],
        lambda_nuclear_grid=[0.05],
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.fit_data(pds)
    trop.fit_model()

    treated_obs = trop.treated_mask_ & trop.observed_mask_
    not_treated = ~trop.treated_mask_

    cf = trop.fit_result_.counterfactual_matrix
    tau = trop.fit_result_.tau_hat_matrix
    assert np.all(np.isfinite(cf[treated_obs])), "Counterfactuals on treated_obs must be finite"
    assert np.all(np.isfinite(tau[treated_obs])), "tau on treated_obs must be finite"
    assert np.all(tau[not_treated] == 0), "tau_hat_matrix must be zero on non-treated cells"

    cell_conv = trop.fit_result_.cell_converged_matrix
    cell_iter = trop.fit_result_.cell_iterations_matrix
    cell_obj = trop.fit_result_.cell_objective_matrix
    assert np.all(np.isfinite(cell_conv[treated_obs])), "cell_converged on treated_obs must be finite"
    assert np.all(np.isfinite(cell_iter[treated_obs])), "cell_iterations on treated_obs must be finite"
    assert np.all(np.isfinite(cell_obj[treated_obs])), "cell_objective on treated_obs must be finite"
    assert np.all(np.isnan(cell_conv[not_treated])), "cell_converged off treated must be nan"
    assert np.all(np.isnan(cell_iter[not_treated])), "cell_iterations off treated must be nan"
    assert np.all(np.isnan(cell_obj[not_treated])), "cell_objective off treated must be nan"


# -----------------------------------------------------------------------------
# 5. Missing-data tests
# -----------------------------------------------------------------------------
def test_trop_global_missing_data():
    """Global mode handles missing values in control cells."""
    pds = _make_small_panel(n_t=25, n_c=5, treat_start=15)
    wide = pds.wide_data.copy()
    wide.iloc[2, 3] = np.nan
    wide.iloc[3, 7] = np.nan
    pds = PanelDataset(wide, [pds.treated_periods[0]], list(pds.treated_units))

    trop = TROP(
        method="global",
        lambda_unit_grid=[0.1],
        lambda_time_grid=[0.1],
        lambda_nuclear_grid=[0.05],
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.fit_data(pds)
    trop.fit_model()

    treated_obs = trop.treated_mask_ & trop.observed_mask_
    assert np.all(np.isfinite(trop.fit_result_.counterfactual_matrix[treated_obs]))
    assert np.all(np.isfinite(trop.fit_result_.tau_hat_matrix[treated_obs]))
    summary = trop.summarize_effects()
    assert np.isfinite(summary["ate"])


def test_trop_local_missing_data():
    """Local mode handles missing values in control cells."""
    pds = _make_small_panel(n_t=20, n_c=4, treat_start=12)
    wide = pds.wide_data.copy()
    wide.iloc[2, 5] = np.nan
    pds = PanelDataset(wide, [pds.treated_periods[0]], list(pds.treated_units))

    trop = TROP(
        method="local",
        lambda_unit_grid=[0.1],
        lambda_time_grid=[0.1],
        lambda_nuclear_grid=[0.05],
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.fit_data(pds)
    trop.fit_model()

    treated_obs = trop.treated_mask_ & trop.observed_mask_
    assert np.all(np.isfinite(trop.fit_result_.counterfactual_matrix[treated_obs]))
    assert np.all(np.isfinite(trop.fit_result_.tau_hat_matrix[treated_obs]))
    summary = trop.summarize_effects()
    assert np.isfinite(summary["ate"])


# -----------------------------------------------------------------------------
# 6. Inference override tests
# -----------------------------------------------------------------------------
def test_trop_inference_override_global_placebo():
    """global + inference_mode=placebo reports placebo."""
    pds = _make_small_panel()
    trop = TROP(method="global", inference_mode="placebo", cv_max_cycles=1, max_cv_placebos=2)
    trop.fit_data(pds)
    trop.fit_model()
    inf = trop.inference_summary()
    assert inf["estimation_method"] == "global"
    assert inf["inference_method"] == "placebo"
    assert "ate" in inf and "ci_percentile" in inf
    assert np.isfinite(inf["ate"])


def test_trop_inference_override_global_bootstrap():
    """global + inference_mode=bootstrap with 2+ treated units reports bootstrap."""
    pds = _make_small_panel(n_treated_units=2)
    trop = TROP(
        method="global",
        inference_mode="bootstrap",
        n_bootstrap=10,
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.fit_data(pds)
    trop.fit_model()
    inf = trop.inference_summary()
    assert inf["estimation_method"] == "global"
    assert inf["inference_method"] == "bootstrap"
    assert "ate" in inf
    assert np.isfinite(inf["ate"])


def test_trop_inference_override_local_placebo():
    """local + inference_mode=placebo reports placebo."""
    pds = _make_small_panel(n_t=20, n_c=3)
    trop = TROP(method="local", inference_mode="placebo", cv_max_cycles=1, max_cv_placebos=2)
    trop.fit_data(pds)
    trop.fit_model()
    inf = trop.inference_summary()
    assert inf["estimation_method"] == "local"
    assert inf["inference_method"] == "placebo"
    assert np.isfinite(inf["ate"])


def test_trop_inference_override_local_bootstrap():
    """local + inference_mode=bootstrap reports bootstrap when 2+ treated units."""
    pds = _make_small_panel(n_t=20, n_c=3, n_treated_units=2)
    trop = TROP(
        method="local",
        inference_mode="bootstrap",
        n_bootstrap=10,
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.fit_data(pds)
    trop.fit_model()
    inf = trop.inference_summary()
    assert inf["estimation_method"] == "local"
    assert inf["inference_method"] == "bootstrap"
    assert np.isfinite(inf["ate"])


def test_trop_inference_override_local_auto():
    """local + inference_mode=auto defaults to placebo."""
    pds = _make_small_panel(n_t=20, n_c=3)
    trop = TROP(method="local", inference_mode="auto", cv_max_cycles=1, max_cv_placebos=2)
    trop.fit_data(pds)
    trop.fit_model()
    inf = trop.inference_summary()
    assert inf["estimation_method"] == "local"
    assert inf["inference_method"] == "placebo"


# -----------------------------------------------------------------------------
# 7. Bootstrap-fallback honesty test
# -----------------------------------------------------------------------------
def test_trop_bootstrap_fallback_honesty():
    """When only 1 treated unit and inference_mode=bootstrap, report actual method (placebo)."""
    pds = _make_small_panel()
    trop = TROP(
        method="global",
        inference_mode="bootstrap",
        n_bootstrap=10,
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.fit_data(pds)
    trop.fit_model()
    inf = trop.inference_summary()
    assert inf["estimation_method"] == "global"
    assert inf["inference_method"] == "placebo", (
        "With 1 treated unit, bootstrap falls back to placebo; must report placebo honestly"
    )


# -----------------------------------------------------------------------------
# 8. cv_mode default and override tests
# -----------------------------------------------------------------------------
def test_trop_cv_mode_default_global():
    """TROP(method=global).cv_mode == global_obs."""
    trop = TROP(method="global")
    assert trop.cv_mode == "global_obs"


def test_trop_cv_mode_default_local():
    """TROP(method=local).cv_mode == local_obs."""
    trop = TROP(method="local")
    assert trop.cv_mode == "local_obs"


def test_trop_cv_mode_override():
    """Explicit cv_mode is stored as passed."""
    trop = TROP(method="global", cv_mode="local_obs")
    assert trop.cv_mode == "local_obs"


def test_trop_cv_mode_global_obs_routes_through_global_scorer():
    """method=global default cv_mode=global_obs uses _cv_score_global_obs during tuning."""
    pds = _make_small_panel()
    trop = TROP(method="global", cv_max_cycles=1, max_cv_placebos=2)
    trop.fit_data(pds)
    trop._validate_panel()
    trop._build_assignment_masks()

    called = {"global": False, "local": False}
    orig_global = trop._cv_score_global_obs
    orig_local = trop._cv_score_local_obs

    def wrap_global(*args, **kwargs):
        called["global"] = True
        return orig_global(*args, **kwargs)

    def wrap_local(*args, **kwargs):
        called["local"] = True
        return orig_local(*args, **kwargs)

    trop._cv_score_global_obs = wrap_global
    trop._cv_score_local_obs = wrap_local
    trop._tune_parameters()
    assert called["global"], "cv_mode=global_obs must use global scorer"
    assert not called["local"]


def test_trop_cv_mode_local_obs_routes_through_local_scorer():
    """method=local default cv_mode=local_obs uses _cv_score_local_obs during tuning."""
    pds = _make_small_panel(n_t=20, n_c=3, treat_start=12)
    trop = TROP(method="local", cv_max_cycles=1, max_cv_placebos=2)
    trop.fit_data(pds)
    trop._validate_panel()
    trop._build_assignment_masks()

    called = {"global": False, "local": False}
    orig_global = trop._cv_score_global_obs
    orig_local = trop._cv_score_local_obs

    def wrap_global(*args, **kwargs):
        called["global"] = True
        return orig_global(*args, **kwargs)

    def wrap_local(*args, **kwargs):
        called["local"] = True
        return orig_local(*args, **kwargs)

    trop._cv_score_global_obs = wrap_global
    trop._cv_score_local_obs = wrap_local
    trop._tune_parameters()
    assert called["local"], "cv_mode=local_obs must use local scorer"
    assert not called["global"]


def test_trop_cv_mode_explicit_global_obs_on_local_estimator():
    """Local estimator with cv_mode=global_obs uses global scorer."""
    pds = _make_small_panel(n_t=20, n_c=3, treat_start=12)
    trop = TROP(method="local", cv_mode="global_obs", cv_max_cycles=1, max_cv_placebos=2)
    trop.fit_data(pds)
    trop._validate_panel()
    trop._build_assignment_masks()

    called = {"global": False, "local": False}
    orig_global = trop._cv_score_global_obs
    orig_local = trop._cv_score_local_obs

    def wrap_global(*args, **kwargs):
        called["global"] = True
        return orig_global(*args, **kwargs)

    def wrap_local(*args, **kwargs):
        called["local"] = True
        return orig_local(*args, **kwargs)

    trop._cv_score_global_obs = wrap_global
    trop._cv_score_local_obs = wrap_local
    trop._tune_parameters()
    assert called["global"], "cv_mode=global_obs must use global scorer regardless of method"
    assert not called["local"]


def test_trop_cv_mode_explicit_local_obs_on_global_estimator():
    """Global estimator with cv_mode=local_obs uses local scorer."""
    pds = _make_small_panel()
    trop = TROP(method="global", cv_mode="local_obs", cv_max_cycles=1, max_cv_placebos=2)
    trop.fit_data(pds)
    trop._validate_panel()
    trop._build_assignment_masks()

    called = {"global": False, "local": False}
    orig_global = trop._cv_score_global_obs
    orig_local = trop._cv_score_local_obs

    def wrap_global(*args, **kwargs):
        called["global"] = True
        return orig_global(*args, **kwargs)

    def wrap_local(*args, **kwargs):
        called["local"] = True
        return orig_local(*args, **kwargs)

    trop._cv_score_global_obs = wrap_global
    trop._cv_score_local_obs = wrap_local
    trop._tune_parameters()
    assert called["local"], "cv_mode=local_obs must use local scorer regardless of method"
    assert not called["global"]


def test_trop_cv_mode_invalid_raises():
    """Invalid cv_mode raises ValueError."""
    try:
        TROP(method="global", cv_mode="invalid")
        assert False, "Expected ValueError for invalid cv_mode"
    except ValueError as e:
        assert "cv_mode must be" in str(e)


# -----------------------------------------------------------------------------
# 9. Local diagnostics placement test
# -----------------------------------------------------------------------------
def test_trop_local_diagnostics_placement():
    """Local diagnostics populated only on treated_obs, nan elsewhere."""
    pds = _make_small_panel(n_t=20, n_c=3, treat_start=12)
    trop = TROP(
        method="local",
        lambda_unit_grid=[0.1],
        lambda_time_grid=[0.1],
        lambda_nuclear_grid=[0.05],
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.fit_data(pds)
    trop.fit_model()

    treated_obs = trop.treated_mask_ & trop.observed_mask_
    not_treated_obs = ~treated_obs

    for mat in (trop.fit_result_.cell_objective_matrix, trop.fit_result_.cell_iterations_matrix):
        assert np.all(np.isfinite(mat[treated_obs]))
        assert np.all(np.isnan(mat[not_treated_obs]))

    cell_conv = trop.fit_result_.cell_converged_matrix
    assert not np.all(np.isfinite(cell_conv)), "cell_converged should not be fully populated"
    assert np.all(np.isfinite(cell_conv[treated_obs]))


# -----------------------------------------------------------------------------
# 10. Consistency test: counterfactual and tau in local mode
# -----------------------------------------------------------------------------
def test_trop_local_counterfactual_tau_consistency():
    """On treated_obs: observed - counterfactual == tau_hat (within tolerance)."""
    pds = _make_small_panel(n_t=20, n_c=3, treat_start=12)
    trop = TROP(
        method="local",
        lambda_unit_grid=[0.1],
        lambda_time_grid=[0.1],
        lambda_nuclear_grid=[0.05],
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.fit_data(pds)
    trop.fit_model()

    Y = np.nan_to_num(trop.wide_.values.astype(float), nan=0.0)
    cf = trop.fit_result_.counterfactual_matrix
    tau = trop.fit_result_.tau_hat_matrix
    treated_obs = trop.treated_mask_ & trop.observed_mask_

    diff = Y[treated_obs] - cf[treated_obs]
    tau_vals = tau[treated_obs]
    np.testing.assert_allclose(diff, tau_vals, rtol=1e-5, atol=1e-8)


# -----------------------------------------------------------------------------
# 11. Strengthened run_analysis test
# -----------------------------------------------------------------------------
def test_trop_run_analysis_strengthened():
    """run_analysis produces finite y, y_hat; lengths match; post-treatment gap sensible."""
    pds = _make_small_panel(n_t=20, n_c=3, effect=6.0, noise_scale=1.0)
    trop = TROP(
        method="local",
        lambda_unit_grid=[0.1],
        lambda_time_grid=[0.1],
        lambda_nuclear_grid=[0.05],
        cv_max_cycles=1,
        max_cv_placebos=2,
    )
    trop.run_analysis(pds)

    assert "y" in trop.results
    assert "y_hat" in trop.results
    y = np.asarray(trop.results["y"]).ravel()
    y_hat = np.asarray(trop.results["y_hat"]).ravel()
    assert np.all(np.isfinite(y))
    assert np.all(np.isfinite(y_hat))
    assert len(y) == len(y_hat)

    treat_start = pds.treated_start_idxs[0]
    post_y = y[treat_start:]
    post_y_hat = y_hat[treat_start:]
    post_gap = np.mean(post_y - post_y_hat)
    assert post_gap > 0, "For positive effect, post-treatment y - y_hat should be positive"


# -----------------------------------------------------------------------------
# 12. get_component_matrices raises in local mode
# -----------------------------------------------------------------------------
def test_trop_local_get_component_matrices_raises():
    """get_component_matrices raises in local mode."""
    pds = _make_small_panel(n_t=20, n_c=3)
    trop = TROP(method="local", cv_max_cycles=1, max_cv_placebos=2)
    trop.fit_data(pds)
    trop.fit_model()

    try:
        trop.get_component_matrices()
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "only available for global mode" in str(e)


# -----------------------------------------------------------------------------
# 13. Constructor validation
# -----------------------------------------------------------------------------
def test_trop_constructor_validation():
    """Constructor validates method and inference_mode."""
    try:
        TROP(method="invalid")
        assert False, "Expected ValueError for invalid method"
    except ValueError as e:
        assert "method must be" in str(e)
    try:
        TROP(inference_mode="invalid")
        assert False, "Expected ValueError for invalid inference_mode"
    except ValueError as e:
        assert "inference_mode must be" in str(e)
