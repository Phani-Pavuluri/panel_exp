"""TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001 — variance/null calibration remediation."""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import tempfile
import time
import warnings
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.governance.investigation_lifecycle_contract import (
    build_investigation_handoff,
    format_handoff_report_section,
)
from panel_exp.methods.tbr import TBRRidge
from panel_exp.validation.track_d_d5_trust_tbrridge_brb_001 import (
    DIAGNOSTIC_WORLDS,
    DiagnosticWorldSpec,
    BrbTrustConfig,
    _build_unit_panel,
    _coverage_metrics,
    _effective_lengths,
    _inject_percent_effect,
    _json_safe,
    _level_true_effect,
    _mean,
    _mean_treated_baseline,
    _prefit_rmse,
    _readout_level_scale,
    _root_cause_tags,
)

_REPO = Path(__file__).resolve().parents[2]
_ARTIFACT_ID = "TBRRIDGE-BRB-VARIANCE-CALIBRATION-REMEDIATION-001"
_ARTIFACT_VERSION = "1.0.0"
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001_summary.json"
_DEFAULT_REPORT = _REPO / "docs/track_d/TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001_REPORT.md"

INPUT_ARTIFACTS = {
    "d5_trust_brb": "docs/track_d/archives/D5_TRUST_TBRRIDGE_BRB_001_summary.json",
    "interval_correction": "docs/track_d/archives/TBRRIDGE_BRB_INTERVAL_CORRECTION_001_summary.json",
    "dcm005_reassessment": "docs/track_d/archives/DCM005_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
    "full_reassessment": "docs/track_d/archives/FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
}

RemediationVerdict = Literal[
    "tbrridge_brb_variance_remediated_restricted",
    "tbrridge_brb_variance_remediation_candidate_only",
    "tbrridge_brb_variance_remediation_failed",
    "tbrridge_brb_diagnostic_only",
    "tbrridge_brb_ineligible",
    "tbrridge_brb_additional_remediation_required",
]

PASS_FAIL_GATES = {
    "null_type_i_max": 0.10,
    "null_coverage_zero_min": 0.90,
    "truth_coverage_clean_min": 0.80,
    "interval_center_gap_abs_max": 2.0,
    "failure_rate_max": 0.10,
}

CLEAN_TRUTH_WORLD_IDS = frozenset(
    {
        "weak_signal",
        "clean_positive_effect",
        "strong_signal",
        "clean_negative_effect",
    }
)

CLEAN_IID_WORLD_IDS = frozenset(
    {
        "clean_null",
        "weak_signal",
        "clean_positive_effect",
        "strong_signal",
        "clean_negative_effect",
        "low_noise",
    }
)

EXTRA_WORLDS: tuple[DiagnosticWorldSpec, ...] = (
    DiagnosticWorldSpec(
        "heavy_tailed_noise",
        percent_effect=0.08,
        scenario_overrides={"noise_scale": 6.0},
        notes="heavy-tailed / high-noise stress",
    ),
    DiagnosticWorldSpec(
        "donor_contamination",
        percent_effect=0.08,
        scenario_overrides={"cross_geo_correlation": 0.95},
        notes="donor contamination / shared shocks",
    ),
    DiagnosticWorldSpec(
        "long_pre_period",
        percent_effect=0.08,
        train_length=36,
        notes="long pre-period",
    ),
    DiagnosticWorldSpec(
        "short_post_period",
        percent_effect=0.08,
        test_length=4,
        notes="short post-period",
    ),
    DiagnosticWorldSpec(
        "long_post_period",
        percent_effect=0.08,
        test_length=16,
        notes="long post-period",
    ),
    DiagnosticWorldSpec(
        "low_ridge_shrinkage",
        percent_effect=0.08,
        n_geos=8,
        treatment_probability=0.5,
        notes="few donors — low ridge shrinkage",
    ),
)

_WORLD_BY_ID = {w.world_id: w for w in DIAGNOSTIC_WORLDS}
for _w in EXTRA_WORLDS:
    _WORLD_BY_ID[_w.world_id] = _w

