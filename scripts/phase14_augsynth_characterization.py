#!/usr/bin/env python3
"""
Phase 14 INV-028 — AugSynth operating-characteristic characterization (investigation-only).

Does not modify eligibility, estimators, inference, or recovery scoring.
Outputs: .phase14_augsynth_characterization.json (local)
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from panel_exp.methods.scm import AugSynth, AugSynthCVXPY, SyntheticControl  # noqa: E402
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason  # noqa: E402
from panel_exp.validation.recovery_metrics import (  # noqa: E402
    SimulationRecord,
    aggregate_recovery_metrics,
)
from panel_exp.validation.recovery_runner import (  # noqa: E402
    RecoveryEstimatorConfig,
    _run_simulation,
)
from panel_exp.validation.synthetic_scenarios import (  # noqa: E402
    get_recovery_scenario,
)
from panel_exp.validation.synthetic_world import SyntheticScenario, SyntheticWorld  # noqa: E402

CHAR_N = 30
PROD_N = 100
SEEDS_CHAR = (0, 1, 2)
SEEDS_PROD = (0, 1, 2)
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


def _configs() -> Dict[str, RecoveryEstimatorConfig]:
    return {
        "AugSynthCVXPY_Point": RecoveryEstimatorConfig(
            config_name="AugSynthCVXPY_Point",
            estimator_name="AugSynthCVXPY",
            factory=lambda: AugSynthCVXPY(inference=None, alpha=0.05),
            inference=None,
            run_kwargs={},
            supports_significance=False,
            intervals_expected=False,
            significance_from_ci=False,
        ),
        "AugSynthCVXPY_UnitJackKnife": RecoveryEstimatorConfig(
            config_name="AugSynthCVXPY_UnitJackKnife",
            estimator_name="AugSynthCVXPY",
            factory=lambda: AugSynthCVXPY(inference="UnitJackKnife", alpha=0.05),
            inference="UnitJackKnife",
            run_kwargs={},
            supports_significance=True,
            intervals_expected=True,
            significance_from_ci=True,
        ),
        "SCM_Point": RecoveryEstimatorConfig(
            config_name="SCM_Point",
            estimator_name="SCM",
            factory=lambda: SyntheticControl(inference=None, alpha=0.05),
            inference=None,
            run_kwargs={},
            supports_significance=False,
            intervals_expected=False,
            significance_from_ci=False,
        ),
        "AugSynth_Point": RecoveryEstimatorConfig(
            config_name="AugSynth_Point",
            estimator_name="AugSynth",
            factory=lambda: AugSynth(inference=None, alpha=0.05),
            inference=None,
            run_kwargs={},
            supports_significance=False,
            intervals_expected=False,
            significance_from_ci=False,
        ),
    }


def _treated_units(n_treated: int, n_geos: int) -> Tuple[str, ...]:
    return tuple(f"geo_{i}" for i in range(min(n_treated, n_geos - 1)))


def _donor_tier_n_geos(tier: str, n_treated: int = 4) -> int:
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
    true_effect: Optional[float] = None,
    n_geos: Optional[int] = None,
    n_treated: Optional[int] = None,
    heterogeneous: bool = False,
    use_default_treated: bool = False,
) -> SyntheticScenario:
    sc = get_recovery_scenario(base_name)
    overrides: Dict[str, Any] = {}
    if true_effect is not None:
        overrides["true_effect"] = true_effect
    if n_geos is not None:
        overrides["n_geos"] = n_geos
    if heterogeneous:
        overrides["heterogeneous_effects"] = True
    if use_default_treated:
        overrides["treated_units"] = ()
    elif n_treated is not None and n_geos is not None:
        overrides["treated_units"] = _treated_units(n_treated, n_geos)
    return replace(sc, **overrides)


def _extended_stats(
    records: Sequence[SimulationRecord],
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
    for r in records:
        if r.failed:
            continue
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
    out: Dict[str, Any] = {
        "failure_rate": failed / n,
        "interval_aligned_rate": aligned / n if intervals_expected else None,
        "mean_interval_width": float(np.mean(widths)) if widths else None,
        "significance_rate": (sig_true / sig_n) if sig_n else None,
    }
    if widths and records:
        truths = [abs(r.true_effect) for r in records if not r.failed and abs(r.true_effect) > 1e-9]
        if truths:
            out["mean_width_over_effect"] = float(np.mean(widths)) / float(np.mean(truths))
    return out


def _aggregate_seed_payloads(
    payloads: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Mean/std/min/max across seed-level aggregates."""

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
    config_name: str,
    scenario: SyntheticScenario,
    *,
    n_simulations: int,
    seeds: Sequence[int],
    tier: str = "characterization",
) -> Dict[str, Any]:
    configs = _configs()
    config = configs[config_name]
    seed_payloads: List[Dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in seeds:
        records: List[SimulationRecord] = []
        for i in range(n_simulations):
            sim_seed = seed * 10_000 + i
            sc = replace(scenario, random_state=sim_seed)
            world = SyntheticWorld.generate(sc)
            records.append(_run_simulation(config, world, alpha=ALPHA))
        agg = aggregate_recovery_metrics(
            estimator=config.config_name,
            scenario=scenario.name,
            records=records,
            intervals_expected=config.intervals_expected,
        )
        payload = agg.to_dict()
        payload.update(
            _extended_stats(records, intervals_expected=config.intervals_expected)
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
        seed_payloads.append(payload)
    elapsed = time.perf_counter() - t0
    return {
        "config": config_name,
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
            "spillover_strength": scenario.spillover_strength,
            "cross_geo_correlation": scenario.cross_geo_correlation,
            "n_treated_explicit": len(scenario.treated_units),
            "treated_units": list(scenario.treated_units),
        },
        "wall_seconds": elapsed,
        "per_seed": seed_payloads,
        "summary": _aggregate_seed_payloads(seed_payloads),
    }


def main() -> None:
    skip = cvxpy_osqp_skip_reason()
    if skip:
        print(f"ABORT: {skip}", file=sys.stderr)
        sys.exit(1)

    cells: Dict[str, Any] = {}
    primary_config = "AugSynthCVXPY_Point"

    # --- Production-tier primary (null + positive, default DGP) ---
    for sc_name, cell_id in (
        ("recovery_null_effect", "prod_null_default"),
        ("recovery_positive_effect", "prod_positive_default"),
    ):
        sc = _build_scenario(sc_name, use_default_treated=True)
        cells[cell_id] = run_cell(
            primary_config,
            sc,
            n_simulations=PROD_N,
            seeds=SEEDS_PROD,
            tier="production_characterization",
        )

    # --- Inference OC (default DGP) ---
    for sc_name, cell_id in (
        ("recovery_null_effect", "infjk_null_default"),
        ("recovery_positive_effect", "infjk_positive_default"),
    ):
        sc = _build_scenario(sc_name, use_default_treated=True)
        cells[cell_id] = run_cell(
            "AugSynthCVXPY_UnitJackKnife",
            sc,
            n_simulations=CHAR_N,
            seeds=SEEDS_CHAR,
            tier="characterization",
        )

    # --- Geometry: treated count (medium panel n=20) ---
    for n_tr in (1, 2, 4):
        for effect_name, te in (("null", 0.0), ("positive", 0.10)):
            sc = _build_scenario(
                "recovery_null_effect" if te == 0.0 else "recovery_positive_effect",
                n_geos=20,
                n_treated=n_tr,
            )
            cells[f"geom_n{n_tr}_{effect_name}"] = run_cell(
                primary_config,
                sc,
                n_simulations=CHAR_N,
                seeds=SEEDS_CHAR,
            )

    # Default sampled treated (~4)
    for effect_name, base in (
        ("null", "recovery_null_effect"),
        ("positive", "recovery_positive_effect"),
    ):
        sc = _build_scenario(base, n_geos=20, use_default_treated=True)
        cells[f"geom_default_{effect_name}"] = run_cell(
            primary_config,
            sc,
            n_simulations=CHAR_N,
            seeds=SEEDS_CHAR,
        )

    # --- Donor tier (n_treated=4 explicit) ---
    for tier in ("small", "medium", "large"):
        n_geos = _donor_tier_n_geos(tier, 4)
        for effect_name, base in (
            ("null", "recovery_null_effect"),
            ("positive", "recovery_positive_effect"),
        ):
            sc = _build_scenario(base, n_geos=n_geos, n_treated=4)
            cells[f"donor_{tier}_{effect_name}"] = run_cell(
                primary_config,
                sc,
                n_simulations=CHAR_N,
                seeds=SEEDS_CHAR,
            )

    # --- Heterogeneity ---
    sc_hom = _build_scenario("recovery_positive_effect", n_geos=20, use_default_treated=True)
    cells["het_hom_default"] = run_cell(
        primary_config, sc_hom, n_simulations=CHAR_N, seeds=SEEDS_CHAR
    )
    sc_het = _build_scenario(
        "recovery_positive_effect",
        n_geos=20,
        use_default_treated=True,
        heterogeneous=True,
    )
    cells["het_multi_default"] = run_cell(
        primary_config, sc_het, n_simulations=CHAR_N, seeds=SEEDS_CHAR
    )

    # --- Stress scenarios ---
    for stress in ("scm_high_collinearity", "scm_donor_contamination"):
        sc = get_recovery_scenario(stress)
        cells[f"stress_{stress}"] = run_cell(
            primary_config,
            sc,
            n_simulations=CHAR_N,
            seeds=SEEDS_CHAR,
        )

    # --- SCM point diagnostic (default positive only) ---
    sc_pos = _build_scenario("recovery_positive_effect", use_default_treated=True)
    cells["diag_scm_point_positive"] = run_cell(
        "SCM_Point",
        sc_pos,
        n_simulations=CHAR_N,
        seeds=SEEDS_CHAR,
    )

    # --- Non-CVXPY AugSynth (single cell) ---
    try:
        cells["augsynth_non_cvxpy_positive"] = run_cell(
            "AugSynth_Point",
            sc_pos,
            n_simulations=min(10, CHAR_N),
            seeds=(0,),
            tier="characterization_probe",
        )
    except Exception as exc:
        cells["augsynth_non_cvxpy_positive"] = {
            "error": str(exc),
            "tier": "characterization_probe",
        }

    out = {
        "investigation_id": "INV-028",
        "phase": 14,
        "package_version": "0.2.1",
        "commit": _git_commit(),
        "characterization_tier_n": CHAR_N,
        "production_tier_n": PROD_N,
        "primary_config": primary_config,
        "eligible_for_nominal_calibration": False,
        "nominal_calibration_eligible_unchanged": ["SCM_UnitJackKnife"],
        "cells": cells,
    }
    out_path = REPO_ROOT / ".phase14_augsynth_characterization.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} ({len(cells)} cells)")


if __name__ == "__main__":
    main()
