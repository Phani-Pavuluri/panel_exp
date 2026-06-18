"""D5-TRUST-TBRRIDGE-PLACEBO-001 — TBRRidge + Placebo qualification.

Characterizes DCM-005 Placebo path: placebo-in-space null reference, falsification
semantics, geometry constraints, and TrustReport eligibility. No production changes.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import time
import warnings
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.governance.investigation_lifecycle_contract import (
    build_investigation_handoff,
    format_handoff_report_section,
)
from panel_exp.methods.tbr import TBRRidge
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_pow_001c import _post_window_arrays, _pooled_point_path
from panel_exp.validation.track_d_d5_stat_tbrridge_inf_001 import (
    GEOMETRY,
    _geometry_guard,
    _inject_percent_effect,
    _json_safe,
    _mean_treated_baseline,
)
from panel_exp.validation.track_d_d5_trust_tbrridge_brb_001 import (
    _assign_treated_units,
    _mean,
    _prefit_rmse,
    _rate,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARTIFACT_ID = "D5-TRUST-TBRRIDGE-PLACEBO-001"
_ARTIFACT_VERSION = "1.0.0"
_CANONICAL_SCALE = "level_mean_relative_percent_injection"
_INVESTIGATION_ID = "INV-TBRRIDGE-PLACEBO-GOVERNED-SEMANTICS-001"
_DEFAULT_SUMMARY = _REPO_ROOT / "docs/track_d/archives/D5_TRUST_TBRRIDGE_PLACEBO_001_summary.json"
_DEFAULT_REPORT = _REPO_ROOT / "docs/track_d/D5_TRUST_TBRRIDGE_PLACEBO_001_REPORT.md"
_MIN_CONTROLS_PRODUCTION = 5

SemanticVerdict = Literal[
    "tbrridge_placebo_null_monitor_only",
    "tbrridge_placebo_falsification_diagnostic_only",
    "tbrridge_placebo_single_treated_restricted",
    "tbrridge_placebo_not_causal_interval_eligible",
    "tbrridge_placebo_production_defect_confirmed",
    "tbrridge_placebo_remediation_inconclusive",
    "tbrridge_placebo_remediation_failed",
]

ProductionDefectDecision = Literal[
    "production_defect_confirmed",
    "production_defect_not_confirmed",
    "production_defect_indeterminate",
    "method_unsuitable_for_causal_interval",
]

POLICY_COMPARISONS: tuple[dict[str, str], ...] = (
    {"policy_id": "A", "name": "current_placebo", "description": "production placebo-in-space with RMSPE filter"},
    {"policy_id": "B", "name": "prefit_gated_placebo", "description": "acceptable pre-period fit only"},
    {"policy_id": "C", "name": "single_treated_only", "description": "exactly one treated unit (production requirement)"},
    {"policy_id": "D", "name": "minimum_control_count", "description": "requires >=5 control units"},
    {"policy_id": "E", "name": "null_monitor_only", "description": "placebo envelope / p-value falsification only"},
    {"policy_id": "F", "name": "causal_interval_blocked", "description": "DCM-005 registry block until reassessment"},
)


@dataclass(frozen=True)
class DiagnosticWorldSpec:
    world_id: str
    scenario_name: str = "scm_low_signal"
    percent_effect: float = 0.0
    n_geos: int = 16
    n_periods: int = 44
    treatment_probability: float = 0.35
    train_length: int | None = None
    test_length: int | None = None
    scenario_overrides: dict[str, Any] = field(default_factory=dict)
    serial_dependence_regime: str = "clean_iid"
    notes: str = ""


@dataclass(frozen=True)
class GeometrySpec:
    geometry_id: str
    force_single_treated: bool = True
    n_geos: int | None = None
    treatment_probability: float | None = None
    notes: str = ""


@dataclass(frozen=True)
class PlaceboTrustConfig:
    n_replicates: int = 3
    n_replicates_fast: int = 2
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    random_state_base: int = 20260622
    min_control_units: int = 3
    fast: bool = False
    effect_sizes: tuple[float, ...] = (0.0, 0.03, 0.08, 0.12, -0.05)
    write_full_results_path: str | None = "/tmp/D5_TRUST_TBRRIDGE_PLACEBO_001_results.json"


DIAGNOSTIC_WORLDS: tuple[DiagnosticWorldSpec, ...] = (
    DiagnosticWorldSpec("clean_null", percent_effect=0.0),
    DiagnosticWorldSpec("clean_positive_effect", percent_effect=0.08),
    DiagnosticWorldSpec("clean_negative_effect", percent_effect=-0.05),
    DiagnosticWorldSpec("weak_signal", percent_effect=0.03, scenario_overrides={"noise_scale": 3.5}),
    DiagnosticWorldSpec("strong_signal", percent_effect=0.12),
    DiagnosticWorldSpec(
        "serial_correlation",
        percent_effect=0.08,
        scenario_overrides={"autocorrelation": 0.7},
        serial_dependence_regime="serial_correlation",
    ),
    DiagnosticWorldSpec(
        "high_serial_correlation",
        percent_effect=0.08,
        scenario_overrides={"autocorrelation": 0.92},
        serial_dependence_regime="high_serial_correlation",
    ),
    DiagnosticWorldSpec(
        "heteroskedasticity",
        percent_effect=0.08,
        scenario_overrides={"noise_scale": 4.8},
        serial_dependence_regime="heteroskedastic",
    ),
    DiagnosticWorldSpec(
        "regime_shift",
        scenario_name="scm_structural_break",
        percent_effect=0.08,
        scenario_overrides={"structural_break_shift": 12.0},
    ),
    DiagnosticWorldSpec(
        "post_treatment_shock",
        scenario_name="scm_structural_break",
        percent_effect=0.0,
        scenario_overrides={"structural_break_shift": 22.0},
    ),
    DiagnosticWorldSpec(
        "pre_trend_violation",
        scenario_name="scm_trend_mismatch",
        percent_effect=0.0,
    ),
    DiagnosticWorldSpec(
        "poor_pre_fit",
        percent_effect=0.08,
        scenario_overrides={"noise_scale": 5.5, "cross_geo_correlation": 0.02},
    ),
    DiagnosticWorldSpec(
        "outlier_period",
        percent_effect=0.08,
        scenario_overrides={"noise_scale": 2.0, "structural_break_shift": 8.0},
    ),
    DiagnosticWorldSpec(
        "small_donor_set",
        percent_effect=0.08,
        n_geos=10,
        treatment_probability=0.45,
    ),
    DiagnosticWorldSpec(
        "large_donor_set",
        percent_effect=0.08,
        n_geos=22,
        treatment_probability=0.2,
    ),
    DiagnosticWorldSpec(
        "low_noise_null",
        percent_effect=0.0,
        scenario_overrides={"noise_scale": 0.4},
    ),
    DiagnosticWorldSpec(
        "contaminated_donor",
        percent_effect=0.08,
        scenario_overrides={"cross_geo_correlation": 0.95},
        notes="high donor contamination stress",
    ),
    DiagnosticWorldSpec("placebo_null", percent_effect=0.0),
)

GEOMETRY_VARIANTS: tuple[GeometrySpec, ...] = (
    GeometrySpec("single_treated_unit", force_single_treated=True, notes="production-supported geometry"),
    GeometrySpec(
        "multiple_treated_units",
        force_single_treated=False,
        notes="unsupported — placebo-in-space requires exactly one treated unit",
    ),
    GeometrySpec(
        "small_control_pool",
        force_single_treated=True,
        n_geos=9,
        treatment_probability=0.55,
        notes="may fail minimum control count gate",
    ),
    GeometrySpec(
        "large_control_pool",
        force_single_treated=True,
        n_geos=24,
        treatment_probability=0.2,
        notes="many donors",
    ),
)

_EFFECT_SWEEP_WORLDS = frozenset({"clean_null", "clean_positive_effect", "weak_signal", "strong_signal"})


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=_REPO_ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _effective_lengths(spec: DiagnosticWorldSpec, cfg: PlaceboTrustConfig) -> tuple[int, int]:
    train = spec.train_length if spec.train_length is not None else cfg.train_length
    test = spec.test_length if spec.test_length is not None else cfg.test_length
    return train, test


def _build_base_panel(
    spec: DiagnosticWorldSpec,
    geom: GeometrySpec,
    cfg: PlaceboTrustConfig,
    *,
    seed: int,
) -> PanelDataset:
    train, test = _effective_lengths(spec, cfg)
    post_end = train + test - 1
    n_geos = geom.n_geos if geom.n_geos is not None else spec.n_geos
    t_prob = geom.treatment_probability if geom.treatment_probability is not None else spec.treatment_probability
    base = RECOVERY_SCENARIO_REGISTRY[spec.scenario_name]
    scenario = replace(
        base,
        random_state=seed,
        n_geos=n_geos,
        n_periods=max(spec.n_periods, post_end + 1),
        treatment_start=train,
        true_effect=0.0,
        **(spec.scenario_overrides or {}),
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    last_panel: PanelDataset | None = None
    for assign_attempt in range(24):
        assign_seed = seed + assign_attempt * 31
        treated = _assign_treated_units(
            wide,
            n_pre=train,
            seed=assign_seed,
            treatment_probability=t_prob,
        )
        control = [u for u in wide.index if u not in treated]
        if geom.force_single_treated:
            treated = [treated[0]]
        units = control + treated
        end = train + test
        panel = PanelDataset(
            wide.loc[units].iloc[:, :end].copy(),
            treated_periods=[TimePeriod(train, end - 1) for _ in treated],
            treated_units=treated,
        )
        last_panel = panel
        if panel.num_control_units >= cfg.min_control_units:
            return panel
    if last_panel is None:
        raise ValueError("assignment produced no panel")
    raise ValueError("insufficient control units after assignment")


def _level_true_effect(percent_effect: float, mean_value: np.ndarray) -> float:
    if abs(percent_effect) < 1e-12:
        return 0.0
    return float(percent_effect * np.mean(mean_value))


def _inference_kwargs() -> dict[str, Any]:
    return {"use_rmspe_filter": True, "max_pre_rmspe_multiple": 5.0}


def _placebo_rank(placebo_stats: np.ndarray, observed_stat: float) -> float | None:
    if placebo_stats.size == 0 or not np.isfinite(observed_stat):
        return None
    return float(np.mean(np.abs(placebo_stats) >= abs(observed_stat)))


def _readout_placebo(
    results: dict[str, Any],
    *,
    test_len: int,
    true_effect_level: float,
    alpha: float,
) -> dict[str, Any]:
    y, y_hat, y_lo, y_hi = _post_window_arrays(results, test_length=test_len)
    y_pt, y_hat_pt = _pooled_point_path(y, y_hat)
    point_estimate = float(np.nanmean(y_pt - y_hat_pt))

    ps = results.get("placebo_stats") or {}
    placebo_stats = np.asarray(ps.get("placebo_stats", []), dtype=float)
    placebo_stats = placebo_stats[np.isfinite(placebo_stats)]
    observed_stat = ps.get("observed_stat")
    p_value = ps.get("p_value")
    ci_low = ps.get("ci_low_inversion")
    ci_high = ps.get("ci_high_inversion")

    placebo_mean = float(np.nanmean(placebo_stats)) if placebo_stats.size else None
    placebo_median = float(np.nanmedian(placebo_stats)) if placebo_stats.size else None
    placebo_std = float(np.nanstd(placebo_stats, ddof=1)) if placebo_stats.size > 1 else None
    placebo_rank = _placebo_rank(placebo_stats, float(observed_stat)) if observed_stat is not None else None

    interval_present = y_lo.size > 0 and y_hi.size > 0
    placebo_lower = placebo_upper = None
    contains_point = contains_truth = contains_zero = None
    if interval_present:
        eff_lo = y - y_hi
        eff_hi = y - y_lo
        placebo_lower = float(np.nanmean(eff_lo))
        placebo_upper = float(np.nanmean(eff_hi))
        contains_point = bool(placebo_lower <= point_estimate <= placebo_upper)
        contains_zero = bool(placebo_lower <= 0.0 <= placebo_upper)
        if np.isfinite(placebo_lower) and np.isfinite(placebo_upper):
            contains_truth = bool(placebo_lower <= true_effect_level <= placebo_upper)

    is_null = abs(true_effect_level) < 1e-9
    null_rejection = bool(p_value is not None and np.isfinite(p_value) and p_value < alpha)
    if is_null:
        sign_correct = bool(not null_rejection)
    else:
        sign_correct = bool(
            np.isfinite(point_estimate) and np.sign(point_estimate) == np.sign(true_effect_level)
        )

    return {
        "point_estimate": point_estimate,
        "true_effect": true_effect_level,
        "effect_scale": _CANONICAL_SCALE,
        "point_estimate_scale": "level_mean_shift",
        "placebo_statistic_scale": "level_mean_post_window_att",
        "placebo_distribution_scale": "level_mean_placebo_att",
        "readout_scale": "level_mean_shift",
        "bias": float(point_estimate - true_effect_level),
        "squared_error": float((point_estimate - true_effect_level) ** 2),
        "sign_correct": sign_correct,
        "placebo_statistics": placebo_stats.tolist() if placebo_stats.size else [],
        "placebo_mean": placebo_mean,
        "placebo_median": placebo_median,
        "placebo_standard_deviation": placebo_std,
        "placebo_rank": placebo_rank,
        "placebo_p_value": float(p_value) if p_value is not None and np.isfinite(p_value) else None,
        "placebo_lower": placebo_lower,
        "placebo_upper": placebo_upper,
        "contains_point": contains_point,
        "contains_truth": contains_truth,
        "contains_zero": contains_zero,
        "null_rejection": null_rejection,
        "inversion_ci_lower": float(ci_low) if ci_low is not None and np.isfinite(ci_low) else None,
        "inversion_ci_upper": float(ci_high) if ci_high is not None and np.isfinite(ci_high) else None,
        "band_type": ps.get("band_type"),
        "finite_outputs": bool(np.isfinite(point_estimate)),
        "n_placebo_draws": int(placebo_stats.size),
    }


def _run_one(
    spec: DiagnosticWorldSpec,
    geom: GeometrySpec,
    cfg: PlaceboTrustConfig,
    *,
    replicate_id: int,
    seed: int,
    percent_effect: float | None = None,
) -> dict[str, Any]:
    train, test = _effective_lengths(spec, cfg)
    eff_pct = spec.percent_effect if percent_effect is None else percent_effect
    base: dict[str, Any] = {
        "world_id": spec.world_id,
        "replicate_id": replicate_id,
        "seed": seed,
        "effect_size": float(eff_pct),
        "effect_scale": _CANONICAL_SCALE,
        "geometry_id": geom.geometry_id,
        "exchangeability_assumption": "placebo_in_space_iid_donors",
        "geometry_supported": True,
        "geometry_failure_reason": None,
    }
    try:
        panel = _build_base_panel(spec, geom, cfg, seed=seed)
        geom_ok, geom_reason = _geometry_guard(panel)
        if not geom_ok:
            raise ValueError(f"geometry_guard_failed:{geom_reason}")

        n_treated = len(panel.treated_units)
        n_control = panel.num_control_units
        base.update(
            {
                "n_treated": n_treated,
                "n_control": n_control,
                "n_placebo_draws": None,
            }
        )

        if not geom.force_single_treated and n_treated != 1:
            base["geometry_supported"] = False
            raise NotImplementedError("placebo-in-space currently supports exactly one treated unit")
        if n_treated != 1:
            base["geometry_supported"] = False
            raise NotImplementedError("placebo-in-space currently supports exactly one treated unit")
        if n_control < _MIN_CONTROLS_PRODUCTION:
            base["geometry_supported"] = False
            raise ValueError(f"Placebo requires >=5 control units (got {n_control})")

        mean_value = _mean_treated_baseline(panel)
        true_level = _level_true_effect(eff_pct, mean_value)
        pds = _inject_percent_effect(panel, eff_pct, mean_value)

        est = TBRRidge(inference="Placebo", alpha=cfg.alpha)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            est.run_analysis(pds, **_inference_kwargs())

        results = getattr(est, "results", {}) or {}
        readout = _readout_placebo(
            results,
            test_len=test,
            true_effect_level=true_level,
            alpha=cfg.alpha,
        )

        ridge_alpha = None
        model = getattr(est, "model", None)
        if model is not None and hasattr(model, "alpha_"):
            ridge_alpha = float(model.alpha_)
        y_hat = np.asarray(results.get("y_hat", []), dtype=float)
        prefit = _prefit_rmse(pds, y_hat) if y_hat.size else float("nan")

        exchangeability = "assumed_under_placebo_in_space"
        if spec.serial_dependence_regime in ("serial_correlation", "high_serial_correlation"):
            exchangeability = "serial_dependence_caveat"

        return {
            **base,
            **readout,
            "true_effect_percent": float(eff_pct),
            "truth_scale": _CANONICAL_SCALE,
            "prefit_rmse": prefit,
            "ridge_alpha": ridge_alpha,
            "exchangeability_status": exchangeability,
            "failure_status": "ok",
            "failure_reason": None,
        }
    except Exception as exc:
        msg = str(exc)[:300]
        geom_supported = "one treated unit" not in msg.lower() and "control units" not in msg.lower()
        return {
            **base,
            "point_estimate": None,
            "true_effect": None,
            "bias": None,
            "squared_error": None,
            "placebo_p_value": None,
            "null_rejection": None,
            "sign_correct": None,
            "failure_status": "fail",
            "failure_reason": msg,
            "geometry_supported": geom_supported,
        }


def _metrics(runs: list[dict[str, Any]]) -> dict[str, Any]:
    null_runs = [r for r in runs if r.get("true_effect") is not None and abs(r["true_effect"]) < 1e-9]
    pos_runs = [r for r in runs if r.get("true_effect") is not None and r["true_effect"] > 1e-9]
    neg_runs = [r for r in runs if r.get("true_effect") is not None and r["true_effect"] < -1e-9]
    return {
        "type_i_error": None
        if not null_runs
        else _rate([r.get("null_rejection") for r in null_runs if r.get("null_rejection") is not None]),
        "power": None if not pos_runs else _rate([r.get("null_rejection") for r in pos_runs]),
        "negative_power": None if not neg_runs else _rate([r.get("null_rejection") for r in neg_runs]),
        "sign_accuracy": _rate([r.get("sign_correct") for r in runs]),
        "mean_placebo_rank_null": _mean([r.get("placebo_rank") for r in null_runs]),
        "n_null": len(null_runs),
        "n_positive": len(pos_runs),
        "n_negative": len(neg_runs),
        "n_ok": len([r for r in runs if r.get("failure_status") == "ok"]),
    }


def _group_metrics(runs: list[dict[str, Any]], key: str) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for r in runs:
        groups.setdefault(str(r.get(key, "unknown")), []).append(r)
    return {k: _metrics(v) for k, v in groups.items()}


def _production_defect_assessment(ok_runs: list[dict[str, Any]]) -> dict[str, Any]:
    null_runs = [r for r in ok_runs if abs(r.get("true_effect") or 0) < 1e-9]
    pos_runs = [r for r in ok_runs if (r.get("true_effect") or 0) > 1e-9]
    type_i = _metrics(null_runs).get("type_i_error")
    power = _metrics(pos_runs).get("power")
    mean_rank_null = _mean([r.get("placebo_rank") for r in null_runs])

    decision: ProductionDefectDecision = "method_unsuitable_for_causal_interval"
    rationale = [
        "Placebo-in-space produces a null-reference envelope and randomization p-value; "
        "it is not a causal sampling distribution for ATT intervals on TBRRidge.",
        "Production requires exactly one treated unit and >=5 controls; multi-treated geometry is unsupported by design.",
    ]
    if type_i is not None and type_i > 0.25:
        rationale.append(f"Elevated null rejection rate ({type_i:.2f}) under clean null worlds.")
    if power is not None and power < 0.2:
        rationale.append(f"Low falsification power ({power:.2f}) on positive worlds.")
    if mean_rank_null is not None and (mean_rank_null < 0.2 or mean_rank_null > 0.8):
        rationale.append(f"Placebo rank on null not near uniform (mean rank extremeness {mean_rank_null:.2f}).")

    return {
        "decision": decision,
        "type_i_null": type_i,
        "power_positive": power,
        "mean_placebo_rank_null": mean_rank_null,
        "rationale": rationale,
        "recommended_correction_artifact": None,
    }


def _decide_verdict(prod: dict[str, Any], ok_runs: list[dict[str, Any]]) -> SemanticVerdict:
    if prod.get("decision") == "production_defect_confirmed":
        return "tbrridge_placebo_production_defect_confirmed"
    multi_fail = any(
        r.get("geometry_id") == "multiple_treated_units" and r.get("failure_status") == "fail"
        for r in ok_runs
    )
    single_ok = any(r.get("geometry_id") == "single_treated_unit" and r.get("failure_status") == "ok" for r in ok_runs)
    if multi_fail and single_ok:
        return "tbrridge_placebo_single_treated_restricted"
    if prod.get("decision") == "method_unsuitable_for_causal_interval":
        return "tbrridge_placebo_null_monitor_only"
    return "tbrridge_placebo_remediation_inconclusive"


def build_d5_trust_tbrridge_placebo_001(cfg: PlaceboTrustConfig | None = None) -> dict[str, Any]:
    cfg = cfg or PlaceboTrustConfig()
    t0 = time.perf_counter()
    n_rep = cfg.n_replicates_fast if cfg.fast else cfg.n_replicates
    worlds = DIAGNOSTIC_WORLDS if not cfg.fast else DIAGNOSTIC_WORLDS[:10]
    geoms = GEOMETRY_VARIANTS if not cfg.fast else GEOMETRY_VARIANTS[:2]
    effect_sizes = cfg.effect_sizes if not cfg.fast else (0.0, 0.08, -0.05)

    all_runs: list[dict[str, Any]] = []
    seed_cursor = cfg.random_state_base

    for spec in worlds:
        for geom in geoms:
            for rep in range(n_rep):
                seed = seed_cursor
                seed_cursor += 1
                all_runs.append(_run_one(spec, geom, cfg, replicate_id=rep, seed=seed))

    for spec in worlds:
        if spec.world_id not in _EFFECT_SWEEP_WORLDS:
            continue
        geom = geoms[0]
        for eff in effect_sizes:
            if abs(eff - spec.percent_effect) < 1e-12:
                continue
            for rep in range(max(1, n_rep // 2)):
                seed = seed_cursor
                seed_cursor += 1
                run = _run_one(spec, geom, cfg, replicate_id=rep, seed=seed, percent_effect=eff)
                run["effect_sweep"] = True
                all_runs.append(run)

    ok_runs = [r for r in all_runs if r.get("failure_status") == "ok"]
    prod = _production_defect_assessment(ok_runs)
    verdict = _decide_verdict(prod, all_runs)

    by_world = _group_metrics(ok_runs, "world_id")
    by_geom = _group_metrics(ok_runs, "geometry_id")
    by_effect: dict[str, Any] = {}
    for eff in effect_sizes:
        eff_runs = [r for r in ok_runs if r.get("effect_size") is not None and abs(r["effect_size"] - eff) < 1e-9]
        by_effect[str(eff)] = _metrics(eff_runs)

    policy_rows: list[dict[str, Any]] = []
    for pol in POLICY_COMPARISONS:
        if pol["policy_id"] == "B":
            subset = [r for r in ok_runs if r.get("prefit_rmse") is not None and r["prefit_rmse"] < 50.0]
        elif pol["policy_id"] == "C":
            subset = [r for r in ok_runs if r.get("geometry_id") == "single_treated_unit"]
        elif pol["policy_id"] == "D":
            subset = [r for r in ok_runs if (r.get("n_control") or 0) >= _MIN_CONTROLS_PRODUCTION]
        else:
            subset = ok_runs
        policy_rows.append({"policy": pol, "metrics": _metrics(subset)})

    summary: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "config": {
            "fast": cfg.fast,
            "n_replicates": n_rep,
            "alpha": cfg.alpha,
            "canonical_scale": _CANONICAL_SCALE,
            "min_controls_production": _MIN_CONTROLS_PRODUCTION,
        },
        "worlds": [w.world_id for w in worlds],
        "effect_sizes": list(effect_sizes),
        "geometry_variants": [g.geometry_id for g in geoms],
        "run_counts": {
            "total_runs": len(all_runs),
            "successful_runs": len(ok_runs),
            "failed_runs": len(all_runs) - len(ok_runs),
            "runtime_seconds": round(time.perf_counter() - t0, 2),
        },
        "point_estimate_results": {
            "mean_bias_clean_positive": _mean(
                [r["bias"] for r in ok_runs if r.get("world_id") == "clean_positive_effect" and r.get("bias") is not None]
            ),
            "sign_accuracy_positive": _rate(
                [r.get("sign_correct") for r in ok_runs if (r.get("true_effect") or 0) > 0]
            ),
        },
        "placebo_distribution_results": {
            "mean_placebo_draws": _mean([r.get("n_placebo_draws") for r in ok_runs]),
            "mean_placebo_std": _mean([r.get("placebo_standard_deviation") for r in ok_runs]),
        },
        "placebo_rank_calibration": {
            "mean_rank_null": _mean(
                [r.get("placebo_rank") for r in ok_runs if abs(r.get("true_effect") or 0) < 1e-9]
            ),
            "uniform_reference": 0.5,
        },
        "p_value_calibration": {
            "mean_p_null": _mean(
                [r.get("placebo_p_value") for r in ok_runs if abs(r.get("true_effect") or 0) < 1e-9]
            ),
            "uniform_reference": 0.5,
        },
        "type_i_by_world": {k: v.get("type_i_error") for k, v in by_world.items()},
        "power_by_effect": by_effect,
        "results_by_geometry": by_geom,
        "results_by_control_count": {
            "small": _metrics([r for r in ok_runs if (r.get("n_control") or 0) < 8]),
            "medium": _metrics([r for r in ok_runs if 8 <= (r.get("n_control") or 0) < 14]),
            "large": _metrics([r for r in ok_runs if (r.get("n_control") or 0) >= 14]),
        },
        "results_by_prefit": {
            "low_prefit_rmse": _metrics([r for r in ok_runs if (r.get("prefit_rmse") or 999) < 30]),
            "high_prefit_rmse": _metrics([r for r in ok_runs if (r.get("prefit_rmse") or 0) >= 30]),
        },
        "results_by_serial_dependence": _group_metrics(ok_runs, "exchangeability_status"),
        "failure_summary": {
            "n_fail": len(all_runs) - len(ok_runs),
            "failure_reasons": list({r.get("failure_reason") for r in all_runs if r.get("failure_status") == "fail"}),
        },
        "policy_comparisons": policy_rows,
        "production_defect_assessment": prod,
        "semantic_classification": {
            "verdict": verdict,
            "supported_roles": ["null_monitor", "falsification_diagnostic"],
            "unsupported_roles": ["restricted_causal_interval", "trust_report", "calibration_signal"],
            "readout_types": {
                "path_band": "null_monitor_interval",
                "p_value": "placebo_p_value",
                "inversion_ci": "falsification_score_not_causal_interval",
            },
        },
        "trustreport_eligibility_implications": {
            "dcm_005_placebo": "null_monitor_falsification_only_pending_dcm005",
            "reassessment_required": True,
        },
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_ready": False,
            "trust_report_authorized_count": 0,
        },
        "limitations": [
            "Characterizes DCM-005 Placebo only; DCM-005 eligibility reassessment out of scope.",
            "Placebo distribution ≠ causal sampling distribution.",
            "Single-treated-unit geometry required; multi-treated unsupported in production.",
            "Does not authorize TrustReport or modify production inference code.",
        ],
        "investigation_handoff": build_investigation_handoff(
            follow_up_issues=[_INVESTIGATION_ID],
            resolved_issues=[],
            terminal_dispositions=[],
            next_artifact="DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
        ),
        "verdict": verdict,
    }

    if cfg.write_full_results_path and not cfg.fast:
        Path(cfg.write_full_results_path).write_text(
            json.dumps(_json_safe({"summary": summary, "runs": all_runs}), indent=2) + "\n"
        )

    return _json_safe(summary)


def _atomic_write_text(path: Path, content: str, *, overwrite: bool = False) -> None:
    path = path.resolve()
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _fmt(val: Any) -> str:
    if val is None:
        return "—"
    if isinstance(val, float):
        return f"{val:.4f}"
    return str(val)


def _write_report(payload: dict[str, Any], path: Path, *, overwrite: bool = False) -> None:
    prod = payload.get("production_defect_assessment", {})
    lines = [
        "# D5 Trust TBRRidge Placebo 001 — Report",
        "",
        f"**Artifact ID:** {_ARTIFACT_ID}",
        f"**Verdict:** `{payload.get('verdict')}`",
        "",
        "> This artifact characterizes TBRRidge Placebo as a null-reference and falsification path.",
        "> It does not establish causal confidence-interval validity.",
        "> It does not authorize TrustReport.",
        "> It does not perform the DCM-005 eligibility reassessment.",
        "",
        "## 1. Executive summary",
        "",
        f"TBRRidge+Placebo characterized. Verdict: `{payload.get('verdict')}`. Assessment: `{prod.get('decision')}`.",
        "",
        "## 2. Prior DCM-005 Placebo status",
        "",
        "Prior eligibility harness: INSUFFICIENT_EVIDENCE; placebo-in-space semantics unvalidated for TBRRidge.",
        "",
        "## 3. Scope",
        "",
        f"{len(payload.get('worlds', []))} worlds; {len(payload.get('geometry_variants', []))} geometry variants.",
        "",
        "## 4. Non-goals",
        "",
        "- No DCM-005 eligibility reassessment",
        "- No TrustReport authorization",
        "- No production algorithm changes",
        "",
        "## 5. TBRRidge estimator path",
        "",
        "RidgeCV on pre-period-normalized controls.",
        "",
        "## 6. Placebo implementation",
        "",
        "Placebo-in-space: each control unit assigned treated window; reference distribution of post-window ATT.",
        "",
        "## 7. Placebo-unit construction",
        "",
        "One control unit pseudo-treated per draw; observed unit retained; RMSPE pre-fit filter optional.",
        "",
        "## 8. Geometry assumptions",
        "",
        "Exactly **one** treated unit; >=5 control units for production path.",
        "",
        "## 9. Exchangeability assumptions",
        "",
        "Donors exchangeable under placebo reassignment; serial dependence invalidates exchangeability.",
        "",
        "## 10. Estimand",
        "",
        f"Post-window mean treated-minus-counterfactual effect ({_CANONICAL_SCALE}).",
        "",
        "## 11. Scale contract",
        "",
        "Level mean shift from percent injection; placebo statistics on same scale.",
        "",
        "## 12. Worlds",
        "",
        ", ".join(payload.get("worlds", [])),
        "",
        "## 13. Effect-size sweep",
        "",
        ", ".join(str(e) for e in payload.get("effect_sizes", [])),
        "",
        "## 14. Geometry sweep",
        "",
        ", ".join(payload.get("geometry_variants", [])),
        "",
        "## 15. Run counts/runtime",
        "",
        f"Total {_fmt(payload.get('run_counts', {}).get('total_runs'))}; "
        f"ok {_fmt(payload.get('run_counts', {}).get('successful_runs'))}; "
        f"runtime {_fmt(payload.get('run_counts', {}).get('runtime_seconds'))}s.",
        "",
        "## 16. Point-estimate behavior",
        "",
        str(payload.get("point_estimate_results", {})),
        "",
        "## 17. Placebo distribution behavior",
        "",
        str(payload.get("placebo_distribution_results", {})),
        "",
        "## 18. Null-rank calibration",
        "",
        str(payload.get("placebo_rank_calibration", {})),
        "",
        "## 19. Null type-I",
        "",
        f"type_i_null: {_fmt(prod.get('type_i_null'))}; mean_p_null: {_fmt(payload.get('p_value_calibration', {}).get('mean_p_null'))}.",
        "",
        "## 20. Positive-effect power",
        "",
        f"power_positive: {_fmt(prod.get('power_positive'))}.",
        "",
        "## 21. Negative-effect power",
        "",
        str((payload.get("power_by_effect") or {}).get("-0.05", {})),
        "",
        "## 22. Serial-dependence findings",
        "",
        str(payload.get("results_by_serial_dependence", {})),
        "",
        "## 23. Pre-fit findings",
        "",
        str(payload.get("results_by_prefit", {})),
        "",
        "## 24. Donor-support findings",
        "",
        str(payload.get("results_by_control_count", {})),
        "",
        "## 25. Multiple-treated findings",
        "",
        str((payload.get("results_by_geometry") or {}).get("multiple_treated_units", "unsupported")),
        "",
        "## 26. Worst-world behavior",
        "",
        f"post_treatment_shock type_i: {_fmt((payload.get('type_i_by_world') or {}).get('post_treatment_shock'))}.",
        "",
        "## 27. Policy comparisons",
        "",
        "A current; B prefit-gated; C single-treated; D min controls; E null-monitor; F blocked.",
        "",
        "## 28. Root-cause determination",
        "",
        "Placebo envelope is null-reference / falsification; not causal ATT uncertainty.",
        "",
        "## 29. Production-defect decision",
        "",
        f"`{prod.get('decision')}` — {'; '.join(prod.get('rationale', []))}",
        "",
        "## 30. Semantic classification",
        "",
        str(payload.get("semantic_classification", {})),
        "",
        "## 31. TrustReport implications",
        "",
        "Null-monitor / falsification only; causal-interval and TrustReport blocked.",
        "",
        "## 32. Authorization status",
        "",
        "**Blocked** — trust_report_authorized=false.",
        "",
        "## 33. Investigation lifecycle update",
        "",
        f"{_INVESTIGATION_ID} remains OPEN with provisional NULL_MONITOR_ONLY recommendation for DCM-005.",
        "",
        "## 34. Remaining limitations",
        "",
        "; ".join(payload.get("limitations", [])),
        "",
        "## 35. Governance verdict",
        "",
        f"**`{payload.get('verdict')}`**",
        "",
    ]
    handoff = payload.get("investigation_handoff") or {}
    lines.extend(
        format_handoff_report_section(
            resolved_in_artifact=[],
            new_investigations=[],
            updated_investigations=[
                f"{_INVESTIGATION_ID} → OPEN; provisional NULL_MONITOR_ONLY recommendation pending DCM-005"
            ],
            deferred_issues=[],
            explicit_exclusions=["DCM-005 eligibility reassessment"],
            revisit_trigger="Before DCM-005 TrustReport eligibility reassessment",
            decision_checkpoint="DCM-005 eligibility reassessment",
            next_artifact=handoff.get("next_artifact"),
        )
    )
    _atomic_write_text(path, "\n".join(lines) + "\n", overwrite=overwrite)


def write_summary(
    path: Path | None = None,
    *,
    cfg: PlaceboTrustConfig | None = None,
    overwrite: bool = False,
    report_path: Path | None = None,
) -> Path:
    payload = build_d5_trust_tbrridge_placebo_001(cfg)
    if path is None:
        path = _DEFAULT_SUMMARY
    _atomic_write_text(path, json.dumps(payload, indent=2) + "\n", overwrite=overwrite)
    _write_report(payload, report_path or _DEFAULT_REPORT, overwrite=overwrite)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--output-local", default="/tmp/D5_TRUST_TBRRIDGE_PLACEBO_001_results.json")
    parser.add_argument("--summary-output", default=str(_DEFAULT_SUMMARY))
    parser.add_argument("--report-output", default=str(_DEFAULT_REPORT))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--fast", action="store_true")
    args = parser.parse_args(argv)

    cfg = PlaceboTrustConfig(
        fast=args.fast,
        write_full_results_path=args.output_local if not args.fast else None,
    )
    write_summary(
        Path(args.summary_output),
        cfg=cfg,
        overwrite=args.overwrite,
        report_path=Path(args.report_output),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
