"""D5-STAT-AUGSYNTH-POINT-001 — Level B characterization for AugSynthCVXPY point.

Unit-panel single-cell, point estimate only (no JK/Conformal/KFold uncertainty).
No promotion or suitability claims. Compare to injected truth, not SCM.
"""

from __future__ import annotations

import copy
import json
import math
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.design.assign import greedy_match_markets
from panel_exp.methods.scm import AugSynthCVXPY
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

_REPO_ROOT = Path(__file__).resolve().parents[2]

OverallVerdict = Literal[
    "characterization_pass_with_caveats",
    "characterization_mixed_requires_followup",
    "characterization_fail_requires_fix",
]

REQUIRED_WORLD_IDS = (
    "clean_null",
    "clean_positive_lift",
    "weak_signal_null",
    "noisy_positive_lift",
    "donor_stress",
    "outside_hull_or_poor_prefit",
    "post_shock_null",
)

NEXT_RECOMMENDED = ["D5-STAT-TBR-AGG-001", "D5-STAT-DID-BOOTSTRAP-001"]

NULL_DIRECTIONAL_THRESHOLD = 1.0


@dataclass(frozen=True)
class WorldSpec:
    world_id: str
    scenario_name: str = "scm_low_signal"
    percent_effect: float = 0.0
    n_geos: int = 16
    n_periods: int = 44
    treatment_start: int = 32
    treatment_probability: float = 0.35
    scenario_overrides: dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass(frozen=True)
class D5StatAugSynthPoint001Config:
    n_replicates: int = 15
    train_length: int = 28
    test_length: int = 8
    random_state_base: int = 20260605
    min_control_units: int = 4


WORLD_SPECS: tuple[WorldSpec, ...] = (
    WorldSpec("clean_null", percent_effect=0.0, notes="stable null"),
    WorldSpec(
        "clean_positive_lift",
        percent_effect=0.08,
        notes="injected post-period level lift",
    ),
    WorldSpec(
        "weak_signal_null",
        percent_effect=0.0,
        scenario_overrides={"noise_scale": 3.8, "cross_geo_correlation": 0.05},
        notes="low SNR null",
    ),
    WorldSpec(
        "noisy_positive_lift",
        percent_effect=0.08,
        scenario_overrides={"noise_scale": 3.2},
        notes="injected lift under higher noise",
    ),
    WorldSpec(
        "donor_stress",
        percent_effect=0.0,
        n_geos=14,
        treatment_probability=0.42,
        notes="fewer geos / thinner donor pool",
    ),
    WorldSpec(
        "outside_hull_or_poor_prefit",
        scenario_name="scm_trend_mismatch",
        percent_effect=0.0,
        notes="trend mismatch — harder pre-fit",
    ),
    WorldSpec(
        "post_shock_null",
        scenario_name="scm_structural_break",
        percent_effect=0.0,
        scenario_overrides={"structural_break_shift": 22.0},
        notes="structural break under null",
    ),
)


def _forbidden_flags() -> dict[str, bool]:
    return {
        "promotion_allowed": False,
        "trust_role_allowed": False,
        "calibration_signal_allowed": False,
        "mmm_allowed": False,
        "llm_recommendation_allowed": False,
        "suitability_claim_allowed": False,
        "governed_uncertainty_allowed": False,
    }


def _assign_greedy_pre_period(
    wide: Any,
    *,
    n_pre: int,
    seed: int,
    treatment_probability: float,
) -> list[str]:
    panel = PanelDataset(wide.copy())
    design = greedy_match_markets(
        func_to_optimize="corr",
        treatment_probability=treatment_probability,
        random_state=seed,
    )
    groups = design.assign(
        panel_data=panel,
        pre_treatment_period=TimePeriod(0, n_pre),
        n_test_grps=1,
    )
    treated = [u for units in groups.values() for u in units]
    if not treated:
        raise ValueError("assignment produced no treated units")
    return treated


