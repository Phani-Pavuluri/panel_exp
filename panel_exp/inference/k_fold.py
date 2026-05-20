"""

Inference: K-Fold
==================

A T-Test for Synthetic Control 

Implementation of: https://arxiv.org/pdf/1812.10820.pdf
"""

from panel_exp.panel_data import long_df_to_paneldataset, PanelDataset, TimePeriod
import pandas as pd
import numpy as np
from scipy import stats


def debias(model
         , new_pds
         , og_pds
         , debias_flag = True):
    """
    :returns: debiased estimate

    :param model:
        Model used for estimation
    :param new_pds:
        Modified PanelDataset
    :param og_pds 
        Original PanelDataset
    """
    
    # estimate
    est = model()
    est.run_analysis(new_pds)
    treatment_mask = (new_pds.times >= new_pds.treated_start_idxs[0]) & (new_pds.times<= new_pds.treated_end_idxs[0])
    
    bias = (est.results['y'] - est.results['y_hat'])[treatment_mask].mean()
    y_hat = est.model.predict(np.array(og_pds.wide_data.loc[og_pds.control_units, og_pds.treated_periods[0].start:og_pds.treated_periods[0].end].T))
    y_hat = y_hat[:, np.newaxis] if y_hat.ndim == 1 else y_hat
    
    if debias_flag:
        debias = (og_pds.wide_data.loc[og_pds.treated_units, og_pds.treated_periods[0].start:og_pds.treated_periods[0].end].T.values - y_hat) -bias 
    else:
        debias = (og_pds.wide_data.loc[og_pds.treated_units, og_pds.treated_periods[0].start:og_pds.treated_periods[0].end].T.values - y_hat)
    
    return debias
    
def cross_fold(pds
             , k
             , model
             , debias_flag
             , alpha = 0.1):
    """
    :returns: tupel of lower, mean, upper estimates for ATT at time T 

    :param pds: 
        Original PanelDataset
    :param k: 
        number of folds to use in the cross-fold procedure
    :param model: 
        Model to be used for estimation
    :param alpha:
    """
    
    from scipy.stats import t
    
    pre_t = (len(pds.times)-pds.num_treated_time_periods) #.min() # add min
    holdout = int(np.floor(np.min([pre_t / k, pds.num_treated_time_periods])))
    
    pre_t_wide_data = pds.wide_data.iloc[:, :pds.treated_start_idxs[0]]
    
    blocks = np.split(pre_t_wide_data.T.index[-k*holdout:], k)
    
    #att_k = np.empty((pds.num_treated_time_periods[0], k ))
    att_k = np.empty((len(pds.treated_units), pds.num_treated_time_periods[0], k ))
    
    for b in range(len(blocks)):
        new_wide_df = pds.wide_data.loc[:, pds.times[:pds.treated_start_idxs[0]]]
        new_wide_df = new_wide_df.drop(blocks[b], axis=1)
        new_wide_df = pd.concat([new_wide_df, pds.wide_data.loc[:, blocks[b]]], axis=1 )
        new_wide_df.columns = range(len(new_wide_df.columns))
        
        new_pds = PanelDataset(new_wide_df
                    , [TimePeriod(start=len(new_wide_df.columns) - len(blocks[b]), end=None) for tp in range(len(pds.treated_units))]
                    , pds.treated_units)
        
        # att_k[:,b] = debias(model, new_pds, pds)
        d = debias(model, new_pds, pds, debias_flag)
        att_k[:, :, b] = d.T
        
    atts_k = att_k.mean(axis=1)
    att = atts_k.mean(axis=1)
    
    post_t = pds.num_treated_time_periods[0]
    # block_size = min(np.floor(pre_t/k), post_t)

    se_hat = np.sqrt(1+((k*holdout)/post_t))*np.std(atts_k, ddof=1)/np.sqrt(k)

    lower = att - t.ppf(1-alpha/2, k-1)*se_hat
    upper = att + t.ppf(1-alpha/2, k-1)*se_hat
    
    return lower , att, upper 


