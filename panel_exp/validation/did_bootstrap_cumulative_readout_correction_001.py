"""DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001 — before/after production fix summary."""

from __future__ import annotations

import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.validation.track_d_d5_stat_did_bootstrap_001 import (
    D5StatDidBootstrap001Config,
    build_d5_stat_did_bootstrap_001,
)

_REPO = Path(__file__).resolve().parents[2]
_BEFORE_ARCHIVE = _REPO / "docs/track_d/archives/D5_STAT_DID_BOOTSTRAP_001_results.json"
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001_summary.json"
)

CorrectionVerdict = Literal[
    "did_bootstrap_cumulative_readout_corrected_requires_reassessment",
    "did_bootstrap_centering_corrected_variance_issue_remains",
    "did_bootstrap_common_timing_restricted",
    "did_bootstrap_correction_inconclusive",
    "did_bootstrap_correction_failed",
]


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (np.bool_, bool)) or type(obj) is bool:
        return bool(obj)
    if isinstance(obj, (np.floating, float)):
        v = float(obj)
        return v if np.isfinite(v) else None
    if isinstance(obj, (np.integer, int)) and not isinstance(obj, bool):
        return int(obj)
    return obj


def _extract_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    agg = payload.get("aggregate_metrics", {})
    runs = [r for r in payload.get("run_results", []) if r.get("callable_status") == "callable_pass"]
    gaps = [
        r["point_minus_bootstrap_center"]
        for r in runs
        if r.get("point_minus_bootstrap_center") is not None and np.isfinite(r["point_minus_bootstrap_center"])
    ]
    widths = [r["interval_width"] for r in runs if r.get("interval_width") is not None]
    pt_in = [
        bool(r["interval_lower"] <= r["point_estimate"] <= r["interval_upper"])
        for r in runs
        if None not in (r.get("interval_lower"), r.get("interval_upper"), r.get("point_estimate"))
    ]
    biases = [r["bias"] for r in runs if r.get("bias") is not None]
    pos_worlds = [w for w, m in agg.items() if m.get("positive_coverage") is not None]
    null_worlds = [w for w, m in agg.items() if m.get("null_coverage") is not None]
    by_world = {
        wid: {
            "coverage": m.get("coverage"),
            "null_coverage": m.get("null_coverage"),
            "positive_coverage": m.get("positive_coverage"),
            "mean_bias": m.get("mean_bias"),
            "rmse": m.get("rmse"),
            "mean_interval_width": m.get("mean_interval_width"),
            "feasible_runs": m.get("feasible_runs"),
        }
        for wid, m in agg.items()
    }
    worst_pos = min((by_world[w].get("positive_coverage") or 0.0) for w in pos_worlds) if pos_worlds else None
    return {
        "null_coverage": summary.get("null_coverage"),
        "positive_coverage": summary.get("positive_coverage"),
        "type_i_error": summary.get("type_i_error"),
        "sign_accuracy_positive": summary.get("sign_accuracy_positive"),
        "mean_point_minus_bootstrap_center": float(np.mean(gaps)) if gaps else None,
        "median_point_minus_bootstrap_center": float(np.median(gaps)) if gaps else None,
        "max_abs_point_minus_bootstrap_center": float(np.max(np.abs(gaps))) if gaps else None,
        "point_in_interval_rate": float(np.mean(pt_in)) if pt_in else None,
        "mean_bias": float(np.mean(biases)) if biases else None,
        "rmse": float(math.sqrt(np.mean(np.array(biases) ** 2))) if biases else None,
        "mean_interval_width": float(np.mean(widths)) if widths else None,
        "bootstrap_variance_mean": float(np.mean([r.get("bootstrap_standard_error") ** 2 for r in runs if r.get("bootstrap_standard_error")])) if runs else None,
        "failure_rate": payload.get("summary", {}).get("total_failures", 0)
        / max(payload.get("summary", {}).get("total_runs", 1), 1),
        "coverage_by_world": by_world,
        "worst_world_positive_coverage": worst_pos,
        "total_runs": payload.get("summary", {}).get("total_runs"),
    }


