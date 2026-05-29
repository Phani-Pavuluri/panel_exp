#!/usr/bin/env python3
"""
Phase 15 INV-029 — Placebo operating-characteristic characterization (investigation-only).

Does not modify placebo implementation, eligibility, thresholds, recovery scoring, or maturity.
Outputs: .phase15_placebo_characterization.json (local)
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from panel_exp.methods.scm import SyntheticControl  # noqa: E402
from panel_exp.methods.tbr import TBR, TBRRidge  # noqa: E402
from panel_exp.validation.recovery_metrics import (  # noqa: E402
    SimulationRecord,
    aggregate_recovery_metrics,
)
from panel_exp.validation.recovery_intervals import extract_recovery_interval  # noqa: E402
from panel_exp.validation.recovery_runner import RecoveryEstimatorConfig  # noqa: E402
from panel_exp.validation.runner import _path_relative_att  # noqa: E402
from panel_exp.validation.synthetic_scenarios import (  # noqa: E402
    get_recovery_scenario,
)
from panel_exp.validation.synthetic_world import SyntheticScenario, SyntheticWorld  # noqa: E402

CHAR_N = 30
PROD_N = 100
SEEDS = (0, 1, 2)
ALPHA = 0.05


def _git_commit() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_ROOT,
                text=True,
            )
            .strip()
        )
    except Exception:
        return "unknown"


def _treated_units(n_treated: int, n_geos: int) -> Tuple[str, ...]:
    return tuple(f"geo_{i}" for i in range(min(n_treated, n_geos - 1)))


def _donor_tier_n_geos(tier: str, n_treated: int = 1) -> int:
    if tier == "small":
        return n_treated + 5
    if tier == "medium":
        return 20
    if tier == "large":
        return 40
    raise ValueError(tier)


def _build_scenario(
    base_name: str,
    *,
    n_geos: Optional[int] = None,
    n_treated: Optional[int] = None,
    heterogeneous: bool = False,
    use_default_treated: bool = False,
) -> SyntheticScenario:
    sc = get_recovery_scenario(base_name)
    overrides: Dict[str, Any] = {}
    if n_geos is not None:
        overrides["n_geos"] = n_geos
    if heterogeneous:
        overrides["heterogeneous_effects"] = True
    if use_default_treated:
        overrides["treated_units"] = ()
    elif n_treated is not None and n_geos is not None:
        overrides["treated_units"] = _treated_units(n_treated, n_geos)
    return replace(sc, **overrides)


def _placebo_configs() -> Dict[str, RecoveryEstimatorConfig]:
    def _cfg(name: str, est_cls: type) -> RecoveryEstimatorConfig:
        return RecoveryEstimatorConfig(
            config_name=name,
            estimator_name=est_cls.__name__,
            factory=lambda c=est_cls: c(inference="Placebo", alpha=ALPHA),
            inference="Placebo",
            run_kwargs={},
            supports_significance=True,
            intervals_expected=True,
            significance_from_ci=True,
        )

    return {
        "SCM_Placebo": _cfg("SCM_Placebo", SyntheticControl),
        "TBRRidge_Placebo": _cfg("TBRRidge_Placebo", TBRRidge),
        "TBR_Placebo": _cfg("TBR_Placebo", TBR),
    }


def _run_placebo_simulation(
    config: RecoveryEstimatorConfig,
    world: SyntheticWorld,
) -> Tuple[SimulationRecord, Dict[str, Any]]:
    """Run one draw; capture placebo semantics metadata when run completes."""
    meta: Dict[str, Any] = {
        "path_interval_type": None,
        "effect_interval_type": None,
        "interval_type": None,
        "placebo_unsupported": None,
        "ci_via_inversion": None,
        "effect_ci_lower_inversion": None,
        "effect_ci_upper_inversion": None,
        "placebo_p_value": None,
    }
    truth = float(world.truth["true_effect"])
    try:
        estimator = config.factory()
        panel = world.to_panel_dataset()
        n_control = len(panel.control_units)
        meta["n_control_units"] = n_control
        meta["n_treated_units"] = len(panel.treated_units)
        estimator.run_analysis(panel, **config.run_kwargs)
    except Exception as exc:
        exc_type = type(exc).__name__
        return (
            SimulationRecord(
                predicted_effect=float("nan"),
                true_effect=truth,
                failed=True,
                failure_type=exc_type,
                failure_message=str(exc),
                intervals_available=False,
                intervals_unavailable_reason=f"run_failed:{exc_type}",
                point_estimand="relative_att_post",
            ),
            meta,
        )

    ir = getattr(estimator, "inference_result", None)
    if ir is not None:
        meta["path_interval_type"] = getattr(
            getattr(ir, "path_interval_type", None),
            "value",
            ir.path_interval_type if hasattr(ir, "path_interval_type") else None,
        )
        eit = getattr(ir, "effect_interval_type", None)
        meta["effect_interval_type"] = getattr(eit, "value", eit)
        it = getattr(ir, "interval_type", None)
        meta["interval_type"] = getattr(it, "value", it)
        assumptions = getattr(ir, "assumptions", None) or {}
        meta["ci_via_inversion"] = assumptions.get("ci_via_inversion")
    results = estimator.results or {}
    meta["placebo_unsupported"] = results.get("placebo_unsupported")
    meta["interval_type_results"] = results.get("interval_type")
    stats = results.get("placebo_stats") or {}
    if stats.get("p_value") is not None and np.isfinite(stats.get("p_value")):
        meta["placebo_p_value"] = float(stats["p_value"])
    if results.get("effect_ci_lower_inversion") is not None:
        meta["effect_ci_lower_inversion"] = float(results["effect_ci_lower_inversion"])
    if results.get("effect_ci_upper_inversion") is not None:
        meta["effect_ci_upper_inversion"] = float(results["effect_ci_upper_inversion"])

    predicted = _path_relative_att(estimator, panel)
    interval = extract_recovery_interval(
        estimator,
        panel,
        alpha=ALPHA,
        significance_from_ci=config.significance_from_ci,
        supports_significance=config.supports_significance,
    )
    intervals_available = (
        interval.interval_aligned
        and interval.ci_lower is not None
        and interval.ci_upper is not None
        and np.isfinite(interval.ci_lower)
        and np.isfinite(interval.ci_upper)
    )
    significant = interval.significant if interval.significance_aligned else None
    failed = not np.isfinite(predicted)
    interval_reason = interval.unavailable_reason
    if config.intervals_expected and not intervals_available and interval_reason is None:
        interval_reason = "interval_estimand_mismatch"

    record = SimulationRecord(
        predicted_effect=predicted,
        true_effect=truth,
        ci_lower=interval.ci_lower if interval.interval_aligned else None,
        ci_upper=interval.ci_upper if interval.interval_aligned else None,
        significant=significant,
        failed=failed,
        failure_type="non_finite_estimate" if failed else None,
        failure_message="non-finite predicted_effect" if failed else None,
        intervals_available=intervals_available if config.intervals_expected else None,
        intervals_unavailable_reason=interval_reason
        if config.intervals_expected and not intervals_available
        else None,
        point_estimand=interval.point_estimand,
        interval_estimand=interval.interval_estimand,
        interval_scale=interval.interval_scale,
        interval_aligned=interval.interval_aligned,
        significance_estimand=interval.significance_estimand,
        significance_aligned=interval.significance_aligned,
    )
    return record, meta


def _extended_stats(
    records: Sequence[SimulationRecord],
    metas: Sequence[Dict[str, Any]],
    *,
    intervals_expected: bool,
) -> Dict[str, Any]:
    n = len(records)
    if n == 0:
        return {}
    failed = sum(1 for r in records if r.failed)
    aligned = sum(1 for r in records if r.interval_aligned)
    widths: List[float] = []
    sig_true = 0
    sig_n = 0
    path_placebo = 0
    inv_ci = 0
    p_values: List[float] = []
    interval_estimands: Dict[str, int] = {}
    failure_messages: Dict[str, int] = {}
    for r, m in zip(records, metas):
        if r.failed:
            key = (r.failure_type or "unknown")[:40]
            failure_messages[key] = failure_messages.get(key, 0) + 1
            continue
        est = r.interval_estimand or "missing"
        interval_estimands[est] = interval_estimands.get(est, 0) + 1
        if m.get("path_interval_type") == "placebo_band":
            path_placebo += 1
        if m.get("ci_via_inversion"):
            inv_ci += 1
        if m.get("placebo_p_value") is not None:
            p_values.append(float(m["placebo_p_value"]))
        if (
            r.ci_lower is not None
            and r.ci_upper is not None
            and np.isfinite(r.ci_lower)
            and np.isfinite(r.ci_upper)
        ):
            widths.append(float(r.ci_upper - r.ci_lower))
        if r.significant is not None and r.significance_aligned:
            sig_n += 1
            if r.significant:
                sig_true += 1
    successful = n - failed
    out: Dict[str, Any] = {
        "failure_rate": failed / n,
        "interval_aligned_rate": aligned / n if intervals_expected else None,
        "mean_interval_width": float(np.mean(widths)) if widths else None,
        "significance_rate": (sig_true / sig_n) if sig_n else None,
        "placebo_band_rate": (path_placebo / successful) if successful else None,
        "inversion_ci_rate": (inv_ci / successful) if successful else None,
        "mean_placebo_p_value": float(np.mean(p_values)) if p_values else None,
        "interval_estimand_counts": interval_estimands,
        "failure_type_counts": failure_messages,
    }
    if widths and records:
        truths = [
            abs(r.true_effect)
            for r in records
            if not r.failed and abs(r.true_effect) > 1e-9
        ]
        if truths:
            out["mean_width_over_effect"] = float(np.mean(widths)) / float(
                np.mean(truths)
            )
    return out


def _aggregate_seed_payloads(payloads: List[Dict[str, Any]]) -> Dict[str, Any]:
    def _col(key: str) -> List[float]:
        vals = []
        for p in payloads:
            v = p.get(key)
            if v is not None and np.isfinite(v):
                vals.append(float(v))
        return vals

    summary: Dict[str, Any] = {}
    for key in (
        "bias",
        "absolute_bias",
        "recovery_success_rate",
        "failure_rate",
        "coverage",
        "false_positive_rate",
        "power",
        "mean_interval_width",
        "significance_rate",
        "interval_aligned_rate",
        "mean_width_over_effect",
        "placebo_band_rate",
        "inversion_ci_rate",
        "mean_placebo_p_value",
    ):
        vals = _col(key)
        if vals:
            summary[key] = {
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals)),
                "min": float(np.min(vals)),
                "max": float(np.max(vals)),
                "n": len(vals),
            }
    summary["failure_types"] = {}
    for p in payloads:
        for k, v in (p.get("failure_types") or {}).items():
            summary["failure_types"][k] = summary["failure_types"].get(k, 0) + int(v)
    return summary


def run_cell(
    config: RecoveryEstimatorConfig,
    scenario: SyntheticScenario,
    *,
    n_simulations: int,
    seeds: Sequence[int],
    tier: str,
) -> Dict[str, Any]:
    seed_payloads: List[Dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in seeds:
        records: List[SimulationRecord] = []
        metas: List[Dict[str, Any]] = []
        for i in range(n_simulations):
            sim_seed = seed * 10_000 + i
            sc = replace(scenario, random_state=sim_seed)
            world = SyntheticWorld.generate(sc)
            rec, meta = _run_placebo_simulation(config, world)
            records.append(rec)
            metas.append(meta)
        agg = aggregate_recovery_metrics(
            estimator=config.config_name,
            scenario=scenario.name,
            records=records,
            intervals_expected=config.intervals_expected,
        )
        payload = agg.to_dict()
        payload.update(
            _extended_stats(
                records,
                metas,
                intervals_expected=config.intervals_expected,
            )
        )
        payload["seed"] = seed
        payload["n_simulations"] = n_simulations
        if records:
            payload["example_failure"] = next(
                (
                    {
                        "failure_type": r.failure_type,
                        "failure_message": (r.failure_message or "")[:200],
                    }
                    for r in records
                    if r.failure_type
                ),
                None,
            )
            ok_meta = next((m for r, m in zip(records, metas) if not r.failed), {})
            payload["example_success_semantics"] = {
                k: ok_meta.get(k)
                for k in (
                    "path_interval_type",
                    "interval_type",
                    "ci_via_inversion",
                    "placebo_p_value",
                )
            }
        seed_payloads.append(payload)
    elapsed = time.perf_counter() - t0
    return {
        "config": config.config_name,
        "scenario_name": scenario.name,
        "tier": tier,
        "n_simulations": n_simulations,
        "seeds": list(seeds),
        "scenario": {
            "n_geos": scenario.n_geos,
            "n_periods": scenario.n_periods,
            "treatment_start": scenario.treatment_start,
            "true_effect": scenario.true_effect,
            "heterogeneous_effects": scenario.heterogeneous_effects,
            "n_treated_explicit": len(scenario.treated_units),
        },
        "wall_seconds": elapsed,
        "per_seed": seed_payloads,
        "summary": _aggregate_seed_payloads(seed_payloads),
    }


def main() -> None:
    configs = _placebo_configs()
    cells: Dict[str, Any] = {}
    primary = configs["SCM_Placebo"]

    # --- Production-tier: single-treated (aligned path) ---
    for sc_name, cell_id in (
        ("recovery_null_effect", "prod_null_single_treated"),
        ("recovery_positive_effect", "prod_positive_single_treated"),
    ):
        sc = _build_scenario(sc_name, n_geos=20, n_treated=1)
        cells[cell_id] = run_cell(
            primary,
            sc,
            n_simulations=PROD_N,
            seeds=SEEDS,
            tier="production_characterization",
        )

    # --- Default multi-treated (documents failure surface) ---
    for sc_name, cell_id in (
        ("recovery_null_effect", "default_multi_null"),
        ("recovery_positive_effect", "default_multi_positive"),
    ):
        sc = _build_scenario(sc_name, use_default_treated=True)
        cells[cell_id] = run_cell(
            primary,
            sc,
            n_simulations=CHAR_N,
            seeds=SEEDS,
            tier="characterization",
        )

    # --- Geometry matrix (SCM) ---
    for n_tr in (1, 2, 4):
        for effect_label, base in (
            ("null", "recovery_null_effect"),
            ("positive", "recovery_positive_effect"),
        ):
            sc = _build_scenario(base, n_geos=20, n_treated=n_tr)
            cells[f"geom_n{n_tr}_{effect_label}"] = run_cell(
                primary,
                sc,
                n_simulations=CHAR_N,
                seeds=SEEDS,
                tier="characterization",
            )

    # --- Donor tier (single-treated; n_control varies) ---
    for tier_name in ("small", "medium", "large"):
        n_geos = _donor_tier_n_geos(tier_name, 1)
        for effect_label, base in (
            ("null", "recovery_null_effect"),
            ("positive", "recovery_positive_effect"),
        ):
            sc = _build_scenario(base, n_geos=n_geos, n_treated=1)
            cells[f"donor_{tier_name}_{effect_label}"] = run_cell(
                primary,
                sc,
                n_simulations=CHAR_N,
                seeds=SEEDS,
                tier="characterization",
            )

    # --- Donor tier insufficient controls (small panel, multi-treated) ---
    sc_small = _build_scenario(
        "recovery_null_effect",
        n_geos=_donor_tier_n_geos("small", 4),
        n_treated=4,
    )
    cells["donor_small_n4_null"] = run_cell(
        primary,
        sc_small,
        n_simulations=CHAR_N,
        seeds=SEEDS,
        tier="characterization",
    )

    # --- Heterogeneous (single-treated positive) ---
    sc_het = _build_scenario(
        "recovery_positive_effect",
        n_geos=20,
        n_treated=1,
        heterogeneous=True,
    )
    cells["het_single_positive"] = run_cell(
        primary,
        sc_het,
        n_simulations=CHAR_N,
        seeds=SEEDS,
        tier="characterization",
    )

    # --- Track D: TBRRidge + TBR (single-treated) ---
    for cfg_name, key in (
        ("TBRRidge_Placebo", "tbrridge"),
        ("TBR_Placebo", "tbr"),
    ):
        for sc_name, cell_suffix in (
            ("recovery_null_effect", "null"),
            ("recovery_positive_effect", "positive"),
        ):
            sc = _build_scenario(sc_name, n_geos=20, n_treated=1)
            cells[f"{key}_single_{cell_suffix}"] = run_cell(
                configs[cfg_name],
                sc,
                n_simulations=CHAR_N,
                seeds=SEEDS,
                tier="characterization",
            )

    out = {
        "investigation_id": "INV-029",
        "phase": 15,
        "package_version": "0.2.1",
        "commit": _git_commit(),
        "characterization_tier_n": CHAR_N,
        "production_tier_n": PROD_N,
        "primary_config": "SCM_Placebo",
        "eligible_for_nominal_calibration": False,
        "nominal_calibration_eligible_unchanged": ["SCM_UnitJackKnife"],
        "cells": cells,
    }
    out_path = REPO_ROOT / ".phase15_placebo_characterization.json"
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out_path} ({len(cells)} cells)")


if __name__ == "__main__":
    main()
