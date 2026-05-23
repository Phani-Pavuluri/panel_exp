"""
Review-only stability flags derived from post-fit diagnostics.

Flags are advisory (ok / warn / fail / bool / unavailable). They do not change
estimates, block runs, or attach to default ``run_analysis`` output.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Tuple, Union

import numpy as np

from panel_exp.diagnostics.estimator_diagnostics import (
    _SCM_WEIGHT_ESTIMATORS,
    _donor_weight_summary,
    _posterior_convergence,
    _pre_period_residual_summary,
    _pretrend_contract_section,
    _results_y_y_hat,
    _trop_donor_support,
    classify_estimator,
)

ReviewFlagValue = Union[bool, str]
LevelFlag = str  # "ok" | "warn" | "fail" | "unavailable"

_ALL_REVIEW_FLAGS: Tuple[str, ...] = (
    "residual_drift",
    "high_donor_concentration",
    "donor_instability",
    "coefficient_instability",
    "fold_instability",
    "pretrend_violation",
    "pretrend_assessment_unavailable",
    "weak_donor_pool",
    "posterior_divergence",
    "mcmc_convergence",
)

_MAX_DONOR_WEIGHT_WARN = 0.50
_MIN_ACTIVE_DONORS_WARN = 3
_TOP3_WEIGHT_SHARE_WARN = 0.85
_RESIDUAL_SLOPE_WARN = 0.35
_RESIDUAL_SLOPE_FAIL = 0.75
_POST_PRE_RMSE_RATIO_WARN = 2.0
_POST_PRE_RMSE_RATIO_FAIL = 3.5
_COEF_DOMINANCE_WARN = 8.0
_COEF_DOMINANCE_FAIL = 16.0
_PRE_CI_WIDTH_RATIO_WARN = 0.35
_PRE_CI_WIDTH_RATIO_FAIL = 0.70
_MCMC_DIVERGENCE_RATE_WARN = 0.01
_MCMC_MAX_RHAT_WARN = 1.01

_TBRIDGE_NAMES = frozenset({"TBR", "TBRRidge"})
_COUNTERFACTUAL_NAMES = frozenset(
    {
        "SyntheticControl",
        "SyntheticControlCVXPY",
        "AugSynth",
        "AugSynthCVXPY",
        "TBR",
        "TBRRidge",
        "SyntheticDID",
        "TROP",
    }
)


def _path_series_1d(
    results: Mapping[str, Any],
    panel: Any,
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """Pool multi-column ``y`` / ``y_hat`` to one series per time when needed."""
    y = results.get("y")
    y_hat = results.get("y_hat")
    if y is None or y_hat is None:
        return None, None
    ya = np.asarray(y, dtype=np.float64)
    yha = np.asarray(y_hat, dtype=np.float64)
    if ya.ndim == 2:
        ya = np.nanmean(ya, axis=1)
    if yha.ndim == 2:
        yha = np.nanmean(yha, axis=1)
    ya = ya.ravel()
    yha = yha.ravel()
    if ya.size != panel.num_timepoints or yha.size != panel.num_timepoints:
        return None, None
    return ya, yha


def _pre_period_residual_summary_pooled(
    analyzer: Any,
    results: Mapping[str, Any],
) -> Dict[str, Any]:
    panel = getattr(analyzer, "panel_data", None)
    if panel is None:
        return {"available": False, "reason": "no_panel_data"}
    y, y_hat = _path_series_1d(results, panel)
    if y is None:
        return {"available": False, "reason": "missing_y_or_y_hat_or_path_length_mismatch"}
    t0 = int(panel.treated_start_idxs[0])
    if t0 < 2:
        return {"available": False, "reason": "insufficient_pre_periods", "n_pre": t0}
    resid = y[:t0] - y_hat[:t0]
    if not np.all(np.isfinite(resid)):
        return {"available": False, "reason": "non_finite_pre_residuals"}
    x = np.arange(t0, dtype=np.float64)
    slope = float(np.polyfit(x, resid, 1)[0]) if t0 >= 2 else float("nan")
    return {
        "available": True,
        "n_pre": t0,
        "rmse": float(np.sqrt(np.mean(resid**2))),
        "mae": float(np.mean(np.abs(resid))),
        "mean_residual": float(np.mean(resid)),
        "residual_slope": slope,
        "max_abs_residual": float(np.max(np.abs(resid))),
    }


def _level_max(a: LevelFlag, b: LevelFlag) -> LevelFlag:
    order = {"unavailable": -1, "ok": 0, "warn": 1, "fail": 2}
    return a if order.get(a, 0) >= order.get(b, 0) else b


def _residual_drift_from_pre(
    pre: Mapping[str, Any],
    *,
    post_pre_level: LevelFlag,
) -> LevelFlag:
    if not pre.get("available"):
        return "unavailable"
    slope = float(pre.get("residual_slope", float("nan")))
    rmse = float(pre.get("rmse", float("nan")))
    if not (slope == slope and rmse == rmse and rmse > 0):
        return "unavailable"
    normalized = abs(slope) / rmse
    level: LevelFlag = "ok"
    if normalized >= _RESIDUAL_SLOPE_FAIL:
        level = "fail"
    elif normalized >= _RESIDUAL_SLOPE_WARN:
        level = "warn"
    return _level_max(level, post_pre_level)


def _post_pre_residual_level(analyzer: Any, results: Mapping[str, Any]) -> LevelFlag:
    panel = getattr(analyzer, "panel_data", None)
    if panel is None:
        return "unavailable"
    y, y_hat = _path_series_1d(results, panel)
    if y is None or y_hat is None:
        return "unavailable"
    t0 = int(panel.treated_start_idxs[0])
    if t0 < 2 or y.size <= t0:
        return "unavailable"
    pre = y[:t0] - y_hat[:t0]
    post = y[t0:] - y_hat[t0:]
    pre_rmse = float(np.sqrt(np.mean(pre**2)))
    post_rmse = float(np.sqrt(np.mean(post**2)))
    if pre_rmse < 1e-12:
        return "unavailable"
    ratio = post_rmse / pre_rmse
    if ratio >= _POST_PRE_RMSE_RATIO_FAIL:
        return "fail"
    if ratio >= _POST_PRE_RMSE_RATIO_WARN:
        return "warn"
    return "ok"


def _donor_flags_from_summary(donor: Mapping[str, Any]) -> Dict[str, ReviewFlagValue]:
    out: Dict[str, ReviewFlagValue] = {
        "high_donor_concentration": "unavailable",
        "donor_instability": "unavailable",
    }
    if not donor.get("available"):
        return out

    if donor.get("weight_kind") == "scm_simplex" and "per_treated" in donor:
        per = donor["per_treated"]
        if isinstance(per, list) and per:
            max_w = max(float(p.get("max_weight", float("nan"))) for p in per)
            top3_share = max(
                float(p.get("top3_weight_share", float("nan"))) for p in per
            )
            n_active = min(int(p.get("n_active_donors", 0)) for p in per)
        else:
            return out
    else:
        max_w = float(donor.get("max_weight", float("nan")))
        raw_top3 = donor.get("top3_weight_share")
        top3_share = float(raw_top3) if raw_top3 is not None else float("nan")
        n_active = int(donor.get("n_active_donors", 0))

    concentrated = False
    if max_w == max_w:
        concentrated = max_w > _MAX_DONOR_WEIGHT_WARN
    if top3_share == top3_share:
        concentrated = concentrated or top3_share > _TOP3_WEIGHT_SHARE_WARN
    out["high_donor_concentration"] = concentrated

    unstable = n_active < _MIN_ACTIVE_DONORS_WARN
    out["donor_instability"] = unstable
    return out


def _coefficient_instability_flag(analyzer: Any, name: str) -> LevelFlag:
    if name not in _TBRIDGE_NAMES:
        return "unavailable"
    model = getattr(analyzer, "model", None)
    coef = getattr(model, "coef_", None) if model is not None else None
    if coef is None:
        return "unavailable"
    c = np.asarray(coef, dtype=np.float64).ravel()
    if c.size == 0 or not np.all(np.isfinite(c)):
        return "unavailable"
    mean_abs = float(np.mean(np.abs(c)))
    if mean_abs < 1e-12:
        return "unavailable"
    dominance = float(np.max(np.abs(c)) / mean_abs)
    if dominance >= _COEF_DOMINANCE_FAIL:
        return "fail"
    if dominance >= _COEF_DOMINANCE_WARN:
        return "warn"
    return "ok"


def _fold_instability_flag(analyzer: Any, results: Mapping[str, Any]) -> LevelFlag:
    inference = getattr(analyzer, "inference", None)
    inf_name = getattr(inference, "__name__", str(inference or "")).lower()
    if "fold" not in inf_name and "kfold" not in inf_name:
        return "unavailable"
    panel = getattr(analyzer, "panel_data", None)
    y_hat = results.get("y_hat")
    y_lower = results.get("y_lower")
    y_upper = results.get("y_upper")
    if panel is None or y_hat is None or y_lower is None or y_upper is None:
        return "unavailable"
    t0 = int(panel.treated_start_idxs[0])
    yh = np.asarray(y_hat, dtype=np.float64).ravel()
    lo = np.asarray(y_lower, dtype=np.float64).ravel()
    hi = np.asarray(y_upper, dtype=np.float64).ravel()
    if t0 < 2 or yh.size < t0:
        return "unavailable"
    width = hi[:t0] - lo[:t0]
    scale = np.abs(yh[:t0]) + 1e-8
    rel = width / scale
    if not np.all(np.isfinite(rel)):
        return "unavailable"
    med = float(np.median(rel))
    if med > _PRE_CI_WIDTH_RATIO_FAIL:
        return "fail"
    if med > _PRE_CI_WIDTH_RATIO_WARN:
        return "warn"
    return "ok"


def _pretrend_flags(results: Mapping[str, Any]) -> Dict[str, ReviewFlagValue]:
    section = _pretrend_contract_section(results)
    out: Dict[str, ReviewFlagValue] = {
        "pretrend_violation": "unavailable",
        "pretrend_assessment_unavailable": False,
    }
    if not section.get("available"):
        out["pretrend_assessment_unavailable"] = True
        return out
    contract = section.get("contract") or {}
    status = str(contract.get("status", "unavailable"))
    if status == "unavailable":
        out["pretrend_assessment_unavailable"] = True
        out["pretrend_violation"] = "unavailable"
    elif status == "fail":
        out["pretrend_violation"] = "fail"
    elif status == "warn":
        out["pretrend_violation"] = "warn"
    else:
        out["pretrend_violation"] = "ok"
    return out


def _trop_weak_donor_flag(analyzer: Any) -> ReviewFlagValue:
    trop = _trop_donor_support(analyzer)
    if not trop.get("available"):
        return "unavailable"
    return bool(trop.get("weak_donor", False))


def _posterior_flags(analyzer: Any) -> Dict[str, ReviewFlagValue]:
    post = _posterior_convergence(analyzer)
    out: Dict[str, ReviewFlagValue] = {
        "posterior_divergence": "unavailable",
        "mcmc_convergence": "unavailable",
    }
    if not post.get("available"):
        return out
    div_rate = post.get("divergence_rate")
    if div_rate is not None and div_rate == div_rate:
        out["posterior_divergence"] = "warn" if float(div_rate) > _MCMC_DIVERGENCE_RATE_WARN else "ok"
    max_rhat = post.get("max_rhat")
    if max_rhat is not None and max_rhat == max_rhat:
        out["mcmc_convergence"] = (
            "warn" if float(max_rhat) > _MCMC_MAX_RHAT_WARN else "ok"
        )
    elif post.get("arviz_available") is False:
        out["mcmc_convergence"] = "unavailable"
    return out


def classify_review_flag_support(
    estimator: Union[str, type, Any],
) -> Dict[str, Any]:
    """
    Classify which review flags apply to an estimator family and why others do not.

    Returns ``classification`` (diagnostic profile), ``supported`` flag names, and
    ``unsupported`` mapping flag → reason string.
    """
    profile = classify_estimator(estimator)
    name = profile.estimator
    supported: List[str] = []
    unsupported: Dict[str, str] = {}

    def _mark(flag: str, *, ok: bool, reason: str) -> None:
        if ok:
            if flag not in supported:
                supported.append(flag)
        else:
            unsupported[flag] = reason

    for flag in _ALL_REVIEW_FLAGS:
        if flag == "residual_drift":
            _mark(
                flag,
                ok=profile.explicit_y_hat and profile.pre_period_residuals,
                reason="requires_path_y_and_y_hat_with_pre_period",
            )
        elif flag in ("high_donor_concentration", "donor_instability"):
            has_weights = (
                profile.donor_control_weights
                or name in _SCM_WEIGHT_ESTIMATORS
                or name == "SyntheticDID"
            )
            if name == "AugSynth":
                _mark(flag, ok=False, reason="simplex_donor_weights_not_exported")
            elif name == "TROP":
                _mark(flag, ok=False, reason="use_weak_donor_pool_not_simplex_weights")
            elif name in _TBRIDGE_NAMES or name == "DID":
                _mark(flag, ok=False, reason="estimator_has_no_donor_weight_vector")
            else:
                _mark(flag, ok=has_weights, reason="donor_weights_not_defined_for_family")
        elif flag == "coefficient_instability":
            _mark(
                flag,
                ok=name in _TBRIDGE_NAMES,
                reason="requires_ridge_or_ols_coefficient_vector",
            )
        elif flag == "fold_instability":
            _mark(
                flag,
                ok=name == "TBRRidge",
                reason="only_meaningful_for_tbrridge_with_kfold_inference",
            )
        elif flag == "pretrend_violation":
            _mark(
                flag,
                ok=profile.primary_diagnostic == "pretrend_contract",
                reason="did_pretrend_contract_only",
            )
        elif flag == "pretrend_assessment_unavailable":
            _mark(
                flag,
                ok=profile.primary_diagnostic == "pretrend_contract",
                reason="did_pretrend_contract_only",
            )
        elif flag == "weak_donor_pool":
            _mark(flag, ok=name == "TROP", reason="trop_fit_diagnostics_only")
        elif flag in ("posterior_divergence", "mcmc_convergence"):
            _mark(
                flag,
                ok=profile.primary_diagnostic == "posterior_convergence",
                reason="requires_bayesian_mcmc_fit",
            )

    if profile.primary_diagnostic == "unsupported":
        for flag in list(supported):
            supported.remove(flag)
        for flag in _ALL_REVIEW_FLAGS:
            if flag not in unsupported:
                unsupported[flag] = "estimator_family_unsupported"

    return {
        "estimator": name,
        "classification": profile.to_dict(),
        "supported": supported,
        "unsupported": unsupported,
    }


def _compute_flag_values(
    analyzer: Any,
    results: Mapping[str, Any],
    *,
    support: Mapping[str, Any],
) -> Dict[str, ReviewFlagValue]:
    name = support["estimator"]
    supported = set(support.get("supported") or [])
    flags: Dict[str, ReviewFlagValue] = {}

    post_pre = (
        _post_pre_residual_level(analyzer, results)
        if "residual_drift" in supported
        else "unavailable"
    )
    if "residual_drift" in supported:
        pre = _pre_period_residual_summary_pooled(analyzer, results)
        if not pre.get("available"):
            pre = _pre_period_residual_summary(analyzer, results)
        flags["residual_drift"] = _residual_drift_from_pre(
            pre, post_pre_level=post_pre
        )

    if "high_donor_concentration" in supported or "donor_instability" in supported:
        donor = _donor_weight_summary(analyzer, name)
        donor_flags = _donor_flags_from_summary(donor)
        for key in ("high_donor_concentration", "donor_instability"):
            if key in supported:
                flags[key] = donor_flags.get(key, "unavailable")

    if "coefficient_instability" in supported:
        flags["coefficient_instability"] = _coefficient_instability_flag(
            analyzer, name
        )

    if "fold_instability" in supported:
        flags["fold_instability"] = _fold_instability_flag(analyzer, results)

    if "pretrend_violation" in supported or "pretrend_assessment_unavailable" in supported:
        pretrend = _pretrend_flags(results)
        for key in ("pretrend_violation", "pretrend_assessment_unavailable"):
            if key in supported:
                flags[key] = pretrend.get(key, "unavailable")

    if "weak_donor_pool" in supported:
        flags["weak_donor_pool"] = _trop_weak_donor_flag(analyzer)

    if "posterior_divergence" in supported or "mcmc_convergence" in supported:
        post_flags = _posterior_flags(analyzer)
        for key in ("posterior_divergence", "mcmc_convergence"):
            if key in supported:
                flags[key] = post_flags.get(key, "unavailable")

    return flags


def collect_review_flags(
    analyzer: Any,
    results: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build review flags and support metadata for a fitted estimator.

    Only flags with valid inputs for the estimator family are computed; others
    appear under ``review_flag_support["unsupported"]`` with reasons.
    """
    resolved = results if results is not None else getattr(analyzer, "results", None)
    if resolved is None:
        raise ValueError(
            "collect_review_flags requires results or analyzer.results after run_analysis."
        )
    support = classify_review_flag_support(analyzer)
    flags = _compute_flag_values(analyzer, resolved, support=support)
    return {
        "estimator": support["estimator"],
        "classification": support["classification"],
        "review_flag_support": {
            "supported": list(support["supported"]),
            "unsupported": dict(support["unsupported"]),
        },
        "review_flags": flags,
    }


def attach_review_flags(
    results: MutableMapping[str, Any],
    payload: Mapping[str, Any],
) -> None:
    """Attach ``review_flags`` (and support metadata) to a results mapping (opt-in)."""
    results["review_flags"] = dict(payload.get("review_flags") or {})
    results["review_flag_support"] = dict(payload.get("review_flag_support") or {})


__all__ = [
    "collect_review_flags",
    "classify_review_flag_support",
    "attach_review_flags",
]
