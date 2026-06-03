"""D5-POW-001b — SCM+UnitJackKnife null-monitor and detection semantics (research).

Post INV-D3-001, characterizes whether interval-excludes-zero (PowerAnalysis
``mean_ss``) is a valid detection criterion for governed SCM+JK readout, and
diagnoses D5-POW-001a pooled-detection degeneracy. Does not modify production code.
"""

from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Sequence

import numpy as np
import pandas as pd

from panel_exp.design.assign import greedy_match_markets
from panel_exp.methods.scm import SyntheticControl
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

Pow001bVerdict = Literal[
    "null_monitor_only",
    "requires_readout_aligned_power_metric",
    "supports_mde_with_caveats",
    "invalid_interval_detection_criterion",
]


@dataclass(frozen=True)
class D5Pow001bConfig:
    n_mc: int = 32
    n_geos: int = 16
    n_periods: int = 44
    treatment_start: int = 32
    test_length: int = 8
    train_length: int = 28
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260602
    scenario_name: str = "scm_low_signal"
    min_control_units: int = 2
    # Null and small positive injections (fractional level shift).
    effect_grid: tuple[float, ...] = (
        0.0,
        0.02,
        0.04,
        0.06,
        0.08,
        0.10,
        0.12,
    )


def _assign_greedy_pre_period(
    wide: pd.DataFrame,
    *,
    n_pre: int,
    seed: int,
    treatment_probability: float,
) -> list[str]:
    panel = PanelDataset(wide.copy())
    design = greedy_match_markets(
        func_to_optimize="corr",
        treatment_probability=treatment_probability,
        random_state=seed,
    )
    groups = design.assign(
        panel_data=panel,
        pre_treatment_period=TimePeriod(0, n_pre),
        n_test_grps=1,
    )
    treated = [u for units in groups.values() for u in units]
    if len(treated) < 1:
        raise ValueError("assignment produced no treated units")
    return treated


def _mean_treated_baseline(panel: PanelDataset) -> np.ndarray:
    return panel.wide_data.loc[panel.treated_units].mean(axis=1).values.astype(float)


def _inject_percent_effect(
    panel: PanelDataset,
    percent_effect: float,
    mean_value: np.ndarray,
) -> PanelDataset:
    mod = copy.deepcopy(panel)
    start = int(mod.treated_start_idxs[0])
    end_idx = int(mod.treated_end_idxs[0])
    if end_idx >= mod.times.shape[0]:
        end_idx = mod.times.shape[0] - 1
    treated_len = end_idx - start + 1
    n_treated = len(mod.treated_units)
    if n_treated == 1:
        delta = float(percent_effect * np.mean(mean_value))
        mod.wide_data.loc[mod.treated_units, mod.times[start : start + treated_len]] += delta
        return mod
    value_effect = percent_effect * mean_value
    mask = np.zeros((n_treated, mod.wide_data.shape[1]), dtype=bool)
    mask[:, start : start + treated_len] = True
    treated_block = mod.wide_data.loc[mod.treated_units].to_numpy(dtype=float)
    treated_block = np.where(mask, treated_block + value_effect.reshape(-1, 1), treated_block)
    mod.wide_data.loc[mod.treated_units] = treated_block
    return mod