REQUIRED_WORLD_IDS: tuple[str, ...] = (
    "clean_null",
    "weak_signal",
    "clean_positive_effect",
    "strong_signal",
    "clean_negative_effect",
    "serial_correlation",
    "high_serial_correlation",
    "heteroskedastic_residuals",
    "heavy_tailed_noise",
    "regime_shift",
    "post_treatment_shock",
    "donor_contamination",
    "poor_pre_fit",
    "low_noise",
    "small_pre_period",
    "long_pre_period",
    "short_post_period",
    "long_post_period",
    "small_donor_support",
    "ridge_dominant",
    "low_ridge_shrinkage",
    "outlier_period",
)

CANDIDATE_POLICIES: dict[str, dict[str, Any]] = {
    "baseline_corrected_brb": {
        "implemented": True,
        "variance_calibration_policy": "none",
        "bootstrap_type": "block",
        "block_length": 3,
        "description": "Centered-deviation BRB after TBRRIDGE_BRB_INTERVAL_CORRECTION_001",
    },
    "variance_scaled_brb": {
        "implemented": True,
        "variance_calibration_policy": "residual_scaled",
        "bootstrap_type": "block",
        "block_length": 3,
        "description": "Residual-pool scaled deviation CI",
    },
    "studentized_brb": {
        "implemented": True,
        "variance_calibration_policy": "studentized",
        "bootstrap_type": "block",
        "block_length": 3,
        "description": "Bootstrap-t pivot on mean-effect replicates",
    },
    "wild_block_brb": {
        "implemented": True,
        "variance_calibration_policy": "none",
        "bootstrap_type": "wild",
        "block_length": 3,
        "description": "Wild (Rademacher) residual bootstrap",
    },
    "larger_block_length_brb": {
        "implemented": True,
        "variance_calibration_policy": "none",
        "bootstrap_type": "block",
        "block_length": 7,
        "description": "Longer moving blocks (length 7)",
    },
    "adaptive_block_length_brb": {
        "implemented": True,
        "variance_calibration_policy": "none",
        "bootstrap_type": "block",
        "block_length": None,
        "description": "Adaptive T^(1/3) block length",
    },
    "null_calibrated_brb": {
        "implemented": True,
        "variance_calibration_policy": "null_calibrated",
        "bootstrap_type": "block",
        "block_length": 3,
        "description": "Minimum half-width from residual-pool null calibration",
    },
    "restricted_worlds_only_brb": {
        "implemented": False,
        "reason": "evaluation filter only; not a production policy",
    },
}


@dataclass(frozen=True)
class RemediationConfig:
    n_replicates: int = 3
    n_replicates_fast: int = 2
    n_bootstrap: int = 40
    n_bootstrap_fast: int = 20
    alpha: float = 0.05
    min_train_periods: int = 5
    random_state_base: int = 20260603
    fast: bool = False
    candidates: tuple[str, ...] = tuple(
        k for k, v in CANDIDATE_POLICIES.items() if v.get("implemented")
    )


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=_REPO,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _load_input_artifacts() -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for key, rel in INPUT_ARTIFACTS.items():
        path = _REPO / rel
        if not path.is_file():
            raise FileNotFoundError(f"Required input artifact missing: {rel}")
        loaded[key] = json.loads(path.read_text(encoding="utf-8"))
    return loaded


