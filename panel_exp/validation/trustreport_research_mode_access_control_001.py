"""TRUSTREPORT-RESEARCH-MODE-ACCESS-CONTROL-001 — governed research-mode access control.

Defines who can view, export, review, and approve research-mode TrustReport artifacts.
DCM-001 and DCM-004 only. Access approval is research-mode only — not deployment authorization.
"""

from __future__ import annotations

import argparse
import copy
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
from panel_exp.validation.trustreport_research_mode_artifact_export_001 import (
    PROMOTED_ROWS,
    _content_hash,
    _payload_is_sanitized,
)
from panel_exp.validation.trustreport_research_mode_review_workflow_001 import (
    _verify_content_hash as _verify_export_hash,
    _verify_manifest,
)

_REPO = Path(__file__).resolve().parents[2]
_ARCHIVE = _REPO / "docs/track_d/archives"
_EXAMPLES = _REPO / "docs/track_d/examples"
_ARTIFACT_ID = "TRUSTREPORT-RESEARCH-MODE-ACCESS-CONTROL-001"
_ARTIFACT_VERSION = "1.0.0"
_DEFAULT_SUMMARY = _ARCHIVE / "TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001_summary.json"
_DEFAULT_REPORT = _REPO / "docs/track_d/TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001_REPORT.md"
_DEFAULT_ACCESS_OUTPUT = Path("/tmp/TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001_decisions.json")
_MANIFEST_PATH = _EXAMPLES / "TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_manifest.json"

AccessDecision = Literal[
    "ACCESS_GRANTED_RESEARCH_VIEW",
    "ACCESS_GRANTED_RESEARCH_EXPORT",
    "ACCESS_GRANTED_RESEARCH_REVIEW",
    "ACCESS_GRANTED_RESEARCH_REVIEW_APPROVE",
    "ACCESS_GRANTED_MANIFEST_VIEW",
    "ACCESS_GRANTED_AUDIT_VIEW",
    "ACCESS_BLOCKED_ROLE_NOT_PERMITTED",
    "ACCESS_BLOCKED_INVALID_ROLE",
    "ACCESS_BLOCKED_UNKNOWN_ROW",
    "ACCESS_BLOCKED_NOT_PROMOTED",
    "ACCESS_BLOCKED_DIAGNOSTIC_ONLY",
    "ACCESS_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
    "ACCESS_BLOCKED_UNSANITIZED_ARTIFACT",
    "ACCESS_BLOCKED_HASH_MISMATCH",
    "ACCESS_BLOCKED_MANIFEST_MISMATCH",
    "ACCESS_BLOCKED_UNREVIEWED_ARTIFACT",
    "ACCESS_BLOCKED_CALIBRATION_SIGNAL",
    "ACCESS_BLOCKED_LIVE_API",
    "ACCESS_BLOCKED_SCHEDULER",
    "ACCESS_BLOCKED_PRODUCTION_DECISIONING",
    "ACCESS_BLOCKED_BUDGET_OPTIMIZATION",
    "ACCESS_BLOCKED_GLOBAL_PLATFORM",
]

GovernanceVerdict = Literal[
    "trustreport_research_mode_access_control_passed",
    "trustreport_research_mode_access_control_blocked_missing_contract",
    "trustreport_research_mode_access_control_failed",
]

REQUIRED_INPUTS: dict[str, str] = {
    "review_workflow": "TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001_summary.json",
    "artifact_export": "TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_summary.json",
    "renderer_summary": "TRUSTREPORT_RESEARCH_MODE_RENDERER_001_summary.json",
    "integration_dry_run": "TRUSTREPORT_INTEGRATION_DRY_RUN_001_summary.json",
    "downstream_promotion": "TRUSTREPORT_DOWNSTREAM_PROMOTION_001_summary.json",
}

ACCESS_SCOPE = frozenset({"DCM-001", "DCM-004"})

ACCESS_CONTRACT_FIELDS = frozenset(
    {
        "access_request_id",
        "artifact_id",
        "row_id",
        "requested_access_mode",
        "requester_role",
        "requester_scope",
        "artifact_scope",
        "research_mode_only",
        "manifest_verified",
        "content_hash_verified",
        "sanitization_verified",
        "review_status",
        "allowed_permissions",
        "blocked_permissions",
        "decision",
        "decision_reason",
        "audit_record",
        "created_at",
    }
)

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "research_viewer": frozenset({"RESEARCH_VIEW", "MANIFEST_VIEW"}),
    "research_exporter": frozenset({"RESEARCH_VIEW", "RESEARCH_EXPORT", "MANIFEST_VIEW"}),
    "research_reviewer": frozenset(
        {"RESEARCH_VIEW", "RESEARCH_REVIEW", "MANIFEST_VIEW", "AUDIT_VIEW"}
    ),
    "causal_methods_reviewer": frozenset(
        {
            "RESEARCH_VIEW",
            "RESEARCH_REVIEW",
            "RESEARCH_REVIEW_APPROVE",
            "MANIFEST_VIEW",
            "AUDIT_VIEW",
        }
    ),
    "governance_reviewer": frozenset(
        {
            "RESEARCH_VIEW",
            "RESEARCH_REVIEW",
            "RESEARCH_REVIEW_APPROVE",
            "MANIFEST_VIEW",
            "AUDIT_VIEW",
        }
    ),
    "audit_viewer": frozenset({"MANIFEST_VIEW", "AUDIT_VIEW"}),
    "research_mode_admin": frozenset(
        {
            "RESEARCH_VIEW",
            "RESEARCH_EXPORT",
            "RESEARCH_REVIEW",
            "RESEARCH_REVIEW_APPROVE",
            "MANIFEST_VIEW",
            "AUDIT_VIEW",
        }
    ),
}

