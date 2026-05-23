"""
Estimator diagnostic classification and post-fit routing.

Each profile records which diagnostic inputs exist for an estimator family and which
diagnostic type is primary. ``attach_estimator_diagnostics`` only populates sections
when inputs are valid (no blocking; additive metadata on ``results``).

Classification (y_hat / pre residuals / donor weights / rolling pre-fit / primary type)
---------------------------------------------------------------------------------------

| Estimator                 | y_hat | pre resid | weights      | rolling pre-fit | primary diagnostic        |
|---------------------------|-------|-----------|--------------|-----------------|---------------------------|
| SyntheticControl          | yes   | yes       | yes (simplex)| yes             | counterfactual stability  |
| SyntheticControlCVXPY     | yes   | yes       | yes          | yes             | counterfactual + donor    |
| AugSynth                  | yes   | yes       | partial      | yes             | counterfactual stability  |
| AugSynthCVXPY             | yes   | yes       | yes          | yes             | counterfactual + donor    |
| TBR                       | yes*  | yes*      | no (OLS)     | limited*        | counterfactual stability  |
| TBRRidge                  | yes   | yes       | no (ridge)   | yes             | counterfactual stability  |
| DID                       | yes   | via tests | no           | yes             | pretrend contract         |
| SyntheticDID              | yes   | yes       | omega, lam   | yes             | donor support             |
| TROP                      | yes   | yes       | unit/time W  | partial         | donor support             |
| BayesianTBR               | yes†  | yes†      | posterior β  | no              | posterior convergence     |
| BayesianTBRHorseShoe      | yes†  | yes†      | posterior β  | no              | posterior convergence     |
| MTGP                      | no‡   | partial‡  | latent GP    | no              | posterior / unsupported   |

* TBR requires a single pre-aggregated treated and control unit.
† Requires a completed MCMC fit on the analyzer object.
‡ Standard ``run_analysis`` does not export a path-level ``y_hat``; use MCMC / ``y_inf`` separately.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Optional, Union

import numpy as np

from panel_exp.utils.counterfactual_stability_tests import (
    _ALLOWED_STABILITY_INFERENCE,
    check_AugSynthCVXPY_weight_health,
)

DiagnosticType = str

_PROFILE_KEYS = (
    "SyntheticControl",
    "SyntheticControlCVXPY",
    "AugSynth",
    "AugSynthCVXPY",
    "TBR",
    "TBRRidge",
    "DID",
    "SyntheticDID",
    "TROP",
    "BayesianTBR",
    "BayesianTBRHorseShoe",
    "MTGP",
)


@dataclass(frozen=True)
class EstimatorDiagnosticProfile:
    """Which diagnostic inputs exist for an estimator class name."""

    estimator: str
    explicit_y_hat: bool
    pre_period_residuals: bool
    donor_control_weights: bool
    rolling_pre_fit_meaningful: bool
    primary_diagnostic: DiagnosticType

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _profile(
    name: str,
    *,
    y_hat: bool,
    pre_resid: bool,
    weights: bool,
    rolling: bool,
    primary: DiagnosticType,
) -> EstimatorDiagnosticProfile:
    return EstimatorDiagnosticProfile(
        estimator=name,
        explicit_y_hat=y_hat,
        pre_period_residuals=pre_resid,
        donor_control_weights=weights,
        rolling_pre_fit_meaningful=rolling,
        primary_diagnostic=primary,
    )


ESTIMATOR_DIAGNOSTIC_PROFILES: Dict[str, EstimatorDiagnosticProfile] = {
    "SyntheticControl": _profile(
        "SyntheticControl",
        y_hat=True,
        pre_resid=True,
        weights=True,
        rolling=True,
        primary="counterfactual_stability",
    ),
    "SyntheticControlCVXPY": _profile(
        "SyntheticControlCVXPY",
        y_hat=True,
        pre_resid=True,
        weights=True,
        rolling=True,
        primary="counterfactual_stability",
    ),
    "AugSynth": _profile(
        "AugSynth",
        y_hat=True,
        pre_resid=True,
        weights=False,
        rolling=True,
        primary="counterfactual_stability",
    ),
    "AugSynthCVXPY": _profile(
        "AugSynthCVXPY",
        y_hat=True,
        pre_resid=True,
        weights=True,
        rolling=True,
        primary="counterfactual_stability",
    ),
    "TBR": _profile(
        "TBR",
        y_hat=True,
        pre_resid=True,
        weights=False,
        rolling=False,
        primary="counterfactual_stability",
    ),
    "TBRRidge": _profile(
        "TBRRidge",
        y_hat=True,
        pre_resid=True,
        weights=False,
        rolling=True,
        primary="counterfactual_stability",
    ),
    "DID": _profile(
        "DID",
        y_hat=True,
        pre_resid=True,
        weights=False,
        rolling=True,
        primary="pretrend_contract",
    ),
    "SyntheticDID": _profile(
        "SyntheticDID",
        y_hat=True,
        pre_resid=True,
        weights=True,
        rolling=True,
        primary="donor_support",
    ),
    "TROP": _profile(
        "TROP",
        y_hat=True,
        pre_resid=True,
        weights=True,
        rolling=False,
        primary="donor_support",
    ),
    "BayesianTBR": _profile(
        "BayesianTBR",
        y_hat=True,
        pre_resid=True,
        weights=False,
        rolling=False,
        primary="posterior_convergence",
    ),
    "BayesianTBRHorseShoe": _profile(
        "BayesianTBRHorseShoe",
        y_hat=True,
        pre_resid=True,
        weights=False,
        rolling=False,
        primary="posterior_convergence",
    ),
    "MTGP": _profile(
        "MTGP",
        y_hat=False,
        pre_resid=False,
        weights=False,
        rolling=False,
        primary="unsupported",
    ),
}

_SCM_WEIGHT_ESTIMATORS = frozenset(
    {
        "SyntheticControl",
        "SyntheticControlCVXPY",
        "AugSynthCVXPY",
    }
)
_AUGSYNTH_WEIGHT_HEALTH = frozenset({"AugSynthCVXPY"})


def classify_estimator(estimator: Union[str, type, Any]) -> EstimatorDiagnosticProfile:
    """Return the diagnostic profile for an estimator class name or instance."""
    if isinstance(estimator, str):
        name = estimator
    elif isinstance(estimator, type):
        name = estimator.__name__
    else:
        name = estimator.__class__.__name__
    try:
        return ESTIMATOR_DIAGNOSTIC_PROFILES[name]
    except KeyError as exc:
        raise KeyError(
            f"Unknown estimator {name!r}; known: {sorted(ESTIMATOR_DIAGNOSTIC_PROFILES)}"
        ) from exc


def _results_y_y_hat(results: Mapping[str, Any]) -> tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    y = results.get("y")
    y_hat = results.get("y_hat")
    if y is None or y_hat is None:
        return None, None
    ya = np.asarray(y, dtype=np.float64).ravel()
    yha = np.asarray(y_hat, dtype=np.float64).ravel()
    if ya.size == 0 or yha.size == 0:
        return None, None
    return ya, yha


def _pre_period_residual_summary(
    analyzer: Any,
    results: Mapping[str, Any],
) -> Dict[str, Any]:
    panel = getattr(analyzer, "panel_data", None)
    if panel is None:
        return {"available": False, "reason": "no_panel_data"}
    y, y_hat = _results_y_y_hat(results)
    if y is None:
        return {"available": False, "reason": "missing_y_or_y_hat"}
    t0 = int(panel.treated_start_idxs[0])
    if y.size != panel.num_timepoints or y_hat.size != panel.num_timepoints:
        return {
            "available": False,
            "reason": "path_length_mismatch",
            "n_y": int(y.size),
            "n_times": int(panel.num_timepoints),
        }
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


def _stability_inference_ok(analyzer: Any) -> bool:
    return getattr(analyzer, "inference", None) in _ALLOWED_STABILITY_INFERENCE


def _extract_scm_weights(analyzer: Any) -> Optional[np.ndarray]:
    model = getattr(analyzer, "model", None)
    for attr in ("weights", "scm_weights"):
        w = getattr(model, attr, None)
        if w is not None:
            return np.asarray(w, dtype=np.float64)
    w = getattr(analyzer, "weights", None)
    if w is not None:
        return np.asarray(w, dtype=np.float64)
    scm = getattr(analyzer, "scm", None)
    if scm is not None:
        inner = getattr(scm, "model", None)
        w = getattr(inner, "weights", None) if inner is not None else None
        if w is not None:
            return np.asarray(w, dtype=np.float64)
    return None


def _donor_weight_summary(analyzer: Any, name: str) -> Dict[str, Any]:
    if name not in _SCM_WEIGHT_ESTIMATORS and name != "SyntheticDID":
        return {"available": False, "reason": "estimator_has_no_simplex_donor_weights"}

    if name == "SyntheticDID":
        omega = getattr(analyzer, "_omega", None)
        lam = getattr(analyzer, "_lam", None)
        if omega is None:
            return {"available": False, "reason": "missing_omega"}
        ow = np.asarray(omega, dtype=np.float64).ravel()
        out: Dict[str, Any] = {
            "available": True,
            "weight_kind": "sdid_unit_omega",
            "n_donors": int(ow.size),
            "n_active_donors": int(np.sum(ow > 1e-6)),
            "max_weight": float(np.max(ow)),
            "entropy": float(-np.sum(ow * np.log(ow + 1e-12))),
        }
        if lam is not None:
            lw = np.asarray(lam, dtype=np.float64).ravel()
            out["time_weights_n_active"] = int(np.sum(lw > 1e-6))
            out["time_weights_max"] = float(np.max(lw))
        return out

    weights = _extract_scm_weights(analyzer)
    if weights is None:
        return {"available": False, "reason": "weights_not_on_analyzer"}
    w = np.abs(weights)
    if w.ndim == 2:
        summaries = []
        for j in range(w.shape[1]):
            col = w[:, j]
            col = col / col.sum() if col.sum() > 0 else col
            summaries.append(_weight_vector_stats(col))
        return {
            "available": True,
            "weight_kind": "scm_simplex",
            "n_treated_columns": int(w.shape[1]),
            "per_treated": summaries,
        }
    col = w.ravel()
    col = col / col.sum() if col.sum() > 0 else col
    return {"available": True, "weight_kind": "scm_simplex", **_weight_vector_stats(col)}


def _weight_vector_stats(w: np.ndarray) -> Dict[str, Any]:
    w = np.asarray(w, dtype=np.float64).ravel()
    w = w / w.sum() if w.sum() > 0 else w
    sorted_w = np.sort(w)[::-1]
    top3 = float(sorted_w[: min(3, sorted_w.size)].sum())
    return {
        "n_donors": int(w.size),
        "n_active_donors": int(np.sum(w > 0.01)),
        "max_weight": float(w.max()) if w.size else float("nan"),
        "top3_weight_share": top3,
        "entropy": float(-np.sum(w * np.log(w + 1e-12))),
    }


def _trop_donor_support(analyzer: Any) -> Dict[str, Any]:
    diag = getattr(analyzer, "fit_diagnostics_", None)
    if not isinstance(diag, Mapping):
        return {"available": False, "reason": "fit_diagnostics_missing"}
    keys = (
        "donor_support_min",
        "donor_unit_weight_mass_on_controls",
        "n_control_units_positive_unit_weight",
        "unstable_zero_support",
    )
    out = {k: diag.get(k) for k in keys if k in diag}
    out["available"] = True
    out["weak_donor"] = bool(diag.get("unstable_zero_support", False))
    return out


def _pretrend_contract_section(results: Mapping[str, Any]) -> Dict[str, Any]:
    contract = results.get("did_pretrend_contract")
    if contract is None:
        return {"available": False, "reason": "did_pretrend_contract_missing"}
    return {"available": True, "contract": dict(contract)}


def _posterior_convergence(analyzer: Any) -> Dict[str, Any]:
    mcmc = getattr(analyzer, "mcmc", None)
    if mcmc is None:
        return {"available": False, "reason": "no_mcmc_object"}
    out: Dict[str, Any] = {"available": True}
    try:
        samples = mcmc.get_samples()
        n_params = len(samples)
        out["n_posterior_groups"] = n_params
    except Exception as exc:  # noqa: BLE001
        out["samples_error"] = str(exc)
    try:
        import arviz as az  # type: ignore

        idata = az.from_numpyro(mcmc)
        div = idata.sample_stats.get("diverging")
        if div is not None:
            out["n_divergences"] = int(np.asarray(div).sum())
            out["divergence_rate"] = float(np.asarray(div).mean())
        summary = az.summary(idata, kind="diagnostics")
        if hasattr(summary, "to_dict"):
            bad_rhat = summary[summary["r_hat"] > 1.01] if "r_hat" in summary.columns else None
            if bad_rhat is not None and len(bad_rhat) > 0:
                out["n_high_rhat"] = int(len(bad_rhat))
            out["max_rhat"] = float(summary["r_hat"].max()) if "r_hat" in summary.columns else None
    except ImportError:
        out["arviz_available"] = False
        out["note"] = "Install arviz for R-hat / divergence summaries."
    except Exception as exc:  # noqa: BLE001
        out["arviz_error"] = str(exc)
    return out


def collect_estimator_diagnostics(analyzer: Any) -> Dict[str, Any]:
    """
    Build a diagnostic payload for ``analyzer`` after ``run_analysis`` (or DID's custom run).

    Sections are omitted when inputs are invalid; ``primary_diagnostic`` always reflects
    the estimator profile.
    """
    name = analyzer.__class__.__name__
    profile = classify_estimator(name)
    results = getattr(analyzer, "results", None) or {}
    payload: Dict[str, Any] = {
        "estimator": name,
        "classification": profile.to_dict(),
        "primary_diagnostic": profile.primary_diagnostic,
        "sections": {},
    }

    if profile.primary_diagnostic == "pretrend_contract":
        section = _pretrend_contract_section(results)
        if section.get("available"):
            payload["sections"]["pretrend_contract"] = section

    if profile.primary_diagnostic in (
        "counterfactual_stability",
        "donor_support",
    ) and profile.explicit_y_hat:
        pre = _pre_period_residual_summary(analyzer, results)
        if pre.get("available"):
            stability: Dict[str, Any] = {
                "pre_period_residuals": pre,
                "rolling_prefit_recommended": profile.rolling_pre_fit_meaningful,
                "heavy_inference_skipped": not _stability_inference_ok(analyzer),
            }
            if not _stability_inference_ok(analyzer):
                stability["note"] = (
                    "Full pseudo-panel stability tests require inference in {None, 'self'}; "
                    "use panel_exp.utils.counterfactual_stability_tests separately."
                )
            payload["sections"]["counterfactual_stability"] = stability

    if profile.donor_control_weights or name in _AUGSYNTH_WEIGHT_HEALTH:
        if name in _AUGSYNTH_WEIGHT_HEALTH and _stability_inference_ok(analyzer):
            panel = getattr(analyzer, "panel_data", None)
            if panel is not None:
                try:
                    health = check_AugSynthCVXPY_weight_health(panel)
                    payload["sections"]["donor_support"] = {
                        "available": True,
                        "source": "AugSynthCVXPY_weight_health",
                        **health,
                    }
                except Exception as exc:  # noqa: BLE001
                    payload["sections"]["donor_support"] = {
                        "available": False,
                        "reason": str(exc),
                    }
        elif name == "TROP":
            trop = _trop_donor_support(analyzer)
            if trop.get("available"):
                payload["sections"]["donor_support"] = trop
        else:
            donor = _donor_weight_summary(analyzer, name)
            if donor.get("available"):
                payload["sections"]["donor_support"] = donor

    if profile.primary_diagnostic == "posterior_convergence":
        post = _posterior_convergence(analyzer)
        if post.get("available"):
            payload["sections"]["posterior_convergence"] = post

    if profile.primary_diagnostic == "unsupported" or not payload["sections"]:
        payload["unsupported_reason"] = (
            "No path-level counterfactual or standard pretrend/donor inputs for this estimator."
            if profile.primary_diagnostic == "unsupported"
            else None
        )

    return payload


def attach_estimator_diagnostics(analyzer: Any) -> Dict[str, Any]:
    """Attach ``estimator_diagnostics`` to ``analyzer.results`` (creates results if needed)."""
    payload = collect_estimator_diagnostics(analyzer)
    if getattr(analyzer, "results", None) is None:
        analyzer.results = {}
    analyzer.results["estimator_diagnostics"] = payload
    return payload
