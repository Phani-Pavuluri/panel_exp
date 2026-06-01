"""D5-INF-002a — SCM Unit Jackknife LOO target characterization (research).

Compares production ``unit_jk`` (full-fit ``y`` vs leave-one-out ``y_hat``) to a
literature-aligned reference (``y_hat`` vs leave-one-out ``y_hat``) and measures
sensitivity of post-period interval half-width to treated-unit post-outcome noise.

Does not modify production inference.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np
import scipy.stats

from panel_exp.inference.unit_jackknife import unit_jk
from panel_exp.methods.scm import SyntheticControl
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

Recommendation = Literal[
    "accepted_deviation",
    "characterization_required",
    "restricted",
    "open_inv_d3_001",
    "continue_investigation",
]


@dataclass(frozen=True)
class D5Inf002aConfig:
    n_mc: int = 80
    alpha: float = 0.05
    treated_post_noise_sd: float = 50.0
    control_post_noise_sd: float = 50.0
    random_state_base: int = 20260528
    scenarios: tuple[str, ...] = ("scm_low_signal", "scm_multi_treated")


def unit_jk_literature_reference(
    panel: PanelDataset,
    estimator,
    *,
    variation: int = 1,
    alpha: float = 0.05,
    **estimator_kwargs,
) -> np.ndarray:
    """LOO jackknife using ``tau_{-i} - tau`` with ``tau = Y - y_hat`` (equivalently ``y_hat - y_hat_{-i}``)."""
    full_est = estimator(**estimator_kwargs)
    full_est.run_analysis(panel)
    mu = np.asarray(full_est.results["y_hat"], dtype=float)

    squared_diffs = np.zeros_like(mu, dtype=float)
    for unit in [u for u in panel.units if u not in panel.treated_units]:
        cur_panel = panel.drop_units(unit)
        est = estimator(**estimator_kwargs)
        est.run_analysis(cur_panel)
        mu_i = np.asarray(est.results["y_hat"], dtype=float)
        squared_diffs += np.square(mu_i - mu)

    jk = ((panel.num_units - 1) / panel.num_units) * squared_diffs
    z = scipy.stats.norm.ppf(alpha / 2 + (1 - alpha))
    return z * np.sqrt(jk)


def _post_slice(panel: PanelDataset) -> slice:
    start = int(panel.treated_start_idxs[0])
    end = int(panel.treated_end_idxs[0]) + 1
    return slice(start, end)


def _post_treatment_errors(errors: np.ndarray, panel: PanelDataset) -> np.ndarray:
    """Extract treated-window errors; supports 1D time or 2D (time × treated unit)."""
    err = np.asarray(errors, dtype=float)
    start = int(panel.treated_start_idxs[0])
    end = int(panel.treated_end_idxs[0]) + 1
    n_treated = len(panel.treated_units)
    if err.ndim == 2:
        return err[start:end, :]
    if err.ndim == 1 and err.size == panel.num_timepoints:
        return err[start:end]
    if err.ndim == 1 and n_treated > 0 and err.size == panel.num_timepoints * n_treated:
        return err.reshape(panel.num_timepoints, n_treated)[start:end, :]
    return err.reshape(-1)


def _mean_post_halfwidth(panel: PanelDataset, errors: np.ndarray) -> float:
    post = _post_treatment_errors(errors, panel)
    if post.size == 0 or not np.any(np.isfinite(post)):
        return float("nan")
    return float(np.nanmean(np.abs(post)))


def _perturb_post_outcomes(
    panel: PanelDataset,
    *,
    units: list[str],
    noise_sd: float,
    seed: int,
) -> PanelDataset:
    if noise_sd <= 0:
        return panel
    rng = np.random.default_rng(seed)
    wide = panel.wide_data.copy()
    sl = _post_slice(panel)
    cols = wide.columns[sl]
    for unit in units:
        if unit not in wide.index:
            continue
        wide.loc[unit, cols] = wide.loc[unit, cols].values + rng.normal(
            0.0, noise_sd, size=len(cols)
        )
    periods = [
        TimePeriod(start=tp.start, end=tp.end)
        for tp in panel.treated_periods
    ]
    return PanelDataset(
        wide,
        treated_periods=periods,
        treated_units=list(panel.treated_units),
    )


def _run_jk_pair(
    panel: PanelDataset,
    *,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    prod = np.asarray(
        unit_jk(panel, SyntheticControl, variation=1, alpha=alpha),
        dtype=float,
    )
    ref = np.asarray(
        unit_jk_literature_reference(
            panel, SyntheticControl, variation=1, alpha=alpha
        ),
        dtype=float,
    )
    return prod, ref


def run_one_replicate(
    panel: PanelDataset,
    *,
    alpha: float,
    treated_post_noise_sd: float,
    control_post_noise_sd: float,
    seed: int,
) -> dict[str, float]:
    prod, ref = _run_jk_pair(panel, alpha=alpha)
    hw_prod = _mean_post_halfwidth(panel, prod)
    hw_ref = _mean_post_halfwidth(panel, ref)

    treated_units = list(panel.treated_units)
    control_units = [u for u in panel.units if u not in panel.treated_units]

    panel_treat_noise = _perturb_post_outcomes(
        panel,
        units=treated_units,
        noise_sd=treated_post_noise_sd,
        seed=seed + 1,
    )
    prod_tn, ref_tn = _run_jk_pair(panel_treat_noise, alpha=alpha)
    hw_prod_tn = _mean_post_halfwidth(panel_treat_noise, prod_tn)
    hw_ref_tn = _mean_post_halfwidth(panel_treat_noise, ref_tn)

    panel_ctrl_noise = _perturb_post_outcomes(
        panel,
        units=control_units,
        noise_sd=control_post_noise_sd,
        seed=seed + 2,
    )
    prod_cn, ref_cn = _run_jk_pair(panel_ctrl_noise, alpha=alpha)
    hw_prod_cn = _mean_post_halfwidth(panel_ctrl_noise, prod_cn)
    hw_ref_cn = _mean_post_halfwidth(panel_ctrl_noise, ref_cn)

    def rel_change(before: float, after: float) -> float:
        if not np.isfinite(before) or before <= 1e-12:
            return float("nan")
        return float(abs(after - before) / before)

    prod_vec = _post_treatment_errors(prod, panel).ravel()
    ref_vec = _post_treatment_errors(ref, panel).ravel()
    if prod_vec.size and prod_vec.size == ref_vec.size:
        corr = float(np.corrcoef(prod_vec, ref_vec)[0, 1])
    else:
        corr = float("nan")

    chg_prod = rel_change(hw_prod, hw_prod_tn)
    chg_ref = rel_change(hw_ref, hw_ref_tn)
    if np.isfinite(chg_prod) and np.isfinite(chg_ref):
        if chg_ref < 1e-6:
            sensitivity_ratio = chg_prod
        else:
            sensitivity_ratio = chg_prod / chg_ref
    else:
        sensitivity_ratio = float("nan")

    return {
        "post_hw_production": hw_prod,
        "post_hw_reference": hw_ref,
        "post_hw_ratio_prod_over_ref": (
            hw_prod / hw_ref if np.isfinite(hw_ref) and hw_ref > 1e-12 else float("nan")
        ),
        "post_hw_corr": corr,
        "treated_noise_rel_change_production": rel_change(hw_prod, hw_prod_tn),
        "treated_noise_rel_change_reference": rel_change(hw_ref, hw_ref_tn),
        "control_noise_rel_change_production": rel_change(hw_prod, hw_prod_cn),
        "control_noise_rel_change_reference": rel_change(hw_ref, hw_ref_cn),
        "sensitivity_ratio_treated": sensitivity_ratio,
    }


def _summarize(samples: list[float]) -> dict[str, float]:
    arr = np.array([x for x in samples if np.isfinite(x)], dtype=float)
    if arr.size == 0:
        return {"mean": float("nan"), "std": float("nan"), "p95": float("nan")}
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "p95": float(np.percentile(arr, 95)),
    }


def _decide(
    *,
    mean_treated_noise_prod: float,
    mean_treated_noise_ref: float,
    mean_sensitivity_ratio: float,
    mean_hw_ratio: float,
    mean_corr: float,
) -> tuple[Recommendation, str, str]:
    """Return recommendation, rationale, d3_find_001_disposition."""
    # Treated post noise should not dominate JK width under correct LOO target.
    if (
        np.isfinite(mean_treated_noise_prod)
        and mean_treated_noise_prod > 0.15
        and np.isfinite(mean_treated_noise_ref)
        and mean_treated_noise_ref < 0.05
        and (
            (np.isfinite(mean_sensitivity_ratio) and mean_sensitivity_ratio > 2.0)
            or mean_treated_noise_prod > 0.5
        )
    ):
        return (
            "open_inv_d3_001",
            (
                "Production JK post half-width shifts materially when only treated "
                "post outcomes are noised, while the literature-aligned y_hat anchor "
                "is stable (sensitivity ratio > 2). Production and reference widths "
                "differ systematically."
            ),
            "open_inv_d3_001",
        )
    if (
        np.isfinite(mean_hw_ratio)
        and mean_hw_ratio > 2.0
        and np.isfinite(mean_corr)
        and mean_corr < 0.5
        and mean_treated_noise_prod > 0.10
    ):
        return (
            "open_inv_d3_001",
            (
                "Production JK post width diverges from literature-aligned LOO reference "
                "(width ratio > 2, low correlation) and is sensitive to treated post noise."
            ),
            "open_inv_d3_001",
        )
    if (
        np.isfinite(mean_corr)
        and mean_corr > 0.995
        and np.isfinite(mean_hw_ratio)
        and 0.85 <= mean_hw_ratio <= 1.15
        and mean_treated_noise_prod < 0.10
    ):
        return (
            "accepted_deviation",
            "Production and reference JK paths are numerically near-identical on this battery.",
            "accepted_deviation",
        )
    if mean_treated_noise_prod > 0.12 or (
        np.isfinite(mean_sensitivity_ratio) and mean_sensitivity_ratio > 1.8
    ):
        return (
            "characterization_required",
            "LOO target mismatch is present but moderate; keep null-monitor-only and characterize further.",
            "characterization_required",
        )
    return (
        "continue_investigation",
        "Mixed signals on LOO target; extend battery before governance change.",
        "continue_investigation",
    )


def run_d5_inf_002a(config: D5Inf002aConfig | None = None) -> dict[str, Any]:
    cfg = config or D5Inf002aConfig()
    rows: list[dict[str, float]] = []

    for scenario_name in cfg.scenarios:
        base_scenario = RECOVERY_SCENARIO_REGISTRY[scenario_name]
        for i in range(cfg.n_mc):
            seed = cfg.random_state_base + i + (hash(scenario_name) % 10_000)
            scenario = base_scenario
            if scenario.random_state != seed:
                from dataclasses import replace

                scenario = replace(scenario, random_state=seed)
            world = SyntheticWorld.generate(scenario)
            panel = world.to_panel_dataset()
            if panel.num_control_units < 2:
                continue
            row = run_one_replicate(
                panel,
                alpha=cfg.alpha,
                treated_post_noise_sd=cfg.treated_post_noise_sd,
                control_post_noise_sd=cfg.control_post_noise_sd,
                seed=seed,
            )
            rows.append({**row, "scenario_name": scenario_name})

    treated_prod = [r["treated_noise_rel_change_production"] for r in rows]
    treated_ref = [r["treated_noise_rel_change_reference"] for r in rows]
    sens_ratio = [r["sensitivity_ratio_treated"] for r in rows]
    hw_ratio = [r["post_hw_ratio_prod_over_ref"] for r in rows]
    corr = [r["post_hw_corr"] for r in rows]

    mean_treated_prod = _summarize(treated_prod)["mean"]
    mean_treated_ref = _summarize(treated_ref)["mean"]
    mean_sens = _summarize(sens_ratio)["mean"]
    mean_hw_ratio = _summarize(hw_ratio)["mean"]
    mean_corr = _summarize(corr)["mean"]

    recommendation, rationale, d3_disp = _decide(
        mean_treated_noise_prod=mean_treated_prod,
        mean_treated_noise_ref=mean_treated_ref,
        mean_sensitivity_ratio=mean_sens,
        mean_hw_ratio=mean_hw_ratio,
        mean_corr=mean_corr,
    )

    return {
        "artifact_id": "D5-INF-002a",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "lane": "research",
        "investigation_id": "INV-D3-001",
        "finding_id": "D3-FIND-001",
        "config": asdict(cfg),
        "hypothesis": (
            "Production unit_jk anchors LOO on observed y while literature SCM jackknife "
            "uses (y_hat_{-i} - y_hat); treated post-outcome noise should inflate "
            "production JK width disproportionately."
        ),
        "primary_metrics": {
            "post_hw_ratio_prod_over_ref": _summarize(hw_ratio),
            "post_hw_corr_prod_vs_ref": _summarize(corr),
            "treated_post_noise_rel_change_production": _summarize(treated_prod),
            "treated_post_noise_rel_change_reference": _summarize(treated_ref),
            "sensitivity_ratio_treated_prod_over_ref": _summarize(sens_ratio),
            "control_post_noise_rel_change_production": _summarize(
                [r["control_noise_rel_change_production"] for r in rows]
            ),
            "control_post_noise_rel_change_reference": _summarize(
                [r["control_noise_rel_change_reference"] for r in rows]
            ),
        },
        "n_replicates": len(rows),
        "recommendation": recommendation,
        "rationale": rationale,
        "d3_find_001_disposition": d3_disp,
        "production_code_path": "panel_exp/inference/unit_jackknife.py::unit_jk",
        "reference_definition": "y_hat_full vs y_hat_leave_one_out (Abadie tau jackknife)",
        "calibration_eligibility_changed": False,
        "notes": [
            "SCM_UnitJackKnife remains null_monitor_only regardless of outcome.",
            "No inference or eligibility code was modified.",
        ],
    }


def write_artifact(payload: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path
