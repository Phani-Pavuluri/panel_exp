#!/usr/bin/env python3
"""
Phase 12 INV-007 — post-fix TBRRidge KFold validation (investigation-only).

Corrective geometry fix validation; does not modify eligibility, estimators beyond
KFold geometry, recovery scoring, thresholds, or maturity labels.
Outputs: .phase12_inv007_kfold_fix_validation.json (local)
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

from panel_exp.validation.recovery_metrics import (  # noqa: E402
    SimulationRecord,
    aggregate_recovery_metrics,
)
from panel_exp.validation.recovery_runner import (  # noqa: E402
    RecoveryEstimatorConfig,
    _run_simulation,
    all_recovery_configs,
)
from panel_exp.validation.synthetic_scenarios import get_recovery_scenario  # noqa: E402
from panel_exp.validation.synthetic_world import SyntheticScenario, SyntheticWorld  # noqa: E402

CHAR_N = 30
PROD_N = 100
SEEDS = (0, 1, 2)
ALPHA = 0.05
CONFIG_NAME = "TBRRidge_Kfold"


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


def _build_scenario(
    base_name: str,
    *,
    n_treated: Optional[int] = None,
    use_default_treated: bool = False,
) -> SyntheticScenario:
    sc = get_recovery_scenario(base_name)
    if use_default_treated:
        return sc
    if n_treated is not None:
        return replace(sc, treated_units=_treated_units(n_treated, sc.n_geos))
    return sc


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
    ordered = 0
    ordered_n = 0
    widths: List[float] = []
    sig_true = 0
    sig_n = 0
    point_estimands: Dict[str, int] = {}
    interval_estimands: Dict[str, int] = {}
    interval_scales: Dict[str, int] = {}
    for r in records:
        if r.failed:
            continue
        point_estimands[r.point_estimand or "missing"] = (
            point_estimands.get(r.point_estimand or "missing", 0) + 1
        )
        if r.interval_estimand:
            interval_estimands[r.interval_estimand] = (
                interval_estimands.get(r.interval_estimand, 0) + 1
            )
        if r.interval_scale:
            interval_scales[r.interval_scale] = (
                interval_scales.get(r.interval_scale, 0) + 1
            )
        if (
            r.ci_lower is not None
            and r.ci_upper is not None
            and np.isfinite(r.ci_lower)
            and np.isfinite(r.ci_upper)
        ):
            widths.append(float(r.ci_upper - r.ci_lower))
            if r.interval_aligned:
                ordered_n += 1
                if r.ci_lower <= r.ci_upper:
                    ordered += 1
        if r.significant is not None and r.significance_aligned:
            sig_n += 1
            if r.significant:
                sig_true += 1
    return {
        "failure_rate": failed / n,
        "interval_aligned_rate": aligned / n if intervals_expected else None,
        "bound_order_rate_when_aligned": (ordered / ordered_n) if ordered_n else None,
        "mean_interval_width": float(np.mean(widths)) if widths else None,
        "significance_rate": (sig_true / sig_n) if sig_n else None,
        "point_estimand_counts": point_estimands,
        "interval_estimand_counts": interval_estimands,
        "interval_scale_counts": interval_scales,
    }


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
        "bound_order_rate_when_aligned",
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
            "n_treated_explicit": len(scenario.treated_units),
            "treated_units": list(scenario.treated_units),
        },
        "wall_seconds": elapsed,
        "per_seed": seed_payloads,
        "summary": _aggregate_seed_payloads(seed_payloads),
    }


def main() -> None:
    config = all_recovery_configs()[CONFIG_NAME]
    cells: Dict[str, Any] = {}

    scenario_bases = ("recovery_null_effect", "recovery_positive_effect")
    treated_specs: List[Tuple[str, Optional[int], bool]] = [
        ("n1", 1, False),
        ("n2", 2, False),
        ("n4", 4, False),
        ("default", None, True),
    ]

    probe = run_cell(
        config,
        _build_scenario("recovery_null_effect", n_treated=2),
        n_simulations=5,
        seeds=(0,),
        tier="probe",
    )
    per_sim = probe["wall_seconds"] / 5
    est_total = per_sim * PROD_N * len(SEEDS) * len(scenario_bases) * len(treated_specs)
    n_simulations = PROD_N if est_total <= 900 else CHAR_N
    tier = (
        "production_characterization"
        if n_simulations == PROD_N
        else "characterization_not_nominal_calibration"
    )
    print(
        f"Using n_simulations={n_simulations} ({tier}); "
        f"estimated wall ~{est_total:.0f}s at n={PROD_N}"
    )

    for base in scenario_bases:
        for label, n_treated, use_default in treated_specs:
            sc = _build_scenario(
                base,
                n_treated=n_treated,
                use_default_treated=use_default,
            )
            cell_id = f"{base}__{label}"
            cells[cell_id] = run_cell(
                config,
                sc,
                n_simulations=n_simulations,
                seeds=SEEDS,
                tier=tier,
            )
            s = cells[cell_id]["summary"]
            fr = (s.get("failure_rate") or {}).get("mean")
            print(f"{cell_id}: failure_rate mean={fr}")

    out = {
        "investigation": "INV-007-kfold-fix-validation",
        "config": CONFIG_NAME,
        "git_commit": _git_commit(),
        "n_simulations": n_simulations,
        "tier": tier,
        "seeds": list(SEEDS),
        "cells": cells,
    }
    out_path = REPO_ROOT / ".phase12_inv007_kfold_fix_validation.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
