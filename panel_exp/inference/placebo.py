"""
Inference: Placebo
==================

Placebo inference for panel data.

Summary of changes
------------------
- Switched from scalar placebo ATT aggregation to full placebo effect paths
  across time so bands are constructed from the correct distribution.
- Implemented pointwise placebo envelopes using quantiles of placebo paths
  across control units.
- Added robust handling for estimator failures and NaN residuals during
  placebo generation.
- Improved treatment-window slicing using positional indexing to avoid
  time-label mismatches.
- Added RMSPE-based filtering of poor placebo fits to stabilize distributions.
- Separated two outputs:
  • `placebo(...)` → placebo null envelope (diagnostic).
  • `placebo_with_ci_inversion(...)` → CI around the estimate via
    randomization-test inversion on the treatment-window cumulative effect.

Notes
-----
- The placebo envelope is useful for null diagnostics but is not a confidence
  interval around the estimate.
- The inversion method targets the cumulative treatment-window effect and
  returns cumulative-effect CI bounds in the stats dictionary. The weekly band
  is a display band obtained by distributing the cumulative CI gap evenly over
  the treated periods.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from panel_exp.panel_data import PanelDataset, TimePeriod



def _rms(x):
    """Root mean square with NaN guard."""
    arr = np.asarray(x, dtype=float)
    if arr.size == 0:
        return np.nan
    return np.sqrt(np.mean(np.square(arr)))



def _effect_path_from_model_results(temp_model):
    """Extract effect path as y - y_hat from a fitted estimator."""
    return np.asarray(temp_model.results['y'] - temp_model.results['y_hat'], dtype=float)



def _get_treatment_end_time(pds):
    """Return treatment end time in the format expected by TimePeriod."""
    if pds.treated_end_idxs[0] >= pds.times.shape[0]:
        return None
    return pds.times[pds.treated_end_idxs[0]]



def _safe_ratio(num, den):
    """Safe ratio helper for RMSPE diagnostics."""
    if not np.isfinite(den) or den <= 0:
        return np.nan
    return float(num / den)



def _build_placebo_distribution(
    pds,
    model,
    use_rmspe_filter=True,
    max_pre_rmspe_multiple=5.0,
    **model_args,
):
    """
    Fit the observed treated assignment plus placebo-in-space assignments.

    Returns
    -------
    observed_effects : np.ndarray
        Effect path for the actual treated assignment.
    observed_stat : float
        Observed average treatment effect over the treated window (used by the
        placebo-envelope diagnostics).
    placebo_path_df : pd.DataFrame
        Pointwise placebo effect paths for eligible placebo units restricted to
        the full time axis. Rows are placebo units, columns are pds.times.
    residual_df : pd.DataFrame
        Effect paths for observed + placebo assignments. Rows are units,
        columns are pds.times.
    diagnostics_df : pd.DataFrame
        Diagnostics for observed + placebo assignments.
    treated_times : np.ndarray
        Time labels for the treated window only.
    """
    treatment_start_time = pds.times[pds.treated_start_idxs[0]]
    treatment_end_time = _get_treatment_end_time(pds)

    start = pds.treated_start_idxs[0]
    treated_len = pds.num_treated_time_periods[0]
    treated_times = pds.times[start:start + treated_len]

    treated_mask = np.zeros(pds.times.shape[0], dtype=bool)
    treated_mask[start:start + treated_len] = True
    pre_mask = np.zeros(pds.times.shape[0], dtype=bool)
    pre_mask[:start] = True

    residuals = []
    diagnostics = []

    observed_model = model(**model_args)
    observed_model.run_analysis(pds)
    observed_effects = _effect_path_from_model_results(observed_model)
    observed_post = observed_effects[treated_mask]
    observed_pre = observed_effects[pre_mask]
    observed_post_rmspe = _rms(observed_post)
    observed_pre_rmspe = _rms(observed_pre)
    observed_ratio = _safe_ratio(observed_post_rmspe, observed_pre_rmspe)
    observed_stat = float(np.nanmean(observed_post))

    observed_label = "__observed__"
    residuals.append([observed_label] + list(observed_effects))
    diagnostics.append(
        {
            'unit': observed_label,
            'is_observed': True,
            'is_treated_unit': True,
            'pre_rmspe': observed_pre_rmspe,
            'post_rmspe': observed_post_rmspe,
            'rmspe_ratio': observed_ratio,
            'att_mean': observed_stat,
            'att_abs_mean': abs(observed_stat),
        }
    )

    for unit in pds.control_units:
        modified_pd = pds.assign_treatment(
            [unit],
            [TimePeriod(treatment_start_time, treatment_end_time)],
        )

        temp_model = model(**model_args)
        try:
            temp_model.run_analysis(modified_pd)
        except (AttributeError, TypeError, ValueError):
            continue
        try:
            effects = _effect_path_from_model_results(temp_model)
        except (KeyError, TypeError):
            continue

        post_effects = effects[treated_mask]
        pre_effects = effects[pre_mask]
        pre_rmspe = _rms(pre_effects)
        post_rmspe = _rms(post_effects)
        ratio = _safe_ratio(post_rmspe, pre_rmspe)
        att_mean = float(np.nanmean(post_effects))

        residuals.append([unit] + list(effects))
        diagnostics.append(
            {
                'unit': unit,
                'is_observed': False,
                'is_treated_unit': False,
                'pre_rmspe': pre_rmspe,
                'post_rmspe': post_rmspe,
                'rmspe_ratio': ratio,
                'att_mean': att_mean,
                'att_abs_mean': abs(att_mean),
            }
        )

    residual_df = pd.DataFrame(residuals, columns=['unit'] + list(pds.times)).set_index('unit')
    diagnostics_df = pd.DataFrame(diagnostics).set_index('unit')

    eligible_placebos = diagnostics_df.index[~diagnostics_df['is_observed']]
    if use_rmspe_filter and np.isfinite(observed_pre_rmspe):
        keep_mask = diagnostics_df.loc[eligible_placebos, 'pre_rmspe'] <= max_pre_rmspe_multiple * observed_pre_rmspe
        eligible_placebos = diagnostics_df.loc[eligible_placebos].index[keep_mask]

    placebo_path_df = residual_df.loc[eligible_placebos]

    return observed_effects, observed_stat, placebo_path_df, residual_df, diagnostics_df, treated_times



def _placebo_ci_inversion(
    observed_stat: float,
    placebo_stats: np.ndarray,
    alpha: float,
    n_grid: int = 200,
    model_name: str | None = None,
) -> tuple[float, float]:
    """
    Compute (1-alpha) CI around the estimate via test inversion.

    For each theta, p(theta) = proportion of placebo distribution as or more
    extreme than |observed_stat - theta|. The CI is {theta : p(theta) >= alpha}.
    Confidence set is built from all theta with p(theta) >= alpha.
    """
    if placebo_stats.size == 0:
        return (np.nan, np.nan)
    placebo_stats = np.asarray(placebo_stats, dtype=float)
    placebo_stats = placebo_stats[np.isfinite(placebo_stats)]
    if placebo_stats.size == 0:
        return (np.nan, np.nan)
    n_placebo = placebo_stats.size

    def p_value(theta: float) -> float:
        # p(theta) = proportion of placebo with |placebo_total| >= |observed_total - theta|
        centered = observed_stat - theta
        return float((1.0 + np.sum(np.abs(placebo_stats) >= np.abs(centered))) / (n_placebo + 1.0))

    spread = max(float(np.ptp(placebo_stats)), 1.0)
    lo = min(observed_stat, np.min(placebo_stats)) - spread - 1e-6
    hi = max(observed_stat, np.max(placebo_stats)) + spread + 1e-6
    thetas = np.linspace(lo, hi, n_grid)
    p_vals = np.array([p_value(t) for t in thetas])

    in_ci = p_vals >= alpha
    if not np.any(in_ci):
        return (np.nan, np.nan)
    ci_low = float(np.min(thetas[in_ci]))
    ci_high = float(np.max(thetas[in_ci]))

    # Invariant: CI must contain observed_total_effect
    if not (ci_low <= observed_stat <= ci_high):
        p_at_obs = p_value(observed_stat)
        max_p_grid = float(np.max(p_vals))
        print(
            "[Placebo CI inversion BUG] ci_low <= observed_total <= ci_high violated. "
            f"observed_total={observed_stat}, ci_low={ci_low}, ci_high={ci_high}, "
            f"p_value(observed_total)={p_at_obs}, max_p_on_grid={max_p_grid}. "
            "Inspect p-value grid / acceptance logic."
        )

    # Debug prints: placebo_total_stats for TBR only
    if model_name == "TBR":
        print(f"[Placebo CI inversion] placebo_total_stats: {placebo_stats}")
        print(
            f"  min(placebo_total_stats)={float(np.min(placebo_stats))}, "
            f"max(placebo_total_stats)={float(np.max(placebo_stats))}, "
            f"mean(placebo_total_stats)={float(np.nanmean(placebo_stats))}, "
            f"median(placebo_total_stats)={float(np.nanmedian(placebo_stats))}"
        )

    return (ci_low, ci_high)



def placebo(
    pds,
    model,
    alpha=0.1,
    plot_1=False,
    plot_2=False,
    use_rmspe_filter=True,
    max_pre_rmspe_multiple=5.0,
    return_stats=False,
    **model_args,
):
    """
    Placebo-in-space null-envelope for panel estimators.

    This returns an array of shape (n_treated_units, n_timepoints, 3), where
    the last dimension is [lower, mean, upper]. For the treated window, the
    center is the observed treated effect path and the lower/upper bands are
    pointwise placebo-path quantiles across placebo units. This object is a
    placebo envelope around the null distribution, not a confidence interval
    around the estimate. Periods outside the treated window are zero-padded to
    match package expectations.
    """
    if len(pds.treated_units) != 1:
        raise NotImplementedError("placebo-in-space currently supports exactly one treated unit")

    observed_effects, observed_stat, placebo_path_df, residual_df, diagnostics_df, treated_times = _build_placebo_distribution(
        pds,
        model,
        use_rmspe_filter=use_rmspe_filter,
        max_pre_rmspe_multiple=max_pre_rmspe_multiple,
        **model_args,
    )

    start = pds.treated_start_idxs[0]
    treated_len = pds.num_treated_time_periods[0]
    pre_len = pds.num_timepoints - treated_len - pds.post_treated_periods
    post_len = pds.post_treated_periods
    treated_path = np.asarray(observed_effects[start:start + treated_len], dtype=float)

    if placebo_path_df.shape[0] == 0:
        lower_path = treated_path.copy()
        upper_path = treated_path.copy()
        placebo_stats = np.array([], dtype=float)
        p_value = np.nan
    else:
        placebo_treated_paths = placebo_path_df.iloc[:, start : start + treated_len].to_numpy(dtype=float)
        lower_path = np.nanquantile(placebo_treated_paths, alpha / 2.0, axis=0)
        upper_path = np.nanquantile(placebo_treated_paths, 1.0 - alpha / 2.0, axis=0)
        placebo_stats = np.nanmean(placebo_treated_paths, axis=1)
        p_value = float((1.0 + np.sum(np.abs(placebo_stats) >= abs(observed_stat))) / (placebo_stats.size + 1.0))

    ests = np.zeros((len(pds.treated_units), treated_len, 3))
    ests[0, :, 0] = lower_path
    ests[0, :, 1] = treated_path
    ests[0, :, 2] = upper_path

    out = np.concatenate(
        [
            np.zeros((len(pds.treated_units), pre_len, 3)),
            ests,
            np.zeros((len(pds.treated_units), post_len, 3)),
        ],
        axis=1,
    )

    if plot_1:
        placebo_units = [idx for idx in residual_df.index if idx != '__observed__']
        if len(placebo_units) > 0:
            plt.plot(residual_df.loc[placebo_units].T, color='black', alpha=0.25)
        plt.plot(residual_df.loc['__observed__'].values, color='red')
        plt.axvline(pds.times[pds.treated_start_idxs[0]])
        plt.title('Observed vs placebo effect paths')

    if plot_2:
        if placebo_path_df.shape[0] > 0:
            plt.hist(placebo_stats)
            plt.axvline(observed_stat)
        plt.title('Placebo distribution of average post-treatment effects')

    if return_stats:
        placebo_treated_paths = placebo_path_df.iloc[:, start:start + treated_len].to_numpy(dtype=float) if placebo_path_df.shape[0] > 0 else np.empty((0, treated_len))
        stats_dict = {
            'p_value': p_value,
            'observed_stat': observed_stat,
            'placebo_stats': placebo_stats,
            'placebo_path_df': placebo_path_df,
            'placebo_treated_paths': placebo_treated_paths,
            'residual_df': residual_df,
            'diagnostics_df': diagnostics_df,
            'treated_times': treated_times,
        }
        return out, stats_dict

    return out



def placebo_with_ci_inversion(
    pds,
    model,
    alpha=0.1,
    use_rmspe_filter=True,
    max_pre_rmspe_multiple=5.0,
    n_grid=200,
    **model_args,
):
    """
    Placebo inference with randomization-test inversion CI around the estimate.

    Returns
    -------
    tuple
        (bounds_array, stats_dict). The returned bounds array has the same shape
        contract as other inference methods: [lower, mean, upper]. The center is
        the observed treated effect path. The inversion itself is performed on
        the cumulative treatment-window effect, and the returned stats dict
        includes cumulative CI bounds. The weekly lower/upper bands are a
        display approximation obtained by spreading the cumulative CI offsets
        evenly across treated periods.
    """
    out, stats_dict = placebo(
        pds,
        model,
        alpha=alpha,
        plot_1=False,
        plot_2=False,
        use_rmspe_filter=use_rmspe_filter,
        max_pre_rmspe_multiple=max_pre_rmspe_multiple,
        return_stats=True,
        **model_args,
    )

    start = pds.treated_start_idxs[0]
    treated_effect_path = np.asarray(out[0, start:start + pds.num_treated_time_periods[0], 1], dtype=float)
    treated_len = pds.num_treated_time_periods[0]
    observed_total = float(np.nansum(treated_effect_path))
    placebo_treated_paths = np.asarray(stats_dict.get('placebo_treated_paths', np.empty((0, treated_len))), dtype=float)
    placebo_total_stats = np.nansum(placebo_treated_paths, axis=1) if placebo_treated_paths.size > 0 else np.array([], dtype=float)

    model_name = getattr(model, "__name__", None)
    ci_low, ci_high = _placebo_ci_inversion(
        observed_total,
        placebo_total_stats,
        alpha=alpha,
        n_grid=n_grid,
        model_name=model_name,
    )
    stats_dict['observed_total_effect'] = observed_total
    stats_dict['placebo_total_stats'] = placebo_total_stats
    stats_dict['ci_low_inversion'] = ci_low
    stats_dict['ci_high_inversion'] = ci_high

    if np.isfinite(ci_low) and np.isfinite(ci_high) and treated_len > 0:
        lower_total_offset = float(observed_total - ci_low)
        upper_total_offset = float(ci_high - observed_total)
        lower_weekly_offset = lower_total_offset / treated_len
        upper_weekly_offset = upper_total_offset / treated_len
        out[0, start:start + treated_len, 0] = treated_effect_path - lower_weekly_offset
        out[0, start:start + treated_len, 2] = treated_effect_path + upper_weekly_offset
        stats_dict['band_type'] = 'cumulative_effect_inversion_display_band'
    else:
        stats_dict['band_type'] = 'placebo_envelope_fallback'

    return out, stats_dict