def kfold(pds
        , model
        , alpha = .1
        , k = 5
        , debias_flag = True
        ) -> pd.DataFrame:
    """
    :param pds:
        Original PanelDataset
    :param k: (int)
        number of folds to use in the cross-fold procedure
    :param model: (panel method)
        Model to be used for estimation
    :param alpha:
        alpha probability 0-1.
    
    :returns:
        Returns pd.DataFrame containing lower, mean, upper estimates for ATT at time T 
    
    """ 

    if not k:
        k = pds.num_timepoints-pds.num_treated_time_periods[0]

    start = pds.treated_start_idxs[0]

    ests = np.zeros((len(pds.treated_units), pds.num_treated_time_periods[0], 3 )) 

    for i in range(pds.num_treated_time_periods[0]):
        og_pds = PanelDataset(pds.wide_data.loc[:, :pds.times[start+i]]
                        ,[TimePeriod(start = pds.times[start] , end=None) for unit in pds.treated_units]
                        ,pds.treated_units)
        
        l, m, up = cross_fold(og_pds, k, model, debias_flag)
        ests[:, :, 0][:,i] = l
        ests[:, :, 1][:,i] = m
        ests[:, :, 2][:,i] = up

    #pre = pd.DataFrame(np.zeros((pds.treated_start_idxs[0], 3)), columns = ['lower', 'mean', 'upper'])
    #post= pd.DataFrame(ests , columns = ['lower', 'mean', 'upper'])

    #return np.concatenate([np.zeros((len(pds.treated_units), pds.num_timepoints-pds.num_treated_time_periods[0]-pds.post_treated_periods, 3 )) , ests], axis=1)
    return  np.concatenate([np.zeros((len(pds.treated_units), pds.num_timepoints-pds.num_treated_time_periods[0]-pds.post_treated_periods, 3 )) # pre-test zeros
                           , ests #k-fold estimates
                           , np.zeros((len(pds.treated_units), pds.post_treated_periods, 3 ))]  #post-test estimates. default to zero]
                           , axis=1)



from typing import Any, List, Tuple, Optional, Union
import pandas as pd
from scipy.stats import t
import multiprocessing as mp
from functools import partial
import hashlib
from pathlib import Path

