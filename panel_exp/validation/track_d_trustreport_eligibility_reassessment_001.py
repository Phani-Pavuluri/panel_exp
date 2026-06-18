"""TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001 — Track D harness."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from panel_exp.validation.trustreport_eligibility_reassessment_001 import (
    REASSESSMENT_VERSION,
    GATE_LABEL,
    extract_corrected_dcm001_evidence,
    reassess_trustreport_eligibility,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARCHIVE_DIR = _REPO_ROOT / "docs" / "track_d" / "archives"
_SUMMARY_PATH = _ARCHIVE_DIR / "TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json"
_PRIOR_SUMMARY = _ARCHIVE_DIR / "TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json"
_CORRECTED_ARCHIVE = _ARCHIVE_DIR / "D5_STAT_SCM_JK_001_results.json"
_HISTORICAL_ARCHIVE = (
    _ARCHIVE_DIR / "D5_STAT_SCM_JK_001_results_historical_pre_harness_correction.json"
)

ReassessmentVerdict = Literal[
    "trustreport_dcm001_eligible_with_restrictions_no_authorization",
    "trustreport_dcm001_promotion_candidate_no_authorization",
    "trustreport_dcm001_insufficient_evidence_no_authorization",
    "trustreport_dcm001_ineligible_no_authorization",
    "trustreport_reassessment_inconclusive",
    "trustreport_reassessment_failed",
]

PROVISIONAL_GATES = {
    "label": GATE_LABEL,
    "geometry": {
        "min_control_units": 4,
        "requires_test_0_assignment": True,
        "no_treated_control_overlap": True,
    },
    "effect_scale": {
        "canonical": "level_effect",
        "forbid_fractional_percent_truth_for_coverage": True,
    },
    "statistical": {
        "coverage_positive_min": 0.50,
        "coverage_nominal": 0.90,
        "coverage_deviation_max": 0.15,
        "type_i_error_clean_null_max": 0.10,
        "noisy_world_coverage_warning_below": 0.85,
        "failure_rate_max": 0.10,
    },
    "semantic": {
        "estimand": "treated_unit_effect",
        "readout_class": "restricted_causal_interval",
        "inference": "unit_jackknife",
        "population_ate_blocked": True,
        "pooled_multicell_blocked": True,
    },
}


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


def _prior_dcm001(prior_summary: dict[str, Any]) -> dict[str, Any]:
    for row in prior_summary.get("combination_results") or []:
        if row.get("combination_key") == "DCM-001":
            return row
    raise KeyError("DCM-001 not found in prior eligibility summary")


def _unchanged_combinations(prior_summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in prior_summary.get("combination_results") or []:
        if row.get("combination_key") == "DCM-001":
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


def _decide_verdict(result_status: str) -> ReassessmentVerdict:
    if result_status == "ELIGIBLE_CANDIDATE":
        return "trustreport_dcm001_promotion_candidate_no_authorization"
    if result_status == "ELIGIBLE_WITH_RESTRICTIONS":
        return "trustreport_dcm001_eligible_with_restrictions_no_authorization"
    if result_status == "INSUFFICIENT_EVIDENCE":
        return "trustreport_dcm001_insufficient_evidence_no_authorization"
    if result_status == "INELIGIBLE":
        return "trustreport_dcm001_ineligible_no_authorization"
    return "trustreport_reassessment_inconclusive"


def build_trustreport_eligibility_reassessment_001() -> dict[str, Any]:
    if not _CORRECTED_ARCHIVE.is_file():
        raise FileNotFoundError(_CORRECTED_ARCHIVE)
    if not _PRIOR_SUMMARY.is_file():
        raise FileNotFoundError(_PRIOR_SUMMARY)

    corrected = _load_json(_CORRECTED_ARCHIVE)
    prior_summary = _load_json(_PRIOR_SUMMARY)
    historical = _load_json(_HISTORICAL_ARCHIVE) if _HISTORICAL_ARCHIVE.is_file() else None

    prior_dcm = _prior_dcm001(prior_summary)
    metrics = extract_corrected_dcm001_evidence(corrected, historical_archive=historical)
    reassessed = reassess_trustreport_eligibility(
        prior_eligibility_result=prior_dcm,
        corrected_empirical_evidence=metrics,
    )

    gates = {
        "support_gate_status": reassessed.support_gate_status,
        "prefit_gate_status": reassessed.prefit_gate_status,
        "donor_gate_status": reassessed.donor_gate_status,
        "label": GATE_LABEL,
    }

    unchanged = _unchanged_combinations(prior_summary)
    promotion_candidates = [
        k
        for k, row in (
            (r["combination_key"], r) for r in unchanged
        )
        if row.get("eligible_for_promotion")
    ]
    if reassessed.eligible_for_promotion:
        promotion_candidates.append("DCM-001")

    payload: dict[str, Any] = {
        "artifact_id": "TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
        "artifact_version": REASSESSMENT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "prior_eligibility_artifact": "TRUSTREPORT-ELIGIBILITY-VALIDATION-001",
        "corrected_evidence_artifact": "D5-STAT-SCM-JK-001",
        "historical_evidence_artifact": "D5_STAT_SCM_JK_001_results_historical_pre_harness_correction.json",
        "reassessment_scope": ["DCM-001"],
        "provisional_gates": PROVISIONAL_GATES,
        "dcm_001_prior_status": prior_dcm.get("eligibility_status"),
        "dcm_001_reassessed_status": reassessed.reassessed_status,
        "dcm_001_metrics": {
            "null_coverage_level": reassessed.null_coverage,
            "positive_coverage_level": reassessed.positive_coverage,
            "positive_coverage_fractional_percent_excluded": metrics.get(
                "positive_coverage_fractional_percent"
            ),
            "negative_coverage_level": reassessed.negative_coverage,
            "type_i_error": reassessed.type_i_error,
            "failure_rate": reassessed.failure_rate,
            "worst_positive_coverage": reassessed.worst_world_coverage,
            "clean_positive_coverage": metrics.get("clean_positive_coverage"),
            "noisy_positive_coverage": metrics.get("noisy_positive_coverage"),
            "bias_level": metrics.get("bias_level"),
            "rmse_level": metrics.get("rmse_level"),
            "effect_scale": reassessed.effect_scale,
            "n_treated_mean": metrics.get("n_treated_mean"),
            "n_control_mean": metrics.get("n_control_mean"),
            "donor_count_mean": metrics.get("donor_count_mean"),
        },
        "support_gate_results": gates,
        "semantic_gate_results": {
            "semantic_class": reassessed.semantic_class,
            "treated_unit_only": True,
            "level_scale_only": True,
            "population_claim_blocked": True,
            "null_monitor_relabel_blocked": True,
        },
        "dcm_001_reassessment": reassessed.to_dict(),
        "unchanged_combination_results": unchanged,
        "promotion_candidate_summary": {
            "promotion_candidate_count": len(promotion_candidates),
            "promotion_candidates": promotion_candidates,
            "dcm_001_eligible_for_promotion": reassessed.eligible_for_promotion,
        },
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_authorized_count": 0,
            "trust_report_ready": False,
        },
        "limitations": [
            "Reassessment applies to DCM-001 only; other combinations unchanged.",
            "Provisional gates labeled provisional_for_trustreport_reassessment_only.",
            "Does not authorize TrustReport or downstream roles.",
            "Historical percent-scale coverage excluded from reassessment metrics.",
            "Stratified DCM-008 and multi-cell paths require separate artifacts.",
        ],
        "verdict": _decide_verdict(reassessed.reassessed_status),
    }
    return payload


def write_summary(path: Path | None = None) -> Path:
    payload = build_trustreport_eligibility_reassessment_001()
    if path is None:
        path = _SUMMARY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_report(path: Path | None = None) -> Path:
    payload = build_trustreport_eligibility_reassessment_001()
    if path is None:
        path = _REPO_ROOT / "docs/track_d/TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md"

    m = payload["dcm_001_metrics"]
    lines = [
        "# TrustReport Eligibility Reassessment 001 — Report",
        "",
        f"**Artifact ID:** TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
        f"**Verdict:** `{payload['verdict']}`",
        f"**DCM-001 reassessed status:** `{payload['dcm_001_reassessed_status']}`",
        "",
        "## 1. Executive summary",
        "",
        "Reassesses DCM-001 (SCM + UnitJackknife) using corrected canonical "
        "D5-STAT-SCM-JK-001 evidence after harness correction. Historical ~7% "
        "positive coverage interpretation is superseded. **No TrustReport authorization.**",
        "",
        "## 2. Why reassessment was required",
        "",
        "Harness correction fixed assignment geometry and level-consistent coverage metrics.",
        "",
        "## 3. Prior eligibility status",
        "",
        f"`{payload['dcm_001_prior_status']}` with positive coverage ~7% on invalid percent scale.",
        "",
        "## 4. Historical evidence defect",
        "",
        "Invalid `groups.values()` assignment and level-vs-fractional-percent truth mismatch.",
        "",
        "## 5. Corrected evidence source",
        "",
        "`D5_STAT_SCM_JK_001_results.json` (harness correction supersession metadata required).",
        "",
        "## 6. Scope",
        "",
        "DCM-001 only.",
        "",
        "## 7. Non-goals",
        "",
        "No TrustReport authorization; no SCM/JK algorithm changes; no unrelated DCM upgrades.",
        "",
        "## 8. DCM-001 identity",
        "",
        "SCM + UnitJackknife, unit-panel single-cell, treated-unit level effect.",
        "",
        "## 9. Geometry reassessment",
        "",
        f"n_treated_mean={m.get('n_treated_mean')}, n_control_mean={m.get('n_control_mean')}, "
        f"donor_count_mean={m.get('donor_count_mean')}.",
        "",
        "## 10. Effect-scale reassessment",
        "",
        f"Canonical `{m.get('effect_scale')}`; fractional-percent coverage excluded from eligibility.",
        "",
        "## 11. Null coverage",
        "",
        f"Level-scale null coverage: **{m.get('null_coverage_level')}**",
        "",
        "## 12. Positive-effect coverage",
        "",
        f"Level-scale positive coverage: **{m.get('positive_coverage_level')}** "
        f"(clean={m.get('clean_positive_coverage')}, noisy={m.get('noisy_positive_coverage')}).",
        "",
        "## 13. Negative-effect coverage",
        "",
        "Not evaluated in D5-STAT-SCM-JK-001 battery.",
        "",
        "## 14. Type-I error",
        "",
        f"Empirical type-I error: **{m.get('type_i_error')}**",
        "",
        "## 15. Bias and RMSE",
        "",
        f"bias_level={m.get('bias_level')}, rmse_level={m.get('rmse_level')} (level scale).",
        "",
        "## 16. Pre-fit sensitivity",
        "",
        f"prefit_gate_status={payload['support_gate_results']['prefit_gate_status']}",
        "",
        "## 17. Donor-support sensitivity",
        "",
        f"donor_gate_status={payload['support_gate_results']['donor_gate_status']}",
        "",
        "## 18. Worst-world behavior",
        "",
        f"Worst positive-world level coverage: **{m.get('worst_positive_coverage')}**",
        "",
        "## 19. Support gates",
        "",
        f"`{json.dumps(payload['support_gate_results'])}`",
        "",
        "## 20. Semantic restrictions",
        "",
        "Treated-unit effect only; level-scale; support-gated; no population ATE.",
        "",
        "## 21. Reassessed status",
        "",
        f"`{payload['dcm_001_reassessed_status']}`",
        "",
        "## 22. Promotion-candidate status",
        "",
        f"eligible_for_promotion={payload['promotion_candidate_summary']['dcm_001_eligible_for_promotion']}",
        "",
        "## 23. Unchanged DCM rows",
        "",
        f"{len(payload['unchanged_combination_results'])} combinations unchanged (no new evidence).",
        "",
        "## 24. TrustReport authorization status",
        "",
        "`trust_report_authorized=false`, `trust_report_authorized_count=0`.",
        "",
        "## 25. Remaining limitations",
        "",
        "\n".join(f"- {x}" for x in payload["limitations"]),
        "",
        "## 26. Required next validation",
        "",
        "D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001; D5-TRUST-STRATIFIED-SCM-JK-001; full promotion decision.",
        "",
        "## 27. Governance verdict",
        "",
        f"`{payload['verdict']}`",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    summary = write_summary()
    report = write_report()
    payload = json.loads(summary.read_text())
    print(f"Wrote {summary} and {report} — verdict={payload['verdict']}")


if __name__ == "__main__":
    main()