def _mean_treated_baseline(panel: PanelDataset) -> np.ndarray:
    return panel.wide_data.loc[panel.treated_units].mean(axis=1).values.astype(float)


def _inject_percent_effect(
    panel: PanelDataset,
    percent_effect: float,
    mean_value: np.ndarray,
) -> tuple[PanelDataset, float]:
    """Return modified panel and injected level effect (known truth in level units)."""
    mod = copy.deepcopy(panel)
    start = int(mod.treated_start_idxs[0])
    end_idx = int(mod.treated_end_idxs[0])
    if end_idx >= mod.times.shape[0]:
        end_idx = mod.times.shape[0] - 1
    treated_len = end_idx - start + 1
    n_treated = len(mod.treated_units)
    if n_treated == 1:
        delta = float(percent_effect * np.mean(mean_value))
        mod.wide_data.loc[mod.treated_units, mod.times[start : start + treated_len]] += delta
        return mod, delta
    value_effect = percent_effect * mean_value
    mask = np.zeros((n_treated, mod.wide_data.shape[1]), dtype=bool)
    mask[:, start : start + treated_len] = True
    treated_block = mod.wide_data.loc[mod.treated_units].to_numpy(dtype=float)
    treated_block = np.where(mask, treated_block + value_effect.reshape(-1, 1), treated_block)
    mod.wide_data.loc[mod.treated_units] = treated_block
    injected = float(np.mean(value_effect)) if percent_effect != 0.0 else 0.0
    return mod, injected


def _build_unit_panel(
    spec: WorldSpec,
    cfg: D5StatAugSynthPoint001Config,
    *,
    seed: int,
) -> PanelDataset:
    base = RECOVERY_SCENARIO_REGISTRY[spec.scenario_name]
    scenario = replace(
        base,
        random_state=seed,
        n_geos=spec.n_geos,
        n_periods=spec.n_periods,
        treatment_start=spec.treatment_start,
        true_effect=0.0,
        **spec.scenario_overrides,
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    treated = _assign_greedy_pre_period(
        wide,
        n_pre=cfg.train_length,
        seed=seed,
        treatment_probability=spec.treatment_probability,
    )
    end = cfg.train_length + cfg.test_length
    return PanelDataset(
        wide.iloc[:, :end].copy(),
        treated_periods=[TimePeriod(cfg.train_length, end - 1) for _ in treated],
        treated_units=treated,
    )


def _prefit_rmse(results: dict[str, Any], train_length: int) -> float | None:
    y = np.asarray(results.get("y"), dtype=float)
    y_hat = np.asarray(results.get("y_hat"), dtype=float)
    if y.size == 0 or y_hat.size == 0 or train_length <= 0:
        return None
    pre = slice(0, min(train_length, y.size, y_hat.size))
    diff = y[pre] - y_hat[pre]
    if not np.any(np.isfinite(diff)):
        return None
    return float(math.sqrt(np.nanmean(diff**2)))


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.floating, float)):
        v = float(obj)
        return v if np.isfinite(v) else None
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    return obj


