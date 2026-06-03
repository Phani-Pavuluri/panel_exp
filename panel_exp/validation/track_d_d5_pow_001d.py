"""D5-POW-001d — Pre/post window sensitivity for design-readout OC (research).

Varies pre-period and post-period lengths under greedy pre-period matching with
unit-level SCM+UnitJackKnife readout. Compares fixed experiment windows to a
single PowerAnalysis-style circular sliding window per configuration.
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

WindowSensitivityVerdict = Literal[
    "stable",
    "moderately_sensitive",
    "unstable",
    "fixed_window_preferred",
]

TRACK_E_SUITABILITY_DIAGNOSTICS: tuple[dict[str, str], ...] = (
    {
        "id": "E-POW-WIN-001",
        "diagnostic": "pre_period_balance_corr",
        "description": "Pearson corr of summed treated vs control KPI in pre-period; flag if below 0.5.",
    },
    {
        "id": "E-POW-WIN-002",
        "diagnostic": "assignment_jaccard_vs_baseline",
        "description": "Overlap of treated markets vs baseline window on same DGP seed.",
    },
    {
        "id": "E-POW-WIN-003",
        "diagnostic": "null_interval_exclusion_fpr",
        "description": "SCM+JK null FPR using correct effect_lo/hi (post D5-POW-001b).",
    },
    {
        "id": "E-POW-WIN-004",
        "diagnostic": "null_monitor_cell_coverage",
        "description": "Fraction of post period×unit cells where JK interval covers zero at null.",
    },
    {
        "id": "E-POW-WIN-005",
        "diagnostic": "injection_grid_point_correlation",
        "description": "Correlation of injected vs mean point effect across small grid.",
    },
    {
        "id": "E-POW-WIN-006",
        "diagnostic": "window_mode_disagreement",
        "description": "Fixed experiment window vs one circular sliding window (PowerAnalysis style).",
    },
    {
        "id": "E-POW-WIN-007",
        "diagnostic": "pre_post_length_bounds",
        "description": "Reject or warn when train_length or test_length outside characterized grid.",
    },
)


@dataclass(frozen=True)
class WindowSpec:
    train_length: int
    test_length: int

    @property
    def key(self) -> str:
        return f"pre{self.train_length}_post{self.test_length}"

    def to_dict(self) -> dict[str, int]:
        return {"train_length": self.train_length, "test_length": self.test_length}


@dataclass(frozen=True)
class D5Pow001dConfig:
    n_mc: int = 20
    n_geos: int = 16
    n_periods: int = 44
    treatment_start: int = 32
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260604
    scenario_name: str = "scm_low_signal"
    min_control_units: int = 2
    baseline_window: WindowSpec = WindowSpec(train_length=28, test_length=8)
    window_grid: tuple[WindowSpec, ...] = (
        WindowSpec(20, 8),
        WindowSpec(24, 8),
        WindowSpec(28, 8),
        WindowSpec(32, 8),
        WindowSpec(28, 4),
        WindowSpec(28, 6),
        WindowSpec(28, 10),
        WindowSpec(28, 12),
    )
    effect_grid: tuple[float, ...] = (0.0, 0.04, 0.08, 0.12)
    include_circular_sliding_sample: bool = True


def _assign_greedy(
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


def _design_context(
    spec: WindowSpec,
    *,
    treated: list[str],
    n_geos: int,
    treatment_probability: float,
    readout_instrument: str,
    window_construction: str,
) -> dict[str, Any]:
    end = spec.train_length + spec.test_length
    n_control = n_geos - len(treated)
    return {
        "design_method_id": "greedy_match_markets",
        "design_method_tier": "tier_1_production_geo",
        "balance_objective": "corr",
        "assignment_constraints": {
            "pre_treatment_period_only": True,
            "n_test_groups": 1,
            "treatment_probability": treatment_probability,
        },
        "pre_period_length": spec.train_length,
        "post_period_length": spec.test_length,
        "pre_period_window": {"start": 0, "end": spec.train_length - 1},
        "post_period_window": {"start": spec.train_length, "end": end - 1},
        "window_construction": window_construction,
        "assignment_geometry": "unit_level_markets",
        "n_geos": n_geos,
        "n_treated_markets": len(treated),
        "n_control_markets": n_control,
        "test_control_ratio": float(len(treated) / n_control) if n_control else float("nan"),
        "readout_instrument": readout_instrument,
    }


def _pre_period_balance(
    wide: pd.DataFrame,
    treated: list[str],
    *,
    n_pre: int,
) -> dict[str, float]:
    pre = wide.iloc[:, :n_pre]
    t_sum = pre.loc[treated].sum(axis=0).values.astype(float)
    c_sum = pre.drop(treated).sum(axis=0).values.astype(float)
    if np.std(t_sum) < 1e-12 or np.std(c_sum) < 1e-12:
        corr = float("nan")
    else:
        corr = float(np.corrcoef(t_sum, c_sum)[0, 1])
    rel_diff = float(np.mean(np.abs(t_sum - c_sum) / (np.abs(c_sum) + 1e-6)))
    return {"pre_balance_corr": corr, "pre_balance_mean_rel_diff": rel_diff}


def _jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return float(len(sa & sb) / len(sa | sb)) if (sa | sb) else float("nan")


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


def _fixed_window_panel(
    wide: pd.DataFrame,
    treated: list[str],
    spec: WindowSpec,
) -> PanelDataset:
    end = spec.train_length + spec.test_length
    return PanelDataset(
        wide.iloc[:, :end].copy(),
        treated_periods=[TimePeriod(spec.train_length, end - 1) for _ in treated],
        treated_units=treated,
    )


def _circular_sliding_panel(
    wide: pd.DataFrame,
    treated: list[str],
    spec: WindowSpec,
    *,
    anchor: int,
) -> PanelDataset:
    """One PowerAnalysis-style circular train+test concat (research approximation)."""
    segment = wide.iloc[:, : spec.train_length + spec.test_length]
    L = segment.shape[1]
    train_idx = [(anchor + j) % L for j in range(spec.train_length)]
    test_idx = [(anchor + spec.train_length + j) % L for j in range(spec.test_length)]
    order = train_idx + test_idx
    reordered = segment.iloc[:, order].copy()
    return PanelDataset(
        reordered,
        treated_periods=[TimePeriod(spec.train_length, L - 1) for _ in treated],
        treated_units=treated,
    )


def _scm_jk_metrics(
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
    y = np.asarray(est.results["y"], dtype=float)
    y_hat = np.asarray(est.results["y_hat"], dtype=float)
    y_lo = np.asarray(est.results["y_lower"], dtype=float)
    y_hi = np.asarray(est.results["y_upper"], dtype=float)
    sl = slice(-test_length, None)
    y, y_hat, y_lo, y_hi = y[sl], y_hat[sl], y_lo[sl], y_hi[sl]
    effect = y - y_hat
    effect_lo = y - y_hi
    effect_hi = y - y_lo
    point_mean = float(np.mean(effect))
    covers_zero = float(np.mean(effect_lo) <= 0.0 <= np.mean(effect_hi))
    cell_covers = (effect_lo <= 0.0) & (0.0 <= effect_hi)
    inj_sign = float(np.sign(percent_effect)) if abs(percent_effect) > 1e-12 else 0.0
    sign_ok = float(
        inj_sign == 0.0 or (np.isfinite(point_mean) and np.sign(point_mean) == inj_sign)
    )
    return {
        "mean_point_effect": point_mean,
        "detected_interval_excludes_zero": float(not covers_zero),
        "cell_covers_zero_rate": float(np.mean(cell_covers)),
        "cell_detected_rate": float(np.mean(~cell_covers)),
        "directional_recovery": sign_ok,
        "mean_jk_halfwidth": float(np.mean((y_hi - y_lo) / 2.0)),
    }


def _effect_grid_corr(curve: dict[float, dict[str, float]]) -> float:
    keys = sorted(curve.keys())
    if len(keys) < 2:
        return float("nan")
    inj = np.array(keys, dtype=float)
    pts = np.array([curve[k]["mean_point_effect"] for k in keys], dtype=float)
    if np.std(inj) < 1e-12 or np.std(pts) < 1e-12:
        return float("nan")
    return float(np.corrcoef(inj, pts)[0, 1])


def _evaluate_window(
    wide: pd.DataFrame,
    spec: WindowSpec,
    *,
    seed: int,
    cfg: D5Pow001dConfig,
    baseline_treated: list[str] | None,
) -> dict[str, Any]:
    if spec.train_length + spec.test_length > wide.shape[1]:
        raise ValueError("window exceeds available periods")

    treated = _assign_greedy(
        wide,
        n_pre=spec.train_length,
        seed=seed,
        treatment_probability=cfg.treatment_probability,
    )
    n_ctrl = len([u for u in wide.index if u not in treated])
    if n_ctrl < cfg.min_control_units:
        raise ValueError("insufficient control units")

    balance = _pre_period_balance(wide, treated, n_pre=spec.train_length)
    stability = (
        {"assignment_jaccard_vs_baseline": _jaccard(treated, baseline_treated)}
        if baseline_treated is not None
        else {}
    )

    panel = _fixed_window_panel(wide, treated, spec)
    mean_value = _mean_treated_baseline(panel)
    curve: dict[float, dict[str, float]] = {}
    for prc in cfg.effect_grid:
        curve[float(prc)] = _scm_jk_metrics(
            panel,
            percent_effect=float(prc),
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=spec.test_length,
        )

    circular_null_delta = float("nan")
    if cfg.include_circular_sliding_sample:
        anchor = (seed % (spec.train_length + spec.test_length))
        circ = _circular_sliding_panel(wide, treated, spec, anchor=anchor)
        null_fixed = curve[0.0]["mean_point_effect"]
        null_circ = _scm_jk_metrics(
            circ,
            percent_effect=0.0,
            mean_value=_mean_treated_baseline(circ),
            alpha=cfg.alpha,
            test_length=spec.test_length,
        )["mean_point_effect"]
        if np.isfinite(null_fixed) and np.isfinite(null_circ):
            circular_null_delta = float(null_circ - null_fixed)

    null_m = curve[0.0]
    pos_m = curve.get(0.08, null_m)

    return {
        "window": spec.to_dict(),
        "window_key": spec.key,
        "design_context": _design_context(
            spec,
            treated=treated,
            n_geos=cfg.n_geos,
            treatment_probability=cfg.treatment_probability,
            readout_instrument="SyntheticControl+UnitJackKnife",
            window_construction="fixed_experiment_window",
        ),
        "treated_units": treated,
        **balance,
        **stability,
        "null_fpr": null_m["detected_interval_excludes_zero"],
        "null_cell_covers_zero_rate": null_m["cell_covers_zero_rate"],
        "effect_grid_corr": _effect_grid_corr(curve),
        "directional_recovery_8pct": pos_m["directional_recovery"],
        "effect_response_8pct": float(pos_m["mean_point_effect"] - null_m["mean_point_effect"]),
        "circular_vs_fixed_null_point_delta": circular_null_delta,
        "by_effect": {str(k): v for k, v in curve.items()},
    }


def run_one_replicate(cfg: D5Pow001dConfig, *, seed: int) -> dict[str, Any]:
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

    baseline_treated = _assign_greedy(
        wide,
        n_pre=cfg.baseline_window.train_length,
        seed=seed,
        treatment_probability=cfg.treatment_probability,
    )

    per_window: list[dict[str, Any]] = []
    for spec in cfg.window_grid:
        try:
            per_window.append(
                _evaluate_window(
                    wide,
                    spec,
                    seed=seed,
                    cfg=cfg,
                    baseline_treated=baseline_treated,
                )
            )
        except ValueError:
            continue

    if not per_window:
        raise ValueError("no valid windows for replicate")

    return {"seed": seed, "windows": per_window}


def _summarize(vals: list[float]) -> dict[str, float]:
    arr = np.array([v for v in vals if np.isfinite(v)], dtype=float)
    if arr.size == 0:
        return {"mean": float("nan"), "std": float("nan"), "p95": float("nan")}
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "p95": float(np.percentile(arr, 95)),
    }


def _aggregate_by_window(rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = sorted({w["window_key"] for r in rows for w in r["windows"]})
    out: dict[str, Any] = {}
    for key in keys:
        samples = [w for r in rows for w in r["windows"] if w["window_key"] == key]
        out[key] = {
            "window": samples[0]["window"],
            "design_context": samples[0]["design_context"],
            "pre_balance_corr": _summarize([s["pre_balance_corr"] for s in samples]),
            "assignment_jaccard_vs_baseline": _summarize(
                [s.get("assignment_jaccard_vs_baseline", float("nan")) for s in samples]
            ),
            "null_fpr": _summarize([s["null_fpr"] for s in samples]),
            "null_cell_covers_zero_rate": _summarize(
                [s["null_cell_covers_zero_rate"] for s in samples]
            ),
            "effect_grid_corr": _summarize([s["effect_grid_corr"] for s in samples]),
            "effect_response_8pct": _summarize([s["effect_response_8pct"] for s in samples]),
            "circular_vs_fixed_null_point_delta": _summarize(
                [s["circular_vs_fixed_null_point_delta"] for s in samples]
            ),
            "n_replicates": len(samples),
        }
    return out


def _decide_sensitivity(
    by_window: dict[str, Any],
    *,
    baseline_key: str,
) -> tuple[WindowSensitivityVerdict, str, list[str]]:
    if baseline_key not in by_window:
        return (
            "unstable",
            "Baseline window missing from aggregation.",
            ["missing_baseline"],
        )

    base = by_window[baseline_key]
    null_fprs = [by_window[k]["null_fpr"]["mean"] for k in by_window]
    grid_corrs = [by_window[k]["effect_grid_corr"]["mean"] for k in by_window]
    circ_deltas = [
        abs(by_window[k]["circular_vs_fixed_null_point_delta"]["mean"])
        for k in by_window
        if np.isfinite(by_window[k]["circular_vs_fixed_null_point_delta"]["mean"])
    ]

    null_range = float(np.nanmax(null_fprs) - np.nanmin(null_fprs)) if null_fprs else float("nan")
    corr_range = float(np.nanmax(grid_corrs) - np.nanmin(grid_corrs)) if grid_corrs else float("nan")
    circ_mean = float(np.nanmean(circ_deltas)) if circ_deltas else float("nan")

    track_e_flags: list[str] = []
    if null_range > 0.25:
        track_e_flags.append("null_fpr_window_sensitive")
    if corr_range > 0.2:
        track_e_flags.append("point_tracking_window_sensitive")
    if np.isfinite(circ_mean) and circ_mean > 5.0:
        track_e_flags.append("circular_sliding_disagrees_with_fixed")

    if null_range > 0.4 or corr_range > 0.35:
        return (
            "unstable",
            "SCM+JK null FPR and/or injection-grid tracking vary strongly across pre/post "
            "windows; window choice is not a neutral nuisance parameter.",
            track_e_flags,
        )

    if null_range > 0.15 or corr_range > 0.1 or (np.isfinite(circ_mean) and circ_mean > 2.0):
        return (
            "moderately_sensitive",
            "Readout OC metrics are moderately sensitive to pre/post length; Track E should "
            "gate suitability on documented window bounds (see E-POW-WIN-* diagnostics).",
            track_e_flags,
        )

    return (
        "fixed_window_preferred",
        "Readout metrics are relatively stable across characterized windows; prefer fixed "
        "experiment pre/post windows over PowerAnalysis circular sliding for governed SCM+JK "
        "interpretation (aligns with D4-FIND-006 accepted_deviation for geo power only).",
        track_e_flags,
    )


def run_d5_pow_001d(config: D5Pow001dConfig | None = None) -> dict[str, Any]:
    cfg = config or D5Pow001dConfig()
    rows: list[dict[str, Any]] = []
    attempts = 0
    while len(rows) < cfg.n_mc and attempts < cfg.n_mc * 3:
        seed = cfg.random_state_base + attempts
        attempts += 1
        try:
            rows.append(run_one_replicate(cfg, seed=seed))
        except ValueError:
            continue
    if not rows:
        raise RuntimeError("D5-POW-001d: no valid replicates")

    by_window = _aggregate_by_window(rows)
    verdict, rationale, track_e_flags = _decide_sensitivity(
        by_window,
        baseline_key=cfg.baseline_window.key,
    )

    return {
        "artifact_id": "D5-POW-001d",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "lane": "research",
        "investigation_id": "D4-FIND-006",
        "prior_artifacts": [
            "docs/track_d/archives/D5_POW_001a_results.json",
            "docs/track_d/archives/D5_POW_001b_results.json",
            "docs/track_d/archives/D5_POW_001c_results.json",
        ],
        "config": {
            **asdict(cfg),
            "baseline_window": cfg.baseline_window.to_dict(),
            "window_grid": [w.to_dict() for w in cfg.window_grid],
        },
        "hypothesis": (
            "Pre/post window length and construction affect greedy assignment balance "
            "and unit-level SCM+JK readout OC metrics."
        ),
        "by_window_summary": by_window,
        "window_sensitivity_verdict": verdict,
        "rationale": rationale,
        "track_e_suitability_diagnostics": list(TRACK_E_SUITABILITY_DIAGNOSTICS),
        "track_e_flags": track_e_flags,
        "d4_find_006_update": verdict,
        "n_replicates": len(rows),
        "pow_001_window_recommendation": (
            "Use fixed design pre/post windows for SCM+JK readout OC; do not interpret "
            "PowerAnalysis circular sliding windows as governed readout behavior."
        ),
        "calibration_eligibility_changed": False,
        "notes": [
            "Design method: greedy_match_markets with pre-period-only assignment.",
            "Unit-level geometry preserved (no 2-row aggregation).",
            "Null FPR uses correct effect_lo/hi semantics (D5-POW-001b).",
            "No production design, power, inference, or eligibility changes.",
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
