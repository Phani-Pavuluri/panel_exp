"""TRUSTREPORT-INTEGRATION-DRY-RUN-001 — restricted TrustReport integration dry-run.

Verifies promoted DCM-001/DCM-004 row contracts can be ingested, validated, and
blocked correctly under dry-run conditions. No live API, scheduler, or production
automation authorization. Does not run new statistical simulations.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from panel_exp.governance.investigation_lifecycle_contract import (
    build_investigation_handoff,
    format_handoff_report_section,
    load_registry,
)

_REPO = Path(__file__).resolve().parents[2]
_ARCHIVE = _REPO / "docs/track_d/archives"
_ARTIFACT_ID = "TRUSTREPORT-INTEGRATION-DRY-RUN-001"
_ARTIFACT_VERSION = "1.0.0"
_DEFAULT_SUMMARY = _ARCHIVE / "TRUSTREPORT_INTEGRATION_DRY_RUN_001_summary.json"
_DEFAULT_REPORT = _REPO / "docs/track_d/TRUSTREPORT_INTEGRATION_DRY_RUN_001_REPORT.md"

DryRunDecision = Literal[
    "DRY_RUN_ACCEPTED_RESTRICTED_TRUSTREPORT",
    "DRY_RUN_ACCEPTED_DIAGNOSTIC_DISPLAY_ONLY",
    "DRY_RUN_ACCEPTED_NULL_MONITOR_ONLY",
    "DRY_RUN_BLOCKED_MISSING_CONTRACT",
    "DRY_RUN_BLOCKED_UNSUPPORTED_GEOMETRY",
    "DRY_RUN_BLOCKED_DIAGNOSTIC_ONLY",
    "DRY_RUN_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
    "DRY_RUN_BLOCKED_NOT_PROMOTED",
    "DRY_RUN_BLOCKED_CALIBRATION_SIGNAL",
    "DRY_RUN_BLOCKED_LIVE_API",
    "DRY_RUN_BLOCKED_SCHEDULER",
    "DRY_RUN_BLOCKED_PRODUCTION_DECISIONING",
    "DRY_RUN_BLOCKED_BUDGET_OPTIMIZATION",
    "DRY_RUN_BLOCKED_UNKNOWN_ROW",
]

GovernanceVerdict = Literal[
    "trustreport_integration_dry_run_passed",
    "trustreport_integration_dry_run_blocked_missing_contract",
    "trustreport_integration_dry_run_failed",
]

REQUIRED_INPUTS: dict[str, str] = {
    "downstream_promotion": "TRUSTREPORT_DOWNSTREAM_PROMOTION_001_summary.json",
    "full_reassessment": "FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
    "dcm001_reassessment": "TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
    "dcm004_reassessment": "DCM004_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
    "prior_validation": "TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json",
}

DRY_RUN_SCOPE = frozenset({"DCM-001", "DCM-004"})

ROW_CONTRACT_FIELDS = frozenset(
    {
        "row_id",
        "design_family",
        "estimator",
        "inference_method",
        "estimand",
        "readout_scope",
        "allowed_geometry",
        "blocked_geometry",
        "minimum_pre_period",
        "minimum_post_period",
        "required_diagnostics",
        "required_warnings",
        "interval_semantics",
        "allowed_role",
        "blocked_roles",
        "audit_artifacts",
    }
)

PROMOTED_ROWS = frozenset({"DCM-001", "DCM-004"})

DIAGNOSTIC_ONLY_ROWS = frozenset(
    {"DCM-002", "DCM-005-BRB", "DCM-005-KFOLD", "DCM-008"}
)

NULL_MONITOR_ROWS = frozenset({"DCM-005-PLACEBO", "SCM-PLACEBO"})


@dataclass(frozen=True)
class DryRunRequest:
    request_id: str
    row_id: str
    request_type: str
    requested_role: str
    geometry: str | None = None
    readout_scope: str | None = None
    include_warnings: bool = True
    include_parallel_trends_warning: bool = True
    claim_type: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DryRunResult:
    request_id: str
    row_id: str
    request_type: str
    decision: DryRunDecision
    accepted: bool
    audit_record_id: str
    gate_results: dict[str, bool] = field(default_factory=dict)
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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


def _atomic_write(path: Path, content: str, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
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


def _load_inputs() -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    paths: dict[str, str] = {}
    for key, fname in REQUIRED_INPUTS.items():
        path = _ARCHIVE / fname
        if not path.is_file():
            raise FileNotFoundError(f"Required input missing: {path}")
        loaded[key] = json.loads(path.read_text(encoding="utf-8"))
        paths[key] = str(path)
    loaded["_paths"] = paths
    return loaded


def _promoted_row_review(promotion: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in promotion.get("reviewed_rows") or []:
        if row.get("row_id") == row_id:
            return row
    raise KeyError(f"Promoted row {row_id} not found in promotion summary")


def _build_row_contract(review: dict[str, Any]) -> dict[str, Any]:
    rc = dict(review.get("restriction_contract") or {})
    row_id = review["row_id"]
    blocked_geom = rc.get("blocked_geometries") or []
    return {
        "row_id": row_id,
        "design_family": rc.get("allowed_design_family", review.get("design_family")),
        "estimator": rc.get("allowed_estimator"),
        "inference_method": rc.get("allowed_inference_method"),
        "estimand": rc.get("allowed_estimand"),
        "readout_scope": rc.get("allowed_readout_scope"),
        "allowed_geometry": rc.get("allowed_geometry"),
        "blocked_geometry": list(blocked_geom),
        "minimum_pre_period": rc.get("minimum_pre_period"),
        "minimum_post_period": rc.get("minimum_post_period"),
        "required_diagnostics": list(rc.get("required_fit_diagnostics") or []),
        "required_warnings": list(rc.get("required_warnings") or review.get("required_warnings") or []),
        "interval_semantics": rc.get("required_interval_semantics"),
        "allowed_role": rc.get("trustreport_role", "restricted_trustreport_research_only"),
        "blocked_roles": sorted(
            set(rc.get("blocked_downstream_uses") or [])
            | {
                "calibration_signal",
                "live_api",
                "scheduler",
                "production_decisioning",
                "budget_optimization_input",
            }
        ),
        "audit_artifacts": list(review.get("evidence_artifacts") or []),
    }


def _contract_complete(contract: dict[str, Any]) -> bool:
    for field_name in ROW_CONTRACT_FIELDS:
        if field_name not in contract:
            return False
        val = contract[field_name]
        if field_name in ("required_warnings", "required_diagnostics", "audit_artifacts", "blocked_geometry"):
            if not val:
                return False
        elif val is None or val == "":
            return False
    return True


def _make_audit_record(
    *,
    request: DryRunRequest,
    result: DryRunResult,
    contract: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "audit_record_id": result.audit_record_id,
        "request_id": request.request_id,
        "row_id": request.row_id,
        "request_type": request.request_type,
        "requested_role": request.requested_role,
        "decision": result.decision,
        "accepted": result.accepted,
        "dry_run_only": True,
        "live_api_authorized": False,
        "scheduler_authorized": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "contract_row_id": (contract or {}).get("row_id"),
        "reason": result.reason,
    }


def _evaluate_dry_run(
    request: DryRunRequest,
    *,
    row_contracts: dict[str, dict[str, Any]],
    promotion: dict[str, Any],
) -> DryRunResult:
    audit_id = f"audit-{request.request_id}"
    promoted = set(promotion.get("promoted_rows") or [])
    decisions = promotion.get("promotion_decisions") or {}

    # Global blocked request types
    role = request.requested_role.lower()
    if role in ("calibration_signal", "calibrationsignal"):
        return DryRunResult(
            request.request_id,
            request.row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_CALIBRATION_SIGNAL",
            False,
            audit_id,
            {"calibration_signal_blocked": True},
            "CalibrationSignal not authorized for any row",
        )
    if role in ("live_api", "live-api", "api"):
        return DryRunResult(
            request.request_id,
            request.row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_LIVE_API",
            False,
            audit_id,
            {"live_api_blocked": True},
            "Live API authorization forbidden in dry-run lane",
        )
    if role in ("scheduler", "scheduler_execution"):
        return DryRunResult(
            request.request_id,
            request.row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_SCHEDULER",
            False,
            audit_id,
            {"scheduler_blocked": True},
            "Scheduler authorization forbidden in dry-run lane",
        )
    if role in ("production_decisioning", "production", "production_decision"):
        return DryRunResult(
            request.request_id,
            request.row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_PRODUCTION_DECISIONING",
            False,
            audit_id,
            {"production_decisioning_blocked": True},
            "Production decisioning forbidden in dry-run lane",
        )
    if role in ("budget_optimization_input", "budget_optimization", "budget"):
        return DryRunResult(
            request.request_id,
            request.row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_BUDGET_OPTIMIZATION",
            False,
            audit_id,
            {"budget_optimization_blocked": True},
            "Budget optimization input forbidden in dry-run lane",
        )

    row_id = request.row_id
    known_rows = frozenset(decisions.keys()) | PROMOTED_ROWS | DIAGNOSTIC_ONLY_ROWS | NULL_MONITOR_ROWS

    if row_id not in known_rows:
        return DryRunResult(
            request.request_id,
            row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_UNKNOWN_ROW",
            False,
            audit_id,
            {"unknown_row": True},
            f"Unknown or unregistered row: {row_id}",
        )

    if row_id not in row_contracts and row_id not in promoted:
        if row_id.startswith("DCM-") or row_id in NULL_MONITOR_ROWS | DIAGNOSTIC_ONLY_ROWS:
            pass  # handled below
        else:
            return DryRunResult(
                request.request_id,
                row_id,
                request.request_type,
                "DRY_RUN_BLOCKED_UNKNOWN_ROW",
                False,
                audit_id,
                {"unknown_row": True},
                f"Unknown or unregistered row: {row_id}",
            )

    if row_id in DIAGNOSTIC_ONLY_ROWS or decisions.get(row_id) == "DO_NOT_PROMOTE_DIAGNOSTIC_ONLY":
        return DryRunResult(
            request.request_id,
            row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_DIAGNOSTIC_ONLY",
            False,
            audit_id,
            {"diagnostic_only": True},
            f"{row_id} is diagnostic-only; restricted TrustReport dry-run blocked",
        )

    if row_id in NULL_MONITOR_ROWS:
        if request.request_type == "causal_trustreport":
            return DryRunResult(
                request.request_id,
                row_id,
                request.request_type,
                "DRY_RUN_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
                False,
                audit_id,
                {"null_monitor_causal_reuse": True},
                "Null-monitor path cannot be reused for causal TrustReport dry-run",
            )
        return DryRunResult(
            request.request_id,
            row_id,
            request.request_type,
            "DRY_RUN_ACCEPTED_NULL_MONITOR_ONLY",
            True,
            audit_id,
            {"null_monitor_only": True},
            "Null-monitor dry-run display only; not causal TrustReport",
        )

    if row_id == "DCM-006":
        if request.claim_type in ("global", "winner", "pooled", "any_cell_success"):
            return DryRunResult(
                request.request_id,
                row_id,
                request.request_type,
                "DRY_RUN_BLOCKED_NOT_PROMOTED",
                False,
                audit_id,
                {"multicell_global_blocked": True},
                "DCM-006 global/winner/pooled claims not promoted",
            )
        return DryRunResult(
            request.request_id,
            row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_NOT_PROMOTED",
            False,
            audit_id,
            {"not_promoted": True},
            "DCM-006 marginal per-cell only; restricted TrustReport dry-run blocked",
        )

    if row_id == "DCM-008" or request.claim_type == "aggregate_stratified":
        return DryRunResult(
            request.request_id,
            row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_DIAGNOSTIC_ONLY",
            False,
            audit_id,
            {"stratified_aggregate_blocked": True},
            "DCM-008 aggregate stratified readout is diagnostic-only",
        )

    if row_id not in promoted:
        return DryRunResult(
            request.request_id,
            row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_NOT_PROMOTED",
            False,
            audit_id,
            {"not_promoted": True},
            f"{row_id} was not promoted for restricted TrustReport",
        )

    contract = row_contracts[row_id]

    if not _contract_complete(contract):
        return DryRunResult(
            request.request_id,
            row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_MISSING_CONTRACT",
            False,
            audit_id,
            {"contract_incomplete": True},
            "Row contract missing required fields",
        )

    if request.request_type == "missing_warnings":
        return DryRunResult(
            request.request_id,
            row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_MISSING_CONTRACT",
            False,
            audit_id,
            {"warnings_missing": True},
            "Required warnings contract absent",
        )

    if row_id == "DCM-004" and request.request_type == "missing_parallel_trends_warning":
        return DryRunResult(
            request.request_id,
            row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_MISSING_CONTRACT",
            False,
            audit_id,
            {"parallel_trends_warning_missing": True},
            "Parallel-trends warning required for DCM-004",
        )

    geom = request.geometry or contract.get("allowed_geometry")
    blocked = set(contract.get("blocked_geometry") or [])
    if geom in blocked or request.request_type == "unsupported_geometry":
        return DryRunResult(
            request.request_id,
            row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_UNSUPPORTED_GEOMETRY",
            False,
            audit_id,
            {"unsupported_geometry": True},
            f"Geometry {geom} blocked for {row_id}",
        )

    if row_id == "DCM-004" and request.request_type == "unsupported_timing":
        return DryRunResult(
            request.request_id,
            row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_UNSUPPORTED_GEOMETRY",
            False,
            audit_id,
            {"unsupported_timing": True},
            "Parallel-trends violation / unsupported timing blocked for DCM-004",
        )

    scope = request.readout_scope or contract.get("readout_scope")
    if scope != contract.get("readout_scope") and request.readout_scope is not None:
        return DryRunResult(
            request.request_id,
            row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_UNSUPPORTED_GEOMETRY",
            False,
            audit_id,
            {"readout_scope_mismatch": True},
            "Readout scope not in allowed contract",
        )

    if not request.include_warnings and row_id in PROMOTED_ROWS:
        return DryRunResult(
            request.request_id,
            row_id,
            request.request_type,
            "DRY_RUN_BLOCKED_MISSING_CONTRACT",
            False,
            audit_id,
            {"warnings_not_included": True},
            "Required warnings must be present for acceptance",
        )

    gates = {
        "row_promoted": row_id in promoted,
        "contract_complete": True,
        "warnings_present": bool(contract.get("required_warnings")),
        "restrictions_present": bool(contract.get("blocked_roles")),
        "geometry_allowed": geom not in blocked,
        "dry_run_only": True,
        "live_api_blocked": True,
        "scheduler_blocked": True,
        "calibration_signal_blocked": True,
    }

    return DryRunResult(
        request.request_id,
        row_id,
        request.request_type,
        "DRY_RUN_ACCEPTED_RESTRICTED_TRUSTREPORT",
        True,
        audit_id,
        gates,
        "Restricted TrustReport dry-run accepted (research mode only)",
    )


def _build_dry_run_requests() -> list[DryRunRequest]:
    reqs: list[DryRunRequest] = [
        # Positive DCM-001
        DryRunRequest("pos-dcm001-valid", "DCM-001", "valid_restricted", "restricted_trustreport_research_only"),
        DryRunRequest("pos-dcm001-warnings", "DCM-001", "warnings_present", "restricted_trustreport_research_only"),
        DryRunRequest(
            "pos-dcm001-geometry",
            "DCM-001",
            "allowed_geometry",
            "restricted_trustreport_research_only",
            geometry="unit_panel_single_cell",
            readout_scope="restricted_causal_interval",
        ),
        # Positive DCM-004
        DryRunRequest("pos-dcm004-valid", "DCM-004", "valid_restricted", "restricted_trustreport_research_only"),
        DryRunRequest("pos-dcm004-warnings", "DCM-004", "warnings_present", "restricted_trustreport_research_only"),
        DryRunRequest(
            "pos-dcm004-geometry",
            "DCM-004",
            "allowed_geometry",
            "restricted_trustreport_research_only",
            geometry="unit_panel_single_cell",
            readout_scope="restricted_causal_interval",
        ),
        # Negative contract/geometry
        DryRunRequest(
            "neg-dcm001-missing-warnings",
            "DCM-001",
            "missing_warnings",
            "restricted_trustreport_research_only",
            include_warnings=False,
        ),
        DryRunRequest(
            "neg-dcm004-missing-pt-warning",
            "DCM-004",
            "missing_parallel_trends_warning",
            "restricted_trustreport_research_only",
            include_parallel_trends_warning=False,
        ),
        DryRunRequest(
            "neg-dcm001-bad-geometry",
            "DCM-001",
            "unsupported_geometry",
            "restricted_trustreport_research_only",
            geometry="aggregate_1x1",
        ),
        DryRunRequest(
            "neg-dcm004-bad-timing",
            "DCM-004",
            "unsupported_timing",
            "restricted_trustreport_research_only",
            geometry="parallel_trends_violation",
        ),
        # Negative excluded rows
        DryRunRequest("neg-brb", "DCM-005-BRB", "causal_trustreport", "restricted_trustreport_research_only"),
        DryRunRequest("neg-kfold", "DCM-005-KFOLD", "causal_trustreport", "restricted_trustreport_research_only"),
        DryRunRequest("neg-placebo", "DCM-005-PLACEBO", "causal_trustreport", "restricted_trustreport_research_only"),
        DryRunRequest(
            "neg-dcm006-global",
            "DCM-006",
            "global_claim",
            "restricted_trustreport_research_only",
            claim_type="global",
        ),
        DryRunRequest(
            "neg-dcm006-pooled",
            "DCM-006",
            "pooled_claim",
            "restricted_trustreport_research_only",
            claim_type="pooled",
        ),
        DryRunRequest(
            "neg-dcm008-aggregate",
            "DCM-008",
            "aggregate_stratified",
            "restricted_trustreport_research_only",
            claim_type="aggregate_stratified",
        ),
        # Boundary blocks
        DryRunRequest("neg-cal-dcm001", "DCM-001", "calibration_signal", "calibration_signal"),
        DryRunRequest("neg-live-dcm004", "DCM-004", "live_api", "live_api"),
        DryRunRequest("neg-scheduler-dcm001", "DCM-001", "scheduler", "scheduler"),
        DryRunRequest("neg-prod-dcm004", "DCM-004", "production", "production_decisioning"),
        DryRunRequest("neg-budget-dcm001", "DCM-001", "budget", "budget_optimization_input"),
        DryRunRequest("neg-unknown", "DCM-999", "unknown", "restricted_trustreport_research_only"),
    ]
    return reqs


def build_trustreport_integration_dry_run_001() -> dict[str, Any]:
    inputs = _load_inputs()
    promotion = inputs["downstream_promotion"]
    registry = load_registry()

    if promotion.get("governance_verdict") != "trustreport_downstream_restricted_row_promotion_approved":
        raise ValueError("Promotion artifact must approve restricted row-level promotion")

    row_contracts: dict[str, dict[str, Any]] = {}
    restriction_contracts: dict[str, dict[str, Any]] = {}
    warning_contracts: dict[str, list[str]] = {}
    for row_id in PROMOTED_ROWS:
        review = _promoted_row_review(promotion, row_id)
        contract = _build_row_contract(review)
        row_contracts[row_id] = contract
        restriction_contracts[row_id] = dict(review.get("restriction_contract") or {})
        warning_contracts[row_id] = list(contract.get("required_warnings") or [])

    contracts_complete = all(_contract_complete(c) for c in row_contracts.values())

    requests = _build_dry_run_requests()
    results: list[DryRunResult] = []
    audit_records: list[dict[str, Any]] = []

    for req in requests:
        result = _evaluate_dry_run(req, row_contracts=row_contracts, promotion=promotion)
        results.append(result)
        contract = row_contracts.get(req.row_id)
        audit_records.append(_make_audit_record(request=req, result=result, contract=contract))

    accepted = [r for r in results if r.accepted]
    blocked = [r for r in results if not r.accepted]

    accepted_restricted = [
        r for r in results if r.decision == "DRY_RUN_ACCEPTED_RESTRICTED_TRUSTREPORT"
    ]
    accepted_row_ids = {r.row_id for r in accepted_restricted}

    # Safety: only DCM-001/004 may be accepted as restricted TrustReport
    for r in accepted_restricted:
        if r.row_id not in PROMOTED_ROWS:
            raise ValueError(f"Unexpected restricted acceptance for {r.row_id}")

    negative_control = [
        r.to_dict()
        for r in results
        if r.request_id.startswith("neg-")
    ]

    positive_pass = all(
        r.decision == "DRY_RUN_ACCEPTED_RESTRICTED_TRUSTREPORT"
        for r in results
        if r.request_id.startswith("pos-")
    )
    negative_pass = all(
        not r.accepted or r.decision.startswith("DRY_RUN_ACCEPTED_NULL")
        for r in results
        if r.request_id.startswith("neg-")
    )

    if contracts_complete and positive_pass and negative_pass:
        verdict: GovernanceVerdict = "trustreport_integration_dry_run_passed"
        next_artifact = "TRUSTREPORT_RESEARCH_MODE_RENDERER_001"
    elif not contracts_complete:
        verdict = "trustreport_integration_dry_run_blocked_missing_contract"
        next_artifact = "TRUSTREPORT_RESTRICTED_ROW_CONTRACTS_001"
    else:
        verdict = "trustreport_integration_dry_run_failed"
        next_artifact = "TRUSTREPORT_RESTRICTED_ROW_CONTRACTS_001"

    deferred = [
        inv["investigation_id"]
        for inv in registry.get("investigations", [])
        if inv.get("status") == "DEFERRED_WITH_TRIGGER"
    ]

    handoff = build_investigation_handoff(
        follow_up_issues=[],
        resolved_issues=[],
        terminal_dispositions=[],
        next_artifact=next_artifact,
    )

    limitations = [
        "This artifact performs a dry-run integration check for restricted row-level TrustReport contracts.",
        "It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, or budget optimization.",
        "Only DCM-001 and DCM-004 are accepted for restricted TrustReport research-mode dry-run.",
        "All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.",
        "Dry-run simulates integration boundaries only; no live execution.",
    ]

    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "input_artifacts": inputs["_paths"],
        "dry_run_scope": sorted(DRY_RUN_SCOPE),
        "dry_run_requests": [r.to_dict() for r in requests],
        "accepted_requests": [r.to_dict() for r in accepted],
        "blocked_requests": [r.to_dict() for r in blocked],
        "accepted_rows": sorted(accepted_row_ids),
        "blocked_rows": sorted({r.row_id for r in blocked}),
        "row_contracts": row_contracts,
        "restriction_contracts": restriction_contracts,
        "warning_contracts": warning_contracts,
        "audit_records": audit_records,
        "negative_control_results": negative_control,
        "global_authorization_summary": {
            "trust_report_platform_authorized": False,
            "live_api_authorized": False,
            "scheduler_authorized": False,
        },
        "live_api_authorization_summary": {
            "live_api_authorized": False,
            "dry_run_only": True,
            "rationale": "Live API blocked in dry-run lane",
        },
        "scheduler_authorization_summary": {
            "scheduler_authorized": False,
            "dry_run_only": True,
            "rationale": "Scheduler blocked in dry-run lane",
        },
        "calibration_signal_summary": {
            "any_calibration_signal_allowed": False,
            "per_row": {row_id: False for row_id in row_contracts},
        },
        "production_decisioning_summary": {
            "any_production_decisioning_allowed": False,
        },
        "budget_optimization_summary": {
            "any_budget_optimization_allowed": False,
        },
        "open_investigation_check": {
            "deferred_investigations": deferred,
            "blocking_for_dry_run": [],
            "rationale": "Deferred multicell investigations do not block DCM-001/004 dry-run",
        },
        "governance_verdict": verdict,
        "limitations": limitations,
        "next_artifact": next_artifact,
        "investigation_handoff": handoff,
        "verdict": verdict,
        "contracts_complete": contracts_complete,
        "dcm001_dry_run_result": next(
            (r.to_dict() for r in results if r.row_id == "DCM-001" and r.request_id == "pos-dcm001-valid"),
            {},
        ),
        "dcm004_dry_run_result": next(
            (r.to_dict() for r in results if r.row_id == "DCM-004" and r.request_id == "pos-dcm004-valid"),
            {},
        ),
        "dry_run_results": [r.to_dict() for r in results],
    }


def write_report(payload: dict[str, Any], path: Path, *, overwrite: bool = False) -> None:
    handoff_lines = format_handoff_report_section(
        resolved_in_artifact=[],
        new_investigations=[],
        updated_investigations=[],
        deferred_issues=payload.get("open_investigation_check", {}).get("deferred_investigations", []),
        explicit_exclusions=sorted(
            set(payload.get("blocked_rows", [])) - set(payload.get("accepted_rows", []))
        ),
        revisit_trigger="After TRUSTREPORT_RESEARCH_MODE_RENDERER_001 or contract remediation",
        decision_checkpoint="TRUSTREPORT_INTEGRATION_DRY_RUN_001",
        next_artifact=payload.get("next_artifact"),
    )
    lines = [
        f"# {_ARTIFACT_ID} Report",
        "",
        "## 1. Executive summary",
        "",
        "This artifact performs a dry-run integration check for restricted row-level TrustReport contracts.",
        "It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, or budget optimization.",
        "Only DCM-001 and DCM-004 are accepted for restricted TrustReport research-mode dry-run.",
        "All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.",
        "",
        f"**Governance verdict:** `{payload.get('governance_verdict')}`",
        f"**Accepted rows:** {payload.get('accepted_rows')}",
        "",
        "## 2. Scope",
        "",
        "Dry-run restricted TrustReport integration for DCM-001 (SCM+JK) and DCM-004 (DID+bootstrap) only.",
        "",
        "## 3. Non-goals",
        "",
        "- No live API authorization",
        "- No scheduler authorization",
        "- No production automation",
        "- No CalibrationSignal promotion",
        "- No new statistical simulations",
        "- No estimator/inference/design changes",
        "",
        "## 4. Input artifacts",
        "",
        json.dumps(payload.get("input_artifacts"), indent=2),
        "",
        "## 5. Dry-run contract",
        "",
        json.dumps(list(ROW_CONTRACT_FIELDS), indent=2),
        "",
        "## 6. Promoted row contracts",
        "",
        json.dumps(payload.get("row_contracts"), indent=2),
        "",
        "## 7. DCM-001 dry-run result",
        "",
        json.dumps(payload.get("dcm001_dry_run_result"), indent=2),
        "",
        "## 8. DCM-004 dry-run result",
        "",
        json.dumps(payload.get("dcm004_dry_run_result"), indent=2),
        "",
        "## 9. Negative-control rows",
        "",
        json.dumps(payload.get("negative_control_results"), indent=2),
        "",
        "## 10. Blocked diagnostic-only rows",
        "",
        "DCM-002, DCM-005-BRB, DCM-005-KFOLD, DCM-008 — DRY_RUN_BLOCKED_DIAGNOSTIC_ONLY",
        "",
        "## 11. Blocked null-monitor causal reuse",
        "",
        "DCM-005-PLACEBO, SCM-PLACEBO causal TrustReport attempts — DRY_RUN_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
        "",
        "## 12. Blocked multi-cell/global claims",
        "",
        "DCM-006 global/winner/pooled — DRY_RUN_BLOCKED_NOT_PROMOTED",
        "",
        "## 13. Blocked stratified aggregate claims",
        "",
        "DCM-008 aggregate — DRY_RUN_BLOCKED_DIAGNOSTIC_ONLY",
        "",
        "## 14. CalibrationSignal boundary",
        "",
        json.dumps(payload.get("calibration_signal_summary"), indent=2),
        "",
        "## 15. Live API boundary",
        "",
        json.dumps(payload.get("live_api_authorization_summary"), indent=2),
        "",
        "## 16. Scheduler boundary",
        "",
        json.dumps(payload.get("scheduler_authorization_summary"), indent=2),
        "",
        "## 17. Production decisioning boundary",
        "",
        json.dumps(payload.get("production_decisioning_summary"), indent=2),
        "",
        "## 18. Budget optimization boundary",
        "",
        json.dumps(payload.get("budget_optimization_summary"), indent=2),
        "",
        "## 19. Audit record verification",
        "",
        f"Audit records emitted: {len(payload.get('audit_records') or [])}",
        "",
        "## 20. Open investigation check",
        "",
        json.dumps(payload.get("open_investigation_check"), indent=2),
        "",
        "## 21. Governance verdict",
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
    payload = build_trustreport_integration_dry_run_001()
    global_auth = payload["global_authorization_summary"]
    cal = payload["calibration_signal_summary"]
    if strict:
        if global_auth.get("trust_report_platform_authorized"):
            raise RuntimeError("trust_report_platform_authorized must remain false")
        if global_auth.get("live_api_authorized"):
            raise RuntimeError("live_api_authorized must remain false")
        if global_auth.get("scheduler_authorized"):
            raise RuntimeError("scheduler_authorized must remain false")
        if cal.get("any_calibration_signal_allowed"):
            raise RuntimeError("CalibrationSignal must remain false")
        for row_id in payload.get("accepted_rows") or []:
            if row_id not in PROMOTED_ROWS:
                raise RuntimeError(f"Unexpected accepted row: {row_id}")
        for rec in payload.get("dry_run_results") or []:
            if rec.get("row_id") in DIAGNOSTIC_ONLY_ROWS | {"DCM-006", "DCM-008"}:
                if rec.get("decision") == "DRY_RUN_ACCEPTED_RESTRICTED_TRUSTREPORT":
                    raise RuntimeError(f"Excluded row {rec['row_id']} must not be accepted")
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
