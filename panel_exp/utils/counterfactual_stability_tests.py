"""Counterfactual stability diagnostics (structural breaks, residual drift).

Residual drift uses **fit + predict only** (no ``run_analysis``, no bootstrap/CV/conformal inference).
It answers whether the counterfactual mapping is stable, not uncertainty quantification.

All linear-algebra paths validate inputs before calling NumPy/SciPy to avoid LAPACK errors
(e.g. DLASCL illegal value) from NaN/Inf, rank-deficient designs, or too-few observations.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from scipy import stats

from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.methods.scm import AugSynthCVXPY, SyntheticControlCVXPY
from panel_exp.methods.tbr import TBR, TBRRidge


WideLike = Union[pd.DataFrame, PanelDataset]
EstimatorName = str
FitPredictFn = Callable[[EstimatorName, PanelDataset], Mapping[str, Any]]

_VAR_EPS = 1e-18

# Residual-drift stability uses fit + predict only; heavy inference (Kfold, placebo, etc.) is forbidden.
_ALLOWED_STABILITY_INFERENCE = frozenset({None, "self"})


def _assert_stability_inference(model: Any, estimator: EstimatorName) -> None:
    """Raise if the analyzer is configured for heavy inference (anything other than None or 'self')."""
    inf = getattr(model, "inference", None)
    if inf not in _ALLOWED_STABILITY_INFERENCE:
        raise ValueError(
            "Counterfactual stability residual drift requires `inference` in {None, 'self'} only; "
            f"got {inf!r} on estimator {estimator!r}. "
            "Do not use Kfold, Placebo, Conformal, BRB, or other inference modes here."
        )


def _finite_1d(y: np.ndarray, *, ctx: str, name: str) -> np.ndarray:
    a = np.asarray(y, dtype=np.float64).ravel()
    if a.size == 0:
        raise ValueError(f"{ctx}: {name} is empty.")
    if not np.all(np.isfinite(a)):
        raise ValueError(f"{ctx}: {name} contains NaN or Inf after coercion to float64.")
    return a


def _finite_2d(X: np.ndarray, *, ctx: str, name: str) -> np.ndarray:
    a = np.asarray(X, dtype=np.float64)
    if a.ndim != 2:
        raise ValueError(f"{ctx}: {name} must be 2-D, got shape {getattr(X, 'shape', None)}.")
    if a.size == 0:
        raise ValueError(f"{ctx}: {name} is empty.")
    if not np.all(np.isfinite(a)):
        raise ValueError(f"{ctx}: {name} contains NaN or Inf.")
    return a


def _safe_lstsq(
    X: np.ndarray,
    y: np.ndarray,
    *,
    ctx: str,
    name: str,
    min_residual_df: int = 1,
) -> Tuple[np.ndarray, np.ndarray, int, np.ndarray]:
    """lstsq with pre-checks; raises ValueError instead of invoking LAPACK on bad data.

    min_residual_df: require n - k >= this value (default 1 for F-tests; use 0 for minimal fits).
    """
    Xf = _finite_2d(X, ctx=ctx, name=f"{name} design matrix")
    yf = _finite_1d(y, ctx=ctx, name=f"{name} outcome")
    n, k = Xf.shape
    if n != yf.size:
        raise ValueError(f"{ctx}: {name} row mismatch (X has {n}, y has {yf.size}).")
    if k < 1:
        raise ValueError(f"{ctx}: {name} design has no columns.")
    if n < k:
        raise ValueError(
            f"{ctx}: {name} has fewer observations ({n}) than predictors ({k}); cannot fit."
        )
    if n - k < min_residual_df:
        raise ValueError(
            f"{ctx}: {name} needs residual df n-k>={min_residual_df}; got n={n}, k={k} (n-k={n - k})."
        )
    # Rank check: avoid singular/ill-conditioned designs
    rank = int(np.linalg.matrix_rank(Xf))
    if rank < k:
        raise ValueError(
            f"{ctx}: {name} design matrix is rank-deficient (rank={rank}, k={k}); "
            "check for constant or collinear predictors in this segment."
        )
    beta, residuals, rnk, s = np.linalg.lstsq(Xf, yf, rcond=None)
    return beta, residuals, int(rnk), s


def _safe_polyfit_slope(x: np.ndarray, y: np.ndarray, *, ctx: str, segment: str) -> float:
    """Degree-1 polyfit slope, or nan if too few points / zero variance x / non-finite data."""
    xv = np.asarray(x, dtype=np.float64).ravel()
    yv = np.asarray(y, dtype=np.float64).ravel()
    if xv.size < 2 or yv.size < 2 or xv.size != yv.size:
        return float("nan")
    if not (np.all(np.isfinite(xv)) and np.all(np.isfinite(yv))):
        return float("nan")
    if float(np.var(xv)) < _VAR_EPS:
        return float("nan")
    try:
        coef = np.polyfit(xv, yv, 1)
        return float(coef[0])
    except (ValueError, np.linalg.LinAlgError):
        return float("nan")


def _resolve_column_position(
    columns: pd.Index,
    label_or_pos: Union[int, float, str, pd.Timestamp],
    *,
    context: str = "",
) -> int:
    """Resolve column index; raises KeyError/ValueError with context (no silent LAPACK)."""
    ctx = f" ({context})" if context else ""
    n = len(columns)
    if isinstance(label_or_pos, (int, np.integer)) and 0 <= int(label_or_pos) < n:
        return int(label_or_pos)

    candidates: List[Any] = [label_or_pos]
    if isinstance(label_or_pos, str):
        try:
            candidates.append(pd.Timestamp(label_or_pos))
        except (ValueError, TypeError):
            pass

    for cand in candidates:
        try:
            loc = columns.get_loc(cand)
        except (KeyError, TypeError):
            continue
        if isinstance(loc, slice):
            raise ValueError(
                f"Column label {cand!r} is ambiguous (slice locator){ctx}. "
                "Use unique time labels in the wide panel."
            )
        if isinstance(loc, (np.ndarray, list)) and not isinstance(loc, bool):
            if hasattr(loc, "__len__") and len(loc) != 1:
                raise ValueError(
                    f"Column label {cand!r} matches multiple columns{ctx}; "
                    "wide panel must have unique period labels."
                )
            loc = int(loc[0]) if len(loc) else None
            if loc is None:
                continue
        try:
            idx = int(np.asarray(loc).item())
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Could not resolve column index for {cand!r}{ctx}.") from exc
        if 0 <= idx < n:
            return idx

    preview = [str(x) for x in list(columns[: min(8, n)])]
    raise KeyError(
        f"Column label {label_or_pos!r} not found in wide data columns "
        f"(n_cols={n}, first columns: {preview}){ctx}."
    )


@dataclass(frozen=True)
class StructuralBreakTestResult:
    test_name: str
    break_label: str
    n_obs: int
    statistic: float
    p_value: float
    reject_null: bool
    effect_direction: str
    mean_pre: float
    mean_post: float
    slope_pre: Optional[float] = None
    slope_post: Optional[float] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ResidualDriftTestResult:
    estimator: str
    train_start_label: str
    train_end_label: str
    pseudo_test_start_label: str
    pseudo_test_end_label: str
    n_train_periods: int
    n_eval_periods: int
    residual_mean: float
    residual_std: float
    residual_rmse: float
    rmse_ratio: Optional[float]
    residual_t_stat: float
    residual_mean_p_value: float
    residual_slope: float
    residual_slope_t_stat: float
    residual_slope_p_value: float
    cumulative_residual: float
    cumulative_residual_abs: float
    residual_sign_balance: float
    residual_centered_flag: bool
    residual_drift_flag: bool
    training_rmse: Optional[float] = None
    training_resid_mean: Optional[float] = None
    training_resid_std: Optional[float] = None
    training_resid_max_abs: Optional[float] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ControlHeterogeneityResult:
    n_controls: int
    pre_shock_cv_mean: float
    shock_cv_mean: float
    post_shock_cv_mean: float
    cv_spike_ratio: float
    n_correlation_stable: int
    n_correlation_degraded: int
    degraded_units: Tuple[str, ...]
    recommended_transform: str
    recommended_drop_units: Tuple[str, ...]
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CounterfactualStabilitySummary:
    break_tests: Tuple[StructuralBreakTestResult, ...]
    residual_drift_tests: Tuple[ResidualDriftTestResult, ...]
    break_candidates: Tuple[Dict[str, Any], ...] = ()
    control_heterogeneity: Optional[ControlHeterogeneityResult] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "break_tests": [x.to_dict() for x in self.break_tests],
            "residual_drift_tests": [x.to_dict() for x in self.residual_drift_tests],
            "break_candidates": list(self.break_candidates),
            "control_heterogeneity": (
                self.control_heterogeneity.to_dict()
                if self.control_heterogeneity is not None
                else None
            ),
        }

    def to_frame(self) -> pd.DataFrame:
        rows: List[Dict[str, Any]] = []
        for item in self.break_tests:
            row = {"result_type": "break_test", **item.to_dict()}
            rows.append(row)
        for item in self.residual_drift_tests:
            row = {"result_type": "residual_drift_test", **item.to_dict()}
            rows.append(row)
        return pd.DataFrame(rows)


def _as_wide_data(data: WideLike) -> pd.DataFrame:
    if isinstance(data, PanelDataset):
        wide = data.wide_data.copy()
    elif isinstance(data, pd.DataFrame):
        wide = data.copy()
    else:
        raise TypeError("data must be a PanelDataset or wide pandas DataFrame")

    if not isinstance(wide.index, pd.Index) or not isinstance(wide.columns, pd.Index):
        raise TypeError("wide data must have labeled index and columns")

    wide = wide.sort_index(axis=0).sort_index(axis=1)
    if not wide.columns.is_unique:
        raise ValueError(
            "Wide panel columns are not unique; stability tests require one column per time period."
        )
    if not wide.index.is_unique:
        raise ValueError(
            "Wide panel row index (units) is not unique; stability tests require one row per unit."
        )
    return wide


def _normalize_units(units: Union[str, Sequence[str]]) -> List[str]:
    if isinstance(units, str):
        return [units]
    out = list(units)
    if not out:
        raise ValueError("treated_units must contain at least one unit")
    return out


def _aggregate_series(
    wide: pd.DataFrame,
    units: Sequence[str],
) -> np.ndarray:
    missing = [u for u in units if u not in wide.index]
    if missing:
        raise KeyError(f"Units not found in wide data: {missing}")
    if len(units) == 1:
        arr = wide.loc[units[0]].to_numpy(dtype=np.float64, copy=True)
    else:
        arr = wide.loc[list(units)].to_numpy(dtype=np.float64, copy=True)
        arr = np.sum(arr, axis=0)
    if not np.all(np.isfinite(arr)):
        raise ValueError(
            "Aggregated treated series contains NaN or Inf; wide panel must be fully numeric and finite "
            f"for units {list(units)!r}."
        )
    return arr


# Estimators that require a single aggregated treated series (mirrors main grid panel_aggregation_config).
# AugSynthCVXPY / SyntheticControlCVXPY / TBR optimize over n_control × n_treated variables;
# with many treated units the problem explodes (e.g. 71 × 69 = 4899 vars).
# Aggregating to 1 treated series reduces it to 71 × 1 = 71.
_ESTIMATORS_AGGREGATE_TREATED = frozenset({"AugSynthCVXPY", "SyntheticControlCVXPY", "TBR"})


def _default_fit_predict(estimator: EstimatorName, pds: PanelDataset) -> Mapping[str, Any]:
    """Fit on pre-period only, predict full timeline — no run_analysis, no bootstrap/CV/inference.

    Mirrors ImpactAnalyzer.run_analysis when ``inference is None`` (y / y_hat only).
    """
    estimator_map = {
        "AugSynthCVXPY": AugSynthCVXPY,
        "SyntheticControlCVXPY": SyntheticControlCVXPY,
        "TBR": TBR,
        "TBRRidge": TBRRidge,
    }
    if estimator not in estimator_map:
        raise ValueError(f"Unsupported estimator {estimator!r}")

    cls = estimator_map[estimator]
    # Never pass string inference modes (e.g. Kfold); stability diagnostics do not estimate uncertainty.
    model: Any = cls(inference=None)
    _assert_stability_inference(model, estimator)

    # Aggregate multiple treated units to a single series for estimators that need it.
    # This mirrors the main grid's panel_aggregation_config and keeps the optimization tractable.
    if estimator in _ESTIMATORS_AGGREGATE_TREATED and len(pds.treated_units) > 1:
        treated_agg = (
            pds.wide_data.loc[pds.treated_units]
            .sum(axis=0)
            .to_frame("__treated__")
            .T
        )
        ctrl = pds.wide_data.drop(index=pds.treated_units)
        agg_wide = pd.concat([treated_agg, ctrl])
        pds = PanelDataset(
            wide_data=agg_wide,
            treated_periods=[pds.treated_periods[0]],
            treated_units=["__treated__"],
        )

    model.panel_data = pds
    model.fit_data(pds)
    fitted = model.fit_model()
    model.model = fitted

    X_ctrl = pds.control_series(pds.treated_units).values.T
    y_hat = fitted.predict(X_ctrl)
    y = pds.treated_series(pds.treated_units).values.T

    if y.shape[0] == pds.num_timepoints and y.shape[1] == 1:
        y = y.reshape(-1)
    y_hat_arr = np.asarray(y_hat)
    if y_hat_arr.ndim == 2 and y_hat_arr.shape[0] == pds.num_timepoints and y_hat_arr.shape[1] == 1:
        y_hat = y_hat_arr.reshape(-1)

    return {
        "times": pds.times,
        "y": y,
        "y_hat": y_hat,
    }


def build_pseudo_test_paneldataset(
    data: WideLike,
    treated_units: Union[str, Sequence[str]],
    train_end: Union[int, float, str, pd.Timestamp],
    pseudo_test_start: Union[int, float, str, pd.Timestamp],
    pseudo_test_end: Union[int, float, str, pd.Timestamp],
) -> PanelDataset:
    wide = _as_wide_data(data)
    treated = _normalize_units(treated_units)

    train_end_idx = _resolve_column_position(wide.columns, train_end, context="pseudo_panel train_end")
    pseudo_start_idx = _resolve_column_position(
        wide.columns, pseudo_test_start, context="pseudo_panel pseudo_test_start"
    )
    pseudo_end_idx = _resolve_column_position(
        wide.columns, pseudo_test_end, context="pseudo_panel pseudo_test_end"
    )

    if pseudo_start_idx <= train_end_idx:
        raise ValueError(
            "pseudo_test_start must come strictly after train_end (pseudo-test window must not overlap "
            f"training columns): train_end_idx={train_end_idx}, pseudo_start_idx={pseudo_start_idx}."
        )
    if pseudo_end_idx < pseudo_start_idx:
        raise ValueError("pseudo_test_end must be on or after pseudo_test_start")
    if train_end_idx < 2:
        raise ValueError("Need at least 3 training periods before the pseudo-test window")

    subset = wide.iloc[:, : pseudo_end_idx + 1].copy()
    start_label = subset.columns[pseudo_start_idx]
    end_label = subset.columns[pseudo_end_idx]
    treated_periods = [TimePeriod(start_label, end_label) for _ in treated]
    return PanelDataset(wide_data=subset, treated_periods=treated_periods, treated_units=treated)


def detect_break_candidates(
    data: WideLike,
    treated_units: Union[str, Sequence[str]],
    control_units: Optional[Sequence[str]] = None,
    method: str = "cusum_residual",
    min_pre_periods: int = 8,
    threshold: float = 3.0,
    n_bai_perron_breaks: int = 1,
    end: Optional[Union[int, float, str, pd.Timestamp]] = None,
) -> List[Dict[str, Any]]:
    wide = _as_wide_data(data)
    treated = _normalize_units(treated_units)

    # Optionally truncate at end
    if end is not None:
        end_idx = _resolve_column_position(wide.columns, end, context="detect_break_candidates end")
        wide = wide.iloc[:, : end_idx + 1]

    if method == "cusum_treated":
        y = _aggregate_series(wide, treated)
        y = _finite_1d(y, ctx="detect_break_candidates", name="treated series")
        mu = float(np.mean(y[:min_pre_periods]))
        sigma = float(np.std(y[:min_pre_periods]))
        if sigma < _VAR_EPS:
            return []
        standardised = (y - mu) / sigma
        cusum = np.cumsum(standardised)
        # CUSUM statistic: maximum absolute value over post-pre-period window
        cusum_stat = float(np.max(np.abs(cusum[min_pre_periods:])))
        if cusum_stat < threshold:
            return []
        # Retrospective break-point estimator: scan each candidate break point and find
        # the one that maximizes the absolute mean difference between pre- and post-segments.
        # This is the standard sup-Wald estimator, equivalent to retrospective CUSUM.
        n = len(y)
        best_stat = -np.inf
        break_idx = min_pre_periods
        for tau in range(min_pre_periods, n - 1):
            pre_mean = float(np.mean(y[:tau]))
            post_mean = float(np.mean(y[tau:]))
            n1, n2 = tau, n - tau
            pooled_var = float(np.var(y[:tau]) / n1 + np.var(y[tau:]) / n2 + _VAR_EPS)
            scan_stat = abs(post_mean - pre_mean) / float(np.sqrt(pooled_var))
            if scan_stat > best_stat:
                best_stat = scan_stat
                break_idx = tau
        direction = "up" if float(np.mean(y[break_idx:])) > float(np.mean(y[:break_idx])) else "down"
        candidates = [
            {
                "break_label": str(wide.columns[break_idx]),
                "break_idx": int(break_idx),
                "cusum_stat": cusum_stat,
                "method": method,
                "direction": direction,
            }
        ]
        return sorted(candidates, key=lambda d: d["cusum_stat"], reverse=True)

    elif method == "cusum_residual":
        y = _aggregate_series(wide, treated)
        y = _finite_1d(y, ctx="detect_break_candidates", name="treated series")
        n = len(y)

        # Build control matrix
        if control_units is None:
            ctrl_keys = [u for u in wide.index if u not in treated]
        else:
            ctrl_keys = list(control_units)

        if ctrl_keys:
            x_ctrl = wide.loc[ctrl_keys].to_numpy(dtype=np.float64, copy=True).sum(axis=0)
        else:
            x_ctrl = np.zeros(n, dtype=np.float64)

        x = np.column_stack([np.ones(n), x_ctrl])

        beta, _, _, _ = _safe_lstsq(
            x[:min_pre_periods],
            y[:min_pre_periods],
            ctx="detect_break_cusum_residual",
            name="pre-period fit",
            min_residual_df=0,
        )
        residuals = y - x @ beta

        mu = float(np.mean(residuals[:min_pre_periods]))
        sigma = float(np.std(residuals[:min_pre_periods]))
        if sigma < _VAR_EPS:
            return []
        standardised = (residuals - mu) / sigma
        cusum = np.cumsum(standardised)
        # CUSUM statistic: maximum absolute value over post-pre-period window
        cusum_stat = float(np.max(np.abs(cusum[min_pre_periods:])))
        if cusum_stat < threshold:
            return []
        # Retrospective break-point estimator: scan each candidate break point and find
        # the one that maximizes the absolute mean difference in residuals between segments.
        best_stat = -np.inf
        break_idx = min_pre_periods
        for tau in range(min_pre_periods, n - 1):
            pre_mean = float(np.mean(residuals[:tau]))
            post_mean = float(np.mean(residuals[tau:]))
            n1, n2 = tau, n - tau
            pooled_var = float(np.var(residuals[:tau]) / n1 + np.var(residuals[tau:]) / n2 + _VAR_EPS)
            scan_stat = abs(post_mean - pre_mean) / float(np.sqrt(pooled_var))
            if scan_stat > best_stat:
                best_stat = scan_stat
                break_idx = tau
        direction = "up" if float(np.mean(residuals[break_idx:])) > float(np.mean(residuals[:break_idx])) else "down"
        candidates = [
            {
                "break_label": str(wide.columns[break_idx]),
                "break_idx": int(break_idx),
                "cusum_stat": cusum_stat,
                "method": method,
                "direction": direction,
            }
        ]
        return sorted(candidates, key=lambda d: d["cusum_stat"], reverse=True)

    elif method == "bai_perron":
        try:
            import ruptures
        except ImportError:
            raise ImportError(
                "ruptures is required for method='bai_perron'. Install with: pip install ruptures"
            )
        y = _aggregate_series(wide, treated)
        y = _finite_1d(y, ctx="detect_break_candidates", name="treated series")
        algo = ruptures.Binseg(model="rbf").fit(y.reshape(-1, 1))
        bkps = algo.predict(n_bkps=n_bai_perron_breaks)
        bkps = [b for b in bkps if b < len(y)]
        candidates = []
        for b in bkps:
            direction = "up" if float(np.mean(y[b:])) > float(np.mean(y[:b])) else "down"
            candidates.append(
                {
                    "break_label": str(wide.columns[b]),
                    "break_idx": int(b),
                    "cusum_stat": float("nan"),
                    "method": method,
                    "direction": direction,
                }
            )
        return sorted(candidates, key=lambda d: d["break_idx"])

    else:
        raise ValueError(f"Unknown method {method!r}. Choose 'cusum_treated', 'cusum_residual', or 'bai_perron'.")


def run_control_heterogeneity_diagnostics(
    data: WideLike,
    treated_units: Union[str, Sequence[str]],
    shock_start: Union[int, float, str, pd.Timestamp],
    shock_end: Union[int, float, str, pd.Timestamp],
    control_units: Optional[Sequence[str]] = None,
    cv_spike_threshold: float = 1.5,
    correlation_drop_threshold: float = 0.2,
    alpha: float = 0.05,
) -> ControlHeterogeneityResult:
    ctx = "run_control_heterogeneity_diagnostics"
    wide = _as_wide_data(data)
    treated = _normalize_units(treated_units)
    control_list = list(control_units) if control_units is not None else [u for u in wide.index if u not in treated]
    shock_start_idx = _resolve_column_position(wide.columns, shock_start, context=ctx)
    shock_end_idx = _resolve_column_position(wide.columns, shock_end, context=ctx)
    if shock_end_idx <= shock_start_idx:
        raise ValueError(f"{ctx}: shock_end must be after shock_start (shock_start_idx={shock_start_idx}, shock_end_idx={shock_end_idx})")
    pre_cols = wide.columns[:shock_start_idx]
    shock_cols = wide.columns[shock_start_idx:shock_end_idx]
    _post_cols = wide.columns[shock_end_idx:]
    if len(pre_cols) < 4:
        raise ValueError(f"{ctx}: need at least 4 pre-shock periods; got {len(pre_cols)}")
    if len(shock_cols) < 2:
        raise ValueError(f"{ctx}: need at least 2 shock periods; got {len(shock_cols)}")

    # Get control matrix (rows=controls, cols=time)
    ctrl_matrix = wide.loc[control_list].to_numpy(dtype=np.float64, copy=True)
    if not np.all(np.isfinite(ctrl_matrix)):
        raise ValueError(f"{ctx}: control matrix contains NaN or Inf.")

    # CV computation — cross-sectional CV at each time point
    pre_indices = range(0, shock_start_idx)
    shock_indices = range(shock_start_idx, shock_end_idx)
    post_indices = range(shock_end_idx, wide.shape[1])

    def _mean_cv(indices: range) -> float:
        cv_vals = []
        for t in indices:
            col_vals = ctrl_matrix[:, t]
            cv_t = np.std(col_vals) / (np.abs(np.mean(col_vals)) + 1e-12)
            cv_vals.append(cv_t)
        return float(np.mean(cv_vals)) if cv_vals else float("nan")

    pre_shock_cv_mean = _mean_cv(pre_indices)
    shock_cv_mean = _mean_cv(shock_indices)
    post_shock_cv_mean = _mean_cv(post_indices) if len(post_indices) > 0 else float("nan")
    cv_spike_ratio = shock_cv_mean / (pre_shock_cv_mean + 1e-12)

    # Correlation stability per control unit
    treated_agg = _aggregate_series(wide, treated)
    treated_pre = treated_agg[:shock_start_idx]
    treated_post = treated_agg[shock_end_idx:]

    degraded_units_list = []
    stable_count = 0

    for u in control_list:
        unit_series = wide.loc[u].to_numpy(dtype=np.float64)
        unit_pre = unit_series[:shock_start_idx]
        unit_post = unit_series[shock_end_idx:]

        # Skip if insufficient post periods
        if len(unit_post) < 4:
            stable_count += 1
            continue

        # Skip if zero variance in either window
        if np.var(unit_pre) < _VAR_EPS or np.var(treated_pre) < _VAR_EPS:
            stable_count += 1
            continue
        if np.var(unit_post) < _VAR_EPS or np.var(treated_post) < _VAR_EPS:
            stable_count += 1
            continue

        pre_corr, _ = stats.pearsonr(unit_pre, treated_pre)
        post_corr, _ = stats.pearsonr(unit_post, treated_post)
        corr_drop = pre_corr - post_corr

        if corr_drop > correlation_drop_threshold:
            degraded_units_list.append(str(u))
        else:
            stable_count += 1

    n_controls = len(control_list)
    n_degraded = len(degraded_units_list)
    n_stable = stable_count

    # Recommendations
    recommended_transform = "pca" if cv_spike_ratio > cv_spike_threshold else "aggregate"

    # Only recommend dropping if < 30% degraded (if > 30% it's market-wide, not donor-specific)
    if n_degraded > 0 and n_degraded / n_controls <= 0.3:
        recommended_drop_units = tuple(degraded_units_list)
    else:
        recommended_drop_units = ()

    # Notes
    if cv_spike_ratio <= cv_spike_threshold and n_degraded == 0:
        notes = "Controls are homogeneous across shock window. Aggregate transform is appropriate."
    elif cv_spike_ratio > cv_spike_threshold and n_degraded == 0:
        notes = (
            f"Controls diverged during shock (cv_spike_ratio={cv_spike_ratio:.2f}) but "
            f"correlation with treated remains stable. Monitor but aggregate transform likely still valid."
        )
    elif cv_spike_ratio <= cv_spike_threshold and n_degraded > 0:
        notes = (
            f"Controls show uniform shock response but {n_degraded} unit(s) have "
            f"degraded correlation with treated post-shock: {degraded_units_list}. "
            f"Consider dropping these donors."
        )
    else:
        notes = (
            f"Controls are heterogeneous (cv_spike_ratio={cv_spike_ratio:.2f}) and "
            f"{n_degraded} unit(s) show correlation degradation. PCA transform recommended. "
            f"Consider dropping: {degraded_units_list}."
        )

    return ControlHeterogeneityResult(
        n_controls=n_controls,
        pre_shock_cv_mean=pre_shock_cv_mean,
        shock_cv_mean=shock_cv_mean,
        post_shock_cv_mean=post_shock_cv_mean,
        cv_spike_ratio=cv_spike_ratio,
        n_correlation_stable=n_stable,
        n_correlation_degraded=n_degraded,
        degraded_units=tuple(degraded_units_list),
        recommended_transform=recommended_transform,
        recommended_drop_units=recommended_drop_units,
        notes=notes,
    )


def run_level_slope_break_test(
    data: WideLike,
    treated_units: Union[str, Sequence[str]],
    break_start: Union[int, float, str, pd.Timestamp],
    end: Optional[Union[int, float, str, pd.Timestamp]] = None,
    alpha: float = 0.05,
) -> StructuralBreakTestResult:
    ctx = "level_slope_break_test"
    wide = _as_wide_data(data)
    treated = _normalize_units(treated_units)
    y = _aggregate_series(wide, treated)

    break_idx = _resolve_column_position(wide.columns, break_start, context=ctx)
    end_idx = (
        len(wide.columns) - 1
        if end is None
        else _resolve_column_position(wide.columns, end, context=f"{ctx} end")
    )
    if end_idx <= break_idx:
        raise ValueError(f"{ctx}: end must be after break_start (break_idx={break_idx}, end_idx={end_idx}).")
    if break_idx < 2:
        raise ValueError(
            f"{ctx}: need at least 3 pre-break periods (break_idx>=2); got break_idx={break_idx}."
        )

    y = y[: end_idx + 1]
    y = _finite_1d(y, ctx=ctx, name="treated series (truncated)")
    n_obs = int(y.size)
    post_len = n_obs - break_idx
    if post_len < 2:
        raise ValueError(
            f"{ctx}: need at least 2 post-break observations; got post_len={post_len} (n={n_obs}, break_idx={break_idx})."
        )

    t = np.arange(n_obs, dtype=np.float64)
    d = (t >= break_idx).astype(np.float64)
    td = t * d

    x = np.column_stack([np.ones_like(t), t, d, td])
    beta_hat, _, _, _ = _safe_lstsq(x, y, ctx=ctx, name="unrestricted break model")
    resid = y - x @ beta_hat
    n, k = x.shape
    rss_u = float(np.sum(resid**2))

    x_r = np.column_stack([np.ones_like(t), t])
    beta_r, _, _, _ = _safe_lstsq(x_r, y, ctx=ctx, name="restricted no-break model")
    resid_r = y - x_r @ beta_r
    rss_r = float(np.sum(resid_r**2))

    q = 2
    denom_df = n - k
    if denom_df <= 0:
        raise ValueError(f"{ctx}: not enough residual df (n={n}, k={k}).")
    f_stat = ((rss_r - rss_u) / q) / (rss_u / denom_df)
    p_value = float(1.0 - stats.f.cdf(f_stat, q, denom_df))

    pre = y[:break_idx]
    post = y[break_idx:]
    slope_pre = _safe_polyfit_slope(
        np.arange(len(pre), dtype=np.float64), pre, ctx=ctx, segment="pre-break"
    )
    slope_post = _safe_polyfit_slope(
        np.arange(len(post), dtype=np.float64), post, ctx=ctx, segment="post-break"
    )
    direction = "up" if float(np.mean(post)) > float(np.mean(pre)) else "down"

    return StructuralBreakTestResult(
        test_name="level_slope_break",
        break_label=str(wide.columns[break_idx]),
        n_obs=n,
        statistic=float(f_stat),
        p_value=p_value,
        reject_null=bool(p_value < alpha),
        effect_direction=direction,
        mean_pre=float(np.mean(pre)),
        mean_post=float(np.mean(post)),
        slope_pre=float(slope_pre),
        slope_post=float(slope_post),
        notes="Tests for a treated-series level/slope shift at the supplied break point.",
    )


def run_treated_control_break_test(
    data: WideLike,
    treated_units: Union[str, Sequence[str]],
    break_start: Union[int, float, str, pd.Timestamp],
    control_units: Optional[Sequence[str]] = None,
    control_transform: str = "aggregate",
    n_control_pcs: int = 3,
    end: Optional[Union[int, float, str, pd.Timestamp]] = None,
    alpha: float = 0.05,
) -> StructuralBreakTestResult:
    ctx = "treated_control_break_test"
    wide = _as_wide_data(data)
    treated = _normalize_units(treated_units)
    control_units = list(control_units) if control_units is not None else [u for u in wide.index if u not in treated]
    if not control_units:
        raise ValueError(f"{ctx}: need at least one control unit (treated={treated!r}).")

    missing_ctrl = [u for u in control_units if u not in wide.index]
    if missing_ctrl:
        raise KeyError(f"{ctx}: control units not in wide panel index: {missing_ctrl!r}.")

    break_idx = _resolve_column_position(wide.columns, break_start, context=ctx)
    end_idx = (
        len(wide.columns) - 1
        if end is None
        else _resolve_column_position(wide.columns, end, context=f"{ctx} end")
    )
    if end_idx <= break_idx:
        raise ValueError(f"{ctx}: end must be after break_start (break_idx={break_idx}, end_idx={end_idx}).")
    if break_idx < 3:
        raise ValueError(
            f"{ctx}: need at least 4 pre-break periods (break_idx>=3); got break_idx={break_idx}."
        )

    y = _aggregate_series(wide.iloc[:, : end_idx + 1], treated)
    y = _finite_1d(y, ctx=ctx, name="treated series")
    x_raw = wide.loc[control_units].iloc[:, : end_idx + 1].to_numpy(dtype=np.float64, copy=True).T
    if not np.all(np.isfinite(x_raw)):
        raise ValueError(
            f"{ctx}: control matrix contains NaN or Inf (control_units={control_units!r}, "
            f"n_periods={x_raw.shape[0]})."
        )

    if control_transform == "aggregate":
        x = x_raw.sum(axis=1, keepdims=True)
        if float(np.var(x)) < _VAR_EPS:
            raise ValueError(f"{ctx}: aggregated control series is (near) constant; cannot fit break model.")
    elif control_transform == "pca":
        n_periods, n_ctrl = x_raw.shape
        if n_periods < 3:
            raise ValueError(f"{ctx}: need at least 3 periods for PCA controls; got n_periods={n_periods}.")
        x_centered = x_raw - x_raw.mean(axis=0, keepdims=True)
        if not np.any(np.abs(x_centered) > _VAR_EPS):
            raise ValueError(f"{ctx}: control matrix is constant after centering; cannot run PCA.")
        try:
            u, s, vt = np.linalg.svd(x_centered, full_matrices=False)
        except np.linalg.LinAlgError as exc:
            raise ValueError(f"{ctx}: SVD failed on control matrix: {exc}") from exc
        n_pcs = max(1, min(int(n_control_pcs), int(u.shape[1]), int(s.size)))
        x = u[:, :n_pcs] * s[:n_pcs]
    else:
        raise ValueError("control_transform must be 'aggregate' or 'pca'")

    if x.shape[0] != y.size:
        raise ValueError(
            f"{ctx}: length mismatch between y (n={y.size}) and control features (n={x.shape[0]})."
        )

    t = np.arange(len(y), dtype=np.float64)
    d = (t >= break_idx).astype(np.float64)
    x_d = x * d[:, None]

    xu = np.column_stack([np.ones(len(y)), x, d, x_d])
    beta_hat, _, _, _ = _safe_lstsq(xu, y, ctx=ctx, name="unrestricted treated~control+break")
    resid_u = y - xu @ beta_hat
    n, k = xu.shape
    rss_u = float(np.sum(resid_u**2))

    xr = np.column_stack([np.ones(len(y)), x])
    beta_r, _, _, _ = _safe_lstsq(xr, y, ctx=ctx, name="restricted treated~control")
    resid_r = y - xr @ beta_r
    rss_r = float(np.sum(resid_r**2))

    q = 1 + x.shape[1]
    denom_df = n - k
    if denom_df <= 0:
        raise ValueError(f"{ctx}: not enough observations for F-test (n={n}, k={k}).")
    f_stat = ((rss_r - rss_u) / q) / (rss_u / denom_df)
    p_value = float(1.0 - stats.f.cdf(f_stat, q, denom_df))

    fitted_no_break = xr @ beta_r
    mean_pre = float(np.mean(y[:break_idx] - fitted_no_break[:break_idx]))
    mean_post = float(np.mean(y[break_idx:] - fitted_no_break[break_idx:]))
    direction = "up" if mean_post > mean_pre else "down"

    return StructuralBreakTestResult(
        test_name="treated_control_relationship_break",
        break_label=str(wide.columns[break_idx]),
        n_obs=n,
        statistic=float(f_stat),
        p_value=p_value,
        reject_null=bool(p_value < alpha),
        effect_direction=direction,
        mean_pre=mean_pre,
        mean_post=mean_post,
        slope_pre=None,
        slope_post=None,
        notes=(
            f"Tests whether the treated-control relationship changes at the supplied break point "
            f"using control_transform={control_transform!r}."
        ),
    )


def run_residual_drift_test(
    data: WideLike,
    treated_units: Union[str, Sequence[str]],
    train_end: Union[int, float, str, pd.Timestamp],
    pseudo_test_start: Union[int, float, str, pd.Timestamp],
    pseudo_test_end: Union[int, float, str, pd.Timestamp],
    estimators: Sequence[EstimatorName] = ("TBRRidge",),
    fit_predict_fn: Optional[FitPredictFn] = None,
    alpha: float = 0.05,
    log_label: Optional[str] = None,
) -> Tuple[ResidualDriftTestResult, ...]:
    wide = _as_wide_data(data)
    pds = build_pseudo_test_paneldataset(
        data=wide,
        treated_units=treated_units,
        train_end=train_end,
        pseudo_test_start=pseudo_test_start,
        pseudo_test_end=pseudo_test_end,
    )
    fit_predict_fn = fit_predict_fn or _default_fit_predict

    start_idx = pds.treated_start_idxs[0]
    end_idx = pds.treated_end_idxs[0]
    train_start_label = str(pds.wide_data.columns[0])
    train_end_label = str(pds.wide_data.columns[start_idx - 1])
    pseudo_start_label = str(pds.wide_data.columns[start_idx])
    pseudo_end_label = str(pds.wide_data.columns[end_idx])

    results: List[ResidualDriftTestResult] = []
    for estimator in estimators:
        prefix = f"[STABILITY_PERF] {log_label} " if log_label else "[STABILITY_PERF] "
        t0 = time.perf_counter()
        print(f"{prefix}estimator={estimator!r} fit_predict_start")
        raw = fit_predict_fn(estimator, pds)
        print(
            f"{prefix}estimator={estimator!r} fit_predict_end "
            f"elapsed_s={time.perf_counter() - t0:.3f}"
        )
        if "y" not in raw or "y_hat" not in raw:
            raise KeyError(
                f"Residual drift test expected keys 'y' and 'y_hat' from estimator {estimator!r}; "
                f"received keys {sorted(raw.keys())}"
            )

        y = np.asarray(raw["y"], dtype=float)
        y_hat = np.asarray(raw["y_hat"], dtype=float)
        if y.ndim > 1:
            y = y.sum(axis=1)
        if y_hat.ndim > 1:
            y_hat = y_hat.sum(axis=1)

        resid = y[start_idx : end_idx + 1] - y_hat[start_idx : end_idx + 1]
        resid = np.asarray(resid, dtype=np.float64).ravel()
        rctx = f"residual_drift_test estimator={estimator!r}"
        if resid.size < 2:
            raise ValueError(
                f"{rctx}: pseudo-test window must contain at least two periods; got resid.size={resid.size}."
            )
        if not np.all(np.isfinite(resid)):
            raise ValueError(f"{rctx}: residuals contain NaN or Inf (check estimator y / y_hat).")

        train_resid = y[:start_idx] - y_hat[:start_idx]
        training_rmse = float(np.sqrt(np.mean(train_resid**2))) if train_resid.size > 0 else float("nan")
        training_resid_mean = float(np.mean(train_resid)) if train_resid.size > 0 else None
        training_resid_std = float(np.std(train_resid, ddof=1)) if train_resid.size > 1 else None
        training_resid_max_abs = float(np.max(np.abs(train_resid))) if train_resid.size > 0 else None

        residual_mean = float(np.mean(resid))
        residual_std = float(np.std(resid, ddof=1)) if resid.size > 1 else 0.0
        residual_rmse = float(np.sqrt(np.mean(resid**2)))
        rmse_ratio: Optional[float] = residual_rmse / training_rmse if (np.isfinite(training_rmse) and training_rmse > 0) else None
        t_stat, p_value = stats.ttest_1samp(resid, 0.0)
        if np.isnan(t_stat):
            t_stat, p_value = 0.0, 1.0

        t = np.arange(resid.size, dtype=np.float64)
        x = np.column_stack([np.ones_like(t), t])
        if float(np.var(t)) < _VAR_EPS:
            raise ValueError(f"{rctx}: time index in pseudo-test window has zero variance (cannot fit slope).")
        beta_hat, _, _, _ = _safe_lstsq(x, resid, ctx=rctx, name="residual~time", min_residual_df=0)
        resid2 = resid - x @ beta_hat
        dof = max(1, resid.size - x.shape[1])
        s2 = float(np.sum(resid2**2) / dof)
        try:
            xtx_pinv = np.linalg.pinv(x.T @ x, rcond=1e-12)
            slope_se = float(np.sqrt(max(float(xtx_pinv[1, 1]) * s2, 0.0)))
        except np.linalg.LinAlgError:
            slope_se = 0.0
        if slope_se > 0 and np.isfinite(slope_se):
            slope_t = float(beta_hat[1] / slope_se)
            slope_p = float(2.0 * (1.0 - stats.t.cdf(abs(slope_t), dof)))
        else:
            slope_t, slope_p = 0.0, 1.0

        sign_balance = float(np.mean(np.sign(resid)))
        residual_centered_flag = bool(p_value >= alpha)
        residual_drift_flag = bool(slope_p < alpha)

        # Build notes with exact conditional logic
        if residual_centered_flag and not residual_drift_flag:
            notes = "Centered residuals and zero drift support counterfactual stability."
        elif not residual_centered_flag and not residual_drift_flag:
            notes = (
                f"Residuals are significantly biased (mean={residual_mean:+.0f}, "
                f"p={p_value:.4f}) but show no increasing drift. Suggests a level "
                f"shift in the pseudo-test window — model may need retraining or "
                f"intercept correction."
            )
        elif residual_centered_flag and residual_drift_flag:
            notes = (
                f"Residuals are centered but show significant drift "
                f"(slope={float(beta_hat[1]):+.0f}/period, p={slope_p:.4f}). "
                f"The counterfactual relationship may be deteriorating over the "
                f"pseudo-test window."
            )
        else:
            notes = (
                f"Residuals are both biased (mean={residual_mean:+.0f}) and drifting "
                f"(slope={float(beta_hat[1]):+.0f}/period). Counterfactual stability "
                f"is strongly violated."
            )

        # Append rmse_ratio info
        if rmse_ratio is not None:
            notes += f" RMSE ratio (pseudo/train)={rmse_ratio:.2f}."
            if rmse_ratio > 2.0:
                notes += " MODEL ACCURACY DEGRADED."

        if training_rmse is not None and np.isfinite(training_rmse) and training_rmse < 1.0:
            notes += (
                f" WARNING: training RMSE near-zero ({training_rmse:.4f})"
                " — check for model overfitting or numerical issues."
            )

        results.append(
            ResidualDriftTestResult(
                estimator=estimator,
                train_start_label=train_start_label,
                train_end_label=train_end_label,
                pseudo_test_start_label=pseudo_start_label,
                pseudo_test_end_label=pseudo_end_label,
                n_train_periods=start_idx,
                n_eval_periods=resid.size,
                residual_mean=residual_mean,
                residual_std=residual_std,
                residual_rmse=residual_rmse,
                rmse_ratio=rmse_ratio,
                training_rmse=training_rmse if train_resid.size > 0 else None,
                training_resid_mean=training_resid_mean,
                training_resid_std=training_resid_std,
                training_resid_max_abs=training_resid_max_abs,
                residual_t_stat=float(t_stat),
                residual_mean_p_value=float(p_value),
                residual_slope=float(beta_hat[1]),
                residual_slope_t_stat=slope_t,
                residual_slope_p_value=slope_p,
                cumulative_residual=float(np.sum(resid)),
                cumulative_residual_abs=float(np.sum(np.abs(resid))),
                residual_sign_balance=sign_balance,
                residual_centered_flag=residual_centered_flag,
                residual_drift_flag=residual_drift_flag,
                notes=notes,
            )
        )
    return tuple(results)


def run_counterfactual_stability_tests(
    data: WideLike,
    treated_units: Union[str, Sequence[str]],
    train_end: Union[int, float, str, pd.Timestamp],
    pseudo_test_start: Union[int, float, str, pd.Timestamp],
    pseudo_test_end: Union[int, float, str, pd.Timestamp],
    break_start: Optional[Union[int, float, str, pd.Timestamp]] = None,
    auto_detect_break: bool = True,
    break_detection_method: str = "cusum_residual",
    break_detection_threshold: float = 3.0,
    control_units: Optional[Sequence[str]] = None,
    estimators: Sequence[EstimatorName] = ("TBRRidge",),
    fit_predict_fn: Optional[FitPredictFn] = None,
    alpha: float = 0.05,
    control_transform: str = "auto",
    n_control_pcs: int = 3,
    log_label: Optional[str] = None,
    run_heterogeneity_check: bool = True,
    cv_spike_threshold: float = 1.5,
    correlation_drop_threshold: float = 0.2,
) -> CounterfactualStabilitySummary:
    # --- Step 1: Break detection — resolves break_start first ---
    candidates: List[Dict[str, Any]] = []
    if break_start is None:
        if not auto_detect_break:
            raise ValueError(
                "break_start is required when auto_detect_break=False. "
                "Either pass break_start explicitly or set auto_detect_break=True."
            )
        candidates = detect_break_candidates(
            data=data,
            treated_units=treated_units,
            control_units=control_units,
            method=break_detection_method,
            threshold=break_detection_threshold,
            end=pseudo_test_end,
        )
        if not candidates:
            raise ValueError(
                "auto_detect_break=True but no structural break candidates were "
                "found above the threshold. Either lower break_detection_threshold, "
                "pass break_start explicitly, or check your data."
            )
        break_start = candidates[0]["break_label"]
        print(
            f"[STABILITY] Auto-detected break at {break_start} "
            f"(method={break_detection_method}, "
            f"cusum_stat={candidates[0]['cusum_stat']:.2f}, "
            f"direction={candidates[0]['direction']}). "
            f"Pass break_start explicitly to override."
        )
    else:
        candidates = detect_break_candidates(
            data=data,
            treated_units=treated_units,
            control_units=control_units,
            method=break_detection_method,
            threshold=break_detection_threshold,
            end=pseudo_test_end,
        )
        if candidates:
            auto_label = candidates[0]["break_label"]
            if str(auto_label) != str(break_start):
                print(
                    f"[STABILITY WARNING] You passed break_start={break_start} but "
                    f"auto-detection found {auto_label} as the strongest candidate "
                    f"(cusum_stat={candidates[0]['cusum_stat']:.2f}). "
                    f"Using your supplied break_start. Pass break_start=None to "
                    f"use auto-detection."
                )

    # --- Step 2: Heterogeneity check — uses resolved break_start ---
    heterogeneity: Optional[ControlHeterogeneityResult] = None
    if run_heterogeneity_check:
        try:
            heterogeneity = run_control_heterogeneity_diagnostics(
                data=data,
                treated_units=treated_units,
                control_units=control_units,
                shock_start=break_start,
                shock_end=pseudo_test_start,
                cv_spike_threshold=cv_spike_threshold,
                correlation_drop_threshold=correlation_drop_threshold,
                alpha=alpha,
            )
        except Exception as _het_exc:
            import warnings as _w
            _w.warn(f"[STABILITY] Heterogeneity check failed (non-fatal): {_het_exc}", UserWarning)

    # --- Step 3: Auto control_transform resolution — uses heterogeneity result ---
    if control_transform == "auto":
        if heterogeneity is not None:
            control_transform = heterogeneity.recommended_transform
            print(
                f"[STABILITY] Auto-selected control_transform={control_transform!r} based on "
                f"heterogeneity diagnostics (cv_spike_ratio={heterogeneity.cv_spike_ratio:.2f})"
            )
        else:
            control_transform = "aggregate"
            print("[STABILITY] control_transform='auto' but heterogeneity check skipped — defaulting to 'aggregate'.")

    break_tests = (
        run_level_slope_break_test(
            data=data,
            treated_units=treated_units,
            break_start=break_start,
            end=pseudo_test_end,
            alpha=alpha,
        ),
        run_treated_control_break_test(
            data=data,
            treated_units=treated_units,
            break_start=break_start,
            control_units=control_units,
            control_transform=control_transform,
            n_control_pcs=n_control_pcs,
            end=pseudo_test_end,
            alpha=alpha,
        ),
    )
    residual_drift_tests = run_residual_drift_test(
        data=data,
        treated_units=treated_units,
        train_end=train_end,
        pseudo_test_start=pseudo_test_start,
        pseudo_test_end=pseudo_test_end,
        estimators=estimators,
        fit_predict_fn=fit_predict_fn,
        alpha=alpha,
        log_label=log_label,
    )
    return CounterfactualStabilitySummary(
        break_tests=break_tests,
        residual_drift_tests=residual_drift_tests,
        break_candidates=tuple(candidates),
        control_heterogeneity=heterogeneity,
    )


def check_AugSynthCVXPY_weight_health(
    pds: PanelDataset,
    min_effective_donors: int = 5,
    concentration_threshold: float = 0.5,
) -> dict:
    """Diagnose AugSynthCVXPY SCM weight distribution for degeneracy or over-concentration.

    Fits AugSynthCVXPY on the given PanelDataset (applies treated aggregation if needed)
    and inspects the resulting donor weights.

    Parameters
    ----------
    pds : PanelDataset
        Panel dataset (typically the pseudo-test panel from build_pseudo_test_paneldataset).
    min_effective_donors : int
        Minimum number of donors with weight > 0.01 to be considered non-degenerate.
    concentration_threshold : float
        Maximum weight a single donor can have before being flagged as concentrated.

    Returns
    -------
    dict with keys: n_total_donors, n_effective_donors, max_weight, top3_weight_share,
                    weight_entropy, is_degenerate, verdict, notes
    """
    # Apply same aggregation as _default_fit_predict for consistency
    _pds = pds
    if len(_pds.treated_units) > 1:
        treated_agg = (
            _pds.wide_data.loc[_pds.treated_units]
            .sum(axis=0)
            .to_frame("__treated__")
            .T
        )
        ctrl = _pds.wide_data.drop(index=_pds.treated_units)
        agg_wide = pd.concat([treated_agg, ctrl])
        _pds = PanelDataset(
            wide_data=agg_wide,
            treated_periods=[_pds.treated_periods[0]],
            treated_units=["__treated__"],
        )

    model = AugSynthCVXPY(inference=None)
    model.fit_data(_pds)
    fitted = model.fit_model()

    donor_names = [u for u in _pds.wide_data.index if u not in _pds.treated_units]
    w_attr = getattr(fitted, "scm_weights", None)
    if w_attr is None:
        w_attr = getattr(fitted, "weights", None)
    if w_attr is None:
        raise AttributeError("Fitted model has neither scm_weights nor weights (unexpected AugSynthCVXPY Model).")
    weights = np.asarray(w_attr, dtype=np.float64).ravel()
    n_total = int(weights.size)
    n_effective = int(np.sum(weights > 0.01))
    max_w = float(weights.max())
    top3 = float(np.sort(weights)[::-1][:3].sum())
    entropy = float(-np.sum(weights * np.log(weights + 1e-12)))
    is_degenerate = n_effective < min_effective_donors or max_w > concentration_threshold

    if n_effective >= 10 and max_w < 0.3:
        verdict = "healthy"
        notes = (
            f"Weight distribution is healthy: {n_effective}/{n_total} active donors, "
            f"max_weight={max_w:.3f}, top3_share={top3:.3f}."
        )
    elif n_effective >= min_effective_donors and max_w < concentration_threshold:
        verdict = "concentrated"
        notes = (
            f"Weight distribution is moderately concentrated: {n_effective}/{n_total} active donors, "
            f"max_weight={max_w:.3f}. Synthetic control is relying on few donors."
        )
    else:
        verdict = "degenerate"
        notes = (
            f"Weight distribution is degenerate: only {n_effective}/{n_total} donors active, "
            f"max_weight={max_w:.3f}. SCM may be over-fitting to a single donor. "
            f"Consider using TBRRidge for stability diagnostics."
        )

    print(f"[STABILITY] AugSynthCVXPY weight verdict: {verdict}")
    print(f"[STABILITY] {notes}")

    return {
        "n_total_donors": n_total,
        "n_effective_donors": n_effective,
        "max_weight": max_w,
        "top3_weight_share": top3,
        "weight_entropy": entropy,
        "is_degenerate": is_degenerate,
        "verdict": verdict,
        "notes": notes,
        "weights": weights,
        "donor_names": donor_names,
    }


def compare_estimator_stability(
    residual_drift_results: Tuple[ResidualDriftTestResult, ...],
    bias_agreement_threshold: float = 0.2,
) -> dict:
    """Compare residual drift results across estimators.

    Parameters
    ----------
    residual_drift_results : tuple of ResidualDriftTestResult
    bias_agreement_threshold : float
        Threshold for bias_ratio below which estimators are considered to agree on bias level.

    Returns
    -------
    dict with keys: estimator_a, estimator_b, bias_ratio, rmse_ratio_gap,
                    agreement, both_centered, interpretation
    """
    results = list(residual_drift_results)
    if len(results) < 2:
        return {
            "estimator_a": results[0].estimator if results else "none",
            "estimator_b": "none",
            "bias_ratio": float("nan"),
            "rmse_ratio_gap": float("nan"),
            "agreement": "n/a",
            "both_centered": False,
            "interpretation": "run multiple estimators to enable comparison",
        }

    a, b = results[0], results[1]
    mean_a, mean_b = a.residual_mean, b.residual_mean
    denom = max(abs(mean_a), abs(mean_b), 1.0)
    bias_ratio = float(abs(mean_a - mean_b) / denom)

    rmse_a = a.rmse_ratio if a.rmse_ratio is not None else float("nan")
    rmse_b = b.rmse_ratio if b.rmse_ratio is not None else float("nan")
    rmse_ratio_gap = float(abs(rmse_a - rmse_b)) if np.isfinite(rmse_a) and np.isfinite(rmse_b) else float("nan")

    both_centered = a.residual_centered_flag and b.residual_centered_flag
    neither_centered = not a.residual_centered_flag and not b.residual_centered_flag
    agreement = "agree" if (both_centered or neither_centered) else "disagree"

    if both_centered:
        interpretation = "Both estimators centered: counterfactual likely stable"
    elif neither_centered:
        interpretation = "Both estimators biased: systematic level shift present"
    elif a.residual_centered_flag and not b.residual_centered_flag:
        interpretation = (
            f"Estimators disagree: {a.estimator} handles shock, {b.estimator} does not. "
            f"Use the centered estimator for main analysis."
        )
    else:
        interpretation = (
            f"Estimators disagree: {b.estimator} handles shock, {a.estimator} does not. "
            f"Use the centered estimator for main analysis."
        )

    return {
        "estimator_a": a.estimator,
        "estimator_b": b.estimator,
        "bias_ratio": bias_ratio,
        "rmse_ratio_gap": rmse_ratio_gap,
        "agreement": agreement,
        "both_centered": both_centered,
        "interpretation": interpretation,
    }


__all__ = [
    "StructuralBreakTestResult",
    "ResidualDriftTestResult",
    "ControlHeterogeneityResult",
    "CounterfactualStabilitySummary",
    "build_pseudo_test_paneldataset",
    "detect_break_candidates",
    "run_level_slope_break_test",
    "run_treated_control_break_test",
    "run_residual_drift_test",
    "run_control_heterogeneity_diagnostics",
    "run_counterfactual_stability_tests",
    "check_AugSynthCVXPY_weight_health",
    "compare_estimator_stability",
]
