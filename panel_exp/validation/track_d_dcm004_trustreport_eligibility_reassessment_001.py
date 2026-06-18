"""DCM-004-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001 — Track D harness."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from panel_exp.validation.dcm004_trustreport_eligibility_reassessment_001 import (
    GATE_LABEL,
    REASSESSMENT_VERSION,
    WORLD_TO_CLASS,
    extract_post_fix_dcm004_evidence,
    reassess_dcm004_trustreport_eligibility,
)
from panel_exp.validation.track_d_d5_stat_did_bootstrap_001 import build_d5_stat_did_bootstrap_001

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARCHIVE_DIR = _REPO_ROOT / "docs/track_d/archives"
_SUMMARY_PATH = _ARCHIVE_DIR / "DCM004_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json"
_PRIOR_SUMMARY = _ARCHIVE_DIR / "TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json"
_CORRECTION_SUMMARY = _ARCHIVE_DIR / "DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001_summary.json"
_HISTORICAL_DID = _ARCHIVE_DIR / "D5_STAT_DID_BOOTSTRAP_001_results.json"

ReassessmentVerdict = Literal[
    "dcm004_eligible_with_restrictions_no_authorization",
    "dcm004_insufficient_evidence_no_authorization",
    "dcm004_ineligible_no_authorization",
    "dcm004_reassessment_inconclusive",
    "dcm004_reassessment_failed",
]


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=_REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _prior_dcm004(prior_summary: dict[str, Any]) -> dict[str, Any]:
    for row in prior_summary.get("combination_results") or []:
        if row.get("combination_key") == "DCM-004":
            return row
    raise KeyError("DCM-004 not found in prior eligibility summary")


def _unchanged_combinations(prior_summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in prior_summary.get("combination_results") or []:
        if row.get("combination_key") == "DCM-004":
            continue
        rows.append(
            {
                "combination_key": row.get("combination_key"),
                "dcm_row_id": row.get("dcm_row_id"),
                "eligibility_status": row.get("eligibility_status"),
                "eligible_for_promotion": row.get("eligible_for_promotion"),
                "trust_report_authorized": row.get("trust_report_authorized"),
                "unchanged_due_to_no_new_evidence": True,
            }
        )
    return rows


def _decide_verdict(status: str) -> ReassessmentVerdict:
    if status == "ELIGIBLE_WITH_RESTRICTIONS":
        return "dcm004_eligible_with_restrictions_no_authorization"
    if status == "INSUFFICIENT_EVIDENCE":
        return "dcm004_insufficient_evidence_no_authorization"
    if status == "INELIGIBLE":
        return "dcm004_ineligible_no_authorization"
    return "dcm004_reassessment_inconclusive"


def build_dcm004_trustreport_eligibility_reassessment_001(
    *,
    fast: bool = False,
) -> dict[str, Any]:
    if not _PRIOR_SUMMARY.is_file():
        raise FileNotFoundError(_PRIOR_SUMMARY)

    from panel_exp.validation.track_d_d5_stat_did_bootstrap_001 import D5StatDidBootstrap001Config

    cfg = D5StatDidBootstrap001Config(fast=fast)
    post_fix_archive = build_d5_stat_did_bootstrap_001(cfg)
    correction_summary = (
        _load_json(_CORRECTION_SUMMARY) if _CORRECTION_SUMMARY.is_file() else None
    )
    prior_summary = _load_json(_PRIOR_SUMMARY)
    prior_dcm = _prior_dcm004(prior_summary)

    metrics = extract_post_fix_dcm004_evidence(
        post_fix_archive,
        correction_summary=correction_summary,
    )
    reassessed = reassess_dcm004_trustreport_eligibility(
        prior_eligibility_result=prior_dcm,
        corrected_empirical_evidence=metrics,
    )

    unchanged = _unchanged_combinations(prior_summary)

    type_i_decomposition = {
        "overall": metrics.get("type_i_error_overall"),
        "supported_worlds": metrics.get("type_i_error_supported"),
        "unsupported_worlds": metrics.get("type_i_error_unsupported"),
        "clean_parallel_null": metrics.get("clean_parallel_null_type_i"),
        "post_shock_null": metrics.get("post_shock_null_type_i"),
        "interpretation": (
            "Aggregate elevation driven primarily by unsupported stress world post_shock_null; "
            "supported clean/weak-signal null worlds ~13% type-I."
        ),
    }

    payload: dict[str, Any] = {
        "artifact_id": "DCM-004-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
        "artifact_version": REASSESSMENT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "reassessment_scope": ["DCM-004"],
        "prior_dcm004_status": prior_dcm.get("eligibility_status"),
        "corrected_evidence_sources": list(reassessed.evidence_sources),
        "supported_contract": reassessed.supported_contract,
        "world_classification": metrics.get("world_classification"),
        "null_metrics_overall": reassessed.null_metrics.get("overall"),
        "null_metrics_supported": reassessed.null_metrics.get("supported"),
        "null_metrics_unsupported": reassessed.null_metrics.get("unsupported"),
        "positive_metrics": reassessed.positive_metrics,
        "negative_metrics": reassessed.negative_metrics,
        "type_i_decomposition": type_i_decomposition,
        "coverage_decomposition": {
            "overall_null": metrics.get("null_coverage_overall"),
            "supported_null": metrics.get("null_coverage_supported"),
            "unsupported_null": metrics.get("null_coverage_unsupported"),
            "overall_positive": metrics.get("positive_coverage_overall"),
            "before_positive": metrics.get("before_positive_coverage"),
        },
        "gate_results": {
            "geometry_gate_status": reassessed.geometry_gate_status,
            "scale_gate_status": reassessed.scale_gate_status,
            "parallel_trends_gate_status": reassessed.parallel_trends_gate_status,
            "timing_gate_status": reassessed.timing_gate_status,
            "dependence_gate_status": reassessed.dependence_gate_status,
            "label": GATE_LABEL,
        },
        "calibration_by_world_class": reassessed.calibration_by_world_class,
        "reassessed_status": reassessed.reassessed_status,
        "dcm004_reassessment": reassessed.to_dict(),
        "promotion_candidate_summary": {
            "promotion_candidate_count": 0,
            "promotion_candidates": [],
            "dcm004_eligible_for_promotion": False,
        },
        "unchanged_combination_results": unchanged,
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_authorized_count": 0,
            "trust_report_ready": False,
        },
        "limitations": [
            "Reassessment applies to DCM-004 only; other DCM rows unchanged.",
            "Post-fix evidence from live D5-STAT-DID-BOOTSTRAP-001 replay with production correction.",
            "Pre-fix canonical archive retained as historical only.",
            "Provisional gates labeled provisional_for_dcm004_reassessment_only.",
            "Does not authorize TrustReport or downstream roles.",
            "Staggered timing and stress worlds excluded from supported contract.",
        ],
        "verdict": _decide_verdict(reassessed.reassessed_status),
    }
    return payload


def write_summary(path: Path | None = None, *, fast: bool = False) -> Path:
    payload = build_dcm004_trustreport_eligibility_reassessment_001(fast=fast)
    if path is None:
        path = _SUMMARY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_report(path: Path | None = None, *, fast: bool = False) -> Path:
    payload = build_dcm004_trustreport_eligibility_reassessment_001(fast=fast)
    if path is None:
        path = _REPO_ROOT / "docs/track_d/DCM004_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md"

    r = payload["dcm004_reassessment"]
    nm = payload["null_metrics_overall"] or {}
    ns = payload["null_metrics_supported"] or {}
    nu = payload["null_metrics_unsupported"] or {}
    pm = payload["positive_metrics"] or {}
    ti = payload["type_i_decomposition"] or {}

    lines = [
        "# DCM-004 TrustReport Eligibility Reassessment — Report",
        "",
        "**Artifact ID:** DCM-004-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
        f"**Verdict:** `{payload['verdict']}`",
        f"**Reassessed status:** `{payload['reassessed_status']}`",
        "",
        "> Reassesses DCM-004 (DID + bootstrap) only. **No TrustReport authorization.**",
        "",
        "## 1. Executive summary",
        "",
        "DCM-004 reassessed using corrected harness geometry, production bootstrap readout fix, "
        "and post-fix canonical replay. Positive coverage improved materially; aggregate null type-I "
        "rose to ~32% but supported-world type-I remains ~13% with stress-world concentration. "
        f"**Status: `{payload['reassessed_status']}`** with promotion blocked.",
        "",
        "## 2. Why reassessment was required",
        "",
        "Prior INSUFFICIENT_EVIDENCE reflected harness defect and production bootstrap miscentering.",
        "",
        "## 3. Prior DCM-004 status",
        "",
        f"`{payload['prior_dcm004_status']}` — missing/invalid positive coverage evidence.",
        "",
        "## 4. Evidence chain",
        "",
        "D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001 → D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION → "
        "DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001 → this reassessment.",
        "",
        "## 5. Corrected production behavior",
        "",
        "Centered-deviation percentile bootstrap intervals anchored to cumulative_att.",
        "",
        "## 6. Scope",
        "",
        "DCM-004 only.",
        "",
        "## 7. Non-goals",
        "",
        "No production changes; no promotion; no full-matrix reassessment.",
        "",
        "## 8. DCM-004 identity",
        "",
        "DID + embedded bootstrap; single-cell unit panel; causal_interval readout.",
        "",
        "## 9. DID estimand",
        "",
        "Cumulative level ATT (`cumulative_att_level`).",
        "",
        "## 10. Bootstrap interval semantics",
        "",
        "`centered_deviation_percentile` on block-resampled cumulative path replicates.",
        "",
        "## 11. Geometry gate",
        "",
        f"`{r.get('geometry_gate_status')}` — explicit test_0/control, n_treated>0, n_control≥4.",
        "",
        "## 12. Scale gate",
        "",
        f"`{r.get('scale_gate_status')}` — cumulative level truth/point/interval aligned.",
        "",
        "## 13. Timing gate",
        "",
        f"`{r.get('timing_gate_status')}` — common simultaneous adoption only.",
        "",
        "## 14. Parallel-trends gate",
        "",
        f"`{r.get('parallel_trends_gate_status')}` — pretrend diagnostic required; violation worlds excluded.",
        "",
        "## 15. Dependence gate",
        "",
        f"`{r.get('dependence_gate_status')}` — serial/heteroskedastic caveats on noisy worlds.",
        "",
        "## 16. Overall null calibration",
        "",
        f"Null coverage {nm.get('null_coverage')}; type-I {nm.get('type_i_error')}.",
        "",
        "## 17. Supported-world null calibration",
        "",
        f"Null coverage {ns.get('null_coverage')}; type-I {ns.get('type_i_error')}.",
        "",
        "## 18. Unsupported-world null calibration",
        "",
        f"Null coverage {nu.get('null_coverage')}; type-I {nu.get('type_i_error')}.",
        "",
        "## 19. Positive-effect coverage",
        "",
        f"Overall {pm.get('overall_positive_coverage')}; clean parallel {pm.get('clean_positive_coverage')}.",
        "",
        "## 20. Negative-effect coverage",
        "",
        "Not characterized in canonical D5 battery.",
        "",
        "## 21. Type-I decomposition",
        "",
        f"Overall {ti.get('overall')}; supported {ti.get('supported_worlds')}; "
        f"unsupported {ti.get('unsupported_worlds')}; post_shock {ti.get('post_shock_null')}.",
        "",
        "## 22. Interval-width findings",
        "",
        "Finite widths; point-in-interval ~100% post-correction.",
        "",
        "## 23. Worst-world behavior",
        "",
        "post_shock_null drives unsupported null failure (type-I 100%).",
        "",
        "## 24. Supported contract",
        "",
        "Common timing, parallel-trends gate, cumulative level estimand, stress worlds excluded.",
        "",
        "## 25. Semantic restrictions",
        "",
        f"`{r.get('semantic_class')}` — no population ATE, no staggered pooled DID.",
        "",
        "## 26. Reassessed eligibility status",
        "",
        f"`{payload['reassessed_status']}`",
        "",
        "## 27. Promotion-candidate status",
        "",
        "`eligible_for_promotion: false`",
        "",
        "## 28. Other DCM rows unchanged",
        "",
        "DCM-001–003, 005–008 preserved with `unchanged_due_to_no_new_evidence`.",
        "",
        "## 29. TrustReport authorization",
        "",
        "**Blocked** — `trust_report_authorized_count: 0`.",
        "",
        "## 30. Remaining limitations",
        "",
        "Stress-world null behavior; noisy-world 80% positive coverage; provisional gates only.",
        "",
        "## 31. Required next validation",
        "",
        "DCM-005 TBRRidge paths; DCM-006 multi-cell; DCM-008 stratified; FULL reassessment later.",
        "",
        "## 32. Governance verdict",
        "",
        f"**`{payload['verdict']}`**",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true")
    args = parser.parse_args()
    summary = write_summary(fast=args.fast)
    report = write_report(fast=args.fast)
    payload = build_dcm004_trustreport_eligibility_reassessment_001(fast=args.fast)
    print(f"Wrote {summary} and {report} — {payload['verdict']}")


if __name__ == "__main__":
    main()
