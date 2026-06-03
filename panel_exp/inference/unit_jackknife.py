from typing import Callable, Dict, Optional

# from ...panel_data import PanelDataset
from panel_exp.panel_data import PanelDataset, TimePeriod

import numpy as np
import scipy.stats


def unit_jk(
    panel: PanelDataset,
    estimator: Callable,
    variation: int = 1,
    alpha: Optional[float] = None,
    **estimator_kwargs
) -> list:
    """updating this to fit ABC of impact.py. Also, taking sqrt of JK variance
    variation 1 comes from https://www.aeaweb.org/articles?id=10.1257/aer.20190159
    variation 2 comes from https://arxiv.org/pdf/1905.02928.pdf

    Args:
        panel (PanelDataset): panel dataset
        estimator (Callable): estimator class
        variation (int, optional): variation of JK. Defaults to 1, which uses squared differences. 2 uses absolute differences.
        alpha (Optional[float], optional): alpha for confidence interval. Defaults to None.
        **estimator_kwargs: kwargs for estimator

    Returns:
        list: list of confidence intervals
    """
    # Full-sample counterfactual anchor (Abadie et al. donor jackknife: compare
    # leave-one-out y_hat to full-fit y_hat, equivalently tau_{-i} - tau on Y - y_hat).
    full_est = estimator(**estimator_kwargs)
    full_est.run_analysis(panel)
    mu = full_est.results["y_hat"]

    if variation == 1:
        squared_diffs = 1.0 * np.zeros_like(mu)
    if variation == 2:
        assert alpha is not None, "Must pass alpha with variation 2"
        residuals = []

    # loop over units, dropping each one and estimating mu to construct uncertainty
    for unit in [unit for unit in panel.units if unit not in panel.treated_units]:
        cur_panel = panel.drop_units(unit)
        est = estimator(**estimator_kwargs)
        est.run_analysis(cur_panel)
        mu_i = est.results["y_hat"]
        if variation == 1:
            squared_diffs += np.square(mu_i * 1.0 - mu * 1.0).astype(float)
        if variation == 2:
            residuals.append(np.abs(mu_i * 1.0 - mu * 1.0))

    # compute JK variance
    if variation == 1:
        JK = ((panel.num_units - 1) / panel.num_units) * squared_diffs

        return scipy.stats.norm.ppf(alpha / 2 + (1 - alpha)) * np.sqrt(JK)

    if variation == 2:
        residuals = np.array(residuals)
        return np.percentile(residuals, 1 - alpha, axis=0)


def _jkp_residual_matrix(
    y: np.ndarray,
    y_hat: np.ndarray,
    start_idx: int,
) -> np.ndarray:
    """Per-unit residuals vs counterfactual on the treated window (TBRRidge: broadcast pooled ``y_hat``)."""
    y_win = np.asarray(y, dtype=float)[start_idx:]
    y_hat_win = np.asarray(y_hat, dtype=float)[start_idx:]
    if y_win.ndim == 2 and y_hat_win.ndim == 1:
        return y_win - y_hat_win[:, np.newaxis]
    return y_win - y_hat_win


def resolve_end_period(time_period):
    """
    Helper function for resolving time index when end is None.
    """
    if time_period.end is None:
        return None
    else:
        return time_period.end + 1


def jkp(
    panel: PanelDataset, estimator: Callable, alpha=0.1, **estimator_kwargs
) -> np.array:
    """
    JackKnife Plus algorithm.

    Args:
        panel (PanelDataset): panel dataset
        estimator (Callable): estimator class
        alpha (float, optional): alpha for confidence interval. Defaults to .1.
        **estimator_kwargs: kwargs for estimator

    Returns:
        np.array: confidence interval
    """
    pre_t_time = panel.treated_start_idxs[0] - 1
    n_treated_units = len(panel.treated_units)
    n_treated_time_periods = (
        panel.treated_end_idxs[0] - panel.treated_start_idxs[0]
    ) + 1

    lower_df = np.zeros((pre_t_time, n_treated_time_periods, n_treated_units))

    upper_df = np.zeros((pre_t_time, n_treated_time_periods, n_treated_units))

    median_df = np.zeros((pre_t_time, n_treated_time_periods, n_treated_units))

    for t_unit in range(pre_t_time):
        # drop t unit from pre-treatment periods
        new_wide_df = panel.wide_data.drop(panel.times[t_unit], axis=1)

        # append to end
        new_wide_df = new_wide_df.assign(
            new_column=panel.wide_data.loc[:, panel.times[t_unit]]
        ).rename(columns={"new_column": panel.times[-1] + 1})

        # new PDS
        new_pds = PanelDataset(
            new_wide_df,
            [
                TimePeriod(start=tp.start, end=resolve_end_period(tp))
                for tp in panel.treated_periods
            ],
            panel.treated_units,
        )
        # fit new model
        model = estimator(**estimator_kwargs)
        model.run_analysis(new_pds)

        residuals = _jkp_residual_matrix(
            model.results["y"],
            model.results["y_hat"],
            new_pds.treated_start_idxs[0],
        )
        error = np.abs(residuals[-1])

        upper = (residuals[:-1] + error).reshape(
            n_treated_time_periods, n_treated_units
        )
        lower = (residuals[:-1] - error).reshape(
            n_treated_time_periods, n_treated_units
        )

        lower_df[t_unit] += lower
        upper_df[t_unit] += upper
        median_df[t_unit] += residuals[:-1].reshape(
            n_treated_time_periods, n_treated_units
        )

    if n_treated_units == 1:
        return (
            np.percentile(lower_df, alpha * 100, axis=0).flatten(),
            np.percentile(upper_df, alpha * 100, axis=0).flatten(),
            np.percentile(median_df, 50, axis=0).flatten(),
        )
    else:
        return (
            np.percentile(lower_df, alpha * 100, axis=0),
            np.percentile(upper_df, alpha * 100, axis=0),
            np.percentile(median_df, 50, axis=0),
        )