INVALID_ROLES = frozenset(
    {
        "production_approver",
        "scheduler_operator",
        "api_operator",
        "budget_optimizer",
        "calibration_signal_writer",
        "global_platform_admin",
        "unknown",
    }
)

BLOCKED_ACCESS_MODES: dict[str, AccessDecision] = {
    "PRODUCTION_VIEW": "ACCESS_BLOCKED_PRODUCTION_DECISIONING",
    "PRODUCTION_EXPORT": "ACCESS_BLOCKED_PRODUCTION_DECISIONING",
    "LIVE_API_EXECUTE": "ACCESS_BLOCKED_LIVE_API",
    "SCHEDULER_EXECUTE": "ACCESS_BLOCKED_SCHEDULER",
    "CALIBRATION_SIGNAL_WRITE": "ACCESS_BLOCKED_CALIBRATION_SIGNAL",
    "BUDGET_OPTIMIZATION_EXECUTE": "ACCESS_BLOCKED_BUDGET_OPTIMIZATION",
    "PRODUCTION_DECISION_APPROVE": "ACCESS_BLOCKED_PRODUCTION_DECISIONING",
    "GLOBAL_PLATFORM_ADMIN": "ACCESS_BLOCKED_GLOBAL_PLATFORM",
}

GRANTED_DECISION_BY_MODE: dict[str, AccessDecision] = {
    "RESEARCH_VIEW": "ACCESS_GRANTED_RESEARCH_VIEW",
    "RESEARCH_EXPORT": "ACCESS_GRANTED_RESEARCH_EXPORT",
    "RESEARCH_REVIEW": "ACCESS_GRANTED_RESEARCH_REVIEW",
    "RESEARCH_REVIEW_APPROVE": "ACCESS_GRANTED_RESEARCH_REVIEW_APPROVE",
    "MANIFEST_VIEW": "ACCESS_GRANTED_MANIFEST_VIEW",
    "AUDIT_VIEW": "ACCESS_GRANTED_AUDIT_VIEW",
}

ALL_RESEARCH_MODES = frozenset(GRANTED_DECISION_BY_MODE.keys())
ALL_BLOCKED_MODES = frozenset(BLOCKED_ACCESS_MODES.keys())

DIAGNOSTIC_ONLY_ROWS = frozenset(
    {"DCM-002", "DCM-005-BRB", "DCM-005-KFOLD", "DCM-008"}
)
NULL_MONITOR_ROWS = frozenset({"DCM-005-PLACEBO", "SCM-PLACEBO"})

ROW_EXPORT_ARTIFACT = {
    "DCM-001": "pos-dcm001-placeholder",
    "DCM-004": "pos-dcm004-placeholder",
}


@dataclass(frozen=True)
class AccessRequest:
    request_id: str
    row_id: str
    export_request_id: str
    request_type: str
    requester_role: str
    requested_access_mode: str
    claim_type: str | None = None
    defect: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AccessResult:
    request_id: str
    row_id: str
    export_id: str
    request_type: str
    decision: AccessDecision
    granted: bool
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
    if not _MANIFEST_PATH.is_file():
        raise FileNotFoundError(f"Required manifest missing: {_MANIFEST_PATH}")
    loaded["export_manifest"] = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
    paths["export_manifest"] = str(_MANIFEST_PATH)
    loaded["_paths"] = paths
    return loaded


def _approved_review_exports(review_summary: dict[str, Any]) -> frozenset[str]:
    approved = set()
    for rec in review_summary.get("accepted_reviews") or []:
        req_id = rec.get("request_id")
        if req_id:
            approved.add(req_id)
    return frozenset(approved)


def _apply_artifact_defect(export_contract: dict[str, Any], defect: str | None) -> dict[str, Any]:
    if not defect:
        return export_contract
    contract = copy.deepcopy(export_contract)
    if defect == "unsanitized":
        contract["sanitized_payload"] = {
            "label": "UNSANITIZED",
            "live_data": True,
            "raw_customer_id": "cust-123",
        }
    elif defect == "hash_mismatch":
        contract["content_hash"] = "0" * 64
        if contract.get("export_manifest"):
            contract["export_manifest"]["content_hash"] = "0" * 64
    elif defect == "manifest_mismatch":
        if contract.get("export_manifest"):
            contract["export_manifest"]["export_id"] = "export-mismatch"
    return contract