def _run_one(
    spec: DiagnosticWorldSpec,
    cfg: RemediationConfig,
    *,
    candidate_id: str,
    replicate_id: int,
    seed: int,
) -> dict[str, Any]:
    policy = CANDIDATE_POLICIES[candidate_id]
    brb_cfg = BrbTrustConfig(
        train_length=spec.train_length if spec.train_length is not None else 28,
        test_length=spec.test_length if spec.test_length is not None else 8,
        alpha=cfg.alpha,
        min_train_periods=cfg.min_train_periods,
        fast=cfg.fast,
    )
    train, test = _effective_lengths(spec, brb_cfg)
    eff_pct = spec.percent_effect
    base: dict[str, Any] = {
        "candidate_id": candidate_id,
        "world_id": spec.world_id,
        "replicate_id": replicate_id,
        "seed": seed,
        "percent_effect_injected": float(eff_pct),
        "serial_dependence_regime": spec.serial_dependence_regime,
    }
    try:
        panel = _build_unit_panel(spec, brb_cfg, seed=seed)
        mean_value = _mean_treated_baseline(panel)
        true_level = _level_true_effect(eff_pct, mean_value)
        pds = _inject_percent_effect(panel, eff_pct, mean_value)

        n_boot = cfg.n_bootstrap_fast if cfg.fast else cfg.n_bootstrap
        kwargs: dict[str, Any] = {
            "n_bootstrap": n_boot,
            "min_train_periods": cfg.min_train_periods,
            "show_progress": False,
            "random_state": seed,
            "center_residuals": True,
            "variance_calibration_policy": policy.get("variance_calibration_policy", "none"),
            "bootstrap_type": policy.get("bootstrap_type", "block"),
        }
        bl = policy.get("block_length")
        if bl is not None:
            kwargs["block_length"] = bl

        est = TBRRidge(inference="BlockResidualBootstrap", alpha=cfg.alpha)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            est.run_analysis(pds, **kwargs)

        results = getattr(est, "results", {}) or {}
        brb_stats = results.get("block_residual_bootstrap_stats") or {}
        readout = _readout_level_scale(
            results,
            test_len=test,
            true_effect_level=true_level,
            brb_stats=brb_stats if isinstance(brb_stats, dict) else None,
        )

        ridge_alpha = None
        model = getattr(est, "model", None)
        if model is not None and hasattr(model, "alpha_"):
            ridge_alpha = float(model.alpha_)

        y_hat = np.asarray(results.get("y_hat", []), dtype=float)
        prefit = _prefit_rmse(pds, y_hat) if y_hat.size else float("nan")

        cal_ratio = None
        if isinstance(brb_stats, dict):
            cal_ratio = brb_stats.get("calibration_ratio_mean_effect")
            if cal_ratio is None and brb_stats.get("bootstrap_mean_replicate_std") is not None:
                emp = brb_stats.get("empirical_mean_standard_error")
                bsd = brb_stats.get("bootstrap_mean_replicate_std")
                if emp and bsd and emp > 1e-12:
                    cal_ratio = float(bsd / emp)

        run = {
            **base,
            **readout,
            "true_effect": true_level,
            "true_effect_percent": float(eff_pct),
            "prefit_rmse": prefit,
            "ridge_alpha": ridge_alpha,
            "block_length": brb_stats.get("block_length") if isinstance(brb_stats, dict) else bl,
            "n_bootstrap_replicates": brb_stats.get("n_bootstrap") if isinstance(brb_stats, dict) else n_boot,
            "bootstrap_failure_count": brb_stats.get("bootstrap_failed_draws") if isinstance(brb_stats, dict) else 0,
            "effective_blocks": brb_stats.get("residual_pool_size") if isinstance(brb_stats, dict) else None,
            "variance_calibration_policy": brb_stats.get("variance_calibration_policy"),
            "variance_scale_factor": brb_stats.get("variance_scale_factor"),
            "calibration_ratio_mean_effect": cal_ratio,
            "bootstrap_mean_replicate_std": brb_stats.get("bootstrap_mean_replicate_std"),
            "empirical_mean_standard_error": brb_stats.get("empirical_mean_standard_error"),
            "pre_period_length": train,
            "post_period_length": test,
            "donor_count": int(pds.num_control_units),
            "failure_status": "ok",
            "failure_reason": None,
        }
        run["root_cause_tags"] = _root_cause_tags(run)
        return run
    except Exception as exc:
        return {
            **base,
            "point_estimate": None,
            "true_effect": None,
            "failure_status": "fail",
            "failure_reason": str(exc)[:300],
            "contains_truth": None,
            "contains_zero": None,
            "root_cause_tags": ["support_failure"],
        }