def _run_one(
    spec: WorldSpec,
    cfg: D5StatAugSynthPoint001Config,
    *,
    replicate_id: int,
    seed: int,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "world_id": spec.world_id,
        "replicate_id": replicate_id,
        "seed": seed,
        "percent_effect": float(spec.percent_effect),
        "interval_present": False,
        "interval_validation_applicable": False,
        **_forbidden_flags(),
    }
    skip = cvxpy_osqp_skip_reason()
    if skip:
        return {
            **base,
            "callable_status": "skipped_optional_dep",
            "finite_outputs": False,
            "true_effect": None,
            "exception_type": "optional_dep_missing",
            "exception_message": skip,
        }
    try:
        panel = _build_unit_panel(spec, cfg, seed=seed)
        if panel.num_control_units < cfg.min_control_units:
            raise ValueError("insufficient control units after assignment")
        mean_value = _mean_treated_baseline(panel)
        pds, injected_level = _inject_percent_effect(
            panel, spec.percent_effect, mean_value
        )
        est = AugSynthCVXPY(inference=None)
        est.run_analysis(pds)
        results = getattr(est, "results", {}) or {}
        sl = slice(-cfg.test_length, None)
        y = np.asarray(results.get("y"), dtype=float).reshape(-1)
        y_hat = np.asarray(results.get("y_hat"), dtype=float).reshape(-1)
        effect = y[sl] - y_hat[sl]
        point_estimate = float(np.nanmean(effect)) if effect.size else float("nan")
        true_effect = float(injected_level)
        bias = point_estimate - true_effect
        abs_err = abs(bias)
        sq_err = bias**2
        is_null = abs(true_effect) < 1e-12
        if is_null:
            sign_correct = abs(point_estimate) < NULL_DIRECTIONAL_THRESHOLD
        else:
            sign_correct = (
                np.isfinite(point_estimate)
                and np.sign(point_estimate) == np.sign(true_effect)
            )
        recovery = None
        if abs(true_effect) > 1e-12 and np.isfinite(point_estimate):
            recovery = float(point_estimate / true_effect)
        finite = effect.size > 0 and np.all(np.isfinite(effect))
        return {
            **base,
            "callable_status": "callable_pass" if finite else "callable_fail",
            "point_estimate": point_estimate,
            "true_effect": true_effect,
            "bias": float(bias),
            "absolute_error": float(abs_err),
            "squared_error": float(sq_err),
            "sign_correct": bool(sign_correct),
            "point_recovery_ratio": recovery,
            "finite_outputs": bool(finite),
            "prefit_rmse": _prefit_rmse(results, cfg.train_length),
            "donor_count": int(pds.num_control_units),
            "exception_type": None,
            "exception_message": None,
        }
    except Exception as exc:
        return {
            **base,
            "callable_status": "callable_fail",
            "point_estimate": None,
            "true_effect": None,
            "bias": None,
            "absolute_error": None,
            "squared_error": None,
            "sign_correct": None,
            "point_recovery_ratio": None,
            "finite_outputs": False,
            "prefit_rmse": None,
            "donor_count": None,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)[:300],
        }


def _aggregate_world(runs: list[dict[str, Any]], spec: WorldSpec) -> dict[str, Any]:
    ok = [r for r in runs if r.get("callable_status") == "callable_pass"]
    failed = [r for r in runs if r.get("callable_status") != "callable_pass"]
    n = len(runs)
    is_null = abs(spec.percent_effect) < 1e-12

    def _vals(key: str) -> np.ndarray:
        return np.array(
            [r[key] for r in ok if r.get(key) is not None and np.isfinite(r[key])],
            dtype=float,
        )

    pts = _vals("point_estimate")
    biases = _vals("bias")
    abs_errs = _vals("absolute_error")
    recovery = _vals("point_recovery_ratio")
    non_finite = [r for r in ok if not r.get("finite_outputs")]

    null_dir_fpr = None
    if is_null and ok:
        flags = [not r.get("sign_correct", True) for r in ok]
        null_dir_fpr = float(np.mean(flags)) if flags else None

    sign_errors = None
    if not is_null and ok:
        sign_errors = float(np.mean([not r.get("sign_correct", False) for r in ok]))

    over_rate = under_rate = None
    if not is_null and ok:
        over = []
        under = []
        for r in ok:
            pe = r.get("point_estimate")
            te = r.get("true_effect")
            if pe is None or te is None or abs(te) < 1e-12:
                continue
            over.append(abs(pe) > abs(te))
            under.append(abs(pe) < abs(te))
        over_rate = float(np.mean(over)) if over else None
        under_rate = float(np.mean(under)) if under else None

    prefit = _vals("prefit_rmse")
    donors = _vals("donor_count")

    return {
        "world_id": spec.world_id,
        "n_replicates": n,
        "feasible_runs": len(ok),
        "failed_runs": len(failed),
        "callable_failure_rate": len(failed) / max(n, 1),
        "mean_point_estimate": float(np.mean(pts)) if pts.size else None,
        "median_point_estimate": float(np.median(pts)) if pts.size else None,
        "mean_true_effect": float(np.mean(_vals("true_effect"))) if ok else None,
        "mean_bias": float(np.mean(biases)) if biases.size else None,
        "mean_absolute_error": float(np.mean(abs_errs)) if abs_errs.size else None,
        "rmse": float(math.sqrt(np.mean(biases**2))) if biases.size else None,
        "median_absolute_error": float(np.median(abs_errs)) if abs_errs.size else None,
        "sign_error_rate": sign_errors,
        "null_false_positive_directional_rate": null_dir_fpr,
        "point_recovery_ratio_mean": float(np.mean(recovery)) if recovery.size else None,
        "point_recovery_ratio_median": float(np.median(recovery)) if recovery.size else None,
        "overstatement_rate": over_rate,
        "understatement_rate": under_rate,
        "non_finite_output_rate": len(non_finite) / max(len(ok), 1),
        "prefit_rmse_mean": float(np.mean(prefit)) if prefit.size else None,
        "donor_count_mean": float(np.mean(donors)) if donors.size else None,
        "notes": spec.notes,
    }