def panel_timeseries_kfold(
    pds: 'PanelDataset',
    model: Any,
    alpha: float = 0.1,
    k: int = 5,
    debias_flag: bool = True,
    block_scheme: str = "expanding",
    n_jobs: int = 1,
    random_state: Optional[int] = None,
    show_progress: bool = True,
    diagnostics_path: Optional[Union[str, Path]] = None,
) -> np.ndarray:
    """
    Panel time series k-fold cross-validation for causal inference.

    This function performs time series cross-validation by creating placebo treatments
    from pre-treatment periods to estimate treatment effects and their uncertainty.

    Notes
    -----
    This implementation is intended to produce pointwise weekly treatment
    effects for each treatment horizon. For horizon `i`, the cross-fold
    routine uses only the last treated-period effect from the debiased path
    rather than averaging over all treated periods observed so far.

    :param pds:
        Original PanelDataset
    :param model: (panel method)
        Model to be used for estimation
    :param alpha: (float)
        alpha probability 0-1 for confidence intervals
    :param debias_flag: (bool)
        Whether to apply debiasing
    :param block_scheme: (str)
        'expanding' for true expanding CV (earliest to latest), 'rolling' for recent periods only,
        'block_random' for shuffled consecutive blocks
    :param n_jobs: (int)
        Number of parallel jobs for multiprocessing (1 = no parallelization)
    :param random_state: (int or None)
        Random seed for reproducible results
    :param show_progress: (bool)
        Whether to show progress bar for long runs
    :param diagnostics_path: (str, Path, or None)
        If provided, per-fold diagnostics are saved to this CSV path.
        Filename convention: TimeSeriesKFold_{EstimatorName}_fold_diagnostics.csv

    :returns:
        Returns np.ndarray containing lower, mean, upper estimates for ATT at time T
        Format: (n_units, n_timepoints, 3) where 3 = [lower, mean, upper]
        Pre-treatment and post-treatment periods are filled with np.nan
    """
    
    # Input validation
    if k <= 0:
        raise ValueError("k must be positive")
    
    pre_t = pds.num_timepoints - pds.num_treated_time_periods[0]
    if k > pre_t:
        raise ValueError(f"k ({k}) cannot be greater than pre-treatment periods ({pre_t})")
    
    if not k:
        k = pre_t

    start = pds.treated_start_idxs[0]

    # Calculate holdout size for time series
    holdout = int(np.floor(np.min([pre_t / k, pds.num_treated_time_periods[0]])))
    if holdout <= 0:
        raise ValueError("Holdout size must be positive. Try reducing k or increasing pre-treatment periods.")
    
    # Initialize results array: (n_units, n_timepoints, 3) for [lower, mean, upper]
    ests = np.full((len(pds.treated_units), pds.num_treated_time_periods[0], 3), np.nan)
    
    # Create time series blocks from pre-treatment period
    pre_t_wide_data = pds.wide_data.iloc[:, :pds.treated_start_idxs[0]]
    
    # Create blocks based on scheme
    blocks = _create_blocks(pre_t_wide_data, k, holdout, block_scheme, random_state)

    # --- Per-fold diagnostics (computed once, before treatment-horizon loop) -----------
    if diagnostics_path is not None:
        try:
            diag_df = _compute_tsk_fold_diagnostics(pds, model, blocks)
            diag_path = Path(diagnostics_path)
            diag_path.parent.mkdir(parents=True, exist_ok=True)
            diag_df.to_csv(diag_path, index=False)
        except Exception as _diag_exc:
            import warnings as _w
            _w.warn(f"TSKFold fold diagnostics could not be saved: {_diag_exc}")
    # -----------------------------------------------------------------------------------

    # Cache for performance
    cache: dict = {}

    # Progress bar for treatment horizons
    if show_progress:
        try:
            from tqdm import tqdm
            treatment_horizons = tqdm(range(pds.num_treated_time_periods[0]), 
                                    desc="Treatment horizons", 
                                    unit="horizon")
        except ImportError:
            treatment_horizons = range(pds.num_treated_time_periods[0])
    else:
        treatment_horizons = range(pds.num_treated_time_periods[0])
    
    for i in treatment_horizons:
        # Create dataset up to current treatment period
        og_pds = PanelDataset(pds.wide_data.loc[:, :pds.times[start+i]]
                        , [TimePeriod(start=pds.times[start], end=None) for unit in pds.treated_units]
                        , pds.treated_units)
        
        # Run time series k-fold for this time period
        l, m, up = _cross_fold(og_pds, k, model, debias_flag, blocks, holdout, alpha, cache, n_jobs, i, show_progress)
        
        # Store results for this time period
        ests[:, i, 0] = l  # lower bounds
        ests[:, i, 1] = m  # mean estimates
        ests[:, i, 2] = up  # upper bounds

    # Return in same format as original kfold, using np.nan for non-treatment periods
    return np.concatenate([np.full((len(pds.treated_units), pds.num_timepoints-pds.num_treated_time_periods[0]-pds.post_treated_periods, 3), np.nan)  # pre-test nans
                           , ests  # time series k-fold estimates
                           , np.full((len(pds.treated_units), pds.post_treated_periods, 3), np.nan)]  # post-test nans
                           , axis=1)