def _authorization_boundaries() -> dict[str, bool]:
    return {
        "research_mode_only": True,
        "live_api_authorized": False,
        "scheduler_authorized": False,
        "calibration_signal_allowed": False,
        "production_decisioning_allowed": False,
        "budget_optimization_allowed": False,
        "trust_report_platform_authorized": False,
    }


def _build_access_contract(
    *,
    request: AccessRequest,
    export_contract: dict[str, Any],
    decision: AccessDecision,
    granted: bool,
    role_perms: frozenset[str],
    review_status: str,
    manifest_ok: bool,
    hash_ok: bool,
    sanitization_ok: bool,
    audit_record_id: str,
) -> dict[str, Any]:
    blocked_perms = sorted(ALL_BLOCKED_MODES | (ALL_RESEARCH_MODES - role_perms))
    return {
        "access_request_id": request.request_id,
        "artifact_id": _ARTIFACT_ID,
        "row_id": request.row_id,
        "requested_access_mode": request.requested_access_mode,
        "requester_role": request.requester_role,
        "requester_scope": "research_mode_only",
        "artifact_scope": export_contract.get("readout_scope"),
        "research_mode_only": True,
        "manifest_verified": manifest_ok,
        "content_hash_verified": hash_ok,
        "sanitization_verified": sanitization_ok,
        "review_status": review_status,
        "allowed_permissions": sorted(role_perms),
        "blocked_permissions": blocked_perms,
        "decision": decision,
        "decision_reason": "Research-mode access granted" if granted else "Access blocked",
        "audit_record": {
            "audit_record_id": audit_record_id,
            "export_id": export_contract.get("export_id"),
            "row_id": request.row_id,
            "research_mode_only": True,
            **_authorization_boundaries(),
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def _evaluate_access(
    request: AccessRequest,
    *,
    export_contracts: dict[str, dict[str, Any]],
    manifest_doc: dict[str, Any],
    promotion: dict[str, Any],
    dry_run: dict[str, Any],
    approved_reviews: frozenset[str],
) -> tuple[AccessResult, dict[str, Any] | None]:
    audit_id = f"access-audit-{request.request_id}"
    promoted = set(promotion.get("promoted_rows") or [])
    dry_accepted = set(dry_run.get("accepted_rows") or [])
    mode = request.requested_access_mode

    if mode in BLOCKED_ACCESS_MODES:
        return (
            AccessResult(
                request.request_id,
                request.row_id,
                "",
                request.request_type,
                BLOCKED_ACCESS_MODES[mode],
                False,
                audit_id,
                {f"{mode}_blocked": True},
                f"Blocked access mode: {mode}",
            ),
            None,
        )

    if request.requester_role in INVALID_ROLES or request.request_type == "invalid_role":
        return (
            AccessResult(
                request.request_id,
                request.row_id,
                "",
                request.request_type,
                "ACCESS_BLOCKED_INVALID_ROLE",
                False,
                audit_id,
                {"invalid_role": True},
                f"Invalid role: {request.requester_role}",
            ),
            None,
        )

    row_id = request.row_id
    known_rows = (
        PROMOTED_ROWS
        | DIAGNOSTIC_ONLY_ROWS
        | NULL_MONITOR_ROWS
        | frozenset((promotion.get("promotion_decisions") or {}).keys())
        | {"DCM-006"}
    )

    if row_id not in known_rows:
        return (
            AccessResult(
                request.request_id,
                row_id,
                "",
                request.request_type,
                "ACCESS_BLOCKED_UNKNOWN_ROW",
                False,
                audit_id,
                {"unknown_row": True},
                f"Unknown row: {row_id}",
            ),
            None,
        )

    if row_id in DIAGNOSTIC_ONLY_ROWS:
        return (
            AccessResult(
                request.request_id,
                row_id,
                "",
                request.request_type,
                "ACCESS_BLOCKED_DIAGNOSTIC_ONLY",
                False,
                audit_id,
                {"diagnostic_only": True},
                f"{row_id} is diagnostic-only",
            ),
            None,
        )

    if row_id in NULL_MONITOR_ROWS and request.request_type == "causal_trustreport":
        return (
            AccessResult(
                request.request_id,
                row_id,
                "",
                request.request_type,
                "ACCESS_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
                False,
                audit_id,
                {"null_monitor_causal_reuse": True},
                "Null-monitor causal TrustReport access blocked",
            ),
            None,
        )

    if row_id == "DCM-006":
        return (
            AccessResult(
                request.request_id,
                row_id,
                "",
                request.request_type,
                "ACCESS_BLOCKED_NOT_PROMOTED",
                False,
                audit_id,
                {"multicell_global_blocked": True},
                "DCM-006 global/winner/pooled access blocked",
            ),
            None,
        )

    if row_id == "DCM-008" or request.claim_type == "aggregate_stratified":
        return (
            AccessResult(
                request.request_id,
                row_id,
                "",
                request.request_type,
                "ACCESS_BLOCKED_DIAGNOSTIC_ONLY",
                False,
                audit_id,
                {"stratified_aggregate_blocked": True},
                "DCM-008 aggregate access blocked",
            ),
            None,
        )

    if row_id not in promoted or row_id not in dry_accepted:
        return (
            AccessResult(
                request.request_id,
                row_id,
                "",
                request.request_type,
                "ACCESS_BLOCKED_NOT_PROMOTED",
                False,
                audit_id,
                {"not_promoted": True},
                f"{row_id} not promoted",
            ),
            None,
        )

    export_id = f"export-{request.export_request_id}"
    base_contract = export_contracts.get(export_id)
    if not base_contract:
        return (
            AccessResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "ACCESS_BLOCKED_NOT_PROMOTED",
                False,
                audit_id,
                {"export_missing": True},
                f"Export missing: {export_id}",
            ),
            None,
        )

    contract = _apply_artifact_defect(base_contract, request.defect)

    if request.defect == "hash_mismatch":
        hash_ok = False
    else:
        hash_ok, _ = _verify_export_hash(base_contract)

    if request.defect == "manifest_mismatch":
        manifest_ok = False
    else:
        manifest_ok = _verify_manifest(request.export_request_id, base_contract, manifest_doc)

    sanitization_ok = _payload_is_sanitized(contract.get("sanitized_payload") or {})

    if request.defect == "unsanitized" or not sanitization_ok:
        return (
            AccessResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "ACCESS_BLOCKED_UNSANITIZED_ARTIFACT",
                False,
                audit_id,
                {"unsanitized_artifact": True},
                "Unsanitized artifact access blocked",
            ),
            None,
        )

    if request.defect == "hash_mismatch" or not hash_ok:
        return (
            AccessResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "ACCESS_BLOCKED_HASH_MISMATCH",
                False,
                audit_id,
                {"hash_mismatch": True},
                "Content hash mismatch",
            ),
            None,
        )

    if request.defect == "manifest_mismatch" or not manifest_ok:
        return (
            AccessResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "ACCESS_BLOCKED_MANIFEST_MISMATCH",
                False,
                audit_id,
                {"manifest_mismatch": True},
                "Manifest mismatch",
            ),
            None,
        )

    role_perms = ROLE_PERMISSIONS.get(request.requester_role, frozenset())
    if mode not in role_perms:
        return (
            AccessResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "ACCESS_BLOCKED_ROLE_NOT_PERMITTED",
                False,
                audit_id,
                {"role_not_permitted": True},
                f"Role {request.requester_role} cannot {mode}",
            ),
            None,
        )

    reviewed = request.export_request_id in approved_reviews
    review_status = "RESEARCH_REVIEW_APPROVED" if reviewed else "REVIEW_PENDING"

    if mode == "RESEARCH_REVIEW_APPROVE" and (
        request.defect == "unreviewed" or not reviewed
    ):
        return (
            AccessResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "ACCESS_BLOCKED_UNREVIEWED_ARTIFACT",
                False,
                audit_id,
                {"unreviewed_artifact": True},
                "Artifact not research-review approved",
            ),
            None,
        )

    decision = GRANTED_DECISION_BY_MODE[mode]
    access_contract = _build_access_contract(
        request=request,
        export_contract=base_contract,
        decision=decision,
        granted=True,
        role_perms=role_perms,
        review_status=review_status,
        manifest_ok=manifest_ok,
        hash_ok=hash_ok,
        sanitization_ok=sanitization_ok,
        audit_record_id=audit_id,
    )

    gates = {
        "row_promoted": row_id in promoted,
        "role_permitted": True,
        "manifest_verified": manifest_ok,
        "hash_verified": hash_ok,
        "sanitization_verified": sanitization_ok,
        "research_mode_only": True,
        "production_permissions_blocked": True,
    }

    return (
        AccessResult(
            request.request_id,
            row_id,
            export_id,
            request.request_type,
            decision,
            True,
            audit_id,
            gates,
            "Research-mode access granted",
        ),
        access_contract,
    )


