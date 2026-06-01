"""D5-POW-001a — TBRRidge+KFold power vs SCM+UnitJackKnife readout alignment (research).

Compares geo-default power path (aggregated panel, TBRRidge, Kfold) to the
governed readout instrument (unit-level panel, SyntheticControl, UnitJackKnife)
on the same design assignment and injected effect grid. Does not modify production
power or estimators.
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
from panel_exp.design.power import PowerAnalysis
from panel_exp.methods.scm import SyntheticControl
from panel_exp.methods.tbr import TBRRidge
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

ProxyVerdict = Literal[
    "rough_proxy",
    "conservative_proxy",
    "optimistic_proxy",
    "unrelated_misleading",
    "narrow_diagnostics_only",
]


@dataclass(frozen=True)
class D5Pow001aConfig:
    n_mc: int = 24
    n_geos: int = 16
    n_periods: int = 44
    treatment_start: int = 32
    n_treated_target: int = 3
    test_length: int = 8
    train_length: int = 28
    mx_effect: float = 0.15
    power_threshold: float = 0.8
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260601
    scenario_name: str = "scm_low_signal"
    min_control_units: int = 2
    include_power_analysis_mde: bool = True
    # Fixed-window effect grid (fractional level shift on treated units).
    effect_grid: tuple[float, ...] = (
        -0.12,
        -0.08,
        -0.04,
        0.0,
        0.04,
        0.08,
        0.12,
        0.16,
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


def _aggregated_power_panel(
    wide: pd.DataFrame,
    treated_units: list[str],
) -> PanelDataset:
    """Geo design: sum test markets and sum controls into two series."""
    control_units = [u for u in wide.index if u not in treated_units]
    treated_series = wide.loc[treated_units].sum(axis=0)
    control_series = wide.loc[control_units].sum(axis=0)
    agg = pd.DataFrame({"treated": treated_series, "control": control_series}).T
    return PanelDataset(
        agg,
        treated_units=["treated"],
        treated_periods=[TimePeriod(0, agg.shape[1] - 1)],
    )


def _mean_treated_baseline(panel: PanelDataset) -> np.ndarray:
    """Per-unit mean level for percent-effect scaling (matches PowerAnalysis)."""
    vals = panel.wide_data.loc[panel.treated_units].mean(axis=1).values.astype(float)
    return vals


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


def _slice_experiment_window(
    panel: PanelDataset,
    *,
    train_length: int,
    test_length: int,
) -> PanelDataset:
    end = train_length + test_length
    wide = panel.wide_data.iloc[:, :end].copy()
    periods = [
        TimePeriod(start=train_length, end=end - 1) for _ in panel.treated_units
    ]
    return PanelDataset(
        wide,
        treated_periods=periods,
        treated_units=list(panel.treated_units),
    )


def _post_mean_significance(
    results: dict,
    panel: PanelDataset,
    *,
    test_length: int | None = None,
) -> dict[str, float]:
    """Post-window mean effect and interval-excludes-zero (PowerAnalysis ``mean_ss``)."""
    y = np.asarray(results["y"], dtype=float).reshape(-1)
    y_hat = np.asarray(results["y_hat"], dtype=float).reshape(-1)
    y_lo = np.asarray(results["y_lower"], dtype=float).reshape(-1)
    y_hi = np.asarray(results["y_upper"], dtype=float).reshape(-1)
    if test_length is not None and test_length > 0 and y.size >= test_length:
        sl = slice(-test_length, None)
    else:
        start = int(panel.treated_start_idxs[0])
        end = int(panel.treated_end_idxs[0]) + 1
        sl = slice(start, end)
    mean_effect = float(np.mean(y[sl] - y_hat[sl]))
    mean_lo = float(np.mean(y[sl] - y_lo[sl]))
    mean_hi = float(np.mean(y[sl] - y_hi[sl]))
    covers_zero = mean_lo <= 0.0 <= mean_hi
    detected = not covers_zero
    return {
        "mean_point_effect": mean_effect,
        "covers_zero": float(covers_zero),
        "detected": float(detected),
    }


def _run_tbr_kfold_readout(
    panel: PanelDataset,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    random_state: int,
    test_length: int,
) -> dict[str, float]:
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    est = TBRRidge(inference="Kfold", alpha=alpha)
    est.run_analysis(pds, random_state=random_state)
    stats = _post_mean_significance(est.results, pds, test_length=test_length)
    stats["path"] = "tbr_kfold"
    return stats


def _run_scm_jk_readout(
    panel: PanelDataset,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
) -> dict[str, float]:
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    est = SyntheticControl(inference="UnitJackKnife", alpha=alpha)
    est.run_analysis(pds)
    stats = _post_mean_significance(est.results, pds, test_length=test_length)
    stats["path"] = "scm_jk"
    return stats


def _power_curve_fixed_window(
    unit_panel: PanelDataset,
    agg_panel: PanelDataset,
    *,
    effect_grid: Sequence[float],
    mean_value: np.ndarray,
    alpha: float,
    seed: int,
    test_length: int,
) -> tuple[dict[float, dict], dict[float, dict]]:
    tbr: dict[float, dict] = {}
    scm: dict[float, dict] = {}
    for prc in effect_grid:
        tbr[float(prc)] = _run_tbr_kfold_readout(
            agg_panel,
            percent_effect=float(prc),
            mean_value=mean_value,
            alpha=alpha,
            random_state=seed + int(prc * 1000),
            test_length=test_length,
        )
        scm[float(prc)] = _run_scm_jk_readout(
            unit_panel,
            percent_effect=float(prc),
            mean_value=mean_value,
            alpha=alpha,
            test_length=test_length,
        )
    return tbr, scm


def _effect_grid_correlation(curve: dict[float, dict]) -> float:
    effects = sorted(curve.keys())
    if len(effects) < 2:
        return float("nan")
    injected = np.array(effects, dtype=float)
    points = np.array([curve[e]["mean_point_effect"] for e in effects], dtype=float)
    if np.std(injected) < 1e-12 or np.std(points) < 1e-12:
        return float("nan")
    return float(np.corrcoef(injected, points)[0, 1])


def _directional_recovery(curve: dict[float, dict]) -> float:
    non_null = [e for e in curve if abs(e) > 1e-9]
    if not non_null:
        return float("nan")
    hits = []
    for e in non_null:
        pt = curve[e]["mean_point_effect"]
        if np.isfinite(pt):
            hits.append(np.sign(pt) == np.sign(e))
    return float(np.mean(hits)) if hits else float("nan")


def _detection_rate(curve: dict[float, dict]) -> dict[float, float]:
    return {float(k): float(v["detected"]) for k, v in curve.items()}


def _mde_from_detection(
    detection: dict[float, float],
    *,
    threshold: float,
) -> float:
    """Smallest |effect| in grid with detection rate >= threshold (non-null)."""
    positives = [
        abs(e)
        for e, d in detection.items()
        if abs(e) > 1e-9 and d >= threshold
    ]
    if not positives:
        return float("nan")
    return float(min(positives))


def _run_geo_power_analysis_mde(
    agg_panel: PanelDataset,
    *,
    cfg: D5Pow001aConfig,
    seed: int,
) -> float:
    """Full geo-style PowerAnalysis MDE percent (subset settings for runtime)."""
    pa = PowerAnalysis(
        agg_panel,
        model=TBRRidge,
        inference="Kfold",
        test_length=cfg.test_length,
        train_length=cfg.train_length,
        mx_effect=cfg.mx_effect,
        n_sample_prc=0.25,
        n_jobs=1,
        ci_version=2,
        alpha=cfg.alpha,
        random_state=seed,
        power=cfg.power_threshold,
    )
    pa.run_analysis()
    return float(pa.mde_percent)


def run_one_replicate(cfg: D5Pow001aConfig, *, seed: int) -> dict[str, Any]:
    from dataclasses import replace

    scenario = RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name]
    scenario = replace(
        scenario,
        random_state=seed,
        n_geos=cfg.n_geos,
        n_periods=cfg.n_periods,
        treatment_start=cfg.treatment_start,
        true_effect=0.0,
    )
    world = SyntheticWorld.generate(scenario)
    wide = world.to_panel_dataset().wide_data

    n_pre = cfg.train_length
    treated_units = _assign_greedy_pre_period(
        wide,
        n_pre=n_pre,
        seed=seed,
        treatment_probability=cfg.treatment_probability,
    )
    end = cfg.train_length + cfg.test_length
    unit_wide = wide.iloc[:, :end].copy()
    post_end = end - 1
    unit_panel = PanelDataset(
        unit_wide,
        treated_periods=[TimePeriod(cfg.train_length, post_end) for _ in treated_units],
        treated_units=treated_units,
    )
    agg_panel = _aggregated_power_panel(wide, treated_units)
    agg_wide = agg_panel.wide_data.iloc[:, :end].copy()
    agg_panel = PanelDataset(
        agg_wide,
        treated_units=["treated"],
        treated_periods=[TimePeriod(cfg.train_length, post_end)],
    )

    mean_value = _mean_treated_baseline(unit_panel)
    tbr_curve, scm_curve = _power_curve_fixed_window(
        unit_panel,
        agg_panel,
        effect_grid=cfg.effect_grid,
        mean_value=mean_value,
        alpha=cfg.alpha,
        seed=seed,
        test_length=cfg.test_length,
    )
    tbr_det = _detection_rate(tbr_curve)
    scm_det = _detection_rate(scm_curve)

    null_pt_tbr = tbr_curve.get(0.0, {}).get("mean_point_effect", float("nan"))
    null_pt_scm = scm_curve.get(0.0, {}).get("mean_point_effect", float("nan"))
    pt_08_tbr = tbr_curve.get(0.08, {}).get("mean_point_effect", float("nan"))
    pt_08_scm = scm_curve.get(0.08, {}).get("mean_point_effect", float("nan"))

    pa_mde = float("nan")
    if cfg.include_power_analysis_mde:
        try:
            pa_mde = _run_geo_power_analysis_mde(agg_panel, cfg=cfg, seed=seed + 9000)
        except Exception:
            pa_mde = float("nan")

    return {
        "seed": seed,
        "n_treated": len(treated_units),
        "n_control": int(unit_panel.num_control_units),
        "null_detection_tbr": tbr_det.get(0.0, float("nan")),
        "null_detection_scm": scm_det.get(0.0, float("nan")),
        "effect_grid_corr_tbr": _effect_grid_correlation(tbr_curve),
        "effect_grid_corr_scm": _effect_grid_correlation(scm_curve),
        "directional_recovery_tbr": _directional_recovery(tbr_curve),
        "directional_recovery_scm": _directional_recovery(scm_curve),
        "effect_response_8pct_tbr": float(pt_08_tbr - null_pt_tbr)
        if np.isfinite(pt_08_tbr) and np.isfinite(null_pt_tbr)
        else float("nan"),
        "effect_response_8pct_scm": float(pt_08_scm - null_pt_scm)
        if np.isfinite(pt_08_scm) and np.isfinite(null_pt_scm)
        else float("nan"),
        "poweranalysis_mde_percent_tbr": pa_mde,
        "tbr_curve": {float(k): v for k, v in tbr_curve.items()},
        "scm_curve": {float(k): v for k, v in scm_curve.items()},
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


def _pool_detection_curves(
    rows: list[dict[str, Any]],
    path_key: str,
) -> dict[float, float]:
    """MC-pooled fraction of replicates with interval-excludes-zero at each effect."""
    effects: set[float] = set()
    for row in rows:
        effects.update(float(k) for k in row[path_key])
    pooled: dict[float, float] = {}
    for e in sorted(effects):
        dets = [float(row[path_key][e]["detected"]) for row in rows if e in row[path_key]]
        pooled[e] = float(np.mean(dets)) if dets else float("nan")
    return pooled


def _decide_proxy(
    *,
    pooled_det_corr: float,
    mean_mde_tbr: float,
    mean_mde_scm: float,
    pooled_null_tbr: float,
    pooled_null_scm: float,
    mean_resp_tbr: float,
    mean_resp_scm: float,
    mean_grid_corr_tbr: float,
    mean_grid_corr_scm: float,
    mean_pa_mde: float,
) -> tuple[ProxyVerdict, str]:
    """Classify whether geo power is a usable proxy for SCM JK readout."""
    tbr_responds = np.isfinite(mean_resp_tbr) and abs(mean_resp_tbr) > 1.0
    scm_flat = (not np.isfinite(mean_resp_scm)) or abs(mean_resp_scm) < 0.5
    tbr_tracks_injection = np.isfinite(mean_grid_corr_tbr) and mean_grid_corr_tbr > 0.5
    scm_tracks_injection = np.isfinite(mean_grid_corr_scm) and mean_grid_corr_scm > 0.5

    if tbr_responds and scm_flat and not scm_tracks_injection:
        return (
            "unrelated_misleading",
            "TBRRidge+KFold point readout moves with injected effects on the aggregated panel; "
            "SCM+UnitJackKnife post mean effect is largely flat across the injection grid on the "
            "unit panel. Geo PowerAnalysis MDE is not a feasibility proxy for governed SCM JK lift.",
        )

    if tbr_tracks_injection and not scm_tracks_injection:
        return (
            "unrelated_misleading",
            "Injection grid correlates with TBRRidge+KFold estimates but not SCM+JK readout.",
        )

    if not np.isfinite(pooled_det_corr):
        if (
            np.isfinite(mean_pa_mde)
            and np.isfinite(mean_mde_scm)
            and mean_mde_scm > 1e-6
            and mean_pa_mde < 0.75 * mean_mde_scm
        ):
            return (
                "optimistic_proxy",
                "Geo PowerAnalysis mde_percent (ci_version=2 null-spread semantics) is "
                "materially lower than pooled SCM+JK interval-detection MDE on the same "
                "assignment; do not treat geo MDE as SCM feasibility evidence.",
            )
        if tbr_responds and scm_flat and not scm_tracks_injection:
            return (
                "unrelated_misleading",
                "TBRRidge+KFold point readout moves with injected effects; SCM+JK does not.",
            )
        if tbr_tracks_injection and scm_tracks_injection:
            return (
                "narrow_diagnostics_only",
                "Injection-grid point effects align on this battery, but pooled interval-detection "
                "curves are degenerate (both paths often exclude zero at all grid points). "
                "Geo PowerAnalysis MDE remains diagnostic-only for SCM JK planning.",
            )
        if tbr_tracks_injection or scm_tracks_injection:
            return (
                "narrow_diagnostics_only",
                "Pooled interval-detection curves are degenerate; use effect-response metrics only.",
            )
        return (
            "unrelated_misleading",
            "Neither path shows stable injection tracking on this battery.",
        )

    scm_no_power = np.isfinite(pooled_null_scm) and pooled_null_scm < 0.15
    tbr_detects = np.isfinite(pooled_null_tbr) and pooled_null_tbr > 0.4

    if scm_no_power and tbr_detects:
        return (
            "unrelated_misleading",
            "TBRRidge+KFold pooled detection exceeds SCM+JK at matched effects.",
        )

    if pooled_det_corr >= 0.65 and np.isfinite(mean_mde_tbr) and np.isfinite(mean_mde_scm):
        ratio = mean_mde_tbr / mean_mde_scm if mean_mde_scm > 1e-6 else float("inf")
        if 0.5 <= ratio <= 2.0:
            return (
                "rough_proxy",
                "Pooled detection curves correlate and fixed-window MDE thresholds are comparable.",
            )
        if ratio > 2.0:
            return (
                "optimistic_proxy",
                "TBRRidge+KFold MDE threshold is lower than SCM+JK on pooled detection.",
            )
        return (
            "conservative_proxy",
            "TBRRidge+KFold MDE threshold is higher than SCM+JK on pooled detection.",
        )

    if pooled_null_tbr > pooled_null_scm + 0.15:
        return (
            "optimistic_proxy",
            "Higher pooled null-interval exclusion rate for TBRRidge+KFold than SCM+JK.",
        )

    if pooled_det_corr >= 0.4:
        return (
            "narrow_diagnostics_only",
            "Partial pooled-detection alignment only; not SCM JK feasibility evidence.",
        )

    if np.isfinite(mean_pa_mde) and tbr_tracks_injection and not scm_tracks_injection:
        return (
            "unrelated_misleading",
            f"Geo PowerAnalysis mde_percent (~{mean_pa_mde:.2f}) uses TBRRidge+Kfold semantics "
            "while SCM+JK readout does not track the injection grid.",
        )

    return (
        "unrelated_misleading",
        "Low pooled-detection correlation and mismatched injection response between paths.",
    )


def run_d5_pow_001a(config: D5Pow001aConfig | None = None) -> dict[str, Any]:
    from dataclasses import replace

    cfg = config or D5Pow001aConfig()
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
            wide_check = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
            treated_check = _assign_greedy_pre_period(
                wide_check,
                n_pre=cfg.train_length,
                seed=seed,
                treatment_probability=cfg.treatment_probability,
            )
            n_ctrl = len([u for u in wide_check.index if u not in treated_check])
            if n_ctrl < cfg.min_control_units:
                continue
            rows.append(run_one_replicate(cfg, seed=seed))
        except ValueError:
            continue
    if not rows:
        raise RuntimeError("D5-POW-001a: no valid replicates (insufficient control units)")

    pooled_tbr = _pool_detection_curves(rows, "tbr_curve")
    pooled_scm = _pool_detection_curves(rows, "scm_curve")
    grid = sorted({float(k) for k in pooled_tbr} | {float(k) for k in pooled_scm})
    if len(grid) > 1:
        tbr_powers = [pooled_tbr.get(g, float("nan")) for g in grid]
        scm_powers = [pooled_scm.get(g, float("nan")) for g in grid]
        finite = [
            i
            for i in range(len(grid))
            if np.isfinite(tbr_powers[i]) and np.isfinite(scm_powers[i])
        ]
        if len(finite) >= 2:
            pooled_det_corr = float(
                np.corrcoef(
                    [tbr_powers[i] for i in finite],
                    [scm_powers[i] for i in finite],
                )[0, 1]
            )
        else:
            pooled_det_corr = float("nan")
    else:
        pooled_det_corr = float("nan")

    mde_tbr = _mde_from_detection(pooled_tbr, threshold=cfg.power_threshold)
    mde_scm = _mde_from_detection(pooled_scm, threshold=cfg.power_threshold)

    resp_tbr = [r["effect_response_8pct_tbr"] for r in rows]
    resp_scm = [r["effect_response_8pct_scm"] for r in rows]
    grid_corr_tbr = [r["effect_grid_corr_tbr"] for r in rows]
    grid_corr_scm = [r["effect_grid_corr_scm"] for r in rows]
    pa_mde = [r["poweranalysis_mde_percent_tbr"] for r in rows]

    verdict, rationale = _decide_proxy(
        pooled_det_corr=pooled_det_corr,
        mean_mde_tbr=mde_tbr,
        mean_mde_scm=mde_scm,
        pooled_null_tbr=pooled_tbr.get(0.0, float("nan")),
        pooled_null_scm=pooled_scm.get(0.0, float("nan")),
        mean_resp_tbr=_summarize(resp_tbr)["mean"],
        mean_resp_scm=_summarize(resp_scm)["mean"],
        mean_grid_corr_tbr=_summarize(grid_corr_tbr)["mean"],
        mean_grid_corr_scm=_summarize(grid_corr_scm)["mean"],
        mean_pa_mde=_summarize(pa_mde)["mean"],
    )

    pow003_status = "restricted"
    if verdict in ("unrelated_misleading", "optimistic_proxy"):
        pow003_status = "restricted"
    elif verdict == "narrow_diagnostics_only":
        pow003_status = "characterization_required"

    return {
        "artifact_id": "D5-POW-001a",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "lane": "research",
        "investigation_id": "D4-FIND-001",
        "config": asdict(cfg),
        "hypothesis": (
            "Geo TBRRidge+KFold MDE on aggregated panel may not align with "
            "SCM+UnitJackKnife readout on the same assignment."
        ),
        "primary_metrics": {
            "pooled_detection_curve_corr": {"mean": pooled_det_corr, "std": 0.0, "p95": pooled_det_corr},
            "mde_pooled_detection_tbr": {"mean": mde_tbr, "std": 0.0, "p95": mde_tbr},
            "mde_pooled_detection_scm": {"mean": mde_scm, "std": 0.0, "p95": mde_scm},
            "pooled_null_detection_tbr": {
                "mean": pooled_tbr.get(0.0, float("nan")),
                "std": 0.0,
                "p95": pooled_tbr.get(0.0, float("nan")),
            },
            "pooled_null_detection_scm": {
                "mean": pooled_scm.get(0.0, float("nan")),
                "std": 0.0,
                "p95": pooled_scm.get(0.0, float("nan")),
            },
            "effect_response_8pct_tbr": _summarize(resp_tbr),
            "effect_response_8pct_scm": _summarize(resp_scm),
            "effect_grid_corr_tbr": _summarize(grid_corr_tbr),
            "effect_grid_corr_scm": _summarize(grid_corr_scm),
            "directional_recovery_tbr": _summarize(
                [r["directional_recovery_tbr"] for r in rows]
            ),
            "directional_recovery_scm": _summarize(
                [r["directional_recovery_scm"] for r in rows]
            ),
            "poweranalysis_mde_percent_geo": _summarize(pa_mde),
        },
        "pooled_detection_curves": {
            "tbr_kfold": {str(k): v for k, v in pooled_tbr.items()},
            "scm_unit_jk": {str(k): v for k, v in pooled_scm.items()},
        },
        "n_replicates": len(rows),
        "proxy_verdict": verdict,
        "rationale": rationale,
        "pow_001_status": "diagnostic_only",
        "pow_003_status_recommendation": pow003_status,
        "d4_find_001_update": verdict,
        "calibration_eligibility_changed": False,
        "notes": [
            "SCM_UnitJackKnife remains null_monitor_only.",
            "Do not use geo PowerAnalysis MDE for MMM or lift feasibility.",
            "TBRRidge+KFold on 2-row panel vs SCM+JK on unit panel — geometry differs by design.",
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