# Cumulative time-series k-fold cross-validation for causal inference.
def panel_timeseries_kfold_cumulative(
    pds: 'PanelDataset',
    model: Any,
    alpha: float = 0.1,
    k: int = 5,
    debias_flag: bool = True,
    block_scheme: str = "expanding",
    n_jobs: int = 1,
    random_state: Optional[int] = None,
    show_progress: bool = True,
) -> np.ndarray:
    """
    Cumulative time-series k-fold cross-validation for causal inference.

    This function mirrors `panel_timeseries_kfold(...)` but targets the
    cumulative treatment effect up to each treatment horizon. It is intended for
    downstream aggregate reporting where summing pointwise weekly bounds would be
    too conservative.

    Returns
    -------
    np.ndarray
        Array of shape (n_units, n_timepoints, 3) with cumulative
        [lower, mean, upper] effects. Pre-treatment and post-treatment periods
        are filled with np.nan.
    """
    if k <= 0:
        raise ValueError("k must be positive")

    pre_t = pds.num_timepoints - pds.num_treated_time_periods[0]
    if k > pre_t:
        raise ValueError(f"k ({k}) cannot be greater than pre-treatment periods ({pre_t})")

    if not k:
        k = pre_t

    start = pds.treated_start_idxs[0]
    holdout = int(np.floor(np.min([pre_t / k, pds.num_treated_time_periods[0]])))
    if holdout <= 0:
        raise ValueError("Holdout size must be positive. Try reducing k or increasing pre-treatment periods.")

    ests = np.full((len(pds.treated_units), pds.num_treated_time_periods[0], 3), np.nan)
    pre_t_wide_data = pds.wide_data.iloc[:, :pds.treated_start_idxs[0]]
    blocks = _create_blocks(pre_t_wide_data, k, holdout, block_scheme, random_state)
    cache: dict = {}

    if show_progress:
        try:
            from tqdm import tqdm
            treatment_horizons = tqdm(range(pds.num_treated_time_periods[0]), desc="Treatment horizons", unit="horizon")
        except ImportError:
            treatment_horizons = range(pds.num_treated_time_periods[0])
    else:
        treatment_horizons = range(pds.num_treated_time_periods[0])

    for i in treatment_horizons:
        og_pds = PanelDataset(
            pds.wide_data.loc[:, :pds.times[start + i]],
            [TimePeriod(start=pds.times[start], end=None) for _ in pds.treated_units],
            pds.treated_units,
        )

        l, m, up = _cross_fold_cumulative(
            og_pds,
            k,
            model,
            debias_flag,
            blocks,
            holdout,
            alpha,
            cache,
            n_jobs,
            i,
            show_progress,
        )

        ests[:, i, 0] = l
        ests[:, i, 1] = m
        ests[:, i, 2] = up

    return np.concatenate([
        np.full((len(pds.treated_units), pds.num_timepoints - pds.num_treated_time_periods[0] - pds.post_treated_periods, 3), np.nan),
        ests,
        np.full((len(pds.treated_units), pds.post_treated_periods, 3), np.nan)
    ], axis=1)


def _create_blocks(
    pre_t_wide_data: pd.DataFrame, 
    k: int, 
    holdout: int, 
    block_scheme: str, 
    random_state: Optional[int] = None
) -> List[np.ndarray]:
    """
    Create time series blocks based on the specified scheme.
    
    :param pre_t_wide_data: Pre-treatment data
    :param k: Number of folds
    :param holdout: Holdout size
    :param block_scheme: Block creation scheme
    :param random_state: Random seed for reproducibility
    :returns: List of blocks
    """
    # Create local random number generator to avoid affecting global state
    rng = np.random.default_rng(random_state)
    
    all_periods = pre_t_wide_data.T.index
    
    if block_scheme == 'expanding':
        # Use the most recent pre-treatment periods as holdouts so each fold has
        # earlier history available for fitting. Blocks remain ordered from
        # earliest to latest within the selected validation region.
        if len(all_periods) >= k * holdout:
            selected_periods = all_periods[-k*holdout:]
        else:
            selected_periods = all_periods
        blocks = np.array_split(selected_periods, k)
        
    elif block_scheme == 'rolling':
        # Use only the last k*holdout pre-treatment periods
        if len(all_periods) >= k * holdout:
            selected_periods = all_periods[-k*holdout:]
        else:
            selected_periods = all_periods
        blocks = np.array_split(selected_periods, k)
        
    elif block_scheme == 'block_random':
        # Create consecutive blocks first, then shuffle the blocks
        if len(all_periods) >= k * holdout:
            selected_periods = all_periods[-k*holdout:]
        else:
            selected_periods = all_periods
        
        # Create consecutive blocks
        consecutive_blocks = np.array_split(selected_periods, k)
        # Shuffle the blocks (not individual periods) using local RNG
        rng.shuffle(consecutive_blocks)
        blocks = consecutive_blocks
        
    else:
        raise ValueError("block_scheme must be 'expanding', 'rolling', or 'block_random'")
    
    return blocks


