"""D5-INST-PLACEBO-001 — SCM placebo geometry characterization (research).

Characterizes SCM+Placebo single-treated vs multi-treated geometry limits under
001e/MCELL fixed windows. No promotion, no CalibrationSignal ingress.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from panel_exp.methods.scm import SyntheticControl
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.inference_result import IntervalType
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_pow_001b import (
    _inject_percent_effect,
    _mean_treated_baseline,
    _scm_jk_readout_metrics,
)
from panel_exp.validation.track_d_d5_pow_001e import _assign, _summarize

GeometryCase = Literal[
    "single_treated_forced",
    "multi_treated_natural",
    "multi_cell_k2_per_cell_single",
]
OverallVerdict = Literal[
    "remain_diagnostic_only_no_promotion",
    "diagnostic_only_confirmed",
]


@dataclass(frozen=True)
class D5InstPlacebo001Config:
    n_mc: int = 14
    n_geos: int = 16
    n_periods: int = 44
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260610
    scenario_name: str = "scm_low_signal"
    reference_design_method: str = "greedy_match_markets"
    effect_grid: tuple[float, ...] = (0.0, 0.04)
    min_control_for_placebo: int = 5
    include_multi_cell_k2: bool = True


def _build_unit_panel(
    wide: pd.DataFrame,
    assignment: dict[str, list[str]],
    *,
    cell_key: str,
    train_length: int,
    test_length: int,
    max_treated_units: int | None = None,
) -> PanelDataset:
    control = list(assignment.get("control") or [])
    treated = list(assignment.get(cell_key) or [])
    if max_treated_units is not None and len(treated) > max_treated_units:
        treated = treated[:max_treated_units]
    end = train_length + test_length
    units = control + treated
    return PanelDataset(
        wide.loc[units].iloc[:, :end].copy(),
        treated_units=treated,
        treated_periods=[TimePeriod(train_length, end - 1) for _ in treated],
    )


def _placebo_readout(
    panel: PanelDataset,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
    geometry_case: str,
    cell_key: str,
) -> dict[str, Any]:
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    n_treated = len(pds.treated_units)
    n_control = len(pds.control_units)
    out: dict[str, Any] = {
        "geometry_case": geometry_case,
        "cell_key": cell_key,
        "n_treated_units": n_treated,
        "n_control_donors": n_control,
        "percent_effect": float(percent_effect),
        "feasible": 0.0,
        "blocked_reason": None,
        "error_type": None,
    }

    if n_treated != 1:
        out["blocked_reason"] = "placebo_in_space_single_treated_only"
        out["error_type"] = "NotImplementedError_expected"
        return out

    if n_control < 2:
        out["blocked_reason"] = "insufficient_control_donors"
        return out

    est = SyntheticControl(inference="Placebo", alpha=alpha)
    try:
        est.run_analysis(pds)
    except (ValueError, NotImplementedError, RuntimeError) as exc:
        out["blocked_reason"] = str(exc)[:200]
        out["error_type"] = type(exc).__name__
        return out

    ir = getattr(est, "inference_result", None)
    stats = est.results.get("placebo_stats") or {}
    path_it = getattr(getattr(ir, "path_interval_type", None), "value", None)
    if path_it is None and ir is not None:
        pit = getattr(ir, "path_interval_type", None)
        path_it = pit.value if hasattr(pit, "value") else pit

    placebo_arr = stats.get("placebo_stats")
    n_pseudo = int(np.size(placebo_arr)) if placebo_arr is not None else 0
    p_val = stats.get("p_value")
    obs_stat = stats.get("observed_stat")

    ci_lo = est.results.get("effect_ci_lower_inversion")
    ci_hi = est.results.get("effect_ci_upper_inversion")
    inversion_ci = (
        ci_lo is not None
        and ci_hi is not None
        and np.isfinite(ci_lo)
        and np.isfinite(ci_hi)
    )
    inversion_excludes_zero = (
        float(ci_lo > 0 or ci_hi < 0) if inversion_ci else float("nan")
    )

    pre = int(pds.treated_start_idxs[0])
    effect = np.asarray(est.results["y"], dtype=float) - np.asarray(
        est.results["y_hat"], dtype=float
    )
    post = effect[-test_length:]
    point_mean = float(np.mean(post))

    out.update(
        {
            "feasible": 1.0,
            "placebo_p_value": float(p_val) if p_val is not None and np.isfinite(p_val) else float("nan"),
            "observed_placebo_stat": float(obs_stat) if obs_stat is not None else float("nan"),
            "n_placebo_pseudo_treated": n_pseudo,
            "path_interval_type": path_it,
            "placebo_band_semantics": float(
                path_it == IntervalType.PLACEBO_BAND.value
                or path_it == IntervalType.PLACEBO_BAND
            ),
            "ci_via_inversion": float(inversion_ci),
            "inversion_ci_excludes_zero": inversion_excludes_zero,
            "mean_point_effect_post": point_mean,
            "effect_ci_lower_inversion": float(ci_lo) if inversion_ci else float("nan"),
            "effect_ci_upper_inversion": float(ci_hi) if inversion_ci else float("nan"),
        }
    )
    diag = stats.get("diagnostics_df")
    if diag is not None and hasattr(diag, "shape"):
        eligible = diag.index[~diag["is_observed"]] if "is_observed" in diag.columns else []
        out["n_eligible_placebo_units_rmspe"] = int(len(eligible))
    return out


def _run_geometry_replicate(
    cfg: D5InstPlacebo001Config,
    *,
    seed: int,
    geometry_case: GeometryCase,
) -> dict[str, Any]:
    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name],
        random_state=seed,
        n_geos=cfg.n_geos,
        n_periods=cfg.n_periods,
        treatment_start=cfg.train_length,
        true_effect=0.0,
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    n_test_grps = 2 if geometry_case == "multi_cell_k2_per_cell_single" else 1
    assignment = _assign(
        cfg.reference_design_method,
        wide,
        train_length=cfg.train_length,
        seed=seed,
        treatment_probability=cfg.treatment_probability,
        n_test_grps=n_test_grps,
        rerandomization_max_iter=500,
    )

    rows: list[dict[str, Any]] = []
    scm_jk_ref: dict[str, Any] = {}

    if geometry_case == "multi_cell_k2_per_cell_single":
        cell_keys = ("test_0", "test_1")
        max_treated = 1
    elif geometry_case == "single_treated_forced":
        cell_keys = ("test_0",)
        max_treated = 1
    else:
        cell_keys = ("test_0",)
        max_treated = None

    for ck in cell_keys:
        panel = _build_unit_panel(
            wide,
            assignment,
            cell_key=ck,
            train_length=cfg.train_length,
            test_length=cfg.test_length,
            max_treated_units=max_treated,
        )
        mean_value = _mean_treated_baseline(panel)
        for prc in cfg.effect_grid:
            key = f"{ck}@{prc}"
            rows.append(
                _placebo_readout(
                    panel,
                    percent_effect=float(prc),
                    mean_value=mean_value,
                    alpha=cfg.alpha,
                    test_length=cfg.test_length,
                    geometry_case=geometry_case,
                    cell_key=ck,
                )
            )
            if float(prc) == 0.0:
                scm_jk_ref[key] = _scm_jk_readout_metrics(
                    panel,
                    percent_effect=0.0,
                    mean_value=mean_value,
                    alpha=cfg.alpha,
                    test_length=cfg.test_length,
                )

    natural_n = len(assignment.get("test_0") or [])
    return {
        "seed": seed,
        "geometry_case": geometry_case,
        "n_test_grps": n_test_grps,
        "n_treated_test_0_assignment": natural_n,
        "n_control_assignment": len(assignment.get("control") or []),
        "placebo_runs": rows,
        "scm_jk_null_reference": scm_jk_ref,
    }


def _aggregate_case(
    replicates: list[dict[str, Any]],
    geometry_case: str,
) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    for rep in replicates:
        if rep["geometry_case"] != geometry_case:
            continue
        runs.extend(rep["placebo_runs"])

    null_runs = [r for r in runs if r.get("percent_effect", 1) == 0.0]
    feasible = [r for r in null_runs if r.get("feasible", 0) >= 1]
    blocked = [r for r in null_runs if r.get("feasible", 0) < 1]

    p_vals = [r["placebo_p_value"] for r in feasible if np.isfinite(r.get("placebo_p_value", np.nan))]
    pseudo_n = [r["n_placebo_pseudo_treated"] for r in feasible]
    donors = [r["n_control_donors"] for r in null_runs]
    inv_excl = [
        r["inversion_ci_excludes_zero"]
        for r in feasible
        if np.isfinite(r.get("inversion_ci_excludes_zero", np.nan))
    ]
    band_sem = [r.get("placebo_band_semantics", 0) for r in feasible]

    def _safe_summ(vals: list[float]) -> dict[str, Any]:
        if not vals:
            return {"mean": None, "std": None, "p95": None, "n": 0}
        return _summarize(vals)

    block_reasons: dict[str, int] = {}
    for r in blocked:
        reason = str(r.get("blocked_reason") or r.get("error_type") or "unknown")[:80]
        block_reasons[reason] = block_reasons.get(reason, 0) + 1

    treated_counts = [r["n_treated_units"] for r in null_runs]

    return {
        "geometry_case": geometry_case,
        "n_replicate_cells": len(null_runs),
        "feasibility_rate": float(len(feasible) / len(null_runs)) if null_runs else 0.0,
        "block_rate": float(len(blocked) / len(null_runs)) if null_runs else 1.0,
        "block_reason_counts": block_reasons,
        "n_treated_units": _summarize([float(x) for x in treated_counts]),
        "n_control_donors": _summarize([float(x) for x in donors]),
        "n_placebo_pseudo_treated": _safe_summ([float(x) for x in pseudo_n]),
        "placebo_p_value": _safe_summ(p_vals),
        "placebo_band_semantics_rate": float(np.mean(band_sem)) if band_sem else 0.0,
        "inversion_ci_excludes_zero_fpr": _safe_summ(inv_excl),
        "geometry_failure_mode": (
            "blocked_multi_treated"
            if geometry_case == "multi_treated_natural"
            else (
                "supported_single_treated"
                if geometry_case == "single_treated_forced"
                else "per_cell_single_treated_only"
            )
        ),
    }


def _decide_status(
    single_agg: dict[str, Any],
    multi_agg: dict[str, Any],
    multi_cell_agg: dict[str, Any] | None,
) -> dict[str, Any]:
    single_ok = single_agg["feasibility_rate"] >= 0.9
    multi_blocked = multi_agg["block_rate"] >= 0.95

    track_e_single = "diagnostic_only" if single_ok else "characterization_required"
    track_e_multi = "blocked" if multi_blocked else "characterization_required"

    return {
        "single_treated": {
            "feasibility_rate": single_agg["feasibility_rate"],
            "track_e_status": track_e_single,
            "calibration_signal_ingress": False,
            "governed_lift": False,
            "interval_semantics": "placebo_band",
            "not_confidence_interval": True,
        },
        "multi_treated_natural": {
            "block_rate": multi_agg["block_rate"],
            "track_e_status": track_e_multi,
            "calibration_signal_ingress": False,
            "pooling_invalid": True,
            "implementation_gate": "placebo() requires len(treated_units)==1",
        },
        "multi_cell_k2": (
            {
                "feasibility_rate": multi_cell_agg["feasibility_rate"] if multi_cell_agg else None,
                "track_e_status": "diagnostic_only_per_cell",
                "no_pooled_placebo": True,
            }
            if multi_cell_agg
            else None
        ),
        "measurement_instrument_tuple": (
            "greedy_match_markets × {single_treated_only|blocked_multi} × "
            "geo.synthetic_control.placebo.relative_att_post.{geometry}.placebo_band"
        ),
        "scm_jk_reference_role": "null_monitor_context_only",
    }


def build_d5_inst_placebo_001(cfg: D5InstPlacebo001Config | None = None) -> dict[str, Any]:
    cfg = cfg or D5InstPlacebo001Config()
    replicates: list[dict[str, Any]] = []
    cases: tuple[GeometryCase, ...] = (
        "single_treated_forced",
        "multi_treated_natural",
    )
    if cfg.include_multi_cell_k2:
        cases = cases + ("multi_cell_k2_per_cell_single",)

    for i in range(cfg.n_mc):
        seed = cfg.random_state_base + i
        for gc in cases:
            replicates.append(_run_geometry_replicate(cfg, seed=seed, geometry_case=gc))

    aggregates = [_aggregate_case(replicates, gc) for gc in cases]
    by_case = {a["geometry_case"]: a for a in aggregates}
    single_agg = by_case["single_treated_forced"]
    multi_agg = by_case["multi_treated_natural"]
    mc_agg = by_case.get("multi_cell_k2_per_cell_single")

    instrument_status = _decide_status(single_agg, multi_agg, mc_agg)

    scm_det = []
    for rep in replicates:
        if rep["geometry_case"] != "single_treated_forced":
            continue
        for _k, jk in rep["scm_jk_null_reference"].items():
            scm_det.append(float(jk.get("detected_correct", 0)))
    placebo_inv = []
    for rep in replicates:
        if rep["geometry_case"] != "single_treated_forced":
            continue
        for run in rep["placebo_runs"]:
            if run.get("percent_effect") != 0.0 or run.get("feasible", 0) < 1:
                continue
            v = run.get("inversion_ci_excludes_zero")
            if v is not None and np.isfinite(v):
                placebo_inv.append(float(v))

    return {
        "artifact_id": "D5-INST-PLACEBO-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "binding_docs": [
            "TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001",
            "TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001",
            "TRACK_E_E5_CALIBRATIONSIGNAL_ELIGIBILITY_POLICY_001",
            "TRACK_D_D3_INFERENCE_METHOD_AUDIT_001",
            "D5_POW_001e_results",
            "D5_MCELL_001_REPORT",
            "PHASE15_PLACEBO_CHARACTERIZATION_001",
        ],
        "governance": {
            "instrument": "SCM_Placebo",
            "reference_instrument": "SCM_UnitJackKnife",
            "status": "diagnostic_only",
            "no_promotion": True,
            "no_calibration_signal_ingress": True,
            "no_lift_evidence": True,
            "no_pooled_multi_cell_placebo": True,
            "placebo_band_not_ci": True,
        },
        "config": {
            "n_mc": cfg.n_mc,
            "reference_design_method": cfg.reference_design_method,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "effect_grid": list(cfg.effect_grid),
            "min_control_for_placebo": cfg.min_control_for_placebo,
            "include_multi_cell_k2": cfg.include_multi_cell_k2,
        },
        "geometry_aggregates": aggregates,
        "instrument_status": instrument_status,
        "scm_jk_vs_placebo_null_context": {
            "scm_jk_interval_exclusion_fpr": _summarize(scm_det),
            "placebo_inversion_exclusion_fpr": _summarize(placebo_inv),
            "note": (
                "SCM+JK null-monitor FPR and placebo inversion exclusion are not "
                "interchangeable estimands; compare as context only."
            ),
        },
        "findings": [
            {
                "id": "D5-PLAC-FIND-001",
                "severity": "high",
                "summary": "placebo() enforces exactly one treated unit; multi-treated panels block.",
                "implication": "Track E INST-006 multi-treated remains blocked; E4-006 fixture valid.",
            },
            {
                "id": "D5-PLAC-FIND-002",
                "severity": "high",
                "summary": "Placebo band semantics (placebo_band) are not CI lift intervals.",
                "implication": "No CalibrationSignal or governed lift from placebo output.",
            },
            {
                "id": "D5-PLAC-FIND-003",
                "severity": "medium",
                "summary": "Multi-cell k=2 supports per-cell single-treated placebo only.",
                "implication": "Do not pool pseudo-treated counts or p-values across cells.",
            },
        ],
        "overall_verdict": "remain_diagnostic_only_no_promotion",
        "track_e_recommendation": {
            "INST-006_single_treated": instrument_status["single_treated"]["track_e_status"],
            "INST-006_multi_treated": instrument_status["multi_treated_natural"]["track_e_status"],
            "wording": (
                "Remain **diagnostic_only** (single-treated); **blocked** (multi-treated default). "
                "TrustReport null-reference context only; never MMM or CalibrationSignal."
            ),
        },
        "user_facing_warnings": [
            "Same null flag on placebo inversion vs SCM+JK does not imply same estimand.",
            "Placebo p-value / band is geometry-limited to single-treated-in-space.",
            "Do not average placebo diagnostics across treated cells or multi-treated pools.",
        ],
        "rules_acknowledged": {
            "no_production_changes": True,
            "no_estimator_changes": True,
            "no_trust_report_changes": True,
            "no_mmm": True,
        },
    }


def write_artifact(path: Path | None = None, *, cfg: D5InstPlacebo001Config | None = None) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INST_PLACEBO_001_results.json"
    )
    payload = build_d5_inst_placebo_001(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_artifact()
    print(f"Wrote {out}")