def _decide_overall(
    aggregate: dict[str, dict[str, Any]],
) -> OverallVerdict:
    core = ("clean_null", "clean_positive_lift")
    for wid in core:
        m = aggregate.get(wid, {})
        if m.get("callable_failure_rate", 0) > 0.1:
            return "characterization_fail_requires_fix"
        if m.get("feasible_runs", 0) > 0 and m.get("non_finite_output_rate", 0) > 0:
            return "characterization_fail_requires_fix"

    mixed = False
    null_dir = aggregate.get("clean_null", {}).get(
        "null_false_positive_directional_rate"
    )
    if null_dir is not None and null_dir > 0.35:
        mixed = True
    weak_dir = aggregate.get("weak_signal_null", {}).get(
        "null_false_positive_directional_rate"
    )
    if weak_dir is not None and weak_dir > 0.45:
        mixed = True
    rec = aggregate.get("clean_positive_lift", {}).get("point_recovery_ratio_mean")
    if rec is not None and (rec < 0.25 or rec > 4.0):
        mixed = True
    sign_err = aggregate.get("clean_positive_lift", {}).get("sign_error_rate")
    if sign_err is not None and sign_err > 0.2:
        mixed = True
    if aggregate.get("donor_stress", {}).get("callable_failure_rate", 0) > 0.25:
        mixed = True
    outside = aggregate.get("outside_hull_or_poor_prefit", {})
    if outside.get("mean_bias") is not None and abs(outside["mean_bias"]) > 5.0:
        mixed = True

    if mixed:
        return "characterization_mixed_requires_followup"
    return "characterization_pass_with_caveats"


def asdict_world(spec: WorldSpec) -> dict[str, Any]:
    return {
        "world_id": spec.world_id,
        "scenario_name": spec.scenario_name,
        "percent_effect": spec.percent_effect,
        "n_geos": spec.n_geos,
        "notes": spec.notes,
    }


def _guardrails_list() -> list[str]:
    return [
        "augsynth_point_only_no_inference_validation",
        "level_b_characterization_only",
        "no_governed_uncertainty_claim",
        "no_suitability_claim",
        "no_promotion",
        "compare_to_injected_truth_not_scm",
    ]


