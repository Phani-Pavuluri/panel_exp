"""Inference mode implementations (migrated from ImpactAnalyzer.run_analysis)."""

from __future__ import annotations

import numpy as np

from panel_exp.inference._impact_common import (
    apply_bounds_to_results,
    apply_effect_bounds_to_results,
    apply_jkp_bounds_to_results,
    flatten_single_unit_results,
    is_tbrridge_multi_treated,
    prepare_y_and_y_hat,
    treatment_window_residuals,
)
from panel_exp.inference.block_residual_bootstrap import block_residual_bootstrap
from panel_exp.inference.conformal import conformal
from panel_exp.inference.context import InferenceRunContext
from panel_exp.inference.k_fold import kfold, panel_timeseries_kfold, panel_timeseries_kfold_cumulative
from panel_exp.inference.placebo import placebo_with_ci_inversion
from panel_exp.inference.unit_jackknife import jkp, unit_jk
from panel_exp.inference_result import InferenceResult, IntervalType


def run_point_estimate(ctx: InferenceRunContext) -> None:
    prepare_y_and_y_hat(ctx)


def run_unit_jackknife(ctx: InferenceRunContext) -> None:
    a = ctx.analyzer
    prepare_y_and_y_hat(ctx)
    a.errors = unit_jk(a.panel_data, a.__class__, alpha=a.alpha, **ctx.inference_kwargs)
    err = np.asarray(a.errors, dtype=float)
    y_hat = np.asarray(a.results["y_hat"], dtype=float)
    if is_tbrridge_multi_treated(a):
        n_u = len(a.panel_data.treated_units)
        err_b = np.broadcast_to(err.reshape(-1, 1), (err.size, n_u))
        y_hat_b = np.broadcast_to(y_hat.reshape(-1, 1), (y_hat.size, n_u))
        a.results["y_upper"] = y_hat_b + err_b
        a.results["y_lower"] = y_hat_b - err_b
    else:
        a.results["y_upper"] = y_hat + err
        a.results["y_lower"] = y_hat - err


def run_jkp(ctx: InferenceRunContext) -> None:
    a = ctx.analyzer
    prepare_y_and_y_hat(ctx)
    a.lower, a.upper, a.y_hat_median = jkp(
        a.panel_data, a.__class__, alpha=a.alpha, **ctx.inference_kwargs
    )
    lo = np.asarray(a.lower, dtype=float)
    if lo.ndim == 2:
        apply_jkp_bounds_to_results(a, a.lower, a.y_hat_median, a.upper)
    else:
        a.results["y_lower"] = np.zeros_like(a.results["y"])
        a.results["y_upper"] = np.zeros_like(a.results["y"])
        pre = a.panel_data.treated_start_idxs[0]
        a.results["y_lower"][pre:] = a.results["y"][pre:] - a.lower
        a.results["y_upper"][pre:] = a.results["y"][pre:] - a.upper
        flatten_single_unit_results(a)


def run_bayesian(ctx: InferenceRunContext) -> None:
    import jax.numpy as jnp

    a = ctx.analyzer
    a.fit_data(ctx.panel_data)
    a.model = a.fit_model()
    a.y_hat = a.model.predict(a.panel_data.control_series(a.panel_data.treated_units).values.T)

    y_mu = jnp.mean(a.y_hat, axis=0)
    y_lower = jnp.quantile(a.y_hat, a.alpha, axis=0)
    y_upper = jnp.quantile(a.y_hat, 1 - a.alpha, axis=0)

    y = a.panel_data.treated_series(a.panel_data.treated_units).values.T
    if y.shape[0] == a.panel_data.num_timepoints and y.shape[1] == 1:
        y = y.reshape(-1)

    a.results = {
        "times": a.panel_data.times,
        "y": y,
        "y_hat": y_mu,
    }
    a.results["y_upper"] = y_upper
    a.results["y_lower"] = y_lower