def _post_window_arrays(
    results: dict,
    *,
    test_length: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    y = np.asarray(results["y"], dtype=float)
    y_hat = np.asarray(results["y_hat"], dtype=float)
    y_lo = np.asarray(results["y_lower"], dtype=float)
    y_hi = np.asarray(results["y_upper"], dtype=float)
    sl = slice(-test_length, None)
    return y[sl], y_hat[sl], y_lo[sl], y_hi[sl]


def _scm_jk_readout_metrics(
    panel: PanelDataset,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
) -> dict[str, float]:
    """SCM+JK metrics separating point recovery, null-monitor, and detection criteria."""
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    est = SyntheticControl(inference="UnitJackKnife", alpha=alpha)
    est.run_analysis(pds)

    y, y_hat, y_lo, y_hi = _post_window_arrays(est.results, test_length=test_length)
    effect = y - y_hat
    # PowerAnalysis / production interval semantics on effect scale.
    effect_lo = y - y_hi
    effect_hi = y - y_lo

    # D5-POW-001a harness mistake (swapped endpoints on mean aggregation).
    wrong_lo = y - y_lo
    wrong_hi = y - y_hi

    point_mean = float(np.mean(effect))
    covers_zero_correct = float(np.mean(effect_lo) <= 0.0 <= np.mean(effect_hi))
    detected_correct = float(not covers_zero_correct)

    covers_zero_wrong = float(np.mean(wrong_lo) <= 0.0 <= np.mean(wrong_hi))
    detected_wrong = float(not covers_zero_wrong)

    cell_covers = (effect_lo <= 0.0) & (0.0 <= effect_hi)
    cell_detected = ~cell_covers

    jk_hw = (y_hi - y_lo) / 2.0
    abs_z_style = float(np.mean(np.abs(effect) > jk_hw)) if jk_hw.size else float("nan")

    injected_sign = float(np.sign(percent_effect)) if abs(percent_effect) > 1e-12 else 0.0
    sign_ok = float(
        injected_sign == 0.0 or (np.isfinite(point_mean) and np.sign(point_mean) == injected_sign)
    )

    return {
        "percent_effect": float(percent_effect),
        "mean_point_effect": point_mean,
        "mean_effect_lo": float(np.mean(effect_lo)),
        "mean_effect_hi": float(np.mean(effect_hi)),
        "mean_jk_halfwidth": float(np.mean(jk_hw)),
        "covers_zero_correct": covers_zero_correct,
        "detected_correct": detected_correct,
        "covers_zero_wrong_001a": covers_zero_wrong,
        "detected_wrong_001a": detected_wrong,
        "cell_covers_zero_rate": float(np.mean(cell_covers)),
        "cell_detected_rate": float(np.mean(cell_detected)),
        "abs_effect_exceeds_jk_hw_rate": abs_z_style,
        "directional_recovery": sign_ok,
        "n_post_cells": float(effect.size),
    }


def run_one_replicate(cfg: D5Pow001bConfig, *, seed: int) -> dict[str, Any]:
    from dataclasses import replace

    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name],
        random_state=seed,
        n_geos=cfg.n_geos,
        n_periods=cfg.n_periods,
        treatment_start=cfg.treatment_start,
        true_effect=0.0,
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    treated = _assign_greedy_pre_period(
        wide,
        n_pre=cfg.train_length,
        seed=seed,
        treatment_probability=cfg.treatment_probability,
    )
    end = cfg.train_length + cfg.test_length
    unit_panel = PanelDataset(
        wide.iloc[:, :end].copy(),
        treated_periods=[TimePeriod(cfg.train_length, end - 1) for _ in treated],
        treated_units=treated,
    )
    mean_value = _mean_treated_baseline(unit_panel)

    by_effect: dict[float, dict[str, float]] = {}
    for prc in cfg.effect_grid:
        by_effect[float(prc)] = _scm_jk_readout_metrics(
            unit_panel,
            percent_effect=float(prc),
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
        )

    null = by_effect[0.0]
    small_pos = by_effect.get(0.04, by_effect.get(0.08, null))

    return {
        "seed": seed,
        "n_treated": len(treated),
        "n_control": int(unit_panel.num_control_units),
        "by_effect": by_effect,
        "null_fpr_correct": null["detected_correct"],
        "null_fpr_wrong_001a": null["detected_wrong_001a"],
        "null_cell_detected_rate": null["cell_detected_rate"],
        "response_4pct_point_delta": float(
            small_pos["mean_point_effect"] - null["mean_point_effect"]
        ),
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


def _pool_by_effect(
    rows: list[dict[str, Any]],
    field: str,
) -> dict[str, float]:
    effects = sorted({float(e) for r in rows for e in r["by_effect"]})
    pooled: dict[str, float] = {}
    for e in effects:
        vals = [float(r["by_effect"][e][field]) for r in rows if e in r["by_effect"]]
        pooled[str(e)] = float(np.mean(vals)) if vals else float("nan")
    return pooled


def _decide_verdict(
    *,
    null_fpr_correct: float,
    null_fpr_wrong: float,
    null_cell_detected: float,
    effect_grid_corr: float,
    degeneracy_from_swap: bool,
) -> tuple[Pow001bVerdict, str, list[str]]:
    attributions: list[str] = []
    if degeneracy_from_swap:
        attributions.append("simulation_harness_endpoint_swap")

    if null_fpr_wrong > 0.85 and null_fpr_correct < 0.5:
        attributions.append("d5_pow_001a_inverted_interval_aggregation")

    if null_fpr_correct > 0.35:
        attributions.append("anti_conservative_null_interval_exclusion")

    if not np.isfinite(effect_grid_corr) or effect_grid_corr < 0.5:
        attributions.append("weak_point_effect_tracking")

    if degeneracy_from_swap and null_fpr_correct < 0.35:
        rationale = (
            "D5-POW-001a pooled detection degeneracy is explained by swapped interval "
            "endpoints on mean aggregation (y-y_lower vs y-y_upper). Under correct "
            "PowerAnalysis semantics, null false-positive rate is moderate and "
            "SCM+UnitJackKnife supports null-monitor interpretation only—not lift "
            "detection or MDE planning via interval-excludes-zero."
        )
        return "null_monitor_only", rationale, attributions

    if null_fpr_correct < 0.2 and np.isfinite(effect_grid_corr) and effect_grid_corr > 0.7:
        return (
            "requires_readout_aligned_power_metric",
            "Point effects track injection but interval-excludes-zero is not a calibrated "
            "detection rule; define readout-aligned power separately from geo PowerAnalysis.",
            attributions,
        )

    return (
        "invalid_interval_detection_criterion",
        "SCM+JK interval exclusion does not support power/MDE interpretation on this battery.",
        attributions,
    )


def run_d5_pow_001b(config: D5Pow001bConfig | None = None) -> dict[str, Any]:
    from dataclasses import replace

    cfg = config or D5Pow001bConfig()
    rows: list[dict[str, Any]] = []
    attempts = 0
    while len(rows) < cfg.n_mc and attempts < cfg.n_mc * 3:
        seed = cfg.random_state_base + attempts
        attempts += 1
        try:
            scenario = replace(
                RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name],
                random_state=seed,
                n_geos=cfg.n_geos,
                n_periods=cfg.n_periods,
                treatment_start=cfg.treatment_start,
            )
            wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
            treated = _assign_greedy_pre_period(
                wide,
                n_pre=cfg.train_length,
                seed=seed,
                treatment_probability=cfg.treatment_probability,
            )
            n_ctrl = len([u for u in wide.index if u not in treated])
            if n_ctrl < cfg.min_control_units:
                continue
            rows.append(run_one_replicate(cfg, seed=seed))
        except ValueError:
            continue
    if not rows:
        raise RuntimeError("D5-POW-001b: no valid replicates")

    null_fpr_c = [r["null_fpr_correct"] for r in rows]
    null_fpr_w = [r["null_fpr_wrong_001a"] for r in rows]
    null_cell = [r["null_cell_detected_rate"] for r in rows]

    grid = sorted(cfg.effect_grid)
    corr_samples = []
    for r in rows:
        inj = np.array(grid, dtype=float)
        pts = np.array([r["by_effect"][g]["mean_point_effect"] for g in grid], dtype=float)
        if np.std(inj) > 1e-12 and np.std(pts) > 1e-12:
            corr_samples.append(float(np.corrcoef(inj, pts)[0, 1]))

    mean_null_fpr_c = _summarize(null_fpr_c)["mean"]
    mean_null_fpr_w = _summarize(null_fpr_w)["mean"]
    degeneracy_from_swap = bool(
        np.isfinite(mean_null_fpr_w)
        and np.isfinite(mean_null_fpr_c)
        and mean_null_fpr_w > 0.85
        and mean_null_fpr_c < mean_null_fpr_w - 0.4
    )

    verdict, rationale, attributions = _decide_verdict(
        null_fpr_correct=mean_null_fpr_c,
        null_fpr_wrong=mean_null_fpr_w,
        null_cell_detected=_summarize(null_cell)["mean"],
        effect_grid_corr=_summarize(corr_samples)["mean"],
        degeneracy_from_swap=degeneracy_from_swap,
    )

    return {
        "artifact_id": "D5-POW-001b",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "lane": "research",
        "investigation_id": "D4-FIND-001",
        "prior_artifact": "docs/track_d/archives/D5_POW_001a_results.json",
        "inv_d3_001_fix_applied": True,
        "config": asdict(cfg),
        "hypothesis": (
            "Pooled interval-detection degeneracy in D5-POW-001a may reflect harness "
            "semantics rather than SCM+JK null-monitor failure."
        ),
        "primary_metrics": {
            "null_fpr_interval_excludes_zero_correct": _summarize(null_fpr_c),
            "null_fpr_interval_excludes_zero_wrong_001a_style": _summarize(null_fpr_w),
            "null_cell_level_detected_rate": _summarize(null_cell),
            "effect_grid_point_correlation": _summarize(corr_samples),
            "directional_recovery_null": _summarize(
                [rows[i]["by_effect"][0.0]["directional_recovery"] for i in range(len(rows))]
            ),
            "directional_recovery_8pct": _summarize(
                [
                    rows[i]["by_effect"].get(0.08, rows[i]["by_effect"][0.0])[
                        "directional_recovery"
                    ]
                    for i in range(len(rows))
                ]
            ),
        },
        "pooled_by_effect": {
            "detected_correct": _pool_by_effect(rows, "detected_correct"),
            "detected_wrong_001a": _pool_by_effect(rows, "detected_wrong_001a"),
            "cell_detected_rate": _pool_by_effect(rows, "cell_detected_rate"),
            "mean_point_effect": _pool_by_effect(rows, "mean_point_effect"),
            "cell_covers_zero_rate": _pool_by_effect(rows, "cell_covers_zero_rate"),
        },
        "degeneracy_attribution": attributions,
        "interval_excludes_zero_valid_for_scm_jk": False,
        "n_replicates": len(rows),
        "pow_verdict": verdict,
        "rationale": rationale,
        "scm_unit_jackknife_governance": "calibration_eligible_null_monitor_only",
        "pow_001_status": "diagnostic_only",
        "pow_001b_recommendation": (
            "Do not use interval-excludes-zero (PowerAnalysis mean_ss) for SCM+JK power or MDE; "
            "use null-monitor cell coverage and readout-aligned metrics if simulation is required."
        ),
        "calibration_eligibility_changed": False,
        "notes": [
            "Correct effect bounds: effect_lo = y - y_upper, effect_hi = y - y_lower.",
            "D5-POW-001a used mean(y-y_lower) and mean(y-y_upper), inverting the interval test.",
            "No production power, inference, estimator, TrustReport, or eligibility changes.",
        ],
    }


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, float):
        return None if not np.isfinite(obj) else obj
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


def write_artifact(payload: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_json_safe(payload), indent=2) + "\n",
        encoding="utf-8",
    )
    return path
