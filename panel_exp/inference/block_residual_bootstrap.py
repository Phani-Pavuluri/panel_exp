"""
Inference: Block Residual Bootstrap
===================================

Model-conditional moving-block residual bootstrap. The estimator is not re-fit
inside each bootstrap draw; cumulative bounds are the primary aggregate uncertainty
object. Weekly bands are for visualization.

High-level summary
------------------
This module implements a block residual bootstrap for panel-based causal
estimators. The procedure fits the estimator once on the observed panel,
extracts a pre-treatment out-of-sample residual pool from treated units using
expanding-window blocks, resamples those residuals in contiguous time blocks,
and adds the sampled noise back to the observed post-treatment effect path to
form bootstrap effect trajectories. Pointwise weekly bands are obtained from
the bootstrap path distribution, while cumulative-effect bands are obtained
from the bootstrap distribution of summed post-treatment effects.

Donor pooling (pool_donor_residuals=True) is an optional experimental mode
that adds control-unit forecast errors to the residual pool for single-treated
cases. The default is False; use only in targeted follow-up runs if needed.

Conceptually, this is a model-conditional time-series bootstrap: the fitted
counterfactual path is treated as fixed, while serially dependent residual
noise is re-sampled with block structure preserved.

References
----------
- Künsch, H. R. (1989). The jackknife and the bootstrap for general stationary
  observations. Annals of Statistics, 17(3), 1217–1241.
- Lahiri, S. N. (2003). Resampling Methods for Dependent Data. Springer.
- Bühlmann, P. (2002). Bootstraps for time series. Statistical Science, 17(1),
  52–72.
"""

from typing import Any, Optional

from panel_exp.panel_data import PanelDataset, TimePeriod

try:
    from tqdm.auto import tqdm
except ImportError:
    try:
        from tqdm import tqdm
    except ImportError:
        tqdm = None
import numpy as np
from scipy import stats


def _ensure_time_by_unit(arr: np.ndarray, num_timepoints: int) -> np.ndarray:
    """Normalize arrays to shape (time, units)."""
    arr = np.asarray(arr, dtype=float)
    if arr.ndim == 1:
        if arr.shape[0] != num_timepoints:
            raise ValueError(f"Expected length {num_timepoints}, got {arr.shape[0]}")
        return arr.reshape(num_timepoints, 1)
    if arr.ndim != 2:
        raise ValueError(f"Expected 1D or 2D array, got ndim={arr.ndim}")
    if arr.shape[0] == num_timepoints:
        return arr
    if arr.shape[1] == num_timepoints:
        return arr.T
    raise ValueError(f"Could not align array with num_timepoints={num_timepoints}; shape={arr.shape}")



# Note: This implementation uses a simple moving-block bootstrap rather than a
# stationary bootstrap or circular bootstrap. The goal is to preserve short-run
# serial dependence in the residual process while keeping the implementation
# lightweight and compatible with the package's existing inference API.