def _compute_tsk_fold_diagnostics(
    pds: 'PanelDataset',
    model: Any,
    blocks: List[np.ndarray],
) -> pd.DataFrame:
    """
    Compute per-fold diagnostics for TimeSeriesKFold.

    For each block (fold), fits the fold-specific model on data strictly preceding
    the holdout window (causal split), then evaluates holdout and training residuals.
    Results are returned as a DataFrame; the caller is responsible for saving it.

    Parameters
    ----------
    pds : PanelDataset
        Full dataset (pre-period + test period).
    model : Any
        Estimator class (same as used in panel_timeseries_kfold).
    blocks : list of array-like
        Holdout blocks as returned by _create_blocks.

    Returns
    -------
    pd.DataFrame
        One row per fold with the following columns:
        fold_id, training_start, training_end, holdout_start, holdout_end,
        n_training_periods, n_holdout_periods, sufficient_training_flag,
        holdout_mean_residual, holdout_rmse, training_rmse, rmse_ratio,
        holdout_residual_slope, slope_pvalue, centered_flag, stable_flag,
        rmse_ratio_flag, overall_valid_fold.
    """
    from scipy import stats as _stats
    from scipy.stats import ttest_1samp as _ttest

    _CENTERED_ALPHA = 0.05
    _STABLE_ALPHA   = 0.05
    _RMSE_RATIO_MAX = 3.0
    _MIN_TRAIN      = 20

    all_pre_periods = list(pds.times[:pds.treated_start_idxs[0]])
    rows: List[dict] = []

    for b, raw_block in enumerate(blocks):
        block_periods = list(raw_block)
        if not block_periods:
            continue

        holdout_start_idx = all_pre_periods.index(block_periods[0])
        train_periods = all_pre_periods[:holdout_start_idx]

        row: dict = {
            "fold_id":               b + 1,
            "training_start":        train_periods[0]  if train_periods else None,
            "training_end":          train_periods[-1] if train_periods else None,
            "holdout_start":         block_periods[0],
            "holdout_end":           block_periods[-1],
            "n_training_periods":    len(train_periods),
            "n_holdout_periods":     len(block_periods),
            "sufficient_training_flag": len(train_periods) >= _MIN_TRAIN,
            "holdout_mean_residual": np.nan,
            "holdout_rmse":          np.nan,
            "training_rmse":         np.nan,
            "rmse_ratio":            np.nan,
            "holdout_residual_slope": np.nan,
            "slope_pvalue":          np.nan,
            "centered_flag":         None,
            "stable_flag":           None,
            "rmse_ratio_flag":       None,
            "overall_valid_fold":    None,
        }

        if not train_periods:
            rows.append(row)
            continue

        # Build fold dataset: training periods then holdout block (treated as "treatment")
        new_wide_df = pds.wide_data.loc[:, train_periods]
        new_wide_df = pd.concat(
            [new_wide_df, pds.wide_data.loc[:, block_periods]], axis=1
        )
        new_wide_df.columns = range(len(new_wide_df.columns))
        new_pds = PanelDataset(
            new_wide_df,
            [TimePeriod(start=len(train_periods), end=None) for _ in pds.treated_units],
            pds.treated_units,
        )

        try:
            est = model()
            est.run_analysis(new_pds)

            # y and y_hat may be (n_periods,) aggregate or (n_periods, n_units) per-unit.
            # Compute aggregate residuals in a shape-agnostic way.
            y_raw     = np.asarray(est.results["y"],     dtype=float)
            y_hat_raw = np.asarray(est.results["y_hat"], dtype=float)

            if y_raw.ndim == 2 and y_hat_raw.ndim == 2 and y_raw.shape == y_hat_raw.shape:
                # Both per-unit (e.g. AugSynth): residual per unit then sum over units
                resid_full = (y_raw - y_hat_raw).sum(axis=1)
            elif y_raw.ndim == 2:
                # y is per-unit, y_hat is aggregate (e.g. TBRRidge)
                y_full     = y_raw.sum(axis=1)
                y_hat_full = y_hat_raw.ravel()
                resid_full = y_full - y_hat_full
            else:
                y_full     = y_raw.ravel()
                y_hat_full = y_hat_raw.ravel()
                if len(y_full) != len(y_hat_full) and len(y_hat_full) > 0:
                    n_units = len(y_full) // len(y_hat_full)
                    y_full = y_full.reshape(n_units, len(y_hat_full)).sum(axis=0)
                resid_full = y_full - y_hat_full

            # Holdout residuals (fold "treatment" period)
            ho_mask    = (new_pds.times >= new_pds.treated_start_idxs[0]) & \
                         (new_pds.times <= new_pds.treated_end_idxs[0])
            resid_hold = resid_full[ho_mask]

            # Training residuals
            tr_mask    = new_pds.times < new_pds.treated_start_idxs[0]
            resid_train = resid_full[tr_mask]

            ho_mean   = float(np.mean(resid_hold))
            ho_rmse   = float(np.sqrt(np.mean(resid_hold ** 2)))
            tr_rmse   = float(np.sqrt(np.mean(resid_train ** 2))) if len(resid_train) else np.nan
            rmse_ratio = ho_rmse / tr_rmse if (tr_rmse and tr_rmse > 0) else np.nan

            # Slope test on holdout residuals
            if len(resid_hold) > 2:
                slope, _, _, p_slope, _ = _stats.linregress(
                    np.arange(len(resid_hold)), resid_hold
                )
            else:
                slope, p_slope = np.nan, np.nan

            # Bias (centered) test
            p_mean = float(_ttest(resid_hold, 0).pvalue) if len(resid_hold) > 1 else np.nan

            centered_flag    = bool(p_mean  > _CENTERED_ALPHA) if np.isfinite(p_mean)   else None
            stable_flag      = bool(p_slope > _STABLE_ALPHA)   if np.isfinite(p_slope)  else None
            rmse_ratio_flag  = bool(rmse_ratio < _RMSE_RATIO_MAX) if np.isfinite(rmse_ratio) else None

            all_flags_present = all(f is not None for f in [centered_flag, stable_flag, rmse_ratio_flag])
            overall = (
                bool(row["sufficient_training_flag"] and centered_flag and stable_flag and rmse_ratio_flag)
                if all_flags_present else None
            )

            row.update({
                "holdout_mean_residual":  ho_mean,
                "holdout_rmse":           ho_rmse,
                "training_rmse":          tr_rmse,
                "rmse_ratio":             rmse_ratio,
                "holdout_residual_slope": float(slope) if np.isfinite(slope) else np.nan,
                "slope_pvalue":           p_slope,
                "centered_flag":          centered_flag,
                "stable_flag":            stable_flag,
                "rmse_ratio_flag":        rmse_ratio_flag,
                "overall_valid_fold":     overall,
            })

        except Exception:
            pass  # row retains NaN/None defaults

        rows.append(row)

    return pd.DataFrame(rows)


