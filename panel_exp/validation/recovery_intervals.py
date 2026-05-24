"""
Recovery interval extraction with explicit estimand alignment metadata.

Point estimates are scored as mean post-period relative ATT (``relative_att_post``).
Coverage and significance metrics use intervals/significance only when declared
aligned with that estimand.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple

import numpy as np

from panel_exp.panel_data import PanelDataset
from panel_exp.validation.did_interval_policy import DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED
from panel_exp.validation.runner import _path_relative_att

POINT_ESTIMAND = "relative_att_post"
INTERVAL_ESTIMAND_RELATIVE_ATT_POST = "relative_att_post"
INTERVAL_ESTIMAND_CUMULATIVE_ATT = "cumulative_att"
INTERVAL_ESTIMAND_PATH_LEVEL_Y = "path_level_y"
INTERVAL_ESTIMAND_UNAVAILABLE = "unavailable"

INTERVAL_SCALE_PATH_PERIOD_RELATIVE_MEAN = "path_period_relative_mean"
INTERVAL_SCALE_CUMULATIVE_ATT = "cumulative_att"
INTERVAL_SCALE_UNAVAILABLE = "unavailable"

SIGNIFICANCE_ESTIMAND_RELATIVE_ATT_POST = "relative_att_post"
SIGNIFICANCE_ESTIMAND_CUMULATIVE_ATT = "cumulative_att"
SIGNIFICANCE_ESTIMAND_UNAVAILABLE = "unavailable"

# Recovery skip when path outcome bounds are ordered y_lower > y_upper (Run 001 BRB failure).
PATH_INTERVAL_BOUNDS_INVERTED = "path_interval_bounds_inverted"


@dataclass(frozen=True)
class RecoveryIntervalExtraction:
    """Scalar interval for recovery with estimand alignment flags."""

    ci_lower: Optional[float]
    ci_upper: Optional[float]
    point_estimand: str
    interval_estimand: str
    interval_scale: str
    interval_aligned: bool
    unavailable_reason: Optional[str] = None
    significance_estimand: Optional[str] = None
    significance_aligned: bool = False
    significant: Optional[bool] = None


def _align_post_series(
    y: np.ndarray,
    y_hat: np.ndarray,
    y_lower: np.ndarray,
    y_upper: np.ndarray,
    panel: PanelDataset,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Align y / bounds to post-period 1d series (pooled over treated units when 2d)."""
    if y.ndim == 2:
        y = np.nanmean(y, axis=1)
        y_hat = np.nanmean(y_hat, axis=1)
        y_lower = np.nanmean(y_lower, axis=1)
        y_upper = np.nanmean(y_upper, axis=1)
    y = y.ravel()
    y_hat = y_hat.ravel()
    y_lower = y_lower.ravel()
    y_upper = y_upper.ravel()

    start = panel.treated_start_idxs[0]
    n_times = panel.num_timepoints
    n_post = n_times - start

    if len(y) == n_times and len(y_hat) == n_times:
        return y[start:], y_hat[start:], y_lower[start:], y_upper[start:]
    if len(y_hat) == n_post:
        y_post = y[start:] if len(y) == n_times else y[-n_post:]
        return y_post, y_hat, y_lower, y_upper
    n_align = min(len(y), len(y_hat), len(y_lower), len(y_upper), n_post)
    return y[-n_align:], y_hat[-n_align:], y_lower[-n_align:], y_upper[-n_align:]