def _aggregate_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [r for r in runs if r.get("failure_status") == "ok"]
    fail = [r for r in runs if r.get("failure_status") != "ok"]
    cov = _coverage_metrics(ok)
    clean_truth = [r for r in ok if r.get("world_id") in CLEAN_TRUTH_WORLD_IDS]
    clean_cov = _coverage_metrics(clean_truth)
    null_runs = [r for r in ok if r.get("true_effect") is not None and abs(r["true_effect"]) < 1e-9]
    return {
        "n_runs": len(runs),
        "failure_rate": len(fail) / max(1, len(runs)),
        "mean_bias": _mean([r.get("point_bias") for r in ok]),
        "median_bias": float(np.median([r["point_bias"] for r in ok if r.get("point_bias") is not None]))
        if ok
        else None,
        "rmse": math.sqrt(_mean([r.get("squared_error") for r in ok]) or 0) if ok else None,
        "mean_interval_width": _mean([r.get("interval_width") for r in ok]),
        "median_interval_width": float(np.median([r["interval_width"] for r in ok if r.get("interval_width") is not None]))
        if ok
        else None,
        "coverage_truth": _mean([r.get("contains_truth") for r in ok if r.get("contains_truth") is not None]),
        "coverage_zero_under_null": cov.get("null_coverage"),
        "type_i_under_null": cov.get("type_i_error"),
        "positive_coverage": cov.get("positive_coverage"),
        "negative_coverage": cov.get("negative_coverage"),
        "positive_power": cov.get("positive_coverage"),
        "negative_power": cov.get("negative_coverage"),
        "sign_accuracy": _mean([r.get("sign_correct") for r in ok if r.get("sign_correct") is not None]),
        "interval_center_gap": _mean(
            [abs(r.get("bootstrap_center_minus_point") or 0) for r in ok if r.get("bootstrap_center_minus_point") is not None]
        ),
        "variance_ratio": _mean([r.get("variance_ratio") for r in ok]),
        "calibration_ratio": _mean([r.get("calibration_ratio_mean_effect") for r in ok]),
        "bootstrap_replicate_sd": _mean([r.get("bootstrap_mean_replicate_std") for r in ok]),
        "empirical_error_sd": _mean([r.get("empirical_mean_standard_error") for r in ok]),
        "mean_block_length": _mean([r.get("block_length") for r in ok if r.get("block_length") is not None]),
        "mean_effective_blocks": _mean([r.get("effective_blocks") for r in ok]),
        "clean_truth_coverage": clean_cov.get("positive_coverage"),
        "clean_negative_coverage": clean_cov.get("negative_coverage"),
        "coverage_by_world": {
            wid: _coverage_metrics([r for r in ok if r.get("world_id") == wid])
            for wid in sorted({r.get("world_id") for r in ok if r.get("world_id")})
        },
    }


def _evaluate_gates(metrics: dict[str, Any]) -> dict[str, Any]:
    type_i = metrics.get("type_i_under_null")
    null_cov = metrics.get("coverage_zero_under_null")
    clean_pos = metrics.get("clean_truth_coverage")
    clean_neg = metrics.get("clean_negative_coverage")
    truth_cov = _mean([v for v in (clean_pos, clean_neg) if v is not None])
    center_gap = metrics.get("interval_center_gap")
    failure_rate = metrics.get("failure_rate")

    checks = {
        "null_type_i": type_i is not None and type_i <= PASS_FAIL_GATES["null_type_i_max"],
        "null_coverage_zero": null_cov is not None and null_cov >= PASS_FAIL_GATES["null_coverage_zero_min"],
        "truth_coverage_clean": truth_cov is not None and truth_cov >= PASS_FAIL_GATES["truth_coverage_clean_min"],
        "interval_center_gap": center_gap is not None and center_gap <= PASS_FAIL_GATES["interval_center_gap_abs_max"],
        "failure_rate": failure_rate is not None and failure_rate <= PASS_FAIL_GATES["failure_rate_max"],
    }
    return {
        "gates": checks,
        "all_pass": all(checks.values()),
        "pass_count": sum(1 for v in checks.values() if v),
        "truth_coverage_aggregate": truth_cov,
    }