def run_block_residual_bootstrap(ctx: InferenceRunContext) -> None:
    a = ctx.analyzer
    kw = ctx.inference_kwargs
    prepare_y_and_y_hat(ctx)

    _is_scm = a.__class__.__name__ in (
        "AugSynth",
        "AugSynthCVXPY",
        "SyntheticControlCVXPY",
    )
    _def_n, _def_bl, _def_mtp = (100, 8, 16) if _is_scm else (200, 7, 12)
    n_bootstrap = kw.pop("n_bootstrap", _def_n)
    block_length = kw.pop("block_length", _def_bl)
    min_train_periods = kw.pop("min_train_periods", _def_mtp)
    pool_donor_residuals = kw.pop("pool_donor_residuals", False)
    _sp = kw.pop("show_progress", None)
    show_progress = _sp if _sp is not None else _is_scm
    random_state = kw.pop("random_state", None)
    center_residuals = kw.pop("center_residuals", True)
    refit_in_bootstrap = kw.pop("refit_in_bootstrap", False)
    refit_mode = kw.pop("refit_mode", "post_only")
    ci_method = kw.pop("ci_method", "percentile")
    bootstrap_type = kw.pop("bootstrap_type", "block")
    variance_calibration_policy = kw.pop("variance_calibration_policy", "none")
    variance_scale_cap = kw.pop("variance_scale_cap", 10.0)

    a.bounds, brb_stats = block_residual_bootstrap(
        a.panel_data,
        a.__class__,
        alpha=a.alpha,
        n_bootstrap=n_bootstrap,
        block_length=block_length,
        min_train_periods=min_train_periods,
        pool_donor_residuals=pool_donor_residuals,
        show_progress=show_progress,
        random_state=random_state,
        center_residuals=center_residuals,
        refit_in_bootstrap=refit_in_bootstrap,
        refit_mode=refit_mode,
        ci_method=ci_method,
        bootstrap_type=bootstrap_type,
        variance_calibration_policy=variance_calibration_policy,
        variance_scale_cap=variance_scale_cap,
        return_stats=True,
        **kw,
    )
    a.results["block_residual_bootstrap_stats"] = brb_stats
    apply_bounds_to_results(a, a.bounds)
    a.results["effect_cumulative_brb"] = brb_stats.get("effect_cumulative_brb", np.nan)
    a.results["effect_ci_lower_cumulative_brb"] = brb_stats.get(
        "effect_ci_lower_cumulative_brb", np.nan
    )
    a.results["effect_ci_upper_cumulative_brb"] = brb_stats.get(
        "effect_ci_upper_cumulative_brb", np.nan
    )
    a.results["effect_mean_brb"] = brb_stats.get("effect_mean_brb", np.nan)
    a.results["effect_ci_lower_mean_brb"] = brb_stats.get("effect_ci_lower_mean_brb", np.nan)
    a.results["effect_ci_upper_mean_brb"] = brb_stats.get("effect_ci_upper_mean_brb", np.nan)
    a.results["bootstrap_interval_method"] = brb_stats.get("bootstrap_interval_method")
    a.results["bootstrap_replicate_estimand"] = brb_stats.get("bootstrap_replicate_estimand")
    a.results["bootstrap_center"] = brb_stats.get("bootstrap_center", np.nan)
    a.results["bootstrap_center_minus_point"] = brb_stats.get("bootstrap_center_minus_point", np.nan)


def run_conformal(ctx: InferenceRunContext) -> None:
    a = ctx.analyzer
    kw = ctx.inference_kwargs
    prepare_y_and_y_hat(ctx)

    pre = a.panel_data.treated_start_idxs[0]
    if is_tbrridge_multi_treated(a):
        y_post = np.asarray(a.results["y"], dtype=float)[pre:]
        y_hat_post = np.asarray(a.results["y_hat"], dtype=float)[pre:]
        resid = y_post - y_hat_post[:, np.newaxis]
        post_mean = float(np.nanmax(np.abs(resid))) if resid.size else 0.0
    else:
        resid = treatment_window_residuals(a.results, a.panel_data)
        post_mean = float(np.max(np.abs(resid))) if resid.size else 0.0
    if post_mean == 0.0:
        post_mean = 1.0

    lower, upper = conformal(
        a.panel_data,
        a.__class__,
        alpha=a.alpha,
        nulls=np.linspace(-post_mean * 10, post_mean * 10, 100),
        **kw,
    )

    a.lower = lower
    a.upper = upper
    apply_effect_bounds_to_results(a, lower, upper)


def run_kfold(ctx: InferenceRunContext) -> None:
    a = ctx.analyzer
    prepare_y_and_y_hat(ctx)
    a.bounds = kfold(a.panel_data, a.__class__)
    apply_bounds_to_results(a, a.bounds)