def _build_access_requests() -> list[AccessRequest]:
    positive = [
        AccessRequest("pos-view-dcm001", "DCM-001", "pos-dcm001-placeholder", "research_view", "research_viewer", "RESEARCH_VIEW"),
        AccessRequest("pos-view-dcm004", "DCM-004", "pos-dcm004-placeholder", "research_view", "research_viewer", "RESEARCH_VIEW"),
        AccessRequest("pos-export-dcm001", "DCM-001", "pos-dcm001-placeholder", "research_export", "research_exporter", "RESEARCH_EXPORT"),
        AccessRequest("pos-export-dcm004", "DCM-004", "pos-dcm004-placeholder", "research_export", "research_exporter", "RESEARCH_EXPORT"),
        AccessRequest("pos-review-dcm001", "DCM-001", "pos-dcm001-placeholder", "research_review", "research_reviewer", "RESEARCH_REVIEW"),
        AccessRequest("pos-review-dcm004", "DCM-004", "pos-dcm004-placeholder", "research_review", "research_reviewer", "RESEARCH_REVIEW"),
        AccessRequest("pos-approve-causal-dcm001", "DCM-001", "pos-dcm001-placeholder", "research_review_approve", "causal_methods_reviewer", "RESEARCH_REVIEW_APPROVE"),
        AccessRequest("pos-approve-causal-dcm004", "DCM-004", "pos-dcm004-placeholder", "research_review_approve", "causal_methods_reviewer", "RESEARCH_REVIEW_APPROVE"),
        AccessRequest("pos-approve-gov-dcm001", "DCM-001", "pos-dcm001-placeholder", "research_review_approve", "governance_reviewer", "RESEARCH_REVIEW_APPROVE"),
        AccessRequest("pos-approve-gov-dcm004", "DCM-004", "pos-dcm004-placeholder", "research_review_approve", "governance_reviewer", "RESEARCH_REVIEW_APPROVE"),
        AccessRequest("pos-manifest-dcm001", "DCM-001", "pos-dcm001-placeholder", "manifest_view", "audit_viewer", "MANIFEST_VIEW"),
        AccessRequest("pos-manifest-dcm004", "DCM-004", "pos-dcm004-placeholder", "manifest_view", "audit_viewer", "MANIFEST_VIEW"),
        AccessRequest("pos-audit-dcm001", "DCM-001", "pos-dcm001-placeholder", "audit_view", "audit_viewer", "AUDIT_VIEW"),
        AccessRequest("pos-audit-dcm004", "DCM-004", "pos-dcm004-placeholder", "audit_view", "audit_viewer", "AUDIT_VIEW"),
        AccessRequest("pos-admin-view-dcm001", "DCM-001", "pos-dcm001-placeholder", "admin_view", "research_mode_admin", "RESEARCH_VIEW"),
        AccessRequest("pos-admin-export-dcm004", "DCM-004", "pos-dcm004-placeholder", "admin_export", "research_mode_admin", "RESEARCH_EXPORT"),
    ]
    negative = [
        AccessRequest("neg-viewer-export", "DCM-001", "pos-dcm001-placeholder", "viewer_export", "research_viewer", "RESEARCH_EXPORT"),
        AccessRequest("neg-exporter-approve", "DCM-001", "pos-dcm001-placeholder", "exporter_approve", "research_exporter", "RESEARCH_REVIEW_APPROVE"),
        AccessRequest("neg-reviewer-approve", "DCM-004", "pos-dcm004-placeholder", "reviewer_approve", "research_reviewer", "RESEARCH_REVIEW_APPROVE"),
        AccessRequest("neg-audit-export", "DCM-001", "pos-dcm001-placeholder", "audit_export", "audit_viewer", "RESEARCH_EXPORT"),
        AccessRequest("neg-invalid-role", "DCM-001", "pos-dcm001-placeholder", "invalid_role", "production_approver", "RESEARCH_VIEW"),
        AccessRequest("neg-unknown", "DCM-999", "pos-dcm001-placeholder", "unknown_row", "research_viewer", "RESEARCH_VIEW"),
        AccessRequest("neg-brb", "DCM-005-BRB", "pos-dcm001-placeholder", "causal_trustreport", "research_viewer", "RESEARCH_VIEW"),
        AccessRequest("neg-kfold", "DCM-005-KFOLD", "pos-dcm001-placeholder", "causal_trustreport", "research_viewer", "RESEARCH_VIEW"),
        AccessRequest("neg-placebo", "DCM-005-PLACEBO", "pos-dcm001-placeholder", "causal_trustreport", "research_viewer", "RESEARCH_VIEW"),
        AccessRequest("neg-dcm006", "DCM-006", "pos-dcm001-placeholder", "global_claim", "research_viewer", "RESEARCH_VIEW", claim_type="global"),
        AccessRequest("neg-dcm008", "DCM-008", "pos-dcm001-placeholder", "aggregate_stratified", "research_viewer", "RESEARCH_VIEW", claim_type="aggregate_stratified"),
        AccessRequest("neg-cal", "DCM-001", "pos-dcm001-placeholder", "calibration_write", "calibration_signal_writer", "CALIBRATION_SIGNAL_WRITE"),
        AccessRequest("neg-live-api", "DCM-004", "pos-dcm004-placeholder", "live_api", "api_operator", "LIVE_API_EXECUTE"),
        AccessRequest("neg-scheduler", "DCM-001", "pos-dcm001-placeholder", "scheduler", "scheduler_operator", "SCHEDULER_EXECUTE"),
        AccessRequest("neg-prod", "DCM-004", "pos-dcm004-placeholder", "production_approve", "production_approver", "PRODUCTION_DECISION_APPROVE"),
        AccessRequest("neg-budget", "DCM-001", "pos-dcm001-placeholder", "budget", "budget_optimizer", "BUDGET_OPTIMIZATION_EXECUTE"),
        AccessRequest("neg-global-admin", "DCM-001", "pos-dcm001-placeholder", "global_admin", "global_platform_admin", "GLOBAL_PLATFORM_ADMIN"),
        AccessRequest("neg-unsanitized", "DCM-001", "pos-dcm001-placeholder", "unsanitized", "research_viewer", "RESEARCH_VIEW", defect="unsanitized"),
        AccessRequest("neg-hash", "DCM-004", "pos-dcm004-placeholder", "hash_mismatch", "research_viewer", "RESEARCH_VIEW", defect="hash_mismatch"),
        AccessRequest("neg-manifest", "DCM-001", "pos-dcm001-placeholder", "manifest_mismatch", "research_viewer", "RESEARCH_VIEW", defect="manifest_mismatch"),
        AccessRequest(
            "neg-unreviewed",
            "DCM-001",
            "pos-dcm001-synthetic",
            "unreviewed_approve",
            "causal_methods_reviewer",
            "RESEARCH_REVIEW_APPROVE",
            defect="unreviewed",
        ),
    ]
    return positive + negative


