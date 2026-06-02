"""D5-MCELL-001 — Optimal concurrent cell-count characterization (research).

Sweeps ``n_test_grps`` (multi-cell geometry) for tier-1 geo designs under the same
fixed-window SCM+JK null-monitor readout as D5-POW-001e. Per-cell only — no pooling.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_pow_001e import (
    CONFIRMED_METHOD_IDS,
    EXCLUDED_FROM_001E,
    METHOD_SPECS,
    D5Pow001eConfig,
    _assign,
    _evaluate_cell,
    _shared_control_adequacy,
    _summarize,
    _test_cell_keys,
    _treatment_cell_conflict,
)

CellCountVerdict = Literal["feasible", "degraded", "blocked", "skipped"]
McellOverallVerdict = Literal[
    "acceptable_with_caveats",
    "acceptable_with_caveats_two_cells",
    "limited_to_single_cell",
    "degrades_beyond_two",
    "insufficient_coverage",
]


@dataclass(frozen=True)
class D5Mcell001Config:
    """Aligned with D5-POW-001e windows; reduced MC for cell-count sweep."""

    n_mc: int = 14
    n_geos: int = 16
    n_periods: int = 44
    treatment_start: int = 32
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260608
    scenario_name: str = "scm_low_signal"
    min_control_units: int = 2
    rerandomization_max_iter: int = 500
    null_fpr_acceptable_max: float = 0.15
    null_fpr_concerning_max: float = 0.35
    requested_cell_counts: tuple[int, ...] = (1, 2, 3, 4, 5)
    readout_instrument: str = "SyntheticControl+UnitJackKnife"
    min_test_units_per_cell: int = 1
    degradation_fpr_delta_vs_baseline: float = 0.12


def _to_pow_cfg(cfg: D5Mcell001Config) -> D5Pow001eConfig:
    return D5Pow001eConfig(
        n_mc=cfg.n_mc,
        n_geos=cfg.n_geos,
        n_periods=cfg.n_periods,
        treatment_start=cfg.treatment_start,
        train_length=cfg.train_length,
        test_length=cfg.test_length,
        alpha=cfg.alpha,
        treatment_probability=cfg.treatment_probability,
        random_state_base=cfg.random_state_base,
        scenario_name=cfg.scenario_name,
        min_control_units=cfg.min_control_units,
        n_test_grps_multi=2,
        rerandomization_max_iter=cfg.rerandomization_max_iter,
        null_fpr_acceptable_max=cfg.null_fpr_acceptable_max,
        null_fpr_concerning_max=cfg.null_fpr_concerning_max,
        geometry_modes=("single_cell",),
        readout_instrument=cfg.readout_instrument,
    )


def _evaluate_at_cell_count(
    wide: Any,
    *,
    method_id: str,
    n_test_grps: int,
    seed: int,
    cfg: D5Mcell001Config,
) -> dict[str, Any]:
    pow_cfg = _to_pow_cfg(cfg)
    geometry_mode = "single_cell" if n_test_grps == 1 else "multi_cell"
    spec = next(s for s in METHOD_SPECS if s.method_id == method_id)

    row: dict[str, Any] = {
        "method_id": method_id,
        "requested_cell_count": n_test_grps,
        "geometry_mode": geometry_mode,
        "n_test_grps": n_test_grps,
        "entrypoint": spec.entrypoint,
        "assignment_geometry": "unit_level_markets",
        "pre_period_window": {"start": 0, "end": cfg.train_length - 1},
        "post_period_window": {
            "start": cfg.train_length,
            "end": cfg.train_length + cfg.test_length - 1,
        },
        "readout_instrument": cfg.readout_instrument,
        "skip_reason": None,
        "per_cell": [],
        "achieved_cell_count": 0,
    }

    if n_test_grps > 1 and not spec.supports_multi_cell:
        row["skip_reason"] = "multi_cell_not_supported_for_method"
        return row

    try:
        assignment = _assign(
            method_id,
            wide,
            train_length=cfg.train_length,
            seed=seed,
            treatment_probability=cfg.treatment_probability,
            n_test_grps=n_test_grps,
            rerandomization_max_iter=cfg.rerandomization_max_iter,
        )
    except (ValueError, RuntimeError) as exc:
        row["skip_reason"] = f"assignment_failed:{type(exc).__name__}"
        return row

    cell_keys = _test_cell_keys(assignment, n_test_grps)
    non_empty = [k for k in cell_keys if len(assignment.get(k) or []) > 0]
    row["achieved_cell_count"] = len(non_empty)
    row["requested_vs_achieved_match"] = row["achieved_cell_count"] == n_test_grps

    control = list(assignment.get("control") or [])
    test_counts = {k: len(assignment.get(k) or []) for k in cell_keys}
    row["control_count"] = len(control)
    row["test_count_per_cell"] = test_counts
    row["shared_control_adequacy"] = _shared_control_adequacy(
        control,
        test_counts,
        min_control_units=cfg.min_control_units,
        n_test_grps=n_test_grps,
    )

    per_cell = [_evaluate_cell(wide, assignment, k, cfg=pow_cfg) for k in cell_keys]
    row["per_cell"] = per_cell

    drifts = {
        c["cell_id"]: c.get("point_null_drift", float("nan"))
        for c in per_cell
        if c.get("point_null_drift") is not None
    }
    row["treatment_cell_conflict"] = _treatment_cell_conflict(drifts)
    row["multiple_comparison_warning"] = bool(
        n_test_grps > 1
        and any(
            (c.get("null_interval_exclusion_fpr") or 0) > cfg.null_fpr_concerning_max
            for c in per_cell
            if c.get("null_interval_exclusion_fpr") is not None
        )
    )
    if not any(c.get("unit_jackknife_feasible") for c in per_cell):
        row["skip_reason"] = row["skip_reason"] or "no_feasible_cells"
    return row


def run_one_replicate_mcell(cfg: D5Mcell001Config, *, seed: int) -> dict[str, Any]:
    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name],
        random_state=seed,
        n_geos=cfg.n_geos,
        n_periods=cfg.n_periods,
        treatment_start=cfg.treatment_start,
        true_effect=0.0,
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    if cfg.train_length + cfg.test_length > wide.shape[1]:
        raise ValueError("fixed window exceeds panel length")

    rows: list[dict[str, Any]] = []
    for method_id in CONFIRMED_METHOD_IDS:
        for k in cfg.requested_cell_counts:
            rows.append(
                _evaluate_at_cell_count(
                    wide,
                    method_id=method_id,
                    n_test_grps=k,
                    seed=seed,
                    cfg=cfg,
                )
            )
    return {"seed": seed, "cell_count_rows": rows}


def _aggregate_cell_count(
    replicates: list[dict[str, Any]],
    *,
    method_id: str,
    n_test_grps: int,
    cfg: D5Mcell001Config,
) -> dict[str, Any]:
    samples = [
        r
        for rep in replicates
        for r in rep["cell_count_rows"]
        if r["method_id"] == method_id and r["requested_cell_count"] == n_test_grps
    ]
    if not samples:
        return {
            "method_id": method_id,
            "requested_cell_count": n_test_grps,
            "cell_count_verdict": "skipped",
            "rationale": "no samples",
        }

    skipped = [s for s in samples if s.get("skip_reason")]
    valid = [s for s in samples if not s.get("skip_reason")]

    achieved = [s.get("achieved_cell_count", 0) for s in samples]
    control_counts = [s.get("control_count", 0) for s in samples]
    shared_ok = [
        1.0
        if s.get("shared_control_adequacy", {}).get("shared_control_adequate")
        else 0.0
        for s in valid
    ]
    shared_stressed = [
        1.0
        if s.get("shared_control_adequacy", {}).get("shared_control_stressed")
        else 0.0
        for s in valid
    ]
    conflict_rate = [
        1.0 if s.get("treatment_cell_conflict", {}).get("treatment_cell_conflict") else 0.0
        for s in valid
    ]
    mc_warn = [1.0 if s.get("multiple_comparison_warning") else 0.0 for s in valid]

    cell_ids = sorted({c["cell_id"] for s in valid for c in s.get("per_cell", [])})
    per_cell_summary: dict[str, Any] = {}
    for cell_id in cell_ids:
        fprs = [
            float(c["null_interval_exclusion_fpr"])
            for s in valid
            for c in s.get("per_cell", [])
            if c.get("cell_id") == cell_id
            and c.get("unit_jackknife_feasible")
            and c.get("null_interval_exclusion_fpr") is not None
        ]
        n_treated = [
            int(c["n_treated"])
            for s in valid
            for c in s.get("per_cell", [])
            if c.get("cell_id") == cell_id
        ]
        n_donors = [
            int(c["n_control_donors"])
            for s in valid
            for c in s.get("per_cell", [])
            if c.get("cell_id") == cell_id
        ]
        balances = [
            float(c["pre_balance_corr"])
            for s in valid
            for c in s.get("per_cell", [])
            if c.get("cell_id") == cell_id
            if np.isfinite(c.get("pre_balance_corr", float("nan")))
        ]
        per_cell_summary[cell_id] = {
            "null_interval_exclusion_fpr": _summarize(fprs),
            "n_treated": _summarize([float(x) for x in n_treated]),
            "n_control_donors": _summarize([float(x) for x in n_donors]),
            "pre_period_balance_corr": _summarize(balances),
        }

    max_cell_fpr = float(
        max(
            (
                v["null_interval_exclusion_fpr"]["mean"]
                for v in per_cell_summary.values()
                if np.isfinite(v["null_interval_exclusion_fpr"]["mean"])
            ),
            default=float("nan"),
        )
    )
    mean_cell_fpr = _summarize(
        [
            float(c["null_interval_exclusion_fpr"])
            for s in valid
            for c in s.get("per_cell", [])
            if c.get("unit_jackknife_feasible")
            and c.get("null_interval_exclusion_fpr") is not None
        ]
    )["mean"]

    empty_cell_rate = float(
        np.mean(
            [
                sum(1 for c in s.get("per_cell", []) if c.get("n_treated", 0) < cfg.min_test_units_per_cell)
                / max(1, len(s.get("per_cell", [])))
                for s in valid
            ]
        )
    ) if valid else float("nan")

    verdict, rationale = _decide_cell_count(
        n_test_grps=n_test_grps,
        n_valid=len(valid),
        n_total=len(samples),
        max_cell_fpr=max_cell_fpr,
        mean_cell_fpr=mean_cell_fpr,
        shared_ok_rate=float(np.mean(shared_ok)) if shared_ok else 0.0,
        shared_stressed_rate=float(np.mean(shared_stressed)) if shared_stressed else 0.0,
        conflict_rate=float(np.mean(conflict_rate)) if conflict_rate else 0.0,
        mc_warn_rate=float(np.mean(mc_warn)) if mc_warn else 0.0,
        empty_cell_rate=empty_cell_rate,
        achieved_mean=float(np.mean(achieved)) if achieved else 0.0,
        cfg=cfg,
    )

    return {
        "method_id": method_id,
        "requested_cell_count": n_test_grps,
        "achieved_cell_count_mean": float(np.mean(achieved)) if achieved else float("nan"),
        "achieved_cell_count_min": int(min(achieved)) if achieved else 0,
        "control_count_mean": float(np.mean(control_counts)) if control_counts else float("nan"),
        "n_replicates": len(samples),
        "n_valid": len(valid),
        "n_skipped": len(skipped),
        "skip_reasons": sorted({s["skip_reason"] for s in skipped if s.get("skip_reason")}),
        "shared_control_adequacy_rate": float(np.mean(shared_ok)) if shared_ok else float("nan"),
        "shared_control_stressed_rate": float(np.mean(shared_stressed)) if shared_stressed else float("nan"),
        "treatment_cell_conflict_rate": float(np.mean(conflict_rate)) if conflict_rate else float("nan"),
        "multiple_comparison_warning_rate": float(np.mean(mc_warn)) if mc_warn else float("nan"),
        "empty_or_underfilled_cell_rate": empty_cell_rate,
        "per_cell_summary": per_cell_summary,
        "max_per_cell_null_fpr": max_cell_fpr,
        "mean_per_cell_null_fpr": mean_cell_fpr,
        "cell_count_verdict": verdict,
        "rationale": rationale,
        "null_interval_exclusion_fpr_pooled_across_cells": None,
    }


def _decide_cell_count(
    *,
    n_test_grps: int,
    n_valid: int,
    n_total: int,
    max_cell_fpr: float,
    mean_cell_fpr: float,
    shared_ok_rate: float,
    shared_stressed_rate: float,
    conflict_rate: float,
    mc_warn_rate: float,
    empty_cell_rate: float,
    achieved_mean: float,
    cfg: D5Mcell001Config,
) -> tuple[CellCountVerdict, str]:
    if n_valid == 0:
        return "blocked", "All replicates skipped."
    if n_valid < max(3, n_total // 3):
        return "skipped", f"Only {n_valid}/{n_total} valid replicates."
    if achieved_mean < n_test_grps - 0.01:
        return "blocked", f"Achieved {achieved_mean:.1f} < requested {n_test_grps} cells."
    if shared_ok_rate < 0.85:
        return "blocked", f"Shared control inadequate in {(1-shared_ok_rate)*100:.0f}% of replicates."
    if empty_cell_rate > 0.25:
        return "blocked", f"Underfilled cells in {empty_cell_rate*100:.0f}% of replicate mass."

    if n_test_grps == 1:
        if np.isfinite(max_cell_fpr) and max_cell_fpr <= cfg.null_fpr_acceptable_max:
            return "feasible", "Single-cell baseline acceptable."
        if np.isfinite(max_cell_fpr) and max_cell_fpr <= cfg.null_fpr_concerning_max:
            return "degraded", "Single-cell baseline elevated null FPR."
        return "blocked", "Single-cell baseline null FPR too high."

    if conflict_rate > 0.25:
        return "degraded", f"Treatment-cell conflict rate {conflict_rate:.2f}."
    if mc_warn_rate > 0.35:
        return "degraded", f"Multiple-comparison warning rate {mc_warn_rate:.2f}."
    if shared_stressed_rate > 0.5:
        return "degraded", f"Shared control stressed in {shared_stressed_rate*100:.0f}% of replicates."
    if np.isfinite(max_cell_fpr) and max_cell_fpr > cfg.null_fpr_concerning_max:
        return "blocked", f"Max per-cell null FPR {max_cell_fpr:.3f} exceeds concern threshold."
    if np.isfinite(max_cell_fpr) and max_cell_fpr > cfg.null_fpr_acceptable_max:
        return "degraded", f"Max per-cell null FPR {max_cell_fpr:.3f} above acceptable."
    return "feasible", "Per-cell null-monitor acceptable under shared-control readout."


def _method_recommendations(
    aggregates: list[dict[str, Any]],
    *,
    cfg: D5Mcell001Config,
) -> dict[str, Any]:
    by_method: dict[str, list[dict[str, Any]]] = {}
    for row in aggregates:
        by_method.setdefault(row["method_id"], []).append(row)

    method_tables: list[dict[str, Any]] = []

    for method_id in CONFIRMED_METHOD_IDS:
        rows = sorted(by_method.get(method_id, []), key=lambda r: r["requested_cell_count"])
        baseline_fpr = float("nan")
        for r in rows:
            if r["requested_cell_count"] == 1:
                baseline_fpr = r.get("max_per_cell_null_fpr", float("nan"))
                break

        recommended = 1
        degraded_at: int | None = None
        blocked_at: int | None = None

        for r in rows:
            k = int(r["requested_cell_count"])
            v = r["cell_count_verdict"]
            if v == "feasible":
                recommended = k
            elif v == "degraded" and degraded_at is None:
                degraded_at = k
            elif v == "blocked" and blocked_at is None:
                blocked_at = k
                break

        if blocked_at is not None and blocked_at <= recommended:
            recommended = max(1, blocked_at - 1)

        method_tables.append(
            {
                "method_id": method_id,
                "recommended_max_cells": recommended,
                "degraded_at_cell_count": degraded_at,
                "blocked_at_cell_count": blocked_at,
                "single_cell_baseline_max_fpr": baseline_fpr,
                "by_cell_count": rows,
            }
        )

    recommended_vals = [t["recommended_max_cells"] for t in method_tables]
    conservative = min(recommended_vals)
    majority = int(np.median(recommended_vals))
    return {
        "per_method": method_tables,
        "conservative_recommended_max_cells": conservative,
        "majority_recommended_max_cells": majority,
        "max_across_methods": max(recommended_vals),
        "rule_of_thumb": _rule_of_thumb(method_tables, cfg, conservative, majority),
    }


def _rule_of_thumb(
    method_tables: list[dict[str, Any]],
    cfg: D5Mcell001Config,
    conservative: int,
    majority: int,
) -> str:
    n_geos = cfg.n_geos
    return (
        f"On scm_low_signal with n_geos={n_geos}, treatment_probability={cfg.treatment_probability}, "
        f"and fixed-window SCM+JK null-monitor readout: **{majority} concurrent cell(s)** is feasible "
        f"for most tier-1 methods; **conservative k≤{conservative}** if all six must pass. "
        f"k≥3 degrades (≈1 treated market per cell, shared-control stress, elevated per-cell null FPR). "
        f"Per-cell evidence only — no pooled multi-cell claim."
    )


def _track_e_mcell_update(conservative_max: int) -> dict[str, Any]:
    return {
        "e_des_mcell_012": "characterized",
        "geo_002_card": "suitable_with_caveats",
        "recommended_max_concurrent_cells": conservative_max,
        "pooling_rule_required_for_pooled_claim": True,
        "warnings": [
            "Do not pool per-cell null FPR or lift across cells.",
            "Report per-cell TrustReport / triangulation dispositions when k>1.",
            "Shared control is control-only donors per cell (exclude other test cells).",
            f"Default product guidance: k≤{conservative_max} under 001 battery settings.",
        ],
    }


def build_d5_mcell_001(cfg: D5Mcell001Config | None = None) -> dict[str, Any]:
    cfg = cfg or D5Mcell001Config()
    replicates = [
        run_one_replicate_mcell(cfg, seed=cfg.random_state_base + i) for i in range(cfg.n_mc)
    ]

    aggregates: list[dict[str, Any]] = []
    for method_id in CONFIRMED_METHOD_IDS:
        for k in cfg.requested_cell_counts:
            aggregates.append(
                _aggregate_cell_count(
                    replicates,
                    method_id=method_id,
                    n_test_grps=k,
                    cfg=cfg,
                )
            )

    recommendations = _method_recommendations(aggregates, cfg=cfg)
    conservative = recommendations["conservative_recommended_max_cells"]
    majority = recommendations["majority_recommended_max_cells"]

    if majority >= 3:
        overall: McellOverallVerdict = "acceptable_with_caveats"
    elif majority >= 2:
        overall = "acceptable_with_caveats_two_cells"
    elif conservative >= 1:
        overall = "limited_to_single_cell"
    else:
        overall = "degrades_beyond_two"

    return {
        "artifact_id": "D5-MCELL-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "binding_docs": [
            "ROADMAP_DESIGN_READOUT_UPDATE_001",
            "D5_POW_001e_results",
            "D5_DES_SUPERGEO_001_REPORT",
            "D5_DES_TRIM_001_REPORT",
            "AUDIT-009_track_e_completion_gate",
        ],
        "governance": {
            "geometry_mode": "multi_cell via n_test_grps > 1",
            "not_a_design_method": True,
            "per_cell_only": True,
            "no_pooled_multi_cell_claim": True,
            "no_mmm_ingress": True,
            "no_promotion": True,
            "excluded_methods": list(EXCLUDED_FROM_001E),
            "readout": "SCM+UnitJackKnife null-monitor reference only",
        },
        "config": {
            "n_mc": cfg.n_mc,
            "n_geos": cfg.n_geos,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "treatment_probability": cfg.treatment_probability,
            "requested_cell_counts": list(cfg.requested_cell_counts),
            "confirmed_methods": list(CONFIRMED_METHOD_IDS),
        },
        "cell_count_aggregates": aggregates,
        "recommendations": recommendations,
        "overall_verdict": overall,
        "track_e": _track_e_mcell_update(conservative),
        "findings": [
            {
                "id": "D5-MCELL-FIND-001",
                "severity": "high",
                "summary": "Shared control pool is subdivided across k cells — control count per cell readout is shared, not per-cell exclusive.",
                "implication": "Large k drives 1 treated market per cell on typical n_geos=16 panels.",
            },
            {
                "id": "D5-MCELL-FIND-002",
                "severity": "medium",
                "summary": "Per-cell null FPR and multiple-comparison warnings rise as k increases.",
                "implication": "No pooled headline; report per-cell only.",
            },
            {
                "id": "D5-MCELL-FIND-003",
                "severity": "medium",
                "summary": "k=2 was acceptable for all six tier-1 methods on 001e/001 battery; k≥3 degrades on this fixture.",
                "implication": f"Rule of thumb: k≤{conservative} unless re-characterized for larger n_geos.",
            },
        ],
        "rules_acknowledged": {
            "no_production_changes": True,
            "no_estimator_changes": True,
            "no_trust_report_changes": True,
        },
    }


def write_artifact(path: Path | None = None, *, cfg: D5Mcell001Config | None = None) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_MCELL_001_results.json"
    )
    payload = build_d5_mcell_001(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_artifact()
    print(f"Wrote {out}")
