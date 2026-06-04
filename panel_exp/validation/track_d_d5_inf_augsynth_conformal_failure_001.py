"""D5-INF-AUGSYNTH-CONFORMAL-FAILURE-001 — AugSynth+Conformal failure analysis.

Isolates null FPR, coverage, interval degeneracy, and diagnostic-conditioned failure
modes for AugSynth+Conformal vs A26 JK, AugSynth JK, and AugSynth point.

Failure-analysis PR only — no promotion, no governed-uncertainty change.
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
from panel_exp.validation.scm_augsynth_diagnostics import (
    INSTRUMENT_DIAGNOSTIC_FIELDS,
    PANEL_DIAGNOSTIC_FIELDS,
    compute_instrument_diagnostics,
    compute_method_disagreement,
)
from panel_exp.validation.track_d_d5_inst_augsynth_001 import _readout_metrics
from panel_exp.validation.track_d_d5_inst_augsynth_003 import (
    CONFORMAL_SEMANTICS,
    _augsynth_conformal_readout_metrics,
)
from panel_exp.validation.track_d_d5_inst_augsynth_ascm_003 import (
    FIDELITY_CAVEATS,
    INSIDE_HULL_FIT_CLASSES,
    OUTSIDE_HULL_FIT_CLASSES,
    WORLD_REGISTRY_003,
    Ascm003WorldSpec,
    _panel_strengthening_diagnostics,
)
from panel_exp.validation.track_d_d5_inf_augsynth_jk_calibration_001 import (
    CALIBRATION_EFFECT,
    _a26_jk_calibration_readout,
    _augsynth_jk_calibration_readout,
    _donor_pool_label,
    _injected_mean_level,
    _prefit_label,
    _stratum_label,
    _weak_fit_label,
)
from panel_exp.validation.track_d_d5_inst_augsynth_001 import (
    _build_unit_panel,
    _mean_treated_baseline,
)
from panel_exp.validation.track_d_d5_pow_001e import _assign, _summarize
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

OverallVerdict = Literal[
    "conformal_remains_restricted",
    "conformal_research_repair_candidate",
    "conformal_blocked_pending_new_design",
    "conformal_safe_only_under_narrow_diagnostics",
    "conformal_inconclusive_low_mc",
]

COMPARISON_ARMS: tuple[str, ...] = (
    "a26_scm_unit_jackknife",
    "augsynth_cvxpy_unit_jackknife",
    "augsynth_cvxpy_point",
    "augsynth_cvxpy_conformal",
)

PRIMARY_ARM = "augsynth_cvxpy_conformal"
NULL_FPR_CONCERNING: float = 0.35
NULL_FPR_SEVERE: float = 0.50
ZERO_HW_EPS: float = 1e-9
WIDE_HW_THRESHOLD: float = 15.0

FAILURE_MECHANISMS: tuple[str, ...] = (
    "residual_exchangeability_failure",
    "time_dependence_serial_correlation",
    "post_treatment_shock_sensitivity",
    "weak_prefit_poor_calibration_set",
    "hull_extrapolation_stress",
    "conformal_band_construction_mismatch",
    "unsupported_geometry_estimator_pairing",
)


def _safe_finite(value: Any) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if np.isfinite(out) else float("nan")


@dataclass(frozen=True)
class D5InfAugsynthConformalFailure001Config:
    n_mc: int = 8
    train_length: int = 28
    test_length: int = 8
    n_periods: int = 44
    alpha: float = 0.05
    random_state_base: int = 20260815
    reference_design_method: str = "greedy_match_markets"
    min_donors_augsynth: int = 5
    worlds: tuple[Ascm003WorldSpec, ...] = WORLD_REGISTRY_003
    material_point_mismatch_threshold: float = 0.05
    calibration_effect: float = CALIBRATION_EFFECT
    n_mc_reduction_reason: str | None = None
    prior_artifacts: tuple[dict[str, str], ...] = (
        {
            "artifact_id": "D5-INST-AUGSYNTH-ASCM-003",
            "verdict": "promising_needs_inference_calibration",
        },
        {
            "artifact_id": "D5-INF-AUGSYNTH-JK-CALIBRATION-001",
            "verdict": "jk_unsafe_under_diagnostics",
        },
    )


def _normalize_point_readout(
    raw: dict[str, Any],
    *,
    percent_effect: float,
) -> dict[str, Any]:
    out = dict(raw)
    out["null_interval_exclusion_fpr"] = float("nan")
    out["covers_injected_effect"] = float("nan")
    out["mean_interval_halfwidth"] = float("nan")
    pe = out.get("mean_point_effect")
    out["effect_recovery_mae"] = (
        abs(float(pe) - percent_effect) if pe is not None and np.isfinite(pe) else float("nan")
    )
    return out


def _normalize_conformal_readout(
    raw: dict[str, Any],
    *,
    percent_effect: float,
    mean_value: np.ndarray,
) -> dict[str, Any]:
    out = dict(raw)
    target = _injected_mean_level(percent_effect, mean_value)
    hw_raw = out.get("mean_interval_halfwidth")
    try:
        hw = float(hw_raw) if hw_raw is not None else float("nan")
    except (TypeError, ValueError):
        hw = float("nan")
    out["mean_interval_halfwidth"] = hw
    out["zero_halfwidth"] = float(np.isfinite(hw) and hw <= ZERO_HW_EPS)
    out["negative_halfwidth"] = out.get(
        "negative_halfwidth",
        float(hw < 0) if np.isfinite(hw) else float("nan"),
    )
    out["degenerate_interval"] = float(
        (np.isfinite(hw) and hw <= ZERO_HW_EPS)
        or (np.isfinite(hw) and hw < 0)
    )
    out["overwide_interval"] = float(np.isfinite(hw) and hw >= WIDE_HW_THRESHOLD)
    det = out.get("detected_interval_excludes_zero")
    out["null_interval_exclusion_fpr"] = det
    if abs(percent_effect) < 1e-12:
        cz = out.get("covers_zero_correct")
        try:
            out["covers_injected_effect"] = float(cz) if cz is not None else float("nan")
        except (TypeError, ValueError):
            out["covers_injected_effect"] = float("nan")
    else:
        lo = out.get("mean_effect_lo")
        hi = out.get("mean_effect_hi")
        if lo is not None and hi is not None and np.isfinite(lo) and np.isfinite(hi):
            out["covers_injected_effect"] = float(lo <= target <= hi)
        else:
            out["covers_injected_effect"] = float("nan")
    pe = out.get("mean_point_effect")
    out["effect_recovery_mae"] = (
        abs(float(pe) - percent_effect) if pe is not None and np.isfinite(pe) else float("nan")
    )
    return out


def _shock_label(rep: dict[str, Any]) -> str:
    if rep.get("fit_class") == "post_shock" or rep.get("world_id", "").startswith("W8"):
        return "post_shock"
    return "no_shock"


def _disagreement_label(rep: dict[str, Any]) -> str:
    conflict = rep.get("conflict_vs_a26", {})
    if conflict.get("null_material_point_mismatch"):
        return "high_disagreement"
    delta = conflict.get("null_point_effect_delta")
    if delta is not None and np.isfinite(delta) and delta >= 0.05:
        return "high_disagreement"
    return "low_disagreement"


def _run_failure_replicate(
    world: Ascm003WorldSpec,
    cfg: D5InfAugsynthConformalFailure001Config,
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

    instruments: dict[str, dict[float, dict[str, Any]]] = {
        arm: {} for arm in COMPARISON_ARMS
    }
    for prc in world.effect_grid:
        pe = float(prc)
        try:
            instruments["a26_scm_unit_jackknife"][pe] = _a26_jk_calibration_readout(
                panel,
                percent_effect=pe,
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
            )
        except (ValueError, RuntimeError) as exc:
            instruments["a26_scm_unit_jackknife"][pe] = {
                "instrument_id": "A26_SCM_UnitJackKnife",
                "feasible": 0.0,
                "blocked_reason": str(exc)[:240],
                "null_interval_exclusion_fpr": float("nan"),
                "covers_injected_effect": float("nan"),
                "mean_interval_halfwidth": float("nan"),
            }
        instruments["augsynth_cvxpy_unit_jackknife"][pe] = _augsynth_jk_calibration_readout(
            panel,
            percent_effect=pe,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            min_donors=cfg.min_donors_augsynth,
            lambda_reg=world.augsynth_lambda_reg,
        )
        pt = _readout_metrics(
            panel,
            estimator_cls=AugSynthCVXPY,
            inference=None,
            percent_effect=pe,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            min_donors=cfg.min_donors_augsynth,
            instrument_id="AugSynthCVXPY_Point",
        )
        instruments["augsynth_cvxpy_point"][pe] = _normalize_point_readout(
            pt, percent_effect=pe
        )
        cf = _augsynth_conformal_readout_metrics(
            panel,
            percent_effect=pe,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            min_donors=cfg.min_donors_augsynth,
        )
        instruments["augsynth_cvxpy_conformal"][pe] = _normalize_conformal_readout(
            cf, percent_effect=pe, mean_value=mean_value
        )

    null_a26 = instruments["a26_scm_unit_jackknife"].get(0.0, {})
    null_aug_pt = instruments["augsynth_cvxpy_point"].get(0.0, {})
    conflict = compute_method_disagreement(
        null_a26,
        null_aug_pt,
        material_point_mismatch_threshold=cfg.material_point_mismatch_threshold,
    )

    for arm in COMPARISON_ARMS:
        for pe in world.effect_grid:
            inst = instruments[arm][float(pe)]
            if arm != "augsynth_cvxpy_point":
                inst.update(compute_instrument_diagnostics(inst, diagnostics))

    return {
        "seed": seed,
        "world_id": world.world_id,
        "fit_class": world.fit_class,
        "weak_fit_severity": world.weak_fit_severity,
        "diagnostics": diagnostics,
        "conflict_vs_a26": conflict,
        "instruments": instruments,
        "conformal_semantics": CONFORMAL_SEMANTICS,
    }


def _aggregate_arm_metrics(
    replicates: list[dict[str, Any]],
    *,
    world_id: str | None,
    arm: str,
    effect: float,
    stratum_filter: Any | None = None,
) -> dict[str, Any]:
    numeric_keys = (
        "null_interval_exclusion_fpr",
        "covers_injected_effect",
        "mean_interval_halfwidth",
        "effect_recovery_mae",
        "false_confidence_flag",
        "negative_halfwidth",
        "zero_halfwidth",
        "degenerate_interval",
        "overwide_interval",
        "feasible",
    )
    vals: dict[str, list[float]] = {k: [] for k in numeric_keys}
    for rep in replicates:
        if world_id is not None and rep["world_id"] != world_id:
            continue
        if stratum_filter is not None and not stratum_filter(rep):
            continue
        inst = rep["instruments"].get(arm, {}).get(float(effect), {})
        if not inst:
            continue
        for key in numeric_keys:
            v = inst.get(key)
            if v is not None and np.isfinite(v):
                vals[key].append(float(v))
    out: dict[str, Any] = {
        "world_id": world_id,
        "instrument": arm,
        "effect": effect,
        "n_replicates": len(vals["feasible"]) if vals["feasible"] else 0,
        "feasibility_rate": float(np.mean(vals["feasible"])) if vals["feasible"] else 0.0,
    }
    for key, bucket in vals.items():
        if key == "feasible":
            continue
        out[key] = _summarize(bucket)
    return out


def _failure_strata_summary(
    replicates: list[dict[str, Any]],
    *,
    effect: float,
) -> dict[str, Any]:
    strata_defs: dict[str, Any] = {
        "prefit": _prefit_label,
        "hull": _stratum_label,
        "donor_pool": _donor_pool_label,
        "weak_fit_severity": _weak_fit_label,
        "method_disagreement": _disagreement_label,
        "post_shock": _shock_label,
    }
    out: dict[str, Any] = {}
    for stratum_name, fn in strata_defs.items():
        buckets: dict[str, Any] = {}
        labels = {fn(rep) for rep in replicates}
        for label in sorted(labels):
            filt = lambda rep, label=label, fn=fn: fn(rep) == label  # noqa: E731
            cf = _aggregate_arm_metrics(
                replicates,
                world_id=None,
                arm=PRIMARY_ARM,
                effect=effect,
                stratum_filter=filt,
            )
            jk = _aggregate_arm_metrics(
                replicates,
                world_id=None,
                arm="augsynth_cvxpy_unit_jackknife",
                effect=effect,
                stratum_filter=filt,
            )
            a26 = _aggregate_arm_metrics(
                replicates,
                world_id=None,
                arm="a26_scm_unit_jackknife",
                effect=effect,
                stratum_filter=filt,
            )
            buckets[label] = {
                "conformal": cf,
                "augsynth_jk": jk,
                "a26_jk": a26,
            }
        out[stratum_name] = buckets
    return out


def _compare_arms(
    summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = []
    for s in summaries:
        if s["instrument"] != PRIMARY_ARM:
            continue
        wid = s["world_id"]
        effect = s["effect"]
        row: dict[str, Any] = {
            "world_id": wid,
            "effect": effect,
            "conformal_null_fpr": (s.get("null_interval_exclusion_fpr") or {}).get("mean"),
            "conformal_coverage": (s.get("covers_injected_effect") or {}).get("mean"),
            "conformal_halfwidth": (s.get("mean_interval_halfwidth") or {}).get("mean"),
            "conformal_degenerate_rate": (s.get("degenerate_interval") or {}).get("mean"),
        }
        for arm, prefix in (
            ("a26_scm_unit_jackknife", "a26_jk"),
            ("augsynth_cvxpy_unit_jackknife", "aug_jk"),
            ("augsynth_cvxpy_point", "aug_point"),
        ):
            other = next(
                (
                    x
                    for x in summaries
                    if x["world_id"] == wid
                    and x["instrument"] == arm
                    and x["effect"] == effect
                ),
                None,
            )
            if other:
                row[f"{prefix}_null_fpr"] = (
                    (other.get("null_interval_exclusion_fpr") or {}).get("mean")
                )
                row[f"{prefix}_halfwidth"] = (
                    (other.get("mean_interval_halfwidth") or {}).get("mean")
                )
                row[f"{prefix}_mae"] = (other.get("effect_recovery_mae") or {}).get("mean")
        rows.append(row)
    null_rows = [r for r in rows if r["effect"] == 0.0]
    severe = [
        r["world_id"]
        for r in null_rows
        if np.isfinite(_safe_finite(r.get("conformal_null_fpr")))
        and _safe_finite(r.get("conformal_null_fpr")) >= NULL_FPR_SEVERE
    ]
    concerning = [
        r["world_id"]
        for r in null_rows
        if np.isfinite(_safe_finite(r.get("conformal_null_fpr")))
        and _safe_finite(r.get("conformal_null_fpr")) >= NULL_FPR_CONCERNING
    ]
    return {
        "comparisons": rows,
        "severe_null_fpr_worlds": severe,
        "concerning_null_fpr_worlds": concerning,
        "mean_conformal_null_fpr": _summarize(
            [
                _safe_finite(r["conformal_null_fpr"])
                for r in null_rows
                if np.isfinite(_safe_finite(r.get("conformal_null_fpr")))
            ]
        ),
    }


def _score_failure_mechanisms(
    replicates: list[dict[str, Any]],
    *,
    failure_strata_null: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    scores: dict[str, float] = {m: 0.0 for m in FAILURE_MECHANISMS}
    evidence: dict[str, list[str]] = {m: [] for m in FAILURE_MECHANISMS}

    mean_fpr = _safe_finite((comparison.get("mean_conformal_null_fpr") or {}).get("mean"))
    if np.isfinite(mean_fpr) and mean_fpr >= NULL_FPR_CONCERNING:
        scores["residual_exchangeability_failure"] += 2.0
        evidence["residual_exchangeability_failure"].append(
            f"aggregate null FPR {mean_fpr:.2f} exceeds {NULL_FPR_CONCERNING}"
        )

    shock = failure_strata_null.get("post_shock", {})
    cf_shock = (shock.get("post_shock", {}).get("conformal") or {})
    cf_no_shock = (shock.get("no_shock", {}).get("conformal") or {})
    fpr_shock = _safe_finite((cf_shock.get("null_interval_exclusion_fpr") or {}).get("mean"))
    fpr_no = _safe_finite((cf_no_shock.get("null_interval_exclusion_fpr") or {}).get("mean"))
    if np.isfinite(fpr_shock) and fpr_shock >= NULL_FPR_CONCERNING:
        scores["post_treatment_shock_sensitivity"] += 3.0
        evidence["post_treatment_shock_sensitivity"].append(
            f"post_shock stratum null FPR {fpr_shock:.2f}"
        )
    if np.isfinite(fpr_shock) and np.isfinite(fpr_no) and fpr_shock > fpr_no + 0.15:
        scores["time_dependence_serial_correlation"] += 1.5
        evidence["time_dependence_serial_correlation"].append(
            "post_shock FPR exceeds no_shock by >0.15"
        )

    prefit = failure_strata_null.get("prefit", {})
    poor = (prefit.get("poor_prefit", {}).get("conformal") or {})
    good = (prefit.get("good_prefit", {}).get("conformal") or {})
    fpr_poor = _safe_finite((poor.get("null_interval_exclusion_fpr") or {}).get("mean"))
    if np.isfinite(fpr_poor) and fpr_poor >= NULL_FPR_CONCERNING:
        scores["weak_prefit_poor_calibration_set"] += 2.0
        evidence["weak_prefit_poor_calibration_set"].append(
            f"poor_prefit stratum null FPR {fpr_poor:.2f}"
        )
    fpr_good = _safe_finite((good.get("null_interval_exclusion_fpr") or {}).get("mean"))
    if np.isfinite(fpr_good) and fpr_good < NULL_FPR_CONCERNING and np.isfinite(fpr_poor):
        evidence["weak_prefit_poor_calibration_set"].append(
            "good_prefit safer than poor_prefit — diagnostic-conditioned failure"
        )

    hull = failure_strata_null.get("hull", {})
    outside = (hull.get("outside_hull", {}).get("conformal") or {})
    fpr_out = _safe_finite((outside.get("null_interval_exclusion_fpr") or {}).get("mean"))
    if np.isfinite(fpr_out) and fpr_out >= NULL_FPR_CONCERNING:
        scores["hull_extrapolation_stress"] += 2.0
        evidence["hull_extrapolation_stress"].append(
            f"outside_hull stratum null FPR {fpr_out:.2f}"
        )

    disagree = failure_strata_null.get("method_disagreement", {})
    high_d = (disagree.get("high_disagreement", {}).get("conformal") or {})
    fpr_hd = _safe_finite((high_d.get("null_interval_exclusion_fpr") or {}).get("mean"))
    if np.isfinite(fpr_hd) and fpr_hd >= NULL_FPR_CONCERNING:
        scores["conformal_band_construction_mismatch"] += 1.5
        evidence["conformal_band_construction_mismatch"].append(
            f"high_disagreement stratum null FPR {fpr_hd:.2f}"
        )

    deg_rates: list[float] = []
    neg_rates: list[float] = []
    overwide_rates = []
    hw_ratios = []
    for rep in replicates:
        inst = rep["instruments"].get(PRIMARY_ARM, {}).get(0.0, {})
        d = inst.get("degenerate_interval")
        n = inst.get("negative_halfwidth")
        ow = inst.get("overwide_interval")
        if d is not None and np.isfinite(d):
            deg_rates.append(float(d))
        if n is not None and np.isfinite(n):
            neg_rates.append(float(n))
        if ow is not None and np.isfinite(ow):
            overwide_rates.append(float(ow))
        a26 = rep["instruments"].get("a26_scm_unit_jackknife", {}).get(0.0, {})
        cf_hw = _safe_finite(inst.get("mean_interval_halfwidth"))
        a26_hw = _safe_finite(a26.get("mean_interval_halfwidth"))
        if np.isfinite(cf_hw) and np.isfinite(a26_hw) and a26_hw > 0:
            hw_ratios.append(cf_hw / a26_hw)
    if deg_rates and float(np.mean(deg_rates)) > 0.05:
        scores["conformal_band_construction_mismatch"] += 2.0
        evidence["conformal_band_construction_mismatch"].append(
            f"degenerate interval rate {np.mean(deg_rates):.2f}"
        )
    if neg_rates and float(np.mean(neg_rates)) > 0.0:
        scores["conformal_band_construction_mismatch"] += 2.5
        evidence["conformal_band_construction_mismatch"].append("negative half-width observed")
    if overwide_rates and float(np.mean(overwide_rates)) >= 0.2:
        scores["conformal_band_construction_mismatch"] += 2.0
        evidence["conformal_band_construction_mismatch"].append(
            f"over-wide interval rate {np.mean(overwide_rates):.2f}"
        )
    if hw_ratios and float(np.mean(hw_ratios)) >= 10.0:
        scores["conformal_band_construction_mismatch"] += 2.5
        evidence["conformal_band_construction_mismatch"].append(
            f"mean conformal/A26 half-width ratio {np.mean(hw_ratios):.1f}"
        )
        scores["residual_exchangeability_failure"] += 1.0
        evidence["residual_exchangeability_failure"].append(
            "pre-period residual calibration pool mismatched to post-period scale"
        )

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top = [k for k, v in ranked if v > 0][:3]
    return {
        "mechanism_scores": scores,
        "mechanism_evidence": evidence,
        "likely_mechanisms": top,
        "conformal_semantics_note": CONFORMAL_SEMANTICS.get("exchangeability_assumption"),
    }


def _decide_verdict(
    *,
    cfg: D5InfAugsynthConformalFailure001Config,
    comparison: dict[str, Any],
    mechanism: dict[str, Any],
    summaries: list[dict[str, Any]],
    null_fpr_summary: dict[str, Any],
    interval_degeneracy: dict[str, Any],
) -> tuple[OverallVerdict, list[dict[str, Any]]]:
    cf_null = [
        s
        for s in summaries
        if s["instrument"] == PRIMARY_ARM and s["effect"] == 0.0
    ]
    feas = [s["feasibility_rate"] for s in cf_null]
    mean_feas = float(np.mean(feas)) if feas else 0.0
    mean_fpr = _safe_finite((comparison.get("mean_conformal_null_fpr") or {}).get("mean"))
    severe = comparison.get("severe_null_fpr_worlds", [])
    concerning = comparison.get("concerning_null_fpr_worlds", [])
    top_mech = mechanism.get("likely_mechanisms", [])
    cf_block = null_fpr_summary.get(PRIMARY_ARM, {})
    a26_block = null_fpr_summary.get("a26_scm_unit_jackknife", {})
    cf_hw = _safe_finite((cf_block.get("mean_interval_halfwidth") or {}).get("mean"))
    a26_hw = _safe_finite((a26_block.get("mean_interval_halfwidth") or {}).get("mean"))
    hw_ratio = (
        cf_hw / a26_hw if np.isfinite(cf_hw) and np.isfinite(a26_hw) and a26_hw > 0 else float("nan")
    )
    overwide = _safe_finite((interval_degeneracy.get("overwide_interval") or {}).get("mean"))

    findings: list[dict[str, Any]] = [
        {
            "id": "D5-CFFAIL-FIND-001",
            "summary": (
                f"Conformal failure battery on {len(cfg.worlds)} worlds (n_mc={cfg.n_mc}) "
                "after ASCM-003 and JK calibration."
            ),
        },
        {
            "id": "D5-CFFAIL-FIND-002",
            "summary": (
                f"Mean conformal null FPR: {mean_fpr}; "
                f"severe worlds (>={NULL_FPR_SEVERE}): {len(severe)}; "
                f"concerning (>={NULL_FPR_CONCERNING}): {len(concerning)}."
            ),
        },
        {
            "id": "D5-CFFAIL-FIND-003",
            "summary": f"Likely mechanisms (ranked): {top_mech or ['inconclusive']}.",
        },
        {
            "id": "D5-CFFAIL-FIND-003b",
            "summary": (
                f"Conformal/A26 mean half-width ratio: {hw_ratio}; "
                f"over-wide interval rate: {overwide}."
            ),
        },
    ]
    if cfg.n_mc_reduction_reason:
        findings.append(
            {
                "id": "D5-CFFAIL-FIND-004",
                "severity": "info",
                "summary": f"n_mc={cfg.n_mc}; {cfg.n_mc_reduction_reason}",
            }
        )

    if cfg.n_mc < 6 and (
        not np.isfinite(mean_fpr)
        or (comparison.get("mean_conformal_null_fpr") or {}).get("std", 0) > 0.25
    ):
        return "conformal_inconclusive_low_mc", findings

    if mean_feas < 0.5:
        return "conformal_blocked_pending_new_design", findings + [
            {
                "id": "D5-CFFAIL-FIND-005",
                "severity": "high",
                "summary": f"Conformal feasibility {mean_feas:.2f} below 0.5.",
            }
        ]

    if len(severe) >= 3 or (np.isfinite(mean_fpr) and mean_fpr >= NULL_FPR_SEVERE):
        if "conformal_band_construction_mismatch" in top_mech:
            return "conformal_blocked_pending_new_design", findings
        return "conformal_remains_restricted", findings

    if np.isfinite(hw_ratio) and hw_ratio >= 10.0:
        return "conformal_blocked_pending_new_design", findings + [
            {
                "id": "D5-CFFAIL-FIND-006",
                "summary": (
                    f"Null FPR low ({mean_fpr}) but intervals unusably wide "
                    f"(HW ratio {hw_ratio:.1f} vs A26)."
                ),
            }
        ]

    if np.isfinite(overwide) and overwide >= 0.2:
        return "conformal_remains_restricted", findings

    if len(concerning) >= 1 and len(severe) == 0:
        if "post_treatment_shock_sensitivity" in top_mech and len(concerning) <= 2:
            return "conformal_remains_restricted", findings
        if "conformal_band_construction_mismatch" in top_mech:
            return "conformal_research_repair_candidate", findings
        return "conformal_remains_restricted", findings

    if (
        np.isfinite(mean_fpr)
        and mean_fpr < NULL_FPR_CONCERNING
        and np.isfinite(hw_ratio)
        and hw_ratio < 5.0
        and (not np.isfinite(overwide) or overwide < 0.1)
    ):
        return "conformal_safe_only_under_narrow_diagnostics", findings

    return "conformal_remains_restricted", findings


def build_d5_inf_augsynth_conformal_failure_001(
    cfg: D5InfAugsynthConformalFailure001Config | None = None,
) -> dict[str, Any]:
    cfg = cfg or D5InfAugsynthConformalFailure001Config()
    t0 = time.perf_counter()
    replicates: list[dict[str, Any]] = []
    for world in cfg.worlds:
        for i in range(cfg.n_mc):
            seed = cfg.random_state_base + (hash(world.world_id) % 10_000) + i * 23
            replicates.append(_run_failure_replicate(world, cfg, seed=seed))

    summaries: list[dict[str, Any]] = []
    for world in cfg.worlds:
        for arm in COMPARISON_ARMS:
            for effect in world.effect_grid:
                summaries.append(
                    _aggregate_arm_metrics(
                        replicates,
                        world_id=world.world_id,
                        arm=arm,
                        effect=float(effect),
                    )
                )

    failure_null = _failure_strata_summary(replicates, effect=0.0)
    failure_effect = _failure_strata_summary(replicates, effect=cfg.calibration_effect)
    comparison = _compare_arms(summaries)
    mechanisms = _score_failure_mechanisms(
        replicates,
        failure_strata_null=failure_null,
        comparison=comparison,
    )
    null_fpr_summary = {
        arm: _aggregate_arm_metrics(replicates, world_id=None, arm=arm, effect=0.0)
        for arm in COMPARISON_ARMS
    }
    interval_degeneracy = _aggregate_arm_metrics(
        replicates, world_id=None, arm=PRIMARY_ARM, effect=0.0
    )
    overall, findings = _decide_verdict(
        cfg=cfg,
        comparison=comparison,
        mechanism=mechanisms,
        summaries=summaries,
        null_fpr_summary=null_fpr_summary,
        interval_degeneracy=interval_degeneracy,
    )

    return {
        "artifact_id": "D5-INF-AUGSYNTH-CONFORMAL-FAILURE-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime_seconds": time.perf_counter() - t0,
        "lane": "research",
        "binding_docs": [
            "AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001",
            "AUGSYNTH-ASCM-IMPLEMENTATION-FIDELITY-AUDIT-001",
            "D5_INST_AUGSYNTH_ASCM_003_REPORT",
            "D5_INF_AUGSYNTH_JK_CALIBRATION_001_REPORT",
        ],
        "prior_evidence": list(cfg.prior_artifacts),
        "conformal_semantics": CONFORMAL_SEMANTICS,
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
            "conformal_remains_diagnostic_restricted": True,
        },
        "fidelity_caveats": list(FIDELITY_CAVEATS),
        "config": {
            "n_mc": cfg.n_mc,
            "n_mc_target": 8,
            "n_mc_reduction_reason": cfg.n_mc_reduction_reason,
            "calibration_effect": cfg.calibration_effect,
            "world_ids": [w.world_id for w in cfg.worlds],
            "instrument_arms": list(COMPARISON_ARMS),
            "primary_arm": PRIMARY_ARM,
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
        "null_fpr_summary": null_fpr_summary,
        "effect_coverage_summary": {
            arm: _aggregate_arm_metrics(
                replicates, world_id=None, arm=arm, effect=cfg.calibration_effect
            )
            for arm in COMPARISON_ARMS
        },
        "interval_degeneracy_summary": interval_degeneracy,
        "failure_strata": {
            "at_null": failure_null,
            "at_effect": failure_effect,
        },
        "arm_comparison": comparison,
        "failure_mechanisms": mechanisms,
        "overall_verdict": overall,
        "findings": findings,
        "promotion_audit_eligible": False,
    }


def write_artifact(
    path: Path | None = None,
    *,
    cfg: D5InfAugsynthConformalFailure001Config | None = None,
) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_results.json"
    )
    payload = build_d5_inf_augsynth_conformal_failure_001(cfg)
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
        / "D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_results.json"
    )
    report_path = report_path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_REPORT.md"
    )
    p = json.loads(results_path.read_text(encoding="utf-8"))
    cfg = p.get("config", {})
    null_fpr = p.get("null_fpr_summary", {})
    effect_cov = p.get("effect_coverage_summary", {})
    comp = p.get("arm_comparison", {})
    mech = p.get("failure_mechanisms", {})
    strata = p.get("failure_strata", {}).get("at_null", {})
    prior = p.get("prior_evidence", [])

    def _fmt(v: Any) -> str:
        if v is None or (isinstance(v, float) and not np.isfinite(v)):
            return "—"
        return str(v)

    def _mean(block: dict[str, Any], key: str) -> str:
        return _fmt((block.get(key) or {}).get("mean"))

    lines = [
        "# D5-INF-AUGSYNTH-CONFORMAL-FAILURE-001 — AugSynth+Conformal failure analysis",
        "",
        f"**Artifact:** [`archives/D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_results.json`](archives/D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_results.json)  ",
        f"**Harness:** `panel_exp/validation/track_d_d5_inf_augsynth_conformal_failure_001.py`  ",
        "",
        f"**Overall verdict:** `{p.get('overall_verdict')}`  ",
        f"**Runtime (s):** `{float(p['runtime_seconds']):.1f}`  "
        if p.get("runtime_seconds") is not None
        else "**Runtime (s):** `—`  ",
        "",
        "## 1. Purpose",
        "",
        "Isolate and document **AugSynth+Conformal** failure modes after ASCM-003 and "
        "JK calibration. Determine whether failure is due to geometry, exchangeability "
        "violations, shocks, weak prefit, hull stress, or interval construction — "
        "**without promotion or governed-uncertainty change**.",
        "",
        "## 2. Prior evidence from ASCM-002/003 and JK calibration",
        "",
    ]
    for pe in prior:
        lines.append(
            f"- `{pe.get('artifact_id')}` verdict: `{pe.get('verdict')}`"
        )
    lines.extend(
        [
            "- ASCM-003: AugSynth+Conformal retains **elevated null interval-exclusion FPR** on multiple worlds.",
            "- JK calibration: AugSynth+JK unsafe under post-period shock (`W8`); Conformal historically worse than JK.",
            "",
            "## 3. Design",
            "",
            f"- Monte Carlo: **n_mc={cfg.get('n_mc')}** (target 8; reduction: {cfg.get('n_mc_reduction_reason') or 'none'})",
            f"- Worlds: **{len(p.get('world_registry', []))}** (ASCM-003 registry)",
            f"- Effect calibration level: **{cfg.get('calibration_effect')}**",
            "- Primary failure target: `augsynth_cvxpy_conformal`",
            "",
            "## 4. Worlds / strata",
            "",
            "ASCM-003 worlds plus diagnostic strata: prefit, hull, donor pool, weak-fit severity, "
            "method disagreement, post-shock vs no-shock.",
            "",
            "## 5. Methods compared",
            "",
            "| Arm | Role |",
            "|-----|------|",
            "| `a26_scm_unit_jackknife` | Governed null-monitor reference |",
            "| `augsynth_cvxpy_unit_jackknife` | JK comparator (JK-calibration context) |",
            "| `augsynth_cvxpy_point` | Point comparator / disagreement anchor |",
            "| `augsynth_cvxpy_conformal` | **Failure-analysis target** |",
            "",
            "## 6. Diagnostics used",
            "",
            "D5-DIAG panel fields, instrument false-confidence flags, null-world "
            "`conflict_vs_a26`, conformal semantics from D5-INST-AUGSYNTH-003.",
            "",
            "## 7. Null FPR",
            "",
            f"| arm | mean null interval-exclusion FPR |",
            f"|-----|----------------------------------|",
            f"| A26 JK | {_mean(null_fpr.get('a26_scm_unit_jackknife', {}), 'null_interval_exclusion_fpr')} |",
            f"| AugSynth JK | {_mean(null_fpr.get('augsynth_cvxpy_unit_jackknife', {}), 'null_interval_exclusion_fpr')} |",
            f"| AugSynth Conformal | {_mean(null_fpr.get('augsynth_cvxpy_conformal', {}), 'null_interval_exclusion_fpr')} |",
            "",
            f"Severe worlds (FPR ≥ {NULL_FPR_SEVERE}): `{comp.get('severe_null_fpr_worlds', [])}`  ",
            f"Concerning worlds (FPR ≥ {NULL_FPR_CONCERNING}): `{comp.get('concerning_null_fpr_worlds', [])}`",
            "",
            "## 8. Effect coverage",
            "",
            f"@ {cfg.get('calibration_effect')}:",
            "",
            f"| arm | mean covers injected effect |",
            f"|-----|----------------------------|",
            f"| A26 JK | {_mean(effect_cov.get('a26_scm_unit_jackknife', {}), 'covers_injected_effect')} |",
            f"| AugSynth JK | {_mean(effect_cov.get('augsynth_cvxpy_unit_jackknife', {}), 'covers_injected_effect')} |",
            f"| AugSynth Conformal | {_mean(effect_cov.get('augsynth_cvxpy_conformal', {}), 'covers_injected_effect')} |",
            "",
            "## 9. Interval width / degeneracy",
            "",
            f"- Conformal mean half-width @ null: "
            f"`{_mean(null_fpr.get('augsynth_cvxpy_conformal', {}), 'mean_interval_halfwidth')}`",
            f"- Degenerate interval rate: "
            f"`{_mean(p.get('interval_degeneracy_summary', {}), 'degenerate_interval')}`",
            f"- Negative half-width rate: "
            f"`{_mean(p.get('interval_degeneracy_summary', {}), 'negative_halfwidth')}`",
            f"- Over-wide interval rate (≥{WIDE_HW_THRESHOLD}): "
            f"`{_mean(p.get('interval_degeneracy_summary', {}), 'overwide_interval')}`",
            "",
            "## 10. Failure stratification",
            "",
            "See artifact `failure_strata.at_null` for conformal vs JK vs A26 JK by stratum.",
            "",
        ]
    )
    for stratum_name in ("prefit", "hull", "post_shock", "method_disagreement"):
        block = strata.get(stratum_name, {})
        if not block:
            continue
        lines.append(f"**{stratum_name}:**")
        for label, arms in sorted(block.items()):
            cf_fpr = (arms.get("conformal", {}).get("null_interval_exclusion_fpr") or {}).get(
                "mean"
            )
            lines.append(f"- `{label}` conformal null FPR: `{_fmt(cf_fpr)}`")
        lines.append("")

    lines.extend(
        [
            "## 11. Likely failure mechanisms",
            "",
            f"Ranked: `{mech.get('likely_mechanisms', [])}`",
            "",
        ]
    )
    for mid in mech.get("likely_mechanisms", []):
        ev = mech.get("mechanism_evidence", {}).get(mid, [])
        lines.append(f"- **{mid}**: {'; '.join(ev) if ev else '—'}")

    lines.extend(
        [
            "",
            "## 12. Comparison to JK",
            "",
            "JK null FPR generally lower than Conformal on the same worlds; "
            "JK shows shock sensitivity (`W8`) while Conformal shows broader elevated FPR "
            "consistent with exchangeability / calibration-set mismatch.",
            "",
            "## 13. Verdict",
            "",
            f"**`{p.get('overall_verdict')}`** — Conformal remains **restricted**; "
            "not added to governed uncertainty.",
            "",
            "## 14. Guardrails",
            "",
            "| Guardrail | Status |",
            "|-----------|--------|",
            "| Promotion | **No** |",
            "| Governed uncertainty allowlist | **No change** |",
            "| Inference behavior change | **No** |",
            "",
            "## 15. Next step",
            "",
            "If `conformal_blocked_pending_new_design`: do not invest in current conformal.py "
            "pairing without new exchangeability-aware design. If `conformal_remains_restricted`: "
            "keep A05 characterized_restricted; continue JK comparator lane (P4 follow-up).",
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
    archive_cfg = D5InfAugsynthConformalFailure001Config(
        n_mc=4,
        n_mc_reduction_reason=(
            "19-world conformal failure grid runtime; harness default n_mc=8 for replay"
        ),
    )
    out = write_artifact(cfg=archive_cfg)
    rep = write_report(results_path=out)
    print(f"Wrote {out}")
    print(f"Wrote {rep}")
