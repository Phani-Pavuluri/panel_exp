"""
Methods: SyntheticDID
=====================

Synthetic Difference-in-Differences (Arkhangelsky et al. 2021)

Combines synthetic control weighting with DID-style differencing.
Estimates unit weights (omega) and time weights (lambda) via alternating
optimization, then computes ATT as a weighted DID contrast.

Scale conventions:
- Internal estimation uses treated MEAN path (moved closer to canonical SDID).
- Exported results (y, y_hat, treatment_effects, y_lower, y_upper) remain
  AGGREGATE scale for backward compatibility with geo-experiment reporting.
- per_geo_effect = tau_mean (ATT on mean scale)
- aggregate_effect = tau_mean * N_tr
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from panel_exp.panel_data import PanelDataset
from panel_exp.impact import ImpactAnalyzer


def _compute_noise_level(Y_control_pre: np.ndarray) -> float:
    """Estimate noise from first differences of pre-treatment control data."""
    if Y_control_pre.shape[1] < 2:
        return 1.0
    diffs = np.diff(Y_control_pre, axis=1)
    return float(np.std(diffs) + 1e-10)


def _project_to_simplex(x: np.ndarray) -> np.ndarray:
    """
    Euclidean projection onto the simplex {w : w >= 0, sum(w) = 1}.
    Uses the standard sort-and-threshold algorithm (Duchi et al.).
    """
    x = np.asarray(x, dtype=float).ravel()
    n = len(x)
    if n == 0:
        return x
    u = np.sort(x)[::-1]
    cssv = np.cumsum(u)
    cand = np.nonzero(u * np.arange(1, n + 1) > (cssv - 1))[0]
    rho = int(cand[-1]) if len(cand) > 0 else 0
    theta = (cssv[rho] - 1) / (rho + 1)
    w = np.maximum(x - theta, 0)
    s = w.sum()
    return w / s if s > 0 else np.ones(n) / n


def _fit_omega(
    Y_treat_pre: np.ndarray,
    Y_control_pre: np.ndarray,
    lam: np.ndarray,
    zeta_omega: float,
) -> np.ndarray:
    """
    Fit omega on pre-period centered (demeaned) data with given lambda.
    Demeaning ensures omega matches trends, not baseline levels.
    """
    _N0 = Y_control_pre.shape[0]
    _T0 = Y_control_pre.shape[1]
    y_pre = Y_treat_pre.ravel()

    y_mean = np.mean(y_pre)
    y_std = np.std(y_pre) + 1e-10
    y_c = (y_pre - y_mean) / y_std

    X_mean = np.mean(Y_control_pre, axis=1, keepdims=True)
    X_std = np.std(Y_control_pre, axis=1, keepdims=True) + 1e-10
    X_c = (Y_control_pre - X_mean) / X_std

    X = X_c.T  # (T0, N0)
    W = np.diag(lam)
    A = X.T @ W @ X + zeta_omega * np.eye(N0)
    b = X.T @ W @ y_c
    omega_unconstrained = np.linalg.solve(A, b)
    return _project_to_simplex(omega_unconstrained)


def _fit_lambda(
    Y_treat_pre: np.ndarray,
    Y_control_pre: np.ndarray,
    omega: np.ndarray,
    zeta_lambda: float,
    max_iter: int = 50,
    tol: float = 1e-8,
) -> np.ndarray:
    """
    Fit time weights lambda from control matrices.
    Construct time weights from inverse residual magnitude with simplex projection.
    """
    _T0 = Y_control_pre.shape[1]
    y_pre = Y_treat_pre.ravel()
    y_mean = np.mean(y_pre)
    y_c = y_pre - y_mean
    X_mean = np.mean(Y_control_pre, axis=1, keepdims=True)
    X_c = Y_control_pre - X_mean
    X = X_c.T  # (T0, N0)
    residuals = y_c - X @ omega
    r_sq = np.maximum(residuals ** 2 + zeta_lambda, 1e-12)
    lam = (1.0 / r_sq) / (1.0 / r_sq).sum()
    return _project_to_simplex(lam)


def _fit_omega_lambda_alternating(
    Y_treat_pre: np.ndarray,
    Y_control_pre: np.ndarray,
    zeta_omega: float,
    zeta_lambda: float,
    use_uniform_lambda: bool,
    max_iter: int = 100,
    tol: float = 1e-8,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Alternating updates for omega and lambda.
    If use_uniform_lambda=True, lambda stays uniform.
    """
    N0 = Y_control_pre.shape[0]
    T0 = Y_control_pre.shape[1]
    omega = np.ones(N0) / N0
    lam = np.ones(T0) / T0

    for _ in range(max_iter):
        omega_old = omega.copy()
        lam_old = lam.copy()
        omega = _fit_omega(Y_treat_pre, Y_control_pre, lam, zeta_omega)
        if not use_uniform_lambda:
            lam = _fit_lambda(Y_treat_pre, Y_control_pre, omega, zeta_lambda)
        else:
            lam = np.ones(T0) / T0
        if np.max(np.abs(omega - omega_old)) < tol and np.max(np.abs(lam - lam_old)) < tol:
            break
    return omega, lam


