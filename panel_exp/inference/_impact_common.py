"""Shared setup helpers for ImpactAnalyzer inference modes."""

from __future__ import annotations

from typing import Any

import numpy as np

from panel_exp.inference.context import InferenceRunContext


def treatment_window_residuals(
    results: dict[str, Any],
    panel: Any,
) -> np.ndarray:
    """Post-period treated minus counterfactual; pooled sum when y is 2-D and y_hat is 1-D."""
    pre = panel.treated_start_idxs[0]
    y = np.asarray(results["y"], dtype=float)[pre:]
    y_hat = np.asarray(results["y_hat"], dtype=float)[pre:]
    if y.ndim == 2 and y_hat.ndim == 1:
        return y.sum(axis=1) - y_hat
    return y - y_hat


def is_tbrridge_multi_treated(analyzer: Any) -> bool:
    """TBRRidge pooled counterfactual with multiple treated units (001e geometry)."""
    return (
        analyzer.__class__.__name__ == "TBRRidge"
        and len(analyzer.panel_data.treated_units) > 1
    )


def prepare_y_and_y_hat(ctx: InferenceRunContext) -> np.ndarray:
    """Fit model, predict, normalize shapes; populate ``analyzer.results`` base keys."""
    a = ctx.analyzer
    a.fit_data(ctx.panel_data)
    a.model = a.fit_model()
    a.y_hat = a.model.predict(a.panel_data.control_series(a.panel_data.treated_units).values.T)

    y = a.panel_data.treated_series(a.panel_data.treated_units).values.T
    if y.shape[0] == a.panel_data.num_timepoints and y.shape[1] == 1:
        y = y.reshape(-1)

    if (
        len(a.y_hat.shape) == 2
        and a.y_hat.shape[0] == a.panel_data.num_timepoints
        and a.y_hat.shape[1] == 1
    ):
        a.y_hat = a.y_hat.reshape(-1)

    a.results = {
        "times": a.panel_data.times,
        "y": y,
        "y_hat": a.y_hat,
    }
    if is_tbrridge_multi_treated(a):
        y_mat = np.asarray(y, dtype=float)
        if y_mat.ndim == 1:
            y_mat = y_mat.reshape(a.panel_data.num_timepoints, -1)
        y_hat_vec = np.asarray(a.y_hat, dtype=float).reshape(-1)[: a.panel_data.num_timepoints]
        a.results["y"] = y_mat
        a.results["y_hat"] = y_hat_vec
        a.results["y_per_unit"] = y_mat
        a.results["readout_family"] = "tbrridge_pooled_counterfactual_multi_treated"
    return y


def flatten_single_unit_results(a: Any) -> None:
    if len(a.panel_data.treated_units) == 1:
        a.results["y_upper"] = a.results["y_upper"].flatten()
        a.results["y_hat"] = a.results["y_hat"].flatten()
        a.results["y_lower"] = a.results["y_lower"].flatten()


def apply_bounds_to_results(a: Any, bounds: np.ndarray) -> None:
    """
    Map k-fold / placebo / BRB bounds tensor to ``y_lower``, ``y_hat``, ``y_upper``.

    ``bounds`` channels are effect quantiles: ``[..., 0]`` lower, ``[..., 1]`` point,
    ``[..., 2]`` upper on the treatment-effect scale. Outcome-level intervals use
    counterfactual ``y_cf = y - effect_point`` so that ``y_lower < y_upper`` when
    ``effect_lo < effect_hi`` (required for relative-ATT recovery extraction).
    """
    effect_lo = bounds[:, :, 0].T
    effect_pt = bounds[:, :, 1].T
    effect_hi = bounds[:, :, 2].T
    y_arr = np.asarray(a.results["y"], dtype=float).reshape(effect_pt.shape)
    y_cf = y_arr - effect_pt
    a.results["y_hat"] = np.asarray(y_cf, dtype=float)
    a.results["y_lower"] = y_cf + effect_lo
    a.results["y_upper"] = y_cf + effect_hi
    flatten_single_unit_results(a)


def apply_effect_bounds_to_results(
    a: Any,
    effect_lower: np.ndarray,
    effect_upper: np.ndarray,
) -> None:
    """
    Map effect-scale interval bounds to outcome ``y_lower`` / ``y_upper``.

    Uses existing counterfactual ``y_hat`` as the point path; adds effect_lo/hi on
    the treatment-effect scale (F-INF-003 conformal orientation fix).
    """
    y_hat = np.asarray(a.results["y_hat"], dtype=float)
    effect_lower = np.asarray(effect_lower, dtype=float)
    effect_upper = np.asarray(effect_upper, dtype=float)
    if effect_lower.ndim == 2 and y_hat.ndim == 1 and effect_lower.shape[0] == y_hat.shape[0]:
        y_hat_b = y_hat[:, np.newaxis]
        a.results["y_lower"] = y_hat_b + effect_lower
        a.results["y_upper"] = y_hat_b + effect_upper
        return
    if effect_lower.shape != y_hat.shape:
        effect_lower = np.broadcast_to(effect_lower, y_hat.shape).copy()
        effect_upper = np.broadcast_to(effect_upper, y_hat.shape).copy()
    a.results["y_lower"] = y_hat + effect_lower
    a.results["y_upper"] = y_hat + effect_upper
    flatten_single_unit_results(a)


def apply_jkp_bounds_to_results(
    a: Any,
    effect_lower: np.ndarray,
    effect_point: np.ndarray,
    effect_upper: np.ndarray,
) -> None:
    """Map JKP post-period effect quantiles to outcome paths (incl. TBRRidge multi-treated)."""
    n_time = a.panel_data.num_timepoints
    n_units = len(a.panel_data.treated_units)
    lo = np.asarray(effect_lower, dtype=float)
    pt = np.asarray(effect_point, dtype=float)
    hi = np.asarray(effect_upper, dtype=float)
    bounds = np.zeros((n_units, n_time, 3))
    pre = a.panel_data.treated_start_idxs[0]
    post_len = lo.shape[0]
    bounds[:, pre : pre + post_len, 0] = lo.T
    bounds[:, pre : pre + post_len, 1] = pt.T
    bounds[:, pre : pre + post_len, 2] = hi.T
    apply_bounds_to_results(a, bounds)