def unit_jackknife(
    panel: PanelDataset, estimator: Callable, **estimator_kwargs
) -> Dict:
    """
    Implements the unit-jackknife as detailed in Synthetic Diff-in-Diff(https://www.aeaweb.org/articles?id=10.1257/aer.20190159)
    Procedure is as follows:

        For each unit i = 1, ..., N in the control group:
            1. Estimate the missing potential outcome for the treated unit
            in each post treatment time period withotu using unit `i` to estimate
            2. Compute the estimand as $\tau_{-i} = Y_{j} - \hat{\mu}_{-i}$ where
            Y_{j} is the observe outcome for treated unit $j$ and $\hat{\mu}_{-i}$
            is the estimate of the missing potential outcome for unit $j$ with
            estimation excluding unit $i$.

        Compute the jackknife variance for each post-treatment time T > T_0 as:
            $V_jack = (N - 1)/N * \sum_{i=1}^N (\tau_{-i} - \tau)^2$

        Where $tau$ and $tau_{-i}$ are the original and jackknife estimate, respectiviely
    """
    # first take the estimate for
    full_estimate = estimator(panel, **estimator_kwargs)
    mu = full_estimate["Y_0"]
    squared_diffs = np.zeros_like(mu)
    # now iterate, dropping units
    for unit in panel.units:
        cur_panel = panel.drop_units(unit)
        mu_i = estimator(cur_panel, **estimator_kwargs)
        # We can ignore Y since we have
        # (Y - mu) - (Y - \hat{mu}) = (Y - Y) + (\hat{mu} - mu)
        squared_diffs += np.square(mu_i - mu)
    V_jack = ((panel.num_units - 1) / panel.num_units) * squared_diffs

    return V_jack


def time_jackknife_plus(
    panel: PanelDataset, estimator: Callable, alpha=0.05, **estimator_kwargs
) -> Dict:
    """
    For each 1 in 1, ..., T_0:
        1. Estimate $\hat{\mu}_{-t, j, T}$, i.e., the panel data prediction for treated
        unit $j$ for each post-treatment time period $T > T_0$ _without_ the pre-treatment
        time $t < T_0$ in the training sample.
        2. Estimate $\hat{\mu}_{-t,j,t}, i.e., the panel data prediction for treated
        unit $j$ at time period $t < T_0$ _without_ $t$ in the training sample, and
        then compute the absolute residual: $\hat{R}_{-t} = |Y_{j,t} - \hat{\mu}}_{-t,j,t}|

    For the normal quantile, $\alpha$, compute for each of the post-treatment periods
    $T > T_0$:
        1. The lower CI bound: q_{\frac{\alpha}{2}}\left(\hat{\mu}_{-t,j,T} - \hat{R}_{-t}\right)
        2. The upper CI bound: q_{1 - \frac{\alpha}{2}}\left(\hat{\mu}_{-t,j,T} - \hat{R}_{-t}\right)
    """
    original_estimate = estimator(panel, **estimator_kwargs)
    num_pre = original_estimate["Y_0_pre"].shape[0]
    num_post = original_estimate["Y_0"].shape - num_pre
    post_mu_estimates = np.zeros((num_pre, num_post))
    R_estimates = np.zeros(num_pre)
    for time_idx, time_point in enumerate(panel.times):
        df = panel.wide_data
        time_col = df.loc[time_point]
        df = df.drop(time_col).insert(panel.num_timepoints - 1, time_point, time_col)
        cur_panel = PanelDataset(
            wide_data=df,
            treated_periods=panel.treated_periods,
            treated_units=panel.treated_units,
            covariates=panel.treated_covariates,
            populations=panel.populations,
        )
        estimate = estimator(cur_panel, **estimator_kwargs)
        # subset to the post-treatment period
        post_mu_estimates[time_idx, :] = estimate["Y_0"][num_pre:-1]
        R_estimates[time_idx] = estimate["Y_1"][-1] - estimate["Y_0"][-1]

    vals = post_mu_estimates - R_estimates[:, None]
    normal_means = vals.mean(1)
    normal_scale = vals.std(1)
    high = scipy.stats.norm.ppf(1 - alpha)
    low = scipy.stats.norm.ppf(alpha)
    return {
        "high": high * normal_scale + normal_means,
        "low": low * normal_scale + normal_means,
    }
