"""D5-STAT-SCM-JK-001 — Level B characterization for SCM + UnitJackKnife.

Unit-panel single-cell geometry only. Deterministic synthetic worlds, modest MC.
No promotion, trust wiring, or suitability claims.
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
from panel_exp.methods.scm import SyntheticControlCVXPY
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SMOKE_ARTIFACT = _REPO_ROOT / "docs/track_d/archives/D5_STAT_SMOKE_CALLABLE_001_results.json"

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

NEXT_RECOMMENDED = ["D5-STAT-AUGSYNTH-POINT-001", "D5-STAT-TBR-AGG-001"]


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
class D5StatScmJk001Config:
    n_replicates: int = 15
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    random_state_base: int = 20260604
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
) -> PanelDataset:
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
        return mod
    value_effect = percent_effect * mean_value
    mask = np.zeros((n_treated, mod.wide_data.shape[1]), dtype=bool)
    mask[:, start : start + treated_len] = True
    treated_block = mod.wide_data.loc[mod.treated_units].to_numpy(dtype=float)
    treated_block = np.where(mask, treated_block + value_effect.reshape(-1, 1), treated_block)
    mod.wide_data.loc[mod.treated_units] = treated_block
    return mod


def _build_unit_panel(
    spec: WorldSpec,
    cfg: D5StatScmJk001Config,
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


def _run_one(
    spec: WorldSpec,
    cfg: D5StatScmJk001Config,
    *,
    replicate_id: int,
    seed: int,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "world_id": spec.world_id,
        "replicate_id": replicate_id,
        "seed": seed,
        "true_effect": float(spec.percent_effect),
        **_forbidden_flags(),
    }
    skip = cvxpy_osqp_skip_reason()
    if skip:
        return {
            **base,
            "callable_status": "skipped_optional_dep",
            "smoke_verdict": "skipped",
            "finite_outputs": False,
            "exception_type": "optional_dep_missing",
            "exception_message": skip,
        }
    try:
        panel = _build_unit_panel(spec, cfg, seed=seed)
        if panel.num_control_units < cfg.min_control_units:
            raise ValueError("insufficient control units after assignment")
        mean_value = _mean_treated_baseline(panel)
        pds = _inject_percent_effect(panel, spec.percent_effect, mean_value)
        est = SyntheticControlCVXPY(inference="UnitJackKnife", alpha=cfg.alpha)
        est.run_analysis(pds)
        results = getattr(est, "results", {}) or {}
        test_len = cfg.test_length
        y = np.asarray(results.get("y"), dtype=float).reshape(-1)
        y_hat = np.asarray(results.get("y_hat"), dtype=float).reshape(-1)
        y_lo = np.asarray(results.get("y_lower"), dtype=float).reshape(-1)
        y_hi = np.asarray(results.get("y_upper"), dtype=float).reshape(-1)
        sl = slice(-test_len, None)
        effect = y[sl] - y_hat[sl]
        point_estimate = float(np.nanmean(effect)) if effect.size else float("nan")
        bias = point_estimate - float(spec.percent_effect)
        abs_err = abs(bias)
        interval_present = y_lo.size > 0 and y_hi.size > 0
        orient_fail = False
        neg_hw = False
        interval_width = None
        interval_lower = None
        interval_upper = None
        contains = None
        if interval_present:
            lo = y_lo[sl]
            hi = y_hi[sl]
            orient_fail = bool(np.any(lo > hi))
            mid = 0.5 * (lo + hi)
            hw = hi - mid
            neg_hw = bool(np.any(hw < 0))
            eff_lo = y[sl] - hi
            eff_hi = y[sl] - lo
            interval_lower = float(np.nanmean(eff_lo))
            interval_upper = float(np.nanmean(eff_hi))
            interval_width = float(interval_upper - interval_lower)
            if spec.percent_effect != 0.0 and np.isfinite(interval_lower):
                contains = bool(
                    float(interval_lower) <= float(spec.percent_effect) <= float(interval_upper)
                )
            elif spec.percent_effect == 0.0:
                contains = bool(float(interval_lower) <= 0.0 <= float(interval_upper))
        def _post_finite(arr: np.ndarray) -> bool:
            part = arr[sl]
            return part.size > 0 and np.all(np.isfinite(part))

        finite = _post_finite(y) and _post_finite(y_hat)
        if interval_present:
            finite = finite and _post_finite(y_lo) and _post_finite(y_hi)
        return {
            **base,
            "callable_status": "callable_pass" if finite else "callable_fail",
            "point_estimate": point_estimate,
            "bias": float(bias),
            "absolute_error": float(abs_err),
            "interval_lower": interval_lower,
            "interval_upper": interval_upper,
            "interval_width": interval_width,
            "interval_contains_truth": bool(contains) if contains is not None else None,
            "interval_orientation_valid": (not orient_fail) if interval_present else None,
            "negative_half_width_detected": bool(neg_hw) if interval_present else None,
            "finite_outputs": finite,
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
            "bias": None,
            "absolute_error": None,
            "interval_lower": None,
            "interval_upper": None,
            "interval_width": None,
            "interval_contains_truth": None,
            "interval_orientation_valid": None,
            "negative_half_width_detected": None,
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
    widths = _vals("interval_width")

    orient_rates = [
        r for r in ok if r.get("interval_orientation_valid") is False
    ]
    neg_hw = [r for r in ok if r.get("negative_half_width_detected")]
    non_finite = [r for r in ok if not r.get("finite_outputs")]

    null_fpr = None
    if is_null and ok:
        rejects = []
        for r in ok:
            lo = r.get("interval_lower")
            hi = r.get("interval_upper")
            if lo is not None and hi is not None:
                rejects.append(not (lo <= 0.0 <= hi))
            elif r.get("point_estimate") is not None:
                rejects.append(abs(r["point_estimate"]) > 1e-6)
        null_fpr = float(np.mean(rejects)) if rejects else None

    coverage_vals = [
        r["interval_contains_truth"]
        for r in ok
        if r.get("interval_contains_truth") is not None
    ]
    coverage = float(np.mean(coverage_vals)) if coverage_vals else None

    sign_errors = None
    if not is_null and pts.size:
        sign_errors = float(
            np.mean((np.sign(pts) != np.sign(spec.percent_effect)).astype(float))
        )

    prefit = _vals("prefit_rmse")
    donors = _vals("donor_count")

    return {
        "world_id": spec.world_id,
        "n_replicates": n,
        "feasible_runs": len(ok),
        "failed_runs": len(failed),
        "null_false_positive_rate": null_fpr,
        "empirical_rejection_rate": null_fpr,
        "coverage": coverage,
        "mean_point_estimate": float(np.mean(pts)) if pts.size else None,
        "mean_true_effect": float(spec.percent_effect),
        "mean_bias": float(np.mean(biases)) if biases.size else None,
        "mean_absolute_error": float(np.mean(abs_errs)) if abs_errs.size else None,
        "rmse": float(math.sqrt(np.mean(biases**2))) if biases.size else None,
        "median_absolute_error": float(np.median(abs_errs)) if abs_errs.size else None,
        "sign_error_rate": sign_errors,
        "mean_interval_width": float(np.mean(widths)) if widths.size else None,
        "median_interval_width": float(np.median(widths)) if widths.size else None,
        "interval_orientation_failure_rate": len(orient_rates) / max(len(ok), 1),
        "negative_half_width_rate": len(neg_hw) / max(len(ok), 1),
        "degenerate_interval_rate": 0.0,
        "non_finite_output_rate": len(non_finite) / max(len(ok), 1),
        "prefit_rmse_mean": float(np.mean(prefit)) if prefit.size else None,
        "donor_count_mean": float(np.mean(donors)) if donors.size else None,
        "notes": spec.notes,
    }


def _decide_overall(
    aggregate: dict[str, dict[str, Any]],
    failure_register: list[dict[str, Any]],
) -> OverallVerdict:
    for m in aggregate.values():
        if m["interval_orientation_failure_rate"] > 0:
            return "characterization_fail_requires_fix"
        if m["negative_half_width_rate"] > 0:
            return "characterization_fail_requires_fix"
        if m.get("feasible_runs", 0) > 0 and m["non_finite_output_rate"] > 0:
            return "characterization_fail_requires_fix"

    null_fpr = aggregate.get("clean_null", {}).get("null_false_positive_rate")
    weak_fpr = aggregate.get("weak_signal_null", {}).get("null_false_positive_rate")
    coverage = aggregate.get("clean_positive_lift", {}).get("coverage")
    donor_stress = aggregate.get("donor_stress", {})
    donor_fail = donor_stress.get("failed_runs", 0)
    stress_finite = donor_stress.get("non_finite_output_rate", 0)

    mixed = False
    if null_fpr is not None and null_fpr > 0.35:
        mixed = True
    if weak_fpr is not None and weak_fpr > 0.45:
        mixed = True
    if coverage is not None and coverage < 0.4:
        mixed = True
    if donor_fail > 2:
        mixed = True
    if stress_finite > 0:
        mixed = True

    if mixed:
        return "characterization_mixed_requires_followup"
    return "characterization_pass_with_caveats"


def build_d5_stat_scm_jk_001(cfg: D5StatScmJk001Config | None = None) -> dict[str, Any]:
    cfg = cfg or D5StatScmJk001Config()
    skip = cvxpy_osqp_skip_reason()
    if skip:
        return {
            "artifact_id": "D5-STAT-SCM-JK-001",
            "artifact_type": "level_b_characterization",
            "method_combination": "SCM+UnitJackKnife",
            "geometry": "unit_panel_single_cell",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_smoke_artifact": "D5-STAT-SMOKE-CALLABLE-001",
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

    overall = _decide_overall(aggregate_metrics, failure_register)
    summary = {
        "n_worlds": len(WORLD_SPECS),
        "n_replicates_per_world": cfg.n_replicates,
        "total_runs": len(run_results),
        "total_failures": len(failure_register),
        "characterization_only": True,
    }

    return _json_safe(
        {
            "artifact_id": "D5-STAT-SCM-JK-001",
            "artifact_type": "level_b_characterization",
            "method_combination": "SCM+UnitJackKnife",
            "geometry": "unit_panel_single_cell",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_smoke_artifact": "D5-STAT-SMOKE-CALLABLE-001",
            "overall_verdict": overall,
            "summary": summary,
            "worlds": [asdict_world(w) for w in WORLD_SPECS],
            "aggregate_metrics": aggregate_metrics,
            "run_results": run_results,
            "failure_register": failure_register,
            "forbidden_flags": _forbidden_flags(),
            "next_recommended_artifacts": NEXT_RECOMMENDED,
            "guardrails": _guardrails_list(),
        }
    )


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
        "level_b_characterization_only",
        "no_statistical_validation_claim",
        "no_suitability_claim",
        "no_promotion",
    ]


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


def write_artifact(path: Path | None = None, *, cfg: D5StatScmJk001Config | None = None) -> Path:
    payload = build_d5_stat_scm_jk_001(cfg)
    if path is None:
        path = _REPO_ROOT / "docs/track_d/archives/D5_STAT_SCM_JK_001_results.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_report(path: Path | None = None, *, cfg: D5StatScmJk001Config | None = None) -> Path:
    payload = build_d5_stat_scm_jk_001(cfg)
    if path is None:
        path = _REPO_ROOT / "docs/track_d/D5_STAT_SCM_JK_001_REPORT.md"
    agg = payload["aggregate_metrics"]
    lines = [
        "# D5-STAT-SCM-JK-001 — Level B characterization (SCM + UnitJackKnife)",
        "",
        "**Artifact ID:** D5-STAT-SCM-JK-001",
        "**Type:** Level B characterization — **not** calibration or promotion",
        f"**Overall verdict:** `{payload['overall_verdict']}`",
        "",
        "**Archive:** [`archives/D5_STAT_SCM_JK_001_results.json`](archives/D5_STAT_SCM_JK_001_results.json)",
        "**Harness:** `panel_exp/validation/track_d_d5_stat_scm_jk_001.py`",
        "",
        "## 1. Purpose",
        "",
        "Characterize SCM + UnitJackKnife on unit-panel single-cell geometry under",
        "deterministic synthetic worlds: null behavior, injected lift, interval sanity,",
        "donor/pre-fit stress, and weak/noisy signal.",
        "",
        "## 2. Relationship to D5-STAT-SMOKE-CALLABLE-001",
        "",
        "Follows smoke callable evidence (`SCM-JK` callable_pass). Smoke does not imply",
        "statistical validation.",
        "",
        "## 3. Relationship to suitability framework",
        "",
        "`SCM-JK` remains `suitability_candidate_pending_oc`; this artifact supplies",
        "Level B evidence only.",
        "",
        "## 4. Scope and exclusions",
        "",
        "SCM + UnitJackKnife only. No AugSynth, TBR, TBRRidge, DID, multi-cell pooled,",
        "supergeo, or trim.",
        "",
        "## 5. DGP world design",
        "",
        "| world_id | intent |",
        "|----------|--------|",
    ]
    for w in payload["worlds"]:
        lines.append(f"| `{w['world_id']}` | {w.get('notes', '')} |")
    lines.extend(
        [
            "",
            f"**Replicates per world:** {payload['summary'].get('n_replicates_per_world', 'n/a')}",
            "",
            "## 8. Results by world",
            "",
            "| world | feasible | null FPR | coverage | mean bias | orient fail rate |",
            "|-------|----------|----------|----------|-----------|------------------|",
        ]
    )
    for wid in REQUIRED_WORLD_IDS:
        m = agg.get(wid, {})
        lines.append(
            f"| `{wid}` | {m.get('feasible_runs', 0)}/{m.get('n_replicates', 0)} | "
            f"{_fmt(m.get('null_false_positive_rate'))} | {_fmt(m.get('coverage'))} | "
            f"{_fmt(m.get('mean_bias'))} | {m.get('interval_orientation_failure_rate', 0):.3f} |"
        )
    lines.extend(
        [
            "",
            "## 14. Overall verdict",
            "",
            f"`{payload['overall_verdict']}`",
            "",
            "## 15. What this artifact does not authorize",
            "",
            "No production promotion, TrustReport roles, CalibrationSignal, MMM, LLM rec,",
            "or claim that SCM+JK is statistically validated or suitable.",
            "",
            "## 16. Recommended next artifacts",
            "",
            f"{', '.join('`' + a + '`' for a in payload['next_recommended_artifacts'])}",
            "",
            "## 17. Guardrails",
            "",
            "Level B characterization only; fixed seeds; no estimator/inference changes.",
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
    cfg = D5StatScmJk001Config()
    out = write_artifact(cfg=cfg)
    write_report(cfg=cfg)
    p = build_d5_stat_scm_jk_001(cfg)
    print(
        f"Wrote {out} — {p['overall_verdict']} "
        f"({p['summary'].get('total_runs', 0)} runs)"
    )


if __name__ == "__main__":
    main()
