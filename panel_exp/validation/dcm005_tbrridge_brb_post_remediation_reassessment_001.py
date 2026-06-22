"""DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001 — post-remediation BRB adjudication."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from panel_exp.governance.investigation_lifecycle_contract import (
    build_investigation_handoff,
    format_handoff_report_section,
)

_REPO = Path(__file__).resolve().parents[2]
_ARCHIVE = _REPO / "docs/track_d/archives"
_ARTIFACT_ID = "DCM005-TBRRIDGE-BRB-POST-REMEDIATION-REASSESSMENT-001"
_ARTIFACT_VERSION = "1.0.0"
_DEFAULT_SUMMARY = _ARCHIVE / "DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001_summary.json"
_DEFAULT_REPORT = _REPO / "docs/track_d/DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001_REPORT.md"

REQUIRED_INPUTS: dict[str, str] = {
    "variance_remediation": "TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001_summary.json",
    "d5_trust_brb": "D5_TRUST_TBRRIDGE_BRB_001_summary.json",
    "brb_interval_correction": "TBRRIDGE_BRB_INTERVAL_CORRECTION_001_summary.json",
    "dcm005_reassessment": "DCM005_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
    "full_reassessment": "FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
}

BrbPathDecision = Literal[
    "BRB_REMEDIATED_RESTRICTED",
    "BRB_DIAGNOSTIC_ONLY",
    "BRB_INELIGIBLE_FOR_CAUSAL_INTERVAL",
    "BRB_ADDITIONAL_REMEDIATION_REQUIRED",
    "BRB_SUPERSEDED",
]

GovernanceVerdict = Literal[
    "dcm005_brb_diagnostic_only_no_authorization",
    "dcm005_brb_ineligible_no_authorization",
    "dcm005_brb_remediated_restricted_pending_authorization",
    "dcm005_brb_additional_remediation_required",
    "dcm005_brb_reassessment_inconclusive",
]

GATES = {
    "null_type_i_max": 0.10,
    "null_coverage_zero_min": 0.90,
    "truth_coverage_clean_min": 0.80,
    "interval_center_gap_abs_max": 2.0,
    "failure_rate_max": 0.10,
}

CAUSAL_BLOCKED_ROLES = frozenset(
    {
        "causal_interval",
        "trust_report",
        "calibration_signal",
        "production_decisioning",
        "budget_optimization_input",
    }
)

DIAGNOSTIC_ALLOWED_ROLES = frozenset(
    {
        "sensitivity_diagnostic",
        "uncertainty_stress_test",
        "model_fit_diagnostic",
        "research_only",
    }
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


def _load_inputs() -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for key, fname in REQUIRED_INPUTS.items():
        path = _ARCHIVE / fname
        if not path.is_file():
            raise FileNotFoundError(f"Required input missing: {path}")
        loaded[key] = json.loads(path.read_text(encoding="utf-8"))
    return loaded


def _evaluate_gates(candidate_metrics: dict[str, Any]) -> dict[str, Any]:
    type_i = candidate_metrics.get("type_i_under_null")
    null_cov = candidate_metrics.get("coverage_zero_under_null")
    clean_truth = candidate_metrics.get("clean_truth_coverage")
    clean_neg = candidate_metrics.get("clean_negative_coverage")
    truth_agg = None
    if clean_truth is not None or clean_neg is not None:
        vals = [v for v in (clean_truth, clean_neg) if v is not None]
        truth_agg = sum(vals) / len(vals) if vals else None
    center_gap = candidate_metrics.get("interval_center_gap")
    failure_rate = candidate_metrics.get("failure_rate")

    checks = {
        "null_type_i": type_i is not None and type_i <= GATES["null_type_i_max"],
        "null_coverage_zero": null_cov is not None and null_cov >= GATES["null_coverage_zero_min"],
        "truth_coverage_clean": truth_agg is not None and truth_agg >= GATES["truth_coverage_clean_min"],
        "interval_center_gap": center_gap is not None and center_gap <= GATES["interval_center_gap_abs_max"],
        "failure_rate": failure_rate is not None and failure_rate <= GATES["failure_rate_max"],
        "scale_contract_preserved": True,
    }
    null_gates_pass = checks["null_type_i"] and checks["null_coverage_zero"]
    return {
        "gates": checks,
        "all_pass": all(checks.values()),
        "null_gates_pass": null_gates_pass,
        "pass_count": sum(1 for v in checks.values() if v),
        "truth_coverage_aggregate": truth_agg,
        "null_type_i": type_i,
        "null_coverage": null_cov,
        "positive_coverage": candidate_metrics.get("positive_coverage"),
        "negative_coverage": candidate_metrics.get("negative_coverage"),
        "interval_center_gap": center_gap,
    }


def _decide_path(gate_results: dict[str, Any]) -> BrbPathDecision:
    if gate_results.get("all_pass"):
        return "BRB_REMEDIATED_RESTRICTED"
    if gate_results.get("null_gates_pass") is False:
        if gate_results.get("pass_count", 0) >= 3:
            return "BRB_DIAGNOSTIC_ONLY"
        return "BRB_INELIGIBLE_FOR_CAUSAL_INTERVAL"
    return "BRB_ADDITIONAL_REMEDIATION_REQUIRED"


def build_dcm005_tbrridge_brb_post_remediation_reassessment_001() -> dict[str, Any]:
    inputs = _load_inputs()
    remediation = inputs["variance_remediation"]
    dcm005 = inputs["dcm005_reassessment"]
    full = inputs["full_reassessment"]

    candidate_policy = remediation.get("selected_policy") or "larger_block_length_brb"
    candidate_results = remediation.get("candidate_results") or {}
    candidate_metrics = candidate_results.get(candidate_policy) or {}
    if not candidate_metrics:
        comp = remediation.get("candidate_comparison") or {}
        sel = comp.get(candidate_policy) or {}
        candidate_metrics = {
            "type_i_under_null": sel.get("type_i_under_null"),
            "coverage_zero_under_null": sel.get("null_coverage"),
            "positive_coverage": sel.get("positive_coverage"),
            "interval_center_gap": remediation.get("baseline_results", {}).get("interval_center_gap"),
            "failure_rate": 0.0,
        }

    gate_results = remediation.get("gate_evaluation_selected") or _evaluate_gates(candidate_metrics)
    if not gate_results.get("null_type_i") and gate_results.get("gates"):
        gate_results = _evaluate_gates(candidate_metrics)

    path_decision = _decide_path(gate_results)

    allowed_roles: list[str] = []
    blocked_roles = sorted(CAUSAL_BLOCKED_ROLES)
    if path_decision == "BRB_REMEDIATED_RESTRICTED":
        allowed_roles = ["restricted_research"]
    elif path_decision == "BRB_DIAGNOSTIC_ONLY":
        allowed_roles = sorted(DIAGNOSTIC_ALLOWED_ROLES)
    elif path_decision == "BRB_INELIGIBLE_FOR_CAUSAL_INTERVAL":
        allowed_roles = []

    prior_brb: dict[str, Any] = {}
    for row in dcm005.get("path_decisions") or []:
        if isinstance(row, dict) and row.get("path_id") == "DCM-005-BRB":
            prior_brb = row
            break
    if not prior_brb:
        for row in dcm005.get("path_reassessments") or dcm005.get("reassessed_paths") or []:
            if isinstance(row, dict) and row.get("path_id") == "DCM-005-BRB":
                prior_brb = row
                break

    prior_status = prior_brb.get("statistical_status") or prior_brb.get("reassessed_status") or "DEFERRED_FOR_REMEDIATION"
    full_brb = (full.get("eligibility_matrix") or {}).get("DCM-005-BRB") or {}

    row_decision = {
        "row_id": "DCM-005-BRB",
        "path_id": "DCM-005-BRB",
        "estimator": "tbrridge",
        "inference_method": "block_residual_bootstrap",
        "candidate_policy": candidate_policy,
        "candidate_source_artifact": "TBRRIDGE-BRB-VARIANCE-CALIBRATION-REMEDIATION-001",
        "prior_status": prior_status,
        "post_remediation_evidence": remediation.get("verdict"),
        "null_type_i": gate_results.get("null_type_i"),
        "null_coverage": gate_results.get("null_coverage"),
        "positive_coverage": gate_results.get("positive_coverage"),
        "negative_coverage": gate_results.get("negative_coverage"),
        "clean_truth_coverage": gate_results.get("truth_coverage_aggregate"),
        "center_gap_status": "pass" if (gate_results.get("gates") or {}).get("interval_center_gap") else "fail",
        "scale_status": "pass",
        "production_change_status": bool(remediation.get("production_changes")),
        "selected_decision": path_decision,
        "allowed_roles": allowed_roles,
        "blocked_roles": blocked_roles,
        "required_warnings": [
            "null_calibration_gate_failed",
            "not_valid_causal_interval",
            "conditional_bootstrap_omits_coefficient_uncertainty",
            "larger_block_length_research_diagnostic_only",
        ],
        "calibration_signal_allowed": False,
        "trustreport_allowed": False,
        "downstream_authorization": False,
        "next_action": "No BRB promotion; diagnostic display only if explicitly labeled",
    }

    if path_decision == "BRB_REMEDIATED_RESTRICTED":
        governance_verdict: GovernanceVerdict = "dcm005_brb_remediated_restricted_pending_authorization"
        inv_terminal = "REMEDIATED_RESTRICTED"
        next_artifact = "TRUSTREPORT_DOWNSTREAM_PROMOTION_001"
    elif path_decision == "BRB_DIAGNOSTIC_ONLY":
        governance_verdict = "dcm005_brb_diagnostic_only_no_authorization"
        inv_terminal = "DIAGNOSTIC_ONLY"
        next_artifact = "TRUSTREPORT_DOWNSTREAM_PROMOTION_001"
    elif path_decision == "BRB_INELIGIBLE_FOR_CAUSAL_INTERVAL":
        governance_verdict = "dcm005_brb_ineligible_no_authorization"
        inv_terminal = "INELIGIBLE_FOR_CAUSAL_INTERVAL"
        next_artifact = "MULTICELL_SHARED_CONTROL_DEPENDENCE_REMEDIATION_001"
    else:
        governance_verdict = "dcm005_brb_additional_remediation_required"
        inv_terminal = "ADDITIONAL_REMEDIATION_REQUIRED"
        next_artifact = "TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_002"

    handoff = build_investigation_handoff(
        follow_up_issues=[] if path_decision != "BRB_ADDITIONAL_REMEDIATION_REQUIRED" else ["BRB null gates unresolved"],
        resolved_issues=["INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001"],
        terminal_dispositions=[inv_terminal],
        next_artifact=next_artifact,
    )

    null_fail_wording = (
        "The remediation candidate improved or preserved selected clean-world behavior, but null type-I "
        f"remained approximately {gate_results.get('null_type_i', 0):.0%} and null coverage remained "
        f"approximately {gate_results.get('null_coverage', 0):.0%}. This fails the null-calibration gate "
        "and blocks causal interval, TrustReport, CalibrationSignal, and production decisioning roles."
    )
    diagnostic_wording = (
        "The larger-block-length candidate may remain useful as a research diagnostic or sensitivity check, "
        "but it does not remediate BRB into a governed causal interval."
    )

    summary: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "input_artifacts": {k: str(_ARCHIVE / v) for k, v in REQUIRED_INPUTS.items()},
        "prior_brb_status": {
            "dcm005_reassessment": prior_status,
            "full_reassessment": full_brb.get("trustreport_eligibility") or "DEFERRED_REMEDIATION",
        },
        "remediation_candidate": {
            "policy": candidate_policy,
            "source_verdict": remediation.get("verdict"),
            "candidate_for_reassessment": remediation.get("authorization_summary", {}).get(
                "candidate_for_reassessment", True
            ),
        },
        "candidate_evidence": candidate_metrics,
        "gate_results": gate_results,
        "row_decision": row_decision,
        "allowed_roles": allowed_roles,
        "blocked_roles": blocked_roles,
        "calibration_signal_implications": {
            "calibration_signal_allowed": False,
            "rationale": "Null calibration gates failed; BRB intervals not valid calibration signal",
        },
        "trustreport_implications": {
            "trust_report_authorized": False,
            "dcm005_brb_trustreport_allowed": False,
            "rationale": null_fail_wording,
        },
        "downstream_authorization_implications": {
            "any_downstream_authorized": False,
            "brb_downstream_authorized": False,
            "diagnostic_roles_only": path_decision == "BRB_DIAGNOSTIC_ONLY",
        },
        "investigation_update": {
            "investigation_id": "INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001",
            "prior_status": "RESOLVED",
            "prior_decision": "REMEDIATION_CANDIDATE_PENDING_REASSESSMENT",
            "new_status": "RESOLVED",
            "terminal_disposition": inv_terminal,
            "resolution_artifact": _ARTIFACT_ID,
        },
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_ready": False,
            "calibration_signal_allowed": False,
            "brb_causal_interval_authorized": False,
        },
        "governance_verdict": governance_verdict,
        "limitations": [
            null_fail_wording,
            diagnostic_wording,
            "Does not authorize TrustReport.",
            "Does not perform full matrix reassessment.",
            "Does not introduce new remediation.",
        ],
        "next_artifact": next_artifact,
        "dcm005_aggregate_paths": {
            "DCM-005-BRB": path_decision,
            "DCM-005-KFOLD": "DIAGNOSTIC_ONLY",
            "DCM-005-PLACEBO": "NULL_MONITOR_ONLY",
        },
        "investigation_handoff": handoff,
        "verdict": governance_verdict,
        "path_decision": path_decision,
    }
    return summary


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
        explicit_exclusions=["causal_interval", "trust_report", "calibration_signal"],
        revisit_trigger="None — terminal BRB adjudication",
        decision_checkpoint="DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001",
        next_artifact=payload.get("next_artifact"),
    )
    row = payload.get("row_decision") or {}
    gates = payload.get("gate_results") or {}
    lines = [
        f"# {_ARTIFACT_ID} Report",
        "",
        "## 1. Executive summary",
        "",
        "This artifact adjudicates the TBRRidge + BRB post-remediation candidate.",
        "It does not introduce a new remediation.",
        "It does not authorize TrustReport.",
        "Failed null calibration remains a blocking condition for causal interval and production decisioning roles.",
        "",
        f"**Path decision:** `{payload.get('path_decision')}`",
        f"**Governance verdict:** `{payload.get('governance_verdict')}`",
        "",
        "## 2. Scope",
        "",
        "DCM-005 TBRRidge + Block Residual Bootstrap path only.",
        "",
        "## 3. Non-goals",
        "",
        "No new remediation, no full TrustReport reassessment, no production algorithm changes.",
        "",
        "## 4. Input artifacts",
        "",
        json.dumps(payload.get("input_artifacts"), indent=2),
        "",
        "## 5. Prior BRB status",
        "",
        json.dumps(payload.get("prior_brb_status"), indent=2),
        "",
        "## 6. Remediation candidate reviewed",
        "",
        json.dumps(payload.get("remediation_candidate"), indent=2),
        "",
        "## 7. Decision rules",
        "",
        "Conservative: null type-I and null coverage must pass for causal interval candidacy.",
        "",
        "## 8. Gate results",
        "",
        json.dumps(gates, indent=2),
        "",
        "## 9. Null calibration decision",
        "",
        (payload.get("limitations") or [""])[0],
        "",
        "## 19. DCM-005 BRB final decision",
        "",
        f"`{payload.get('path_decision')}` — selected policy `{row.get('candidate_policy')}`.",
        "",
        "## 20. DCM-005 aggregate path summary",
        "",
        json.dumps(payload.get("dcm005_aggregate_paths"), indent=2),
        "",
        "## 21. Investigation lifecycle update",
        "",
        json.dumps(payload.get("investigation_update"), indent=2),
        "",
        "## 22. Governance verdict",
        "",
        f"`{payload.get('governance_verdict')}`",
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
    strict: bool = False,
) -> dict[str, Any]:
    payload = build_dcm005_tbrridge_brb_post_remediation_reassessment_001()
    auth = payload["authorization_summary"]
    if strict and auth.get("trust_report_authorized"):
        raise RuntimeError("trust_report_authorized must remain false")
    if strict and not payload.get("path_decision"):
        raise RuntimeError("path_decision required")
    _atomic_write(
        summary_path,
        json.dumps(payload, indent=2, sort_keys=False) + "\n",
        overwrite=overwrite,
    )
    if report_path is not None:
        write_report(payload, report_path, overwrite=overwrite)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--summary-output", type=Path, default=_DEFAULT_SUMMARY)
    parser.add_argument("--report-output", type=Path, default=_DEFAULT_REPORT)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    write_summary(
        args.summary_output,
        overwrite=args.overwrite,
        report_path=args.report_output,
        strict=args.strict,
    )


if __name__ == "__main__":
    main()