def _sample_moving_blocks(
    residuals: np.ndarray,
    target_len: int,
    block_length: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample moving residual blocks to length target_len."""
    residuals = np.asarray(residuals, dtype=float)
    if target_len <= 0:
        return np.empty((0, residuals.shape[1] if residuals.ndim == 2 else 1))
    if residuals.ndim == 1:
        residuals = residuals.reshape(-1, 1)
    n_pre = residuals.shape[0]
    if n_pre == 0:
        return np.zeros((target_len, residuals.shape[1]), dtype=float)
    block_length = max(1, min(int(block_length), n_pre))
    max_start = max(1, n_pre - block_length + 1)
    starts = np.arange(max_start)
    chunks = []
    total = 0
    while total < target_len:
        s = int(rng.choice(starts))
        chunk = residuals[s:s + block_length]
        chunks.append(chunk)
        total += chunk.shape[0]
    return np.vstack(chunks)[:target_len]


def _sample_wild_bootstrap(
    residuals: np.ndarray,
    target_len: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Wild bootstrap: sample rows with replacement and multiply by Rademacher (±1) signs."""
    residuals = np.asarray(residuals, dtype=float)
    if target_len <= 0:
        return np.empty((0, residuals.shape[1] if residuals.ndim == 2 else 1))
    if residuals.ndim == 1:
        residuals = residuals.reshape(-1, 1)
    n_pre = residuals.shape[0]
    n_series = residuals.shape[1]
    if n_pre == 0:
        return np.zeros((target_len, n_series), dtype=float)
    indices = rng.integers(0, n_pre, size=target_len)
    signs = 2 * rng.integers(0, 2, size=(target_len, n_series)) - 1
    return residuals[indices] * signs


def _compute_bca_quantiles(
    boot_values: np.ndarray,
    observed: float,
    alpha: float,
) -> tuple[float, float, float, float, float, bool]:
    """
    Compute BCa-adjusted quantiles for bootstrap distribution.
    Returns (lower, upper, bca_bias_correction, bca_acceleration, bca_fallback_used).
    If BCa fails numerically, returns percentile bounds and bca_fallback_used=True.
    """
    boot_flat = np.asarray(boot_values, dtype=float).ravel()
    boot_flat = boot_flat[np.isfinite(boot_flat)]
    n = len(boot_flat)
    if n < 10:
        return (
            float(np.nanquantile(boot_flat, alpha / 2.0)),
            float(np.nanquantile(boot_flat, 1.0 - alpha / 2.0)),
            0.0,
            0.0,
            True,
        )
    try:
        # Bias correction: proportion of bootstrap samples < observed
        p_less = np.mean(boot_flat < observed)
        z0 = stats.norm.ppf(np.clip(p_less, 1e-10, 1 - 1e-10))

        # Acceleration: jackknife-style over bootstrap sample (leave-one-out influence)
        # Simplified: use (mean - leave-one-out means) as proxy for acceleration
        jack_means = (np.sum(boot_flat) - boot_flat) / (n - 1)
        mean_jack = np.mean(jack_means)
        acc_num = np.sum((mean_jack - jack_means) ** 3)
        acc_denom = 6 * (np.sum((mean_jack - jack_means) ** 2) ** 1.5)
        if acc_denom < 1e-14:
            a_hat = 0.0
        else:
            a_hat = acc_num / acc_denom

        # BCa-adjusted quantiles
        z_alpha_2 = stats.norm.ppf(alpha / 2.0)
        z_1_minus_alpha_2 = stats.norm.ppf(1.0 - alpha / 2.0)
        adj_low = stats.norm.cdf(z0 + (z0 + z_alpha_2) / (1 - a_hat * (z0 + z_alpha_2)))
        adj_high = stats.norm.cdf(z0 + (z0 + z_1_minus_alpha_2) / (1 - a_hat * (z0 + z_1_minus_alpha_2)))

        # Clamp to valid quantile range
        adj_low = np.clip(adj_low, 0.0, 1.0)
        adj_high = np.clip(adj_high, 0.0, 1.0)
        if adj_low >= adj_high:
            raise ValueError("BCa quantiles invalid")

        lower = float(np.nanquantile(boot_flat, adj_low))
        upper = float(np.nanquantile(boot_flat, adj_high))
        return (lower, upper, float(z0), float(a_hat), False)
    except (ValueError, ZeroDivisionError, FloatingPointError):
        lower = float(np.nanquantile(boot_flat, alpha / 2.0))
        upper = float(np.nanquantile(boot_flat, 1.0 - alpha / 2.0))
        return (lower, upper, 0.0, 0.0, True)


def _residual_pool_per_period_std(pre_residuals: np.ndarray) -> float:
    """Per-period cross-unit mean residual std for variance calibration."""
    arr = np.asarray(pre_residuals, dtype=float)
    if arr.size == 0:
        return float("nan")
    if arr.ndim == 1:
        return float(np.nanstd(arr, ddof=1)) if arr.size > 1 else float("nan")
    per_period = np.nanmean(arr, axis=1)
    return float(np.nanstd(per_period, ddof=1)) if per_period.size > 1 else float("nan")


def _mean_effect_bootstrap_interval(
    boot_replicates: np.ndarray,
    point_estimate: float,
    alpha: float,
    *,
    variance_calibration_policy: str = "none",
    residual_pool_std: float | None = None,
    post_window_len: int | None = None,
    variance_scale_cap: float = 10.0,
) -> tuple[float, float, float, float]:
    """Centered-deviation percentile CI for mean post-window treatment effect.

    Bootstrap replicates and plug-in point must both be on the **mean effect**
    scale (average treated-minus-counterfactual over the post window).

    Returns (ci_lower, ci_upper, bootstrap_center, variance_scale_factor).
  """
    boot_flat = np.asarray(boot_replicates, dtype=float).ravel()
    boot_flat = boot_flat[np.isfinite(boot_flat)]
    if boot_flat.size == 0 or not np.isfinite(point_estimate):
        return np.nan, np.nan, np.nan, 1.0
    bootstrap_center = float(np.mean(boot_flat))
    boot_sd = float(np.std(boot_flat, ddof=1)) if boot_flat.size > 1 else 0.0
    deviations = boot_flat - bootstrap_center
    variance_scale = 1.0
    policy = str(variance_calibration_policy or "none").lower()

    if policy in ("residual_scaled", "variance_scaled", "brb_variance_calibrated"):
        if (
            residual_pool_std is not None
            and np.isfinite(residual_pool_std)
            and post_window_len
            and post_window_len > 0
            and boot_sd > 1e-12
        ):
            target_sd = float(residual_pool_std) / np.sqrt(float(post_window_len))
            variance_scale = float(
                np.clip(target_sd / boot_sd, 1.0, float(variance_scale_cap))
            )
            deviations = deviations * variance_scale
        ci_lower = float(point_estimate + np.percentile(deviations, (alpha / 2.0) * 100.0))
        ci_upper = float(point_estimate + np.percentile(deviations, (1.0 - alpha / 2.0) * 100.0))
    elif policy in ("studentized", "brb_studentized"):
        if boot_sd > 1e-12:
            pivots = (point_estimate - boot_flat) / boot_sd
            ci_lower = float(point_estimate - boot_sd * np.percentile(pivots, (1.0 - alpha / 2.0) * 100.0))
            ci_upper = float(point_estimate - boot_sd * np.percentile(pivots, (alpha / 2.0) * 100.0))
        else:
            ci_lower = float(point_estimate + np.percentile(deviations, (alpha / 2.0) * 100.0))
            ci_upper = float(point_estimate + np.percentile(deviations, (1.0 - alpha / 2.0) * 100.0))
    elif policy in ("null_calibrated", "brb_null_calibrated"):
        ci_lower = float(point_estimate + np.percentile(deviations, (alpha / 2.0) * 100.0))
        ci_upper = float(point_estimate + np.percentile(deviations, (1.0 - alpha / 2.0) * 100.0))
        width_before = float(ci_upper - ci_lower)
        if (
            residual_pool_std is not None
            and np.isfinite(residual_pool_std)
            and post_window_len
            and post_window_len > 0
        ):
            z = float(stats.norm.ppf(1.0 - alpha / 2.0))
            min_hw = z * float(residual_pool_std) / np.sqrt(float(post_window_len))
            if point_estimate - ci_lower < min_hw:
                ci_lower = float(point_estimate - min_hw)
            if ci_upper - point_estimate < min_hw:
                ci_upper = float(point_estimate + min_hw)
            if width_before > 1e-12:
                variance_scale = float((ci_upper - ci_lower) / width_before)
    else:
        ci_lower = float(point_estimate + np.percentile(deviations, (alpha / 2.0) * 100.0))
        ci_upper = float(point_estimate + np.percentile(deviations, (1.0 - alpha / 2.0) * 100.0))

    return ci_lower, ci_upper, bootstrap_center, variance_scale


# New helpers
def _slice_panel_to_periods(
    pds: 'PanelDataset',
    periods: list,
    treated_start_idx: int,
    treated_units: Optional[list] = None,
) -> 'PanelDataset':
    """Create a PanelDataset over the provided periods with a pseudo-treatment start."""
    new_wide_df = pds.wide_data.loc[:, periods].copy()
    new_wide_df.columns = range(len(new_wide_df.columns))
    treated_units = pds.treated_units if treated_units is None else treated_units
    return PanelDataset(
        new_wide_df,
        [TimePeriod(start=treated_start_idx, end=None) for _ in range(len(treated_units))],
        treated_units,
    )


def _replace_treated_outcomes_in_panel(
    pds: 'PanelDataset',
    treated_outcomes: np.ndarray,
) -> 'PanelDataset':
    """
    Replace treatment-window treated-unit outcomes with pseudo outcomes.

    Returns a new PanelDataset with the same control data and treatment periods,
    but treated-unit rows in the treatment-window columns replaced by the
    provided pseudo outcomes (time-by-unit shape).
    """
    start = pds.treated_start_idxs[0]
    treated_len = pds.num_treated_time_periods[0]
    end = start + treated_len
    treated_outcomes = _ensure_time_by_unit(np.asarray(treated_outcomes, dtype=float), treated_len)
    new_wide_df = pds.wide_data.copy()
    treatment_cols = new_wide_df.columns[start:end]
    new_wide_df.loc[pds.treated_units, treatment_cols] = treated_outcomes.T
    return PanelDataset(new_wide_df, pds.treated_periods, pds.treated_units)


def _replace_treated_preperiod_in_panel(
    pds: 'PanelDataset',
    treated_pre_outcomes: np.ndarray,
) -> 'PanelDataset':
    """
    Replace pre-period treated-unit outcomes with pseudo outcomes.

    Returns a new PanelDataset with the same control data, treatment timing,
    and post-period observed outcomes. Only treated-unit rows for the pre-period
    columns (0 to treated_start_idxs[0]) are replaced.
    """
    start = pds.treated_start_idxs[0]
    treated_pre_outcomes = _ensure_time_by_unit(
        np.asarray(treated_pre_outcomes, dtype=float), start
    )
    new_wide_df = pds.wide_data.copy()
    pre_cols = new_wide_df.columns[:start]
    new_wide_df.loc[pds.treated_units, pre_cols] = treated_pre_outcomes.T
    return PanelDataset(new_wide_df, pds.treated_periods, pds.treated_units)


def _collect_oos_pre_residuals(
    pds: 'PanelDataset',
    model: Any,
    block_length: int,
    center_residuals: bool = True,
    min_train_periods: Optional[int] = None,
    pool_donor_residuals: bool = False,
    show_progress: bool = False,
    verbose: bool = False,
    **model_args,
) -> np.ndarray:
    """
    Collect out-of-sample pre-period residuals using expanding-window blocks.

    Standard path (pool_donor_residuals=False): residuals from treated units
    only, one column per treated unit. Vector time-block sampling preserves
    cross-unit correlation within each block.

    Experimental path (pool_donor_residuals=True, single treated only): adds
    donor-unit forecast errors to the pool. Use only in targeted follow-up runs.

    The model is re-fit only to generate a pre-period residual pool. Final BRB
    treatment-period bands remain conditional on the single model fit on the
    full observed panel.
    """
    start = pds.treated_start_idxs[0]
    all_pre_periods = list(pds.times[:start])
    n_pre = len(all_pre_periods)
    n_treated_units = len(pds.treated_units)

    if n_pre == 0:
        return np.empty((0, n_treated_units), dtype=float)

    if min_train_periods is None:
        min_train_periods = max(block_length, 5)
    min_train_periods = max(1, min(int(min_train_periods), n_pre))

    # Standard OOS path: treated units only. Donor pooling is experimental (single-treated only).
    try:
        n_ctrl = len(pds.control_units) if hasattr(pds, 'control_units') else 0
    except Exception:
        n_ctrl = 0
    use_donor_pooling = bool(pool_donor_residuals and n_treated_units == 1 and n_ctrl > 0)

    if not use_donor_pooling:
        n_series = n_treated_units
        residual_rows = []

        # Pre-compute holdout block sequence for progress reporting
        block_starts = []
        hs = min_train_periods
        while hs < n_pre:
            he = min(hs + block_length, n_pre)
            if he > hs:
                block_starts.append(hs)
            hs = he

        use_tqdm = show_progress and tqdm is not None
        if verbose:
            print("[BRB verbose] Starting BRB OOS residual collection")
        iterator = tqdm(block_starts, desc="BRB OOS residual blocks") if use_tqdm else block_starts

        for holdout_start in iterator:
            holdout_end = min(holdout_start + block_length, n_pre)
            train_periods = all_pre_periods[:holdout_start]
            holdout_periods = all_pre_periods[holdout_start:holdout_end]

            if len(train_periods) == 0 or len(holdout_periods) == 0:
                continue

            periods = train_periods + holdout_periods

            try:
                fold_pds = _slice_panel_to_periods(
                    pds,
                    periods,
                    treated_start_idx=len(train_periods),
                    treated_units=list(pds.treated_units),
                )
                fold_model = model(**model_args)
                fold_model.run_analysis(fold_pds)
            except (AttributeError, TypeError, ValueError):
                continue

            y_fold = _ensure_time_by_unit(np.asarray(fold_model.results['y'], dtype=float), fold_pds.num_timepoints)
            yhat_fold = _ensure_time_by_unit(np.asarray(fold_model.results['y_hat'], dtype=float), fold_pds.num_timepoints)
            fold_resid = np.asarray(y_fold[len(train_periods):len(periods)] - yhat_fold[len(train_periods):len(periods)], dtype=float)
            residual_rows.append(fold_resid)

        if len(residual_rows) > 0:
            residual_pool = np.vstack(residual_rows)
            valid_mask = np.all(np.isfinite(residual_pool), axis=1)
            oos_residuals = residual_pool[valid_mask]
        else:
            residual_pool = np.empty((0, n_series), dtype=float)
            oos_residuals = residual_pool

        n_valid = oos_residuals.shape[0]
        min_required = max(3 * block_length, 10)
        use_fallback = n_valid == 0 or n_valid < min_required

        if use_fallback:
            fallback_model = model(**model_args)
            fallback_model.run_analysis(pds)
            y_full = _ensure_time_by_unit(np.asarray(fallback_model.results['y'], dtype=float), pds.num_timepoints)
            yhat_full = _ensure_time_by_unit(np.asarray(fallback_model.results['y_hat'], dtype=float), pds.num_timepoints)
            oos_residuals = np.asarray(y_full[:start] - yhat_full[:start], dtype=float)
            if verbose:
                reason = "empty" if n_valid == 0 else f"insufficient ({n_valid} < {min_required})"
                print(f"[BRB verbose] OOS residual pool {reason}; falling back to in-sample pre residuals.")

        if center_residuals and oos_residuals.size > 0:
            oos_residuals = oos_residuals - np.nanmean(oos_residuals, axis=0, keepdims=True)

        if verbose:
            resid_flat = np.ravel(oos_residuals)
            resid_mean = float(np.nanmean(resid_flat)) if resid_flat.size > 0 else np.nan
            resid_std = float(np.nanstd(resid_flat)) if resid_flat.size > 1 else 0.0
            resid_min = float(np.nanmin(resid_flat)) if resid_flat.size > 0 else np.nan
            resid_max = float(np.nanmax(resid_flat)) if resid_flat.size > 0 else np.nan
            pool_size = oos_residuals.shape[0]
            print(
                f"[BRB verbose] Residual pool: n_pre={n_pre}, n_valid_used={pool_size}, "
                f"n_units={n_treated_units}, pooled_donors=False, n_candidate_units={n_treated_units}, "
                f"block_length={block_length}, min_train_periods={min_train_periods}"
            )
            print(
                f"[BRB verbose] Residual scale: mean={resid_mean:.4g}, std={resid_std:.4g}, "
                f"min={resid_min:.4g}, max={resid_max:.4g}"
            )

        return np.asarray(oos_residuals, dtype=float)

    # Experimental: donor pooling for single-treated case only
    candidate_units = list(pds.treated_units) + list(pds.control_units)
    n_series = len(candidate_units)
    residual_rows = []

    block_starts = []
    hs = min_train_periods
    while hs < n_pre:
        he = min(hs + block_length, n_pre)
        if he > hs:
            block_starts.append(hs)
        hs = he

    use_tqdm = show_progress and tqdm is not None
    if verbose:
        print("[BRB verbose] Starting BRB OOS residual collection (donor pooling)")
    iterator = tqdm(block_starts, desc="BRB OOS residual blocks") if use_tqdm else block_starts

    for holdout_start in iterator:
        holdout_end = min(holdout_start + block_length, n_pre)
        train_periods = all_pre_periods[:holdout_start]
        holdout_periods = all_pre_periods[holdout_start:holdout_end]

        if len(train_periods) == 0 or len(holdout_periods) == 0:
            continue

        periods = train_periods + holdout_periods
        block_matrix = np.full((len(holdout_periods), n_series), np.nan)

        for j, unit in enumerate(candidate_units):
            try:
                unit_pds = _slice_panel_to_periods(pds, periods, treated_start_idx=len(train_periods), treated_units=[unit])
                fold_model = model(**model_args)
                fold_model.run_analysis(unit_pds)
            except (AttributeError, TypeError, ValueError):
                continue

            y_fold = _ensure_time_by_unit(np.asarray(fold_model.results['y'], dtype=float), unit_pds.num_timepoints)
            yhat_fold = _ensure_time_by_unit(np.asarray(fold_model.results['y_hat'], dtype=float), unit_pds.num_timepoints)
            fold_resid = np.asarray(y_fold[len(train_periods):len(periods)] - yhat_fold[len(train_periods):len(periods)], dtype=float)
            fold_resid = _ensure_time_by_unit(fold_resid, len(holdout_periods))
            block_matrix[:, j] = fold_resid[:, 0]

        residual_rows.append(block_matrix)

    if len(residual_rows) > 0:
        residual_pool = np.vstack(residual_rows)
        valid_mask = np.all(np.isfinite(residual_pool), axis=1)
        oos_residuals = residual_pool[valid_mask]
    else:
        residual_pool = np.empty((0, n_series), dtype=float)
        oos_residuals = residual_pool

    n_valid = oos_residuals.shape[0]
    min_required = max(3 * block_length, 10)
    use_fallback = n_valid == 0 or n_valid < min_required

    if use_fallback:
        fallback_model = model(**model_args)
        fallback_model.run_analysis(pds)
        y_full = _ensure_time_by_unit(np.asarray(fallback_model.results['y'], dtype=float), pds.num_timepoints)
        yhat_full = _ensure_time_by_unit(np.asarray(fallback_model.results['y_hat'], dtype=float), pds.num_timepoints)
        oos_residuals = np.asarray(y_full[:start] - yhat_full[:start], dtype=float)
        if oos_residuals.ndim == 1:
            oos_residuals = oos_residuals.reshape(-1, 1)
        if verbose:
            reason = "empty" if n_valid == 0 else f"insufficient ({n_valid} < {min_required})"
            print(f"[BRB verbose] OOS residual pool {reason}; falling back to in-sample pre residuals.")

    if center_residuals and oos_residuals.size > 0:
        oos_residuals = oos_residuals - np.nanmean(oos_residuals, axis=0, keepdims=True)

    if verbose:
        resid_flat = np.ravel(oos_residuals)
        resid_mean = float(np.nanmean(resid_flat)) if resid_flat.size > 0 else np.nan
        resid_std = float(np.nanstd(resid_flat)) if resid_flat.size > 1 else 0.0
        resid_min = float(np.nanmin(resid_flat)) if resid_flat.size > 0 else np.nan
        resid_max = float(np.nanmax(resid_flat)) if resid_flat.size > 0 else np.nan
        pool_size = oos_residuals.shape[0]
        print(
            f"[BRB verbose] Residual pool (donor pooling): n_pre={n_pre}, n_valid_used={pool_size}, "
            f"n_candidate_units={len(candidate_units)}, block_length={block_length}, min_train_periods={min_train_periods}"
        )
        print(
            f"[BRB verbose] Residual scale: mean={resid_mean:.4g}, std={resid_std:.4g}, "
            f"min={resid_min:.4g}, max={resid_max:.4g}"
        )

    return np.asarray(oos_residuals, dtype=float)

def block_residual_bootstrap(
    pds: 'PanelDataset',
    model: Any,
    alpha: float = 0.1,
    n_bootstrap: int = 200,
    block_length: Optional[int] = 7,
    random_state: Optional[int] = None,
    center_residuals: bool = True,
    min_train_periods: Optional[int] = 12,
    pool_donor_residuals: bool = False,
    show_progress: bool = False,
    refit_in_bootstrap: bool = False,
    refit_mode: str = "post_only",
    ci_method: str = "percentile",
    bootstrap_type: str = "block",
    variance_calibration_policy: str = "none",
    variance_scale_cap: float = 10.0,
    return_stats: bool = False,
    verbose: bool = False,
    **model_args,
):
    """
    Block residual bootstrap for panel estimators.

    Algorithm
    ---------
    1. Fit the estimator once on the observed panel.
    2. Estimate an out-of-sample pre-treatment residual pool from treated units
       using expanding-window blocks.
    3. Optionally center those residuals.
    4. Sample residuals via block (moving-block) or wild (Rademacher sign) bootstrap.
    5. Form bootstrap effect paths in one of two ways:
       - **Conditional (default)**: Add sampled residual blocks to the observed
         treatment-window effect path.
       - **Refit**: Replace treatment-window treated outcomes with bootstrap
         pseudo data (observed + sampled residuals) and re-fit the estimator
         inside each bootstrap draw; compute effect as y_boot - yhat_boot.
    6. Form pointwise and cumulative confidence bands from bootstrap quantiles.
       Cumulative bands use percentile or BCa; weekly bands use percentile.

    Parameters (additional)
    -----------------------
    ci_method : "percentile" | "bca"
        Cumulative CI method. "percentile" (default) or "bca" (bias-corrected
        accelerated). BCa applies only to cumulative intervals; weekly bands
        remain percentile.
    bootstrap_type : "block" | "wild"
        "block" (default): moving-block bootstrap. "wild": Rademacher sign
        weights (experimental, off by default).
    variance_calibration_policy : "none" | "residual_scaled" | "studentized" | "null_calibrated"
        Optional mean-effect interval calibration. Default "none" preserves
        centered-deviation percentile behavior (TBRRIDGE_BRB_INTERVAL_CORRECTION_001).
    variance_scale_cap : float
        Upper cap for residual-scaled deviation multiplier (default 10).

    Notes
    -----
    - refit_in_bootstrap=False: fast, model-conditional bootstrap that ignores
      estimator-parameter uncertainty.
    - refit_in_bootstrap=True: includes estimator uncertainty but can be much
      slower (one full fit per bootstrap draw).
    - refit_mode="post_only" (default): when refit_in_bootstrap=True, perturbs
      post-period treated outcomes and refits (current behavior).
    - refit_mode="pre_bootstrap": when refit_in_bootstrap=True, bootstraps the
      treated pre-period for model fitting to capture coefficient-estimation
      uncertainty; post-period outcomes remain observed.
    - ci_method="bca": BCa-adjusted cumulative intervals; falls back to
      percentile on numerical failure.
    - bootstrap_type="wild": experimental wild bootstrap; block is default.
    - The residual pool is estimated from blocked out-of-sample pre-period
      forecast errors using expanding windows.
    - pool_donor_residuals=False (default): standard path, treated-unit residuals only.
    - pool_donor_residuals=True: optional experimental mode that adds donor-unit
      forecast errors to the pool for single-treated cases. Use only in targeted
      follow-up runs if needed.
    - The cumulative bands are the primary aggregate uncertainty object;
      the pointwise weekly bands are for visualization.
    """
    if n_bootstrap <= 0:
        raise ValueError("n_bootstrap must be positive")
    if refit_mode not in ("post_only", "pre_bootstrap"):
        raise ValueError(
            f"refit_mode must be 'post_only' or 'pre_bootstrap', got {refit_mode!r}"
        )

    # Filter BRB-only params so they are not passed to estimator __init__
    _brb_only = {
        "refit_mode",
        "refit_in_bootstrap",
        "ci_method",
        "bootstrap_type",
        "variance_calibration_policy",
        "variance_scale_cap",
    }
    model_args = {k: v for k, v in model_args.items() if k not in _brb_only}

    rng = np.random.default_rng(random_state)
    fitted = model(**model_args)
    fitted.run_analysis(pds)

    y = _ensure_time_by_unit(np.asarray(fitted.results['y'], dtype=float), pds.num_timepoints)
    y_hat = _ensure_time_by_unit(np.asarray(fitted.results['y_hat'], dtype=float), pds.num_timepoints)
    effect = y - y_hat

    start = pds.treated_start_idxs[0]
    treated_len = pds.num_treated_time_periods[0]
    end = start + treated_len
    n_units = effect.shape[1]
    bootstrap_n_series = n_units

    prov_block = block_length if block_length is not None else max(2, int(round(max(1, start) ** (1.0 / 3.0))))
    min_train_periods_used = min_train_periods if min_train_periods is not None else max(prov_block, 5)

    pre_residuals = _collect_oos_pre_residuals(
        pds,
        model,
        block_length=prov_block,
        center_residuals=center_residuals,
        min_train_periods=min_train_periods_used,
        pool_donor_residuals=pool_donor_residuals,
        show_progress=show_progress,
        verbose=verbose,
        **model_args,
    )
    if pre_residuals.ndim == 1:
        pre_residuals = pre_residuals.reshape(-1, 1)

    bootstrap_n_series = pre_residuals.shape[1]

    n_pre = max(1, pre_residuals.shape[0])
    if block_length is None:
        # Moving-block bootstrap theory favors block length ~ T^(1/3) for bias/variance tradeoff
        block_length = max(2, int(round(n_pre ** (1.0 / 3.0))))
    # Enforce: block_length >= 2 (preserve time-dependence), block_length <= n_pre
    block_length = max(2, min(int(block_length), n_pre)) if n_pre >= 2 else 1

    treated_effect = np.asarray(effect[start:end], dtype=float)
    if treated_effect.ndim == 1:
        treated_effect = treated_effect.reshape(-1, 1)

    boot_paths = np.full((n_bootstrap, treated_len, n_units), np.nan)
    use_tqdm_boot = show_progress and tqdm is not None
    bootstrap_successful_draws = 0
    bootstrap_failed_draws = 0
    pre_bootstrap_enabled = refit_in_bootstrap and refit_mode == "pre_bootstrap"
    pre_bootstrap_successful_draws = 0
    pre_bootstrap_failed_draws = 0
    pre_bootstrap_length = start if pre_bootstrap_enabled else 0
    if verbose:
        print("[BRB verbose] Starting BRB bootstrap simulation")
    refit_model_args = {k: v for k, v in model_args.items() if k != 'inference'}
    refit_model_args['inference'] = None
    use_wild = bootstrap_type == "wild"
    boot_iterator = tqdm(range(n_bootstrap), desc="BRB bootstrap draws") if use_tqdm_boot else range(n_bootstrap)
    fitted_pre_treated = np.asarray(y_hat[:start], dtype=float)
    if fitted_pre_treated.ndim == 1:
        fitted_pre_treated = fitted_pre_treated.reshape(-1, 1)
    for b in boot_iterator:
        if use_wild:
            sampled = _sample_wild_bootstrap(pre_residuals, treated_len, rng)
        else:
            sampled = _sample_moving_blocks(pre_residuals, treated_len, block_length, rng)
        if sampled.shape[1] == n_units:
            sampled_for_treated = sampled
        elif n_units == 1 and sampled.shape[1] >= 1:
            sampled_for_treated = np.nanmean(sampled, axis=1, keepdims=True)
        else:
            raise ValueError(
                f"BRB sampled residual dimension mismatch: sampled shape={sampled.shape}, treated_effect shape={treated_effect.shape}"
            )
        draw_failed = False
        if refit_in_bootstrap:
            if refit_mode == "pre_bootstrap":
                # Sample pre-period residual blocks for coefficient-uncertainty mode
                if use_wild:
                    sampled_pre = _sample_wild_bootstrap(pre_residuals, start, rng)
                else:
                    sampled_pre = _sample_moving_blocks(pre_residuals, start, block_length, rng)
                if sampled_pre.shape[1] == n_units:
                    sampled_pre_for_treated = sampled_pre
                elif n_units == 1 and sampled_pre.shape[1] >= 1:
                    sampled_pre_for_treated = np.nanmean(sampled_pre, axis=1, keepdims=True)
                else:
                    sampled_pre_for_treated = np.nanmean(sampled_pre[:, :n_units], axis=1, keepdims=True)
                pseudo_pre_treated = fitted_pre_treated + sampled_pre_for_treated
                try:
                    pseudo_pds = _replace_treated_preperiod_in_panel(pds, pseudo_pre_treated)
                    boot_model = model(**refit_model_args)
                    boot_model.run_analysis(pseudo_pds)
                    yhat_boot = _ensure_time_by_unit(
                        np.asarray(boot_model.results['y_hat'], dtype=float),
                        pseudo_pds.num_timepoints,
                    )
                    # Effect = observed post minus predicted counterfactual
                    y_obs_post = np.asarray(y[start:end], dtype=float)
                    if y_obs_post.ndim == 1:
                        y_obs_post = y_obs_post.reshape(-1, 1)
                    boot_effect = y_obs_post - yhat_boot[start:end]
                    if boot_effect.ndim == 1:
                        boot_effect = boot_effect.reshape(-1, 1)
                    if not np.all(np.isfinite(boot_effect)):
                        draw_failed = True
                        boot_paths[b] = treated_effect + sampled_for_treated
                        pre_bootstrap_failed_draws += 1
                    else:
                        cum = np.nansum(boot_effect)
                        if not np.isfinite(cum):
                            draw_failed = True
                            boot_paths[b] = treated_effect + sampled_for_treated
                            pre_bootstrap_failed_draws += 1
                        else:
                            boot_paths[b] = boot_effect
                            pre_bootstrap_successful_draws += 1
                except (AttributeError, TypeError, ValueError):
                    draw_failed = True
                    boot_paths[b] = treated_effect + sampled_for_treated
                    pre_bootstrap_failed_draws += 1
            else:
                # post_only: current behavior
                pseudo_treated = np.asarray(y[start:end], dtype=float) + sampled_for_treated
                if pseudo_treated.ndim == 1:
                    pseudo_treated = pseudo_treated.reshape(-1, 1)
                try:
                    pseudo_pds = _replace_treated_outcomes_in_panel(pds, pseudo_treated)
                    boot_model = model(**refit_model_args)
                    boot_model.run_analysis(pseudo_pds)
                    y_boot = _ensure_time_by_unit(np.asarray(boot_model.results['y'], dtype=float), pseudo_pds.num_timepoints)
                    yhat_boot = _ensure_time_by_unit(np.asarray(boot_model.results['y_hat'], dtype=float), pseudo_pds.num_timepoints)
                    boot_effect = np.asarray(y_boot[start:end] - yhat_boot[start:end], dtype=float)
                    if boot_effect.ndim == 1:
                        boot_effect = boot_effect.reshape(-1, 1)
                    if not np.all(np.isfinite(boot_effect)):
                        draw_failed = True
                        boot_paths[b] = treated_effect + sampled_for_treated
                    else:
                        cum = np.nansum(boot_effect)
                        if not np.isfinite(cum):
                            draw_failed = True
                            boot_paths[b] = treated_effect + sampled_for_treated
                        else:
                            boot_paths[b] = boot_effect
                except (AttributeError, TypeError, ValueError):
                    draw_failed = True
                    boot_paths[b] = treated_effect + sampled_for_treated
        else:
            boot_paths[b] = treated_effect + sampled_for_treated
            if not np.all(np.isfinite(boot_paths[b])):
                draw_failed = True
            else:
                cum = np.nansum(boot_paths[b])
                if not np.isfinite(cum):
                    draw_failed = True
        if draw_failed:
            bootstrap_failed_draws += 1
        else:
            bootstrap_successful_draws += 1

    if verbose:
        print(
            f"[BRB verbose] Bootstrap paths: shape={boot_paths.shape}, "
            f"treatment_window_len={treated_len}, n_units={n_units}, bootstrap_n_series={bootstrap_n_series}"
        )

    # Mean post-window effect estimand (matches TBRRidge / recovery path-period readout).
    plugin_mean_effect = float(np.nanmean(treated_effect))
    boot_mean_replicates = np.nanmean(boot_paths, axis=(1, 2))
    residual_pool_std = _residual_pool_per_period_std(pre_residuals)
    mean_ci_lower, mean_ci_upper, bootstrap_center_mean, variance_scale_factor = (
        _mean_effect_bootstrap_interval(
            boot_mean_replicates,
            plugin_mean_effect,
            alpha,
            variance_calibration_policy=variance_calibration_policy,
            residual_pool_std=residual_pool_std,
            post_window_len=treated_len,
            variance_scale_cap=variance_scale_cap,
        )
    )
    boot_mean_replicate_std = (
        float(np.std(boot_mean_replicates[np.isfinite(boot_mean_replicates)], ddof=1))
        if np.sum(np.isfinite(boot_mean_replicates)) > 1
        else float("nan")
    )
    empirical_mean_se = (
        float(np.nanstd(treated_effect, ddof=1) / np.sqrt(treated_len))
        if treated_effect.size > 1
        else float("nan")
    )
    calibration_ratio_mean_effect = (
        float(boot_mean_replicate_std / empirical_mean_se)
        if np.isfinite(boot_mean_replicate_std)
        and np.isfinite(empirical_mean_se)
        and empirical_mean_se > 1e-12
        else None
    )
    bootstrap_center_minus_point = (
        float(bootstrap_center_mean - plugin_mean_effect)
        if np.isfinite(bootstrap_center_mean) and np.isfinite(plugin_mean_effect)
        else np.nan
    )

    # Path bounds: constant shift from plug-in path so recovery mean-effect interval
    # equals the centered-deviation CI (see TBRRIDGE_BRB_INTERVAL_CORRECTION_001).
    if np.isfinite(mean_ci_lower) and np.isfinite(mean_ci_upper):
        effect_lo_path = treated_effect - mean_ci_upper
        effect_hi_path = treated_effect - mean_ci_lower
    else:
        effect_lo_path = np.nanquantile(boot_paths, alpha / 2.0, axis=0)
        effect_hi_path = np.nanquantile(boot_paths, 1.0 - alpha / 2.0, axis=0)

    out = np.full((n_units, pds.num_timepoints, 3), np.nan)
    out[:, start:end, 0] = effect_lo_path.T
    out[:, start:end, 1] = treated_effect.T
    out[:, start:end, 2] = effect_hi_path.T

    cumulative_boot = np.nansum(boot_paths, axis=1)
    observed_cumulative = np.nansum(treated_effect, axis=0)
    cumulative_lower = np.nanquantile(cumulative_boot, alpha / 2.0, axis=0)
    cumulative_upper = np.nanquantile(cumulative_boot, 1.0 - alpha / 2.0, axis=0)

    # Bootstrap distribution for cumulative effect (aggregate when n_units > 1)
    cumulative_boot_agg = np.sum(cumulative_boot, axis=1) if n_units > 1 else cumulative_boot[:, 0]
    observed_cumulative_agg = float(np.sum(observed_cumulative)) if n_units > 1 else float(observed_cumulative[0])
    cb_valid = cumulative_boot_agg[np.isfinite(cumulative_boot_agg)]

    # BCa for cumulative bounds when ci_method is bca
    bca_bias_correction = None
    bca_acceleration = None
    bca_fallback_used = False
    if ci_method == "bca" and len(cb_valid) >= 10:
        _low, _upp, _z0, _a, _fallback = _compute_bca_quantiles(
            cumulative_boot_agg, observed_cumulative_agg, alpha
        )
        if not _fallback:
            if n_units > 1:
                cumulative_lower_agg = _low
                cumulative_upper_agg = _upp
            else:
                cumulative_lower = np.array([_low])
                cumulative_upper = np.array([_upp])
            bca_bias_correction = _z0
            bca_acceleration = _a
        else:
            bca_fallback_used = True

    # When n_units > 1, aggregate effects after bootstrap
    if n_units > 1:
        cumulative_lower_agg = float(np.nanquantile(cumulative_boot_agg, alpha / 2.0))
        cumulative_upper_agg = float(np.nanquantile(cumulative_boot_agg, 1.0 - alpha / 2.0))
        if ci_method == "bca" and not bca_fallback_used and len(cb_valid) >= 10:
            cumulative_lower_agg = _low
            cumulative_upper_agg = _upp
        elif ci_method != "bca" or bca_fallback_used:
            pass  # already percentile
        boot_std_agg = float(np.nanstd(cumulative_boot_agg))
        boot_mean_agg = float(np.nanmean(cumulative_boot_agg))
        boot_min_agg = float(np.nanmin(cumulative_boot_agg))
        boot_max_agg = float(np.nanmax(cumulative_boot_agg))
    else:
        if ci_method == "bca" and not bca_fallback_used and len(cb_valid) >= 10:
            cumulative_lower = np.array([_low])
            cumulative_upper = np.array([_upp])
        boot_std_agg = float(np.nanstd(cumulative_boot_agg)) if len(cumulative_boot_agg) > 0 else np.nan

    # Bootstrap distribution diagnostics (from cumulative bootstrap)
    if len(cb_valid) >= 4:
        boot_skew = float(stats.skew(cb_valid))
        boot_kurtosis = float(stats.kurtosis(cb_valid))
        boot_q10 = float(np.nanquantile(cb_valid, 0.10))
        boot_q90 = float(np.nanquantile(cb_valid, 0.90))
    else:
        boot_skew = np.nan
        boot_kurtosis = np.nan
        boot_q10 = np.nan
        boot_q90 = np.nan

    bootstrap_failure_rate = bootstrap_failed_draws / max(1, n_bootstrap)
    bootstrap_failure_warning = bootstrap_failure_rate > 0.10

    # Estimator variance: conditional vs refit std (only one available per run)
    boot_std_scalar = float(np.nanstd(cumulative_boot_agg)) if n_units >= 1 else np.nan
    bootstrap_std_conditional = boot_std_scalar if not refit_in_bootstrap else None
    bootstrap_std_refit = boot_std_scalar if refit_in_bootstrap else None
    estimator_variance_fraction = None

    # Detect CI collapse (overfitting, degenerate pool, or block sampling failure)
    residual_pool_size = pre_residuals.shape[0]
    ci_width = np.asarray(cumulative_upper - cumulative_lower)
    if np.any(ci_width < 1e-6):
        collapse_idx = np.where(ci_width < 1e-6)[0]
        for i in collapse_idx:
            bstd_i = float(np.nanstd(cumulative_boot[:, i])) if cumulative_boot.size > 0 else np.nan
            if verbose:
                print(
                    f"[BRB verbose] WARNING: Bootstrap CI collapsed (unit {i}). "
                    f"boot_cumulative_std={bstd_i:.4g}, residual_pool_size={residual_pool_size}, "
                    f"block_length={block_length}"
                )

    boot_mean = np.nanmean(cumulative_boot, axis=0)
    boot_std = np.nanstd(cumulative_boot, axis=0)
    boot_min = np.nanmin(cumulative_boot, axis=0)
    boot_max = np.nanmax(cumulative_boot, axis=0)

    # Primary stats: scalars for downstream (aggregate when n_units > 1)
    if n_units > 1:
        brb_stats = {
            'effect_mean_brb': plugin_mean_effect,
            'effect_ci_lower_mean_brb': mean_ci_lower,
            'effect_ci_upper_mean_brb': mean_ci_upper,
            'bootstrap_interval_method': (
                'centered_deviation_percentile_mean_effect'
                if variance_calibration_policy in (None, '', 'none')
                else f'centered_deviation_{variance_calibration_policy}_mean_effect'
            ),
            'bootstrap_replicate_estimand': 'post_window_mean_effect_level',
            'bootstrap_center': bootstrap_center_mean,
            'bootstrap_center_minus_point': bootstrap_center_minus_point,
            'bootstrap_mean_replicate_std': boot_mean_replicate_std,
            'empirical_mean_standard_error': empirical_mean_se,
            'calibration_ratio_mean_effect': calibration_ratio_mean_effect,
            'variance_calibration_policy': variance_calibration_policy,
            'variance_scale_factor': variance_scale_factor,
            'residual_pool_per_period_std': residual_pool_std,
            'bootstrap_replicate_count': int(np.sum(np.isfinite(boot_mean_replicates))),
            'point_estimate': plugin_mean_effect,
            'interval_lower': mean_ci_lower,
            'interval_upper': mean_ci_upper,
            'effect_cumulative_brb': observed_cumulative_agg,
            'effect_ci_lower_cumulative_brb': cumulative_lower_agg,
            'effect_ci_upper_cumulative_brb': cumulative_upper_agg,
            'block_length': block_length,
            'n_bootstrap': n_bootstrap,
            'residual_pool_size': residual_pool_size,
            'min_train_periods': min_train_periods_used,
            'pool_donor_residuals': pool_donor_residuals,
            'bootstrap_n_series': bootstrap_n_series,
            'n_treated_units': n_units,
            'bootstrap_cumulative_mean': boot_mean_agg,
            'bootstrap_cumulative_std': boot_std_agg,
            'bootstrap_cumulative_min': boot_min_agg,
            'bootstrap_cumulative_max': boot_max_agg,
            'bootstrap_effect_path_shape': boot_paths.shape,
            'pre_residual_shape': pre_residuals.shape,
            'effect_cumulative_brb_per_unit': observed_cumulative,
            'effect_ci_lower_cumulative_brb_per_unit': cumulative_lower,
            'effect_ci_upper_cumulative_brb_per_unit': cumulative_upper,
            'refit_in_bootstrap': refit_in_bootstrap,
            'refit_mode': refit_mode,
            'pre_bootstrap_enabled': pre_bootstrap_enabled,
            'pre_bootstrap_length': pre_bootstrap_length,
            'pre_bootstrap_successful_draws': pre_bootstrap_successful_draws,
            'pre_bootstrap_failed_draws': pre_bootstrap_failed_draws,
            'ci_method': ci_method,
            'bootstrap_type': bootstrap_type,
            'bca_bias_correction': bca_bias_correction,
            'bca_acceleration': bca_acceleration,
            'bca_fallback_used': bca_fallback_used,
            'bootstrap_skew': boot_skew,
            'bootstrap_kurtosis': boot_kurtosis,
            'bootstrap_quantile_10': boot_q10,
            'bootstrap_quantile_90': boot_q90,
            'bootstrap_successful_draws': bootstrap_successful_draws,
            'bootstrap_failed_draws': bootstrap_failed_draws,
            'bootstrap_failure_rate': bootstrap_failure_rate,
            'bootstrap_failure_warning': bootstrap_failure_warning,
            'bootstrap_std_conditional': bootstrap_std_conditional,
            'bootstrap_std_refit': bootstrap_std_refit,
            'estimator_variance_fraction': estimator_variance_fraction,
        }
    else:
        boot_std_agg = float(np.nanstd(cumulative_boot_agg))
        brb_stats = {
            'effect_mean_brb': plugin_mean_effect,
            'effect_ci_lower_mean_brb': mean_ci_lower,
            'effect_ci_upper_mean_brb': mean_ci_upper,
            'bootstrap_interval_method': (
                'centered_deviation_percentile_mean_effect'
                if variance_calibration_policy in (None, '', 'none')
                else f'centered_deviation_{variance_calibration_policy}_mean_effect'
            ),
            'bootstrap_replicate_estimand': 'post_window_mean_effect_level',
            'bootstrap_center': bootstrap_center_mean,
            'bootstrap_center_minus_point': bootstrap_center_minus_point,
            'bootstrap_mean_replicate_std': boot_mean_replicate_std,
            'empirical_mean_standard_error': empirical_mean_se,
            'calibration_ratio_mean_effect': calibration_ratio_mean_effect,
            'variance_calibration_policy': variance_calibration_policy,
            'variance_scale_factor': variance_scale_factor,
            'residual_pool_per_period_std': residual_pool_std,
            'bootstrap_replicate_count': int(np.sum(np.isfinite(boot_mean_replicates))),
            'point_estimate': plugin_mean_effect,
            'interval_lower': mean_ci_lower,
            'interval_upper': mean_ci_upper,
            'effect_cumulative_brb': float(observed_cumulative[0]),
            'effect_ci_lower_cumulative_brb': float(cumulative_lower[0]),
            'effect_ci_upper_cumulative_brb': float(cumulative_upper[0]),
            'block_length': block_length,
            'n_bootstrap': n_bootstrap,
            'residual_pool_size': residual_pool_size,
            'min_train_periods': min_train_periods_used,
            'pool_donor_residuals': pool_donor_residuals,
            'bootstrap_n_series': bootstrap_n_series,
            'single_treated_pooling_rule': ('row_mean' if bootstrap_n_series > 1 else 'identity'),
            'bootstrap_cumulative_mean': float(boot_mean[0]),
            'bootstrap_cumulative_std': float(boot_std[0]),
            'bootstrap_cumulative_min': float(boot_min[0]),
            'bootstrap_cumulative_max': float(boot_max[0]),
            'bootstrap_effect_path_shape': boot_paths.shape,
            'pre_residual_shape': pre_residuals.shape,
            'refit_in_bootstrap': refit_in_bootstrap,
            'refit_mode': refit_mode,
            'pre_bootstrap_enabled': pre_bootstrap_enabled,
            'pre_bootstrap_length': pre_bootstrap_length,
            'pre_bootstrap_successful_draws': pre_bootstrap_successful_draws,
            'pre_bootstrap_failed_draws': pre_bootstrap_failed_draws,
            'ci_method': ci_method,
            'bootstrap_type': bootstrap_type,
            'bca_bias_correction': bca_bias_correction,
            'bca_acceleration': bca_acceleration,
            'bca_fallback_used': bca_fallback_used,
            'bootstrap_skew': boot_skew,
            'bootstrap_kurtosis': boot_kurtosis,
            'bootstrap_quantile_10': boot_q10,
            'bootstrap_quantile_90': boot_q90,
            'bootstrap_successful_draws': bootstrap_successful_draws,
            'bootstrap_failed_draws': bootstrap_failed_draws,
            'bootstrap_failure_rate': bootstrap_failure_rate,
            'bootstrap_failure_warning': bootstrap_failure_warning,
            'bootstrap_std_conditional': bootstrap_std_conditional,
            'bootstrap_std_refit': bootstrap_std_refit,
            'estimator_variance_fraction': estimator_variance_fraction,
        }


    if verbose:
        _mean = boot_mean_agg if n_units > 1 else float(boot_mean[0])
        _std = boot_std_agg if n_units > 1 else float(boot_std[0])
        _min = boot_min_agg if n_units > 1 else float(boot_min[0])
        _max = boot_max_agg if n_units > 1 else float(boot_max[0])
        print(
            f"[BRB verbose] block_length={block_length}, min_train_periods={min_train_periods_used}, "
            f"n_units={n_units}, pool_donor_residuals={pool_donor_residuals}, bootstrap_n_series={bootstrap_n_series}, "
            f"refit_in_bootstrap={refit_in_bootstrap}, single_treated_pooling_rule={('row_mean' if (n_units == 1 and bootstrap_n_series > 1) else 'identity')}, "
            f"pre_residual_shape={pre_residuals.shape}, bootstrap_path_shape={boot_paths.shape}, boot_cumulative mean={_mean}, "
            f"std={_std}, min={_min}, max={_max}"
        )

    if return_stats:
        return out, brb_stats
    return out