def _decide_verdict(before: dict[str, Any], after: dict[str, Any]) -> CorrectionVerdict:
    if after.get("positive_coverage") is None or after.get("null_coverage") is None:
        return "did_bootstrap_correction_inconclusive"
    pos_improved = (after.get("positive_coverage") or 0) >= 0.75 and (
        before.get("positive_coverage") or 0
    ) < 0.25
    pt_in_improved = (after.get("point_in_interval_rate") or 0) >= 0.95 and (
        before.get("point_in_interval_rate") or 0
    ) < 0.75
    clean_after = (after.get("coverage_by_world") or {}).get("clean_parallel_positive_lift", {})
    clean_null_after = (after.get("coverage_by_world") or {}).get("clean_parallel_null", {})
    clean_pos_cov = clean_after.get("positive_coverage")
    clean_null_cov = clean_null_after.get("null_coverage")
    clean_ok = (clean_pos_cov or 0) >= 0.85 and (clean_null_cov or 0) >= 0.8
    null_not_catastrophic = (after.get("type_i_error") or 0) <= 0.35
    if pos_improved and pt_in_improved and clean_ok and null_not_catastrophic:
        return "did_bootstrap_cumulative_readout_corrected_requires_reassessment"
    if pos_improved and pt_in_improved and clean_ok:
        return "did_bootstrap_centering_corrected_variance_issue_remains"
    if pos_improved and clean_ok:
        return "did_bootstrap_correction_inconclusive"
    return "did_bootstrap_correction_failed"


def build_did_bootstrap_cumulative_readout_correction_001(
    *,
    fast: bool = False,
) -> dict[str, Any]:
    cfg = D5StatDidBootstrap001Config(fast=fast)
    before_payload = json.loads(_BEFORE_ARCHIVE.read_text(encoding="utf-8")) if _BEFORE_ARCHIVE.is_file() else {}
    after_payload = build_d5_stat_did_bootstrap_001(cfg)
    before = _extract_metrics(before_payload)
    after = _extract_metrics(after_payload)
    verdict = _decide_verdict(before, after)
    return _json_safe(
        {
            "artifact_id": "DID-BOOTSTRAP-CUMULATIVE-READOUT-CORRECTION-001",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "verdict": verdict,
            "production_change": {
                "file": "panel_exp/methods/DID.py",
                "bootstrap_interval_method": "centered_deviation_percentile",
                "bootstrap_replicate_estimand": "cumulative_path_att_block_resampled_panel",
                "interval_construction": "point_estimate + quantiles(bootstrap_replicate - bootstrap_center)",
                "point_estimand": "cumulative_path_att_original_panel",
                "truth_scale": "cumulative_level",
                "timing_geometry": "common_simultaneous_adoption",
            },
            "before_metrics": before,
            "after_metrics": after,
            "delta": {
                "null_coverage": _delta(before.get("null_coverage"), after.get("null_coverage")),
                "positive_coverage": _delta(before.get("positive_coverage"), after.get("positive_coverage")),
                "type_i_error": _delta(before.get("type_i_error"), after.get("type_i_error")),
                "point_in_interval_rate": _delta(
                    before.get("point_in_interval_rate"), after.get("point_in_interval_rate")
                ),
                "mean_point_minus_bootstrap_center": _delta(
                    before.get("mean_point_minus_bootstrap_center"),
                    after.get("mean_point_minus_bootstrap_center"),
                ),
            },
            "forbidden_flags": {
                "trust_report_authorized": bool(False),
                "trust_report_ready": bool(False),
                "dcm004_reassessment_complete": bool(False),
            },
            "next_recommended_artifact": "DCM-004 eligibility reassessment",
        }
    )


def _delta(before: float | None, after: float | None) -> float | None:
    if before is None or after is None:
        return None
    return float(after - before)


def write_summary(path: Path | None = None, *, fast: bool = False, overwrite: bool = False) -> Path:
    path = (path or _DEFAULT_SUMMARY).resolve()
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite: {path}")
    payload = build_did_bootstrap_cumulative_readout_correction_001(fast=fast)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=_DEFAULT_SUMMARY)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--fast", action="store_true")
    args = parser.parse_args()
    out = write_summary(args.output, fast=args.fast, overwrite=args.overwrite)
    payload = build_did_bootstrap_cumulative_readout_correction_001(fast=args.fast)
    print(f"Wrote {out} — {payload['verdict']}")


if __name__ == "__main__":
    main()