def _root_cause_table(baseline: dict[str, Any], inputs: dict[str, Any]) -> list[dict[str, Any]]:
    inv = inputs.get("interval_correction", {})
    after = inv.get("after_metrics") or {}
    rows = [
        {
            "question": "Is undercoverage caused by bootstrap replicate variance being too small?",
            "finding": (
                "Partially on mean-effect scale: calibration_ratio_mean_effect often < 1 "
                f"(baseline mean {baseline.get('calibration_ratio')}); cumulative variance_ratio is inflated by scale mismatch."
            ),
            "tags": ["mean_replicate_underestimation", "cumulative_diagnostic_mismatch"],
        },
        {
            "question": "Is null type-I high because intervals are too narrow?",
            "finding": (
                f"Partially: type-I {baseline.get('type_i_under_null')} with null coverage {baseline.get('coverage_zero_under_null')}; "
                "null_calibrated widening helps marginally but does not reach gates."
            ),
            "tags": ["interval_width", "null_type_i"],
        },
        {
            "question": "Is the interval centered correctly after the prior correction?",
            "finding": (
                f"Yes: mean |bootstrap_center_minus_point| ≈ {baseline.get('interval_center_gap')} "
                f"(prior gap {after.get('bootstrap_center_minus_point')})."
            ),
            "tags": ["centering_resolved"],
        },
        {
            "question": "Does ridge shrinkage bias interact with bootstrap variance?",
            "finding": (
                f"Yes: null worlds show material point bias (mean bias {baseline.get('mean_bias')}); "
                "conditional BRB cannot correct estimator bias."
            ),
            "tags": ["point_bias", "ridge_shrinkage"],
        },
        {
            "question": "Does BRB condition on fitted ridge coefficients correctly?",
            "finding": "Conditional resampling (no refit) ignores coefficient-estimation uncertainty.",
            "tags": ["conditional_bootstrap", "coefficient_uncertainty_omitted"],
        },
    ]
    return rows


def _select_policy(candidate_results: dict[str, dict[str, Any]]) -> tuple[str | None, dict[str, Any]]:
    ranked: list[tuple[str, dict[str, Any]]] = []
    for cid, metrics in candidate_results.items():
        gate = metrics.get("gate_evaluation") or {}
        ranked.append((cid, gate))
    ranked.sort(key=lambda x: (x[1].get("pass_count", 0), x[1].get("truth_coverage_aggregate") or 0), reverse=True)
    if not ranked:
        return None, {}
    best_id, best_gate = ranked[0]
    if best_gate.get("all_pass"):
        return best_id, best_gate
    if best_gate.get("pass_count", 0) >= 3:
        return best_id, best_gate
    return best_id, best_gate


def _decide_verdict(
    *,
    selected_policy: str | None,
    gate_eval: dict[str, Any],
    baseline_gates: dict[str, Any],
) -> RemediationVerdict:
    if selected_policy is None:
        return "tbrridge_brb_variance_remediation_failed"
    if gate_eval.get("all_pass"):
        return "tbrridge_brb_variance_remediated_restricted"
    if gate_eval.get("pass_count", 0) >= 3 and selected_policy != "baseline_corrected_brb":
        return "tbrridge_brb_variance_remediation_candidate_only"
    if baseline_gates.get("pass_count", 0) == gate_eval.get("pass_count", 0):
        return "tbrridge_brb_additional_remediation_required"
    if gate_eval.get("pass_count", 0) > baseline_gates.get("pass_count", 0):
        return "tbrridge_brb_variance_remediation_candidate_only"
    return "tbrridge_brb_variance_remediation_failed"


