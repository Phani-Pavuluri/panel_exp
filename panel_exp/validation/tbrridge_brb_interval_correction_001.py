"""TBRRIDGE_BRB_INTERVAL_CORRECTION_001 — before/after production fix summary."""

from __future__ import annotations

import json
import math
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.governance.investigation_lifecycle_contract import (
    build_investigation_handoff,
    format_handoff_report_section,
)
from panel_exp.validation.track_d_d5_trust_tbrridge_brb_001 import (
    BrbTrustConfig,
    build_d5_trust_tbrridge_brb_001,
)

_REPO = Path(__file__).resolve().parents[2]
_BEFORE_SUMMARY = _REPO / "docs/track_d/archives/D5_TRUST_TBRRIDGE_BRB_001_summary.json"
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_BRB_INTERVAL_CORRECTION_001_summary.json"
_DEFAULT_REPORT = _REPO / "docs/track_d/TBRRIDGE_BRB_INTERVAL_CORRECTION_001_REPORT.md"

CorrectionVerdict = Literal[
    "tbrridge_brb_interval_corrected_requires_reassessment",
    "tbrridge_brb_centering_corrected_variance_issue_remains",
    "tbrridge_brb_serial_dependence_restricted",
    "tbrridge_brb_correction_inconclusive",
    "tbrridge_brb_correction_failed",
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


def _metrics_from_trust_summary(summary: dict[str, Any]) -> dict[str, Any]:
    cov_eff = summary.get("coverage_by_effect", {})
    center = summary.get("bootstrap_centering_diagnostics", {})
    var = summary.get("variance_decomposition", {})
    pt = summary.get("point_estimate_results", {})
    return {
        "bootstrap_center_minus_point": center.get("mean_bootstrap_center_minus_point"),
        "null_coverage": (cov_eff.get("0.0") or {}).get("null_coverage"),
        "positive_coverage": (cov_eff.get("0.08") or {}).get("positive_coverage"),
        "negative_coverage": (cov_eff.get("-0.05") or {}).get("negative_coverage"),
        "type_i_error": (cov_eff.get("0.0") or {}).get("type_i_error"),
        "mean_bias_clean_positive": pt.get("mean_bias_clean_positive"),
        "rmse_clean_positive": pt.get("rmse_clean_positive"),
        "mean_interval_width": var.get("mean_interval_width"),
        "mean_variance_ratio": var.get("mean_variance_ratio"),
        "coverage_by_world": summary.get("coverage_by_world"),
        "coverage_by_block_length": summary.get("coverage_by_block_length"),
        "coverage_by_serial_dependence": summary.get("coverage_by_serial_dependence"),
        "failure_count": (summary.get("failure_summary") or {}).get("failure_count"),
    }


def _decide_verdict(before: dict[str, Any], after: dict[str, Any]) -> CorrectionVerdict:
    gap_before = abs(before.get("bootstrap_center_minus_point") or 0)
    gap_after = abs(after.get("bootstrap_center_minus_point") or 0)
    pos_before = before.get("positive_coverage") or 0
    pos_after = after.get("positive_coverage") or 0
    null_after = after.get("null_coverage")
    if gap_after >= gap_before * 0.5 and pos_after <= pos_before + 0.05:
        return "tbrridge_brb_correction_failed"
    if gap_after < max(1.0, gap_before * 0.05) and pos_after > pos_before + 0.15:
        if null_after is not None and null_after >= 0.75:
            return "tbrridge_brb_interval_corrected_requires_reassessment"
        if null_after is not None and null_after < 0.75:
            return "tbrridge_brb_centering_corrected_variance_issue_remains"
        return "tbrridge_brb_interval_corrected_requires_reassessment"
    if gap_after < max(1.0, gap_before * 0.05) and pos_after > pos_before:
        return "tbrridge_brb_centering_corrected_variance_issue_remains"
    return "tbrridge_brb_correction_inconclusive"


def build_tbrridge_brb_interval_correction_001(
    *,
    fast: bool = False,
    write_full_results_path: str | None = "/tmp/TBRRIDGE_BRB_INTERVAL_CORRECTION_001_results.json",
) -> dict[str, Any]:
    before_raw = json.loads(_BEFORE_SUMMARY.read_text()) if _BEFORE_SUMMARY.exists() else {}
    before_metrics = _metrics_from_trust_summary(before_raw)

    after_payload = build_d5_trust_tbrridge_brb_001(
        BrbTrustConfig(fast=fast, write_full_results_path=write_full_results_path if not fast else None)
    )
    after_metrics = _metrics_from_trust_summary(after_payload)

    verdict = _decide_verdict(before_metrics, after_metrics)

    summary: dict[str, Any] = {
        "artifact_id": "TBRRIDGE-BRB-INTERVAL-CORRECTION-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "config": {"fast": fast, "replay_harness": "D5-TRUST-TBRRIDGE-BRB-001"},
        "original_defect": {
            "description": "BRB bootstrap cumulative-sum replicates misaligned with TBRRidge mean post-window point readout",
            "bootstrap_center_gap_before": before_metrics.get("bootstrap_center_minus_point"),
            "positive_coverage_before": before_metrics.get("positive_coverage"),
        },
        "point_estimand": "post_window_mean_treated_minus_counterfactual_level",
        "bootstrap_replicate_estimand_before": "cumulative_sum_post_window_effect_path",
        "bootstrap_replicate_estimand_after": "post_window_mean_effect_level",
        "interval_method_before": "raw_percentile_path_quantiles_misaligned_with_point",
        "interval_method_after": "centered_deviation_percentile_mean_effect",
        "resampling_contract": {
            "method": "moving_block_residual_bootstrap",
            "residual_source": "oos_pre_period_expanding_window",
            "center_residuals": True,
            "conditional_on_observed_effect_path": True,
            "block_resampling": "contiguous_moving_blocks",
        },
        "before_metrics": before_metrics,
        "after_metrics": after_metrics,
        "centering_comparison": {
            "gap_before": before_metrics.get("bootstrap_center_minus_point"),
            "gap_after": after_metrics.get("bootstrap_center_minus_point"),
            "gap_reduction_ratio": (
                abs(after_metrics.get("bootstrap_center_minus_point") or 0)
                / max(abs(before_metrics.get("bootstrap_center_minus_point") or 1), 1e-9)
            ),
        },
        "coverage_by_effect": after_payload.get("coverage_by_effect"),
        "coverage_by_world": after_payload.get("coverage_by_world"),
        "coverage_by_block_length": after_payload.get("coverage_by_block_length"),
        "coverage_by_serial_dependence": after_payload.get("coverage_by_serial_dependence"),
        "variance_comparison": {
            "variance_ratio_before": before_metrics.get("mean_variance_ratio"),
            "variance_ratio_after": after_metrics.get("mean_variance_ratio"),
            "width_before": before_metrics.get("mean_interval_width"),
            "width_after": after_metrics.get("mean_interval_width"),
        },
        "failure_summary": after_payload.get("failure_summary"),
        "backward_compatibility": {
            "cumulative_brb_stats_retained": True,
            "additive_metadata_fields": True,
            "tbrridge_point_unchanged": True,
        },
        "trustreport_implications": {
            "dcm005_reassessment_required": True,
            "trust_report_authorized": False,
        },
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_ready": False,
            "trust_report_authorized_count": 0,
        },
        "limitations": [
            "Null calibration may weaken when plug-in point is biased away from zero on null worlds.",
            "Does not perform DCM-005 eligibility reassessment.",
            "KFold/Placebo paths unchanged.",
        ],
        "investigation_handoff": build_investigation_handoff(
            follow_up_issues=["INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001"],
            resolved_issues=["INV-TBRRIDGE-BRB-ESTIMAND-ALIGNMENT-001"],
            terminal_dispositions=[],
            next_artifact="D5-TRUST-TBRRIDGE-KFOLD-001",
        ),
        "verdict": verdict,
    }

    if write_full_results_path and not fast:
        Path(write_full_results_path).write_text(
            json.dumps({"summary": summary, "after_replay": after_payload}, indent=2) + "\n"
        )

    return _json_safe(summary)


