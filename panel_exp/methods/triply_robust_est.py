from __future__ import annotations

import itertools
import math
import warnings
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.utils import check_random_state

from panel_exp.panel_data import PanelDataset
from panel_exp.impact import ImpactAnalyzer


# =============================================================================
# Triply Robust Panel Estimator (TROP)
# =============================================================================
# Practical implementation of the estimator proposed in:
# Athey, Imbens, Qu, Viviano, "Triply Robust Panel Estimators"
# https://arxiv.org/abs/2508.21536
#
# This implementation follows the paper's estimator structure:
#   1) unit/time fixed effects
#   2) low-rank regression adjustment with nuclear-norm regularization
#   3) unit weights with exponential distance decay
#   4) time weights with exponential distance decay
#   5) leave-one-out cross-validation over (zeta_u, zeta_t, lambda_L)
#   6) support for multiple treated units / treated periods
#   7) nonparametric bootstrap for variance with multiple treated units
#
# Design notes:
# - The optimization is solved using a proximal-gradient routine for the weighted
#   nuclear-norm objective.
# - We expose a sklearn-like wrapper so the estimator works with the current
#   ImpactAnalyzer integration pattern.
# - The estimator predicts untreated potential outcomes for treated cells.
#
# Assumptions:
# - No spillovers and no dynamic treatment effects, matching the paper's setup.
# - wide_data is unit x time.
# - treated_start_idxs are valid and treatment, once on, continues to the end of
#   the panel for treated units in the standard path. More general binary masks
#   are also supported internally.
#
# Mode notes:
# - global mode: production/scalable approximation; one masked weighted low-rank fit.
# - local mode: higher-fidelity benchmark; per-treated-cell fit with target-specific
#   weights; slower because it refits per treated cell.
# =============================================================================


EPS = 1e-10


def _trop_scalar_is_missing(v: Any) -> bool:
    """True if v is None, pandas NA, or a floating NaN (not for arrays/lists)."""
    if v is None:
        return True
    if isinstance(v, float) and math.isnan(v):
        return True
    try:
        if isinstance(v, np.floating) and np.isnan(v):
            return True
    except (TypeError, ValueError):
        pass
    try:
        if pd.isna(v):
            return True
    except (TypeError, ValueError):
        pass
    return False


def _trop_int_from_scalar(
    value: Any,
    *,
    field_name: str,
    function_name: str,
    section: str,
    required: bool = False,
    default: Optional[int] = None,
) -> Optional[int]:
    """
    NaN-safe scalar→int. Prints [TROP int-cast debug] when input is missing/non-finite.
    Use for any int() that might see NaN/None from panel data or diagnostics dicts.
    """
    if _trop_scalar_is_missing(value):
        print(
            f"[TROP int-cast debug] field={field_name!r} value={value!r} "
            f"function={function_name!r} section={section!r} reason=missing_or_na"
        )
        if required:
            raise ValueError(
                f"TROP requires a finite integer for {field_name} in {function_name} ({section}); got {value!r}"
            )
        return default
    try:
        x = float(value)
    except (TypeError, ValueError, OverflowError) as e:
        print(
            f"[TROP int-cast debug] field={field_name!r} value={value!r} "
            f"function={function_name!r} section={section!r} reason=not_numeric err={e!r}"
        )
        if required:
            raise ValueError(
                f"TROP requires a finite integer for {field_name} in {function_name} ({section}); got {value!r}"
            ) from e
        return default
    if not math.isfinite(x):
        print(
            f"[TROP int-cast debug] field={field_name!r} value={value!r} "
            f"function={function_name!r} section={section!r} reason=non_finite_float"
        )
        if required:
            raise ValueError(
                f"TROP requires a finite integer for {field_name} in {function_name} ({section}); got {value!r}"
            )
        return default
    try:
        return int(x)
    except (ValueError, OverflowError) as e:
        print(
            f"[TROP int-cast debug] field={field_name!r} value={value!r} "
            f"function={function_name!r} section={section!r} reason=int_conversion err={e!r}"
        )
        if required:
            raise
        return default


def _trop_int_from_numpy_count(
    count: Any,
    *,
    field_name: str,
    function_name: str,
    section: str,
) -> int:
    """
    int() wrapper for e.g. bool-mask .sum() results. If the count is non-finite, debug-print and return 0.
    """
    try:
        x = count.item() if hasattr(count, "item") else count
    except (ValueError, TypeError):
        x = count
    if _trop_scalar_is_missing(x):
        print(
            f"[TROP int-cast debug] field={field_name!r} value={x!r} "
            f"function={function_name!r} section={section!r} reason=count_missing_or_na"
        )
        return 0
    try:
        xf = float(x)
    except (TypeError, ValueError, OverflowError) as e:
        print(
            f"[TROP int-cast debug] field={field_name!r} value={x!r} "
            f"function={function_name!r} section={section!r} reason=count_not_numeric err={e!r}"
        )
        return 0
    if not math.isfinite(xf):
        print(
            f"[TROP int-cast debug] field={field_name!r} value={x!r} "
            f"function={function_name!r} section={section!r} reason=count_non_finite"
        )
        return 0
    return int(xf)


# Default hyperparameter grids (stability-first tuning): stronger regularization, distributed weights
_DEFAULT_LAMBDA_UNIT_GRID = (1.0, 5.0, 10.0, 25.0, 50.0)
_DEFAULT_LAMBDA_TIME_GRID = (0.1, 0.5, 1.0)
_DEFAULT_LAMBDA_NUCLEAR_GRID = (0.1, 0.5, 1.0)


def _soft_threshold_singular_values(s: np.ndarray, tau: float) -> np.ndarray:
    """Singular-value soft-thresholding for nuclear-norm proximal step."""
    return np.maximum(s - tau, 0.0)


def _as_float_array(x) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    return arr


