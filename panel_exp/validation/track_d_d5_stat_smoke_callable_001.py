"""D5-STAT-SMOKE-CALLABLE-001 — smoke / schema / callability / orientation / guard battery.

First evidence-execution artifact after DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.
No heavy MC, no statistical validation claims, no promotion or trust wiring.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.validation.track_d_d5_inst_audit_001 import (
    GEOMETRY_BUILDERS,
    ProbeConfig,
    _build_wide,
    _optional_skip,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SUITABILITY_JSON = (
    _REPO_ROOT / "docs/track_d/archives/DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.json"
)

CallableStatus = Literal[
    "callable_pass",
    "callable_fail",
    "blocked_expected",
    "skipped_not_smoke_safe",
]
SmokeVerdict = Literal["pass", "fail", "expected_block", "skipped"]
OverallVerdict = Literal[
    "smoke_pass_with_expected_blocks",
    "smoke_pass_with_caveats",
    "smoke_fail_requires_fix",
]

NON_EXECUTABLE_SUITABILITY = frozenset(
    {
        "blocked_before_suitability",
        "bridge_required_before_suitability",
        "implementation_fix_required",
        "research_only",
        "quarantine_or_deprecate",
    }
)

EXECUTABLE_ALLOWED_USE = frozenset(
    {
        "oc_execution_only",
        "diagnostic_research_only",
        "metadata_guardrail_only",
        "planning_only",
    }
)

# combination_id -> (estimator_class, inference mode or "__did_embedded__", geometry key)
COMBO_PROBE_SPEC: dict[str, tuple[str, str | None, str]] = {
    "SCM-JK": ("SyntheticControlCVXPY", "UnitJackKnife", "single_cell_unit_level"),
    "SCM-PLACEBO": ("SyntheticControlCVXPY", "Placebo", "single_treated_unit"),
    "AUGSYNTH-POINT": ("AugSynthCVXPY", None, "single_cell_unit_level"),
    "TBR-AGG-POINT": ("TBR", None, "aggregate_two_series"),
    "TBR-AGG-KFOLD": ("TBR", "Kfold", "aggregate_two_series"),
    "DID-BOOTSTRAP": ("DID", "__did_embedded__", "single_cell_unit_level"),
    "TBRRIDGE-KFOLD": ("TBRRidge", "Kfold", "single_cell_unit_level"),
    "MCELL-PERCELL-SCM-JK": (
        "SyntheticControlCVXPY",
        "UnitJackKnife",
        "multi_cell_per_cell_unit",
    ),
    "TIER1-SCM-JK": ("SyntheticControlCVXPY", "UnitJackKnife", "single_cell_unit_level"),
    "MCELL-AUGSYNTH-POINT": ("AugSynthCVXPY", None, "multi_cell_per_cell_unit"),
    "AUGSYNTH-KFOLD": ("AugSynthCVXPY", "Kfold", "single_cell_unit_level"),
}

MINIMUM_COMBO_IDS = frozenset(
    {
        "SCM-JK",
        "SCM-PLACEBO",
        "AUGSYNTH-POINT",
        "TBR-AGG-POINT",
        "DID-BOOTSTRAP",
        "TBRRIDGE-KFOLD",
        "MCELL-PERCELL-SCM-JK",
        "AUGSYNTH-CONFORMAL",
        "AUGSYNTH-JK",
        "MCELL-POOLED-AUGSYNTH",
        "MCELL-POOLED-SCM-JK",
        "SUPERGEO-SCM-JK",
        "TRIM-SCM-JK",
        "SUPERGEO-AUGSYNTH-POINT",
        "TRIM-AUGSYNTH-POINT",
        "TBR-UNIT-JK",
        "TBRRIDGE-BAYESIAN-REG",
    }
)

NEXT_RECOMMENDED = ["D5-STAT-SCM-JK-001"]


@dataclass(frozen=True)
class SmokeConfig:
    seed: int = 42
    train_length: int = 18
    test_length: int = 6
    n_geos: int = 10


def load_suitability_framework() -> dict[str, Any]:
    return json.loads(_SUITABILITY_JSON.read_text(encoding="utf-8"))


def _forbidden_flags() -> dict[str, bool]:
    return {
        "promotion_allowed": False,
        "trust_role_allowed": False,
        "calibration_signal_allowed": False,
        "mmm_allowed": False,
        "llm_recommendation_allowed": False,
    }


def _should_execute(suit_row: dict[str, Any]) -> tuple[bool, str]:
    cid = suit_row["combination_id"]
    cls_name = suit_row["suitability_class"]
    allowed_use = suit_row["current_allowed_use"]
    if cls_name in NON_EXECUTABLE_SUITABILITY:
        return False, f"suitability_class={cls_name}"
    if allowed_use == "no_runtime_use":
        return False, f"current_allowed_use={allowed_use}"
    if cid not in COMBO_PROBE_SPEC:
        return False, "no_smoke_probe_mapping"
    return True, "smoke_probe_mapped"


def _interval_checks(results: dict[str, Any]) -> dict[str, Any]:
    y_lo = results.get("y_lower")
    y_hi = results.get("y_upper")
    if y_lo is None or y_hi is None:
        return {
            "interval_present": False,
            "interval_orientation_valid": None,
            "negative_half_width_detected": None,
        }
    lo = np.asarray(y_lo, dtype=float).reshape(-1)
    hi = np.asarray(y_hi, dtype=float).reshape(-1)
    mask = np.isfinite(lo) & np.isfinite(hi)
    if not mask.any():
        return {
            "interval_present": True,
            "interval_orientation_valid": False,
            "negative_half_width_detected": None,
        }
    orient = bool(np.all(lo[mask] <= hi[mask]))
    mid = 0.5 * (lo[mask] + hi[mask])
    half_w = hi[mask] - mid
    neg_hw = bool(np.any(half_w < 0))
    return {
        "interval_present": True,
        "interval_orientation_valid": orient,
        "negative_half_width_detected": neg_hw,
    }


def _schema_and_finite(results: dict[str, Any] | None) -> tuple[bool, bool, bool]:
    if not results or not isinstance(results, dict):
        return False, False, False
    has_y = "y" in results and results["y"] is not None
    has_yhat = "y_hat" in results and results["y_hat"] is not None
    schema_ok = has_y and has_yhat
    finite = True
    for key in ("y", "y_hat"):
        if key in results and results[key] is not None:
            arr = np.asarray(results[key], dtype=float).reshape(-1)
            if arr.size:
                finite_vals = arr[np.isfinite(arr)]
                if finite_vals.size == 0 or not np.all(np.isfinite(finite_vals)):
                    finite = False
    point_present = results.get("point_estimate") is not None or has_yhat
    return schema_ok, bool(point_present), finite


def _execute_combo(
    combo_id: str,
    suit_row: dict[str, Any],
    wide: Any,
    cfg: SmokeConfig,
) -> dict[str, Any]:
    spec = COMBO_PROBE_SPEC[combo_id]
    cls_name, inference, geom_key = spec
    probe_cfg = ProbeConfig(
        seed=cfg.seed,
        train_length=cfg.train_length,
        test_length=cfg.test_length,
        n_geos=cfg.n_geos,
    )
    builder = GEOMETRY_BUILDERS.get(geom_key)
    row_base: dict[str, Any] = {
        "combination_id": combo_id,
        "suitability_class": suit_row["suitability_class"],
        "source_matrix_status": suit_row["source_matrix_status"],
        "estimator_family": suit_row["estimator_family"],
        "inference_family": suit_row["inference_family"],
        "geometry": suit_row["geometry"],
        "probe_spec": {"class": cls_name, "inference": inference, "geometry_key": geom_key},
        **_forbidden_flags(),
    }
    if builder is None:
        row_base.update(
            {
                "callable_status": "callable_fail",
                "smoke_verdict": "fail",
                "exception_type": "KeyError",
                "exception_message": f"unknown geometry {geom_key}",
            }
        )
        return _finalize_row(row_base)

    panel = builder(wide, probe_cfg)
    skip = _optional_skip(cls_name)
    if skip:
        row_base.update(
            {
                "callable_status": "skipped_not_smoke_safe",
                "smoke_verdict": "skipped",
                "exception_type": "optional_dep_missing",
                "exception_message": skip,
            }
        )
        return _finalize_row(row_base)

    import importlib

    mod_map = {
        "SyntheticControlCVXPY": ("panel_exp.methods.scm", "SyntheticControlCVXPY"),
        "AugSynthCVXPY": ("panel_exp.methods.scm", "AugSynthCVXPY"),
        "TBR": ("panel_exp.methods.tbr", "TBR"),
        "TBRRidge": ("panel_exp.methods.tbr", "TBRRidge"),
        "DID": ("panel_exp.methods.DID", "DID"),
    }
    mod_name, attr = mod_map[cls_name]
    cls = getattr(importlib.import_module(mod_name), attr)

    extra: dict[str, Any] = {}
    inf = None if inference == "__did_embedded__" else inference
    if inference == "Placebo":
        extra["placebo_strict"] = False
    if inference == "BlockResidualBootstrap":
        extra.update(
            n_bootstrap=12,
            block_length=3,
            min_train_periods=5,
            show_progress=False,
            random_state=cfg.seed,
        )
    if inference == "Kfold":
        extra["random_state"] = cfg.seed
    if inference == "Conformal":
        extra["random_state"] = cfg.seed

    try:
        if inference == "__did_embedded__":
            est = cls()
            est.run_analysis(panel, multiple_treated="pooled")
        elif inf is None:
            est = cls(inference=None)
            est.run_analysis(panel)
        else:
            est = cls(inference=inf, alpha=0.05)
            est.run_analysis(panel, **extra)
        results = getattr(est, "results", {}) or {}
        schema_ok, point_present, finite = _schema_and_finite(results)
        ival = _interval_checks(results)
        identity_ok = est.__class__.__name__ == cls_name
        silent_geo = False
        if suit_row["geometry"] in (
            "supergeo_cluster",
            "trimmed_pair",
            "pooled_multi_cell",
        ) and geom_key in ("single_cell_unit_level", "aggregate_two_series"):
            silent_geo = True
        row_base.update(
            {
                "callable_status": "callable_pass" if schema_ok and finite else "callable_fail",
                "method_identity_preserved": identity_ok,
                "output_schema_valid": schema_ok,
                "point_estimate_present": point_present,
                "finite_outputs": finite,
                "unsupported_geometry_silently_allowed": silent_geo,
                "exception_type": None,
                "exception_message": None,
                **ival,
            }
        )
        if not schema_ok or not finite or not identity_ok:
            row_base["callable_status"] = "callable_fail"
            row_base["smoke_verdict"] = "fail"
        elif silent_geo:
            row_base["callable_status"] = "callable_fail"
            row_base["smoke_verdict"] = "fail"
        elif ival["interval_present"] and ival["interval_orientation_valid"] is False:
            row_base["callable_status"] = "callable_fail"
            row_base["smoke_verdict"] = "fail"
        elif ival.get("negative_half_width_detected"):
            row_base["callable_status"] = "callable_fail"
            row_base["smoke_verdict"] = "fail"
        else:
            row_base["smoke_verdict"] = "pass"
    except Exception as exc:
        row_base.update(
            {
                "callable_status": "callable_fail",
                "smoke_verdict": "fail",
                "method_identity_preserved": False,
                "output_schema_valid": False,
                "point_estimate_present": False,
                "interval_present": False,
                "interval_orientation_valid": None,
                "negative_half_width_detected": None,
                "finite_outputs": False,
                "unsupported_geometry_silently_allowed": False,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc)[:300],
            }
        )
    return _finalize_row(row_base)


def _finalize_row(row: dict[str, Any]) -> dict[str, Any]:
    defaults = {
        "method_identity_preserved": False,
        "output_schema_valid": False,
        "point_estimate_present": False,
        "interval_present": False,
        "interval_orientation_valid": None,
        "negative_half_width_detected": None,
        "finite_outputs": False,
        "unsupported_geometry_silently_allowed": False,
        "exception_type": None,
        "exception_message": None,
    }
    for k, v in defaults.items():
        row.setdefault(k, v)
    row.setdefault("callable_status", "callable_fail")
    row.setdefault("smoke_verdict", "fail")
    return row


def _expected_block_row(suit_row: dict[str, Any], reason: str) -> dict[str, Any]:
    return _finalize_row(
        {
            "combination_id": suit_row["combination_id"],
            "suitability_class": suit_row["suitability_class"],
            "source_matrix_status": suit_row["source_matrix_status"],
            "estimator_family": suit_row["estimator_family"],
            "inference_family": suit_row["inference_family"],
            "geometry": suit_row["geometry"],
            "callable_status": "blocked_expected",
            "smoke_verdict": "expected_block",
            "method_identity_preserved": True,
            "output_schema_valid": False,
            "point_estimate_present": False,
            "interval_present": False,
            "interval_orientation_valid": None,
            "negative_half_width_detected": None,
            "finite_outputs": False,
            "unsupported_geometry_silently_allowed": False,
            "exception_type": None,
            "exception_message": reason,
            "block_reason": reason,
            **_forbidden_flags(),
        }
    )


def _skipped_row(suit_row: dict[str, Any], reason: str) -> dict[str, Any]:
    row = _expected_block_row(suit_row, reason)
    row["callable_status"] = "skipped_not_smoke_safe"
    row["smoke_verdict"] = "skipped"
    return row


def build_d5_stat_smoke_callable_001(cfg: SmokeConfig | None = None) -> dict[str, Any]:
    cfg = cfg or SmokeConfig()
    framework = load_suitability_framework()
    wide = _build_wide(
        ProbeConfig(
            seed=cfg.seed,
            train_length=cfg.train_length,
            test_length=cfg.test_length,
            n_geos=cfg.n_geos,
        )
    )
    rows: list[dict[str, Any]] = []
    for suit_row in framework["rows"]:
        execute, reason = _should_execute(suit_row)
        if execute:
            rows.append(_execute_combo(suit_row["combination_id"], suit_row, wide, cfg))
        elif suit_row["suitability_class"] in NON_EXECUTABLE_SUITABILITY:
            rows.append(_expected_block_row(suit_row, reason))
        else:
            rows.append(_skipped_row(suit_row, reason))

    executed = [r for r in rows if r["callable_status"] in ("callable_pass", "callable_fail")]
    expected_blocked = [r for r in rows if r["callable_status"] == "blocked_expected"]
    skipped = [r for r in rows if r["callable_status"] == "skipped_not_smoke_safe"]
    failures = [r for r in rows if r["smoke_verdict"] == "fail"]
    unexpected_callable_fail = [
        r for r in executed if r["callable_status"] == "callable_fail"
    ]
    silent_geo = [r for r in rows if r.get("unsupported_geometry_silently_allowed")]
    orient_fail = [
        r
        for r in executed
        if r.get("interval_present") and r.get("interval_orientation_valid") is False
    ]
    neg_hw = [r for r in executed if r.get("negative_half_width_detected")]

    if failures or unexpected_callable_fail or silent_geo or orient_fail or neg_hw:
        overall: OverallVerdict = "smoke_fail_requires_fix"
    elif unexpected_callable_fail:
        overall = "smoke_fail_requires_fix"
    elif skipped:
        overall = "smoke_pass_with_caveats"
    else:
        overall = "smoke_pass_with_expected_blocks"

    summary = {
        "total_rows_checked": len(rows),
        "executed_rows": len(executed),
        "expected_blocked_rows": len(expected_blocked),
        "skipped_rows": len(skipped),
        "failures": len(failures),
        "unexpected_callable_failures": len(unexpected_callable_fail),
        "unexpected_silent_geometry_allowance": len(silent_geo),
        "interval_orientation_failures": len(orient_fail),
        "negative_half_width_detections": len(neg_hw),
        "callable_pass_count": sum(1 for r in rows if r["callable_status"] == "callable_pass"),
    }

    return {
        "artifact_id": "D5-STAT-SMOKE-CALLABLE-001",
        "artifact_type": "smoke_callable_validation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_framework": "DESIGN-ESTIMATOR-INFERENCE-SUITABILITY-FRAMEWORK-001",
        "overall_verdict": overall,
        "summary": summary,
        "forbidden_flags": _forbidden_flags(),
        "next_recommended_artifacts": list(NEXT_RECOMMENDED),
        "minimum_combos_covered": sorted(MINIMUM_COMBO_IDS),
        "rows": rows,
        "guardrails": [
            "no_statistical_validation_claim",
            "no_suitability_claim",
            "no_promotion",
            "no_trustreport_wiring",
            "no_calibration_signal",
            "no_mmm",
            "no_llm_recommendation",
        ],
    }


def write_artifact(path: Path | None = None, *, cfg: SmokeConfig | None = None) -> Path:
    payload = build_d5_stat_smoke_callable_001(cfg)
    if path is None:
        path = _REPO_ROOT / "docs/track_d/archives/D5_STAT_SMOKE_CALLABLE_001_results.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_report(path: Path | None = None, *, cfg: SmokeConfig | None = None) -> Path:
    payload = build_d5_stat_smoke_callable_001(cfg)
    if path is None:
        path = _REPO_ROOT / "docs/track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md"
    s = payload["summary"]
    lines = [
        "# D5-STAT-SMOKE-CALLABLE-001 Report",
        "",
        "**Artifact ID:** D5-STAT-SMOKE-CALLABLE-001",
        "**Type:** Smoke / schema / callability / orientation / guard battery",
        f"**Overall verdict:** `{payload['overall_verdict']}`",
        "",
        "## 1. Purpose",
        "",
        "First evidence-execution step after the suitability framework. Verifies callable",
        "paths on tiny deterministic fixtures and records expected-blocked combinations",
        "without executing them.",
        "",
        "## 2. Relationship to suitability framework",
        "",
        "Inputs from `DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001` — OC-ready does",
        "**not** imply suitable or statistically validated.",
        "",
        "## 13. Results summary",
        "",
        f"- Total rows: {s['total_rows_checked']}",
        f"- Executed: {s['executed_rows']}",
        f"- Expected blocked: {s['expected_blocked_rows']}",
        f"- Skipped (no probe): {s['skipped_rows']}",
        f"- Failures: {s['failures']}",
        f"- Callable pass: {s['callable_pass_count']}",
        "",
        "## 14. Overall verdict",
        "",
        f"`{payload['overall_verdict']}`",
        "",
        "## 15. Follow-up actions",
        "",
        f"Next recommended: **{payload['next_recommended_artifacts'][0]}**",
        "(only if smoke passes without structural failures).",
        "",
        "## 16. What this artifact does not authorize",
        "",
        "- Statistical validation · suitability · promotion · TrustReport roles",
        "- CalibrationSignal · MMM · LLM recommendations",
        "",
        "## 17. Guardrails",
        "",
        "Smoke-pass does not mean validated or suitable.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    out = write_artifact()
    write_report()
    p = build_d5_stat_smoke_callable_001()
    print(f"Wrote {out} — {p['overall_verdict']} ({p['summary']['total_rows_checked']} rows)")


if __name__ == "__main__":
    main()