def build_d5_stat_augsynth_point_001(
    cfg: D5StatAugSynthPoint001Config | None = None,
) -> dict[str, Any]:
    cfg = cfg or D5StatAugSynthPoint001Config()
    skip = cvxpy_osqp_skip_reason()
    if skip:
        return _json_safe(
            {
                "artifact_id": "D5-STAT-AUGSYNTH-POINT-001",
                "artifact_type": "level_b_characterization",
                "method_combination": "AugSynthCVXPY point",
                "geometry": "unit_panel_single_cell",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source_smoke_artifact": "D5-STAT-SMOKE-CALLABLE-001",
                "source_scm_jk_artifact": "D5-STAT-SCM-JK-001",
                "overall_verdict": "characterization_fail_requires_fix",
                "summary": {"blocked_reason": skip},
                "worlds": [asdict_world(w) for w in WORLD_SPECS],
                "aggregate_metrics": {},
                "run_results": [],
                "failure_register": [{"reason": skip}],
                "forbidden_flags": _forbidden_flags(),
                "next_recommended_artifacts": NEXT_RECOMMENDED,
                "guardrails": _guardrails_list(),
            }
        )

    run_results: list[dict[str, Any]] = []
    failure_register: list[dict[str, Any]] = []
    aggregate_metrics: dict[str, dict[str, Any]] = {}

    for widx, spec in enumerate(WORLD_SPECS):
        world_runs: list[dict[str, Any]] = []
        for rep in range(cfg.n_replicates):
            row: dict[str, Any] | None = None
            for attempt in range(6):
                seed = cfg.random_state_base + widx * 1000 + rep * 17 + attempt
                candidate = _run_one(spec, cfg, replicate_id=rep, seed=seed)
                if candidate.get("callable_status") == "callable_pass":
                    row = candidate
                    break
                if attempt == 5:
                    row = candidate
            assert row is not None
            world_runs.append(row)
            run_results.append(row)
            if row.get("callable_status") != "callable_pass":
                failure_register.append(
                    {
                        "world_id": spec.world_id,
                        "replicate_id": rep,
                        "exception_type": row.get("exception_type"),
                        "exception_message": row.get("exception_message"),
                    }
                )
        aggregate_metrics[spec.world_id] = _aggregate_world(world_runs, spec)

    overall = _decide_overall(aggregate_metrics)
    return _json_safe(
        {
            "artifact_id": "D5-STAT-AUGSYNTH-POINT-001",
            "artifact_type": "level_b_characterization",
            "method_combination": "AugSynthCVXPY point",
            "geometry": "unit_panel_single_cell",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_smoke_artifact": "D5-STAT-SMOKE-CALLABLE-001",
            "source_scm_jk_artifact": "D5-STAT-SCM-JK-001",
            "overall_verdict": overall,
            "summary": {
                "n_worlds": len(WORLD_SPECS),
                "n_replicates_per_world": cfg.n_replicates,
                "total_runs": len(run_results),
                "total_failures": len(failure_register),
                "characterization_only": True,
                "inference_validation": False,
            },
            "worlds": [asdict_world(w) for w in WORLD_SPECS],
            "aggregate_metrics": aggregate_metrics,
            "run_results": run_results,
            "failure_register": failure_register,
            "forbidden_flags": _forbidden_flags(),
            "next_recommended_artifacts": NEXT_RECOMMENDED,
            "guardrails": _guardrails_list(),
        }
    )


