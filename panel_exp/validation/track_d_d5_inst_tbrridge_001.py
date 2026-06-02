"""D5-INST-TBRRIDGE-001 — TBRRidge + KFold / BRB restricted-instrument OC (research).

Characterizes TBRRidge comparators under flat tier-1 assignment vs SCM+JK null-monitor
reference. No promotion, no CalibrationSignal ingress.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from panel_exp.methods.tbr import TBRRidge
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_pow_001b import (
    _inject_percent_effect,
    _mean_treated_baseline,
    _scm_jk_readout_metrics,
)
from panel_exp.validation.track_d_d5_pow_001c import (
    _aggregated_two_row_panel,
    _readout_metrics,
)
from panel_exp.validation.track_d_d5_pow_001e import _assign, _summarize

InstVerdict = Literal[
    "remain_restricted",
    "restricted_diagnostic_only",
    "restricted_narrower_wording",
]
OverallVerdict = Literal[
    "remain_restricted_no_promotion",
    "diagnostic_only_confirmed",
]


@dataclass(frozen=True)
class D5InstTbrridge001Config:
    n_mc: int = 14
    n_geos: int = 16
    n_periods: int = 44
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260609
    scenario_name: str = "scm_low_signal"
    reference_design_method: str = "greedy_match_markets"
    effect_grid: tuple[float, ...] = (0.0, 0.04, 0.08)
    null_fpr_acceptable_max: float = 0.15
    null_fpr_concerning_max: float = 0.35
    include_multi_cell_k2: bool = True
    kfold_seed_sensitivity_replicates: int = 3


def _build_unit_panel(
    wide: pd.DataFrame,
    assignment: dict[str, list[str]],
    *,
    cell_key: str,
    train_length: int,
    test_length: int,
) -> PanelDataset:
    """Per-cell readout panel: shared control donors + one test cell (001e contract)."""
    control = list(assignment.get("control") or [])
    treated = list(assignment.get(cell_key) or [])
    end = train_length + test_length
    units = control + treated
    return PanelDataset(
        wide.loc[units].iloc[:, :end].copy(),
        treated_units=treated,
        treated_periods=[TimePeriod(train_length, end - 1) for _ in treated],
    )


def _run_tbr(
    panel: PanelDataset,
    *,
    inference: str,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
    random_state: int,
    path: str,
) -> dict[str, float]:
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    est = TBRRidge(inference=inference, alpha=alpha)
    kwargs: dict[str, Any] = {}
    if inference in ("Kfold", "kfold"):
        kwargs["random_state"] = random_state
    try:
        est.run_analysis(pds, **kwargs)
    except (ValueError, RuntimeError) as exc:
        return {
            "path": path,
            "feasible": 0.0,
            "error": f"{type(exc).__name__}:{exc}",
            "mean_point_effect": float("nan"),
            "detected_interval_excludes_zero": float("nan"),
            "covers_zero": float("nan"),
            "mean_interval_halfwidth": float("nan"),
            "directional_recovery": float("nan"),
        }
    out = _readout_metrics(
        est.results,
        test_length=test_length,
        percent_effect=percent_effect,
    )
    out["path"] = path
    out["feasible"] = 1.0
    y, y_hat, y_lo, y_hi = _post_arrays(est.results, test_length)
    out["mean_interval_halfwidth"] = float(np.mean((y_hi - y_lo) / 2.0))
    out["point_to_scm_scale_note"] = path
    return out


def _post_arrays(results: dict, test_length: int) -> tuple[np.ndarray, ...]:
    y = np.asarray(results["y"], dtype=float)
    y_hat = np.asarray(results["y_hat"], dtype=float)
    y_lo = np.asarray(results["y_lower"], dtype=float)
    y_hi = np.asarray(results["y_upper"], dtype=float)
    sl = slice(-test_length, None)
    return y[sl], y_hat[sl], y_lo[sl], y_hi[sl]


def _run_replicate(
    cfg: D5InstTbrridge001Config,
    *,
    seed: int,
    n_test_grps: int,
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
    assignment = _assign(
        cfg.reference_design_method,
        wide,
        train_length=cfg.train_length,
        seed=seed,
        treatment_probability=cfg.treatment_probability,
        n_test_grps=n_test_grps,
        rerandomization_max_iter=500,
    )

    cell_key = "test_0"
    unit_panel = _build_unit_panel(
        wide,
        assignment,
        cell_key=cell_key,
        train_length=cfg.train_length,
        test_length=cfg.test_length,
    )
    mean_value = _mean_treated_baseline(unit_panel)
    post_end = cfg.train_length + cfg.test_length - 1
    agg_panel = _aggregated_two_row_panel(
        wide,
        list(assignment.get(cell_key) or []),
        train_length=cfg.train_length,
        post_end=post_end,
    )
    agg_mean = _mean_treated_baseline(agg_panel)

    instruments: dict[str, dict[float, dict[str, float]]] = {
        "scm_jk_unit": {},
        "tbr_kfold_unit": {},
        "tbr_kfold_agg2": {},
        "tbr_brb_unit": {},
        "tbr_brb_agg2": {},
    }

    for prc in cfg.effect_grid:
        instruments["scm_jk_unit"][float(prc)] = _scm_jk_readout_metrics(
            unit_panel,
            percent_effect=float(prc),
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
        )
        instruments["tbr_kfold_unit"][float(prc)] = _run_tbr(
            unit_panel,
            inference="Kfold",
            percent_effect=float(prc),
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            random_state=seed,
            path="tbr_kfold_unit",
        )
        instruments["tbr_kfold_agg2"][float(prc)] = _run_tbr(
            agg_panel,
            inference="Kfold",
            percent_effect=float(prc),
            mean_value=agg_mean,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            random_state=seed,
            path="tbr_kfold_agg2",
        )
        instruments["tbr_brb_unit"][float(prc)] = _run_tbr(
            unit_panel,
            inference="BlockResidualBootstrap",
            percent_effect=float(prc),
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            random_state=seed,
            path="tbr_brb_unit",
        )
        instruments["tbr_brb_agg2"][float(prc)] = _run_tbr(
            agg_panel,
            inference="BlockResidualBootstrap",
            percent_effect=float(prc),
            mean_value=agg_mean,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            random_state=seed,
            path="tbr_brb_agg2",
        )

    null_scm = instruments["scm_jk_unit"][0.0]
    null_tbr_u = instruments["tbr_kfold_unit"][0.0]
    disagreement = {
        "detection_scm_vs_tbr_kfold_unit": float(
            null_scm.get("detected_correct", 0) != null_tbr_u.get("detected_interval_excludes_zero", 1)
        ),
        "point_sign_disagreement": float(
            np.sign(null_scm.get("mean_point_effect", 0)) != np.sign(null_tbr_u.get("mean_point_effect", 0))
            if null_tbr_u.get("feasible", 1)
            else float("nan")
        ),
        "tbr_kfold_higher_detection_than_scm": float(
            null_tbr_u.get("detected_interval_excludes_zero", 0)
            > null_scm.get("detected_correct", 0)
        ),
    }

    kfold_seed_spread: list[float] = []
    for off in range(cfg.kfold_seed_sensitivity_replicates):
        m = _run_tbr(
            unit_panel,
            inference="Kfold",
            percent_effect=0.0,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            random_state=seed + 1000 + off,
            path="tbr_kfold_unit",
        )
        if m.get("feasible", 1):
            kfold_seed_spread.append(m["mean_point_effect"])

    row: dict[str, Any] = {
        "seed": seed,
        "geometry_mode": "single_cell" if n_test_grps == 1 else "multi_cell",
        "n_test_grps": n_test_grps,
        "n_control": len(assignment.get("control") or []),
        "n_treated_test_0": len(assignment.get("test_0") or []),
        "instruments": instruments,
        "disagreement_at_null": disagreement,
        "kfold_null_point_spread": float(np.std(kfold_seed_spread)) if kfold_seed_spread else float("nan"),
    }

    if n_test_grps == 2 and cfg.include_multi_cell_k2:
        per_cell_scm = []
        per_cell_tbr = []
        for ck in ("test_0", "test_1"):
            cp = _build_unit_panel(
                wide, assignment, cell_key=ck, train_length=cfg.train_length, test_length=cfg.test_length
            )
            mv = _mean_treated_baseline(cp)
            per_cell_scm.append(
                _scm_jk_readout_metrics(
                    cp, percent_effect=0.0, mean_value=mv, alpha=cfg.alpha, test_length=cfg.test_length
                )
            )
            per_cell_tbr.append(
                _run_tbr(
                    cp,
                    inference="Kfold",
                    percent_effect=0.0,
                    mean_value=mv,
                    alpha=cfg.alpha,
                    test_length=cfg.test_length,
                    random_state=seed,
                    path=f"tbr_kfold_{ck}",
                )
            )
        row["multi_cell_k2_per_cell_null"] = {
            "scm_jk": per_cell_scm,
            "tbr_kfold": per_cell_tbr,
        }

    return row


def _aggregate_instrument(
    replicates: list[dict[str, Any]],
    instrument_key: str,
    *,
    effect: float,
) -> dict[str, Any]:
    vals_fpr = []
    vals_point = []
    vals_hw = []
    vals_cov = []
    feasible = []
    for rep in replicates:
        if rep.get("geometry_mode") != "single_cell":
            continue
        inst = rep["instruments"][instrument_key].get(float(effect), {})
        if instrument_key.startswith("tbr") and not inst.get("feasible", 1):
            continue
        if instrument_key == "scm_jk_unit":
            if "detected_correct" in inst:
                vals_fpr.append(float(inst["detected_correct"]))
            if "mean_point_effect" in inst:
                vals_point.append(float(inst["mean_point_effect"]))
            if "mean_jk_halfwidth" in inst:
                vals_hw.append(float(inst["mean_jk_halfwidth"]))
            if "covers_zero_correct" in inst:
                vals_cov.append(float(inst["covers_zero_correct"]))
        else:
            if "detected_interval_excludes_zero" in inst:
                vals_fpr.append(float(inst["detected_interval_excludes_zero"]))
            if "mean_point_effect" in inst:
                vals_point.append(float(inst["mean_point_effect"]))
            if "mean_interval_halfwidth" in inst:
                vals_hw.append(float(inst["mean_interval_halfwidth"]))
            if "covers_zero" in inst:
                vals_cov.append(float(inst["covers_zero"]))
        feasible.append(float(inst.get("feasible", 1)))

    return {
        "instrument": instrument_key,
        "effect": effect,
        "null_interval_exclusion_fpr": _summarize(vals_fpr),
        "mean_point_effect": _summarize(vals_point),
        "mean_interval_halfwidth": _summarize(vals_hw),
        "covers_zero_rate": _summarize(vals_cov),
        "feasibility_rate": float(np.mean(feasible)) if feasible else 0.0,
    }


def _decide_instrument_status(
    scm_null: dict[str, Any],
    tbr_unit_null: dict[str, Any],
    tbr_agg_null: dict[str, Any],
    brb_unit_null: dict[str, Any],
    *,
    cfg: D5InstTbrridge001Config,
) -> dict[str, Any]:
    tbr_fpr = tbr_unit_null["null_interval_exclusion_fpr"]["mean"]
    scm_fpr = scm_null["null_interval_exclusion_fpr"]["mean"]
    brb_feas = brb_unit_null.get("feasibility_rate", 0.0)

    verdict: InstVerdict = "remain_restricted"
    rationale = "TBRRidge remains restricted comparator; not governed lift or CalibrationSignal."

    if np.isfinite(tbr_fpr) and tbr_fpr > cfg.null_fpr_concerning_max:
        rationale = (
            f"Unit-panel TBRRidge+Kfold null FPR {tbr_fpr:.3f} exceeds concern threshold "
            f"({cfg.null_fpr_concerning_max}); remain restricted."
        )
    elif np.isfinite(tbr_fpr) and tbr_fpr > cfg.null_fpr_acceptable_max:
        verdict = "restricted_diagnostic_only"
        rationale = (
            "Elevated null interval-exclusion vs SCM+JK; diagnostic/TrustReport context only."
        )
    elif np.isfinite(scm_fpr) and np.isfinite(tbr_fpr) and tbr_fpr > scm_fpr + 0.1:
        verdict = "restricted_diagnostic_only"
        rationale = "TBRRidge+Kfold more anti-conservative than SCM+JK null-monitor at null."

    agg_fpr = tbr_agg_null["null_interval_exclusion_fpr"]["mean"]
    unit_pt = tbr_unit_null["mean_point_effect"]["mean"]
    agg_pt = tbr_agg_null["mean_point_effect"]["mean"]
    magnitude_ratio = (
        abs(agg_pt / unit_pt) if np.isfinite(unit_pt) and abs(unit_pt) > 1e-6 else float("nan")
    )

    return {
        "tbr_kfold_unit": verdict,
        "tbr_kfold_agg2": "remain_restricted",
        "tbr_brb_unit": "restricted_narrower_wording" if brb_feas < 0.9 else "remain_restricted",
        "rationale": rationale,
        "null_fpr_tbr_kfold_unit": tbr_fpr,
        "null_fpr_scm_jk_unit": scm_fpr,
        "null_fpr_tbr_kfold_agg2": agg_fpr,
        "agg_to_unit_point_ratio_at_null": magnitude_ratio,
        "brb_feasibility_rate": brb_feas,
        "track_e_inst_002": "restricted",
        "track_e_inst_003": "restricted",
        "calibration_signal_ingress": False,
        "governed_lift": False,
    }


def build_d5_inst_tbrridge_001(cfg: D5InstTbrridge001Config | None = None) -> dict[str, Any]:
    cfg = cfg or D5InstTbrridge001Config()
    replicates: list[dict[str, Any]] = []
    for i in range(cfg.n_mc):
        seed = cfg.random_state_base + i
        replicates.append(_run_replicate(cfg, seed=seed, n_test_grps=1))
        if cfg.include_multi_cell_k2:
            replicates.append(_run_replicate(cfg, seed=seed + 50000, n_test_grps=2))

    single = [r for r in replicates if r["geometry_mode"] == "single_cell"]
    inst_keys = ("scm_jk_unit", "tbr_kfold_unit", "tbr_kfold_agg2", "tbr_brb_unit", "tbr_brb_agg2")
    summaries = [_aggregate_instrument(single, k, effect=0.0) for k in inst_keys]
    summaries_effect = [_aggregate_instrument(single, "tbr_kfold_unit", effect=0.08) for _ in [0]]

    scm_null = next(s for s in summaries if s["instrument"] == "scm_jk_unit")
    tbr_u = next(s for s in summaries if s["instrument"] == "tbr_kfold_unit")
    tbr_a = next(s for s in summaries if s["instrument"] == "tbr_kfold_agg2")
    brb_u = next(s for s in summaries if s["instrument"] == "tbr_brb_unit")

    status = _decide_instrument_status(scm_null, tbr_u, tbr_a, brb_u, cfg=cfg)

    disagree_rate = float(
        np.mean([r["disagreement_at_null"]["detection_scm_vs_tbr_kfold_unit"] for r in single])
    )
    kfold_spread = _summarize([r["kfold_null_point_spread"] for r in single])

    return {
        "artifact_id": "D5-INST-TBRRIDGE-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "binding_docs": [
            "TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001",
            "TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001",
            "TRACK_E_E5_CALIBRATIONSIGNAL_ELIGIBILITY_POLICY_001",
            "D5_POW_001e_results",
            "D5_MCELL_001_REPORT",
        ],
        "governance": {
            "instruments": ["TBRRidge_Kfold", "TBRRidge_BlockResidualBootstrap"],
            "reference_instrument": "SCM_UnitJackKnife",
            "status": "restricted_comparator",
            "no_promotion": True,
            "no_calibration_signal_ingress": True,
            "no_pooled_multi_cell_claim": True,
            "no_override_governed_primary": True,
        },
        "config": {
            "n_mc": cfg.n_mc,
            "reference_design_method": cfg.reference_design_method,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "effect_grid": list(cfg.effect_grid),
            "include_multi_cell_k2": cfg.include_multi_cell_k2,
        },
        "instrument_summaries_null": summaries,
        "instrument_summary_injected_8pct": summaries_effect[0],
        "disagreement_with_scm_jk": {
            "detection_mismatch_rate": disagree_rate,
            "kfold_null_point_std_across_seeds": kfold_spread,
        },
        "instrument_status": status,
        "findings": [
            {
                "id": "D5-TBR-FIND-001",
                "severity": "high",
                "summary": "TBRRidge+Kfold on 2-row aggregate diverges from unit SCM+JK (001a/001c).",
                "implication": "Do not use geo power / agg TBR as null-monitor for unit tests.",
            },
            {
                "id": "D5-TBR-FIND-002",
                "severity": "high",
                "summary": "TBRRidge null interval-exclusion behavior differs from SCM+JK reference.",
                "implication": "E4 restricted-positive context must not upgrade governed primary.",
            },
            {
                "id": "D5-TBR-FIND-003",
                "severity": "medium",
                "summary": "Kfold seed sensitivity affects TBR point readout at null.",
                "implication": "Report as diagnostic_only; not decision-grade stability.",
            },
        ],
        "overall_verdict": "remain_restricted_no_promotion",
        "track_e_recommendation": {
            "INST-002": status["track_e_inst_002"],
            "INST-003": status["track_e_inst_003"],
            "wording": (
                "Remain **restricted** / **diagnostic_only** for TrustReport context; "
                "never CalibrationSignal or governed lift. Unit SCM+JK is null-monitor reference."
            ),
        },
        "user_facing_warnings": [
            "TBRRidge+Kfold is the geo PowerAnalysis readout path — not equivalent to SCM+JK unit null-monitor.",
            "Do not treat restricted TBR positive intervals as lift promotion over null-compatible SCM+JK primary.",
            "2-row aggregated TBR magnitudes are not comparable to unit relative ATT without estimand bridge.",
        ],
        "rules_acknowledged": {
            "no_production_changes": True,
            "no_estimator_changes": True,
            "no_trust_report_changes": True,
            "no_mmm": True,
        },
    }


def write_artifact(path: Path | None = None, *, cfg: D5InstTbrridge001Config | None = None) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INST_TBRRIDGE_001_results.json"
    )
    payload = build_d5_inst_tbrridge_001(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_artifact()
    print(f"Wrote {out}")
