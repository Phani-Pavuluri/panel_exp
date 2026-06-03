"""D5-INST-TBRRIDGE-003 — Targeted OC for F-INF-002 (A16, A18, A21).

Re-runs TBRRidge + UnitJackKnife, Conformal, and JKP on the 001e unit-panel battery
after pooled-counterfactual interface fix. Compares to archived D5-INST-TBRRIDGE-002
pre-fix snapshots. No promotion, MMM, or CalibrationSignal.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.governance.interval_semantics_contract import (
    IntervalReadout,
    classify_interval_semantics,
)
from panel_exp.methods.tbr import TBRRidge
from panel_exp.validation.track_d_d5_inst_tbrridge_001 import _readout_metrics
from panel_exp.validation.track_d_d5_pow_001c import _inject_percent_effect
from panel_exp.inference_result import IntervalType
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_inst_tbrridge_001 import (
    _build_unit_panel,
    _post_arrays,
)
from panel_exp.validation.track_d_d5_inst_tbrridge_002 import D5InstTbrridge002Config
from panel_exp.validation.track_d_d5_inf_postfix_001 import (
    _aggregate_runs,
    _compare_pre_post,
    _decide_postfix_disposition,
)
from panel_exp.validation.track_d_d5_pow_001e import _assign

Tbrridge003Disposition = Literal[
    "diagnostic_interval_only",
    "callable_unverified_interval_semantics",
    "characterized_restricted",
    "blocked_invalid_interval",
    "blocked_interface",
    "restricted_no_promotion",
]

OverallVerdict = Literal[
    "remain_restricted_no_promotion",
    "blocked_low_feasibility",
]

TARGETS: tuple[tuple[str, str, str], ...] = (
    ("A16", "UnitJackKnife", "tbrridge_jk"),
    ("A18", "Conformal", "tbrridge_conformal"),
    ("A21", "JKP", "tbrridge_jkp"),
)

# Archived D5-INST-TBRRIDGE-002 null summaries (pre F-INF-002).
PRE_FIX_TBRRIDGE_002: dict[str, dict[str, Any]] = {
    "A16": {
        "source_artifact": "D5-INST-TBRRIDGE-002",
        "instrument_key": "tbrridge_jk",
        "single_cell_multi_treated": {
            "feasibility_rate": 0.0,
            "null_interval_exclusion_fpr_mean": float("nan"),
            "negative_halfwidth_rate": float("nan"),
            "inverted_bound_rate": float("nan"),
            "mean_interval_halfwidth_mean": float("nan"),
            "dominant_failure_class": "interface_shape",
        },
    },
    "A18": {
        "source_artifact": "D5-INST-TBRRIDGE-002",
        "instrument_key": "tbrridge_conformal",
        "single_cell_multi_treated": {
            "feasibility_rate": 0.0,
            "null_interval_exclusion_fpr_mean": float("nan"),
            "negative_halfwidth_rate": float("nan"),
            "inverted_bound_rate": float("nan"),
            "mean_interval_halfwidth_mean": float("nan"),
            "dominant_failure_class": "interface_shape",
        },
    },
    "A21": {
        "source_artifact": "D5-INST-TBRRIDGE-002",
        "instrument_key": "tbrridge_jkp",
        "single_cell_multi_treated": {
            "feasibility_rate": 0.0,
            "null_interval_exclusion_fpr_mean": float("nan"),
            "negative_halfwidth_rate": float("nan"),
            "inverted_bound_rate": float("nan"),
            "mean_interval_halfwidth_mean": float("nan"),
            "dominant_failure_class": "interface_shape",
        },
    },
}


@dataclass(frozen=True)
class D5InstTbrridge003Config:
    n_mc: int = 14
    n_geos: int = 16
    n_periods: int = 44
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260625
    scenario_name: str = "scm_low_signal"
    reference_design_method: str = "greedy_match_markets"
    effect_grid: tuple[float, ...] = (0.0, 0.08)
    include_single_treated_probe: bool = True
    single_treated_n_mc: int = 6
    null_fpr_acceptable_max: float = 0.15
    null_fpr_concerning_max: float = 0.35
    min_feasibility_rate: float = 0.7
    min_feasibility_for_characterized: float = 0.85


def _structural_per_run(
    results: dict[str, Any] | None,
    *,
    test_length: int,
) -> dict[str, float]:
    if not results:
        return {
            "has_interval": 0.0,
            "negative_halfwidth": float("nan"),
            "inverted_bound": float("nan"),
            "mean_interval_halfwidth": float("nan"),
        }
    try:
        y, y_hat, y_lo, y_hi = _post_arrays(results, test_length)
    except (KeyError, ValueError, TypeError):
        return {
            "has_interval": 0.0,
            "negative_halfwidth": float("nan"),
            "inverted_bound": float("nan"),
            "mean_interval_halfwidth": float("nan"),
        }
    mask = np.isfinite(y_lo) & np.isfinite(y_hi)
    if not np.any(mask):
        return {
            "has_interval": 0.0,
            "negative_halfwidth": float("nan"),
            "inverted_bound": float("nan"),
            "mean_interval_halfwidth": float("nan"),
        }
    lo = y_lo[mask]
    hi = y_hi[mask]
    hw = (hi - lo) / 2.0
    return {
        "has_interval": 1.0,
        "negative_halfwidth": float(np.mean(hw < 0)),
        "inverted_bound": float(np.mean(lo > hi)),
        "mean_interval_halfwidth": float(np.mean(hw)),
    }


def _extended_tbrridge_run(
    panel: PanelDataset,
    *,
    inference: str,
    instrument_key: str,
    percent_effect: float,
    mean_value: np.ndarray,
    cfg: D5InstTbrridge003Config,
    random_state: int,
) -> dict[str, Any]:
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    est = TBRRidge(inference=inference, alpha=cfg.alpha)
    kwargs: dict[str, Any] = {}
    if inference in ("Kfold", "kfold"):
        kwargs["random_state"] = random_state
    try:
        est.run_analysis(pds, **kwargs)
    except (ValueError, RuntimeError) as exc:
        err = f"{type(exc).__name__}:{exc}"
        failure_class = (
            "interface_shape"
            if "broadcast" in err.lower() or "ambiguous" in err.lower()
            else "runtime_error"
        )
        return {
            "instrument_key": instrument_key,
            "inference": inference,
            "feasible": 0.0,
            "error": err,
            "failure_class": failure_class,
        }
    out = _readout_metrics(
        est.results,
        test_length=cfg.test_length,
        percent_effect=percent_effect,
    )
    out.update(
        {
            "feasible": 1.0,
            "instrument_key": instrument_key,
            "inference": inference,
            "readout_family": est.results.get("readout_family"),
        }
    )
    struct = _structural_per_run(est.results, test_length=cfg.test_length)
    out["negative_halfwidth"] = struct["negative_halfwidth"]
    out["inverted_bound"] = struct["inverted_bound"]
    out["inverted_bound_rate"] = struct["inverted_bound"]
    if np.isfinite(struct["mean_interval_halfwidth"]):
        out["mean_interval_halfwidth"] = struct["mean_interval_halfwidth"]
    return out


def _run_multi_treated_replicate(cfg: D5InstTbrridge003Config, *, seed: int) -> dict[str, Any]:
    base = D5InstTbrridge002Config(
        n_mc=1,
        n_geos=cfg.n_geos,
        n_periods=cfg.n_periods,
        train_length=cfg.train_length,
        test_length=cfg.test_length,
        random_state_base=seed,
        scenario_name=cfg.scenario_name,
        reference_design_method=cfg.reference_design_method,
        effect_grid=cfg.effect_grid,
        treatment_probability=cfg.treatment_probability,
    )
    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY[base.scenario_name],
        random_state=seed,
        n_geos=base.n_geos,
        n_periods=base.n_periods,
        treatment_start=base.train_length,
        true_effect=0.0,
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    assignment = _assign(
        base.reference_design_method,
        wide,
        train_length=base.train_length,
        seed=seed,
        treatment_probability=base.treatment_probability,
        n_test_grps=1,
        rerandomization_max_iter=500,
    )
    panel = _build_unit_panel(
        wide,
        assignment,
        cell_key="test_0",
        train_length=base.train_length,
        test_length=base.test_length,
    )
    mean_value = panel.wide_data.loc[panel.treated_units].mean(axis=1).values.astype(float)

    instrument_runs: dict[str, dict[float, dict[str, Any]]] = {}
    for _row, inference, key in TARGETS:
        instrument_runs[key] = {}
        for prc in cfg.effect_grid:
            instrument_runs[key][float(prc)] = _extended_tbrridge_run(
                panel,
                inference=inference,
                instrument_key=key,
                percent_effect=float(prc),
                mean_value=mean_value,
                cfg=cfg,
                random_state=seed,
            )

    return {
        "seed": seed,
        "geometry_mode": "single_cell_multi_treated",
        "instrument_runs": instrument_runs,
        "n_treated": len(panel.treated_units),
        "n_control": len(panel.control_units),
    }


def _single_treated_panel(cfg: D5InstTbrridge003Config, *, seed: int) -> PanelDataset:
    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name],
        random_state=seed,
        n_geos=12,
        n_periods=cfg.n_periods,
        treatment_start=cfg.train_length,
        true_effect=0.0,
        treated_units=("geo_0",),
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    return PanelDataset(
        wide,
        [TimePeriod(cfg.train_length, None)],
        ["geo_0"],
    )


def _run_single_treated_replicate(cfg: D5InstTbrridge003Config, *, seed: int) -> dict[str, Any]:
    panel = _single_treated_panel(cfg, seed=seed)
    mean_value = panel.wide_data.loc[panel.treated_units].mean(axis=1).values.astype(float)
    instrument_runs: dict[str, dict[float, dict[str, Any]]] = {}
    for _row, inference, key in TARGETS:
        instrument_runs[key] = {
            0.0: _extended_tbrridge_run(
                panel,
                inference=inference,
                instrument_key=key,
                percent_effect=0.0,
                mean_value=mean_value,
                cfg=cfg,
                random_state=seed,
            )
        }
    return {
        "seed": seed,
        "geometry_mode": "single_cell_single_treated",
        "instrument_runs": instrument_runs,
        "n_treated": 1,
    }


def _finf_classification(
    *,
    inference: str,
    summary_null: dict[str, Any],
    test_length: int,
) -> dict[str, Any]:
    fpr = summary_null.get("null_interval_exclusion_fpr", {}).get("mean", float("nan"))
    hw_mean = summary_null.get("mean_interval_halfwidth", {}).get("mean", float("nan"))
    neg_rate = summary_null.get("negative_halfwidth_rate", float("nan"))
    n = max(int(summary_null.get("n_feasible", 8)), 1)
    margin = abs(hw_mean) if np.isfinite(hw_mean) and hw_mean > 0 else 1.0
    if np.isfinite(neg_rate) and neg_rate > 0:
        margin = -margin
    interval_type = (
        IntervalType.CONFORMAL_INTERVAL.value
        if inference == "Conformal"
        else IntervalType.CONFIDENCE_INTERVAL.value
    )
    readout = IntervalReadout(
        estimator_name="TBRRidge",
        inference_mode=inference,
        geometry_mode="single_cell",
        path_interval_type=interval_type,
        y=np.full(n, 10.0),
        y_hat=np.full(n, 10.0),
        y_lower=np.full(n, 10.0 - margin),
        y_upper=np.full(n, 10.0 + margin),
        test_length=test_length,
        null_interval_exclusion_rate=float(fpr) if np.isfinite(fpr) else None,
    )
    verdict = classify_interval_semantics(readout, require_metadata_bindings=False)
    return {
        "classification": verdict.classification.value,
        "is_governed_uncertainty": verdict.is_governed_uncertainty,
        "issue_codes": [i.code for i in verdict.issues],
    }


def _decide_tbrridge_003_disposition(
    summary: dict[str, Any],
    *,
    cfg: D5InstTbrridge003Config,
) -> tuple[Tbrridge003Disposition, str]:
    feas = float(summary.get("feasibility_rate", 0.0))
    if feas < 0.1:
        return (
            "blocked_interface",
            "Feasibility near zero — interface or runtime failure on battery.",
        )

    from panel_exp.validation.track_d_d5_inf_postfix_001 import D5InfPostfix001Config

    pf_cfg = D5InfPostfix001Config(
        min_feasibility_rate=cfg.min_feasibility_rate,
        null_fpr_acceptable_max=cfg.null_fpr_acceptable_max,
        null_fpr_concerning_max=cfg.null_fpr_concerning_max,
    )
    base_disp, base_reason = _decide_postfix_disposition(summary, cfg=pf_cfg)

    fpr = summary.get("null_interval_exclusion_fpr", {}).get("mean", float("nan"))
    neg = summary.get("negative_halfwidth_rate", float("nan"))
    inv = summary.get("inverted_bound_rate", float("nan"))

    if base_disp == "blocked_invalid_interval":
        return ("blocked_invalid_interval", base_reason)
    if base_disp == "restricted_no_promotion" and feas < cfg.min_feasibility_rate:
        return ("callable_unverified_interval_semantics", base_reason)

    structural_ok = (
        (not np.isfinite(neg) or neg == 0.0)
        and (not np.isfinite(inv) or inv == 0.0)
        and feas >= cfg.min_feasibility_rate
    )
    if structural_ok and feas >= cfg.min_feasibility_for_characterized:
        if np.isfinite(fpr) and fpr <= cfg.null_fpr_acceptable_max:
            return (
                "characterized_restricted",
                "Feasible on 001e battery; structural bands valid; null FPR within acceptable "
                "range — restricted diagnostic (not governed uncertainty).",
            )
        if np.isfinite(fpr) and fpr <= cfg.null_fpr_concerning_max:
            return (
                "callable_unverified_interval_semantics",
                f"Structurally valid; null interval-exclusion FPR {fpr:.3f} elevated — "
                "behavioral semantics unverified.",
            )

    if base_disp == "diagnostic_interval_only":
        return ("diagnostic_interval_only", base_reason)
    if base_disp == "callable_unverified_interval_semantics":
        return ("callable_unverified_interval_semantics", base_reason)
    return ("callable_unverified_interval_semantics", base_reason)


def _audit_010_bucket(disposition: Tbrridge003Disposition) -> str:
    if disposition in ("diagnostic_interval_only", "characterized_restricted"):
        return "characterized_restricted"
    if disposition == "callable_unverified_interval_semantics":
        return "callable_unverified_interval_semantics"
    if disposition == "blocked_invalid_interval":
        return "blocked_invalid_interval"
    if disposition == "blocked_interface":
        return "blocked_interface"
    return "callable_unverified_interval_semantics"


def _pre_fix_flat(row_id: str) -> dict[str, Any]:
    snap = PRE_FIX_TBRRIDGE_002[row_id]["single_cell_multi_treated"]
    return {
        "feasibility_rate": snap["feasibility_rate"],
        "null_interval_exclusion_fpr": {"mean": snap["null_interval_exclusion_fpr_mean"]},
        "negative_halfwidth_rate": snap["negative_halfwidth_rate"],
        "inverted_bound_rate": snap["inverted_bound_rate"],
        "mean_interval_halfwidth": {"mean": snap["mean_interval_halfwidth_mean"]},
    }


def build_d5_inst_tbrridge_003(cfg: D5InstTbrridge003Config | None = None) -> dict[str, Any]:
    cfg = cfg or D5InstTbrridge003Config()

    multi_reps = [_run_multi_treated_replicate(cfg, seed=cfg.random_state_base + i) for i in range(cfg.n_mc)]
    single_reps: list[dict[str, Any]] = []
    if cfg.include_single_treated_probe:
        for i in range(cfg.single_treated_n_mc):
            single_reps.append(
                _run_single_treated_replicate(cfg, seed=cfg.random_state_base + 10_000 + i)
            )

    tuples_out: dict[str, Any] = {}
    for row_id, inference, key in TARGETS:
        post_multi = _aggregate_runs(
            multi_reps,
            instrument=key,
            geometry_mode="single_cell_multi_treated",
        )
        post_single = (
            _aggregate_runs(
                single_reps,
                instrument=key,
                geometry_mode="single_cell_single_treated",
            )
            if single_reps
            else None
        )
        pre = _pre_fix_flat(row_id)
        compare = _compare_pre_post(pre, post_multi)
        disp, reason = _decide_tbrridge_003_disposition(post_multi, cfg=cfg)
        finf = _finf_classification(
            inference=inference,
            summary_null=post_multi,
            test_length=cfg.test_length,
        )
        tuples_out[row_id] = {
            "audit_010_row": row_id,
            "estimator": "TBRRidge",
            "inference": inference,
            "instrument_key": key,
            "geometries": ["single_cell_multi_treated", "single_cell_single_treated"],
            "pre_fix": PRE_FIX_TBRRIDGE_002[row_id],
            "post_fix": {
                "single_cell_multi_treated": post_multi,
                "single_cell_single_treated": post_single,
            },
            "comparison_multi_treated": compare,
            "tbrridge_003_disposition": disp,
            "disposition_rationale": reason,
            "f_inf_classification": finf,
            "interface_failure_resolved": compare.get("feasibility_rate_delta", 0) is not None
            and post_multi.get("feasibility_rate", 0) > pre.get("feasibility_rate", 0),
            "audit_010_status_after_oc": _audit_010_bucket(disp),
            "promotion": False,
            "calibration_signal_eligible": False,
            "mmm_ready": False,
            "governed_uncertainty": False,
        }

    feasible_any = any(
        tuples_out[r]["post_fix"]["single_cell_multi_treated"].get("feasibility_rate", 0) >= 0.1
        for r, _, _ in TARGETS
    )
    overall: OverallVerdict = (
        "remain_restricted_no_promotion" if feasible_any else "blocked_low_feasibility"
    )

    return {
        "artifact_id": "D5-INST-TBRRIDGE-003",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "prerequisite": "F-INF-002",
        "binding_docs": [
            "F_INF_002_TBRRIDGE_INTERFACE_FIX.md",
            "D5_INST_TBRRIDGE_002",
            "AUDIT-010_mmm_readiness_gap.md",
            "F_BACKLOG_001_IMPLEMENTATION_BACKLOG_CLOSEOUT.md",
        ],
        "governance": {
            "scope": "A16 + A18 + A21 only",
            "no_promotion": True,
            "no_calibration_signal_expansion": True,
            "no_mmm_ingress": True,
            "no_governed_uncertainty_claim": True,
            "no_additional_inference_fix": True,
            "f_inf_classifier_unchanged": True,
            "audit_010_verdict": "not_ready_continue_track_f",
        },
        "config": {
            "n_mc": cfg.n_mc,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "effect_grid": list(cfg.effect_grid),
            "include_single_treated_probe": cfg.include_single_treated_probe,
            "single_treated_n_mc": cfg.single_treated_n_mc,
        },
        "tuples": tuples_out,
        "overall_verdict": overall,
        "next_authorized_track_f_implementation": "none_until_governance_pr",
        "track_f_notes": {
            "prior_battery": "D5-INST-TBRRIDGE-002",
            "interface_fix": "F-INF-002",
            "expected_outcome": "restricted diagnostic at best — not promotion or governed uncertainty",
        },
    }


def write_artifact(path: Path | None = None, *, cfg: D5InstTbrridge003Config | None = None) -> Path:
    cfg = cfg or D5InstTbrridge003Config()
    payload = build_d5_inst_tbrridge_003(cfg)
    out = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INST_TBRRIDGE_003_results.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return out


__all__ = [
    "D5InstTbrridge003Config",
    "PRE_FIX_TBRRIDGE_002",
    "TARGETS",
    "build_d5_inst_tbrridge_003",
    "write_artifact",
]