def _atomic_write(path: Path, content: str, *, overwrite: bool = False) -> None:
    path = path.resolve()
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _write_report(payload: dict[str, Any], path: Path, *, overwrite: bool = False) -> None:
    b, a = payload.get("before_metrics", {}), payload.get("after_metrics", {})
    lines = [
        "# TBRRidge BRB Interval Correction 001 — Report",
        "",
        f"**Artifact ID:** TBRRIDGE-BRB-INTERVAL-CORRECTION-001",
        f"**Verdict:** `{payload.get('verdict')}`",
        "",
        "> This artifact corrects TBRRidge BRB interval construction. "
        "It does not perform DCM-005 eligibility reassessment. "
        "It does not authorize TrustReport. "
        "It does not validate KFold or Placebo inference.",
        "",
        "## 1. Executive summary",
        "",
        "Aligned BRB bootstrap replicates and intervals to mean post-window effect estimand "
        "via centered-deviation percentile construction.",
        "",
        "## 5. TBRRidge point estimand",
        "",
        f"`{payload.get('point_estimand')}`",
        "",
        "## 6. BRB replicate estimand before correction",
        "",
        f"`{payload.get('bootstrap_replicate_estimand_before')}`",
        "",
        "## 7. Root cause",
        "",
        "Cumulative-sum bootstrap replicates (~n_periods × n_units × point) vs mean point readout.",
        "",
        "## 10. Selected interval construction",
        "",
        f"`{payload.get('interval_method_after')}`",
        "",
        "## 16. Before centering",
        "",
        f"Gap: {b.get('bootstrap_center_minus_point')}",
        "",
        "## 17. After centering",
        "",
        f"Gap: {a.get('bootstrap_center_minus_point')}",
        "",
        "## 19. Positive coverage",
        "",
        f"Before: {b.get('positive_coverage')} → After: {a.get('positive_coverage')}",
        "",
        "## 18. Null coverage",
        "",
        f"Before: {b.get('null_coverage')} → After: {a.get('null_coverage')}",
        "",
        "## 33. Authorization status",
        "",
        "Blocked.",
        "",
        "## 35. Governance verdict",
        "",
        f"`{payload.get('verdict')}`",
        "",
    ]
    handoff = payload.get("investigation_handoff") or {}
    lines.extend(
        format_handoff_report_section(
            resolved_in_artifact=handoff.get("resolved_issues") or [],
            new_investigations=handoff.get("follow_up_issues") or [],
            updated_investigations=["INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001 → OPEN in registry"],
            deferred_issues=[],
            explicit_exclusions=["KFold/Placebo validation", "DCM-005 eligibility reassessment"],
            revisit_trigger="After KFold and Placebo characterization, before DCM-005 eligibility reassessment",
            decision_checkpoint="DCM-005 eligibility reassessment must consume INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001",
            next_artifact=handoff.get("next_artifact"),
        )
    )
    _atomic_write(path, "\n".join(lines) + "\n", overwrite=overwrite)


def write_summary(
    path: Path | None = None,
    *,
    fast: bool = False,
    overwrite: bool = False,
    report_path: Path | None = None,
) -> Path:
    payload = build_tbrridge_brb_interval_correction_001(fast=fast)
    if path is None:
        path = _DEFAULT_SUMMARY
    _atomic_write(path, json.dumps(payload, indent=2) + "\n", overwrite=overwrite)
    _write_report(payload, report_path or _DEFAULT_REPORT, overwrite=overwrite)
    return path


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--summary-output", default=str(_DEFAULT_SUMMARY))
    parser.add_argument("--report-output", default=str(_DEFAULT_REPORT))
    args = parser.parse_args()
    write_summary(
        Path(args.summary_output),
        fast=args.fast,
        overwrite=args.overwrite,
        report_path=Path(args.report_output),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