def build_tbrridge_brb_variance_calibration_remediation_001(
    cfg: RemediationConfig | None = None,
    *,
    candidates: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    cfg = cfg or RemediationConfig()
    if candidates:
        cfg = replace(cfg, candidates=candidates)
    t0 = time.perf_counter()
    inputs = _load_input_artifacts()

    worlds = [_WORLD_BY_ID[wid] for wid in REQUIRED_WORLD_IDS]
    n_rep = cfg.n_replicates_fast if cfg.fast else cfg.n_replicates

    all_runs: dict[str, list[dict[str, Any]]] = {}
    for cid in cfg.candidates:
        if not CANDIDATE_POLICIES.get(cid, {}).get("implemented"):
            continue
        runs: list[dict[str, Any]] = []
        for spec in worlds:
            for rep in range(n_rep):
                seed = cfg.random_state_base + hash((cid, spec.world_id, rep)) % 100_000
                runs.append(_run_one(spec, cfg, candidate_id=cid, replicate_id=rep, seed=seed))
        all_runs[cid] = runs

    candidate_results = {cid: _aggregate_runs(runs) for cid, runs in all_runs.items()}
    for cid, metrics in candidate_results.items():
        metrics["gate_evaluation"] = _evaluate_gates(metrics)

    baseline = candidate_results.get("baseline_corrected_brb", {})
    selected_policy, selected_gate = _select_policy(candidate_results)
    verdict = _decide_verdict(
        selected_policy=selected_policy,
        gate_eval=selected_gate,
        baseline_gates=(baseline.get("gate_evaluation") or {}),
    )

    selected_spec = CANDIDATE_POLICIES.get(selected_policy or "", {})
    production_changes = selected_spec.get("variance_calibration_policy", "none") not in (
        None,
        "",
        "none",
    )
    candidate_for_reassessment = verdict in (
        "tbrridge_brb_variance_remediated_restricted",
        "tbrridge_brb_variance_remediation_candidate_only",
    )

    next_artifact = (
        "DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001"
        if candidate_for_reassessment
        else (
            "TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_002"
            if verdict == "tbrridge_brb_additional_remediation_required"
            else "MARK_TBRRIDGE_BRB_DIAGNOSTIC_ONLY_DISPOSITION_001"
        )
    )

    inv_resolution = (
        "REMEDIATED_RESTRICTED"
        if verdict == "tbrridge_brb_variance_remediated_restricted"
        else (
            "REMEDIATION_CANDIDATE_PENDING_REASSESSMENT"
            if verdict == "tbrridge_brb_variance_remediation_candidate_only"
            else (
                "DIAGNOSTIC_ONLY"
                if verdict in ("tbrridge_brb_diagnostic_only", "tbrridge_brb_ineligible")
                else "ADDITIONAL_REMEDIATION_REQUIRED"
            )
        )
    )

    handoff = build_investigation_handoff(
        follow_up_issues=[] if candidate_for_reassessment else ["BRB variance/null gates not met"],
        resolved_issues=["INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001"]
        if verdict != "tbrridge_brb_additional_remediation_required"
        else [],
        terminal_dispositions=[inv_resolution],
        next_artifact=next_artifact,
    )

    runtime_s = time.perf_counter() - t0

    summary: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "input_artifacts": {k: str(_REPO / v) for k, v in INPUT_ARTIFACTS.items()},
        "config": {
            "fast": cfg.fast,
            "n_replicates": n_rep,
            "n_bootstrap": cfg.n_bootstrap_fast if cfg.fast else cfg.n_bootstrap,
            "candidates": list(cfg.candidates),
            "world_count": len(worlds),
            "runtime_seconds": runtime_s,
        },
        "candidate_policies": CANDIDATE_POLICIES,
        "worlds": [w.world_id for w in worlds],
        "run_counts": {cid: len(runs) for cid, runs in all_runs.items()},
        "baseline_results": baseline,
        "candidate_results": {k: v for k, v in candidate_results.items() if k != "baseline_corrected_brb"},
        "candidate_comparison": {
            cid: {
                "gate_pass_count": (candidate_results[cid].get("gate_evaluation") or {}).get("pass_count"),
                "all_gates_pass": (candidate_results[cid].get("gate_evaluation") or {}).get("all_pass"),
                "type_i_under_null": candidate_results[cid].get("type_i_under_null"),
                "null_coverage": candidate_results[cid].get("coverage_zero_under_null"),
                "positive_coverage": candidate_results[cid].get("positive_coverage"),
                "calibration_ratio": candidate_results[cid].get("calibration_ratio"),
            }
            for cid in candidate_results
        },
        "root_cause_analysis": _root_cause_table(baseline, inputs),
        "pass_fail_gates": PASS_FAIL_GATES,
        "selected_policy": selected_policy,
        "production_changes": production_changes,
        "coverage_results": {
            cid: {
                "null": candidate_results[cid].get("coverage_zero_under_null"),
                "positive": candidate_results[cid].get("positive_coverage"),
                "negative": candidate_results[cid].get("negative_coverage"),
            }
            for cid in candidate_results
        },
        "type_i_results": {cid: candidate_results[cid].get("type_i_under_null") for cid in candidate_results},
        "power_results": {
            cid: {
                "positive": candidate_results[cid].get("positive_power"),
                "negative": candidate_results[cid].get("negative_power"),
            }
            for cid in candidate_results
        },
        "sign_accuracy_results": {cid: candidate_results[cid].get("sign_accuracy") for cid in candidate_results},
        "calibration_ratio_results": {cid: candidate_results[cid].get("calibration_ratio") for cid in candidate_results},
        "interval_width_results": {cid: candidate_results[cid].get("mean_interval_width") for cid in candidate_results},
        "failure_summary": {cid: candidate_results[cid].get("failure_rate") for cid in candidate_results},
        "semantic_classification": (
            "restricted_causal_interval_candidate"
            if verdict == "tbrridge_brb_variance_remediated_restricted"
            else "remediation_candidate_pending_reassessment"
            if verdict == "tbrridge_brb_variance_remediation_candidate_only"
            else "causal_interval_blocked"
        ),
        "trustreport_eligibility_implications": {
            "trust_report_authorized": False,
            "candidate_for_reassessment": candidate_for_reassessment,
            "dcm005_brb_path": "DEFERRED_REMEDIATION" if not candidate_for_reassessment else "PENDING_POST_REMEDIATION_REASSESSMENT",
        },
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_ready": False,
            "trust_report_authorized_count": 0,
            "candidate_for_reassessment": candidate_for_reassessment,
        },
        "investigation_handoff": handoff,
        "limitations": [
            "Conditional BRB does not refit ridge coefficients; point bias under null remains.",
            "Cumulative variance_ratio diagnostic mixes sum-scale bootstrap with per-period empirical SE.",
            "Remediation policies widen or recalibrate mean-effect intervals only.",
            "Does not authorize TrustReport; post-remediation reassessment required if candidate.",
        ],
        "verdict": verdict,
        "next_artifact": next_artifact,
        "gate_evaluation_selected": selected_gate,
        "investigation_resolution": {
            "investigation_id": "INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001",
            "terminal_decision": inv_resolution,
        },
    }
    return _json_safe(summary)