def _path_relative_ci_from_results(
    estimator: Any,
    panel: PanelDataset,
) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Mean post-period relative ATT bounds from path ``y``, ``y_hat``, ``y_lower``, ``y_upper``.

    Uses the same period pooling as ``_path_relative_att`` and converts level bounds to
    per-period relative effects before averaging.
    """
    results = getattr(estimator, "results", None) or {}
    y = np.asarray(results.get("y", []), dtype=float)
    y_hat = np.asarray(results.get("y_hat", []), dtype=float)
    y_lo = np.asarray(results.get("y_lower", []), dtype=float)
    y_hi = np.asarray(results.get("y_upper", []), dtype=float)
    if y.size == 0 or y_hat.size == 0 or y_lo.size == 0 or y_hi.size == 0:
        return None, None, "no_path_intervals_in_results"

    try:
        y_post, yh_post, yl_post, yu_post = _align_post_series(
            y, y_hat, y_lo, y_hi, panel
        )
    except Exception:
        return None, None, "path_interval_alignment_failed"

    mask = (
        np.isfinite(y_post)
        & np.isfinite(yh_post)
        & np.isfinite(yl_post)
        & np.isfinite(yu_post)
        & (yh_post != 0)
    )
    if not np.any(mask):
        return None, None, "no_finite_post_periods"

    yl = yl_post[mask]
    yu = yu_post[mask]
    if float(np.nanmean(yl)) > float(np.nanmean(yu)):
        return None, None, PATH_INTERVAL_BOUNDS_INVERTED

    rel_lo = (y_post[mask] - yu) / yh_post[mask]
    rel_hi = (y_post[mask] - yl) / yh_post[mask]
    if not (np.any(np.isfinite(rel_lo)) and np.any(np.isfinite(rel_hi))):
        return None, None, "non_finite_relative_interval"
    lo = float(np.nanmean(rel_lo))
    hi = float(np.nanmean(rel_hi))
    if lo > hi:
        return None, None, PATH_INTERVAL_BOUNDS_INVERTED
    return lo, hi, None


def _is_did_estimator(estimator: Any) -> bool:
    return estimator.__class__.__name__ == "DID"


def _significance_from_pvalue(estimator: Any, alpha: float) -> Tuple[Optional[bool], str, bool]:
    pvalue = getattr(estimator, "treatment_pvalue", None)
    if pvalue is None:
        results = getattr(estimator, "results", None) or {}
        pvalue = results.get("p_value")
    if pvalue is None:
        return None, SIGNIFICANCE_ESTIMAND_UNAVAILABLE, False
    try:
        sig = bool(float(pvalue) < alpha)
    except (TypeError, ValueError):
        return None, SIGNIFICANCE_ESTIMAND_UNAVAILABLE, False
    if _is_did_estimator(estimator):
        return sig, SIGNIFICANCE_ESTIMAND_CUMULATIVE_ATT, False
    return sig, SIGNIFICANCE_ESTIMAND_RELATIVE_ATT_POST, True


def extract_recovery_interval(
    estimator: Any,
    panel: PanelDataset,
    *,
    alpha: float,
    significance_from_ci: bool,
    supports_significance: bool,
) -> RecoveryIntervalExtraction:
    """
    Extract recovery interval + significance with explicit estimand metadata.

    DID: ``treatment_ci`` and post-period ``y_lower``/``y_upper`` are not relative ATT
    intervals for the scored point estimand — marked unaligned. See
    ``did_interval_policy`` on DID results and ``DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED``.
    """
    point = POINT_ESTIMAND

    if _is_did_estimator(estimator):
        sig, sig_est, sig_aligned = (None, SIGNIFICANCE_ESTIMAND_UNAVAILABLE, False)
        if supports_significance:
            sig, sig_est, sig_aligned = _significance_from_pvalue(estimator, alpha)
        return RecoveryIntervalExtraction(
            ci_lower=None,
            ci_upper=None,
            point_estimand=point,
            interval_estimand=INTERVAL_ESTIMAND_CUMULATIVE_ATT,
            interval_scale=INTERVAL_SCALE_CUMULATIVE_ATT,
            interval_aligned=False,
            unavailable_reason=DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED,
            significance_estimand=sig_est,
            significance_aligned=sig_aligned,
            significant=sig,
        )

    lo, hi, path_reason = _path_relative_ci_from_results(estimator, panel)
    if (
        lo is not None
        and hi is not None
        and np.isfinite(lo)
        and np.isfinite(hi)
        and lo <= hi
    ):
        sig = None
        sig_est = SIGNIFICANCE_ESTIMAND_UNAVAILABLE
        sig_aligned = False
        if supports_significance:
            if significance_from_ci:
                sig = bool(lo > 0.0 or hi < 0.0)
                sig_est = SIGNIFICANCE_ESTIMAND_RELATIVE_ATT_POST
                sig_aligned = True
            else:
                sig, sig_est, sig_aligned = _significance_from_pvalue(estimator, alpha)
        return RecoveryIntervalExtraction(
            ci_lower=lo,
            ci_upper=hi,
            point_estimand=point,
            interval_estimand=INTERVAL_ESTIMAND_RELATIVE_ATT_POST,
            interval_scale=INTERVAL_SCALE_PATH_PERIOD_RELATIVE_MEAN,
            interval_aligned=True,
            unavailable_reason=None,
            significance_estimand=sig_est,
            significance_aligned=sig_aligned,
            significant=sig,
        )

    # Path bounds present but not convertible
    results = getattr(estimator, "results", None) or {}
    has_path_bounds = bool(
        results.get("y_lower") is not None and results.get("y_upper") is not None
    )
    interval_estimand = (
        INTERVAL_ESTIMAND_PATH_LEVEL_Y if has_path_bounds else INTERVAL_ESTIMAND_UNAVAILABLE
    )
    interval_scale = INTERVAL_SCALE_UNAVAILABLE
    reason = path_reason or "interval_estimand_mismatch"

    sig, sig_est, sig_aligned = (None, SIGNIFICANCE_ESTIMAND_UNAVAILABLE, False)
    if supports_significance and not significance_from_ci:
        sig, sig_est, sig_aligned = _significance_from_pvalue(estimator, alpha)

    return RecoveryIntervalExtraction(
        ci_lower=None,
        ci_upper=None,
        point_estimand=point,
        interval_estimand=interval_estimand,
        interval_scale=interval_scale,
        interval_aligned=False,
        unavailable_reason=reason,
        significance_estimand=sig_est,
        significance_aligned=sig_aligned,
        significant=sig,
    )


def verify_point_interval_alignment(
    estimator: Any,
    panel: PanelDataset,
) -> bool:
    """True when path relative point and aligned interval bracket the same estimand."""
    point = _path_relative_att(estimator, panel)
    extraction = extract_recovery_interval(
        estimator,
        panel,
        alpha=0.05,
        significance_from_ci=False,
        supports_significance=False,
    )
    if not extraction.interval_aligned:
        return False
    if extraction.ci_lower is None or extraction.ci_upper is None:
        return False
    if not np.isfinite(point):
        return False
    return extraction.ci_lower <= point <= extraction.ci_upper