def _safe_normalize(weights: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    total = weights.sum()
    if not np.isfinite(total) or total <= 0:
        return np.ones_like(weights) / len(weights)
    return weights / total


@dataclass
class TROPFitResult:
    """Internal container for fitted TROP objects.

    For global mode: alpha, delta, low_rank, effective_weight_matrix are populated.
    For local mode: these may be None or nan-filled; counterfactual_matrix and
    tau_hat_matrix are populated from per-cell fits.
    """

    counterfactual_matrix: np.ndarray
    tau_hat_matrix: np.ndarray
    lambda_unit: float
    lambda_time: float
    lambda_nuclear: float
    unit_weights: Optional[np.ndarray] = None
    time_weights: Optional[np.ndarray] = None
    effective_weight_matrix: Optional[np.ndarray] = None
    alpha: Optional[np.ndarray] = None
    delta: Optional[np.ndarray] = None
    low_rank: Optional[np.ndarray] = None
    objective_value: float = 0.0
    iterations: int = 0
    converged: bool = False
    cv_score: Optional[float] = None
    # Mode and local diagnostics
    method: str = "global"
    cell_converged_matrix: Optional[np.ndarray] = None
    cell_iterations_matrix: Optional[np.ndarray] = None
    cell_objective_matrix: Optional[np.ndarray] = None
    cv_mode: Optional[str] = None


class TROPWrapper:
    """
    Minimal wrapper to make TROP compatible with ImpactAnalyzer expectations.

    predict(X) ignores X contents and returns the fitted treated-series
    counterfactual path. This mirrors the package's light sklearn-style usage.
    """

    def __init__(self, y_hat_full: np.ndarray, treated_start_idx: int):
        self.y_hat_full = np.asarray(y_hat_full, dtype=float).reshape(-1)
        _tsi = _trop_int_from_scalar(
            treated_start_idx,
            field_name="treated_start_idx",
            function_name="TROPWrapper.__init__",
            section="sklearn_wrapper",
            required=True,
        )
        assert _tsi is not None
        self.treated_start_idx = _tsi
        self.params = None

    def predict(self, X):
        n = len(X)
        if n == len(self.y_hat_full):
            return self.y_hat_full
        if n == self.treated_start_idx:
            return self.y_hat_full[: self.treated_start_idx]
        post_len = len(self.y_hat_full) - self.treated_start_idx
        if n == post_len:
            return self.y_hat_full[self.treated_start_idx :]
        if n < len(self.y_hat_full):
            return self.y_hat_full[-n:]
        reps = int(np.ceil(n / len(self.y_hat_full)))
        return np.tile(self.y_hat_full, reps)[:n]


class TROP(ImpactAnalyzer):
    """
    Triply Robust Panel Estimator.

    Supports two estimation modes (method) and two tuning modes (cv_mode):

    - method: controls the estimation path at fit time.
      * global: One masked weighted low-rank fit (production/scalable).
      * local: Per-treated-cell fitting with cell-specific weights (slower, closer to paper).

    - cv_mode: controls which scoring path is used during parameter tuning.
      * global_obs: Row-level placebo CV with one global fit per placebo (fast, scalable).
      * local_obs: Row-level placebo CV with per-cell local fits per placebo (slower, closer to paper).

    Defaults: method=global -> cv_mode=global_obs; method=local -> cv_mode=local_obs.
    Flexible: method and cv_mode are independent (e.g. global estimator can be tuned with local_obs).

    References
    ----------
    Athey, Imbens, Qu, Viviano.
    "Triply Robust Panel Estimators".
    https://arxiv.org/abs/2508.21536

    Parameters
    ----------
    inference : Optional[Callable]
        Placeholder to align with package API. For multiple treated units, use
        bootstrap_variance() below.
    alpha : float, default=0.1
        Confidence level helper to match package behavior.
    full_model : bool, default=False
        Kept for compatibility. TROP is fundamentally a panel estimator that
        should use pre-treatment untreated cells to tune and fit.
    method : str, default="global"
        "global" = one masked weighted low-rank fit; "local" = per-cell fitting.
    cv_mode : str, optional
        "global_obs" | "local_obs". Controls tuning path. Default: global_obs for method=global,
        local_obs for method=local. Independent of method (flexible combinations allowed).
    inference_mode : str, default="auto"
        "auto" | "placebo" | "bootstrap". Auto: local->placebo; global->placebo if
        treated_units<2 else bootstrap.
    lambda_unit_grid : Sequence[float], optional
        Grid for unit-distance decay parameter zeta_u in the paper.
    lambda_time_grid : Sequence[float], optional
        Grid for time-distance decay parameter zeta_t in the paper.
    lambda_nuclear_grid : Sequence[float], optional
        Grid for nuclear-norm penalty lambda_L.
    cv_max_cycles : int, default=3
        Coordinate-descent cycling count for tuning as described in the paper.
    max_iter : int, default=500
        Maximum proximal-gradient iterations.
    tol : float, default=1e-6
        Optimization tolerance.
    step_size : float, default=1.0
        Initial proximal-gradient step size.
    l_step_multiplier : float, default=1.0
        Multiplies ``local_step`` only in the low-rank proximal gradient step
        ``Z = L - (local_step * l_step_multiplier) * grad`` (diagnostic / tuning knob).
    seasonal_period : Optional[int], default=None
        Optional seasonal period for time-distance calculations. If provided,
        time distance is min(|t-s|, seasonal wrap) within a season-aware metric.
    random_state : Optional[int], default=None
        Reproducibility for bootstrap / CV tie-breaking.
    verbose : bool, default=False
        Emit progress logs.
    trop_tuning_mode : str, default="stability_first"
        "stability_first" = full grid + validity filters + ranked selection (global method).
        "legacy_coordinate_descent" = original coordinate-descent CV (min CV score only).
    min_donor_support : int, default=3
        Minimum treated_row_*_n_support (global mode); configs below this are invalid.
    flat_cf_rel_tol : float, default=1e-5
        Relative tolerance: counterfactual is "flat" if (cf_post_max - cf_post_min) < tol * scale.
    reference_effects : Optional[dict], default=None
        Optional {"ridge": float, "augsynth": float} for directional consistency in extended selection.
    ci_width_ratio_max / ci_width_ratio_min : float
        Reject configs whose CI width / |ATE| is implausible when placebo inference is available.
    max_placebo_std_selection : Optional[float]
        Reject configs with placebo ATE std above this threshold (if finite).
    tuning_placebo_max_fits : int, default=12
        Cap placebo refits per config when logging tuning table (0 = skip placebo columns).
    disable_internal_tuning : bool, default=False
        If True, skip all internal search (stability_first, legacy CV, filtering). Requires
        singleton ``lambda_*_grid``; returns those lambdas unchanged. Use when an outer runner
        sweeps hyperparameters.
    """

    def __init__(
        self,
        inference: Optional[Callable] = None,
        alpha: float = 0.1,
        full_model: bool = False,
        method: str = "global",
        inference_mode: str = "auto",
        local_max_treated_cells: Optional[int] = None,
        local_reuse_tuning: bool = True,
        cv_mode: Optional[str] = None,
        lambda_unit_grid: Optional[Sequence[float]] = None,
        lambda_time_grid: Optional[Sequence[float]] = None,
        lambda_nuclear_grid: Optional[Sequence[float]] = None,
        cv_max_cycles: int = 3,
        max_iter: int = 500,
        tol: float = 1e-6,
        step_size: float = 1.0,
        l_step_multiplier: float = 1.0,
        seasonal_period: Optional[int] = None,
        min_overlap_periods: int = 5,
        custom_treated_mask: Optional[np.ndarray] = None,
        max_cv_placebos: int = 10,
        n_bootstrap: int = 200,
        random_state: Optional[int] = None,
        verbose: bool = False,
        enforce_nonnegative_counterfactual: bool = False,
        trop_tuning_mode: str = "stability_first",
        min_donor_support: int = 3,
        flat_cf_rel_tol: float = 1e-5,
        reference_effects: Optional[Dict[str, float]] = None,
        ci_width_ratio_max: float = 50.0,
        ci_width_ratio_min: float = 1e-8,
        max_placebo_std_selection: Optional[float] = None,
        tuning_placebo_max_fits: int = 12,
        disable_internal_tuning: bool = False,
        debug_donor_weights: bool = False,
        diagnostic_weight_threshold_compare: bool = False,
    ):
        if method not in ("global", "local"):
            raise ValueError(f"method must be 'global' or 'local', got {method!r}")
        if inference_mode not in ("auto", "placebo", "bootstrap"):
            raise ValueError(f"inference_mode must be 'auto', 'placebo', or 'bootstrap', got {inference_mode!r}")

        _cv_mode = cv_mode if cv_mode is not None else ("global_obs" if method == "global" else "local_obs")
        if _cv_mode not in ("global_obs", "local_obs"):
            raise ValueError(f"cv_mode must be 'global_obs' or 'local_obs', got {_cv_mode!r}")

        print("TROP INIT → method:", method, "| cv_mode:", _cv_mode)

        self.inference = inference
        self.alpha = alpha
        self.ppf = stats.norm.ppf(alpha / 2 + (1 - alpha))
        self.full_model = full_model
        self.method = method
        self.inference_mode = inference_mode
        self.local_max_treated_cells = local_max_treated_cells
        self.local_reuse_tuning = local_reuse_tuning
        self.cv_mode = _cv_mode

        self.lambda_unit_grid = list(lambda_unit_grid or list(_DEFAULT_LAMBDA_UNIT_GRID))
        self.lambda_time_grid = list(lambda_time_grid or list(_DEFAULT_LAMBDA_TIME_GRID))
        self.lambda_nuclear_grid = list(lambda_nuclear_grid or list(_DEFAULT_LAMBDA_NUCLEAR_GRID))
        self.cv_max_cycles = _trop_int_from_scalar(
            cv_max_cycles,
            field_name="cv_max_cycles",
            function_name="TROP.__init__",
            section="hyperparams",
            required=True,
        )
        assert self.cv_max_cycles is not None
        self.max_iter = _trop_int_from_scalar(
            max_iter,
            field_name="max_iter",
            function_name="TROP.__init__",
            section="hyperparams",
            required=True,
        )
        assert self.max_iter is not None
        self.tol = float(tol)
        self.step_size = float(step_size)
        self.l_step_multiplier = float(l_step_multiplier)
        self.seasonal_period = seasonal_period
        self.min_overlap_periods = _trop_int_from_scalar(
            min_overlap_periods,
            field_name="min_overlap_periods",
            function_name="TROP.__init__",
            section="hyperparams",
            required=True,
        )
        assert self.min_overlap_periods is not None
        self.custom_treated_mask = None if custom_treated_mask is None else np.asarray(custom_treated_mask, dtype=bool)
        self.max_cv_placebos = _trop_int_from_scalar(
            max_cv_placebos,
            field_name="max_cv_placebos",
            function_name="TROP.__init__",
            section="hyperparams",
            required=True,
        )
        assert self.max_cv_placebos is not None
        self.n_bootstrap = _trop_int_from_scalar(
            n_bootstrap,
            field_name="n_bootstrap",
            function_name="TROP.__init__",
            section="hyperparams",
            required=True,
        )
        assert self.n_bootstrap is not None
        self.random_state = random_state
        self.verbose = verbose
        self.enforce_nonnegative_counterfactual = bool(enforce_nonnegative_counterfactual)
        if trop_tuning_mode not in ("stability_first", "legacy_coordinate_descent"):
            raise ValueError(
                f"trop_tuning_mode must be 'stability_first' or 'legacy_coordinate_descent', got {trop_tuning_mode!r}"
            )
        self.trop_tuning_mode = trop_tuning_mode
        self.min_donor_support = _trop_int_from_scalar(
            min_donor_support,
            field_name="min_donor_support",
            function_name="TROP.__init__",
            section="hyperparams",
            required=True,
        )
        assert self.min_donor_support is not None
        self.flat_cf_rel_tol = float(flat_cf_rel_tol)
        self.reference_effects = dict(reference_effects) if reference_effects else None
        self.ci_width_ratio_max = float(ci_width_ratio_max)
        self.ci_width_ratio_min = float(ci_width_ratio_min)
        self.max_placebo_std_selection = max_placebo_std_selection
        self.tuning_placebo_max_fits = _trop_int_from_scalar(
            tuning_placebo_max_fits,
            field_name="tuning_placebo_max_fits",
            function_name="TROP.__init__",
            section="hyperparams",
            required=True,
        )
        assert self.tuning_placebo_max_fits is not None
        self.disable_internal_tuning = bool(disable_internal_tuning)
        self.debug_donor_weights = bool(debug_donor_weights)
        self.diagnostic_weight_threshold_compare = bool(diagnostic_weight_threshold_compare)
        self._rng = check_random_state(random_state)

        # fitted state
        self.panel_data: Optional[PanelDataset] = None
        self.wide_: Optional[pd.DataFrame] = None
        self.times_: Optional[pd.Index] = None
        self.units_: Optional[pd.Index] = None
        self.treated_mask_: Optional[np.ndarray] = None
        self.control_mask_: Optional[np.ndarray] = None
        self.observed_mask_: Optional[np.ndarray] = None
        self.fit_result_: Optional[TROPFitResult] = None
        self.best_params_: Optional[dict] = None
        self.cv_history_: list[dict] = []
        self.treated_start_idx_: Optional[int] = None
        self.tuning_comparison_df_: Optional[pd.DataFrame] = None
        self.tuning_selection_summary_: Optional[dict[str, Any]] = None

    def set_treatment_mask(self, treated_mask: np.ndarray):
        """Allow arbitrary unit x time treatment masks for staggered/intermittent exposure."""
        treated_mask = np.asarray(treated_mask, dtype=bool)
        if self.wide_ is not None and treated_mask.shape != self.wide_.shape:
            raise ValueError(f"treated_mask shape {treated_mask.shape} does not match panel shape {self.wide_.shape}.")
        self.custom_treated_mask = treated_mask
        self.treated_mask_ = treated_mask.copy()
        self.control_mask_ = ~self.treated_mask_

    # ---------------------------------------------------------------------
    # Package API compatibility
    # ---------------------------------------------------------------------
    def fit_data(self, panel: PanelDataset):
        """
        Keep the same package pattern as TBR/TBRRidge.

        Returns
        -------
        X : np.ndarray
            Control panel over time (n_time x n_control)
        y : np.ndarray
            Aggregated treated series over time
        """
        self.panel_data = panel
        wide = panel.wide_data.copy()
        self.wide_ = wide
        self.times_ = wide.columns
        self.units_ = wide.index

        treated_units = list(panel.treated_units)

        treated_series = panel.treated_series(treated_units=treated_units, period="full").values.T
        if treated_series.ndim > 1:
            y = treated_series.sum(axis=1)
        else:
            y = treated_series.flatten()

        X = panel.control_series(treated_units=treated_units, period="full").values.T
        if X.ndim == 1:
            X = X.reshape(-1, 1)

        self.treated_start_idx_ = _trop_int_from_scalar(
            panel.treated_start_idxs[0],
            field_name="panel.treated_start_idxs[0]",
            function_name="fit_data",
            section="panel_setup",
            required=True,
        )
        assert self.treated_start_idx_ is not None
        return X, y

    def fit_model(self):
        """Fit TROP and return a sklearn-like wrapper for downstream package use."""
        # Phase 9: Print inference settings (for debugging degenerate inference)
        if self.disable_internal_tuning:
            print("[TROP DEBUG] disable_internal_tuning=True — no internal CV/grid/stability selection")
        else:
            print(f"[TROP DEBUG] max_cv_placebos={self.max_cv_placebos} n_bootstrap={self.n_bootstrap} cv_max_cycles={self.cv_max_cycles}")
        self.fit_data(self.panel_data)
        self._validate_panel()
        if self.custom_treated_mask is not None:
            self.set_treatment_mask(self.custom_treated_mask)
        else:
            self._build_assignment_masks()
        best_params = self._tune_parameters()
        self.best_params_ = best_params
        if self.verbose:
            print(f"[TROP] best params={best_params}")
        # Phase 4: Debug lambda selection
        print(f"[TROP DEBUG] chosen lambda_unit={best_params.get('lambda_unit')} lambda_time={best_params.get('lambda_time')} lambda_nuclear={best_params.get('lambda_nuclear')} | cv_mode={self.cv_mode} | method={self.method}")
        print(f"[TROP DEBUG] cv_history_ length={len(self.cv_history_)} | n_cv_candidates={len(self.cv_history_)}")
        if len(self.cv_history_) > 0:
            if self.disable_internal_tuning:
                print(f"[TROP DEBUG] fixed lambdas — cv_history_ metadata: {self.cv_history_[0]}")
            else:
                hist = [x for x in self.cv_history_ if not x.get("hard_invalid", False)]
                pool = hist if hist else self.cv_history_
                best_entry = min(pool, key=lambda x: x.get("cv_score", float("inf")))
                print(f"[TROP DEBUG] best cv_score={best_entry.get('cv_score')} | best params from cv_history={best_entry}")
        if any(np.isnan([best_params.get("lambda_unit"), best_params.get("lambda_time"), best_params.get("lambda_nuclear")])):
            print("[TROP DEBUG WARN] One or more chosen lambdas is NaN")
        # Task 1-4, 8: Enable solver/FE diagnostics for the final fit only (not CV)
        self._debug_this_fit = True
        fit_result = self._fit_for_params(**best_params)
        self._debug_this_fit = False
        self.fit_result_ = fit_result

        # Task 3: Temporary debug prints for counterfactual path (treated observed post-period)
        treated_obs = self.treated_mask_ & self.observed_mask_
        n_t = self.wide_.shape[1]
        post_cols = np.arange(n_t) >= self.treated_start_idx_
        treated_obs_post = treated_obs & np.broadcast_to(post_cols, treated_obs.shape)
        cf_vals = fit_result.counterfactual_matrix[treated_obs_post]
        tau_vals = fit_result.tau_hat_matrix[treated_obs_post]
        if cf_vals.size > 0:
            print(f"[TROP DEBUG] counterfactual_matrix (treated post): min={float(np.min(cf_vals)):.4g} max={float(np.max(cf_vals)):.4g}")
        if tau_vals.size > 0:
            print(f"[TROP DEBUG] tau_hat_matrix (treated post): min={float(np.min(tau_vals)):.4g} max={float(np.max(tau_vals)):.4g}")
        y_hat_agg = self._aggregate_treated_counterfactual(fit_result.counterfactual_matrix)
        if y_hat_agg.size > 0:
            post_yh = y_hat_agg[self.treated_start_idx_ :]
            if post_yh.size > 0:
                print(f"[TROP DEBUG] aggregated y_hat_full (post): min={float(np.min(post_yh)):.4g} max={float(np.max(post_yh)):.4g}")

        # aggregate fitted counterfactual for treated units into one series wrapper
        y_hat_full = self._aggregate_treated_counterfactual(fit_result.counterfactual_matrix)
        return TROPWrapper(y_hat_full=y_hat_full, treated_start_idx=self.treated_start_idx_)

    def run_analysis(
        self,
        panel_data: PanelDataset,
        **inference_kwargs,
    ) -> Dict:
        """Run analysis and aggregate y to 1D when multiple treated units (y_hat is already aggregated)."""
        super().run_analysis(panel_data, **inference_kwargs)
        y = self.results["y"]
        y_hat = self.results["y_hat"]
        if y.ndim == 2 and y_hat.ndim == 1:
            self.results["y"] = np.sum(y, axis=1)
        return self.results

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    @staticmethod
    def _bootstrap_pvalue_two_sided(
        samples: np.ndarray, alpha: float = 0.1
    ) -> tuple[Optional[float], bool]:
        """
        Two-sided p-value: 2 * min(P(sample > 0), P(sample < 0)).
        Degenerate (all equal): p_value = None. Empty: (nan, False).
        """
        samples = np.asarray(samples, dtype=float)
        n = len(samples)
        if n == 0:
            return np.nan, False
        # Single draw or identical draws: not a usable bootstrap distribution
        if n == 1 or (n > 1 and np.allclose(samples, samples[0])):
            return None, False
        p_gt = float(np.mean(samples > 0.0))
        p_lt = float(np.mean(samples < 0.0))
        p_value = float(2.0 * min(p_gt, p_lt))
        p_value = min(max(p_value, 0.0), 1.0)
        significant = p_value is not None and np.isfinite(p_value) and p_value < alpha
        return p_value, significant

    def _trop_ci_sanity_check(
        self,
        cumulative_effect: float,
        ci_lo: float,
        ci_hi: float,
    ) -> None:
        """Warn on inverted bounds, effect outside CI, or implausible narrow CI (prints [TROP CI WARNING] ...)."""
        if not (np.isfinite(ci_lo) and np.isfinite(ci_hi) and np.isfinite(cumulative_effect)):
            return
        if ci_hi < ci_lo:
            print(f"[TROP CI WARNING] Inconsistent CI scale detected: Effect Upper ({ci_hi}) < Effect Lower ({ci_lo})")
            return
        width = ci_hi - ci_lo
        ae = abs(float(cumulative_effect))
        if ae > 0 and width > 0:
            if ae > abs(ci_hi) + 1e-6 and ae > abs(ci_lo) + 1e-6:
                print(
                    "[TROP CI WARNING] Inconsistent CI scale detected: "
                    f"|effect|={ae:.6g} vs bounds [{ci_lo:.6g}, {ci_hi:.6g}]"
                )
            if width < 1e-6 * max(ae, 1.0):
                print(
                    "[TROP CI WARNING] Inconsistent CI scale detected: "
                    f"CI width={width:.6g} is tiny relative to |effect|={ae:.6g}"
                )

    def bootstrap_variance(self, n_boot: Optional[int] = None, random_state: Optional[int] = None) -> dict:
        """
        Nonparametric bootstrap over treated/control unit rows.

        Returns
        -------
        dict with keys:
            variance, std_error, bootstrap_ates, ate, ci_percentile,
            ci_normal, p_value, significant
        """
        if self.fit_result_ is None:
            raise RuntimeError("Fit the model before calling bootstrap_variance().")
        if self.panel_data is None or self.wide_ is None:
            raise RuntimeError("Panel data not set.")

        rng = check_random_state(self.random_state if random_state is None else random_state)
        treated_units = list(self.panel_data.treated_units)
        control_units = list(self.panel_data.control_units)
        if n_boot is None:
            n_boot = self.n_bootstrap
        else:
            _nb = _trop_int_from_scalar(
                n_boot,
                field_name="n_boot",
                function_name="bootstrap_variance",
                section="bootstrap",
                required=False,
                default=self.n_bootstrap,
            )
            n_boot = _nb if _nb is not None else self.n_bootstrap

        if len(treated_units) < 2:
            return self.placebo_variance()

        # Cumulative ATT over all treated, observed cells (same unit as total_incremental / CSV Absolute Effect).
        mask_fit = self.treated_mask_ & self.observed_mask_
        ate = float(np.sum(self.fit_result_.tau_hat_matrix[mask_fit]))
        bootstrap_ates = []
        params = self.best_params_ or self._tune_parameters()

        for _ in range(n_boot):
            sampled_controls = list(rng.choice(control_units, size=len(control_units), replace=True))
            sampled_treated = list(rng.choice(treated_units, size=len(treated_units), replace=True))
            sampled_units = sampled_controls + sampled_treated
            sampled_labels = [f"boot_unit_{j}__{unit}" for j, unit in enumerate(sampled_units)]
            wide_boot = self.wide_.loc[sampled_units].copy()
            wide_boot.index = sampled_labels
            treated_boot = sampled_labels[len(sampled_controls):]

            panel_boot = PanelDataset(
                wide_data=wide_boot,
                treated_periods=self.panel_data.treated_periods,
                treated_units=treated_boot,
            )
            est_boot = TROP(
                inference=self.inference,
                alpha=self.alpha,
                full_model=self.full_model,
                method=self.method,
                inference_mode=self.inference_mode,
                cv_mode=self.cv_mode,
                local_max_treated_cells=self.local_max_treated_cells,
                local_reuse_tuning=self.local_reuse_tuning,
                lambda_unit_grid=[params["lambda_unit"]],
                lambda_time_grid=[params["lambda_time"]],
                lambda_nuclear_grid=[params["lambda_nuclear"]],
                disable_internal_tuning=True,
                cv_max_cycles=1,
                max_iter=self.max_iter,
                tol=self.tol,
                step_size=self.step_size,
                l_step_multiplier=self.l_step_multiplier,
                seasonal_period=self.seasonal_period,
                min_overlap_periods=self.min_overlap_periods,
                max_cv_placebos=self.max_cv_placebos,
                n_bootstrap=self.n_bootstrap,
                random_state=rng.randint(0, 2**31 - 1),
                verbose=False,
                enforce_nonnegative_counterfactual=self.enforce_nonnegative_counterfactual,
            )
            est_boot.fit_data(panel_boot)
            est_boot._validate_panel()
            est_boot._build_assignment_masks()
            fit_boot = est_boot._fit_for_params(**params)
            mask_b = est_boot.treated_mask_ & est_boot.observed_mask_
            tau_boot = fit_boot.tau_hat_matrix[mask_b]
            bootstrap_ates.append(float(np.sum(tau_boot)))

        bootstrap_ates = np.asarray(bootstrap_ates, dtype=float)
        variance = float(np.var(bootstrap_ates, ddof=1)) if len(bootstrap_ates) > 1 else 0.0
        std_error = float(np.sqrt(max(variance, 0.0)))
        alpha_tail = self.alpha / 2.0
        ci_percentile = (
            float(np.quantile(bootstrap_ates, alpha_tail)),
            float(np.quantile(bootstrap_ates, 1.0 - alpha_tail)),
        ) if len(bootstrap_ates) > 0 else (np.nan, np.nan)
        ci_normal = (ate - self.ppf * std_error, ate + self.ppf * std_error)
        p_value, significant = self._bootstrap_pvalue_two_sided(bootstrap_ates, alpha=self.alpha)

        return {
            "ate": ate,
            "variance": variance,
            "std_error": std_error,
            "bootstrap_ates": bootstrap_ates,
            "ci_percentile": ci_percentile,
            "ci_normal": ci_normal,
            "cumulative_ci": ci_percentile,
            "p_value": p_value,
            "significant": significant,
        }
    def placebo_variance(self) -> dict:
        """Placebo variance for single- or few-treated-unit panels using control units."""
        if self.fit_result_ is None:
            raise RuntimeError("Fit the model before calling placebo_variance().")

        control_rows = np.where(~self.treated_mask_.any(axis=1))[0]
        treated_patterns = self._treated_row_patterns()
        placebo_ates = []
        params = self.best_params_ or self._tune_parameters()
        mask_fit = self.treated_mask_ & self.observed_mask_
        ate = float(np.sum(self.fit_result_.tau_hat_matrix[mask_fit]))

        if len(control_rows) == 0:
            raise ValueError("Need at least one control unit for placebo variance.")

        for prow in control_rows:
            for pattern in treated_patterns:
                treated_mask_backup = self.treated_mask_.copy()
                control_mask_backup = self.control_mask_.copy()
                placebo_mask = treated_mask_backup.copy()
                placebo_mask[prow, pattern] = True
                self.treated_mask_ = placebo_mask
                self.control_mask_ = ~placebo_mask
                fit_res = self._fit_for_params(**params)
                pm = self.treated_mask_ & self.observed_mask_
                placebo_ates.append(float(np.sum(fit_res.tau_hat_matrix[pm])))
                self.treated_mask_ = treated_mask_backup
                self.control_mask_ = control_mask_backup

        placebo_ates = np.asarray(placebo_ates, dtype=float)
        # Phase 5: Placebo inference debug
        n_placebo = len(placebo_ates)
        p_min = float(np.min(placebo_ates)) if n_placebo > 0 else np.nan
        p_max = float(np.max(placebo_ates)) if n_placebo > 0 else np.nan
        p_mean = float(np.mean(placebo_ates)) if n_placebo > 0 else np.nan
        p_std = float(np.std(placebo_ates)) if n_placebo > 1 else 0.0
        all_same = n_placebo <= 1 or (p_std == 0 and np.all(placebo_ates == placebo_ates[0]))
        has_nan_inf = not np.all(np.isfinite(placebo_ates)) if n_placebo > 0 else False
        print(f"[TROP DEBUG] placebo: n={n_placebo} min={p_min} max={p_max} mean={p_mean} std={p_std} all_identical={all_same} has_nan_inf={has_nan_inf}")
        if n_placebo <= 1 or all_same or (p_std == 0 and n_placebo > 1):
            print("[TROP DEBUG] *** Degenerate placebo distribution ***")
        variance = float(np.var(placebo_ates, ddof=1)) if len(placebo_ates) > 1 else 0.0
        std_error = float(np.sqrt(max(variance, 0.0)))
        alpha_tail = self.alpha / 2.0
        ci_percentile = (
            float(np.quantile(placebo_ates, alpha_tail)),
            float(np.quantile(placebo_ates, 1.0 - alpha_tail)),
        ) if len(placebo_ates) > 0 else (np.nan, np.nan)
        ci_normal = (ate - self.ppf * std_error, ate + self.ppf * std_error)
        p_value, significant = self._bootstrap_pvalue_two_sided(placebo_ates, alpha=self.alpha)

        return {
            "ate": ate,
            "variance": variance,
            "std_error": std_error,
            "placebo_ates": placebo_ates,
            "ci_percentile": ci_percentile,
            "ci_normal": ci_normal,
            "cumulative_ci": ci_percentile,
            "p_value": p_value,
            "significant": significant,
        }

    def _placebo_variance_with_params(
        self,
        params: dict,
        *,
        max_placebo_fits: Optional[int] = None,
    ) -> dict:
        """
        Placebo inference using explicit (lambda_unit, lambda_time, lambda_nuclear).
        Optionally cap total placebo fits for fast tuning-table rows.
        """
        if self.fit_result_ is None:
            raise RuntimeError("Set fit_result_ before _placebo_variance_with_params().")

        control_rows = np.where(~self.treated_mask_.any(axis=1))[0]
        treated_patterns = self._treated_row_patterns()
        placebo_ates = []
        mask_fit = self.treated_mask_ & self.observed_mask_
        ate = float(np.sum(self.fit_result_.tau_hat_matrix[mask_fit]))

        if len(control_rows) == 0:
            raise ValueError("Need at least one control unit for placebo variance.")

        lu, lt, ln = params["lambda_unit"], params["lambda_time"], params["lambda_nuclear"]
        fit_count = 0
        for prow, pattern in itertools.product(control_rows, treated_patterns):
            if max_placebo_fits is not None and fit_count >= max_placebo_fits:
                break
            treated_mask_backup = self.treated_mask_.copy()
            control_mask_backup = self.control_mask_.copy()
            placebo_mask = treated_mask_backup.copy()
            placebo_mask[prow, pattern] = True
            self.treated_mask_ = placebo_mask
            self.control_mask_ = ~placebo_mask
            fit_res = self._fit_for_params(
                lambda_unit=float(lu),
                lambda_time=float(lt),
                lambda_nuclear=float(ln),
            )
            pm = self.treated_mask_ & self.observed_mask_
            placebo_ates.append(float(np.sum(fit_res.tau_hat_matrix[pm])))
            self.treated_mask_ = treated_mask_backup
            self.control_mask_ = control_mask_backup
            fit_count += 1

        placebo_ates = np.asarray(placebo_ates, dtype=float)
        n_placebo = len(placebo_ates)
        p_std = float(np.std(placebo_ates, ddof=1)) if n_placebo > 1 else 0.0
        variance = float(np.var(placebo_ates, ddof=1)) if len(placebo_ates) > 1 else 0.0
        std_error = float(np.sqrt(max(variance, 0.0)))
        alpha_tail = self.alpha / 2.0
        ci_percentile = (
            float(np.quantile(placebo_ates, alpha_tail)),
            float(np.quantile(placebo_ates, 1.0 - alpha_tail)),
        ) if len(placebo_ates) > 0 else (np.nan, np.nan)
        ci_normal = (ate - self.ppf * std_error, ate + self.ppf * std_error)
        p_value, significant = self._bootstrap_pvalue_two_sided(placebo_ates, alpha=self.alpha)

        return {
            "ate": ate,
            "variance": variance,
            "std_error": std_error,
            "placebo_std": p_std,
            "placebo_ates": placebo_ates,
            "ci_percentile": ci_percentile,
            "ci_normal": ci_normal,
            "cumulative_ci": ci_percentile,
            "p_value": p_value,
            "significant": significant,
            "n_placebo_fits": n_placebo,
        }

    def get_component_matrices(self) -> dict[str, pd.DataFrame]:
        if self.fit_result_ is None or self.wide_ is None:
            raise RuntimeError("Model not fitted.")
        if self.fit_result_.method == "local":
            raise ValueError(
                "Component matrices (alpha, delta, low_rank, effective_weights) are only "
                "available for global mode. Local mode fits per-cell and has no single "
                "global decomposition."
            )
        return {
            "alpha": pd.DataFrame(
                np.repeat(self.fit_result_.alpha, self.wide_.shape[1], axis=1),
                index=self.wide_.index,
                columns=self.wide_.columns,
            ),
            "delta": pd.DataFrame(
                np.repeat(self.fit_result_.delta, self.wide_.shape[0], axis=0),
                index=self.wide_.index,
                columns=self.wide_.columns,
            ),
            "low_rank": pd.DataFrame(
                self.fit_result_.low_rank,
                index=self.wide_.index,
                columns=self.wide_.columns,
            ),
            "effective_weights": pd.DataFrame(
                self.fit_result_.effective_weight_matrix,
                index=self.wide_.index,
                columns=self.wide_.columns,
            ),
        }
    def export_tuning_comparison_csv(self, path: str) -> None:
        """Write `tuning_comparison_df_` to CSV (after stability_first fit)."""
        if self.tuning_comparison_df_ is None or self.tuning_comparison_df_.empty:
            raise RuntimeError("No tuning comparison table; run fit_model with trop_tuning_mode='stability_first' first.")
        self.tuning_comparison_df_.to_csv(path, index=False)

    def summarize_effects(self) -> dict:
        if self.fit_result_ is None or self.wide_ is None:
            raise RuntimeError("Model not fitted.")

        treated_obs = self.treated_mask_ & self.observed_mask_
        tau = self.fit_result_.tau_hat_matrix
        counterfactual = self.fit_result_.counterfactual_matrix
        observed = self.wide_.values.astype(float)

        ate = float(np.mean(tau[treated_obs]))
        total_incremental = float(np.sum(tau[treated_obs]))
        observed_total = float(np.sum(observed[treated_obs]))
        counterfactual_total = float(np.sum(counterfactual[treated_obs]))
        relative_lift = np.nan
        if abs(counterfactual_total) > EPS:
            relative_lift = total_incremental / counterfactual_total

        # Post-period counterfactual min/max (treated observed cells in post-period only)
        post_cols = np.arange(self.wide_.shape[1]) >= self.treated_start_idx_
        treated_obs_post = treated_obs & post_cols[np.newaxis, :]
        cf_post_vals = counterfactual[treated_obs_post]
        cf_post_min = float(np.min(cf_post_vals)) if cf_post_vals.size > 0 else np.nan
        cf_post_max = float(np.max(cf_post_vals)) if cf_post_vals.size > 0 else np.nan

        return {
            "ate": ate,
            "total_incremental": total_incremental,
            "observed_total": observed_total,
            "counterfactual_total": counterfactual_total,
            "relative_lift": float(relative_lift) if np.isfinite(relative_lift) else np.nan,
            "cf_post_min": cf_post_min,
            "cf_post_max": cf_post_max,
        }

    def period_effects(self) -> pd.DataFrame:
        if self.fit_result_ is None or self.wide_ is None:
            raise RuntimeError("Model not fitted.")

        rows = []
        tau = self.fit_result_.tau_hat_matrix
        observed = self.wide_.values.astype(float)
        counterfactual = self.fit_result_.counterfactual_matrix

        for t_idx, period in enumerate(self.wide_.columns):
            mask_t = self.treated_mask_[:, t_idx] & self.observed_mask_[:, t_idx]
            n_treated = _trop_int_from_numpy_count(
                mask_t.sum(),
                field_name="n_treated_cells(period_effects)",
                function_name="period_effects",
                section="period_summary",
            )
            if n_treated == 0:
                continue
            incremental = float(np.sum(tau[:, t_idx][mask_t]))
            ate_t = float(np.mean(tau[:, t_idx][mask_t]))
            observed_t = float(np.sum(observed[:, t_idx][mask_t]))
            counterfactual_t = float(np.sum(counterfactual[:, t_idx][mask_t]))
            relative_lift_t = np.nan
            if abs(counterfactual_t) > EPS:
                relative_lift_t = incremental / counterfactual_t
            rows.append(
                {
                    "period": period,
                    "n_treated_cells": n_treated,
                    "incremental": incremental,
                    "ate": ate_t,
                    "observed": observed_t,
                    "counterfactual": counterfactual_t,
                    "relative_lift": float(relative_lift_t) if np.isfinite(relative_lift_t) else np.nan,
                }
            )

        return pd.DataFrame(rows).set_index("period") if rows else pd.DataFrame(
            columns=["n_treated_cells", "incremental", "ate", "observed", "counterfactual", "relative_lift"]
        )

    def inference_summary(self, n_boot: Optional[int] = None, random_state: Optional[int] = None) -> dict:
        if self.fit_result_ is None:
            raise RuntimeError("Fit the model before calling inference_summary().")

        try:
            base = self.summarize_effects()
        except Exception as ex:
            print(f"[TROP inference_summary] FAILED phase=summarize_effects error={ex!r}")
            raise

        use_placebo = False
        if self.inference_mode == "placebo":
            use_placebo = True
        elif self.inference_mode == "bootstrap":
            use_placebo = False
        elif self.inference_mode == "auto":
            if self.method == "local":
                use_placebo = True
            else:
                use_placebo = len(self.panel_data.treated_units) < 2

        try:
            if use_placebo:
                infer = self.placebo_variance()
                infer["inference_method"] = "placebo"
                infer["method"] = "placebo"
            else:
                infer = self.bootstrap_variance(n_boot=n_boot, random_state=random_state)
                if "bootstrap_ates" in infer:
                    infer["inference_method"] = "bootstrap"
                    infer["method"] = "bootstrap"
                else:
                    infer["inference_method"] = "placebo"
                    infer["method"] = "placebo"
            infer["estimation_method"] = self.method
            ts = getattr(self, "tuning_selection_summary_", None)
            if isinstance(ts, dict):
                infer["trop_tuning_selection"] = ts
        except Exception as ex:
            print(
                f"[TROP inference_summary] FAILED phase=placebo_or_bootstrap "
                f"method={'placebo' if use_placebo else 'bootstrap'} error={ex!r}"
            )
            raise

        try:
            # Cumulative effect — align with summarize_effects total_incremental (single unit for CSV Absolute Effect)
            inc_t = float(base.get("total_incremental", np.nan))
            ate = float(inc_t) if np.isfinite(inc_t) else 0.0
            infer["ate"] = ate

            for key in ("ci_percentile", "ci_normal"):
                if key in infer:
                    lo, hi = infer[key]
                    if not (np.isfinite(lo) and np.isfinite(hi)):
                        infer[key] = (ate, ate)

            ci_p = infer.get("ci_percentile", (np.nan, np.nan))
            infer["cumulative_ci_brackets_ate"] = None
            infer["ci_invalid_effect_scale"] = False
            if isinstance(ci_p, (list, tuple)) and len(ci_p) >= 2 and np.isfinite(ci_p[0]) and np.isfinite(ci_p[1]):
                lo, hi = float(ci_p[0]), float(ci_p[1])
                infer["cumulative_ci"] = (lo, hi)
                tol = 1e-5 * max(abs(float(ate)), 1.0)
                brackets = lo <= hi and (lo - tol <= float(ate) <= hi + tol)
                infer["cumulative_ci_brackets_ate"] = bool(brackets)
                if not brackets:
                    infer["ci_invalid_effect_scale"] = True
                    print(
                        "\n[TROP CI ERROR] Cumulative CI does not bracket total_incremental (effect space): "
                        f"ate={float(ate):.6g}, ci=({lo:.6g}, {hi:.6g}) — blanking CI fields."
                    )
                    infer["ci_percentile"] = (np.nan, np.nan)
                    infer["ci_normal"] = (np.nan, np.nan)
                    infer["cumulative_ci"] = (np.nan, np.nan)
                else:
                    self._trop_ci_sanity_check(float(ate), lo, hi)

            # Task 2: Hard warning for invalid counterfactual_total
            cf_t = base.get("counterfactual_total", np.nan)
            invalid_cf = not np.isfinite(cf_t) or cf_t <= 0
            if invalid_cf:
                print("\n" + "!" * 60)
                print("[TROP WARNING] *** INVALID COUNTERFACTUAL TOTAL ***")
                print(f"  counterfactual_total = {cf_t} (non-finite or <= 0)")
                print("  relative_lift will be set to None. Do not interpret percentage.")
                print("!" * 60 + "\n")
                base["invalid_counterfactual_total"] = True
                base["relative_lift"] = None
            else:
                base["invalid_counterfactual_total"] = False

            # Phase 8: Other sanity warnings
            obs_t = base.get("observed_total", np.nan)
            inc_t2 = base.get("total_incremental", np.nan)
            pv = infer.get("p_value", np.nan)
            ci_p2 = infer.get("ci_percentile", (np.nan, np.nan))
            if not np.isfinite(obs_t):
                print(f"[TROP DEBUG] *** observed_total non-finite: {obs_t} ***")
            if not np.isfinite(inc_t2):
                print(f"[TROP DEBUG] *** total_incremental non-finite: {inc_t2} ***")
            if pv is None:
                print("[TROP DEBUG] *** p_value is None (degenerate bootstrap / placebo distribution) ***")
            elif not np.isfinite(pv) or (isinstance(pv, float) and np.isnan(pv)):
                print(f"[TROP DEBUG] *** p_value is NaN: {pv} ***")
            if len(ci_p2) >= 2 and (
                not np.isfinite(ci_p2[0]) or not np.isfinite(ci_p2[1]) or ci_p2[0] == ci_p2[1]
            ):
                print(f"[TROP DEBUG] *** ci_percentile invalid or identical: {ci_p2} ***")
        except Exception as ex:
            print(f"[TROP inference_summary] FAILED phase=merge_ci_and_effect_fields error={ex!r}")
            raise

        try:
            out = {**base, **infer}
            fd = getattr(self, "fit_diagnostics_", None)
            if fd is not None:
                out["fit_diagnostics"] = fd
            return out
        except Exception as ex:
            print(
                f"[TROP inference_summary] FAILED phase=final_assembly "
                f"(dict merge base+infer or fit_diagnostics attach) error={ex!r}"
            )
            raise

    def get_counterfactual_matrix(self) -> pd.DataFrame:
        if self.fit_result_ is None or self.wide_ is None:
            raise RuntimeError("Model not fitted.")
        return pd.DataFrame(
            self.fit_result_.counterfactual_matrix,
            index=self.wide_.index,
            columns=self.wide_.columns,
        )

    def get_effect_matrix(self) -> pd.DataFrame:
        if self.fit_result_ is None or self.wide_ is None:
            raise RuntimeError("Model not fitted.")
        return pd.DataFrame(
            self.fit_result_.tau_hat_matrix,
            index=self.wide_.index,
            columns=self.wide_.columns,
        )

    # ---------------------------------------------------------------------
    # Internal panel setup
    # ---------------------------------------------------------------------
    def _validate_panel(self):
        if self.panel_data is None or self.wide_ is None:
            raise RuntimeError("Call fit_data() first.")
        if self.wide_.isnull().all(axis=1).any():
            raise ValueError("Found unit(s) with all outcomes missing.")
        self.observed_mask_ = np.isfinite(self.wide_.values.astype(float))
        if len(self.panel_data.treated_units) == 0:
            raise ValueError("TROP requires at least one treated unit.")
        if len(self.panel_data.control_units) == 0:
            raise ValueError("TROP requires at least one control unit.")

    def _build_assignment_masks(self):
        """
        Build treatment mask over unit x time.
        Supports either the standard panel_exp convention of one start time per treated
        unit or an explicitly supplied binary unit x time treatment mask.
        """
        n_units, n_periods = self.wide_.shape

        if self.custom_treated_mask is not None:
            treated_mask = np.asarray(self.custom_treated_mask, dtype=bool)
            if treated_mask.shape != (n_units, n_periods):
                raise ValueError(
                    f"custom_treated_mask shape {treated_mask.shape} does not match panel shape {(n_units, n_periods)}."
                )
        else:
            treated_mask = np.zeros((n_units, n_periods), dtype=bool)
            treated_units = list(self.panel_data.treated_units)
            start_idx_map = {}
            for unit, start_idx in zip(treated_units, self.panel_data.treated_start_idxs):
                si = _trop_int_from_scalar(
                    start_idx,
                    field_name=f"treated_start_idxs[{unit!r}]",
                    function_name="_build_assignment_masks",
                    section="treatment_mask",
                    required=True,
                )
                assert si is not None
                start_idx_map[unit] = si

            for i, unit in enumerate(self.wide_.index):
                if unit in start_idx_map:
                    treated_mask[i, start_idx_map[unit] :] = True

        self.treated_mask_ = treated_mask
        self.control_mask_ = ~treated_mask

    # ---------------------------------------------------------------------
    # Weight construction from the paper's distance-decay proposal
    # ---------------------------------------------------------------------
    def _time_distance(self, treated_cols: np.ndarray) -> np.ndarray:
        n_t = self.wide_.shape[1]
        all_t = np.arange(n_t)
        d = np.min(np.abs(all_t[:, None] - treated_cols[None, :]), axis=1)
        if self.seasonal_period is not None and self.seasonal_period > 1:
            raw = np.abs(all_t[:, None] - treated_cols[None, :]) % self.seasonal_period
            seasonal_d = np.minimum(raw, self.seasonal_period - raw)
            d = np.minimum(d, np.min(seasonal_d, axis=1))
        return d.astype(float)

    def _unit_distance(self, treated_rows: np.ndarray) -> np.ndarray:
        """
        Root mean squared untreated-outcome gap between each unit and the nearest
        treated unit, using only observed untreated overlap and penalizing sparse overlap.
        """
        Y = self.wide_.values.astype(float)
        n_u, _ = Y.shape
        d = np.zeros(n_u, dtype=float)

        for i in range(n_u):
            candidate_dists = []
            for tr in treated_rows:
                overlap = self.control_mask_[i] & self.control_mask_[tr] & self.observed_mask_[i] & self.observed_mask_[tr]
                overlap_n = _trop_int_from_numpy_count(
                    overlap.sum(),
                    field_name="overlap_n(_unit_distance inner)",
                    function_name="_unit_distance",
                    section="donor_overlap",
                )
                if overlap_n < self.min_overlap_periods:
                    continue
                diff = Y[i, overlap] - Y[tr, overlap]
                rms = np.sqrt(np.mean(diff**2))
                overlap_penalty = np.sqrt(self.min_overlap_periods / overlap_n)
                candidate_dists.append(rms * overlap_penalty)
            d[i] = min(candidate_dists) if candidate_dists else np.inf

        d[treated_rows] = 0.0
        finite = np.isfinite(d)
        if not finite.all():
            max_finite = np.max(d[finite]) if finite.any() else 1.0
            d[~finite] = max_finite + 1.0
        return d

    def _make_unit_weights(self, lambda_unit: float) -> np.ndarray:
        treated_rows = np.where(self.treated_mask_.any(axis=1))[0]
        d_u = self._unit_distance(treated_rows)
        w = np.exp(-lambda_unit * d_u)
        # controls only carry balancing weight; treated units weight 0 in objective
        w[treated_rows] = 0.0
        return _safe_normalize(w)

    def _make_unit_weights_before_treated_zero(self, lambda_unit: float) -> np.ndarray:
        """Diagnostic: same distances as _make_unit_weights but do NOT zero treated rows (pre-threshold view)."""
        treated_rows = np.where(self.treated_mask_.any(axis=1))[0]
        d_u = self._unit_distance(treated_rows)
        w = np.exp(-lambda_unit * d_u)
        return _safe_normalize(w)

    def _make_time_weights(self, lambda_time: float) -> np.ndarray:
        treated_cols = np.where(self.treated_mask_.any(axis=0))[0]
        d_t = self._time_distance(treated_cols)
        w = np.exp(-lambda_time * d_t)
        # treated periods weight 0 in objective
        w[treated_cols] = 0.0
        return _safe_normalize(w)

    def _unit_distance_to_target(
        self, target_row: int, exclude_col: Optional[int] = None
    ) -> np.ndarray:
        """Distance from every unit j to target treated unit. Uses overlapping untreated periods."""
        Y = self.wide_.values.astype(float)
        n_u, n_t = Y.shape
        d = np.zeros(n_u, dtype=float)
        exclude_mask = np.zeros(n_t, dtype=bool)
        if exclude_col is not None:
            exclude_mask[exclude_col] = True

        for i in range(n_u):
            overlap = (
                self.control_mask_[i]
                & self.control_mask_[target_row]
                & self.observed_mask_[i]
                & self.observed_mask_[target_row]
                & ~exclude_mask
            )
            overlap_n = _trop_int_from_numpy_count(
                overlap.sum(),
                field_name="overlap_n(_unit_distance_to_target)",
                function_name="_unit_distance_to_target",
                section="donor_overlap",
            )
            if overlap_n < self.min_overlap_periods:
                d[i] = np.inf
                continue
            diff = Y[i, overlap] - Y[target_row, overlap]
            rms = np.sqrt(np.mean(diff**2))
            overlap_penalty = np.sqrt(self.min_overlap_periods / overlap_n)
            d[i] = rms * overlap_penalty

        d[target_row] = 0.0
        finite = np.isfinite(d)
        if not finite.all():
            max_finite = np.max(d[finite]) if finite.any() else 1.0
            d[~finite] = max_finite + 1.0
        return d

    def _time_distance_to_target(self, target_col: int) -> np.ndarray:
        """Absolute distance from every time period to target_col."""
        n_t = self.wide_.shape[1]
        all_t = np.arange(n_t, dtype=float)
        d = np.abs(all_t - target_col)
        if self.seasonal_period is not None and self.seasonal_period > 1:
            raw = np.abs(all_t - target_col) % self.seasonal_period
            seasonal_d = np.minimum(raw, self.seasonal_period - raw)
            d = np.minimum(d, seasonal_d)
        d[target_col] = 0.0
        return d

    def _make_unit_weights_for_target(
        self, target_row: int, exclude_col: Optional[int], lambda_unit: float
    ) -> np.ndarray:
        d_u = self._unit_distance_to_target(target_row, exclude_col)
        w = np.exp(-lambda_unit * d_u)
        w[target_row] = 0.0
        return _safe_normalize(w)

    def _make_time_weights_for_target(self, target_col: int, lambda_time: float) -> np.ndarray:
        d_t = self._time_distance_to_target(target_col)
        w = np.exp(-lambda_time * d_t)
        w[target_col] = 0.0
        return _safe_normalize(w)

    def _treated_row_patterns(self) -> list[np.ndarray]:
        treated_rows = np.where(self.treated_mask_.any(axis=1))[0]
        patterns = []
        seen = set()
        for tr in treated_rows:
            cols = np.where(self.treated_mask_[tr])[0]
            key = tuple(cols.tolist())
            if key and key not in seen:
                seen.add(key)
                patterns.append(cols)
        if not patterns:
            raise ValueError("Need at least one treated timing pattern.")
        return patterns

    def _recenter_components(self, alpha: np.ndarray, delta: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        unit_weights = np.maximum(self._make_unit_weights(0.0), EPS)
        time_weights = np.maximum(self._make_time_weights(0.0), EPS)
        return self._recenter_components_with_weights(alpha, delta, unit_weights, time_weights)

    def _recenter_components_with_weights(
        self,
        alpha: np.ndarray,
        delta: np.ndarray,
        unit_weights: np.ndarray,
        time_weights: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        unit_weights = np.maximum(np.asarray(unit_weights, dtype=float), EPS)
        time_weights = np.maximum(np.asarray(time_weights, dtype=float), EPS)
        alpha_mean = float(np.average(alpha.ravel(), weights=unit_weights))
        alpha = alpha - alpha_mean
        delta = delta + alpha_mean
        delta_mean = float(np.average(delta.ravel(), weights=time_weights))
        delta = delta - delta_mean
        # Task 3: Store for recentering debug (weighted means removed)
        if not hasattr(self, "_recenter_debug"):
            self._recenter_debug = {}
        self._recenter_debug["alpha_mean_removed"] = alpha_mean
        self._recenter_debug["delta_mean_removed"] = delta_mean
        self._recenter_debug["L_mean_removed"] = 0.0  # L is not recentered
        return alpha, delta

    # ---------------------------------------------------------------------
    # Core weighted low-rank optimization
    # ---------------------------------------------------------------------
    def _solve_weighted_low_rank(
        self,
        Y: np.ndarray,
        W: np.ndarray,
        recenter_unit_weights: np.ndarray,
        recenter_time_weights: np.ndarray,
        lambda_nuclear: float,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, int, bool]:
        """
        Solve weighted low-rank objective. Caller constructs W (zero on treated/missing).
        Returns alpha, delta, L, objective_value, iterations, converged.
        """
        Y_filled = np.nan_to_num(Y, nan=0.0)
        n_u, n_t = Y.shape
        alpha = np.zeros((n_u, 1), dtype=float)
        delta = np.zeros((1, n_t), dtype=float)
        L = np.zeros((n_u, n_t), dtype=float)
        step = self.step_size
        converged = False
        prev_obj = np.inf

        # Treated-post vs control-pre masks (for L-gradient fix and debug only; W unchanged).
        tp_mask: Optional[np.ndarray] = None
        cp_mask: Optional[np.ndarray] = None
        tm = getattr(self, "treated_mask_", None)
        ts = getattr(self, "treated_start_idx_", None)
        if tm is not None and ts is not None and tm.shape == (n_u, n_t):
            post_c = np.arange(n_t) >= int(ts)
            tp_mask = tm & np.broadcast_to(post_c, tm.shape)
            ctrl_rows = ~tm.any(axis=1)
            pre_c = np.arange(n_t) < int(ts)
            cp_mask = ctrl_rows[:, np.newaxis] & pre_c[np.newaxis, :]

        for it in range(1, self.max_iter + 1):
            R = Y_filled - L
            for i in range(n_u):
                wi = W[i, :]
                denom = wi.sum()
                if denom > EPS:
                    alpha[i, 0] = np.sum(wi * (R[i, :] - delta.ravel())) / denom
            for t in range(n_t):
                wt = W[:, t]
                denom = wt.sum()
                if denom > EPS:
                    delta[0, t] = np.sum(wt * (R[:, t] - alpha.ravel())) / denom

            alpha, delta = self._recenter_components_with_weights(
                alpha, delta, recenter_unit_weights, recenter_time_weights
            )

            residual = alpha + delta + L - Y_filled
            # Weighted gradient for the fitted loss on donor/observed cells.
            grad = W * residual
            # W is zero on treated-post by design, so W*residual gives no L update there and L
            # stays identically zero on those cells. The nuclear penalty still applies to the
            # full matrix; L must be free to take nonzero values on treated-post for mu_hat.
            if tp_mask is not None:
                grad = np.where(tp_mask, residual, grad)
            accepted = False
            local_step = step
            for _ in range(20):
                eff_l_step = local_step * float(self.l_step_multiplier)
                Z = L - eff_l_step * grad
                U, s, Vt = np.linalg.svd(Z, full_matrices=False)
                s_thr = _soft_threshold_singular_values(s, local_step * lambda_nuclear)
                L_new = (U * s_thr) @ Vt
                obj_new = self._objective(Y_filled, W, alpha, delta, L_new, lambda_nuclear)
                quad = self._objective_quadratic_majorizer(
                    Y_filled, W, alpha, delta, L, L_new, grad, lambda_nuclear, local_step
                )
                if obj_new <= quad + 1e-8:
                    accepted = True
                    L = L_new
                    step = local_step * 1.05
                    break
                local_step *= 0.5
            if not accepted:
                L = L_new
                step = local_step

            if self.verbose:
                _L = L
                gmin, gmax = float(np.min(_L)), float(np.max(_L))
                tpmn, tpmx = float("nan"), float("nan")
                cpmn, cpmx = float("nan"), float("nan")
                if tp_mask is not None and tp_mask.any():
                    tpmn, tpmx = float(np.min(_L[tp_mask])), float(np.max(_L[tp_mask]))
                if cp_mask is not None and cp_mask.any():
                    cpmn, cpmx = float(np.min(_L[cp_mask])), float(np.max(_L[cp_mask]))
                print(
                    f"[TROP L post-update] it={it} L[all] min={gmin:.8g} max={gmax:.8g} | "
                    f"L[treated_post] min={tpmn:.8g} max={tpmx:.8g} | "
                    f"L[control_pre] min={cpmn:.8g} max={cpmx:.8g}"
                )

            obj = self._objective(Y_filled, W, alpha, delta, L, lambda_nuclear)
            rel_impr = abs(prev_obj - obj) / max(abs(prev_obj), 1.0)
            if self.verbose:
                fro_l = float(np.linalg.norm(L, "fro"))
                _, s_it, _ = np.linalg.svd(L, full_matrices=False)
                tau_it = float(step) * float(lambda_nuclear)
                s_thr_it = _soft_threshold_singular_values(s_it, tau_it)
                n_sv_pos = int(np.sum(s_thr_it > 0))
                lr_min_it = lr_max_it = float("nan")
                tm = getattr(self, "treated_mask_", None)
                ts = getattr(self, "treated_start_idx_", None)
                if tm is not None and ts is not None:
                    post_c = np.arange(n_t) >= int(ts)
                    tp = tm & np.broadcast_to(post_c, tm.shape)
                    if tp.any():
                        Ltp = L[tp]
                        lr_min_it, lr_max_it = float(np.min(Ltp)), float(np.max(Ltp))
                print(
                    f"[TROP L iter] it={it} objective={obj:.8g} ||L||_F={fro_l:.8g} "
                    f"lr_treated_post_min={lr_min_it} lr_treated_post_max={lr_max_it} "
                    f"n_nonzero_sv_after_threshold={n_sv_pos}"
                )
            if rel_impr < self.tol:
                converged = True
                prev_obj = obj
                break
            prev_obj = obj

        # Final L: singular values before / after soft-threshold (same tau as diagnostic below)
        s_final = np.linalg.svd(L, full_matrices=False, compute_uv=False)
        tau_final = float(step) * float(lambda_nuclear)
        s_thr_final = _soft_threshold_singular_values(s_final, tau_final)
        n_nz_sv_final = int(np.sum(s_thr_final > 0))
        if self.verbose:
            print(
                "[TROP L fit] singular_values_before_threshold:",
                np.array2string(s_final, precision=8, separator=", ", max_line_width=240),
            )
            print(
                f"[TROP L fit] singular_values_after_threshold (tau={tau_final:.8g}):",
                np.array2string(s_thr_final, precision=8, separator=", ", max_line_width=240),
            )

        # Task 2: Treated row alpha support - cells and weight mass contributing to alpha update
        # Task 4: Low-rank diagnostics (s, s_thr, norm L)
        if self.method == "global":
            self._solver_debug_diag = {}
            treated_rows = np.where(self.treated_mask_.any(axis=1))[0]
            for i in treated_rows:
                wi = W[i, :]
                n_support = _trop_int_from_numpy_count(
                    (wi > EPS).sum(),
                    field_name=f"treated_row_{int(i)}_n_support",
                    function_name="_solve_weighted_low_rank",
                    section="solver_diagnostics",
                )
                weight_mass = float(wi.sum())
                self._solver_debug_diag[f"treated_row_{i}_n_support"] = n_support
                self._solver_debug_diag[f"treated_row_{i}_weight_mass"] = weight_mass
            self._solver_debug_diag["treated_rows"] = treated_rows.tolist()
            self._solver_debug_diag["sv_before_threshold"] = s_final.copy()
            self._solver_debug_diag["sv_after_threshold"] = s_thr_final.copy()
            self._solver_debug_diag["L_frobenius_norm"] = float(np.linalg.norm(L, "fro"))
            self._solver_debug_diag["n_nonzero_singular_values_after_threshold"] = n_nz_sv_final

        return alpha, delta, L, float(prev_obj), it, converged

    def _fit_global_for_params(
        self,
        lambda_unit: float,
        lambda_time: float,
        lambda_nuclear: float,
    ) -> TROPFitResult:
        """Solve the weighted TROP objective on observed untreated cells (global mode)."""
        Y = self.wide_.values.astype(float)
        n_u, n_t = Y.shape
        W_u = self._make_unit_weights(lambda_unit)
        W_t = self._make_time_weights(lambda_time)
        W = np.outer(W_u, W_t)
        W[~self.observed_mask_] = 0.0
        W[self.treated_mask_] = 0.0

        # --- Donor / weight diagnostics (global) — independent of solver -------------
        # Design note: _make_unit_weights() sets W_u[treated_rows]=0 so treated units do not
        # receive unit-balancing weight. Then W[i,:]=0 for treated rows i — legacy
        # "treated_row_i_n_support" counted positive W on those rows and was ~always 0.
        # Feasibility should use control-unit donor mass (n_control_units_positive_unit_weight).
        control_unit_mask = ~self.treated_mask_.any(axis=1)
        n_ctrl_pos = _trop_int_from_numpy_count(
            np.sum(W_u[control_unit_mask] > EPS),
            field_name="n_control_units_positive_unit_weight",
            function_name="_fit_global_for_params",
            section="donor_support_diagnostics",
        )
        donor_mass = float(np.sum(W_u[control_unit_mask]))
        W_u_pre = self._make_unit_weights_before_treated_zero(lambda_unit)
        W_pre = np.outer(W_u_pre, W_t)
        W_pre[~self.observed_mask_] = 0.0
        treated_rows_pre = np.where(self.treated_mask_.any(axis=1))[0]
        _EPS_RAW = 1e-16
        _raw_fin: dict[str, Any] = {}
        for i in treated_rows_pre:
            raw_n = _trop_int_from_numpy_count(
                (W_pre[i, :] > _EPS_RAW).sum(),
                field_name=f"treated_row_{int(i)}_n_nonzero_raw_outer",
                function_name="_fit_global_for_params",
                section="donor_weight_threshold_compare",
            )
            fin_n = _trop_int_from_numpy_count(
                (W[i, :] > EPS).sum(),
                field_name=f"treated_row_{int(i)}_n_nonzero_after_masks",
                function_name="_fit_global_for_params",
                section="donor_weight_threshold_compare",
            )
            _raw_fin[f"treated_row_{int(i)}_n_nonzero_raw_outer"] = raw_n
            _raw_fin[f"treated_row_{int(i)}_n_nonzero_after_masks"] = fin_n
        if self.debug_donor_weights:
            print("[TROP DEBUG donor] W_u after zeroing treated (used in fit):")
            for idx, name in enumerate(self.wide_.index):
                print(f"  unit[{idx}] {name!s}: W_u={float(W_u[idx]):.8g}  W_u_pre={float(W_u_pre[idx]):.8g}")
            print(f"[TROP DEBUG donor] W_t min={float(np.min(W_t)):.6g} max={float(np.max(W_t)):.6g} sum={float(np.sum(W_t)):.6g}")
            print(
                f"[TROP DEBUG donor] controls: n_positive_Wu={n_ctrl_pos} mass={donor_mass:.6g} "
                f"(treated-row W[i,:] is all-zero by construction because W_u[treated]=0)"
            )
            for i in treated_rows_pre:
                print(
                    f"  treated_row_{i}: raw_outer_n>{_EPS_RAW}={_raw_fin.get(f'treated_row_{int(i)}_n_nonzero_raw_outer')}, "
                    f"after_treated_cell_mask_n>{EPS}={_raw_fin.get(f'treated_row_{int(i)}_n_nonzero_after_masks')}"
                )
        if self.diagnostic_weight_threshold_compare:
            print("[TROP diagnostic] raw (1e-16) vs masked treated-cell counts per treated row:", _raw_fin)

        recenter_u = np.maximum(self._make_unit_weights(0.0), EPS)
        recenter_t = np.maximum(self._make_time_weights(0.0), EPS)
        alpha, delta, L, obj_val, it, converged = self._solve_weighted_low_rank(
            Y, W, recenter_u, recenter_t, lambda_nuclear
        )

        Y_filled = np.nan_to_num(Y, nan=0.0)
        mu_hat = alpha + delta + L

        # Task 1-4, 8: FE/low-rank diagnostics (before clipping)
        post_cols = np.arange(n_t) >= self.treated_start_idx_
        treated_post = self.treated_mask_ & np.broadcast_to(post_cols, self.treated_mask_.shape)
        treated_rows = np.where(self.treated_mask_.any(axis=1))[0]
        # fit_diagnostics_ for Task 8 return
        self.fit_diagnostics_ = {
            "donor_support_min": n_ctrl_pos,
            "donor_unit_weight_mass_on_controls": donor_mass,
            "n_control_units_positive_unit_weight": n_ctrl_pos,
            "donor_support_zero_any": bool(n_ctrl_pos == 0 or donor_mass <= EPS * max(n_u, 1)),
            "note_global_treated_row_W_row_zero_by_design": True,
        }
        self.fit_diagnostics_.update(_raw_fin)

        # Task 1: Alpha/delta summary
        alpha_flat = alpha.ravel()
        delta_flat = delta.ravel()
        print(f"[TROP FE] alpha (all rows): min={float(np.min(alpha_flat)):.4g} max={float(np.max(alpha_flat)):.4g}")
        if len(treated_rows) > 0:
            tr_alpha = alpha_flat[treated_rows]
            print(f"[TROP FE] treated-row alpha: {tr_alpha}")
            self.fit_diagnostics_["treated_row_alpha"] = [float(x) for x in tr_alpha]
        delta_post = delta_flat[self.treated_start_idx_ :]
        print(f"[TROP FE] delta (all cols): min={float(np.min(delta_flat)):.4g} max={float(np.max(delta_flat)):.4g}")
        if len(delta_post) > 0:
            print(f"[TROP FE] treated-post delta: min={float(np.min(delta_post)):.4g} max={float(np.max(delta_post)):.4g}")
            self.fit_diagnostics_["treated_post_delta_min"] = float(np.min(delta_post))
            self.fit_diagnostics_["treated_post_delta_max"] = float(np.max(delta_post))

        if treated_post.any():
            fe_part = alpha + delta
            fe_post = fe_part[treated_post]
            lr_post = L[treated_post]
            full_post = mu_hat[treated_post]
            fe_min, fe_max = float(np.min(fe_post)), float(np.max(fe_post))
            print(f"[TROP DECOMP] FE-part (alpha+delta) treated post: min={fe_min:.4g} max={fe_max:.4g}")
            print(f"[TROP DECOMP] low-rank part (L) treated post: min={float(np.min(lr_post)):.4g} max={float(np.max(lr_post)):.4g}")
            print(f"[TROP DECOMP] full prediction (mu_hat) treated post: min={float(np.min(full_post)):.4g} max={float(np.max(full_post)):.4g}")
            self.fit_diagnostics_["fe_treated_post_min"] = fe_min
            self.fit_diagnostics_["fe_treated_post_max"] = fe_max
            self.fit_diagnostics_["lr_treated_post_min"] = float(np.min(lr_post))
            self.fit_diagnostics_["lr_treated_post_max"] = float(np.max(lr_post))
            self.fit_diagnostics_["full_treated_post_min"] = float(np.min(full_post))
            self.fit_diagnostics_["full_treated_post_max"] = float(np.max(full_post))

        # Task 3: Recentering debug (weighted means removed)
        rc = getattr(self, "_recenter_debug", {})
        am = rc.get("alpha_mean_removed", np.nan)
        dm = rc.get("delta_mean_removed", np.nan)
        print(f"[TROP RECENTER] alpha weighted mean removed: {am:.4g}")
        print(f"[TROP RECENTER] delta weighted mean removed: {dm:.4g}")
        self.fit_diagnostics_["alpha_mean_removed"] = am
        self.fit_diagnostics_["delta_mean_removed"] = dm

        # Task 2, 4: Merge solver debug into fit_diagnostics_
        sbd = getattr(self, "_solver_debug_diag", {})
        for k, v in sbd.items():
            if isinstance(v, np.ndarray):
                self.fit_diagnostics_[k] = v.tolist()
            else:
                self.fit_diagnostics_[k] = v

        # Task 3: "Zero support" — use donor pool on control units, not W[i,:] on treated rows.
        # In global mode W[treated_row, :] is identically zero because W_u[treated]=0 by design
        # (treated units do not enter the weighted loss on their own row); legacy n_support on
        # treated rows was misleading.
        _tr_list = sbd.get("treated_rows", [])
        weak_donor = (n_ctrl_pos < self.min_donor_support) or (donor_mass <= EPS * max(n_u, 1))
        self.fit_diagnostics_["unstable_zero_support"] = bool(weak_donor)
        if weak_donor:
            import warnings
            warnings.warn(
                f"TROP weak donor pool: n_control_units_positive_unit_weight={n_ctrl_pos} "
                f"(min_donor_support={self.min_donor_support}), donor_unit_weight_mass_on_controls={donor_mass:.6g}. "
                "Counterfactual / inference may be unreliable.",
                UserWarning,
                stacklevel=2,
            )
        lr_fro = float(sbd.get("L_frobenius_norm", np.nan))
        flat_lr = bool(np.isfinite(lr_fro) and lr_fro <= EPS * max(n_u * n_t, 1))

        counterfactual = mu_hat.copy()
        if self.enforce_nonnegative_counterfactual:
            counterfactual = np.maximum(counterfactual, 0.0)
        tau_hat = np.zeros_like(Y_filled)
        tau_hat[self.treated_mask_ & self.observed_mask_] = (
            Y_filled[self.treated_mask_ & self.observed_mask_]
            - counterfactual[self.treated_mask_ & self.observed_mask_]
        )

        if treated_post.any():
            cf_tp = counterfactual[treated_post]
            cf_pmin = float(np.min(cf_tp))
            cf_pmax = float(np.max(cf_tp))
            self.fit_diagnostics_["cf_post_min"] = cf_pmin
            self.fit_diagnostics_["cf_post_max"] = cf_pmax
            cf_range = abs(cf_pmax - cf_pmin)
            scale = max(abs(cf_pmax), abs(cf_pmin), 1.0) if np.isfinite(cf_pmin) and np.isfinite(cf_pmax) else 1.0
            flat_cf_range = bool(cf_range < self.flat_cf_rel_tol * scale)
            self.fit_diagnostics_["flat_counterfactual"] = bool(flat_lr or flat_cf_range)
        else:
            self.fit_diagnostics_["flat_counterfactual"] = bool(flat_lr)

        return TROPFitResult(
            counterfactual_matrix=counterfactual,
            tau_hat_matrix=tau_hat,
            lambda_unit=float(lambda_unit),
            lambda_time=float(lambda_time),
            lambda_nuclear=float(lambda_nuclear),
            unit_weights=W_u,
            time_weights=W_t,
            effective_weight_matrix=W,
            alpha=alpha.copy(),
            delta=delta.copy(),
            low_rank=L.copy(),
            objective_value=obj_val,
            iterations=it,
            converged=converged,
            method="global",
            cv_mode=self.cv_mode,
        )

    def _fit_for_params(
        self,
        lambda_unit: float,
        lambda_time: float,
        lambda_nuclear: float,
    ) -> TROPFitResult:
        """Dispatcher: route to global or local fit."""
        if self.method == "global":
            return self._fit_global_for_params(lambda_unit, lambda_time, lambda_nuclear)
        if self.method == "local":
            return self._fit_local_for_params(lambda_unit, lambda_time, lambda_nuclear)
        raise ValueError(f"method must be 'global' or 'local', got {self.method!r}")

    def _fit_local_cell(
        self,
        target_row: int,
        target_col: int,
        lambda_unit: float,
        lambda_time: float,
        lambda_nuclear: float,
    ) -> dict:
        """Fit one treated cell with target-specific weights. Returns diagnostics dict."""
        Y = self.wide_.values.astype(float)
        n_u, n_t = Y.shape

        W_u = self._make_unit_weights_for_target(target_row, exclude_col=target_col, lambda_unit=lambda_unit)
        W_t = self._make_time_weights_for_target(target_col, lambda_time)
        W = np.outer(W_u, W_t)
        W[~self.observed_mask_] = 0.0
        W[self.treated_mask_] = 0.0
        W[target_row, target_col] = 0.0

        recenter_u = np.maximum(W_u.copy(), EPS)
        recenter_t = np.maximum(W_t.copy(), EPS)
        alpha, delta, L, obj_val, it, converged = self._solve_weighted_low_rank(
            Y, W, recenter_u, recenter_t, lambda_nuclear
        )

        Y_filled = np.nan_to_num(Y, nan=0.0)
        mu_hat = alpha + delta + L
        counterfactual = float(mu_hat[target_row, target_col])
        observed = float(Y_filled[target_row, target_col])
        tau_hat = observed - counterfactual

        return {
            "counterfactual": counterfactual,
            "tau_hat": tau_hat,
            "alpha": alpha,
            "delta": delta,
            "low_rank": L,
            "objective_value": obj_val,
            "iterations": it,
            "converged": converged,
            "unit_weights": W_u,
            "time_weights": W_t,
        }

    def _fit_local_for_params(
        self,
        lambda_unit: float,
        lambda_time: float,
        lambda_nuclear: float,
    ) -> TROPFitResult:
        """Per-cell local fitting over all treated observed cells."""
        Y = self.wide_.values.astype(float)
        n_u, n_t = Y.shape
        Y_filled = np.nan_to_num(Y, nan=0.0)

        treated_obs = self.treated_mask_ & self.observed_mask_
        n_treated_cells = _trop_int_from_numpy_count(
            treated_obs.sum(),
            field_name="n_treated_cells",
            function_name="_fit_local_for_params",
            section="local_fit",
        )
        if self.local_max_treated_cells is not None and n_treated_cells > self.local_max_treated_cells:
            raise ValueError(
                f"local_max_treated_cells={self.local_max_treated_cells} exceeded "
                f"({n_treated_cells} treated cells). Increase limit or use global mode."
            )

        counterfactual_matrix = Y_filled.copy()
        tau_hat_matrix = np.zeros_like(Y_filled)
        cell_converged = np.full((n_u, n_t), np.nan, dtype=float)
        cell_iterations = np.full((n_u, n_t), np.nan, dtype=float)
        cell_objective = np.full((n_u, n_t), np.nan, dtype=float)

        treated_rows, treated_cols = np.where(treated_obs)
        for idx in range(len(treated_rows)):
            tr = _trop_int_from_scalar(
                treated_rows[idx],
                field_name=f"treated_rows[{idx}]",
                function_name="_fit_local_for_params",
                section="local_fit_indices",
                required=True,
            )
            tc = _trop_int_from_scalar(
                treated_cols[idx],
                field_name=f"treated_cols[{idx}]",
                function_name="_fit_local_for_params",
                section="local_fit_indices",
                required=True,
            )
            assert tr is not None and tc is not None
            cell_res = self._fit_local_cell(tr, tc, lambda_unit, lambda_time, lambda_nuclear)
            counterfactual_matrix[tr, tc] = cell_res["counterfactual"]
            tau_hat_matrix[tr, tc] = cell_res["tau_hat"]
            cell_converged[tr, tc] = float(cell_res["converged"])
            cell_iterations[tr, tc] = float(cell_res["iterations"])
            cell_objective[tr, tc] = cell_res["objective_value"]

        if self.enforce_nonnegative_counterfactual:
            counterfactual_matrix = np.maximum(counterfactual_matrix, 0.0)
            tau_hat_matrix[treated_obs] = Y_filled[treated_obs] - counterfactual_matrix[treated_obs]

        return TROPFitResult(
            counterfactual_matrix=counterfactual_matrix,
            tau_hat_matrix=tau_hat_matrix,
            lambda_unit=float(lambda_unit),
            lambda_time=float(lambda_time),
            lambda_nuclear=float(lambda_nuclear),
            unit_weights=None,
            time_weights=None,
            effective_weight_matrix=None,
            alpha=None,
            delta=None,
            low_rank=None,
            objective_value=float(np.nanmean(cell_objective[treated_obs])),
            iterations=(
                _trop_int_from_scalar(
                    np.nansum(cell_iterations[treated_obs]),
                    field_name="iterations(nansum cell_iterations)",
                    function_name="_fit_local_for_params",
                    section="local_fit_summary",
                    required=False,
                    default=0,
                )
                or 0
            ),
            converged=bool(np.nanmin(cell_converged[treated_obs])),
            method="local",
            cell_converged_matrix=cell_converged,
            cell_iterations_matrix=cell_iterations,
            cell_objective_matrix=cell_objective,
            cv_mode=self.cv_mode,
        )

    def _objective(self, Y, W, alpha, delta, L, lambda_nuclear):
        resid = Y - alpha - delta - L
        loss = 0.5 * np.sum(W * resid**2)
        s = np.linalg.svd(L, full_matrices=False, compute_uv=False)
        penalty = lambda_nuclear * np.sum(s)
        return float(loss + penalty)

    def _objective_quadratic_majorizer(self, Y, W, alpha, delta, L_old, L_new, grad, lambda_nuclear, step):
        resid_old = Y - alpha - delta - L_old
        loss_old = 0.5 * np.sum(W * resid_old**2)
        diff = L_new - L_old
        maj = loss_old + np.sum(grad * diff) + (0.5 / step) * np.sum(diff**2)
        s = np.linalg.svd(L_new, full_matrices=False, compute_uv=False)
        penalty = lambda_nuclear * np.sum(s)
        return float(maj + penalty)

    # ---------------------------------------------------------------------
    # Cross-validation from the paper + stability-first tuning
    # ---------------------------------------------------------------------
    def _min_treated_row_n_support(self) -> int:
        """Prefer donor pool on control units (global); legacy treated-row W counts are misleading."""
        fd = getattr(self, "fit_diagnostics_", {}) or {}
        for key in ("n_control_units_positive_unit_weight", "donor_support_min"):
            v = fd.get(key)
            if v is not None:
                iv = _trop_int_from_scalar(
                    v,
                    field_name=key,
                    function_name="_min_treated_row_n_support",
                    section="fit_diagnostics",
                    required=False,
                    default=None,
                )
                if iv is not None:
                    return iv
        sbd = getattr(self, "_solver_debug_diag", {}) or {}
        tr = sbd.get("treated_rows", [])
        if not tr:
            return 0
        ns_list: List[int] = []
        for i in tr:
            kk = f"treated_row_{i}_n_support"
            raw = sbd.get(kk, 0)
            iv = _trop_int_from_scalar(
                raw,
                field_name=kk,
                function_name="_min_treated_row_n_support",
                section="_solver_debug_diag",
                required=False,
                default=None,
            )
            if iv is not None:
                ns_list.append(iv)
        return min(ns_list) if ns_list else 0

    def _compute_stability_score(self, min_ns: int, cf_post_min: float, cf_post_max: float) -> float:
        """Higher is more stable: reward donor breadth and non-flat post counterfactual."""
        cf_range = abs(float(cf_post_max) - float(cf_post_min))
        return float(min_ns) + float(np.log1p(cf_range + EPS))

    def _reference_effects_ok(self, ate: float) -> bool:
        ref = self.reference_effects
        if not ref:
            return True
        # Reference-dict keys: canonical estimator names plus legacy aliases for older configs.
        for key in (
            "ridge",
            "augsynth",
            "Ridge",
            "AugSynthCVXPY",
            "SyntheticControlCVXPY",
            "TBRRidge",
            "AugSynth",
            "SyntheticControl",
        ):
            v = ref.get(key)
            if v is None or not np.isfinite(v) or abs(float(v)) < 1e-12:
                continue
            if np.sign(float(ate)) != np.sign(float(v)):
                return False
        return True

    def _extended_selection_invalid(
        self,
        ate: float,
        ci_lo: float,
        ci_hi: float,
        placebo_std: float,
    ) -> bool:
        """Reject CI scale mismatch, huge placebo noise, etc. (when inference columns are available)."""
        if not (np.isfinite(ate) and np.isfinite(ci_lo) and np.isfinite(ci_hi)):
            return True
        width = abs(float(ci_hi) - float(ci_lo))
        eff = abs(float(ate))
        if eff > 1e-12:
            ratio = width / eff
            if ratio > self.ci_width_ratio_max or ratio < self.ci_width_ratio_min:
                return True
        if self.max_placebo_std_selection is not None and np.isfinite(placebo_std):
            if float(placebo_std) > float(self.max_placebo_std_selection):
                return True
        if not self._reference_effects_ok(ate):
            return True
        return False

    def _tune_parameters(self) -> dict:
        if self.disable_internal_tuning:
            gu, gt, gn = self.lambda_unit_grid, self.lambda_time_grid, self.lambda_nuclear_grid
            if len(gu) != 1 or len(gt) != 1 or len(gn) != 1:
                raise ValueError(
                    "disable_internal_tuning=True requires singleton lambda grids "
                    "(lambda_unit_grid, lambda_time_grid, lambda_nuclear_grid each of length 1)."
                )
            print("[TROP] Internal tuning disabled — using fixed lambdas")
            out = {
                "lambda_unit": float(gu[0]),
                "lambda_time": float(gt[0]),
                "lambda_nuclear": float(gn[0]),
            }
            self.cv_history_.append(
                {
                    **out,
                    "cv_score": float("nan"),
                    "stage": "disable_internal_tuning",
                    "cv_mode": self.cv_mode,
                }
            )
            return out
        if self.trop_tuning_mode == "legacy_coordinate_descent":
            return self._tune_parameters_legacy()
        if self.method != "global":
            warnings.warn(
                "TROP stability_first tuning is designed for method='global'. "
                "Falling back to legacy_coordinate_descent for local mode.",
                UserWarning,
                stacklevel=2,
            )
            return self._tune_parameters_legacy()
        return self._tune_parameters_stability_first()

    def _tune_parameters_legacy(self) -> dict:
        """
        Leave-one-out placebo-style cross-validation inspired by the paper.

        Strategy:
        1) hold fixed two params and grid-search the third to get upper bounds
        2) cycle through (lambda_unit, lambda_time, lambda_nuclear)
        3) objective: average placebo squared treatment effect on control units
           treated in their own pseudo-treated periods after leaving their outcomes out
        """
        current = {
            "lambda_unit": self.lambda_unit_grid[min(1, len(self.lambda_unit_grid) - 1)],
            "lambda_time": self.lambda_time_grid[min(1, len(self.lambda_time_grid) - 1)],
            "lambda_nuclear": self.lambda_nuclear_grid[min(1, len(self.lambda_nuclear_grid) - 1)],
        }

        # warm-start one-dimensional scans to mimic paper's staged search
        for key, grid in [
            ("lambda_unit", self.lambda_unit_grid),
            ("lambda_time", self.lambda_time_grid),
            ("lambda_nuclear", self.lambda_nuclear_grid),
        ]:
            scores = []
            for val in grid:
                trial = current.copy()
                trial[key] = val
                score = self._cv_score(**trial)
                self.cv_history_.append({**trial, "cv_score": score, "stage": f"init_{key}", "cv_mode": self.cv_mode})
                scores.append((score, val))
            current[key] = min(scores, key=lambda x: x[0])[1]

        # coordinate descent cycling
        for cycle in range(self.cv_max_cycles):
            updated = False
            for key, grid in [
                ("lambda_unit", self.lambda_unit_grid),
                ("lambda_time", self.lambda_time_grid),
                ("lambda_nuclear", self.lambda_nuclear_grid),
            ]:
                scores = []
                for val in grid:
                    trial = current.copy()
                    trial[key] = val
                    score = self._cv_score(**trial)
                    self.cv_history_.append({**trial, "cv_score": score, "stage": f"cycle_{cycle}_{key}", "cv_mode": self.cv_mode})
                    scores.append((score, val))
                best_val = min(scores, key=lambda x: x[0])[1]
                if best_val != current[key]:
                    updated = True
                    current[key] = best_val
            if not updated:
                break
        return current

    def _tune_parameters_stability_first(self) -> dict:
        """
        Full Cartesian grid over lambdas; discard invalid fits; rank by CV then stability;
        optionally apply extended checks (CI scale, placebo noise, reference effects).
        """
        rows: List[dict[str, Any]] = []
        grid = list(
            itertools.product(self.lambda_unit_grid, self.lambda_time_grid, self.lambda_nuclear_grid)
        )
        n_grid = len(grid)
        print(
            f"[TROP tuning] stability_first: evaluating {n_grid} configurations "
            f"(|unit|×|time|×|nuclear| = {len(self.lambda_unit_grid)}×{len(self.lambda_time_grid)}×{len(self.lambda_nuclear_grid)})"
        )

        for lu, lt, ln in grid:
            lu, lt, ln = float(lu), float(lt), float(ln)
            pdict = {"lambda_unit": lu, "lambda_time": lt, "lambda_nuclear": ln}
            fit_res = self._fit_for_params(lu, lt, ln)
            self.fit_result_ = fit_res
            summ = self.summarize_effects()
            fd = getattr(self, "fit_diagnostics_", {}) or {}
            unstable = bool(fd.get("unstable_zero_support", False))
            min_ns = self._min_treated_row_n_support()
            cf_min = float(summ.get("cf_post_min", np.nan))
            cf_max = float(summ.get("cf_post_max", np.nan))
            abs_effect = float(summ.get("total_incremental", np.nan))
            cf_range = abs(cf_max - cf_min) if np.isfinite(cf_min) and np.isfinite(cf_max) else 0.0
            scale = max(abs(cf_max), abs(cf_min), 1.0) if np.isfinite(cf_max) and np.isfinite(cf_min) else 1.0
            flat_cf = cf_range < self.flat_cf_rel_tol * scale

            hard_invalid = unstable or (min_ns < self.min_donor_support) or flat_cf
            stab = self._compute_stability_score(min_ns, cf_min, cf_max)

            cv_score = float("inf")
            if not hard_invalid:
                cv_score = self._cv_score(lu, lt, ln)

            p_val = np.nan
            ci_lo = np.nan
            ci_hi = np.nan
            p_std = np.nan
            if not hard_invalid and self.tuning_placebo_max_fits > 0:
                try:
                    inf = self._placebo_variance_with_params(
                        pdict, max_placebo_fits=self.tuning_placebo_max_fits
                    )
                    pv_raw = inf.get("p_value", np.nan)
                    if pv_raw is None:
                        p_val = np.nan
                    else:
                        try:
                            p_val = float(pv_raw)
                        except (TypeError, ValueError):
                            p_val = np.nan
                    cum_ci = inf.get("cumulative_ci") or inf.get("ci_percentile")
                    if cum_ci is not None and isinstance(cum_ci, (list, tuple)) and len(cum_ci) >= 2:
                        ci_lo, ci_hi = float(cum_ci[0]), float(cum_ci[1])
                    else:
                        cn = inf.get("ci_normal", (np.nan, np.nan))
                        ci_lo = float(cn[0]) if cn and len(cn) > 0 else np.nan
                        ci_hi = float(cn[1]) if cn and len(cn) > 1 else np.nan
                    p_std = float(inf.get("placebo_std", np.nan))
                except Exception as ex:  # noqa: BLE001
                    if self.verbose:
                        print(f"[TROP tuning] placebo inference failed for {pdict}: {ex}")

            ext_invalid = False
            if not hard_invalid:
                if np.isfinite(p_val):
                    ext_invalid = self._extended_selection_invalid(abs_effect, ci_lo, ci_hi, p_std)
                elif self.reference_effects:
                    ext_invalid = not self._reference_effects_ok(abs_effect)

            row = {
                "lambda_unit": lu,
                "lambda_time": lt,
                "lambda_nuclear": ln,
                "absolute_effect": abs_effect,
                "p_value": p_val,
                "ci_lower": ci_lo,
                "ci_upper": ci_hi,
                "donor_support_min": min_ns,
                "unstable_zero_support": unstable,
                "cf_post_min": cf_min,
                "cf_post_max": cf_max,
                "placebo_std": p_std,
                "cv_score": cv_score,
                "stability_score": stab,
                "hard_invalid": hard_invalid,
                "extended_invalid": ext_invalid,
            }
            rows.append(row)
            self.cv_history_.append(
                {
                    **pdict,
                    "cv_score": cv_score,
                    "stage": "stability_first_grid",
                    "cv_mode": self.cv_mode,
                    "hard_invalid": hard_invalid,
                    "stability_score": stab,
                }
            )

        self.tuning_comparison_df_ = pd.DataFrame(rows)

        hard_ok = [r for r in rows if not r["hard_invalid"]]
        if not hard_ok:
            raise RuntimeError(
                "TROP stability_first: no configuration passed hard filters "
                "(unstable_zero_support, min donor support, non-flat counterfactual). "
                "Relax min_donor_support, flat_cf_rel_tol, or expand grids."
            )

        ext_ok = [r for r in hard_ok if not r["extended_invalid"]]
        pool = ext_ok if ext_ok else hard_ok
        used_extended = bool(ext_ok)
        if not ext_ok:
            warnings.warn(
                "[TROP tuning] No configuration passed extended checks (CI scale / placebo_std / reference_effects). "
                "Selecting among hard-valid configs only.",
                UserWarning,
                stacklevel=2,
            )

        # Selection: lowest CV score, then highest stability (tie-break)
        pool.sort(key=lambda r: (float(r["cv_score"]), -float(r["stability_score"])))
        chosen = pool[0]

        self.tuning_selection_summary_ = {
            "selected": dict(chosen),
            "used_extended_filters": used_extended,
            "n_configs": n_grid,
            "n_hard_valid": len(hard_ok),
            "n_extended_valid": len(ext_ok),
            "reference_effects": self.reference_effects,
        }

        # Printed comparison: valid configs sorted by stability (desc), then CV (asc)
        display_rows = [r for r in rows if not r["hard_invalid"]]
        display_rows.sort(key=lambda r: (-float(r["stability_score"]), float(r["cv_score"])))
        print("\n[TROP tuning] Valid configurations (stability ↓, then CV ↑):")
        cols = [
            "lambda_unit",
            "lambda_time",
            "lambda_nuclear",
            "cv_score",
            "stability_score",
            "donor_support_min",
            "absolute_effect",
            "p_value",
            "placebo_std",
            "hard_invalid",
            "extended_invalid",
        ]
        disp_df = pd.DataFrame(display_rows)[cols] if display_rows else pd.DataFrame()
        if not disp_df.empty:
            with pd.option_context("display.max_rows", 200, "display.width", 200):
                print(disp_df.to_string(index=False))
        print(
            f"\n[TROP tuning] Selected λ = ({chosen['lambda_unit']}, {chosen['lambda_time']}, {chosen['lambda_nuclear']}) "
            f"| CV={chosen['cv_score']:.6g} | stability={chosen['stability_score']:.6g} | "
            f"donor_support_min={chosen['donor_support_min']}"
        )
        ref = self.reference_effects or {}
        if ref:
            print(f"[TROP tuning] reference_effects (directional check): {ref}")

        return {
            "lambda_unit": float(chosen["lambda_unit"]),
            "lambda_time": float(chosen["lambda_time"]),
            "lambda_nuclear": float(chosen["lambda_nuclear"]),
        }

    def _cv_score(self, lambda_unit: float, lambda_time: float, lambda_nuclear: float) -> float:
        """
        Dispatcher: route to global_obs or local_obs scorer based on cv_mode.
        cv_mode controls which fitting path is used during tuning (not method).
        """
        if self.cv_mode == "global_obs":
            return self._cv_score_global_obs(lambda_unit, lambda_time, lambda_nuclear)
        if self.cv_mode == "local_obs":
            return self._cv_score_local_obs(lambda_unit, lambda_time, lambda_nuclear)
        raise ValueError(f"cv_mode must be 'global_obs' or 'local_obs', got {self.cv_mode!r}")

    def _cv_score_global_obs(
        self, lambda_unit: float, lambda_time: float, lambda_nuclear: float
    ) -> float:
        """
        Global-observation CV: row-level placebo, one masked low-rank fit per placebo.
        Production/scalable approximation path; not exact paper-style observation-level LOOCV.
        """
        control_rows = np.where(~self.treated_mask_.any(axis=1))[0]
        treated_patterns = self._treated_row_patterns()
        if len(control_rows) == 0 or len(treated_patterns) == 0:
            raise ValueError("Need at least one control unit and one treated timing pattern for CV.")

        scores = []
        max_placebos = min(len(control_rows), self.max_cv_placebos)
        placebo_rows = (
            control_rows
            if len(control_rows) <= max_placebos
            else self._rng.choice(control_rows, size=max_placebos, replace=False)
        )

        for prow in placebo_rows:
            for pattern in treated_patterns:
                treated_mask_backup = self.treated_mask_.copy()
                control_mask_backup = self.control_mask_.copy()
                placebo_mask = treated_mask_backup.copy()
                placebo_mask[prow, pattern] = True
                self.treated_mask_ = placebo_mask
                self.control_mask_ = ~placebo_mask
                fit_res = self._fit_global_for_params(
                    lambda_unit=lambda_unit,
                    lambda_time=lambda_time,
                    lambda_nuclear=lambda_nuclear,
                )
                placebo_tau = fit_res.tau_hat_matrix[prow, pattern]
                scores.append(np.mean(placebo_tau**2))
                self.treated_mask_ = treated_mask_backup
                self.control_mask_ = control_mask_backup

        return float(np.mean(scores))

    def _cv_score_local_obs(
        self, lambda_unit: float, lambda_time: float, lambda_nuclear: float
    ) -> float:
        """
        Local-observation CV: row-level placebo, per-cell local fits per placebo.
        Closer to paper-style observation-specific scoring; slower than global_obs.
        """
        control_rows = np.where(~self.treated_mask_.any(axis=1))[0]
        treated_patterns = self._treated_row_patterns()
        if len(control_rows) == 0 or len(treated_patterns) == 0:
            raise ValueError("Need at least one control unit and one treated timing pattern for CV.")

        scores = []
        max_placebos = min(len(control_rows), self.max_cv_placebos)
        placebo_rows = (
            control_rows
            if len(control_rows) <= max_placebos
            else self._rng.choice(control_rows, size=max_placebos, replace=False)
        )

        for prow in placebo_rows:
            for pattern in treated_patterns:
                treated_mask_backup = self.treated_mask_.copy()
                control_mask_backup = self.control_mask_.copy()
                placebo_mask = treated_mask_backup.copy()
                placebo_mask[prow, pattern] = True
                self.treated_mask_ = placebo_mask
                self.control_mask_ = ~placebo_mask
                fit_res = self._fit_local_for_params(
                    lambda_unit=lambda_unit,
                    lambda_time=lambda_time,
                    lambda_nuclear=lambda_nuclear,
                )
                placebo_tau = fit_res.tau_hat_matrix[prow, pattern]
                scores.append(np.mean(placebo_tau**2))
                self.treated_mask_ = treated_mask_backup
                self.control_mask_ = control_mask_backup

        return float(np.mean(scores))

    # ---------------------------------------------------------------------
    # Aggregation helpers
    # ---------------------------------------------------------------------
    def _aggregate_treated_counterfactual(self, counterfactual_matrix: np.ndarray) -> np.ndarray:
        treated_rows = np.where(self.treated_mask_.any(axis=1))[0]
        # Task 5: Aggregation audit - shape, sum across rows, post-period segment
        slice_cf = counterfactual_matrix[treated_rows]
        row_sum = slice_cf.sum(axis=0)
        post_start = getattr(self, "treated_start_idx_", 0)
        post_segment = row_sum[post_start:]
        print(
            f"[TROP AGG] treated-row slice shape={slice_cf.shape} | "
            f"sum across rows (full): min={float(np.min(row_sum)):.4g} max={float(np.max(row_sum)):.4g} | "
            f"post-period segment len={len(post_segment)} min={float(np.min(post_segment)):.4g} max={float(np.max(post_segment)):.4g}"
        )
        return row_sum