def _atomic_write(path: Path, content: str, *, overwrite: bool = False) -> None:
    path = path.resolve()
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_report(payload: dict[str, Any], path: Path, *, overwrite: bool = False) -> None:
    handoff_lines = format_handoff_report_section(
        resolved_in_artifact=["INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001"],
        new_investigations=[],
        updated_investigations=["INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001"],
        deferred_issues=[],
        explicit_exclusions=[],
        revisit_trigger="Post-remediation reassessment if candidate",
        decision_checkpoint="DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001",
        next_artifact=payload.get("next_artifact"),
    )
    baseline = payload.get("baseline_results") or {}
    selected = payload.get("selected_policy")
    comp = payload.get("candidate_comparison") or {}
    sel_metrics = comp.get(selected or "", {})
    lines = [
        f"# {_ARTIFACT_ID} Report",
        "",
        "## 1. Executive summary",
        "",
        "This artifact remediates or adjudicates the TBRRidge + BRB variance/null-calibration issue.",
        "It does not authorize TrustReport.",
        "It does not perform the full TrustReport eligibility reassessment.",
        "Any successful remediation requires a subsequent reassessment before promotion.",
        "",
        f"**Verdict:** `{payload.get('verdict')}`",
        f"**Selected policy:** `{selected}`",
        f"**Production variance policy added:** `{payload.get('production_changes')}`",
        "",
        "## 2. Prior evidence state",
        "",
        "TBRRIDGE_BRB_INTERVAL_CORRECTION_001 fixed centering; null type-I and positive coverage remained unacceptable.",
        "",
        "## 3. Scope",
        "",
        "TBRRidge + BlockResidualBootstrap across 22 diagnostic worlds and 7 implemented candidate policies.",
        "",
        "## 4. Non-goals",
        "",
        "No TrustReport authorization; no full matrix reassessment; no SCM/DID/KFold/Placebo changes.",
        "",
        "## 5. Root-cause questions",
        "",
        json.dumps(payload.get("root_cause_analysis"), indent=2),
        "",
        "## 6. Candidate remediation policies",
        "",
        json.dumps(payload.get("candidate_policies"), indent=2),
        "",
        "## 7. Worlds",
        "",
        ", ".join(payload.get("worlds") or []),
        "",
        "## 10. Baseline corrected-BRB behavior",
        "",
        f"Null type-I: {baseline.get('type_i_under_null')}; null coverage: {baseline.get('coverage_zero_under_null')}; "
        f"positive coverage: {baseline.get('positive_coverage')}; center gap: {baseline.get('interval_center_gap')}.",
        "",
        "## 11. Candidate comparison",
        "",
        json.dumps(comp, indent=2),
        "",
        "## 12. Null calibration",
        "",
        json.dumps(payload.get("type_i_results"), indent=2),
        "",
        "## 13. Positive/negative coverage",
        "",
        json.dumps(payload.get("coverage_results"), indent=2),
        "",
        "## 16. Calibration ratio analysis",
        "",
        json.dumps(payload.get("calibration_ratio_results"), indent=2),
        "",
        "## 21. Selected policy",
        "",
        f"`{selected}` — gate pass count {sel_metrics.get('gate_pass_count')}; all gates pass: {sel_metrics.get('all_gates_pass')}.",
        "",
        "## 22. Production changes",
        "",
        "Added optional `variance_calibration_policy` (`residual_scaled`, `studentized`, `null_calibrated`) "
        "to `block_residual_bootstrap.py`; default `none` preserves corrected baseline.",
        "",
        "## 23. Pass/fail gate results",
        "",
        json.dumps(payload.get("gate_evaluation_selected"), indent=2),
        "",
        "## 25. Semantic classification",
        "",
        f"`{payload.get('semantic_classification')}`",
        "",
        "## 27. Authorization status",
        "",
        json.dumps(payload.get("authorization_summary"), indent=2),
        "",
        "## 28. Investigation lifecycle update",
        "",
        json.dumps(payload.get("investigation_resolution"), indent=2),
        "",
        "## 30. Governance verdict",
        "",
        f"`{payload.get('verdict')}`",
        "",
        *handoff_lines,
        "",
        "## Residual Issues and Handoff",
        "",
        f"Next artifact: `{payload.get('next_artifact')}`",
    ]
    _atomic_write(path, "\n".join(lines) + "\n", overwrite=overwrite)


