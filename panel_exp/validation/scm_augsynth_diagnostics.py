"""SCM / AugSynthCVXPY diagnostic helpers (D5-DIAG-SCM-AUGSYNTH-001).

Descriptive, provisional diagnostics for Track D validation harnesses.
Does not change estimator or inference production behavior.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from panel_exp.methods.scm import AugSynthCVXPY, SyntheticControl
from panel_exp.panel_data import PanelDataset
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason

PANEL_DIAGNOSTIC_FIELDS: tuple[str, ...] = (
    "scm_pre_rmse",
    "scm_pre_rmse_normalized",
    "augsynth_pre_rmse",
    "augsynth_pre_rmse_normalized",
    "fit_improvement_rmse",
    "fit_improvement_relative",
    "donor_sparsity_n_control",
    "hull_min_donor_z_distance",
    "weight_herfindahl",
    "max_weight",
    "n_negative_weights",
    "effective_donor_count",
    "treated_pre_period_std",
    "donor_weighted_pre_period_std",
    "scale_bridge_ratio",
    "outcome_model_alpha",
    "outcome_model_coef_l2_norm",
    "outcome_model_available",
    "diagnostics_feasible",
)

INSTRUMENT_DIAGNOSTIC_FIELDS: tuple[str, ...] = (
    "false_confidence_flag",
    "narrow_interval_poor_fit_flag",
)

CONFLICT_DIAGNOSTIC_FIELDS: tuple[str, ...] = (
    "null_sign_disagreement",
    "null_material_point_mismatch",
    "null_point_effect_delta",
)


def pre_period_rmse(results: dict[str, Any], train_length: int) -> float:
    """Pre-period RMSE of fitted vs observed treated path."""
    y = np.asarray(results["y"], dtype=float)
    y_hat = np.asarray(results["y_hat"], dtype=float)
    if y.ndim == 2:
        y = np.nanmean(y, axis=1)
        y_hat = np.nanmean(y_hat, axis=1)
    pre = slice(0, min(train_length, y.shape[0]))
    err = y[pre] - y_hat[pre]
    if not np.any(np.isfinite(err)):
        return float("nan")
    return float(np.sqrt(np.nanmean(err**2)))


def treated_pre_period_std(panel: PanelDataset, train_length: int) -> float:
    if not panel.treated_units:
        return float("nan")
    wide = panel.wide_data
    pre_cols = list(panel.times[:train_length])
    treated = panel.treated_units[0]
    yt = wide.loc[treated, pre_cols].values.astype(float)
    if not np.any(np.isfinite(yt)):
        return float("nan")
    return float(np.nanstd(yt))


def normalized_pre_period_error(
    results: dict[str, Any],
    train_length: int,
    panel: PanelDataset,
) -> float:
    rmse = pre_period_rmse(results, train_length)
    denom = treated_pre_period_std(panel, train_length)
    if not np.isfinite(rmse) or not np.isfinite(denom) or denom <= 1e-12:
        return float("nan")
    return float(rmse / denom)


def hull_min_donor_z_distance(panel: PanelDataset, train_length: int) -> float:
    """Min z-scaled L2 distance from treated pre-profile to donor pre-profiles."""
    if not panel.treated_units or not panel.control_units:
        return float("nan")
    wide = panel.wide_data
    pre_cols = list(panel.times[:train_length])
    treated = panel.treated_units[0]
    yt = wide.loc[treated, pre_cols].values.astype(float)
    controls = panel.control_units
    X = wide.loc[controls, pre_cols].values.astype(float)
    if X.shape[0] == 0:
        return float("nan")
    mu = np.nanmean(X, axis=0)
    sd = np.nanstd(X, axis=0) + 1e-9
    z_t = (yt - mu) / sd
    z_c = (X - mu) / sd
    dists = [float(np.linalg.norm(z_t - z_c[i])) for i in range(X.shape[0])]
    return float(min(dists)) if dists else float("nan")


def _extract_scm_weights(aug_est: AugSynthCVXPY) -> np.ndarray | None:
    scm = getattr(aug_est, "scm", None)
    model = getattr(scm, "model", None) if scm is not None else None
    weights = getattr(model, "weights", None)
    if weights is None:
        return None
    arr = np.asarray(weights, dtype=float)
    if arr.ndim == 2:
        return arr[:, 0]
    return arr.reshape(-1)


def weight_diagnostics(weights: np.ndarray | None) -> dict[str, float]:
    unavailable = {
        "weight_herfindahl": float("nan"),
        "max_weight": float("nan"),
        "n_negative_weights": float("nan"),
        "effective_donor_count": float("nan"),
    }
    if weights is None:
        return unavailable
    arr = np.asarray(weights, dtype=float).reshape(-1)
    neg = int(np.sum(arr < -1e-9))
    abs_arr = np.abs(arr)
    pos = abs_arr[abs_arr > 1e-12]
    if pos.size == 0:
        return {
            "weight_herfindahl": float("nan"),
            "max_weight": float("nan"),
            "n_negative_weights": float(neg),
            "effective_donor_count": float("nan"),
        }
    p = pos / pos.sum()
    herf = float(np.sum(p**2))
    eff = float(1.0 / herf) if herf > 1e-12 else float("nan")
    return {
        "weight_herfindahl": herf,
        "max_weight": float(np.max(p)),
        "n_negative_weights": float(neg),
        "effective_donor_count": eff,
    }


def scale_bridge_pre_std_ratio(
    panel: PanelDataset,
    train_length: int,
    *,
    scm_weights: np.ndarray | None,
) -> dict[str, float]:
    """Treated pre-period std vs donor-weighted synthetic pre-period std (D10)."""
    out = {
        "treated_pre_period_std": treated_pre_period_std(panel, train_length),
        "donor_weighted_pre_period_std": float("nan"),
        "scale_bridge_ratio": float("nan"),
    }
    if not panel.treated_units or not panel.control_units:
        return out
    wide = panel.wide_data
    pre_cols = list(panel.times[:train_length])
    controls = panel.control_units
    X = wide.loc[controls, pre_cols].values.astype(float)
    if X.shape[0] == 0:
        return out

    if scm_weights is not None:
        w = np.asarray(scm_weights, dtype=float).reshape(-1)
        if w.shape[0] != X.shape[0]:
            w = w[: X.shape[0]]
        abs_w = np.abs(w)
        if abs_w.sum() > 1e-12:
            p = abs_w / abs_w.sum()
        else:
            p = np.full(X.shape[0], 1.0 / X.shape[0])
    else:
        p = np.full(X.shape[0], 1.0 / X.shape[0])

    synth = p @ X
    donor_std = float(np.nanstd(synth))
    out["donor_weighted_pre_period_std"] = donor_std
    treated_std = out["treated_pre_period_std"]
    if np.isfinite(treated_std) and np.isfinite(donor_std) and donor_std > 1e-12:
        out["scale_bridge_ratio"] = float(treated_std / donor_std)
    return out


def outcome_model_diagnostics(aug_est: AugSynthCVXPY) -> dict[str, float]:
    """Outcome-model descriptive fields (D8); no alternate refit."""
    out = {
        "outcome_model_alpha": float("nan"),
        "outcome_model_coef_l2_norm": float("nan"),
        "outcome_model_available": 0.0,
    }
    om = getattr(aug_est, "outcome_model", None)
    if om is None or not hasattr(om, "coef_"):
        return out
    coef = np.asarray(om.coef_, dtype=float)
    out["outcome_model_coef_l2_norm"] = float(np.linalg.norm(coef))
    out["outcome_model_alpha"] = float(getattr(om, "alpha", float("nan")))
    out["outcome_model_available"] = 1.0
    return out


def relative_fit_improvement(scm_rmse: float, augsynth_rmse: float) -> float:
    if not np.isfinite(scm_rmse) or not np.isfinite(augsynth_rmse) or scm_rmse <= 1e-12:
        return float("nan")
    return float((scm_rmse - augsynth_rmse) / scm_rmse)


def compute_method_disagreement(
    null_a26: dict[str, Any],
    null_aug: dict[str, Any],
    *,
    material_point_mismatch_threshold: float,
) -> dict[str, float]:
    a26_point = null_a26.get("mean_point_effect")
    aug_point = null_aug.get("mean_point_effect")
    feasible = bool(null_aug.get("feasible")) and a26_point is not None
    if not feasible:
        return {
            "null_sign_disagreement": float("nan"),
            "null_material_point_mismatch": float("nan"),
            "null_point_effect_delta": float("nan"),
        }
    a26_f = float(a26_point)
    aug_f = float(aug_point)
    delta = aug_f - a26_f
    return {
        "null_sign_disagreement": float(np.sign(aug_f) != np.sign(a26_f)),
        "null_material_point_mismatch": float(abs(delta) > material_point_mismatch_threshold),
        "null_point_effect_delta": float(delta),
    }


def false_confidence_flag(
    inst: dict[str, Any],
    panel_diagnostics: dict[str, Any],
    *,
    scm_rmse_weak_threshold: float = 1.0,
    hull_stress_threshold: float = 2.5,
    null_point_threshold: float = 0.03,
) -> float:
    """D11: large point effect with poor SCM fit and hull stress (provisional rule)."""
    point = abs(float(inst.get("mean_point_effect", 0.0)))
    if not np.isfinite(point) or point < null_point_threshold:
        return 0.0
    if not bool(inst.get("feasible")):
        return 0.0
    scm_rmse = float(panel_diagnostics.get("scm_pre_rmse", float("nan")))
    hull_z = float(panel_diagnostics.get("hull_min_donor_z_distance", float("nan")))
    poor_scm = np.isfinite(scm_rmse) and scm_rmse >= scm_rmse_weak_threshold
    hull_stress = np.isfinite(hull_z) and hull_z >= hull_stress_threshold
    return float(poor_scm and hull_stress)


def narrow_interval_poor_fit_flag(
    inst: dict[str, Any],
    panel_diagnostics: dict[str, Any],
    *,
    scm_rmse_weak_threshold: float = 1.0,
    hull_stress_threshold: float = 2.5,
    min_interval_halfwidth: float = 0.03,
) -> float:
    """Interval contradiction proxy: narrow band with poor pre-fit or hull stress."""
    if not bool(inst.get("feasible")):
        return 0.0
    halfwidth = inst.get("mean_interval_halfwidth", inst.get("mean_jk_halfwidth"))
    if halfwidth is None:
        return 0.0
    hw = float(halfwidth)
    if not np.isfinite(hw):
        return 0.0
    point = abs(float(inst.get("mean_point_effect", 0.0)))
    scm_rmse = float(panel_diagnostics.get("scm_pre_rmse", float("nan")))
    hull_z = float(panel_diagnostics.get("hull_min_donor_z_distance", float("nan")))
    poor_fit = (
        (np.isfinite(scm_rmse) and scm_rmse >= scm_rmse_weak_threshold)
        or (np.isfinite(hull_z) and hull_z >= hull_stress_threshold)
    )
    if not poor_fit:
        return 0.0
    narrow_ref = max(min_interval_halfwidth, point * 0.5) if point > 0 else min_interval_halfwidth
    return float(hw < narrow_ref)


def compute_instrument_diagnostics(
    inst: dict[str, Any],
    panel_diagnostics: dict[str, Any],
) -> dict[str, float]:
    return {
        "false_confidence_flag": false_confidence_flag(inst, panel_diagnostics),
        "narrow_interval_poor_fit_flag": narrow_interval_poor_fit_flag(
            inst, panel_diagnostics
        ),
    }


def _blocked_panel_diagnostics(
    panel: PanelDataset,
    *,
    train_length: int,
    min_donors: int,
    blocked_reason: str,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "scm_pre_rmse": float("nan"),
        "scm_pre_rmse_normalized": float("nan"),
        "augsynth_pre_rmse": float("nan"),
        "augsynth_pre_rmse_normalized": float("nan"),
        "fit_improvement_rmse": float("nan"),
        "fit_improvement_relative": float("nan"),
        "donor_sparsity_n_control": float(len(panel.control_units)),
        "hull_min_donor_z_distance": hull_min_donor_z_distance(panel, train_length),
        "weight_herfindahl": float("nan"),
        "max_weight": float("nan"),
        "n_negative_weights": float("nan"),
        "effective_donor_count": float("nan"),
        "treated_pre_period_std": treated_pre_period_std(panel, train_length),
        "donor_weighted_pre_period_std": float("nan"),
        "scale_bridge_ratio": float("nan"),
        "outcome_model_alpha": float("nan"),
        "outcome_model_coef_l2_norm": float("nan"),
        "outcome_model_available": 0.0,
        "diagnostics_feasible": 0.0,
        "blocked_reason": blocked_reason,
    }
    return out


def compute_panel_scm_augsynth_diagnostics(
    panel: PanelDataset,
    *,
    train_length: int,
    min_donors: int,
    alpha: float,
    percent_effect: float = 0.0,
    inject_percent_effect,
    mean_treated_baseline,
) -> dict[str, Any]:
    """Fit SCM + AugSynthCVXPY on a panel and emit panel-level diagnostics."""
    if len(panel.control_units) < min_donors:
        return _blocked_panel_diagnostics(
            panel,
            train_length=train_length,
            min_donors=min_donors,
            blocked_reason=f"insufficient_donors_need_{min_donors}",
        )
    skip = cvxpy_osqp_skip_reason()
    if skip:
        return _blocked_panel_diagnostics(
            panel,
            train_length=train_length,
            min_donors=min_donors,
            blocked_reason=skip,
        )

    out: dict[str, Any] = {
        "donor_sparsity_n_control": float(len(panel.control_units)),
        "hull_min_donor_z_distance": hull_min_donor_z_distance(panel, train_length),
        "treated_pre_period_std": treated_pre_period_std(panel, train_length),
        "diagnostics_feasible": 0.0,
    }
    out.update(
        {
            k: float("nan")
            for k in PANEL_DIAGNOSTIC_FIELDS
            if k not in out
        }
    )

    mean_value = mean_treated_baseline(panel)
    pds = inject_percent_effect(panel, percent_effect, mean_value)

    scm_weights: np.ndarray | None = None
    try:
        scm = SyntheticControl(inference=None, alpha=alpha)
        scm.run_analysis(pds)
        scm_results = scm.results or {}
        out["scm_pre_rmse"] = pre_period_rmse(scm_results, train_length)
        out["scm_pre_rmse_normalized"] = normalized_pre_period_error(
            scm_results, train_length, panel
        )
    except Exception as exc:
        out["scm_fit_error"] = type(exc).__name__
        return out

    try:
        aug = AugSynthCVXPY(inference=None, alpha=alpha, min_donors=min_donors)
        aug.run_analysis(pds)
        aug_results = aug.results or {}
        out["augsynth_pre_rmse"] = pre_period_rmse(aug_results, train_length)
        out["augsynth_pre_rmse_normalized"] = normalized_pre_period_error(
            aug_results, train_length, panel
        )
        scm_weights = _extract_scm_weights(aug)
        out.update(weight_diagnostics(scm_weights))
        out.update(outcome_model_diagnostics(aug))
        out.update(
            scale_bridge_pre_std_ratio(
                panel, train_length, scm_weights=scm_weights
            )
        )
        if np.isfinite(out["scm_pre_rmse"]) and np.isfinite(out["augsynth_pre_rmse"]):
            out["fit_improvement_rmse"] = float(
                out["scm_pre_rmse"] - out["augsynth_pre_rmse"]
            )
            out["fit_improvement_relative"] = relative_fit_improvement(
                float(out["scm_pre_rmse"]), float(out["augsynth_pre_rmse"])
            )
        out["diagnostics_feasible"] = 1.0
    except Exception as exc:
        out["augsynth_fit_error"] = type(exc).__name__
    return out