def build_trustreport_research_mode_access_control_001() -> dict[str, Any]:
    inputs = _load_inputs()
    review_summary = inputs["review_workflow"]
    export_summary = inputs["artifact_export"]
    dry_run = inputs["integration_dry_run"]
    promotion = inputs["downstream_promotion"]
    manifest_doc = inputs["export_manifest"]
    registry = load_registry()

    if review_summary.get("governance_verdict") != "trustreport_research_mode_review_workflow_passed":
        raise ValueError("Review workflow must have passed before access control")
    if export_summary.get("governance_verdict") != "trustreport_research_mode_artifact_export_passed":
        raise ValueError("Artifact export must have passed before access control")

    export_contracts = dict(export_summary.get("export_contracts") or {})
    approved_reviews = _approved_review_exports(review_summary)

    requests = _build_access_requests()
    results: list[AccessResult] = []
    access_contracts: dict[str, dict[str, Any]] = {}
    decision_records: dict[str, dict[str, Any]] = {}
    audit_records: list[dict[str, Any]] = []
    hash_verification: list[dict[str, Any]] = []
    manifest_verification: list[dict[str, Any]] = []
    sanitization_results: list[dict[str, Any]] = []
    review_status_check: list[dict[str, Any]] = []

    deferred = [
        inv["investigation_id"]
        for inv in registry.get("investigations", [])
        if inv.get("status") == "DEFERRED_WITH_TRIGGER"
    ]

    role_matrix = {
        role: sorted(perms) for role, perms in ROLE_PERMISSIONS.items()
    }

    for req in requests:
        result, contract = _evaluate_access(
            req,
            export_contracts=export_contracts,
            manifest_doc=manifest_doc,
            promotion=promotion,
            dry_run=dry_run,
            approved_reviews=approved_reviews,
        )
        results.append(result)

        if contract is not None:
            access_contracts[req.request_id] = contract
            decision_records[req.request_id] = contract

        export_id = result.export_id or f"export-{req.export_request_id}"
        base = export_contracts.get(export_id)
        if base and req.request_id.startswith("pos-"):
            h_ok, h_val = _verify_export_hash(base)
            hash_verification.append(
                {"request_id": req.request_id, "export_id": export_id, "verified": h_ok, "content_hash": h_val}
            )
            m_ok = _verify_manifest(req.export_request_id, base, manifest_doc)
            manifest_verification.append(
                {"request_id": req.request_id, "export_id": export_id, "verified": m_ok}
            )
            sanitization_results.append(
                {
                    "request_id": req.request_id,
                    "sanitized": _payload_is_sanitized(base.get("sanitized_payload") or {}),
                    "measurement_label": (base.get("sanitized_payload") or {}).get("label"),
                }
            )
            review_status_check.append(
                {
                    "request_id": req.request_id,
                    "export_request_id": req.export_request_id,
                    "review_approved": req.export_request_id in approved_reviews,
                    "review_status": contract.get("review_status") if contract else "blocked",
                }
            )

        audit_records.append(
            {
                "audit_record_id": result.audit_record_id,
                "request_id": req.request_id,
                "row_id": req.row_id,
                "decision": result.decision,
                "granted": result.granted,
                "requester_role": req.requester_role,
                "requested_access_mode": req.requested_access_mode,
                "research_mode_only": True,
                "live_api_authorized": False,
                "scheduler_authorized": False,
                "production_approval": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    granted = [r for r in results if r.granted]
    blocked = [r for r in results if not r.granted]
    accepted_row_ids = {r.row_id for r in granted}

    for r in granted:
        if r.row_id not in PROMOTED_ROWS:
            raise ValueError(f"Unexpected access grant for {r.row_id}")

    for role, perms in ROLE_PERMISSIONS.items():
        if perms & ALL_BLOCKED_MODES:
            raise ValueError(f"Role {role} has blocked production permissions")

    contracts_complete = all(
        ACCESS_CONTRACT_FIELDS <= set(c.keys()) for c in access_contracts.values()
    )

    positive_ids = {r.request_id for r in requests if r.request_id.startswith("pos-")}
    positive_pass = all(r.granted for r in results if r.request_id in positive_ids)
    negative_pass = all(not r.granted for r in results if r.request_id.startswith("neg-"))

    if contracts_complete and positive_pass and negative_pass:
        verdict: GovernanceVerdict = "trustreport_research_mode_access_control_passed"
        next_artifact = "TRUSTREPORT_RESEARCH_MODE_AUDIT_LOG_001"
    elif not contracts_complete:
        verdict = "trustreport_research_mode_access_control_blocked_missing_contract"
        next_artifact = "TRUSTREPORT_RESEARCH_MODE_AUDIT_LOG_001"
    else:
        verdict = "trustreport_research_mode_access_control_failed"
        next_artifact = "TRUSTREPORT_RESEARCH_MODE_AUDIT_LOG_001"

    handoff = build_investigation_handoff(
        follow_up_issues=[],
        resolved_issues=[],
        terminal_dispositions=[],
        next_artifact=next_artifact,
    )

    limitations = [
        "This artifact defines research-mode access control for exported TrustReport artifacts.",
        "It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, budget optimization, or global platform rollout.",
        "Access approval is research-mode access approval only.",
        "Only DCM-001 and DCM-004 are accepted for research-mode access.",
        "All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.",
    ]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "input_artifacts": inputs["_paths"],
        "access_scope": sorted(ACCESS_SCOPE),
        "role_permission_matrix": role_matrix,
        "access_requests": [r.to_dict() for r in requests],
        "granted_access": [r.to_dict() for r in granted],
        "blocked_access": [r.to_dict() for r in blocked],
        "accepted_rows": sorted(accepted_row_ids),
        "blocked_rows": sorted({r.row_id for r in blocked}),
        "access_contracts": access_contracts,
        "access_decision_records": decision_records,
        "audit_records": audit_records,
        "negative_control_results": [r.to_dict() for r in results if r.request_id.startswith("neg-")],
        "manifest_verification_results": manifest_verification,
        "hash_verification_results": hash_verification,
        "sanitization_results": sanitization_results,
        "review_status_check": review_status_check,
        "global_authorization_summary": {
            "trust_report_platform_authorized": False,
            "live_api_authorized": False,
            "scheduler_authorized": False,
        },
        "live_api_authorization_summary": {
            "live_api_authorized": False,
            "research_mode_only": True,
        },
        "scheduler_authorization_summary": {
            "scheduler_authorized": False,
            "research_mode_only": True,
        },
        "calibration_signal_summary": {
            "any_calibration_signal_allowed": False,
        },
        "production_decisioning_summary": {
            "any_production_decisioning_allowed": False,
        },
        "budget_optimization_summary": {
            "any_budget_optimization_allowed": False,
        },
        "open_investigation_check": {
            "deferred_investigations": deferred,
            "blocking_for_access": [],
        },
        "governance_verdict": verdict,
        "limitations": limitations,
        "next_artifact": next_artifact,
        "investigation_handoff": handoff,
        "verdict": verdict,
        "contracts_complete": contracts_complete,
        "dcm001_access_result": next(
            (r.to_dict() for r in results if r.request_id == "pos-view-dcm001"),
            {},
        ),
        "dcm004_access_result": next(
            (r.to_dict() for r in results if r.request_id == "pos-view-dcm004"),
            {},
        ),
        "access_results": [r.to_dict() for r in results],
        "_decision_records_full": decision_records,
    }
    return payload


def write_report(payload: dict[str, Any], path: Path, *, overwrite: bool = False) -> None:
    handoff_lines = format_handoff_report_section(
        resolved_in_artifact=[],
        new_investigations=[],
        updated_investigations=[],
        deferred_issues=payload.get("open_investigation_check", {}).get("deferred_investigations", []),
        explicit_exclusions=sorted(
            set(payload.get("blocked_rows", [])) - set(payload.get("accepted_rows", []))
        ),
        revisit_trigger="After TRUSTREPORT_RESEARCH_MODE_AUDIT_LOG_001",
        decision_checkpoint="TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001",
        next_artifact=payload.get("next_artifact"),
    )
    lines = [
        f"# {_ARTIFACT_ID} Report",
        "",
        "## 1. Executive summary",
        "",
        "This artifact defines research-mode access control for exported TrustReport artifacts.",
        "It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, budget optimization, or global platform rollout.",
        "Access approval is research-mode access approval only.",
        "Only DCM-001 and DCM-004 are accepted for research-mode access.",
        "All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.",
        "",
        f"**Governance verdict:** `{payload.get('governance_verdict')}`",
        f"**Accepted rows:** {payload.get('accepted_rows')}",
        "",
        "## 2. Scope",
        "",
        "Research-mode access control for DCM-001 (SCM+JK) and DCM-004 (DID+bootstrap).",
        "",
        "## 3. Non-goals",
        "",
        "- No live API, scheduler, production automation, deployment approval",
        "- No CalibrationSignal, budget optimization, stakeholder production approval",
        "- No new statistical simulations or algorithm changes",
        "",
        "## 4. Input artifacts",
        "",
        json.dumps(payload.get("input_artifacts"), indent=2),
        "",
        "## 5. Research-mode access-control contract",
        "",
        json.dumps(list(ACCESS_CONTRACT_FIELDS), indent=2),
        "",
        "## 6. Role model",
        "",
        json.dumps(sorted(ROLE_PERMISSIONS.keys()), indent=2),
        "",
        "## 7. Role-permission matrix",
        "",
        json.dumps(payload.get("role_permission_matrix"), indent=2),
        "",
        "## 8. Access decision classes",
        "",
        "Granted: research view/export/review/approve, manifest view, audit view. All production modes blocked.",
        "",
        "## 9. DCM-001 access result",
        "",
        json.dumps(payload.get("dcm001_access_result"), indent=2),
        "",
        "## 10. DCM-004 access result",
        "",
        json.dumps(payload.get("dcm004_access_result"), indent=2),
        "",
        "## 11. Manifest/hash/sanitization gates",
        "",
        json.dumps(
            {
                "manifest": payload.get("manifest_verification_results"),
                "hash": payload.get("hash_verification_results"),
                "sanitization": payload.get("sanitization_results"),
            },
            indent=2,
        ),
        "",
        "## 12. Review-status gate",
        "",
        json.dumps(payload.get("review_status_check"), indent=2),
        "",
        "## 13. Negative-control access requests",
        "",
        json.dumps(payload.get("negative_control_results"), indent=2),
        "",
        "## 14. Blocked diagnostic-only rows",
        "",
        "DCM-002, DCM-005-BRB, DCM-005-KFOLD, DCM-008 — ACCESS_BLOCKED_DIAGNOSTIC_ONLY",
        "",
        "## 15. Blocked null-monitor causal reuse",
        "",
        "DCM-005-PLACEBO — ACCESS_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
        "",
        "## 16. Blocked multi-cell/global claims",
        "",
        "DCM-006 — ACCESS_BLOCKED_NOT_PROMOTED",
        "",
        "## 17. Blocked stratified aggregate claims",
        "",
        "DCM-008 — ACCESS_BLOCKED_DIAGNOSTIC_ONLY",
        "",
        "## 18. CalibrationSignal boundary",
        "",
        json.dumps(payload.get("calibration_signal_summary"), indent=2),
        "",
        "## 19. Live API boundary",
        "",
        json.dumps(payload.get("live_api_authorization_summary"), indent=2),
        "",
        "## 20. Scheduler boundary",
        "",
        json.dumps(payload.get("scheduler_authorization_summary"), indent=2),
        "",
        "## 21. Production decisioning boundary",
        "",
        json.dumps(payload.get("production_decisioning_summary"), indent=2),
        "",
        "## 22. Budget optimization boundary",
        "",
        json.dumps(payload.get("budget_optimization_summary"), indent=2),
        "",
        "## 23. Global platform boundary",
        "",
        "`trust_report_platform_authorized`: false; `GLOBAL_PLATFORM_ADMIN` blocked",
        "",
        "## 24. Audit record verification",
        "",
        f"Audit records: {len(payload.get('audit_records') or [])}",
        "",
        "## 25. Open investigation check",
        "",
        json.dumps(payload.get("open_investigation_check"), indent=2),
        "",
        "## 26. Governance verdict",
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
    access_output_path: Path | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    payload = build_trustreport_research_mode_access_control_001()
    full_records = payload.pop("_decision_records_full", {})

    if access_output_path is not None:
        _atomic_write(
            access_output_path,
            json.dumps(full_records, indent=2, sort_keys=False) + "\n",
            overwrite=overwrite,
        )

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
        for rec in payload.get("access_results") or []:
            if rec.get("row_id") in DIAGNOSTIC_ONLY_ROWS | {"DCM-006", "DCM-008"}:
                if rec.get("decision", "").startswith("ACCESS_GRANTED"):
                    raise RuntimeError(f"Excluded row {rec['row_id']} must not grant access")
        for role, perms in ROLE_PERMISSIONS.items():
            if perms & ALL_BLOCKED_MODES:
                raise RuntimeError(f"Role {role} must not have production permissions")
        for audit in payload.get("audit_records") or []:
            if audit.get("production_approval"):
                raise RuntimeError("Access must not imply production approval")

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
    parser.add_argument("--access-output-local", type=Path, default=_DEFAULT_ACCESS_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    write_summary(
        args.summary_output,
        overwrite=args.overwrite,
        report_path=args.report_output,
        access_output_path=args.access_output_local,
        strict=args.strict,
    )


if __name__ == "__main__":
    main()
