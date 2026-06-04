"""D5-INF-AUGSYNTH-JK-CALIBRATION-001 — AugSynth+UnitJackKnife inference calibration.

Characterizes null FPR, effect coverage, interval width, false-confidence behavior,
and diagnostic-conditioned inference vs A26 SCM+UnitJackKnife after ASCM-003.

No promotion, no governed-uncertainty allowlist change, no inference behavior change.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.methods.scm import AugSynthCVXPY
from panel_exp.panel_data import PanelDataset
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.scm_augsynth_diagnostics import (
    INSTRUMENT_DIAGNOSTIC_FIELDS,
    PANEL_DIAGNOSTIC_FIELDS,
    compute_instrument_diagnostics,
    compute_method_disagreement,
)
from panel_exp.validation.track_d_d5_inst_augsynth_001 import (
    _build_unit_panel,
    _inject_percent_effect,
    _mean_treated_baseline,
    _post_window_arrays,
)
from panel_exp.validation.track_d_d5_inst_augsynth_ascm_003 import (
    FIDELITY_CAVEATS,
    INSIDE_HULL_FIT_CLASSES,
    OUTSIDE_HULL_FIT_CLASSES,
    WORLD_REGISTRY_003,
    Ascm003WorldSpec,
    _panel_strengthening_diagnostics,
)
from panel_exp.validation.track_d_d5_pow_001b import _scm_jk_readout_metrics
from panel_exp.validation.track_d_d5_pow_001e import _assign, _summarize
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

OverallVerdict = Literal[
    "jk_not_ready",
    "jk_safe_but_conservative",
    "jk_promising_needs_more_oc",
    "jk_unsafe_under_diagnostics",
    "jk_calibration_candidate_future_only",
]

JK_ARMS: tuple[str, ...] = (
    "a26_scm_unit_jackknife",
    "augsynth_cvxpy_unit_jackknife",
)

CALIBRATION_EFFECT: float = 0.08
NARROW_HW_THRESHOLD: float = 0.015
POOR_FIT_RMSE_THRESHOLD: float = 2.5
HIGH_HULL_Z_THRESHOLD: float = 2.0
NULL_FPR_UNSAFE: float = 0.15
CONSERVATIVE_HW_RATIO: float = 1.35


@dataclass(frozen=True)
class D5InfAugsynthJkCalibration001Config:
    n_mc: int = 8
    train_length: int = 28
    test_length: int = 8
    n_periods: int = 44
    alpha: float = 0.05
    random_state_base: int = 20260801
    reference_design_method: str = "greedy_match_markets"
    min_donors_augsynth: int = 5
    worlds: tuple[Ascm003WorldSpec, ...] = WORLD_REGISTRY_003
    material_point_mismatch_threshold: float = 0.05
    calibration_effect: float = CALIBRATION_EFFECT
    n_mc_reduction_reason: str | None = None
    prior_artifact_id: str = "D5-INST-AUGSYNTH-ASCM-003"
    prior_artifact_verdict: str = "promising_needs_inference_calibration"


def _injected_mean_level(percent_effect: float, mean_value: np.ndarray) -> float:
    return float(percent_effect * np.mean(mean_value))


def _normalize_jk_readout(
    raw: dict[str, Any],
    *,
    percent_effect: float,
    mean_value: np.ndarray,
) -> dict[str, Any]:
    out = dict(raw)
    target = _injected_mean_level(percent_effect, mean_value)
    lo = out.get("mean_effect_lo")
    hi = out.get("mean_effect_hi")
    if lo is not None and hi is not None and np.isfinite(lo) and np.isfinite(hi):
        out["covers_injected_effect"] = float(lo <= target <= hi)
    elif abs(percent_effect) < 1e-12:
        out["covers_injected_effect"] = out.get("covers_zero_correct", float("nan"))
    else:
        out["covers_injected_effect"] = float("nan")
    hw = out.get("mean_interval_halfwidth")
    if hw is None or not np.isfinite(hw):
        hw = out.get("mean_jk_halfwidth")
    out["mean_interval_halfwidth"] = hw
    det = out.get("detected_interval_excludes_zero")
    if det is None:
        det = out.get("detected_correct")
    out["null_interval_exclusion_fpr"] = det
    out["effect_recovery_mae"] = (
        abs(float(out.get("mean_point_effect", float("nan"))) - percent_effect)
        if np.isfinite(out.get("mean_point_effect", float("nan")))
        else float("nan")
    )
    return out


def _augsynth_jk_calibration_readout(
    panel: PanelDataset,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
    min_donors: int,
    lambda_reg: float,
) -> dict[str, Any]:
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    out: dict[str, Any] = {
        "instrument_id": "AugSynthCVXPY_UnitJackKnife",
        "percent_effect": float(percent_effect),
        "feasible": 0.0,
        "blocked_reason": None,
        "augsynth_lambda_reg_used": float(lambda_reg),
    }
    if len(pds.control_units) < min_donors:
        out["blocked_reason"] = f"insufficient_donors_need_{min_donors}"
        return out
    skip = cvxpy_osqp_skip_reason()
    if skip:
        out["blocked_reason"] = skip
        return out
    try:
        est = AugSynthCVXPY(
            inference="UnitJackKnife",
            alpha=alpha,
            min_donors=min_donors,
            lambda_reg=lambda_reg,
        )
        est.run_analysis(pds)
        out["feasible"] = 1.0
    except Exception as exc:
        out["blocked_reason"] = str(exc)[:240]
        return out
    y, y_hat, y_lo, y_hi = _post_window_arrays(est.results or {}, test_length)
    effect = y - y_hat
    effect_lo = y - y_hi
    effect_hi = y - y_lo
    jk_hw = (y_hi - y_lo) / 2.0
    out.update(
        {
            "mean_point_effect": float(np.mean(effect)),
            "mean_effect_lo": float(np.mean(effect_lo)),
            "mean_effect_hi": float(np.mean(effect_hi)),
            "mean_jk_halfwidth": float(np.mean(jk_hw)),
            "covers_zero_correct": float(np.mean(effect_lo) <= 0.0 <= np.mean(effect_hi)),
            "detected_correct": float(
                not (np.mean(effect_lo) <= 0.0 <= np.mean(effect_hi))
            ),
            "detected_interval_excludes_zero": float(
                not (np.mean(effect_lo) <= 0.0 <= np.mean(effect_hi))
            ),
        }
    )
    return _normalize_jk_readout(out, percent_effect=percent_effect, mean_value=mean_value)


def _a26_jk_calibration_readout(
    panel: PanelDataset,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
) -> dict[str, Any]:
    raw = _scm_jk_readout_metrics(
        panel,
        percent_effect=percent_effect,
        mean_value=mean_value,
        alpha=alpha,
        test_length=test_length,
    )
    raw["instrument_id"] = "A26_SCM_UnitJackKnife"
    raw["feasible"] = 1.0
    return _normalize_jk_readout(raw, percent_effect=percent_effect, mean_value=mean_value)


def _false_confidence_breakdown(
    inst: dict[str, Any],
    diagnostics: dict[str, Any],
    conflict: dict[str, Any],
) -> dict[str, float]:
    hw_raw = inst.get("mean_interval_halfwidth")
    try:
        hw = float(hw_raw) if hw_raw is not None else float("nan")
    except (TypeError, ValueError):
        hw = float("nan")
    narrow = bool(np.isfinite(hw) and hw < NARROW_HW_THRESHOLD)
    scm_rmse = float(diagnostics.get("scm_pre_rmse", float("nan")))
    hull_z = float(diagnostics.get("hull_min_donor_z_distance", float("nan")))
    poor_fit = bool(
        inst.get("narrow_interval_poor_fit_flag")
        or (np.isfinite(scm_rmse) and scm_rmse >= POOR_FIT_RMSE_THRESHOLD)
    )
    high_stress = bool(np.isfinite(hull_z) and hull_z >= HIGH_HULL_Z_THRESHOLD)
    high_disagreement = bool(conflict.get("null_material_point_mismatch"))
    return {
        "narrow_interval_flag": float(narrow),
        "false_conf_narrow_poor_prefit": float(narrow and poor_fit),
        "false_conf_narrow_high_donor_stress": float(narrow and high_stress),
        "false_conf_narrow_high_disagreement": float(narrow and high_disagreement),
    }


def _run_calibration_replicate(
    world: Ascm003WorldSpec,
    cfg: D5InfAugsynthJkCalibration001Config,
    *,
    seed: int,
) -> dict[str, Any]:
    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY[world.scenario_name],
        random_state=seed,
        n_geos=world.n_geos,
        n_periods=cfg.n_periods,
        treatment_start=cfg.train_length,
        true_effect=0.0,
        **world.scenario_overrides,
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data

    if world.use_scenario_treated_units and scenario.treated_units:
        treated = [u for u in scenario.treated_units if u in wide.index]
        control = [u for u in wide.index if u not in treated]
        assignment = {"control": control, "test_0": treated}
    else:
        assignment = _assign(
            cfg.reference_design_method,
            wide,
            train_length=cfg.train_length,
            seed=seed,
            treatment_probability=world.treatment_probability,
            n_test_grps=world.n_test_grps,
            rerandomization_max_iter=500,
        )

    panel = _build_unit_panel(
        wide,
        assignment,
        cell_key="test_0",
        train_length=cfg.train_length,
        test_length=cfg.test_length,
    )
    mean_value = _mean_treated_baseline(panel)
    diagnostics = _panel_strengthening_diagnostics(
        panel,
        train_length=cfg.train_length,
        test_length=cfg.test_length,
        min_donors=cfg.min_donors_augsynth,
        alpha=cfg.alpha,
    )

    instruments: dict[str, dict[float, dict[str, Any]]] = {arm: {} for arm in JK_ARMS}
    for prc in world.effect_grid:
        pe = float(prc)
        a26 = _a26_jk_calibration_readout(
            panel,
            percent_effect=pe,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
        )
        aug = _augsynth_jk_calibration_readout(
            panel,
            percent_effect=pe,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            min_donors=cfg.min_donors_augsynth,
            lambda_reg=world.augsynth_lambda_reg,
        )
        instruments["a26_scm_unit_jackknife"][pe] = a26
        instruments["augsynth_cvxpy_unit_jackknife"][pe] = aug

    null_a26 = instruments["a26_scm_unit_jackknife"].get(0.0, {})
    null_aug = instruments["augsynth_cvxpy_unit_jackknife"].get(0.0, {})
    conflict = compute_method_disagreement(
        null_a26,
        null_aug,
        material_point_mismatch_threshold=cfg.material_point_mismatch_threshold,
    )

    for arm in JK_ARMS:
        for pe in world.effect_grid:
            inst = instruments[arm][float(pe)]
            inst.update(compute_instrument_diagnostics(inst, diagnostics))
            inst.update(_false_confidence_breakdown(inst, diagnostics, conflict))

    return {
        "seed": seed,
        "world_id": world.world_id,
        "fit_class": world.fit_class,
        "weak_fit_severity": world.weak_fit_severity,
        "augsynth_lambda_reg": world.augsynth_lambda_reg,
        "diagnostics": diagnostics,
        "conflict_vs_a26": conflict,
        "instruments": instruments,
    }


def _aggregate_jk_metrics(
    replicates: list[dict[str, Any]],
    *,
    world_id: str | None,
    arm: str,
    effect: float,
    stratum_filter: Any | None = None,
) -> dict[str, Any]:
    vals: dict[str, list[float]] = {
        "null_interval_exclusion_fpr": [],
        "covers_injected_effect": [],
        "mean_interval_halfwidth": [],
        "effect_recovery_mae": [],
        "false_confidence_flag": [],
        "false_conf_narrow_poor_prefit": [],
        "false_conf_narrow_high_donor_stress": [],
        "false_conf_narrow_high_disagreement": [],
        "feasible": [],
    }
    for rep in replicates:
        if world_id is not None and rep["world_id"] != world_id:
            continue
        if stratum_filter is not None and not stratum_filter(rep):
            continue
        inst = rep["instruments"].get(arm, {}).get(float(effect), {})
        if not inst:
            continue
        vals["feasible"].append(float(inst.get("feasible", 0.0)))
        for key in vals:
            if key == "feasible":
                continue
            v = inst.get(key)
            if v is not None and np.isfinite(v):
                vals[key].append(float(v))
    out: dict[str, Any] = {
        "world_id": world_id,
        "instrument": arm,
        "effect": effect,
        "n_replicates": len(vals["feasible"]),
        "feasibility_rate": float(np.mean(vals["feasible"])) if vals["feasible"] else 0.0,
    }
    for key, bucket in vals.items():
        if key == "feasible":
            continue
        out[key] = _summarize(bucket)
    return out


def _stratum_label(rep: dict[str, Any]) -> str:
    fit = rep.get("fit_class", "")
    if fit in OUTSIDE_HULL_FIT_CLASSES:
        return "outside_hull"
    if fit in INSIDE_HULL_FIT_CLASSES:
        return "inside_hull"
    return "other"


def _prefit_label(rep: dict[str, Any]) -> str:
    diag = rep.get("diagnostics", {})
    norm = float(diag.get("scm_pre_rmse_normalized", float("nan")))
    if not np.isfinite(norm):
        rmse = float(diag.get("scm_pre_rmse", float("nan")))
        return "poor_prefit" if np.isfinite(rmse) and rmse >= POOR_FIT_RMSE_THRESHOLD else "unknown_prefit"
    return "good_prefit" if norm < 1.0 else "poor_prefit"


def _donor_pool_label(rep: dict[str, Any]) -> str:
    fit = rep.get("fit_class", "")
    if "sparse" in fit:
        return "donor_sparse"
    if "rich" in fit:
        return "donor_rich"
    n_control = float(rep.get("diagnostics", {}).get("donor_sparsity_n_control", float("nan")))
    if np.isfinite(n_control):
        if n_control <= 8:
            return "donor_sparse"
        if n_control >= 18:
            return "donor_rich"
    return "donor_moderate"


def _weak_fit_label(rep: dict[str, Any]) -> str:
    sev = rep.get("weak_fit_severity")
    if sev:
        return f"weak_fit_{sev}"
    fit = rep.get("fit_class", "")
    if fit.startswith("weak_fit"):
        return "weak_fit_moderate"
    return "not_weak_fit"


def _diagnostic_strata_summary(
    replicates: list[dict[str, Any]],
    *,
    effect: float,
) -> dict[str, Any]:
    strata_defs: dict[str, Any] = {
        "prefit": _prefit_label,
        "hull": _stratum_label,
        "donor_pool": _donor_pool_label,
        "weak_fit_severity": _weak_fit_label,
    }
    out: dict[str, Any] = {}
    for stratum_name, fn in strata_defs.items():
        buckets: dict[str, dict[str, Any]] = {}
        labels = {fn(rep) for rep in replicates}
        for label in sorted(labels):
            filt = lambda rep, label=label, fn=fn: fn(rep) == label  # noqa: E731
            buckets[label] = {
                arm: _aggregate_jk_metrics(
                    replicates,
                    world_id=None,
                    arm=arm,
                    effect=effect,
                    stratum_filter=filt,
                )
                for arm in JK_ARMS
            }
        out[stratum_name] = buckets
    return out


def _compare_a26_vs_aug_jk(
    summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = []
    for s in summaries:
        if s["instrument"] != "augsynth_cvxpy_unit_jackknife":
            continue
        world_id = s["world_id"]
        effect = s["effect"]
        a26 = next(
            (
                x
                for x in summaries
                if x["world_id"] == world_id
                and x["instrument"] == "a26_scm_unit_jackknife"
                and x["effect"] == effect
            ),
            None,
        )
        if not a26:
            continue
        aug_fpr = (s.get("null_interval_exclusion_fpr") or {}).get("mean")
        a26_fpr = (a26.get("null_interval_exclusion_fpr") or {}).get("mean")
        aug_cov = (s.get("covers_injected_effect") or {}).get("mean")
        a26_cov = (a26.get("covers_injected_effect") or {}).get("mean")
        aug_hw = (s.get("mean_interval_halfwidth") or {}).get("mean")
        a26_hw = (a26.get("mean_interval_halfwidth") or {}).get("mean")
        aug_mae = (s.get("effect_recovery_mae") or {}).get("mean")
        a26_mae = (a26.get("effect_recovery_mae") or {}).get("mean")
        hw_ratio = (
            float(aug_hw / a26_hw)
            if np.isfinite(aug_hw) and np.isfinite(a26_hw) and a26_hw > 0
            else float("nan")
        )
        rows.append(
            {
                "world_id": world_id,
                "effect": effect,
                "a26_null_fpr": a26_fpr,
                "aug_null_fpr": aug_fpr,
                "a26_effect_coverage": a26_cov,
                "aug_effect_coverage": aug_cov,
                "a26_mean_halfwidth": a26_hw,
                "aug_mean_halfwidth": aug_hw,
                "aug_over_a26_hw_ratio": hw_ratio,
                "a26_mae": a26_mae,
                "aug_mae": aug_mae,
                "aug_beats_a26_mae": bool(
                    np.isfinite(a26_mae) and np.isfinite(aug_mae) and aug_mae < a26_mae
                ),
            }
        )
    null_rows = [r for r in rows if r["effect"] == 0.0]
    effect_rows = [r for r in rows if r["effect"] == CALIBRATION_EFFECT]
    unsafe_null = [
        r for r in null_rows if np.isfinite(r.get("aug_null_fpr") or float("nan")) and r["aug_null_fpr"] > NULL_FPR_UNSAFE
    ]
    return {
        "comparisons": rows,
        "unsafe_aug_null_fpr_worlds": [r["world_id"] for r in unsafe_null],
        "mean_aug_over_a26_hw_ratio_at_null": _summarize(
            [r["aug_over_a26_hw_ratio"] for r in null_rows if np.isfinite(r["aug_over_a26_hw_ratio"])]
        ),
        "mean_aug_over_a26_hw_ratio_at_effect": _summarize(
            [r["aug_over_a26_hw_ratio"] for r in effect_rows if np.isfinite(r["aug_over_a26_hw_ratio"])]
        ),
    }


def _false_confidence_summary(
    replicates: list[dict[str, Any]],
    *,
    arm: str,
    effect: float,
) -> dict[str, Any]:
    keys = (
        "false_confidence_flag",
        "false_conf_narrow_poor_prefit",
        "false_conf_narrow_high_donor_stress",
        "false_conf_narrow_high_disagreement",
    )
    out: dict[str, Any] = {"instrument": arm, "effect": effect}
    for key in keys:
        vals = []
        for rep in replicates:
            inst = rep["instruments"].get(arm, {}).get(float(effect), {})
            v = inst.get(key)
            if v is not None and np.isfinite(v):
                vals.append(float(v))
        out[key] = _summarize(vals)
    return out


def _decide_verdict(
    *,
    summaries: list[dict[str, Any]],
    comparison: dict[str, Any],
    diagnostic_strata: dict[str, Any],
    cfg: D5InfAugsynthJkCalibration001Config,
) -> tuple[OverallVerdict, list[dict[str, Any]]]:
    aug_null = [
        s
        for s in summaries
        if s["instrument"] == "augsynth_cvxpy_unit_jackknife" and s["effect"] == 0.0
    ]
    feas = [s["feasibility_rate"] for s in aug_null]
    mean_feas = float(np.mean(feas)) if feas else 0.0

    unsafe_worlds = comparison.get("unsafe_aug_null_fpr_worlds", [])
    hw_ratio = (comparison.get("mean_aug_over_a26_hw_ratio_at_null") or {}).get("mean")

    unsafe_strata: list[str] = []
    for stratum_name, buckets in diagnostic_strata.get("prefit", {}).items():
        aug = buckets.get("augsynth_cvxpy_unit_jackknife", {})
        fpr = (aug.get("null_interval_exclusion_fpr") or {}).get("mean")
        if np.isfinite(fpr) and fpr > NULL_FPR_UNSAFE:
            unsafe_strata.append(f"prefit:{stratum_name}")

    findings: list[dict[str, Any]] = [
        {
            "id": "D5-JKCAL-FIND-001",
            "summary": (
                f"JK calibration battery on {len(cfg.worlds)} ASCM-003 worlds "
                f"(n_mc={cfg.n_mc}) after {cfg.prior_artifact_id} "
                f"verdict `{cfg.prior_artifact_verdict}`."
            ),
        },
        {
            "id": "D5-JKCAL-FIND-002",
            "summary": (
                f"AugSynth+JK unsafe null-FPR worlds (>{NULL_FPR_UNSAFE}): "
                f"{len(unsafe_worlds)} — {unsafe_worlds[:5]}"
                + ("..." if len(unsafe_worlds) > 5 else "")
            ),
        },
    ]
    if cfg.n_mc_reduction_reason:
        findings.append(
            {
                "id": "D5-JKCAL-FIND-003",
                "severity": "info",
                "summary": f"n_mc={cfg.n_mc}; {cfg.n_mc_reduction_reason}",
            }
        )

    if mean_feas < 0.5:
        return "jk_not_ready", findings + [
            {
                "id": "D5-JKCAL-FIND-004",
                "severity": "high",
                "summary": f"AugSynth+JK feasibility {mean_feas:.2f} below 0.5.",
            }
        ]

    if unsafe_worlds or unsafe_strata:
        return "jk_unsafe_under_diagnostics", findings + [
            {
                "id": "D5-JKCAL-FIND-005",
                "severity": "high",
                "summary": "Elevated null FPR under one or more worlds/diagnostic strata.",
            }
        ]

    conservative = np.isfinite(hw_ratio) and hw_ratio >= CONSERVATIVE_HW_RATIO
    if conservative and not unsafe_worlds:
        return "jk_safe_but_conservative", findings + [
            {
                "id": "D5-JKCAL-FIND-006",
                "summary": (
                    f"Null FPR safe; AugSynth+JK intervals wider than A26 "
                    f"(mean HW ratio {hw_ratio:.2f})."
                ),
            }
        ]

    return "jk_promising_needs_more_oc", findings + [
        {
            "id": "D5-JKCAL-FIND-007",
            "summary": "Null FPR acceptable on available slice; coverage/width tradeoffs need larger n_mc.",
        }
    ]


def build_d5_inf_augsynth_jk_calibration_001(
    cfg: D5InfAugsynthJkCalibration001Config | None = None,
) -> dict[str, Any]:
    cfg = cfg or D5InfAugsynthJkCalibration001Config()
    t0 = time.perf_counter()
    replicates: list[dict[str, Any]] = []
    for world in cfg.worlds:
        for i in range(cfg.n_mc):
            seed = cfg.random_state_base + (hash(world.world_id) % 10_000) + i * 19
            replicates.append(_run_calibration_replicate(world, cfg, seed=seed))

    summaries: list[dict[str, Any]] = []
    for world in cfg.worlds:
        for arm in JK_ARMS:
            for effect in world.effect_grid:
                summaries.append(
                    _aggregate_jk_metrics(
                        replicates,
                        world_id=world.world_id,
                        arm=arm,
                        effect=float(effect),
                    )
                )

    diagnostic_strata_null = _diagnostic_strata_summary(replicates, effect=0.0)
    diagnostic_strata_effect = _diagnostic_strata_summary(
        replicates, effect=cfg.calibration_effect
    )
    comparison = _compare_a26_vs_aug_jk(summaries)
    false_conf_null = {
        arm: _false_confidence_summary(replicates, arm=arm, effect=0.0) for arm in JK_ARMS
    }
    false_conf_effect = {
        arm: _false_confidence_summary(replicates, arm=arm, effect=cfg.calibration_effect)
        for arm in JK_ARMS
    }
    overall, findings = _decide_verdict(
        summaries=summaries,
        comparison=comparison,
        diagnostic_strata=diagnostic_strata_null,
        cfg=cfg,
    )

    return {
        "artifact_id": "D5-INF-AUGSYNTH-JK-CALIBRATION-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime_seconds": time.perf_counter() - t0,
        "lane": "research",
        "binding_docs": [
            "AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001",
            "AUGSYNTH-ASCM-IMPLEMENTATION-FIDELITY-AUDIT-001",
            "D5_DIAG_SCM_AUGSYNTH_001_REPORT",
            "D5_INST_AUGSYNTH_ASCM_003_REPORT",
        ],
        "prior_evidence": {
            "artifact_id": cfg.prior_artifact_id,
            "verdict": cfg.prior_artifact_verdict,
        },
        "governance": {
            "no_promotion": True,
            "no_governed_uncertainty_allowlist_change": True,
            "no_eligibility_change": True,
            "no_threshold_finalization": True,
            "no_estimator_behavior_change": True,
            "no_inference_behavior_change": True,
            "no_trust_report_change": True,
            "no_f_decision_change": True,
            "no_calibration_signal_ingress": True,
            "no_mmm": True,
            "augsynth_jk_not_governed_uncertainty": True,
        },
        "fidelity_caveats": list(FIDELITY_CAVEATS),
        "config": {
            "n_mc": cfg.n_mc,
            "n_mc_target": 8,
            "n_mc_reduction_reason": cfg.n_mc_reduction_reason,
            "calibration_effect": cfg.calibration_effect,
            "world_ids": [w.world_id for w in cfg.worlds],
            "instrument_arms": list(JK_ARMS),
            "diagnostic_fields": {
                "panel": list(PANEL_DIAGNOSTIC_FIELDS),
                "instrument": list(INSTRUMENT_DIAGNOSTIC_FIELDS),
            },
        },
        "world_registry": [
            {
                "world_id": w.world_id,
                "fit_class": w.fit_class,
                "weak_fit_severity": w.weak_fit_severity,
                "effect_grid": list(w.effect_grid),
            }
            for w in cfg.worlds
        ],
        "replicates": replicates,
        "summaries_by_world_arm_effect": summaries,
        "null_fpr_summary": {
            arm: _aggregate_jk_metrics(
                replicates, world_id=None, arm=arm, effect=0.0
            )
            for arm in JK_ARMS
        },
        "effect_coverage_summary": {
            arm: _aggregate_jk_metrics(
                replicates,
                world_id=None,
                arm=arm,
                effect=cfg.calibration_effect,
            )
            for arm in JK_ARMS
        },
        "interval_width_summary": {
            "at_null": {
                arm: (s.get("mean_interval_halfwidth") or {})
                for arm, s in {
                    a: _aggregate_jk_metrics(replicates, world_id=None, arm=a, effect=0.0)
                    for a in JK_ARMS
                }.items()
            },
            "at_effect": {
                arm: (s.get("mean_interval_halfwidth") or {})
                for arm, s in {
                    a: _aggregate_jk_metrics(
                        replicates,
                        world_id=None,
                        arm=a,
                        effect=cfg.calibration_effect,
                    )
                    for a in JK_ARMS
                }.items()
            },
        },
        "false_confidence_summary": {
            "at_null": false_conf_null,
            "at_effect": false_conf_effect,
        },
        "diagnostic_strata": {
            "at_null": diagnostic_strata_null,
            "at_effect": diagnostic_strata_effect,
        },
        "a26_vs_aug_jk_comparison": comparison,
        "overall_verdict": overall,
        "findings": findings,
        "promotion_audit_eligible": False,
    }


def write_artifact(
    path: Path | None = None,
    *,
    cfg: D5InfAugsynthJkCalibration001Config | None = None,
) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INF_AUGSYNTH_JK_CALIBRATION_001_results.json"
    )
    payload = build_d5_inf_augsynth_jk_calibration_001(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


def write_report(
    results_path: Path | None = None,
    report_path: Path | None = None,
) -> Path:
    results_path = results_path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INF_AUGSYNTH_JK_CALIBRATION_001_results.json"
    )
    report_path = report_path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "D5_INF_AUGSYNTH_JK_CALIBRATION_001_REPORT.md"
    )
    p = json.loads(results_path.read_text(encoding="utf-8"))
    cfg = p.get("config", {})
    null_fpr = p.get("null_fpr_summary", {})
    effect_cov = p.get("effect_coverage_summary", {})
    comp = p.get("a26_vs_aug_jk_comparison", {})
    fc = p.get("false_confidence_summary", {})
    prior = p.get("prior_evidence", {})

    def _fmt(v: Any) -> str:
        if v is None or (isinstance(v, float) and not np.isfinite(v)):
            return "—"
        return str(v)

    def _mean(block: dict[str, Any], key: str) -> str:
        return _fmt((block.get(key) or {}).get("mean"))

    lines = [
        "# D5-INF-AUGSYNTH-JK-CALIBRATION-001 — AugSynth+UnitJackKnife inference calibration",
        "",
        f"**Artifact:** [`archives/D5_INF_AUGSYNTH_JK_CALIBRATION_001_results.json`](archives/D5_INF_AUGSYNTH_JK_CALIBRATION_001_results.json)  ",
        f"**Harness:** `panel_exp/validation/track_d_d5_inf_augsynth_jk_calibration_001.py`  ",
        "",
        f"**Overall verdict:** `{p.get('overall_verdict')}`  ",
        f"**Runtime (s):** `{float(p['runtime_seconds']):.1f}`  "
        if p.get("runtime_seconds") is not None
        else "**Runtime (s):** `—`  ",
        "",
        "## 1. Purpose",
        "",
        "Calibrate and characterize **AugSynth+UnitJackKnife** inference after "
        "ASCM-003 (`promising_needs_inference_calibration`). This PR does **not** promote "
        "AugSynth+JK or add it to governed uncertainty.",
        "",
        "## 2. Prior evidence from ASCM-003",
        "",
        f"- Prior artifact: `{prior.get('artifact_id')}`  ",
        f"- Prior verdict: `{prior.get('verdict')}`  ",
        "- AugSynth point showed partial weak-fit MAE gains; JK null FPR was 0.0 on weak-fit "
        "worlds in ASCM-003 slice but sample was small (`n_mc=4`).",
        "",
        "## 3. Design",
        "",
        f"- Monte Carlo: **n_mc={cfg.get('n_mc')}** (target 8+; reduction: {cfg.get('n_mc_reduction_reason') or 'none'})",
        f"- Worlds: **{len(p.get('world_registry', []))}** (ASCM-003 registry)",
        f"- Calibration effect: **{cfg.get('calibration_effect')}**",
        "- Arms: A26 SCM+UnitJackKnife vs AugSynth+UnitJackKnife only",
        "",
        "## 4. Worlds / strata",
        "",
        "Same 19-world ASCM-003 registry with weak-fit severity, hull, donor sparsity/richness, "
        "and ridge-λ worlds. Diagnostic strata: good/poor prefit, inside/outside hull, "
        "donor pool, weak-fit severity bands.",
        "",
        "## 5. Methods compared",
        "",
        "| Arm | Role |",
        "|-----|------|",
        "| `a26_scm_unit_jackknife` | Governed null-monitor reference |",
        "| `augsynth_cvxpy_unit_jackknife` | Calibration target (not promoted) |",
        "",
        "## 6. Diagnostics used",
        "",
        "D5-DIAG panel fields (`scm_pre_rmse`, `hull_min_donor_z_distance`, `fit_improvement_rmse`, …) "
        "plus instrument flags (`false_confidence_flag`, `narrow_interval_poor_fit_flag`) and "
        "null-world `conflict_vs_a26` disagreement.",
        "",
        "## 7. Null FPR",
        "",
        f"| arm | mean null interval-exclusion FPR |",
        f"|-----|----------------------------------|",
        f"| A26 JK | {_mean(null_fpr.get('a26_scm_unit_jackknife', {}), 'null_interval_exclusion_fpr')} |",
        f"| AugSynth JK | {_mean(null_fpr.get('augsynth_cvxpy_unit_jackknife', {}), 'null_interval_exclusion_fpr')} |",
        "",
        f"Unsafe AugSynth+JK worlds (FPR > {NULL_FPR_UNSAFE}): "
        f"`{comp.get('unsafe_aug_null_fpr_worlds', [])}`",
        "",
        "## 8. Effect coverage",
        "",
        f"@ {cfg.get('calibration_effect')} injection:",
        "",
        f"| arm | mean covers injected effect |",
        f"|-----|----------------------------|",
        f"| A26 JK | {_mean(effect_cov.get('a26_scm_unit_jackknife', {}), 'covers_injected_effect')} |",
        f"| AugSynth JK | {_mean(effect_cov.get('augsynth_cvxpy_unit_jackknife', {}), 'covers_injected_effect')} |",
        "",
        "## 9. Interval width / conservatism",
        "",
        f"- Mean AugSynth/A26 half-width ratio @ null: "
        f"`{_fmt((comp.get('mean_aug_over_a26_hw_ratio_at_null') or {}).get('mean'))}`",
        f"- Mean AugSynth/A26 half-width ratio @ effect: "
        f"`{_fmt((comp.get('mean_aug_over_a26_hw_ratio_at_effect') or {}).get('mean'))}`",
        f"- Conservative threshold ratio: `{CONSERVATIVE_HW_RATIO}`",
        "",
        "## 10. False-confidence behavior",
        "",
        "Rates for narrow interval + poor prefit, high donor stress, and high SCM/AugSynth disagreement:",
        "",
    ]
    for key in (
        "false_conf_narrow_poor_prefit",
        "false_conf_narrow_high_donor_stress",
        "false_conf_narrow_high_disagreement",
    ):
        aug = (fc.get("at_null", {}).get("augsynth_cvxpy_unit_jackknife", {}).get(key) or {})
        lines.append(
            f"- `{key}` (AugSynth JK @ null): mean `{_fmt(aug.get('mean'))}`"
        )
    lines.extend(
        [
            "",
            "## 11. Diagnostic-conditioned results",
            "",
            "See artifact `diagnostic_strata.at_null` and `diagnostic_strata.at_effect` for "
            "FPR, coverage, and half-width by prefit, hull, donor-pool, and weak-fit severity.",
            "",
            "## 12. Comparison to A26",
            "",
            "Per-world comparison in artifact `a26_vs_aug_jk_comparison.comparisons` "
            "(FPR, coverage, half-width, point MAE).",
            "",
            "## 13. Verdict",
            "",
            f"**`{p.get('overall_verdict')}`** — AugSynth+JK remains **diagnostic / not governed uncertainty**.",
            "",
            "## 14. Guardrails",
            "",
            "| Guardrail | Status |",
            "|-----------|--------|",
            "| Promotion | **No** |",
            "| Governed uncertainty allowlist | **No change** |",
            "| Threshold finalization | **No** |",
            "| Estimator / inference code change | **No** |",
            "",
            "## 15. Next step",
            "",
            "If `jk_safe_but_conservative`: continue comparator lane; optional larger-n OC. "
            "If `jk_promising_needs_more_oc`: extend n_mc and weak-fit strata before any "
            "calibration-candidate discussion. No promotion audit.",
            "",
            "## Findings",
            "",
        ]
    )
    for f in p.get("findings", []):
        sev = f.get("severity")
        prefix = f" ({sev})" if sev else ""
        lines.append(f"- **{f.get('id', 'FIND')}**{prefix}: {f.get('summary')}")
    lines.append("")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


if __name__ == "__main__":
    archive_cfg = D5InfAugsynthJkCalibration001Config(
        n_mc=4,
        n_mc_reduction_reason=(
            "19-world JK calibration grid runtime; harness default n_mc=8 for replay"
        ),
    )
    out = write_artifact(cfg=archive_cfg)
    rep = write_report(results_path=out)
    print(f"Wrote {out}")
    print(f"Wrote {rep}")
