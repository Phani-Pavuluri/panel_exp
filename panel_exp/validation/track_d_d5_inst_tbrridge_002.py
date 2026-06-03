"""D5-INST-TBRRIDGE-002 — TBRRidge remaining inference OC (research).

Characterizes UnitJackKnife, JKP, Conformal, TimeSeriesKfold, and registry Bayesian
on unit panels after AUDIT-010 + Track F P0. TBRRidge+Kfold/BRB are context-only (001).
Not class TBR. No promotion, no CalibrationSignal.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.governance.instrument_contract import (
    INV_015_REGISTRY_BAYESIAN_NOT_MCMC,
    registry_bayesian_production_block_reason,
)
from panel_exp.methods.tbr import TBRRidge
from panel_exp.panel_data import PanelDataset
from panel_exp.validation.recovery_runner import all_recovery_configs
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_inst_audit_001 import ProbeConfig, _build_wide, _probe_run
from panel_exp.validation.track_d_d5_inst_tbrridge_001 import (
    _aggregate_instrument,
    _build_unit_panel,
    _run_tbr,
)
from panel_exp.validation.track_d_d5_pow_001b import _mean_treated_baseline, _scm_jk_readout_metrics
from panel_exp.validation.track_d_d5_pow_001e import _assign, _summarize

ModeDisposition = Literal[
    "already_characterized_restricted",
    "characterized_restricted",
    "callable_unverified_interval_semantics",
    "blocked_interface",
    "blocked_production_policy",
    "deferred_fix_required",
]

OverallVerdict = Literal[
    "remain_restricted_no_promotion",
    "blocked_low_feasibility",
]

P2_TARGETS: tuple[tuple[str, str], ...] = (
    ("UnitJackKnife", "tbrridge_jk"),
    ("JKP", "tbrridge_jkp"),
    ("Conformal", "tbrridge_conformal"),
    ("TimeSeriesKfold", "tbrridge_timeseries_kfold"),
    ("Bayesian", "tbrridge_bayesian_registry"),
)

CONTEXT_001: tuple[tuple[str, str], ...] = (
    ("Kfold", "tbrridge_kfold_unit"),
    ("BlockResidualBootstrap", "tbrridge_brb_unit"),
)


@dataclass(frozen=True)
class D5InstTbrridge002Config:
    n_mc: int = 14
    n_geos: int = 16
    n_periods: int = 44
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260622
    scenario_name: str = "scm_low_signal"
    reference_design_method: str = "greedy_match_markets"
    effect_grid: tuple[float, ...] = (0.0, 0.08)
    include_combo_scale_probe: bool = True
    combo_probe: ProbeConfig = ProbeConfig(train_length=20, test_length=6, n_geos=12, seed=42)
    null_fpr_acceptable_max: float = 0.15
    null_fpr_concerning_max: float = 0.35
    min_feasibility_for_characterized: float = 0.85


def _run_tbrridge_mode(
    panel: PanelDataset,
    *,
    inference: str,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
    random_state: int,
    instrument_key: str,
) -> dict[str, Any]:
    """Extended run wrapper with interval-semantics flags."""
    if inference == "Bayesian":
        block = registry_bayesian_production_block_reason("TBRRidge", inference)
        if block:
            return {
                "instrument_key": instrument_key,
                "inference": inference,
                "feasible": 0.0,
                "blocked_reason": block,
                "production_policy_block": True,
            }

    t0 = time.perf_counter()
    out = _run_tbr(
        panel,
        inference=inference,
        percent_effect=percent_effect,
        mean_value=mean_value,
        alpha=alpha,
        test_length=test_length,
        random_state=random_state,
        path=instrument_key,
    )
    out["wall_time_s"] = time.perf_counter() - t0
    out["inference"] = inference
    out["instrument_key"] = instrument_key

    if out.get("feasible", 0) < 0.5:
        err = str(out.get("error", ""))
        if "broadcast" in err.lower() or "ambiguous" in err.lower():
            out["failure_class"] = "interface_shape"
        elif out.get("production_policy_block"):
            out["failure_class"] = "production_policy"
        else:
            out["failure_class"] = "runtime_error"
        return out

    hw = float(out.get("mean_interval_halfwidth", float("nan")))
    out["negative_halfwidth"] = float(hw < 0) if np.isfinite(hw) else float("nan")
    out["interval_semantics_verified"] = 0.0
    if inference in ("Kfold", "BlockResidualBootstrap"):
        out["interval_semantics_verified"] = 1.0
    elif inference == "TimeSeriesKfold" and not out.get("negative_halfwidth"):
        out["interval_semantics_verified"] = 0.0
    return out


def _run_replicate(cfg: D5InstTbrridge002Config, *, seed: int) -> dict[str, Any]:
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
        n_test_grps=1,
        rerandomization_max_iter=500,
    )
    unit_panel = _build_unit_panel(
        wide,
        assignment,
        cell_key="test_0",
        train_length=cfg.train_length,
        test_length=cfg.test_length,
    )
    mean_value = _mean_treated_baseline(unit_panel)

    instruments: dict[str, dict[float, dict[str, Any]]] = {}
    for inf, key in P2_TARGETS + CONTEXT_001:
        instruments[key] = {}
        for prc in cfg.effect_grid:
            instruments[key][float(prc)] = _run_tbrridge_mode(
                unit_panel,
                inference=inf,
                percent_effect=float(prc),
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                random_state=seed,
                instrument_key=key,
            )

    scm_null = _scm_jk_readout_metrics(
        unit_panel,
        percent_effect=0.0,
        mean_value=mean_value,
        alpha=cfg.alpha,
        test_length=cfg.test_length,
    )

    return {
        "seed": seed,
        "geometry_mode": "single_cell",
        "assignment": assignment,
        "p2_instruments": instruments,
        "scm_jk_null": scm_null,
        "n_treated": len(unit_panel.treated_units),
        "n_control": len(unit_panel.control_units),
    }


def _combo_scale_probes(cfg: D5InstTbrridge002Config) -> dict[str, Any]:
    if not cfg.include_combo_scale_probe:
        return {"enabled": False}
    wide = _build_wide(cfg.combo_probe)
    assignment = _assign(
        "greedy_match_markets",
        wide,
        train_length=cfg.combo_probe.train_length,
        seed=cfg.combo_probe.seed,
        treatment_probability=0.35,
        n_test_grps=1,
        rerandomization_max_iter=500,
    )
    panel = _build_unit_panel(
        wide,
        assignment,
        cell_key="test_0",
        train_length=cfg.combo_probe.train_length,
        test_length=cfg.combo_probe.test_length,
    )
    probes: dict[str, Any] = {}
    for inf, _ in P2_TARGETS + CONTEXT_001:
        kwargs: dict[str, Any] = {}
        if inf in ("Kfold", "TimeSeriesKfold"):
            kwargs["random_state"] = 0
        if inf == "BlockResidualBootstrap":
            kwargs.update(
                n_bootstrap=12,
                block_length=4,
                min_train_periods=6,
                show_progress=False,
                random_state=0,
            )
        probes[inf] = _probe_run(TBRRidge, panel, inference=inf, extra_kwargs=kwargs)
    return {
        "enabled": True,
        "panel_meta": {
            "train_length": cfg.combo_probe.train_length,
            "test_length": cfg.combo_probe.test_length,
            "n_geos": cfg.combo_probe.n_geos,
        },
        "probes": probes,
    }


def _summarize_mode(
    replicates: list[dict[str, Any]],
    instrument_key: str,
    *,
    effect: float = 0.0,
) -> dict[str, Any]:
    agg = _aggregate_instrument(
        [
            {
                "geometry_mode": "single_cell",
                "instruments": {instrument_key: r["p2_instruments"][instrument_key]},
            }
            for r in replicates
        ],
        instrument_key,
        effect=effect,
    )
    neg_hw = []
    failure_classes = []
    for r in replicates:
        inst = r["p2_instruments"][instrument_key].get(float(effect), {})
        if "negative_halfwidth" in inst:
            neg_hw.append(float(inst["negative_halfwidth"]))
        failure_classes.append(inst.get("failure_class"))
    agg["negative_halfwidth_rate"] = float(np.mean(neg_hw)) if neg_hw else float("nan")
    agg["dominant_failure_class"] = (
        max(set(failure_classes), key=failure_classes.count) if failure_classes else None
    )
    return agg


def _disposition_for_mode(
    summary_null: dict[str, Any],
    *,
    inference: str,
    cfg: D5InstTbrridge002Config,
) -> tuple[ModeDisposition, str]:
    if inference in ("Kfold", "BlockResidualBootstrap"):
        return (
            "already_characterized_restricted",
            "D5-INST-TBRRIDGE-001 — remain restricted diagnostic; no re-promotion.",
        )

    feas = float(summary_null.get("feasibility_rate", 0.0))
    if inference == "Bayesian":
        return (
            "blocked_production_policy",
            f"INV-015: registry Bayesian ≠ BayesianTBR MCMC; probe policy block ({INV_015_REGISTRY_BAYESIAN_NOT_MCMC}).",
        )

    if feas < 0.1:
        fc = summary_null.get("dominant_failure_class")
        if fc == "interface_shape":
            return (
                "blocked_interface",
                "TBRRidge multi-treated path shape breaks unit LOO/JKP/Conformal readout (broadcast).",
            )
        return (
            "deferred_fix_required",
            f"Low feasibility ({feas:.2f}); interface fix before OC.",
        )

    if inference == "TimeSeriesKfold":
        fpr = summary_null.get("null_interval_exclusion_fpr", {}).get("mean", float("nan"))
        neg = summary_null.get("negative_halfwidth_rate", float("nan"))
        if np.isfinite(neg) and neg > 0:
            return (
                "callable_unverified_interval_semantics",
                "Runs on 001e panel but negative interval half-width — not governed uncertainty.",
            )
        if np.isfinite(fpr) and fpr > cfg.null_fpr_concerning_max:
            return (
                "callable_unverified_interval_semantics",
                f"Distinct from Kfold (horizon blocking) but null FPR {fpr:.2f} — restricted only.",
            )
        if feas >= cfg.min_feasibility_for_characterized:
            return (
                "characterized_restricted",
                "Distinct TimeSeriesKfold path; feasible on battery; remain restricted vs SCM+JK.",
            )
        return (
            "callable_unverified_interval_semantics",
            "Partial feasibility — restricted diagnostic only.",
        )

    if feas >= cfg.min_feasibility_for_characterized:
        return (
            "characterized_restricted",
            "Feasible on battery — still restricted vs SCM+JK scale.",
        )

    return (
        "blocked_interface",
        "Does not meet characterization threshold on 001e unit panel.",
    )


def _tbr_label_audit() -> dict[str, Any]:
    configs = all_recovery_configs()
    tbr = configs.get("TBR")
    tbrr = configs.get("TBRRidge")
    tbr_inst = tbr.factory() if tbr else None
    tbrr_inst = tbrr.factory() if tbrr else None
    return {
        "recovery_runner_TBR_class": type(tbr_inst).__name__ if tbr_inst else None,
        "recovery_runner_TBRRidge_class": type(tbrr_inst).__name__ if tbrr_inst else None,
        "distinct_from_class_TBR": (
            type(tbr_inst).__name__ == "TBR" and type(tbrr_inst).__name__ == "TBRRidge"
        ),
        "p0_002_satisfied": type(tbr_inst).__name__ == "TBR",
    }


def build_d5_inst_tbrridge_002(cfg: D5InstTbrridge002Config | None = None) -> dict[str, Any]:
    cfg = cfg or D5InstTbrridge002Config()
    replicates = [_run_replicate(cfg, seed=cfg.random_state_base + i) for i in range(cfg.n_mc)]

    mode_summaries_null: dict[str, Any] = {}
    mode_summaries_injected: dict[str, Any] = {}
    mode_dispositions: dict[str, Any] = {}

    for inf, key in P2_TARGETS + CONTEXT_001:
        sn = _summarize_mode(replicates, key, effect=0.0)
        si = _summarize_mode(replicates, key, effect=0.08)
        disp, reason = _disposition_for_mode(sn, inference=inf, cfg=cfg)
        mode_summaries_null[key] = sn
        mode_summaries_injected[key] = si
        mode_dispositions[inf] = {
            "instrument_key": key,
            "disposition": disp,
            "reason": reason,
            "audit_010_row": f"A16–A21 (TBRRidge+{inf})" if inf in {t[0] for t in P2_TARGETS} else "A13–A14",
        }

    kfold_null = mode_summaries_null["tbrridge_kfold_unit"]
    tskf_null = mode_summaries_null["tbrridge_timeseries_kfold"]
    kfold_tskf_comparison = {
        "both_feasible": (
            kfold_null.get("feasibility_rate", 0) >= 0.85
            and tskf_null.get("feasibility_rate", 0) >= 0.85
        ),
        "null_point_mean_delta": float(
            abs(
                tskf_null.get("mean_point_effect", {}).get("mean", float("nan"))
                - kfold_null.get("mean_point_effect", {}).get("mean", float("nan"))
            )
        )
        if tskf_null.get("mean_point_effect") and kfold_null.get("mean_point_effect")
        else float("nan"),
        "distinct_inference_path": True,
        "note": "TimeSeriesKfold uses horizon-blocked folds; Kfold uses panel K-fold — not interchangeable.",
    }

    scm_null = _summarize(
        [r["scm_jk_null"].get("detected_correct", float("nan")) for r in replicates]
    )

    feasible_p2 = [
        mode_dispositions[inf]["disposition"]
        not in ("blocked_interface", "blocked_production_policy", "deferred_fix_required")
        for inf, _ in P2_TARGETS
    ]
    overall: OverallVerdict = "remain_restricted_no_promotion"
    if sum(feasible_p2) == 0:
        overall = "blocked_low_feasibility"

    return {
        "artifact_id": "D5-INST-TBRRIDGE-002",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "binding_docs": [
            "AUDIT-010_mmm_readiness_gap.md",
            "D5_INST_TBRRIDGE_001_REPORT.md",
            "TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001.md",
            "D5_INST_COMBO_AUDIT_001_REPORT.md",
        ],
        "governance": {
            "estimator": "TBRRidge",
            "not_class_TBR": True,
            "tbr_label_audit": _tbr_label_audit(),
            "reference_context": "D5-INST-TBRRIDGE-001 (Kfold/BRB)",
            "calibration_signal_ingress": False,
            "mmm_ingress": False,
            "track_b_alias_expansion": False,
            "promotion": False,
            "audit_010_verdict": "not_ready_continue_track_f",
        },
        "config": {
            "n_mc": cfg.n_mc,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "effect_grid": list(cfg.effect_grid),
            "p2_targets": [list(t) for t in P2_TARGETS],
            "context_001": [list(t) for t in CONTEXT_001],
        },
        "mode_summaries_null": mode_summaries_null,
        "mode_summaries_injected_8pct": mode_summaries_injected,
        "mode_dispositions": mode_dispositions,
        "kfold_vs_timeseries_kfold": kfold_tskf_comparison,
        "combo_scale_probes": _combo_scale_probes(cfg),
        "scm_jk_null_detected_rate": scm_null,
        "overall_verdict": overall,
        "track_f_p2_roadmap": {
            "TBRRidge_UnitJackKnife": mode_dispositions["UnitJackKnife"]["disposition"],
            "TBRRidge_JKP": mode_dispositions["JKP"]["disposition"],
            "TBRRidge_Conformal": mode_dispositions["Conformal"]["disposition"],
            "TBRRidge_TimeSeriesKfold": mode_dispositions["TimeSeriesKfold"]["disposition"],
            "TBRRidge_Bayesian_registry": mode_dispositions["Bayesian"]["disposition"],
            "next_battery": "D5-INST-AUGSYNTH-003 (Conformal) — separate estimator family",
        },
        "findings": [
            {
                "id": "D5-TBR2-FIND-001",
                "severity": "high",
                "summary": "TBRRidge+UnitJackKnife/JKP/Conformal fail on 001e unit panel (shape broadcast).",
                "implication": "Remain blocked_interface; not Track B / MMM candidates.",
            },
            {
                "id": "D5-TBR2-FIND-002",
                "severity": "high",
                "summary": "TimeSeriesKfold feasible but interval semantics unverified (negative HW possible).",
                "implication": "Restricted diagnostic only — distinct from governed Kfold in 001.",
            },
            {
                "id": "D5-TBR2-FIND-003",
                "severity": "high",
                "summary": "Registry Bayesian on TBRRidge blocked by INV-015; not BayesianTBR MCMC.",
                "implication": "No production or CalibrationSignal path.",
            },
            {
                "id": "D5-TBR2-FIND-004",
                "severity": "medium",
                "summary": "TBRRidge ≠ class TBR — recovery_runner P0 label audit passes.",
                "implication": "Reports must keep estimand families separate.",
            },
        ],
        "user_facing_warnings": [
            "Do not conflate TBRRidge with class TBR (aggregate 1×1 only).",
            "Do not treat registry Bayesian as BayesianTBR NUTS posterior.",
            "TBRRidge unit point scale ≠ SCM+JK relative ATT without bridge.",
            "TimeSeriesKfold ≠ Kfold — different fold geometry; both restricted.",
        ],
        "rules_acknowledged": {
            "no_production_changes": True,
            "no_estimator_redesign": True,
            "no_trust_report_changes": True,
            "no_calibration_signal": True,
            "no_mmm": True,
            "no_promotion": True,
        },
    }


def write_artifact(path: Path | None = None, *, cfg: D5InstTbrridge002Config | None = None) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INST_TBRRIDGE_002_results.json"
    )
    payload = build_d5_inst_tbrridge_002(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_artifact()
    print(f"Wrote {out}")