def _fit_omega_centered_uniform_lambda(
    Y_treat_pre: np.ndarray,
    Y_control_pre: np.ndarray,
    zeta_omega: float,
) -> np.ndarray:
    """
    Fit omega on pre-period centered data with uniform lambda.
    DEPRECATED: use _fit_omega_lambda_alternating with use_uniform_lambda=True.
    """
    lam = np.ones(Y_control_pre.shape[1]) / Y_control_pre.shape[1]
    return _fit_omega(Y_treat_pre, Y_control_pre, lam, zeta_omega)


class SyntheticDID(ImpactAnalyzer):
    """
    Synthetic Difference-in-Differences (Arkhangelsky et al. 2021).

    Combines synthetic control with DID: estimates unit weights (omega) and
    time weights (lambda) on pre-period data, then computes ATT as a weighted
    DID contrast.

    Internal estimation uses treated MEAN path (moved closer to canonical SDID). Exported
    results remain aggregate-scale for backward compatibility.

    Parameters
    ----------
    alpha : float, default=0.1
        Significance level for inference.
    n_bootstrap : int, default=100
        Number of bootstrap/placebo replications.
    eta_omega : float or None
        Regularization for omega. Default: (N_tr * T_post)^(1/4).
    eta_lambda : float
        Regularization for lambda (legacy). Prefer zeta_lambda.
    zeta_omega : float or None
        Regularization for omega. If None, computed as eta_omega * noise_level.
    zeta_lambda : float or None
        Regularization for lambda. If None, computed as eta_lambda * noise_level.
    use_uniform_lambda : bool, default=False
        If True, use uniform lambda (1/T0). Otherwise estimate lambda.
    variance_method : str, default="time_block_bootstrap"
        "time_block_bootstrap" or "placebo".
    """

    def __init__(
        self,
        inference: Optional[object] = None,
        alpha: float = 0.1,
        n_bootstrap: int = 100,
        eta_omega: Optional[float] = None,
        eta_lambda: float = 1e-6,
        zeta_omega: Optional[float] = None,
        zeta_lambda: Optional[float] = None,
        use_uniform_lambda: bool = False,
        variance_method: str = "time_block_bootstrap",
    ):
        self.inference = inference
        self.alpha = alpha
        self.n_bootstrap = n_bootstrap
        self.eta_omega = eta_omega
        self.eta_lambda = eta_lambda
        self.zeta_omega = zeta_omega
        self.zeta_lambda = zeta_lambda
        self.use_uniform_lambda = use_uniform_lambda
        if variance_method not in ("time_block_bootstrap", "placebo"):
            raise ValueError(
                f"variance_method must be 'time_block_bootstrap' or 'placebo', got '{variance_method}'"
            )
        self.variance_method = variance_method
        self.z_critical = stats.norm.ppf(1 - alpha / 2)
        self.bootstrap_block_size = 5
        self.bootstrap_seed = 42

    def fit_data(self, panel: PanelDataset) -> None:
        """Extract panel data and validate structure."""
        self.panel_data = panel
        self._validate_panel(panel)

    def _validate_panel(self, panel: PanelDataset) -> None:
        """Validate panel structure for SDID."""
        assert len(set(panel.treated_start_idxs)) == 1, "Must be Simultaneous Adoption"
        assert len(set(panel.treated_end_idxs)) == 1, "Must be Simultaneous End"

        wide = panel.wide_data.values
        n_units, n_times = wide.shape
        T0 = panel.treated_start_idxs[0]
        T1 = panel.treated_end_idxs[0] + 1
        post_len = T1 - T0

        if T0 <= 0:
            raise ValueError("SyntheticDID requires at least one pre-treatment period.")
        if post_len <= 0:
            raise ValueError("SyntheticDID requires at least one post-treatment period.")

        control_idx = [i for i in range(n_units) if panel.wide_data.index[i] not in panel.treated_units]
        N0 = len(control_idx)
        N_tr = n_units - N0

        if N0 < 2:
            raise ValueError(
                "SyntheticDID requires at least 2 control units for synthetic weighting."
            )

        if self.variance_method == "placebo" and N0 < N_tr + 2:
            raise ValueError(
                f"Placebo inference requires at least N_tr+2 control units. "
                f"Got N_control={N0}, N_treated={N_tr}. Need at least {N_tr + 2} controls."
            )

        if np.any(np.isnan(wide)):
            raise ValueError("SyntheticDID does not support missing values in the estimation window.")

    def fit_model(self) -> None:
        """Estimate omega and lambda weights, and compute ATT on mean scale."""
        panel = self.panel_data
        wide = panel.wide_data.values
        n_units, n_times = wide.shape
        T0 = panel.treated_start_idxs[0]
        T1 = panel.treated_end_idxs[0] + 1
        post_len = T1 - T0

        control_idx = [i for i in range(n_units) if panel.wide_data.index[i] not in panel.treated_units]
        treat_idx = [i for i in range(n_units) if panel.wide_data.index[i] in panel.treated_units]
        _N0 = len(control_idx)
        N_tr = len(treat_idx)

        Y_control = wide[control_idx, :]
        Y_treat = wide[treat_idx, :]
        # MEAN scale for treated-mean SDID (not sum)
        Y_treat_mean = np.mean(Y_treat, axis=0)

        Y_control_pre = Y_control[:, :T0]
        Y_treat_pre = Y_treat_mean[:T0].reshape(1, -1)
        Y_control_post = Y_control[:, T0:T1]
        Y_treat_post = Y_treat_mean[T0:T1]

        noise_level = _compute_noise_level(Y_control_pre)
        self.noise_level = noise_level

        eta_omega = self.eta_omega
        if eta_omega is None:
            eta_omega = (N_tr * post_len) ** 0.25
        zeta_omega = self.zeta_omega
        if zeta_omega is None:
            zeta_omega = eta_omega * noise_level
        self.zeta_omega_ = zeta_omega

        eta_lambda = self.eta_lambda
        zeta_lambda = self.zeta_lambda
        if zeta_lambda is None:
            zeta_lambda = eta_lambda * noise_level
        self.zeta_lambda_ = zeta_lambda

        omega, lam = _fit_omega_lambda_alternating(
            Y_treat_pre,
            Y_control_pre,
            zeta_omega=zeta_omega,
            zeta_lambda=zeta_lambda,
            use_uniform_lambda=self.use_uniform_lambda,
        )

        y_mean = float(np.mean(Y_treat_pre))
        x_mean = np.mean(Y_control_pre, axis=1)
        alpha = y_mean - float(omega @ x_mean)

        self.omega = omega
        self.lam = lam
        self._alpha = alpha

        Y_syn_pre = alpha + omega @ Y_control_pre
        Y_syn_post = alpha + omega @ Y_control_post

        treat_pre_weighted = float(lam @ Y_treat_pre.ravel())
        syn_pre_weighted = float(lam @ Y_syn_pre)
        pre_gap_adjustment = treat_pre_weighted - syn_pre_weighted

        treat_post_avg = float(np.mean(Y_treat_post))
        syn_post_avg = float(np.mean(Y_syn_post))

        tau_mean = (treat_post_avg - syn_post_avg) - pre_gap_adjustment

        self.treatment_effect = tau_mean
        self.per_geo_effect = tau_mean
        self.aggregate_effect = tau_mean * N_tr
        self.n_treated_units = N_tr
        self._pre_gap_adjustment = pre_gap_adjustment

        Y_syn_full_mean = alpha + omega @ Y_control
        self._Y_syn_full_mean = Y_syn_full_mean
        self._Y_treat_mean = Y_treat_mean
        self._Y_control = Y_control
        self._Y_treat = Y_treat
        self._T0 = T0
        self._T1 = T1
        self._omega = omega
        self._lam = lam

        pre_treat = Y_treat_pre.ravel()
        pre_syn = Y_syn_pre
        pre_resid = np.abs(pre_treat - pre_syn)
        top5_by_fit = np.argsort(pre_resid)[: min(5, T0)].tolist()
        pre_rmse = float(np.sqrt(np.mean((pre_treat - pre_syn) ** 2)))
        eff_n_omega = float(1.0 / (np.sum(omega ** 2) + 1e-12))
        eff_n_lambda = float(1.0 / (np.sum(lam ** 2) + 1e-12))
        omega_top = np.argsort(omega)[::-1][:5]
        lambda_top = np.argsort(lam)[::-1][:5]

        self.sdid_diagnostics = {
            "top_5_best_fit_pre_weeks": top5_by_fit,
            "pre_rmse": pre_rmse,
            "pre_rmse_mean_scale": pre_rmse,
            "pre_rmse_aggregate_scale": pre_rmse * N_tr,
            "pre_mean_gap": float(np.mean(pre_treat) - np.mean(pre_syn)),
            "post_mean_gap": float(treat_post_avg - syn_post_avg),
            "eff_n_omega": eff_n_omega,
            "eff_n_lambda": eff_n_lambda,
            "omega_top_k": [(int(i), float(omega[i])) for i in omega_top],
            "lambda_top_k": [(int(i), float(lam[i])) for i in lambda_top],
            "noise_level": noise_level,
            "zeta_omega": zeta_omega,
            "zeta_lambda": zeta_lambda,
            "inference_method": self.variance_method,
        }

        if self.variance_method == "time_block_bootstrap":
            se, ci_lower, ci_upper, pvalue, bootstrap_effects = self._time_block_bootstrap_se_ci(
                Y_control,
                Y_treat_mean,
                T0,
                T1,
            )
        else:
            se, ci_lower, ci_upper, pvalue, bootstrap_effects = self._placebo_variance_se_ci(
                Y_control,
                Y_treat,
                T0,
                T1,
            )

        self.treatment_se = se
        self.treatment_ci = (ci_lower, ci_upper)
        self.treatment_pvalue = pvalue
        self.bootstrap_effects_ = bootstrap_effects

    def _compute_att_from_matrices(
        self,
        Y_control_pre: np.ndarray,
        Y_control_post: np.ndarray,
        Y_treat_pre: np.ndarray,
        Y_treat_post: np.ndarray,
        use_uniform_lambda: Optional[bool] = None,
    ) -> float:
        """Refit SDID on supplied matrices (mean-scale) and return one post-period ATT."""
        if Y_control_pre.shape[1] <= 0 or Y_control_post.shape[1] <= 0:
            raise ValueError("Bootstrap resample must contain at least one pre and one post period.")
        n_post = Y_control_post.shape[1]
        noise_level = _compute_noise_level(Y_control_pre)
        eta_omega = self.eta_omega
        if eta_omega is None:
            eta_omega = max((1 * max(n_post, 1)) ** 0.25, 1.0)
        zeta_omega = self.zeta_omega_ if hasattr(self, "zeta_omega_") else eta_omega * noise_level
        zeta_lambda = self.zeta_lambda_ if hasattr(self, "zeta_lambda_") else self.eta_lambda * noise_level
        use_ul = self.use_uniform_lambda if use_uniform_lambda is None else use_uniform_lambda

        omega_b, lam_b = _fit_omega_lambda_alternating(
            Y_treat_pre.reshape(1, -1),
            Y_control_pre,
            zeta_omega=zeta_omega,
            zeta_lambda=zeta_lambda,
            use_uniform_lambda=use_ul,
        )
        alpha_b = float(np.mean(Y_treat_pre) - omega_b @ np.mean(Y_control_pre, axis=1))

        Y_syn_pre_b = alpha_b + omega_b @ Y_control_pre
        Y_syn_post_b = alpha_b + omega_b @ Y_control_post

        treat_pre_w = lam_b @ Y_treat_pre.ravel()
        syn_pre_w = lam_b @ Y_syn_pre_b
        tau_b = (np.mean(Y_treat_post) - np.mean(Y_syn_post_b)) - (treat_pre_w - syn_pre_w)
        return float(tau_b)

    def _moving_block_indices(self, n: int, block_size: int, rng: np.random.Generator) -> np.ndarray:
        """Sample time indices using a moving block bootstrap."""
        if n <= 0:
            return np.array([], dtype=int)
        block_size = max(1, min(block_size, n))
        starts = np.arange(0, n - block_size + 1)
        out = []
        while len(out) < n:
            s = int(rng.choice(starts))
            out.extend(range(s, s + block_size))
        return np.asarray(out[:n], dtype=int)

    def _resample_time_blocks(
        self,
        Y_control: np.ndarray,
        Y_treat_mean: np.ndarray,
        T0: int,
        T1: int,
        rng: np.random.Generator,
    ) -> tuple:
        """Resample pre and post periods separately."""
        post_len = T1 - T0
        idx_pre = self._moving_block_indices(T0, self.bootstrap_block_size, rng)
        idx_post = self._moving_block_indices(post_len, self.bootstrap_block_size, rng) + T0
        Y_control_pre_b = Y_control[:, idx_pre]
        Y_control_post_b = Y_control[:, idx_post]
        Y_treat_pre_b = Y_treat_mean[idx_pre]
        Y_treat_post_b = Y_treat_mean[idx_post]
        return Y_control_pre_b, Y_control_post_b, Y_treat_pre_b, Y_treat_post_b

    def _time_block_bootstrap_se_ci(
        self,
        Y_control: np.ndarray,
        Y_treat_mean: np.ndarray,
        T0: int,
        T1: int,
    ) -> tuple:
        """Time block bootstrap inference for SDID (mean-scale)."""
        rng = np.random.default_rng(self.bootstrap_seed)
        bootstrap_effects = []
        failed = 0

        for _ in range(self.n_bootstrap):
            try:
                Y_c_pre, Y_c_post, Y_t_pre, Y_t_post = self._resample_time_blocks(
                    Y_control, Y_treat_mean, T0, T1, rng
                )
                tau_b = self._compute_att_from_matrices(Y_c_pre, Y_c_post, Y_t_pre, Y_t_post)
                if np.isfinite(tau_b):
                    bootstrap_effects.append(float(tau_b))
                else:
                    failed += 1
            except Exception:
                failed += 1

        bootstrap_effects = np.asarray(bootstrap_effects, dtype=float)
        self.bootstrap_failures_ = failed

        if bootstrap_effects.size < 30:
            return np.nan, np.nan, np.nan, np.nan, bootstrap_effects

        se = float(np.std(bootstrap_effects, ddof=1))
        if not np.isfinite(se) or se <= 0:
            se = np.nan
        ci_lower = float(np.percentile(bootstrap_effects, (self.alpha / 2) * 100))
        ci_upper = float(np.percentile(bootstrap_effects, (1 - self.alpha / 2) * 100))
        if np.isfinite(se) and se > 0:
            z_score = float(self.treatment_effect / se)
            pvalue = float(2 * (1 - stats.norm.cdf(abs(z_score))))
        else:
            pvalue = np.nan
        return float(se), float(ci_lower), float(ci_upper), float(pvalue), bootstrap_effects

    def _placebo_variance_se_ci(
        self,
        Y_control: np.ndarray,
        Y_treat: np.ndarray,
        T0: int,
        T1: int,
    ) -> tuple:
        """
        Placebo inference: sample pseudo-treated from donors, re-fit, compute placebo ATT.
        Returns SE, CI, p-value on per-geo (mean) scale.
        """
        N0 = Y_control.shape[0]
        N_tr = Y_treat.shape[0]
        if N0 < N_tr + 2:
            raise ValueError(
                f"Placebo requires at least N_tr+2 controls. Got N_control={N0}, N_treated={N_tr}."
            )

        rng = np.random.default_rng(self.bootstrap_seed)
        placebo_effects = []
        failed = 0

        for _ in range(self.n_bootstrap):
            try:
                perm = rng.permutation(N0)
                pseudo_treat_idx = perm[:N_tr]
                pseudo_ctrl_idx = perm[N_tr:]
                Y_pseudo_treat = Y_control[pseudo_treat_idx, :]
                Y_pseudo_ctrl = Y_control[pseudo_ctrl_idx, :]
                Y_pseudo_treat_mean = np.mean(Y_pseudo_treat, axis=0)

                Y_ctrl_pre = Y_pseudo_ctrl[:, :T0]
                Y_ctrl_post = Y_pseudo_ctrl[:, T0:T1]
                Y_treat_pre = Y_pseudo_treat_mean[:T0].reshape(1, -1)
                Y_treat_post = Y_pseudo_treat_mean[T0:T1]

                tau_p = self._compute_att_from_matrices(
                    Y_ctrl_pre, Y_ctrl_post,
                    Y_treat_pre.ravel(), Y_treat_post,
                )
                if np.isfinite(tau_p):
                    placebo_effects.append(float(tau_p))
                else:
                    failed += 1
            except Exception:
                failed += 1

        placebo_effects = np.asarray(placebo_effects, dtype=float)
        self.placebo_effects_ = placebo_effects
        self.placebo_failures_ = failed
        self.bootstrap_failures_ = failed

        if placebo_effects.size < 10:
            return np.nan, np.nan, np.nan, np.nan, placebo_effects

        se = float(np.std(placebo_effects, ddof=1))
        if not np.isfinite(se) or se <= 0:
            se = np.nan
        ci_lower = float(np.percentile(placebo_effects, (self.alpha / 2) * 100))
        ci_upper = float(np.percentile(placebo_effects, (1 - self.alpha / 2) * 100))
        tau = self.treatment_effect
        if np.isfinite(se) and se > 0:
            pvalue = float(2 * min(stats.norm.cdf(tau / se), 1 - stats.norm.cdf(tau / se)))
        else:
            pvalue = float(np.mean(np.abs(placebo_effects) >= np.abs(tau)))
        return float(se), float(ci_lower), float(ci_upper), float(pvalue), placebo_effects

    def run_analysis(self, panel_data: PanelDataset, multiple_treated: str = "pooled") -> None:
        """
        Run analysis and populate results.
        Exported paths (y, y_hat, treatment_effects, y_lower, y_upper) remain
        AGGREGATE scale for backward compatibility.
        """
        self.panel_data = panel_data
        self.fit_data(panel_data)
        self.fit_model()

        panel = self.panel_data
        wide = panel.wide_data.values
        control_idx = [i for i in range(wide.shape[0]) if panel.wide_data.index[i] not in panel.treated_units]
        treat_idx = [i for i in range(wide.shape[0]) if panel.wide_data.index[i] in panel.treated_units]
        Y_control = wide[control_idx, :]
        Y_treat = wide[treat_idx, :]
        N_tr = len(treat_idx)

        Y_syn_mean = self._alpha + self._omega @ Y_control
        Y_treat_agg = np.sum(Y_treat, axis=0)
        y = Y_treat_agg
        y_hat = np.asarray(Y_syn_mean * N_tr, dtype=float).copy()
        t0 = panel.treated_start_idxs[0]
        t1 = panel.treated_end_idxs[0] + 1

        pre_gap_adjustment = float(getattr(self, "_pre_gap_adjustment", 0.0))
        y_hat[t0:t1] = y_hat[t0:t1] + pre_gap_adjustment * N_tr

        effect = np.asarray(y, dtype=float) - np.asarray(y_hat, dtype=float)

        if len(panel_data.treated_units) == 1:
            self.results = {
                "times": panel.times,
                "y": y,
                "y_hat": y_hat,
                "treatment_effects": effect,
                "average_treatment_effect": self.aggregate_effect,
                "per_geo_effect": self.per_geo_effect,
                "aggregate_effect": self.aggregate_effect,
            }
        else:
            self.results = {
                "times": panel.times,
                "y": y.reshape(-1, 1),
                "y_hat": y_hat.reshape(-1, 1),
                "treatment_effects": effect.reshape(-1, 1),
                "average_treatment_effect": self.aggregate_effect,
                "per_geo_effect": self.per_geo_effect,
                "aggregate_effect": self.aggregate_effect,
            }

        ci_lower, ci_upper = self.treatment_ci
        y_lower = np.full_like(y_hat, np.nan, dtype=float)
        y_upper = np.full_like(y_hat, np.nan, dtype=float)
        if np.isfinite(ci_lower) and np.isfinite(ci_upper):
            ci_lower_agg = ci_lower * N_tr
            ci_upper_agg = ci_upper * N_tr
            y_lower[t0:t1] = y[t0:t1] - ci_upper_agg
            y_upper[t0:t1] = y[t0:t1] - ci_lower_agg
        self.results["y_lower"] = y_lower
        self.results["y_upper"] = y_upper

        class _Predictor:
            def __init__(self, omega, alpha, n_tr):
                self.omega = omega
                self.alpha = alpha
                self.n_tr = n_tr

            def predict(self, X):
                X = np.asarray(X)
                if X.ndim == 1:
                    X = X.reshape(1, -1)
                if X.shape[0] == len(self.omega):
                    return (self.alpha + self.omega @ X).ravel() * self.n_tr
                return (self.alpha + self.omega @ X.T).ravel() * self.n_tr

        self.model = _Predictor(self._omega, self._alpha, N_tr)

    def summary(self) -> pd.DataFrame:
        """Return summary DataFrame compatible with DID (aggregate effect)."""
        tau = getattr(self, "aggregate_effect", self.treatment_effect)
        t0 = self.panel_data.treated_start_idxs[0]
        t1 = self.panel_data.treated_end_idxs[0] + 1
        n_post = t1 - t0
        return pd.DataFrame(
            {
                "Average": [tau, 0],
                "Cumulative": [tau * n_post, 0],
            },
            index=["Absolute Effect", "Relative Effect"],
        )

    def get_detailed_results(self) -> dict:
        """Return SDID inference and diagnostics for MMT reporting."""
        parallel_trends_test = {"parallel_trends_violated": False, "interaction_pvalue": 1.0}

        bootstrap_effects = getattr(self, "bootstrap_effects_", np.array([], dtype=float))
        placebo_effects = getattr(self, "placebo_effects_", np.array([], dtype=float))

        if self.variance_method == "placebo":
            placebo_test = {
                "placebo_pvalue": getattr(self, "treatment_pvalue", np.nan),
                "n_placebos": int(placebo_effects.size),
                "placebo_effects": placebo_effects,
            }
        else:
            placebo_test = {
                "placebo_pvalue": np.nan,
                "n_placebos": 0,
                "placebo_effects": np.array([], dtype=float),
            }

        draws = bootstrap_effects if self.variance_method == "time_block_bootstrap" else placebo_effects
        n_failures = int(getattr(self, "bootstrap_failures_", 0))
        inference_diagnostics = {
            "method": self.variance_method,
            "n_replications": self.n_bootstrap,
            "failures": n_failures,
            "draws": draws,
            "draws_mean": float(np.mean(draws)) if draws.size > 0 else np.nan,
        }

        return {
            "treatment_effect": getattr(self, "per_geo_effect", self.treatment_effect),
            "treatment_effect_per_geo": getattr(self, "per_geo_effect", self.treatment_effect),
            "treatment_effect_aggregate": getattr(self, "aggregate_effect", self.treatment_effect),
            "standard_error": self.treatment_se,
            "p_value": getattr(self, "treatment_pvalue", None),
            "significant": (
                np.isfinite(getattr(self, "treatment_pvalue", np.nan))
                and getattr(self, "treatment_pvalue", np.nan) < self.alpha
            ),
            "parallel_trends_test": parallel_trends_test,
            "placebo_test": placebo_test,
            "sdid_diagnostics": getattr(self, "sdid_diagnostics", {}),
            "treatment_ci": getattr(self, "treatment_ci", None),
            "inference_diagnostics": inference_diagnostics,
        }