def write_artifact(
    path: Path | None = None,
    *,
    cfg: D5StatAugSynthPoint001Config | None = None,
) -> Path:
    payload = build_d5_stat_augsynth_point_001(cfg)
    if path is None:
        path = _REPO_ROOT / "docs/track_d/archives/D5_STAT_AUGSYNTH_POINT_001_results.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_report(
    path: Path | None = None,
    *,
    cfg: D5StatAugSynthPoint001Config | None = None,
) -> Path:
    payload = build_d5_stat_augsynth_point_001(cfg)
    if path is None:
        path = _REPO_ROOT / "docs/track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md"
    agg = payload["aggregate_metrics"]
    lines = [
        "# D5-STAT-AUGSYNTH-POINT-001 — Level B characterization (AugSynthCVXPY point)",
        "",
        "**Artifact ID:** D5-STAT-AUGSYNTH-POINT-001",
        "**Type:** Level B point characterization — **not** inference validation",
        f"**Overall verdict:** `{payload['overall_verdict']}`",
        "",
        "**Archive:** [`archives/D5_STAT_AUGSYNTH_POINT_001_results.json`](archives/D5_STAT_AUGSYNTH_POINT_001_results.json)",
        "**Harness:** `panel_exp/validation/track_d_d5_stat_augsynth_point_001.py`",
        "",
        "## 1. Purpose",
        "",
        "Characterize AugSynthCVXPY **point** estimates on unit-panel single-cell geometry.",
        "Compare to **injected level truth**, not SCM+JK (prior SCM-JK was mixed).",
        "",
        "## 2. Relationship to D5-STAT-SMOKE-CALLABLE-001",
        "",
        "`AUGSYNTH-POINT` smoke callable_pass — does not authorize inference or suitability.",
        "",
        "## 3. Relationship to D5-STAT-SCM-JK-001",
        "",
        "Parallel Level B battery; SCM-JK is **context only**, not ground truth for AugSynth.",
        "",
        "## 4. Relationship to suitability framework",
        "",
        "`AUGSYNTH-POINT` remains `diagnostic_candidate_pending_oc`; G1–G8 fidelity still open.",
        "",
        "## 5. Scope and exclusions",
        "",
        "Point only. No JK, Conformal, KFold uncertainty, multi-cell, supergeo, trim, TBR, DID.",
        "",
        "## 6. DGP world design",
        "",
        "Same seven-world family as SCM-JK (15 replicates/world, fixed seeds).",
        "",
        "## 7. AugSynthCVXPY execution path",
        "",
        "`AugSynthCVXPY(inference=None)` + `greedy_match_markets` + percent injection.",
        "",
        "## 8. Metrics",
        "",
        "Point recovery ratio vs injected level, null directional false-signal rate, bias/MAE/RMSE,",
        "over/understatement on injected worlds.",
        "",
        "## 9. Results by world",
        "",
        "| world | feasible | null dir. FPR | recovery mean | sign err | callable fail |",
        "|-------|----------|-----------------|---------------|----------|---------------|",
    ]
    for wid in REQUIRED_WORLD_IDS:
        m = agg.get(wid, {})
        lines.append(
            f"| `{wid}` | {m.get('feasible_runs', 0)}/{m.get('n_replicates', 0)} | "
            f"{_fmt(m.get('null_false_positive_directional_rate'))} | "
            f"{_fmt(m.get('point_recovery_ratio_mean'))} | "
            f"{_fmt(m.get('sign_error_rate'))} | "
            f"{m.get('callable_failure_rate', 0):.3f} |"
        )
    lines.extend(
        [
            "",
            "## 17. Overall verdict",
            "",
            f"`{payload['overall_verdict']}`",
            "",
            "## 18. What this artifact does not authorize",
            "",
            "No governed uncertainty, suitability, promotion, TrustReport, CalibrationSignal, MMM, LLM.",
            "No claim that point characterization validates AugSynth inference.",
            "",
            "## 19. Recommended next artifacts",
            "",
            f"{', '.join('`' + a + '`' for a in payload['next_recommended_artifacts'])}",
            "",
            "## 20. Guardrails",
            "",
            "Level B only; interval fields explicitly not applicable.",
            "",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _fmt(val: Any) -> str:
    if val is None:
        return "—"
    if isinstance(val, float):
        return f"{val:.4f}"
    return str(val)


def main() -> None:
    cfg = D5StatAugSynthPoint001Config()
    out = write_artifact(cfg=cfg)
    write_report(cfg=cfg)
    p = build_d5_stat_augsynth_point_001(cfg)
    print(
        f"Wrote {out} — {p['overall_verdict']} "
        f"({p['summary'].get('total_runs', 0)} runs)"
    )


if __name__ == "__main__":
    main()
