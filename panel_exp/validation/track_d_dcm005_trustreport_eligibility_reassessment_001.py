"""DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001 — Track D harness."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from panel_exp.governance.investigation_lifecycle_contract import (
    format_handoff_report_section,
    load_registry,
)
from panel_exp.validation.dcm005_trustreport_eligibility_reassessment_001 import (
    GATE_LABEL,
    INV_BRB,
    INV_KFOLD,
    INV_PLACEBO,
    REASSESSMENT_VERSION,
    REMEDIATION_ARTIFACT_BRB,
    load_dcm005_evidence,
    reassess_dcm005_trustreport_eligibility,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARCHIVE_DIR = _REPO_ROOT / "docs/track_d/archives"
_SUMMARY_PATH = _ARCHIVE_DIR / "DCM005_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json"
_REPORT_PATH = _REPO_ROOT / "docs/track_d/DCM005_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md"
_PRIOR_SUMMARY = _ARCHIVE_DIR / "TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json"
_BRB_SUMMARY = _ARCHIVE_DIR / "D5_TRUST_TBRRIDGE_BRB_001_summary.json"
_BRB_CORRECTION = _ARCHIVE_DIR / "TBRRIDGE_BRB_INTERVAL_CORRECTION_001_summary.json"
_KFOLD_SUMMARY = _ARCHIVE_DIR / "D5_TRUST_TBRRIDGE_KFOLD_001_summary.json"
_PLACEBO_SUMMARY = _ARCHIVE_DIR / "D5_TRUST_TBRRIDGE_PLACEBO_001_summary.json"

ReassessmentVerdict = Literal[
    "dcm005_mixed_path_specific_restrictions_no_authorization",
    "dcm005_all_paths_ineligible_no_authorization",
    "dcm005_diagnostic_paths_only_no_authorization",
    "dcm005_insufficient_evidence_no_authorization",
    "dcm005_reassessment_inconclusive",
    "dcm005_reassessment_failed",
]

_REQUIRED_SUMMARIES = (
    _BRB_SUMMARY,
    _BRB_CORRECTION,
    _KFOLD_SUMMARY,
    _PLACEBO_SUMMARY,
    _PRIOR_SUMMARY,
)


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
    if not path.is_file():
        raise FileNotFoundError(f"Required evidence missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _prior_dcm005_paths(prior_summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in prior_summary.get("combination_results") or []:
        key = row.get("combination_key")
        if key and str(key).startswith("DCM-005"):
            rows[str(key)] = row
    if not rows:
        raise KeyError("DCM-005 paths not found in prior eligibility summary")
    return rows


def _unchanged_combinations(prior_summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in prior_summary.get("combination_results") or []:
        key = str(row.get("combination_key", ""))
        if key.startswith("DCM-005"):
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


def _decide_verdict(aggregate_status: str) -> ReassessmentVerdict:
    if aggregate_status == "MIXED_WITH_TERMINAL_PATH_DECISIONS":
        return "dcm005_mixed_path_specific_restrictions_no_authorization"
    if aggregate_status == "INELIGIBLE_FOR_CAUSAL_INTERVAL":
        return "dcm005_all_paths_ineligible_no_authorization"
    if aggregate_status == "DIAGNOSTIC_ONLY":
        return "dcm005_diagnostic_paths_only_no_authorization"
    if aggregate_status == "INSUFFICIENT_EVIDENCE":
        return "dcm005_insufficient_evidence_no_authorization"
    return "dcm005_reassessment_inconclusive"


def build_dcm005_trustreport_eligibility_reassessment_001() -> dict[str, Any]:
    for path in _REQUIRED_SUMMARIES:
        if not path.is_file():
            raise FileNotFoundError(path)

    prior_summary = _load_json(_PRIOR_SUMMARY)
    prior_paths = _prior_dcm005_paths(prior_summary)
    registry = load_registry()
    inv_by_id = {i["investigation_id"]: i for i in registry.get("investigations", [])}

    evidence = load_dcm005_evidence(
        brb_summary=_load_json(_BRB_SUMMARY),
        brb_correction_summary=_load_json(_BRB_CORRECTION),
        kfold_summary=_load_json(_KFOLD_SUMMARY),
        placebo_summary=_load_json(_PLACEBO_SUMMARY),
    )

    reassessed = reassess_dcm005_trustreport_eligibility(
        prior_eligibility_result=prior_paths.get("DCM-005-BRB"),
        path_evidence=evidence,
        registry_investigations=inv_by_id,
    )

    path_rows = [p.to_dict() for p in reassessed.path_decisions]
    consumption = {
        INV_BRB: {
            "prior_status": inv_by_id[INV_BRB].get("status"),
            "reassessed_status": "DEFERRED_WITH_TRIGGER",
            "terminal_disposition": "REMEDIATE",
            "target_artifact": REMEDIATION_ARTIFACT_BRB,
        },
        INV_KFOLD: {
            "prior_status": inv_by_id[INV_KFOLD].get("status"),
            "reassessed_status": "RESOLVED",
            "terminal_disposition": "DIAGNOSTIC_ONLY",
            "resolution_artifact": "DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
        },
        INV_PLACEBO: {
            "prior_status": inv_by_id[INV_PLACEBO].get("status"),
            "reassessed_status": "RESOLVED",
            "terminal_disposition": "NULL_MONITOR_ONLY",
            "resolution_artifact": "DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
        },
    }

    payload: dict[str, Any] = {
        "artifact_id": "DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
        "artifact_version": REASSESSMENT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "reassessment_scope": ["DCM-005-BRB", "DCM-005-KFOLD", "DCM-005-PLACEBO"],
        "prior_dcm005_status": {
            "DCM-005-BRB": prior_paths.get("DCM-005-BRB", {}).get("eligibility_status"),
            "DCM-005-KFOLD": prior_paths.get("DCM-005-KFOLD", {}).get("eligibility_status"),
            "DCM-005-PLACEBO": prior_paths.get("DCM-005-PLACEBO", {}).get("eligibility_status"),
        },
        "evidence_sources": list(reassessed.evidence_sources),
        "path_decisions": path_rows,
        "aggregate_dcm005_status": reassessed.aggregate_status,
        "dcm005_reassessment": reassessed.to_dict(),
        "promotion_candidate_summary": {
            "count": 0,
            "promotion_candidate_count": 0,
            "promotion_candidates": [],
            "dcm005_eligible_for_promotion": False,
        },
        "investigation_consumption": consumption,
        "investigation_handoff": reassessed.investigation_handoff,
        "unchanged_combination_results": _unchanged_combinations(prior_summary),
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_authorized_count": 0,
            "trust_report_ready": False,
            "label": GATE_LABEL,
        },
        "limitations": [
            "Reassessment applies to DCM-005 TBRRidge paths only; other DCM rows unchanged.",
            "Uses committed D5-TRUST characterization summaries; no new statistical runs.",
            "BRB causal-interval path deferred for variance remediation.",
            "KFold diagnostic-only; Placebo null-monitor-only.",
            "Does not authorize TrustReport or downstream roles.",
            "Does not complete FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT.",
        ],
        "verdict": _decide_verdict(reassessed.aggregate_status),
    }
    return payload


def write_summary(path: Path | None = None) -> Path:
    payload = build_dcm005_trustreport_eligibility_reassessment_001()
    if path is None:
        path = _SUMMARY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_report(path: Path | None = None) -> Path:
    payload = build_dcm005_trustreport_eligibility_reassessment_001()
    if path is None:
        path = _REPORT_PATH

    paths = {p["path_id"]: p for p in payload["path_decisions"]}
    brb = paths["DCM-005-BRB"]
    kf = paths["DCM-005-KFOLD"]
    pl = paths["DCM-005-PLACEBO"]
    handoff = payload["investigation_handoff"]

    lines = [
        "# DCM-005 TrustReport Eligibility Reassessment — Report",
        "",
        "**Artifact ID:** DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
        f"**Verdict:** `{payload['verdict']}`",
        f"**Aggregate status:** `{payload['aggregate_dcm005_status']}`",
        "",
        "> This reassessment issues path-specific decisions for DCM-005.",
        "> It does not authorize TrustReport.",
        "> It does not promote any TBRRidge inference path.",
        "> It does not reinterpret diagnostic intervals as causal uncertainty.",
        "",
        "## 1. Executive summary",
        "",
        "DCM-005 TBRRidge BRB, KFold, and Placebo paths reassessed from committed trust "
        "characterization evidence. BRB centering corrected but variance calibration failed; "
        "deferred for remediation. KFold diagnostic-only. Placebo null-monitor-only. "
        "**No TrustReport authorization.**",
        "",
        "## 2. Why DCM-005 reassessment was required",
        "",
        "Prior harness marked INSUFFICIENT_EVIDENCE / INELIGIBLE without path-specific trust evidence.",
        "",
        "## 3. Prior DCM-005 status",
        "",
        str(payload["prior_dcm005_status"]),
        "",
        "## 4. Evidence chain",
        "",
        "D5-TRUST-TBRRIDGE-BRB-001 → TBRRIDGE-BRB-INTERVAL-CORRECTION-001 → "
        "D5-TRUST-TBRRIDGE-KFOLD-001 → D5-TRUST-TBRRIDGE-PLACEBO-001 → this reassessment.",
        "",
        "## 5. Scope",
        "",
        "DCM-005 BRB, KFold, Placebo paths only.",
        "",
        "## 6. Non-goals",
        "",
        "No production changes; no full-matrix reassessment; no TrustReport promotion.",
        "",
        "## 7. DCM-005 identity",
        "",
        "TBRRidge estimator with BRB, KFold, or Placebo inference on unit-panel single-cell geometry.",
        "",
        "## 8. Path-specific decision framework",
        "",
        "Each path receives independent statistical, semantic, and eligibility decisions.",
        "",
        "## 9. BRB evidence summary",
        "",
        "Centering gap ~−292.6 → ~0.006; null coverage ~40.5%; type-I ~59.5%; variance ratio ~11.",
        "",
        "## 10. BRB statistical decision",
        "",
        f"`{brb['statistical_status']}` — variance calibration unacceptable for causal interval.",
        "",
        "## 11. BRB semantic decision",
        "",
        f"`{brb['semantic_class']}` — causal interval blocked.",
        "",
        "## 12. BRB investigation disposition",
        "",
        f"`{brb['investigation_disposition']}` — {INV_BRB} → DEFERRED_WITH_TRIGGER → "
        f"{REMEDIATION_ARTIFACT_BRB}.",
        "",
        "## 13. KFold evidence summary",
        "",
        "CV stability band; sign accuracy ~1.7% positive; no temporal leakage; not causal ATT interval.",
        "",
        "## 14. KFold statistical decision",
        "",
        f"`{kf['statistical_status']}`",
        "",
        "## 15. KFold semantic decision",
        "",
        f"`{kf['semantic_class']}` — dispersion band is diagnostic only.",
        "",
        "## 16. KFold investigation disposition",
        "",
        f"`{kf['investigation_disposition']}` — {INV_KFOLD} RESOLVED.",
        "",
        "## 17. Placebo evidence summary",
        "",
        "Single-treated only; ≥5 controls; null type-I 0%; null-reference / falsification semantics.",
        "",
        "## 18. Placebo statistical decision",
        "",
        f"`{pl['statistical_status']}` for governed null-monitor role.",
        "",
        "## 19. Placebo semantic decision",
        "",
        f"`{pl['semantic_class']}` — not causal ATT uncertainty.",
        "",
        "## 20. Placebo investigation disposition",
        "",
        f"`{pl['investigation_disposition']}` — {INV_PLACEBO} RESOLVED.",
        "",
        "## 21. Aggregate DCM-005 status",
        "",
        f"`{payload['aggregate_dcm005_status']}`",
        "",
        "## 22. Supported roles by path",
        "",
        f"BRB: {brb['supported_roles']}; KFold: {kf['supported_roles']}; Placebo: {pl['supported_roles']}",
        "",
        "## 23. Blocked roles by path",
        "",
        f"BRB: {brb['blocked_roles']}; KFold: {kf['blocked_roles']}; Placebo: {pl['blocked_roles']}",
        "",
        "## 24. Promotion-candidate status",
        "",
        "`eligible_for_promotion: false` for all paths.",
        "",
        "## 25. TrustReport authorization",
        "",
        "**Blocked** — `trust_report_authorized_count: 0`.",
        "",
        "## 26. Other DCM rows unchanged",
        "",
        "DCM-001–004, 006–008 preserved with `unchanged_due_to_no_new_evidence`.",
        "",
        "## 27. Remaining limitations",
        "",
        "BRB variance remediation pending; FULL reassessment not performed.",
        "",
        "## 28. Governance updates",
        "",
        "OPEN_INVESTIGATIONS_001 consumed for KFold and Placebo; BRB deferred with remediation trigger.",
        "",
        "## 29. Final verdict",
        "",
        f"**`{payload['verdict']}`**",
        "",
    ]

    resolved = [INV_KFOLD, INV_PLACEBO]
    updated = [
        f"{INV_BRB} → DEFERRED_WITH_TRIGGER; REMEDIATE → {REMEDIATION_ARTIFACT_BRB}",
        f"{INV_KFOLD} → RESOLVED; DIAGNOSTIC_ONLY",
        f"{INV_PLACEBO} → RESOLVED; NULL_MONITOR_ONLY",
    ]
    lines.extend(
        format_handoff_report_section(
            resolved_in_artifact=resolved,
            new_investigations=[],
            updated_investigations=updated,
            deferred_issues=[INV_BRB],
            explicit_exclusions=["FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT"],
            revisit_trigger="After BRB variance remediation or remediation closeout decision",
            decision_checkpoint="FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT",
            next_artifact=handoff.get("next_artifact"),
        )
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    summary = write_summary()
    report = write_report()
    payload = build_dcm005_trustreport_eligibility_reassessment_001()
    print(f"Wrote {summary} and {report} — {payload['verdict']}")


if __name__ == "__main__":
    main()