def run_placebo(ctx: InferenceRunContext) -> None:
    a = ctx.analyzer
    kw = ctx.inference_kwargs
    prepare_y_and_y_hat(ctx)

    n_control = len(a.panel_data.control_units)
    is_tbr = a.__class__.__name__ == "TBR"

    if is_tbr:
        a.results["placebo_unsupported"] = "TBR requires aggregated control; placebo-in-space excluded"
    elif n_control <= 1:
        a.results["placebo_unsupported"] = f"Placebo requires >1 control units (got {n_control})"
    elif n_control < 5:
        a.results["placebo_unsupported"] = f"Placebo requires >=5 control units (got {n_control})"

    if a.results.get("placebo_unsupported"):
        reason = a.results["placebo_unsupported"]
        a.inference_result = InferenceResult.unavailable(
            method="Placebo",
            alpha=a.alpha,
            reason=reason,
        )
        a.results["intervals_available"] = False
        a.results["interval_type"] = IntervalType.UNAVAILABLE.value
        placebo_strict = kw.get("placebo_strict", True)
        if placebo_strict:
            raise ValueError(f"Placebo inference unavailable: {reason}")
    else:
        a.bounds, placebo_stats_dict = placebo_with_ci_inversion(
            a.panel_data, a.__class__, alpha=a.alpha, **kw
        )
        a.results["placebo_stats"] = placebo_stats_dict
        apply_bounds_to_results(a, a.bounds)

        ci_low = placebo_stats_dict.get("ci_low_inversion")
        ci_high = placebo_stats_dict.get("ci_high_inversion")
        has_effect_ci = (
            ci_low is not None
            and ci_high is not None
            and np.isfinite(ci_low)
            and np.isfinite(ci_high)
        )
        if has_effect_ci:
            a.results["effect_ci_lower_inversion"] = float(ci_low)
            a.results["effect_ci_upper_inversion"] = float(ci_high)

        pre = a.panel_data.treated_start_idxs[0]
        point = float(np.nanmean(a.results["y"][pre:] - a.results["y_hat"][pre:]))
        a.inference_result = InferenceResult(
            point_estimate=point,
            interval_lower=float(ci_low) if has_effect_ci else None,
            interval_upper=float(ci_high) if has_effect_ci else None,
            interval_type=(
                IntervalType.CONFIDENCE_INTERVAL
                if has_effect_ci
                else IntervalType.UNAVAILABLE
            ),
            path_interval_type=IntervalType.PLACEBO_BAND,
            effect_interval_type=(
                IntervalType.CONFIDENCE_INTERVAL if has_effect_ci else None
            ),
            alpha=a.alpha,
            method="Placebo",
            assumptions={
                "placebo_in_space": True,
                "path_y_bounds_are_placebo_band": True,
                "ci_via_inversion": has_effect_ci,
            },
            warnings=(
                []
                if has_effect_ci
                else [
                    "Placebo path band present; cumulative-effect inversion CI not finite."
                ]
            ),
        )
        a.inference_result.attach_to_results(a.results)


def run_timeseries_kfold(ctx: InferenceRunContext) -> None:
    a = ctx.analyzer
    kw = ctx.inference_kwargs
    k = kw.get("k", 5)
    debias_flag = kw.get("debias_flag", True)
    block_scheme = kw.get("block_scheme", "expanding")
    n_jobs = kw.get("n_jobs", 1)
    random_state = kw.get("random_state", None)
    show_progress = kw.get("show_progress", True)
    diagnostics_path = kw.get("diagnostics_path", None) or getattr(a, "tsk_diagnostics_path", None)

    pre_t = a.panel_data.treated_start_idxs[0]
    model_pre_yhat: np.ndarray | None = None

    if a.full_model:
        a.fit_data(ctx.panel_data)
        a.model = a.fit_model()
        raw_yhat = a.model.predict(a.panel_data.control_series(a.panel_data.treated_units).values.T)
        if (
            len(raw_yhat.shape) == 2
            and raw_yhat.shape[0] == a.panel_data.num_timepoints
            and raw_yhat.shape[1] == 1
        ):
            raw_yhat = raw_yhat.reshape(-1)
        model_pre_yhat = np.asarray(raw_yhat[:pre_t], dtype=float).copy()

    y = a.panel_data.treated_series(a.panel_data.treated_units).values.T
    if y.shape[0] == a.panel_data.num_timepoints and y.shape[1] == 1:
        y = y.reshape(-1)

    a.results = {
        "times": a.panel_data.times,
        "y": y,
    }

    a.bounds = panel_timeseries_kfold(
        a.panel_data,
        a.__class__,
        alpha=a.alpha,
        k=k,
        debias_flag=debias_flag,
        block_scheme=block_scheme,
        n_jobs=n_jobs,
        random_state=random_state,
        show_progress=show_progress,
        diagnostics_path=diagnostics_path,
    )
    apply_bounds_to_results(a, a.bounds)

    if model_pre_yhat is not None:
        a.results["y_hat"][:pre_t] = model_pre_yhat

    cumulative_bounds = panel_timeseries_kfold_cumulative(
        a.panel_data,
        a.__class__,
        alpha=a.alpha,
        k=k,
        debias_flag=debias_flag,
        block_scheme=block_scheme,
        n_jobs=n_jobs,
        random_state=random_state,
        show_progress=show_progress,
    )
    pre_t = a.panel_data.treated_start_idxs[0]
    n_treated = a.panel_data.num_treated_time_periods[0]
    if n_treated > 0 and cumulative_bounds.shape[1] >= pre_t + n_treated:
        last_idx = pre_t + n_treated - 1
        cum_lo = cumulative_bounds[:, last_idx, 0]
        cum_mu = cumulative_bounds[:, last_idx, 1]
        cum_hi = cumulative_bounds[:, last_idx, 2]
        a.results["effect_cumulative_tsk"] = float(np.nanmean(cum_mu))
        a.results["effect_ci_lower_cumulative_tsk"] = float(np.nanmean(cum_lo))
        a.results["effect_ci_upper_cumulative_tsk"] = float(np.nanmean(cum_hi))