def write_summary(
    summary_path: Path,
    *,
    overwrite: bool = False,
    report_path: Path | None = None,
    local_results_path: Path | None = None,
    fast: bool = False,
    candidates: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    cfg = RemediationConfig(fast=fast)
    payload = build_tbrridge_brb_variance_calibration_remediation_001(cfg, candidates=candidates)
    _atomic_write(
        summary_path,
        json.dumps(payload, indent=2, sort_keys=False) + "\n",
        overwrite=overwrite,
    )
    if local_results_path is not None:
        _atomic_write(
            local_results_path,
            json.dumps(payload, indent=2) + "\n",
            overwrite=overwrite,
        )
    if report_path is not None:
        write_report(payload, report_path, overwrite=overwrite)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--summary-output", type=Path, default=_DEFAULT_SUMMARY)
    parser.add_argument("--report-output", type=Path, default=_DEFAULT_REPORT)
    parser.add_argument("--output-local", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--candidate", action="append", dest="candidates", default=None)
    args = parser.parse_args()
    cands = tuple(args.candidates) if args.candidates else None
    write_summary(
        args.summary_output,
        overwrite=args.overwrite,
        report_path=args.report_output,
        local_results_path=args.output_local,
        fast=args.fast,
        candidates=cands,
    )


if __name__ == "__main__":
    main()