def _cross_fold(
    pds: 'PanelDataset',
    k: int,
    model: Any,
    debias_flag: bool,
    blocks: List[np.ndarray],
    holdout: int,
    alpha: float = 0.1,
    cache: Optional[dict] = None,
    n_jobs: int = 1,
    treatment_horizon: int = 0,
    show_progress: bool = True
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Panel time series cross-fold validation for a single time period.
    
    The standard error adjustment is adapted from Chernozhukov et al. (2021)
    for the block-CV setting. This is a heuristic adjustment that accounts
    for finite sample bias in cross-validation.
    
    NOTE: This is an adaptation of the Chernozhukov et al. (2021) formula
    for the block-CV setting, not a direct application. The original paper
    focused on sample-splitting/DML, while this applies the adjustment
    to block cross-validation.
    
    :returns: tuple of lower, mean, upper estimates for ATT at time T 
    """
    
    if cache is None:
        cache = {}
    
    # Initialize array to store ATT estimates for each fold
    att_k = np.full((len(pds.treated_units), k), np.nan)
    
    def process_fold(b: int) -> np.ndarray:
        """Process a single fold - can be parallelized."""
        block_hash = hashlib.md5(np.asarray(blocks[b]).tobytes()).hexdigest()[:8]
        cache_key = (b, len(pds.treated_units), pds.treated_start_idxs[0], treatment_horizon, block_hash)

        if cache_key in cache:
            return cache[cache_key]

        block_periods = list(blocks[b])
        all_pre_periods = list(pds.times[:pds.treated_start_idxs[0]])
        if len(block_periods) == 0:
            result = np.full(len(pds.treated_units), np.nan)
            cache[cache_key] = result
            return result

        holdout_start = all_pre_periods.index(block_periods[0])
        train_periods = all_pre_periods[:holdout_start]

        if len(train_periods) == 0:
            result = np.full(len(pds.treated_units), np.nan)
            cache[cache_key] = result
            return result

        new_wide_df = pds.wide_data.loc[:, train_periods]
        new_wide_df = pd.concat([new_wide_df, pds.wide_data.loc[:, block_periods]], axis=1)
        new_wide_df.columns = range(len(new_wide_df.columns))

        new_pds = PanelDataset(
            new_wide_df,
            [TimePeriod(start=len(train_periods), end=None) for _ in range(len(pds.treated_units))],
            pds.treated_units,
        )

        try:
            d = debias(model, new_pds, pds, debias_flag)
        except (AttributeError, TypeError, ValueError):
            result = np.full(len(pds.treated_units), np.nan)
            cache[cache_key] = result
            return result

        d = np.asarray(d, dtype=float)
        if d.ndim == 1:
            result = d[-1:].astype(float)
        else:
            result = d[-1, :].astype(float)

        cache[cache_key] = result
        return result
    
    # Process folds with progress bar
    if n_jobs > 1 and k > 1:
        # Use joblib for safer multiprocessing with complex objects
        try:
            from joblib import Parallel, delayed
            if show_progress:
                try:
                    from tqdm import tqdm
                    # Create progress bar for folds
                    fold_range = tqdm(range(k), desc=f"Folds (horizon {treatment_horizon})", 
                                    unit="fold", leave=False)
                except ImportError:
                    fold_range = range(k)
            else:
                fold_range = range(k)
            
            results = Parallel(n_jobs=n_jobs)(delayed(process_fold)(b) for b in fold_range)
            for b, result in enumerate(results):
                att_k[:, b] = result
        except ImportError:
            # Fallback to sequential if joblib not available
            if show_progress:
                try:
                    from tqdm import tqdm
                    fold_range = tqdm(range(k), desc=f"Folds (horizon {treatment_horizon})", 
                                    unit="fold", leave=False)
                except ImportError:
                    fold_range = range(k)
            else:
                fold_range = range(k)
            
            for b in fold_range:
                att_k[:, b] = process_fold(b)
    else:
        # Sequential processing with progress bar
        if show_progress:
            try:
                from tqdm import tqdm
                fold_range = tqdm(range(k), desc=f"Folds (horizon {treatment_horizon})", 
                                unit="fold", leave=False)
            except ImportError:
                fold_range = range(k)
        else:
            fold_range = range(k)
        
        for b in fold_range:
            att_k[:, b] = process_fold(b)
    
    # Calculate mean ATT across valid folds using the pointwise effect for the
    # current treatment horizon only.
    att = np.nanmean(att_k, axis=1)

    valid_counts = np.sum(np.isfinite(att_k), axis=1)
    min_valid = int(valid_counts.min()) if valid_counts.size > 0 else 0

    if min_valid <= 1:
        lower, upper = att.copy(), att.copy()
        return lower, att, upper

    # Conservative finite-sample adjustment for blocked time-series CV.
    scale = np.sqrt(1 + ((k * holdout) / max(1, pds.num_treated_time_periods[0])))
    se_hat = scale * np.nanstd(att_k, ddof=1, axis=1) / np.sqrt(valid_counts)

    t_val = t.ppf(1 - alpha/2, min_valid - 1)
    lower = att - t_val * se_hat
    upper = att + t_val * se_hat

    return lower, att, upper


# Helper for cumulative effects up to the current horizon
def _cross_fold_cumulative(
    pds: 'PanelDataset',
    k: int,
    model: Any,
    debias_flag: bool,
    blocks: List[np.ndarray],
    holdout: int,
    alpha: float = 0.1,
    cache: Optional[dict] = None,
    n_jobs: int = 1,
    treatment_horizon: int = 0,
    show_progress: bool = True
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Cross-fold helper targeting cumulative effects up to the current horizon."""
    if cache is None:
        cache = {}

    att_k = np.full((len(pds.treated_units), k), np.nan)

    def process_fold(b: int) -> np.ndarray:
        block_hash = hashlib.md5(np.asarray(blocks[b]).tobytes()).hexdigest()[:8]
        cache_key = ("cum", b, len(pds.treated_units), pds.treated_start_idxs[0], treatment_horizon, block_hash)

        if cache_key in cache:
            return cache[cache_key]

        block_periods = list(blocks[b])
        all_pre_periods = list(pds.times[:pds.treated_start_idxs[0]])
        if len(block_periods) == 0:
            result = np.full(len(pds.treated_units), np.nan)
            cache[cache_key] = result
            return result

        holdout_start = all_pre_periods.index(block_periods[0])
        train_periods = all_pre_periods[:holdout_start]

        if len(train_periods) == 0:
            result = np.full(len(pds.treated_units), np.nan)
            cache[cache_key] = result
            return result

        new_wide_df = pds.wide_data.loc[:, train_periods]
        new_wide_df = pd.concat([new_wide_df, pds.wide_data.loc[:, block_periods]], axis=1)
        new_wide_df.columns = range(len(new_wide_df.columns))

        new_pds = PanelDataset(
            new_wide_df,
            [TimePeriod(start=len(train_periods), end=None) for _ in range(len(pds.treated_units))],
            pds.treated_units,
        )

        try:
            d = debias(model, new_pds, pds, debias_flag)
        except (AttributeError, TypeError, ValueError):
            result = np.full(len(pds.treated_units), np.nan)
            cache[cache_key] = result
            return result

        d = np.asarray(d, dtype=float)
        if d.ndim == 1:
            result = np.array([np.nansum(d)], dtype=float)
        else:
            result = np.nansum(d, axis=0).astype(float)

        cache[cache_key] = result
        return result

    if n_jobs > 1 and k > 1:
        try:
            from joblib import Parallel, delayed
            if show_progress:
                try:
                    from tqdm import tqdm
                    fold_range = tqdm(range(k), desc=f"Folds (horizon {treatment_horizon})", unit="fold", leave=False)
                except ImportError:
                    fold_range = range(k)
            else:
                fold_range = range(k)

            results = Parallel(n_jobs=n_jobs)(delayed(process_fold)(b) for b in fold_range)
            for b, result in enumerate(results):
                att_k[:, b] = result
        except ImportError:
            if show_progress:
                try:
                    from tqdm import tqdm
                    fold_range = tqdm(range(k), desc=f"Folds (horizon {treatment_horizon})", unit="fold", leave=False)
                except ImportError:
                    fold_range = range(k)
            else:
                fold_range = range(k)

            for b in fold_range:
                att_k[:, b] = process_fold(b)
    else:
        if show_progress:
            try:
                from tqdm import tqdm
                fold_range = tqdm(range(k), desc=f"Folds (horizon {treatment_horizon})", unit="fold", leave=False)
            except ImportError:
                fold_range = range(k)
        else:
            fold_range = range(k)

        for b in fold_range:
            att_k[:, b] = process_fold(b)

    att = np.nanmean(att_k, axis=1)
    valid_counts = np.sum(np.isfinite(att_k), axis=1)
    min_valid = int(valid_counts.min()) if valid_counts.size > 0 else 0

    if min_valid <= 1:
        lower, upper = att.copy(), att.copy()
        return lower, att, upper

    scale = np.sqrt(1 + ((k * holdout) / max(1, pds.num_treated_time_periods[0])))
    se_hat = scale * np.nanstd(att_k, ddof=1, axis=1) / np.sqrt(valid_counts)

    t_val = t.ppf(1 - alpha/2, min_valid - 1)
    lower = att - t_val * se_hat
    upper = att + t_val * se_hat
    return lower, att, upper