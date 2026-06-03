"""D5-INST-AUGSYNTH-ASCM-003 — stratified AugSynth/ASCM OC with D5-DIAG diagnostics.

Post D5-DIAG-SCM-AUGSYNTH-001 and AUGSYNTH-ASCM-IMPLEMENTATION-FIDELITY-AUDIT-001.
Uses merged diagnostics + fidelity caveats to characterize when AugSynth/ASCM helps,
when it fails, and which diagnostics support future threshold calibration.

No promotion, no threshold finalization, no estimator/inference behavior change.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.methods.scm import AugSynthCVXPY
from panel_exp.panel_data import PanelDataset
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.scm_augsynth_diagnostics import (
    CONFLICT_DIAGNOSTIC_FIELDS,
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
from panel_exp.validation.track_d_d5_inst_augsynth_ascm_002 import (
    INSTRUMENT_ARMS,
    AscmWorldSpec,
    D5InstAugsynthAscm002Config,
    WORLD_REGISTRY as ASCM002_WORLD_REGISTRY,
    _aggregate_arm_world,
    _compare_weak_fit_vs_a26,
    _panel_strengthening_diagnostics,
    _recovery_metrics,
    _run_instrument_arm,
)
from panel_exp.validation.track_d_d5_inst_augsynth_003 import (
    _augsynth_conformal_readout_metrics,
)
from panel_exp.validation.track_d_d5_inst_augsynth_kfold_001 import (
    _augsynth_readout_metrics,
)
from panel_exp.validation.track_d_d5_pow_001b import _scm_jk_readout_metrics
from panel_exp.validation.track_d_d5_pow_001e import _assign, _summarize
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

OverallVerdict = Literal[
    "continue_diagnostic_comparator",
    "promising_needs_inference_calibration",
    "implementation_fix_required",
    "stop_augsynth_lane",
    "promotion_audit_candidate_future_only",
]

PRIMARY_INSTRUMENT_ARMS: tuple[str, ...] = (
    "a26_scm_unit_jackknife",
    "augsynth_cvxpy_point",
    "augsynth_cvxpy_unit_jackknife",
)

SECONDARY_DIAGNOSTIC_ARMS: tuple[str, ...] = (
    "augsynth_cvxpy_conformal",
    "augsynth_cvxpy_kfold",
)

FIDELITY_CAVEATS: tuple[dict[str, str], ...] = (
    {
        "id": "G4",
        "summary": "D1 scm_pre_rmse uses SciPy SyntheticControl, not inner SyntheticControlCVXPY.",
    },
    {
        "id": "G1",
        "summary": "penalty/penalty_strength stored on AugSynthCVXPY but unused on OSQP SCM path.",
    },
    {
        "id": "G7",
        "summary": "OC uses level mean_point_effect; summary() uses relative effect estimand.",
    },
    {
        "id": "G8",
        "summary": "Hull stress uses z-distance proxy, not true convex hull membership.",
    },
)


@dataclass(frozen=True)
class Ascm003WorldSpec:
    world_id: str
    charter_label: str
    scenario_name: str
    scenario_overrides: dict[str, Any] = field(default_factory=dict)
    n_geos: int = 16
    treatment_probability: float = 0.35
    n_test_grps: int = 1
    fit_class: str = "baseline"
    use_scenario_treated_units: bool = False
    effect_grid: tuple[float, ...] = (0.0, 0.08)
    augsynth_lambda_reg: float = 0.0
    weak_fit_severity: str | None = None


def _from_002(world: AscmWorldSpec, **overrides: Any) -> Ascm003WorldSpec:
    return Ascm003WorldSpec(
        world_id=overrides.pop("world_id", world.world_id),
        charter_label=overrides.pop("charter_label", world.charter_label),
        scenario_name=overrides.pop("scenario_name", world.scenario_name),
        scenario_overrides=overrides.pop(
            "scenario_overrides", dict(world.scenario_overrides)
        ),
        n_geos=overrides.pop("n_geos", world.n_geos),
        treatment_probability=overrides.pop(
            "treatment_probability", world.treatment_probability
        ),
        n_test_grps=overrides.pop("n_test_grps", world.n_test_grps),
        fit_class=overrides.pop("fit_class", world.fit_class),
        use_scenario_treated_units=overrides.pop(
            "use_scenario_treated_units", world.use_scenario_treated_units
        ),
        effect_grid=overrides.pop("effect_grid", world.effect_grid),
        augsynth_lambda_reg=overrides.pop("augsynth_lambda_reg", 0.0),
        weak_fit_severity=overrides.pop("weak_fit_severity", None),
        **overrides,
    )


SEVERITY_EXTENSION_WORLDS: tuple[Ascm003WorldSpec, ...] = (
    Ascm003WorldSpec(
        "W2m_mild_weak_fit",
        "mild weak SCM fit / inside hull",
        "scm_trend_mismatch",
        scenario_overrides={"noise_scale": 1.6},
        fit_class="weak_fit",
        weak_fit_severity="mild",
    ),
    Ascm003WorldSpec(
        "W2s_severe_weak_fit",
        "severe weak SCM fit / inside hull",
        "scm_trend_mismatch",
        scenario_overrides={"noise_scale": 4.2},
        fit_class="weak_fit",
        weak_fit_severity="severe",
    ),
    Ascm003WorldSpec(
        "W3s_severe_outside_hull",
        "severe weak SCM fit / outside donor hull",
        "scm_low_signal",
        scenario_overrides={"cross_geo_correlation": 0.03, "noise_scale": 4.5},
        fit_class="weak_fit_outside_hull",
        weak_fit_severity="severe",
    ),
    Ascm003WorldSpec(
        "W4s_ultra_sparse_donor_pool",
        "ultra-sparse donor pool",
        "scm_low_signal",
        n_geos=9,
        treatment_probability=0.45,
        fit_class="sparse_donors",
    ),
    Ascm003WorldSpec(
        "W5s_very_rich_donor_pool",
        "very rich donor pool",
        "scm_low_signal",
        n_geos=28,
        scenario_overrides={"cross_geo_correlation": 0.55},
        fit_class="rich_donors",
    ),
    Ascm003WorldSpec(
        "W2r_lambda_reg_moderate",
        "weak fit with moderate AugSynth ridge lambda",
        "scm_trend_mismatch",
        fit_class="weak_fit",
        weak_fit_severity="moderate",
        augsynth_lambda_reg=0.01,
    ),
    Ascm003WorldSpec(
        "W2r_lambda_reg_high",
        "weak fit with high AugSynth ridge lambda",
        "scm_trend_mismatch",
        fit_class="weak_fit",
        weak_fit_severity="moderate",
        augsynth_lambda_reg=0.05,
    ),
)

WORLD_REGISTRY_003: tuple[Ascm003WorldSpec, ...] = tuple(
    _from_002(w) for w in ASCM002_WORLD_REGISTRY
) + SEVERITY_EXTENSION_WORLDS

INSIDE_HULL_FIT_CLASSES: frozenset[str] = frozenset(
    {"baseline", "strong_fit", "weak_fit", "sparse_donors", "rich_donors"}
)
OUTSIDE_HULL_FIT_CLASSES: frozenset[str] = frozenset({"weak_fit_outside_hull"})


@dataclass(frozen=True)
class D5InstAugsynthAscm003Config:
    n_mc: int = 14
    train_length: int = 28
    test_length: int = 8
    n_periods: int = 44
    alpha: float = 0.05
    random_state_base: int = 20260715
    reference_design_method: str = "greedy_match_markets"
    min_donors_augsynth: int = 5
    kfold_random_state: int = 0
    worlds: tuple[Ascm003WorldSpec, ...] = WORLD_REGISTRY_003
    material_point_mismatch_threshold: float = 0.05
    weak_fit_world_ids: tuple[str, ...] = tuple(
        w.world_id
        for w in WORLD_REGISTRY_003
        if w.fit_class.startswith("weak_fit")
    )
    n_mc_reduction_reason: str | None = None
    fidelity_audit_id: str = "AUGSYNTH-ASCM-IMPLEMENTATION-FIDELITY-AUDIT-001"
    fidelity_audit_verdict: str = "fidelity_confirmed_with_caveats"
    diag_module_id: str = "D5-DIAG-SCM-AUGSYNTH-001"

    def as_002_cfg(self) -> D5InstAugsynthAscm002Config:
        """Bridge to ASCM-002 helpers that expect AscmWorldSpec worlds."""
        worlds_002 = tuple(
            AscmWorldSpec(
                w.world_id,
                w.charter_label,
                w.scenario_name,
                scenario_overrides=w.scenario_overrides,
                n_geos=w.n_geos,
                treatment_probability=w.treatment_probability,
                n_test_grps=w.n_test_grps,
                fit_class=w.fit_class,
                use_scenario_treated_units=w.use_scenario_treated_units,
                effect_grid=w.effect_grid,
            )
            for w in self.worlds
        )
        return D5InstAugsynthAscm002Config(
            n_mc=self.n_mc,
            train_length=self.train_length,
            test_length=self.test_length,
            n_periods=self.n_periods,
            alpha=self.alpha,
            random_state_base=self.random_state_base,
            reference_design_method=self.reference_design_method,
            min_donors_augsynth=self.min_donors_augsynth,
            kfold_random_state=self.kfold_random_state,
            worlds=worlds_002,
            material_point_mismatch_threshold=self.material_point_mismatch_threshold,
            weak_fit_world_ids=self.weak_fit_world_ids,
        )


def _readout_metrics_with_lambda_reg(
    panel: PanelDataset,
    *,
    inference: str | None,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
    min_donors: int,
    instrument_id: str,
    lambda_reg: float,
) -> dict[str, Any]:
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    n_control = len(pds.control_units)
    n_treated = len(pds.treated_units)
    out: dict[str, Any] = {
        "instrument_id": instrument_id,
        "percent_effect": float(percent_effect),
        "n_control_donors": n_control,
        "n_treated_units": n_treated,
        "feasible": 0.0,
        "fit_success": 0.0,
        "has_point": 0.0,
        "has_interval": 0.0,
        "blocked_reason": None,
        "error_type": None,
        "wall_time_s": float("nan"),
        "augsynth_lambda_reg_used": float(lambda_reg),
    }
    if n_control < min_donors:
        out["blocked_reason"] = f"insufficient_donors_need_{min_donors}_got_{n_control}"
        return out
    skip = cvxpy_osqp_skip_reason()
    if skip:
        out["blocked_reason"] = skip
        return out
    t0 = time.perf_counter()
    try:
        est = AugSynthCVXPY(
            inference=inference,
            alpha=alpha,
            min_donors=min_donors,
            lambda_reg=lambda_reg,
        )
        est.run_analysis(pds)
        out["fit_success"] = 1.0
        out["feasible"] = 1.0
    except Exception as exc:
        out["error_type"] = type(exc).__name__
        out["blocked_reason"] = str(exc)[:240]
        out["wall_time_s"] = time.perf_counter() - t0
        return out
    out["wall_time_s"] = time.perf_counter() - t0
    results = est.results or {}
    y, y_hat, y_lo, y_hi = _post_window_arrays(results, test_length)
    if not (np.any(np.isfinite(y)) and np.any(np.isfinite(y_hat))):
        out["blocked_reason"] = "non_finite_y_or_y_hat"
        return out
    out["has_point"] = 1.0
    effect = y - y_hat
    effect_lo = y - y_hi
    effect_hi = y - y_lo
    point_mean = float(np.mean(effect))
    has_interval = inference is not None and inference not in ("point_estimate",)
    out["has_interval"] = float(has_interval)
    covers_zero = float(np.nan)
    detected = float(np.nan)
    mean_hw = float(np.nan)
    if has_interval and np.any(np.isfinite(y_lo)) and np.any(np.isfinite(y_hi)):
        covers_zero = float(np.mean(effect_lo) <= 0.0 <= np.mean(effect_hi))
        detected = float(not covers_zero)
        mean_hw = float(np.mean((y_hi - y_lo) / 2.0))
    ir = getattr(est, "inference_result", None)
    path_it = None
    if ir is not None:
        pit = getattr(ir, "path_interval_type", None)
        path_it = getattr(pit, "value", pit)
    out.update(
        {
            "mean_point_effect": point_mean,
            "covers_zero_correct": covers_zero,
            "detected_interval_excludes_zero": detected,
            "mean_interval_halfwidth": mean_hw,
            "path_interval_type": path_it,
            "directional_recovery": float(
                abs(percent_effect) < 1e-12
                or (np.isfinite(point_mean) and np.sign(point_mean) == np.sign(percent_effect))
            ),
        }
    )
    return out


def _run_instrument_arm_003(
    panel: PanelDataset,
    arm: str,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    cfg: D5InstAugsynthAscm003Config,
    lambda_reg: float,
) -> dict[str, Any]:
    cfg2 = cfg.as_002_cfg()
    if arm == "a26_scm_unit_jackknife":
        return _run_instrument_arm(
            panel, arm, percent_effect=percent_effect, mean_value=mean_value, cfg=cfg2
        )
    if arm == "augsynth_cvxpy_point":
        return _readout_metrics_with_lambda_reg(
            panel,
            inference=None,
            percent_effect=percent_effect,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            min_donors=cfg.min_donors_augsynth,
            instrument_id="AugSynthCVXPY_Point",
            lambda_reg=lambda_reg,
        )
    if arm == "augsynth_cvxpy_unit_jackknife":
        return _readout_metrics_with_lambda_reg(
            panel,
            inference="UnitJackKnife",
            percent_effect=percent_effect,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            min_donors=cfg.min_donors_augsynth,
            instrument_id="AugSynthCVXPY_UnitJackKnife",
            lambda_reg=lambda_reg,
        )
    if arm == "augsynth_cvxpy_conformal":
        raw = _augsynth_conformal_readout_metrics(
            panel,
            percent_effect=percent_effect,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            min_donors=cfg.min_donors_augsynth,
        )
        raw["augsynth_lambda_reg_used"] = 0.0
        return raw
    if arm == "augsynth_cvxpy_kfold":
        raw = _augsynth_readout_metrics(
            panel,
            inference="Kfold",
            percent_effect=percent_effect,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            min_donors=cfg.min_donors_augsynth,
            instrument_id="AugSynthCVXPY_Kfold",
            random_state=cfg.kfold_random_state,
        )
        raw["augsynth_lambda_reg_used"] = 0.0
        return raw
    raise ValueError(f"unknown arm: {arm}")


def _run_world_replicate(
    world: Ascm003WorldSpec,
    cfg: D5InstAugsynthAscm003Config,
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
        n_test_grps = 1
    else:
        n_test_grps = world.n_test_grps
        assignment = _assign(
            cfg.reference_design_method,
            wide,
            train_length=cfg.train_length,
            seed=seed,
            treatment_probability=world.treatment_probability,
            n_test_grps=n_test_grps,
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
        arm: {} for arm in INSTRUMENT_ARMS
    }
    for arm in INSTRUMENT_ARMS:
        for prc in world.effect_grid:
            inst = _run_instrument_arm_003(
                panel,
                arm,
                percent_effect=float(prc),
                mean_value=mean_value,
                cfg=cfg,
                lambda_reg=world.augsynth_lambda_reg,
            )
            inst.update(_recovery_metrics(inst, percent_effect=float(prc)))
            inst.update(compute_instrument_diagnostics(inst, diagnostics))
            instruments[arm][float(prc)] = inst

    null_a26 = instruments["a26_scm_unit_jackknife"].get(0.0, {})
    null_aug = instruments["augsynth_cvxpy_point"].get(0.0, {})
    conflict = compute_method_disagreement(
        null_a26,
        null_aug,
        material_point_mismatch_threshold=cfg.material_point_mismatch_threshold,
    )

    return {
        "seed": seed,
        "world_id": world.world_id,
        "fit_class": world.fit_class,
        "charter_label": world.charter_label,
        "scenario_name": world.scenario_name,
        "weak_fit_severity": world.weak_fit_severity,
        "augsynth_lambda_reg": world.augsynth_lambda_reg,
        "n_control": len(panel.control_units),
        "n_treated": len(panel.treated_units),
        "diagnostics": diagnostics,
        "instruments": instruments,
        "conflict_vs_a26": conflict,
        "fidelity_caveats_applied": [c["id"] for c in FIDELITY_CAVEATS],
    }


def _aggregate_panel_diagnostics(
    replicates: list[dict[str, Any]],
    *,
    world_id: str,
) -> dict[str, Any]:
    out: dict[str, Any] = {"world_id": world_id}
    for key in PANEL_DIAGNOSTIC_FIELDS:
        vals = []
        for rep in replicates:
            if rep["world_id"] != world_id:
                continue
            diag = rep.get("diagnostics", {})
            if not diag.get("diagnostics_feasible"):
                continue
            v = diag.get(key)
            if v is not None and np.isfinite(v):
                vals.append(float(v))
        out[key] = _summarize(vals)
    out["diagnostics_feasible_rate"] = float(
        np.mean(
            [
                float(rep.get("diagnostics", {}).get("diagnostics_feasible", 0.0))
                for rep in replicates
                if rep["world_id"] == world_id
            ]
        )
        if any(rep["world_id"] == world_id for rep in replicates)
        else 0.0
    )
    return out


def _hull_strata_summary(
    summaries: list[dict[str, Any]],
    replicates: list[dict[str, Any]],
    *,
    cfg: D5InstAugsynthAscm003Config,
) -> dict[str, Any]:
    world_by_id = {w.world_id: w for w in cfg.worlds}

    def _stratum(fit_classes: frozenset[str]) -> dict[str, Any]:
        world_ids = [
            w.world_id for w in cfg.worlds if w.fit_class in fit_classes
        ]
        rows = []
        for wid in world_ids:
            a26 = next(
                (
                    s
                    for s in summaries
                    if s["world_id"] == wid
                    and s["instrument"] == "a26_scm_unit_jackknife"
                    and s["effect"] == 0.08
                ),
                None,
            )
            aug = next(
                (
                    s
                    for s in summaries
                    if s["world_id"] == wid
                    and s["instrument"] == "augsynth_cvxpy_point"
                    and s["effect"] == 0.08
                ),
                None,
            )
            if not a26 or not aug:
                continue
            a26_mae = (a26.get("effect_recovery_mae") or {}).get("mean")
            aug_mae = (aug.get("effect_recovery_mae") or {}).get("mean")
            panel_diag = _aggregate_panel_diagnostics(replicates, world_id=wid)
            hull_z = (panel_diag.get("hull_min_donor_z_distance") or {}).get("mean")
            rows.append(
                {
                    "world_id": wid,
                    "fit_class": world_by_id[wid].fit_class,
                    "a26_mae_at_8pct": a26_mae,
                    "augsynth_mae_at_8pct": aug_mae,
                    "augsynth_beats_a26_mae": bool(
                        np.isfinite(a26_mae)
                        and np.isfinite(aug_mae)
                        and aug_mae < a26_mae
                    ),
                    "mean_hull_min_donor_z_distance": hull_z,
                }
            )
        beat = sum(1 for r in rows if r.get("augsynth_beats_a26_mae"))
        return {
            "world_count": len(rows),
            "augsynth_beats_a26_count": beat,
            "worlds": rows,
        }

    return {
        "inside_hull": _stratum(INSIDE_HULL_FIT_CLASSES),
        "outside_hull": _stratum(OUTSIDE_HULL_FIT_CLASSES),
    }


def _weak_fit_severity_summary(
    summaries: list[dict[str, Any]],
    *,
    cfg: D5InstAugsynthAscm003Config,
) -> dict[str, Any]:
    severity_buckets: dict[str, list[dict[str, Any]]] = {}
    for w in cfg.worlds:
        if not w.fit_class.startswith("weak_fit"):
            continue
        sev = w.weak_fit_severity or "moderate"
        a26 = next(
            (
                s
                for s in summaries
                if s["world_id"] == w.world_id
                and s["instrument"] == "a26_scm_unit_jackknife"
                and s["effect"] == 0.08
            ),
            None,
        )
        aug = next(
            (
                s
                for s in summaries
                if s["world_id"] == w.world_id
                and s["instrument"] == "augsynth_cvxpy_point"
                and s["effect"] == 0.08
            ),
            None,
        )
        if not a26 or not aug:
            continue
        a26_mae = (a26.get("effect_recovery_mae") or {}).get("mean")
        aug_mae = (aug.get("effect_recovery_mae") or {}).get("mean")
        row = {
            "world_id": w.world_id,
            "augsynth_lambda_reg": w.augsynth_lambda_reg,
            "a26_mae_at_8pct": a26_mae,
            "augsynth_mae_at_8pct": aug_mae,
            "augsynth_beats_a26_mae": bool(
                np.isfinite(a26_mae) and np.isfinite(aug_mae) and aug_mae < a26_mae
            ),
        }
        severity_buckets.setdefault(sev, []).append(row)
    out: dict[str, Any] = {}
    for sev, rows in sorted(severity_buckets.items()):
        out[sev] = {
            "world_count": len(rows),
            "augsynth_beats_a26_count": sum(
                1 for r in rows if r.get("augsynth_beats_a26_mae")
            ),
            "worlds": rows,
        }
    return out


def _diagnostic_usefulness(
    summaries: list[dict[str, Any]],
    replicates: list[dict[str, Any]],
    *,
    cfg: D5InstAugsynthAscm003Config,
) -> dict[str, Any]:
    pairs: list[tuple[float, float, bool]] = []
    for w in cfg.worlds:
        a26 = next(
            (
                s
                for s in summaries
                if s["world_id"] == w.world_id
                and s["instrument"] == "a26_scm_unit_jackknife"
                and s["effect"] == 0.08
            ),
            None,
        )
        aug = next(
            (
                s
                for s in summaries
                if s["world_id"] == w.world_id
                and s["instrument"] == "augsynth_cvxpy_point"
                and s["effect"] == 0.08
            ),
            None,
        )
        if not a26 or not aug:
            continue
        a26_mae = (a26.get("effect_recovery_mae") or {}).get("mean")
        aug_mae = (aug.get("effect_recovery_mae") or {}).get("mean")
        panel = _aggregate_panel_diagnostics(replicates, world_id=w.world_id)
        fit_imp = (panel.get("fit_improvement_rmse") or {}).get("mean")
        hull_z = (panel.get("hull_min_donor_z_distance") or {}).get("mean")
        if not (np.isfinite(a26_mae) and np.isfinite(aug_mae)):
            continue
        beats = aug_mae < a26_mae
        if np.isfinite(fit_imp):
            pairs.append((float(fit_imp), float(a26_mae - aug_mae), beats))
        if np.isfinite(hull_z) and hull_z >= 2.0 and not beats:
            pass  # counted below

    fit_improvement_predicts_win = 0
    fit_improvement_total = 0
    for fit_imp, _delta, beats in pairs:
        if fit_imp > 0:
            fit_improvement_total += 1
            if beats:
                fit_improvement_predicts_win += 1

    high_hull_aug_loses = 0
    high_hull_total = 0
    for w in cfg.worlds:
        panel = _aggregate_panel_diagnostics(replicates, world_id=w.world_id)
        hull_z = (panel.get("hull_min_donor_z_distance") or {}).get("mean")
        if hull_z is None or not np.isfinite(hull_z) or hull_z < 2.0:
            continue
        high_hull_total += 1
        aug = next(
            (
                s
                for s in summaries
                if s["world_id"] == w.world_id
                and s["instrument"] == "augsynth_cvxpy_point"
                and s["effect"] == 0.08
            ),
            None,
        )
        a26 = next(
            (
                s
                for s in summaries
                if s["world_id"] == w.world_id
                and s["instrument"] == "a26_scm_unit_jackknife"
                and s["effect"] == 0.08
            ),
            None,
        )
        if not aug or not a26:
            continue
        a26_mae = (a26.get("effect_recovery_mae") or {}).get("mean")
        aug_mae = (aug.get("effect_recovery_mae") or {}).get("mean")
        if np.isfinite(a26_mae) and np.isfinite(aug_mae) and aug_mae >= a26_mae:
            high_hull_aug_loses += 1

    false_conf_a26 = [
        (s.get("false_confidence_rate") or {}).get("mean", float("nan"))
        for s in summaries
        if s["instrument"] == "a26_scm_unit_jackknife" and s["effect"] == 0.0
    ]
    false_conf_aug_jk = [
        (s.get("false_confidence_rate") or {}).get("mean", float("nan"))
        for s in summaries
        if s["instrument"] == "augsynth_cvxpy_unit_jackknife" and s["effect"] == 0.0
    ]

    return {
        "fit_improvement_positive_and_aug_wins_rate": (
            float(fit_improvement_predicts_win / fit_improvement_total)
            if fit_improvement_total
            else float("nan")
        ),
        "fit_improvement_positive_world_count": fit_improvement_total,
        "high_hull_stress_aug_loses_rate": (
            float(high_hull_aug_loses / high_hull_total) if high_hull_total else float("nan")
        ),
        "high_hull_stress_world_count": high_hull_total,
        "mean_false_confidence_rate_a26_null": _summarize(
            [x for x in false_conf_a26 if np.isfinite(x)]
        ),
        "mean_false_confidence_rate_aug_jk_null": _summarize(
            [x for x in false_conf_aug_jk if np.isfinite(x)]
        ),
        "panel_diagnostic_fields_tracked": list(PANEL_DIAGNOSTIC_FIELDS),
        "instrument_diagnostic_fields_tracked": list(INSTRUMENT_DIAGNOSTIC_FIELDS),
        "conflict_diagnostic_fields_tracked": list(CONFLICT_DIAGNOSTIC_FIELDS),
        "provisional_threshold_calibration_ready": True,
    }


def _null_interval_summary(
    summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    arms = (
        "a26_scm_unit_jackknife",
        "augsynth_cvxpy_point",
        "augsynth_cvxpy_unit_jackknife",
        "augsynth_cvxpy_conformal",
    )
    out: dict[str, Any] = {}
    for arm in arms:
        fprs = [
            (s.get("null_interval_exclusion_fpr") or {}).get("mean", float("nan"))
            for s in summaries
            if s["instrument"] == arm and s["effect"] == 0.0
        ]
        hws = [
            (s.get("mean_interval_halfwidth") or {}).get("mean", float("nan"))
            for s in summaries
            if s["instrument"] == arm and s["effect"] == 0.0
        ]
        out[arm] = {
            "null_interval_exclusion_fpr": _summarize(
                [x for x in fprs if np.isfinite(x)]
            ),
            "mean_interval_halfwidth_at_null": _summarize(
                [x for x in hws if np.isfinite(x)]
            ),
        }
    return out


def _decide_overall(
    summaries: list[dict[str, Any]],
    weak_compare: dict[str, Any],
    diagnostic_usefulness: dict[str, Any],
    null_summary: dict[str, Any],
    *,
    cfg: D5InstAugsynthAscm003Config,
) -> tuple[OverallVerdict, list[dict[str, Any]]]:
    pt_feas = [
        s["feasibility_rate"]
        for s in summaries
        if s["instrument"] == "augsynth_cvxpy_point" and s["effect"] == 0.0
    ]
    mean_feas = float(np.mean(pt_feas)) if pt_feas else 0.0

    beat = int(weak_compare.get("augsynth_beats_a26_weak_fit_world_count", 0))
    n_weak = int(weak_compare.get("weak_fit_world_count", 0))

    aug_jk_fprs = [
        (null_summary.get("augsynth_cvxpy_unit_jackknife") or {})
        .get("null_interval_exclusion_fpr", {})
        .get("mean", float("nan"))
    ]
    cf_fprs = [
        (null_summary.get("augsynth_cvxpy_conformal") or {})
        .get("null_interval_exclusion_fpr", {})
        .get("mean", float("nan"))
    ]
    per_world_jk = [
        r.get("augsynth_jk_null_fpr")
        for r in weak_compare.get("weak_fit_comparisons", [])
    ]
    jk_unsafe = any(np.isfinite(x) and x > 0.15 for x in per_world_jk if x is not None)
    conformal_unsafe = any(np.isfinite(x) and x > 0.5 for x in cf_fprs)

    fit_win_rate = diagnostic_usefulness.get(
        "fit_improvement_positive_and_aug_wins_rate", float("nan")
    )

    findings: list[dict[str, Any]] = [
        {
            "id": "D5-ASCM3-FIND-001",
            "summary": (
                f"Stratified OC with D5-DIAG fields across {len(cfg.worlds)} worlds "
                f"(n_mc={cfg.n_mc})."
            ),
        },
        {
            "id": "D5-ASCM3-FIND-002",
            "summary": (
                f"AugSynth point beats A26 MAE on {beat}/{n_weak} weak-fit worlds @ 8%."
            ),
        },
        {
            "id": "D5-ASCM3-FIND-003",
            "summary": (
                "Fidelity audit caveats G1/G4/G7/G8 carried in artifact metadata; "
                "interpret diagnostics as provisional comparators only."
            ),
        },
    ]
    if conformal_unsafe:
        findings.append(
            {
                "id": "D5-ASCM3-FIND-004",
                "severity": "high",
                "summary": "AugSynth+Conformal retains elevated null interval-exclusion FPR.",
                "implication": "Inference pairing ADR still required; not null-monitor ready.",
            }
        )
    if cfg.n_mc < 14:
        findings.append(
            {
                "id": "D5-ASCM3-FIND-005",
                "severity": "info",
                "summary": f"n_mc={cfg.n_mc} (<14): {cfg.n_mc_reduction_reason or 'runtime reduction documented'}.",
            }
        )

    if mean_feas < 0.5:
        return "implementation_fix_required", findings + [
            {
                "id": "D5-ASCM3-FIND-006",
                "severity": "high",
                "summary": f"AugSynth point feasibility rate {mean_feas:.2f} below 0.5.",
            }
        ]

    partial_recovery = beat >= max(1, n_weak // 2)
    diag_signal = np.isfinite(fit_win_rate) and fit_win_rate >= 0.4
    jk_ok = not jk_unsafe

    if partial_recovery and jk_ok and (conformal_unsafe or diag_signal):
        return "promising_needs_inference_calibration", findings

    return "continue_diagnostic_comparator", findings


def build_d5_inst_augsynth_ascm_003(
    cfg: D5InstAugsynthAscm003Config | None = None,
) -> dict[str, Any]:
    cfg = cfg or D5InstAugsynthAscm003Config()
    t0 = time.perf_counter()
    replicates: list[dict[str, Any]] = []
    for world in cfg.worlds:
        for i in range(cfg.n_mc):
            seed = cfg.random_state_base + (hash(world.world_id) % 10_000) + i * 17
            replicates.append(_run_world_replicate(world, cfg, seed=seed))

    summaries: list[dict[str, Any]] = []
    for world in cfg.worlds:
        for arm in INSTRUMENT_ARMS:
            for effect in world.effect_grid:
                summaries.append(
                    _aggregate_arm_world(
                        replicates,
                        world_id=world.world_id,
                        arm=arm,
                        effect=float(effect),
                    )
                )

    panel_diag_by_world = [
        _aggregate_panel_diagnostics(replicates, world_id=w.world_id)
        for w in cfg.worlds
    ]
    weak_compare = _compare_weak_fit_vs_a26(
        summaries, weak_world_ids=cfg.weak_fit_world_ids
    )
    hull_strata = _hull_strata_summary(summaries, replicates, cfg=cfg)
    severity_summary = _weak_fit_severity_summary(summaries, cfg=cfg)
    diagnostic_usefulness = _diagnostic_usefulness(
        summaries, replicates, cfg=cfg
    )
    null_summary = _null_interval_summary(summaries)
    overall, findings = _decide_overall(
        summaries,
        weak_compare,
        diagnostic_usefulness,
        null_summary,
        cfg=cfg,
    )
    runtime_s = time.perf_counter() - t0

    return {
        "artifact_id": "D5-INST-AUGSYNTH-ASCM-003",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime_seconds": runtime_s,
        "lane": "research",
        "binding_docs": [
            "AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001",
            cfg.fidelity_audit_id,
            cfg.diag_module_id,
            "D5_INST_AUGSYNTH_ASCM_002_REPORT",
            "D5_DIAG_SCM_AUGSYNTH_001_REPORT",
        ],
        "governance": {
            "no_promotion": True,
            "no_calibration_signal_ingress": True,
            "no_mmm": True,
            "no_governed_uncertainty_allowlist_change": True,
            "no_trust_report_change": True,
            "no_f_decision_change": True,
            "no_threshold_finalization": True,
            "no_eligibility_change": True,
            "a26_remains_baseline": True,
            "augsynth_not_primary": True,
            "primary_inference_not_selected": True,
        },
        "fidelity_audit": {
            "audit_id": cfg.fidelity_audit_id,
            "verdict": cfg.fidelity_audit_verdict,
            "caveats": list(FIDELITY_CAVEATS),
        },
        "config": {
            "n_mc": cfg.n_mc,
            "n_mc_target": 14,
            "n_mc_reduction_reason": cfg.n_mc_reduction_reason,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "world_ids": [w.world_id for w in cfg.worlds],
            "instrument_arms": list(INSTRUMENT_ARMS),
            "primary_instrument_arms": list(PRIMARY_INSTRUMENT_ARMS),
            "secondary_diagnostic_arms": list(SECONDARY_DIAGNOSTIC_ARMS),
            "min_donors_augsynth": cfg.min_donors_augsynth,
            "weak_fit_world_ids": list(cfg.weak_fit_world_ids),
        },
        "world_registry": [
            {
                "world_id": w.world_id,
                "charter_label": w.charter_label,
                "scenario_name": w.scenario_name,
                "fit_class": w.fit_class,
                "effect_grid": list(w.effect_grid),
                "weak_fit_severity": w.weak_fit_severity,
                "augsynth_lambda_reg": w.augsynth_lambda_reg,
            }
            for w in cfg.worlds
        ],
        "replicates": replicates,
        "summaries_by_world_arm_effect": summaries,
        "panel_diagnostics_by_world": panel_diag_by_world,
        "weak_fit_vs_a26": weak_compare,
        "weak_fit_severity_summary": severity_summary,
        "hull_strata_summary": hull_strata,
        "null_interval_summary": null_summary,
        "diagnostic_usefulness": diagnostic_usefulness,
        "overall_verdict": overall,
        "findings": findings,
        "promotion_audit_eligible": False,
        "promotion_audit_opened": False,
    }


def write_artifact(
    path: Path | None = None,
    *,
    cfg: D5InstAugsynthAscm003Config | None = None,
) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INST_AUGSYNTH_ASCM_003_results.json"
    )
    payload = build_d5_inst_augsynth_ascm_003(cfg)
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
        / "D5_INST_AUGSYNTH_ASCM_003_results.json"
    )
    report_path = report_path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "D5_INST_AUGSYNTH_ASCM_003_REPORT.md"
    )
    p = json.loads(results_path.read_text(encoding="utf-8"))
    cfg = p.get("config", {})
    weak = p.get("weak_fit_vs_a26", {})
    hull = p.get("hull_strata_summary", {})
    sev = p.get("weak_fit_severity_summary", {})
    diag = p.get("diagnostic_usefulness", {})
    null = p.get("null_interval_summary", {})
    fid = p.get("fidelity_audit", {})

    def _fmt(v: Any) -> str:
        if v is None:
            return "—"
        if isinstance(v, float) and not np.isfinite(v):
            return "—"
        return str(v)

    lines = [
        "# D5-INST-AUGSYNTH-ASCM-003 — stratified AugSynth/ASCM OC (diagnostics + fidelity)",
        "",
        f"**Artifact:** [`archives/D5_INST_AUGSYNTH_ASCM_003_results.json`](archives/D5_INST_AUGSYNTH_ASCM_003_results.json)  ",
        f"**Harness:** `panel_exp/validation/track_d_d5_inst_augsynth_ascm_003.py`  ",
        f"**Diagnostics:** [`../validation/scm_augsynth_diagnostics.py`](../validation/scm_augsynth_diagnostics.py) (D5-DIAG-SCM-AUGSYNTH-001)  ",
        f"**Fidelity audit:** [`../AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md`](../AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md)  ",
        "",
        f"**Overall verdict:** `{p.get('overall_verdict')}`  ",
        f"**Runtime (s):** `{float(p['runtime_seconds']):.1f}`  "
        if p.get("runtime_seconds") is not None
        else "**Runtime (s):** `—`  ",
        f"**Promotion audit eligible:** `{p.get('promotion_audit_eligible')}`",
        "",
        "## 1. Purpose",
        "",
        "Run the next stratified operating-characteristic (OC) battery for **AugSynth/ASCM vs A26** "
        "after D5-DIAG-SCM-AUGSYNTH-001 and the implementation fidelity audit. Characterize when "
        "AugSynth helps, when it fails, and which D5-DIAG fields are useful for future threshold "
        "calibration — **without promotion or threshold finalization**.",
        "",
        "## 2. Design",
        "",
        f"- Monte Carlo replicates: **n_mc={cfg.get('n_mc')}** (target ≥14; "
        f"reduction reason: {cfg.get('n_mc_reduction_reason') or 'none'})",
        f"- Worlds: **{len(p.get('world_registry', []))}** (ASCM-002 charter + weak-fit severity grid + "
        "donor sparsity/richness extensions + ridge-λ sensitivity worlds)",
        "- Primary arms: A26 SCM+UnitJackKnife, AugSynth point, AugSynth+UnitJackKnife",
        "- Secondary diagnostic arms: AugSynth+Conformal, AugSynth+Kfold (inference context only)",
        "- Panel diagnostics: full D5-DIAG field set on every replicate",
        "",
        "## 3. Worlds / strata",
        "",
        "| world_id | fit_class | weak_fit_severity | lambda_reg |",
        "|----------|-----------|-------------------|------------|",
    ]
    for w in p.get("world_registry", []):
        lines.append(
            f"| `{w['world_id']}` | {w['fit_class']} | "
            f"{w.get('weak_fit_severity') or '—'} | {w.get('augsynth_lambda_reg', 0)} |"
        )

    lines.extend(
        [
            "",
            "## 4. Methods compared",
            "",
            "| Arm | Role |",
            "|-----|------|",
            "| `a26_scm_unit_jackknife` | Baseline / null-monitor reference |",
            "| `augsynth_cvxpy_point` | AugSynth point comparator |",
            "| `augsynth_cvxpy_unit_jackknife` | AugSynth inference comparator |",
            "| `augsynth_cvxpy_conformal` | Diagnostic-only (elevated null FPR historically) |",
            "| `augsynth_cvxpy_kfold` | Diagnostic-only |",
            "",
            "## 5. Diagnostics included",
            "",
            "Panel (D5-DIAG): "
            + ", ".join(f"`{f}`" for f in diag.get("panel_diagnostic_fields_tracked", [])),
            "",
            "Instrument: "
            + ", ".join(
                f"`{f}`" for f in diag.get("instrument_diagnostic_fields_tracked", [])
            ),
            "",
            "Conflict vs A26: "
            + ", ".join(
                f"`{f}`" for f in diag.get("conflict_diagnostic_fields_tracked", [])
            ),
            "",
            "## 6. Results summary",
            "",
            f"- AugSynth point beats A26 MAE on **{weak.get('augsynth_beats_a26_weak_fit_world_count', 0)}/"
            f"{weak.get('weak_fit_world_count', 0)}** weak-fit worlds @ 8% injection.",
            f"- Inside-hull AugSynth wins: **{hull.get('inside_hull', {}).get('augsynth_beats_a26_count', 0)}/"
            f"{hull.get('inside_hull', {}).get('world_count', 0)}**.",
            f"- Outside-hull AugSynth wins: **{hull.get('outside_hull', {}).get('augsynth_beats_a26_count', 0)}/"
            f"{hull.get('outside_hull', {}).get('world_count', 0)}**.",
            "",
            "## 7. Weak-fit recovery",
            "",
        ]
    )
    for sev_key, block in sorted(sev.items()):
        lines.append(
            f"- **{sev_key}**: AugSynth beats A26 on "
            f"{block.get('augsynth_beats_a26_count', 0)}/{block.get('world_count', 0)} worlds."
        )
    lines.extend(
        [
            "",
            "## 8. Inside-hull vs outside-hull behavior",
            "",
            "Inside-hull strata aggregate worlds with fit classes "
            f"{sorted(INSIDE_HULL_FIT_CLASSES)}; outside-hull uses `{sorted(OUTSIDE_HULL_FIT_CLASSES)}`.",
            "",
            "| stratum | AugSynth beats A26 @ 8% | world count |",
            "|---------|-------------------------|-------------|",
            f"| inside | {hull.get('inside_hull', {}).get('augsynth_beats_a26_count', 0)} | "
            f"{hull.get('inside_hull', {}).get('world_count', 0)} |",
            f"| outside | {hull.get('outside_hull', {}).get('augsynth_beats_a26_count', 0)} | "
            f"{hull.get('outside_hull', {}).get('world_count', 0)} |",
            "",
            "## 9. Null FPR / interval behavior",
            "",
            "| arm | mean null interval-exclusion FPR | mean null half-width |",
            "|-----|----------------------------------|----------------------|",
        ]
    )
    for arm in (
        "a26_scm_unit_jackknife",
        "augsynth_cvxpy_point",
        "augsynth_cvxpy_unit_jackknife",
        "augsynth_cvxpy_conformal",
    ):
        block = null.get(arm, {})
        fpr = (block.get("null_interval_exclusion_fpr") or {}).get("mean")
        hw = (block.get("mean_interval_halfwidth_at_null") or {}).get("mean")
        lines.append(f"| `{arm}` | {_fmt(fpr)} | {_fmt(hw)} |")

    lines.extend(
        [
            "",
            "## 10. Diagnostic usefulness",
            "",
            f"- Positive `fit_improvement_rmse` → AugSynth wins rate: "
            f"**{_fmt(diag.get('fit_improvement_positive_and_aug_wins_rate'))}** "
            f"(n={diag.get('fit_improvement_positive_world_count', 0)} worlds).",
            f"- High hull stress (z≥2) → AugSynth loses rate: "
            f"**{_fmt(diag.get('high_hull_stress_aug_loses_rate'))}** "
            f"(n={diag.get('high_hull_stress_world_count', 0)} worlds).",
            "- Provisional threshold calibration: fields emitted; **numeric cutoffs not finalized**.",
            "",
            "## 11. Fidelity-audit caveats carried forward",
            "",
            f"Audit **{fid.get('audit_id')}** verdict: `{fid.get('verdict')}`.",
            "",
        ]
    )
    for c in fid.get("caveats", []):
        lines.append(f"- **{c.get('id')}**: {c.get('summary')}")

    lines.extend(
        [
            "",
            "## 12. Decision / verdict",
            "",
            f"**`{p.get('overall_verdict')}`** — see findings below. No promotion audit opened.",
            "",
            "## 13. Guardrails",
            "",
            "| Guardrail | Status |",
            "|-----------|--------|",
            "| Promotion | **No** |",
            "| Threshold finalization | **No** |",
            "| Eligibility change | **No** |",
            "| Estimator behavior change | **No** |",
            "| Inference behavior change | **No** |",
            "| TrustReport / F-DECISION | **No change** |",
            "| CalibrationSignal / MMM | **No** |",
            "",
            "## 14. Next step",
            "",
            "Continue diagnostic-comparator lane with inference-pairing ADR if "
            "`promising_needs_inference_calibration`; otherwise extend threshold calibration "
            "on D5-DIAG fields (ASCM-004+). Optional fidelity follow-ups: G4 SCM-leg alignment, "
            "G8 hull definition — separate implementation PRs only.",
            "",
            "## Findings",
            "",
        ]
    )
    for f in p.get("findings", []):
        sev = f.get("severity")
        prefix = f" ({sev})" if sev else ""
        lines.append(f"- **{f.get('id', 'FIND')}**{prefix}: {f.get('summary')}")

    lines.extend(
        [
            "",
            "## Weak-fit comparison detail",
            "",
            "| world | AugSynth beats A26 MAE @ 8% | A26 JK null FPR | AugSynth JK null FPR |",
            "|-------|------------------------------|-----------------|----------------------|",
        ]
    )
    for row in weak.get("weak_fit_comparisons", []):
        lines.append(
            f"| `{row.get('world_id')}` | {row.get('augsynth_beats_a26_mae')} | "
            f"{row.get('a26_jk_null_fpr')} | {row.get('augsynth_jk_null_fpr')} |"
        )
    lines.append("")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


if __name__ == "__main__":
    archive_cfg = D5InstAugsynthAscm003Config(
        n_mc=4,
        n_mc_reduction_reason=(
            "19-world grid runtime in dev environment; harness default n_mc=14 for replay"
        ),
    )
    out = write_artifact(cfg=archive_cfg)
    rep = write_report(results_path=out)
    print(f"Wrote {out}")
    print(f"Wrote {rep}")
