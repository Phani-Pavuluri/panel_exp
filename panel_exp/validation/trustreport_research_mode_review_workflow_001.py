"""TRUSTREPORT-RESEARCH-MODE-REVIEW-WORKFLOW-001 — governed human-review workflow.

Defines and validates research-mode review workflow for exported TrustReport artifacts.
DCM-001 and DCM-004 only. Review approval is research-mode only — not production authorization.
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
    EXPORT_BANNER,
    PROMOTED_ROWS,
    ROW_EXPORT_WARNINGS,
    _content_hash,
    _payload_is_sanitized,
)

_REPO = Path(__file__).resolve().parents[2]
_ARCHIVE = _REPO / "docs/track_d/archives"
_EXAMPLES = _REPO / "docs/track_d/examples"
_ARTIFACT_ID = "TRUSTREPORT-RESEARCH-MODE-REVIEW-WORKFLOW-001"
_ARTIFACT_VERSION = "1.0.0"
_DEFAULT_SUMMARY = _ARCHIVE / "TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001_summary.json"
_DEFAULT_REPORT = _REPO / "docs/track_d/TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001_REPORT.md"
_DEFAULT_REVIEW_OUTPUT = Path("/tmp/TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001_reviews.json")
_MANIFEST_PATH = _EXAMPLES / "TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_manifest.json"

ReviewDecision = Literal[
    "REVIEW_ACCEPTED_RESEARCH_MODE",
    "REVIEW_ACCEPTED_MANIFEST_ONLY",
    "REVIEW_BLOCKED_MISSING_BANNER",
    "REVIEW_BLOCKED_MISSING_WARNING",
    "REVIEW_BLOCKED_MISSING_RESTRICTION",
    "REVIEW_BLOCKED_MISSING_AUDIT_TRAIL",
    "REVIEW_BLOCKED_HASH_MISMATCH",
    "REVIEW_BLOCKED_MANIFEST_MISMATCH",
    "REVIEW_BLOCKED_UNSANITIZED_PAYLOAD",
    "REVIEW_BLOCKED_LIVE_MEASUREMENT_PAYLOAD",
    "REVIEW_BLOCKED_PRODUCTION_RECOMMENDATION",
    "REVIEW_BLOCKED_BUDGET_RECOMMENDATION",
    "REVIEW_BLOCKED_INVALID_REVIEWER_ROLE",
    "REVIEW_BLOCKED_DIAGNOSTIC_ONLY",
    "REVIEW_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
    "REVIEW_BLOCKED_NOT_PROMOTED",
    "REVIEW_BLOCKED_CALIBRATION_SIGNAL",
    "REVIEW_BLOCKED_LIVE_API",
    "REVIEW_BLOCKED_SCHEDULER",
    "REVIEW_BLOCKED_PRODUCTION_DECISIONING",
    "REVIEW_BLOCKED_BUDGET_OPTIMIZATION",
    "REVIEW_BLOCKED_UNKNOWN_ROW",
]

GovernanceVerdict = Literal[
    "trustreport_research_mode_review_workflow_passed",
    "trustreport_research_mode_review_workflow_blocked_missing_contract",
    "trustreport_research_mode_review_workflow_failed",
]

REQUIRED_INPUTS: dict[str, str] = {
    "artifact_export": "TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_summary.json",
    "renderer_summary": "TRUSTREPORT_RESEARCH_MODE_RENDERER_001_summary.json",
    "integration_dry_run": "TRUSTREPORT_INTEGRATION_DRY_RUN_001_summary.json",
    "downstream_promotion": "TRUSTREPORT_DOWNSTREAM_PROMOTION_001_summary.json",
}

REVIEW_SCOPE = frozenset({"DCM-001", "DCM-004"})

REVIEW_CONTRACT_FIELDS = frozenset(
    {
        "review_id",
        "artifact_id",
        "export_id",
        "row_id",
        "review_mode",
        "review_status",
        "reviewer_role",
        "review_checklist",
        "required_banners_present",
        "warnings_present",
        "restrictions_present",
        "blocked_uses_present",
        "audit_trail_present",
        "content_hash_verified",
        "manifest_verified",
        "sanitization_verified",
        "authorization_boundaries_verified",
        "open_investigation_check",
        "decision_record",
        "created_at",
    }
)

VALID_REVIEWER_ROLES = frozenset(
    {"research_reviewer", "causal_methods_reviewer", "governance_reviewer"}
)
INVALID_REVIEWER_ROLES = frozenset(
    {"production_approver", "scheduler_operator", "api_operator", "budget_optimizer", "unknown"}
)

REVIEW_CHECKLIST_ITEMS = [
    "research_mode_banner_present",
    "not_for_production_banner_present",
    "not_for_budget_optimization_banner_present",
    "no_calibration_signal_banner_present",
    "no_live_api_banner_present",
    "no_scheduler_banner_present",
    "sanitized_artifact_export_banner_present",
    "row_identity_preserved",
    "method_identity_preserved",
    "warnings_present",
    "restrictions_present",
    "blocked_uses_present",
    "audit_trail_present",
    "manifest_present",
    "content_hash_matches",
    "payload_placeholder_or_synthetic_only",
    "no_raw_live_measurement_payload",
    "no_production_recommendation",
    "no_budget_allocation_recommendation",
]

DIAGNOSTIC_ONLY_ROWS = frozenset(
    {"DCM-002", "DCM-005-BRB", "DCM-005-KFOLD", "DCM-008"}
)
NULL_MONITOR_ROWS = frozenset({"DCM-005-PLACEBO", "SCM-PLACEBO"})

EXPORT_REQUEST_MAP = {
    "pos-dcm001-placeholder": ("DCM-001", "research_reviewer"),
    "pos-dcm001-synthetic": ("DCM-001", "causal_methods_reviewer"),
    "pos-dcm001-manifest": ("DCM-001", "governance_reviewer"),
    "pos-dcm004-placeholder": ("DCM-004", "research_reviewer"),
    "pos-dcm004-synthetic": ("DCM-004", "causal_methods_reviewer"),
    "pos-dcm004-manifest": ("DCM-004", "governance_reviewer"),
}


@dataclass(frozen=True)
class ReviewRequest:
    request_id: str
    row_id: str
    export_request_id: str
    request_type: str
    reviewer_role: str
    workflow_action: str = "RESEARCH_MODE_REVIEW_APPROVAL"
    claim_type: str | None = None
    defect: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReviewResult:
    request_id: str
    row_id: str
    export_id: str
    request_type: str
    decision: ReviewDecision
    accepted: bool
    review_status: str
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


def _verify_content_hash(export_contract: dict[str, Any]) -> tuple[bool, str]:
    body = copy.deepcopy(export_contract)
    stored = body.pop("content_hash", None)
    manifest = body.pop("export_manifest", None)
    body.pop("export_status", None)
    body.pop("export_decision", None)
    computed = _content_hash(body)
    if stored != computed:
        return False, f"stored={stored} computed={computed}"
    if manifest and manifest.get("content_hash") != stored:
        return False, "manifest hash mismatch"
    return True, stored or ""


def _verify_manifest(
    export_request_id: str,
    export_contract: dict[str, Any],
    manifest_doc: dict[str, Any],
) -> bool:
    exports = manifest_doc.get("exports") or {}
    entry = exports.get(export_request_id)
    if not entry:
        return False
    contract_manifest = export_contract.get("export_manifest") or {}
    return (
        entry.get("export_id") == contract_manifest.get("export_id")
        and entry.get("content_hash") == contract_manifest.get("content_hash")
        and entry.get("row_id") == export_contract.get("row_id")
    )


def _run_checklist(
    export_contract: dict[str, Any],
    *,
    hash_ok: bool,
    manifest_ok: bool,
) -> dict[str, bool]:
    banners = list(export_contract.get("banners") or [])
    banner_set = {b.upper() for b in banners}
    payload = export_contract.get("sanitized_payload") or {}
    auth = export_contract.get("authorization_boundaries") or {}

    checklist = {
        "research_mode_banner_present": "RESEARCH MODE ONLY" in banner_set,
        "not_for_production_banner_present": "NOT FOR PRODUCTION DECISIONING" in banner_set,
        "not_for_budget_optimization_banner_present": "NOT FOR BUDGET OPTIMIZATION" in banner_set,
        "no_calibration_signal_banner_present": "NO CALIBRATIONSIGNAL AUTHORIZATION" in banner_set,
        "no_live_api_banner_present": "NO LIVE API AUTHORIZATION" in banner_set,
        "no_scheduler_banner_present": "NO SCHEDULER AUTHORIZATION" in banner_set,
        "sanitized_artifact_export_banner_present": "SANITIZED ARTIFACT EXPORT" in banner_set,
        "row_identity_preserved": bool(export_contract.get("row_id")),
        "method_identity_preserved": bool(export_contract.get("method_identity")),
        "warnings_present": bool(export_contract.get("warnings")),
        "restrictions_present": bool(export_contract.get("restrictions")),
        "blocked_uses_present": bool(export_contract.get("blocked_uses")),
        "audit_trail_present": bool(export_contract.get("audit_trail")),
        "manifest_present": bool(export_contract.get("export_manifest")),
        "content_hash_matches": hash_ok,
        "payload_placeholder_or_synthetic_only": payload.get("label")
        in (
            "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED",
            "SYNTHETIC_DRY_RUN_PAYLOAD",
            "MANIFEST_ONLY_EXPORT",
        ),
        "no_raw_live_measurement_payload": payload.get("live_data") is not True
        and payload.get("live_measurement") is not True,
        "no_production_recommendation": "production_recommendation" not in json.dumps(payload).lower(),
        "no_budget_allocation_recommendation": "budget_allocation" not in json.dumps(payload).lower(),
        "manifest_verified": manifest_ok,
        "sanitization_verified": _payload_is_sanitized(payload),
        "authorization_boundaries_verified": (
            auth.get("research_mode_only") is True
            and auth.get("live_api_authorized") is False
            and auth.get("scheduler_authorized") is False
            and auth.get("calibration_signal_allowed") is False
            and auth.get("production_decisioning_allowed") is False
            and auth.get("budget_optimization_allowed") is False
            and auth.get("trust_report_platform_authorized") is False
        ),
    }
    return checklist


def _apply_defect(export_contract: dict[str, Any], defect: str | None) -> dict[str, Any]:
    if not defect:
        return export_contract
    contract = copy.deepcopy(export_contract)
    if defect == "missing_banner":
        contract["banners"] = []
    elif defect == "missing_warnings":
        contract["warnings"] = []
    elif defect == "missing_restrictions":
        contract["restrictions"] = []
    elif defect == "missing_audit_trail":
        contract["audit_trail"] = {}
    elif defect == "hash_mismatch":
        contract["content_hash"] = "0" * 64
        if contract.get("export_manifest"):
            contract["export_manifest"]["content_hash"] = "0" * 64
    elif defect == "manifest_mismatch":
        if contract.get("export_manifest"):
            contract["export_manifest"]["export_id"] = "export-mismatch"
    elif defect == "unsanitized_payload":
        contract["sanitized_payload"] = {
            "label": "UNSANITIZED",
            "live_data": True,
            "raw_customer_id": "cust-123",
        }
    elif defect == "live_measurement_payload":
        contract["sanitized_payload"] = {
            "label": "LIVE_MEASUREMENT",
            "live_measurement": True,
            "point_estimate": 1.23,
        }
    elif defect == "production_recommendation":
        contract["sanitized_payload"] = {
            "label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED",
            "placeholder": True,
            "production_recommendation": "deploy",
        }
    elif defect == "budget_recommendation":
        contract["sanitized_payload"] = {
            "label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED",
            "placeholder": True,
            "budget_allocation": {"cell_a": 0.6},
        }
    return contract


def _build_review_contract(
    *,
    review_id: str,
    export_contract: dict[str, Any],
    request: ReviewRequest,
    checklist: dict[str, bool],
    decision: ReviewDecision,
    review_status: str,
    deferred: list[str],
) -> dict[str, Any]:
    return {
        "review_id": review_id,
        "artifact_id": _ARTIFACT_ID,
        "export_id": export_contract.get("export_id", f"export-{request.export_request_id}"),
        "row_id": request.row_id,
        "review_mode": "research_mode_review_only",
        "review_status": review_status,
        "reviewer_role": request.reviewer_role,
        "review_checklist": checklist,
        "required_banners_present": all(
            checklist.get(k, False)
            for k in (
                "research_mode_banner_present",
                "not_for_production_banner_present",
                "not_for_budget_optimization_banner_present",
                "no_calibration_signal_banner_present",
                "no_live_api_banner_present",
                "no_scheduler_banner_present",
                "sanitized_artifact_export_banner_present",
            )
        ),
        "warnings_present": checklist.get("warnings_present", False),
        "restrictions_present": checklist.get("restrictions_present", False),
        "blocked_uses_present": checklist.get("blocked_uses_present", False),
        "audit_trail_present": checklist.get("audit_trail_present", False),
        "content_hash_verified": checklist.get("content_hash_matches", False),
        "manifest_verified": checklist.get("manifest_verified", False),
        "sanitization_verified": checklist.get("sanitization_verified", False),
        "authorization_boundaries_verified": checklist.get("authorization_boundaries_verified", False),
        "open_investigation_check": {"deferred_investigations": deferred, "blocking_for_review": []},
        "decision_record": {
            "decision": decision,
            "workflow_action": request.workflow_action,
            "production_approval": False,
            "research_mode_review_only": True,
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def _evaluate_review(
    request: ReviewRequest,
    *,
    export_contracts: dict[str, dict[str, Any]],
    manifest_doc: dict[str, Any],
    promotion: dict[str, Any],
    dry_run: dict[str, Any],
) -> tuple[ReviewResult, dict[str, Any] | None]:
    audit_id = f"review-audit-{request.request_id}"
    promoted = set(promotion.get("promoted_rows") or [])
    dry_accepted = set(dry_run.get("accepted_rows") or [])
    action = request.workflow_action.upper()

    blocked_actions = {
        "PRODUCTION_APPROVAL": "REVIEW_BLOCKED_PRODUCTION_DECISIONING",
        "LIVE_API_APPROVAL": "REVIEW_BLOCKED_LIVE_API",
        "SCHEDULER_APPROVAL": "REVIEW_BLOCKED_SCHEDULER",
        "CALIBRATION_SIGNAL_APPROVAL": "REVIEW_BLOCKED_CALIBRATION_SIGNAL",
        "BUDGET_OPTIMIZATION_APPROVAL": "REVIEW_BLOCKED_BUDGET_OPTIMIZATION",
        "AUTO_RECOMMENDATION_APPROVAL": "REVIEW_BLOCKED_PRODUCTION_DECISIONING",
        "GLOBAL_PLATFORM_APPROVAL": "REVIEW_BLOCKED_PRODUCTION_DECISIONING",
    }
    if action in blocked_actions:
        return (
            ReviewResult(
                request.request_id,
                request.row_id,
                "",
                request.request_type,
                blocked_actions[action],  # type: ignore[arg-type]
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {f"{action}_blocked": True},
                f"Workflow action {action} forbidden",
            ),
            None,
        )

    if request.reviewer_role in INVALID_REVIEWER_ROLES or request.request_type == "invalid_reviewer_role":
        return (
            ReviewResult(
                request.request_id,
                request.row_id,
                "",
                request.request_type,
                "REVIEW_BLOCKED_INVALID_REVIEWER_ROLE",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"invalid_reviewer_role": True},
                f"Invalid reviewer role: {request.reviewer_role}",
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
            ReviewResult(
                request.request_id,
                row_id,
                "",
                request.request_type,
                "REVIEW_BLOCKED_UNKNOWN_ROW",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"unknown_row": True},
                f"Unknown row: {row_id}",
            ),
            None,
        )

    if row_id in DIAGNOSTIC_ONLY_ROWS:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                "",
                request.request_type,
                "REVIEW_BLOCKED_DIAGNOSTIC_ONLY",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"diagnostic_only": True},
                f"{row_id} is diagnostic-only",
            ),
            None,
        )

    if row_id in NULL_MONITOR_ROWS and request.request_type == "causal_trustreport":
        return (
            ReviewResult(
                request.request_id,
                row_id,
                "",
                request.request_type,
                "REVIEW_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"null_monitor_causal_reuse": True},
                "Null-monitor path cannot receive causal TrustReport review",
            ),
            None,
        )

    if row_id == "DCM-006":
        return (
            ReviewResult(
                request.request_id,
                row_id,
                "",
                request.request_type,
                "REVIEW_BLOCKED_NOT_PROMOTED",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"multicell_global_blocked": True},
                "DCM-006 global/winner/pooled review blocked",
            ),
            None,
        )

    if row_id == "DCM-008" or request.claim_type == "aggregate_stratified":
        return (
            ReviewResult(
                request.request_id,
                row_id,
                "",
                request.request_type,
                "REVIEW_BLOCKED_DIAGNOSTIC_ONLY",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"stratified_aggregate_blocked": True},
                "DCM-008 aggregate stratified review blocked",
            ),
            None,
        )

    if row_id not in promoted or row_id not in dry_accepted:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                "",
                request.request_type,
                "REVIEW_BLOCKED_NOT_PROMOTED",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"not_promoted": True},
                f"{row_id} not promoted or dry-run approved",
            ),
            None,
        )

    export_id = f"export-{request.export_request_id}"
    base_contract = export_contracts.get(export_id)
    if not base_contract:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_NOT_PROMOTED",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"export_missing": True},
                f"Export contract missing: {export_id}",
            ),
            None,
        )

    contract = _apply_defect(base_contract, request.defect)

    if request.defect == "hash_mismatch":
        hash_ok = False
    else:
        hash_ok, _ = _verify_content_hash(base_contract)

    if request.defect == "manifest_mismatch":
        manifest_ok = False
    else:
        manifest_ok = _verify_manifest(request.export_request_id, base_contract, manifest_doc)

    checklist = _run_checklist(contract, hash_ok=hash_ok, manifest_ok=manifest_ok)

    if request.defect == "missing_banner" or not checklist["research_mode_banner_present"]:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_MISSING_BANNER",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"missing_banner": True},
                "Required banners missing",
            ),
            None,
        )

    if request.defect == "missing_warnings" or not checklist["warnings_present"]:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_MISSING_WARNING",
                False,
                "RESEARCH_REVIEW_REJECTED",
                audit_id,
                {"missing_warnings": True},
                "Required warnings missing",
            ),
            None,
        )

    if request.defect == "missing_restrictions" or not checklist["restrictions_present"]:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_MISSING_RESTRICTION",
                False,
                "RESEARCH_REVIEW_REJECTED",
                audit_id,
                {"missing_restrictions": True},
                "Required restrictions missing",
            ),
            None,
        )

    if request.defect == "missing_audit_trail" or not checklist["audit_trail_present"]:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_MISSING_AUDIT_TRAIL",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"missing_audit_trail": True},
                "Audit trail missing",
            ),
            None,
        )

    if request.defect == "hash_mismatch" or not checklist["content_hash_matches"]:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_HASH_MISMATCH",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"hash_mismatch": True},
                "Content hash mismatch",
            ),
            None,
        )

    if request.defect == "manifest_mismatch" or not checklist["manifest_verified"]:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_MANIFEST_MISMATCH",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"manifest_mismatch": True},
                "Manifest mismatch",
            ),
            None,
        )

    if request.defect == "unsanitized_payload":
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_UNSANITIZED_PAYLOAD",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"unsanitized_payload": True},
                "Unsanitized payload",
            ),
            None,
        )

    if request.defect == "live_measurement_payload":
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_LIVE_MEASUREMENT_PAYLOAD",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"live_measurement_payload": True},
                "Raw/live measurement payload",
            ),
            None,
        )

    if not checklist["no_raw_live_measurement_payload"]:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_LIVE_MEASUREMENT_PAYLOAD",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"live_measurement_payload": True},
                "Raw/live measurement payload",
            ),
            None,
        )

    if not checklist["sanitization_verified"]:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_UNSANITIZED_PAYLOAD",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"unsanitized_payload": True},
                "Unsanitized payload",
            ),
            None,
        )

    if request.defect == "production_recommendation" or not checklist["no_production_recommendation"]:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_PRODUCTION_RECOMMENDATION",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"production_recommendation": True},
                "Production recommendation present",
            ),
            None,
        )

    if request.defect == "budget_recommendation" or not checklist["no_budget_allocation_recommendation"]:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_BUDGET_RECOMMENDATION",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"budget_recommendation": True},
                "Budget allocation recommendation present",
            ),
            None,
        )

    if request.reviewer_role not in VALID_REVIEWER_ROLES:
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_INVALID_REVIEWER_ROLE",
                False,
                "RESEARCH_REVIEW_BLOCKED",
                audit_id,
                {"invalid_reviewer_role": True},
                f"Invalid reviewer role: {request.reviewer_role}",
            ),
            None,
        )

    required = [checklist[item] for item in REVIEW_CHECKLIST_ITEMS if item in checklist]
    if not all(required):
        return (
            ReviewResult(
                request.request_id,
                row_id,
                export_id,
                request.request_type,
                "REVIEW_BLOCKED_MISSING_BANNER",
                False,
                "RESEARCH_REVIEW_REJECTED",
                audit_id,
                {"checklist_incomplete": True},
                "Review checklist incomplete",
            ),
            None,
        )

    payload_label = contract.get("sanitized_payload", {}).get("label")
    if payload_label == "MANIFEST_ONLY_EXPORT":
        decision: ReviewDecision = "REVIEW_ACCEPTED_MANIFEST_ONLY"
    else:
        decision = "REVIEW_ACCEPTED_RESEARCH_MODE"

    review_id = f"review-{request.request_id}"
    review_contract = _build_review_contract(
        review_id=review_id,
        export_contract=base_contract,
        request=request,
        checklist=checklist,
        decision=decision,
        review_status="RESEARCH_REVIEW_APPROVED",
        deferred=[],
    )

    gates = {
        "row_promoted": row_id in promoted,
        "checklist_complete": True,
        "research_mode_review_only": True,
        "production_approval": False,
    }

    return (
        ReviewResult(
            request.request_id,
            row_id,
            export_id,
            request.request_type,
            decision,
            True,
            "RESEARCH_REVIEW_APPROVED",
            audit_id,
            gates,
            "Research-mode review approved (not production authorization)",
        ),
        review_contract,
    )


def _build_review_requests() -> list[ReviewRequest]:
    positive = [
        ReviewRequest(
            req_id,
            row_id,
            req_id,
            "research_review",
            role,
        )
        for req_id, (row_id, role) in EXPORT_REQUEST_MAP.items()
    ]
    negative = [
        ReviewRequest("neg-missing-banner", "DCM-001", "pos-dcm001-placeholder", "missing_banner", "research_reviewer", defect="missing_banner"),
        ReviewRequest("neg-missing-warnings", "DCM-001", "pos-dcm001-placeholder", "missing_warnings", "research_reviewer", defect="missing_warnings"),
        ReviewRequest("neg-missing-restrictions", "DCM-004", "pos-dcm004-placeholder", "missing_restrictions", "research_reviewer", defect="missing_restrictions"),
        ReviewRequest("neg-missing-audit", "DCM-004", "pos-dcm004-placeholder", "missing_audit_trail", "governance_reviewer", defect="missing_audit_trail"),
        ReviewRequest("neg-hash-mismatch", "DCM-001", "pos-dcm001-synthetic", "hash_mismatch", "causal_methods_reviewer", defect="hash_mismatch"),
        ReviewRequest("neg-manifest-mismatch", "DCM-004", "pos-dcm004-synthetic", "manifest_mismatch", "causal_methods_reviewer", defect="manifest_mismatch"),
        ReviewRequest("neg-unsanitized", "DCM-001", "pos-dcm001-placeholder", "unsanitized_payload", "research_reviewer", defect="unsanitized_payload"),
        ReviewRequest("neg-live-payload", "DCM-004", "pos-dcm004-placeholder", "live_measurement_payload", "research_reviewer", defect="live_measurement_payload"),
        ReviewRequest("neg-prod-rec", "DCM-001", "pos-dcm001-placeholder", "production_recommendation", "research_reviewer", defect="production_recommendation"),
        ReviewRequest("neg-budget-rec", "DCM-004", "pos-dcm004-placeholder", "budget_recommendation", "research_reviewer", defect="budget_recommendation"),
        ReviewRequest("neg-invalid-role", "DCM-001", "pos-dcm001-placeholder", "invalid_reviewer_role", "production_approver"),
        ReviewRequest("neg-brb", "DCM-005-BRB", "pos-dcm001-placeholder", "causal_trustreport", "research_reviewer"),
        ReviewRequest("neg-kfold", "DCM-005-KFOLD", "pos-dcm001-placeholder", "causal_trustreport", "research_reviewer"),
        ReviewRequest("neg-placebo", "DCM-005-PLACEBO", "pos-dcm001-placeholder", "causal_trustreport", "research_reviewer"),
        ReviewRequest("neg-dcm006", "DCM-006", "pos-dcm001-placeholder", "global_claim", "research_reviewer", claim_type="global"),
        ReviewRequest("neg-dcm008", "DCM-008", "pos-dcm001-placeholder", "aggregate_stratified", "governance_reviewer", claim_type="aggregate_stratified"),
        ReviewRequest("neg-cal", "DCM-001", "pos-dcm001-placeholder", "calibration_approval", "governance_reviewer", workflow_action="CALIBRATION_SIGNAL_APPROVAL"),
        ReviewRequest("neg-live", "DCM-004", "pos-dcm004-placeholder", "live_api_approval", "research_reviewer", workflow_action="LIVE_API_APPROVAL"),
        ReviewRequest("neg-scheduler", "DCM-001", "pos-dcm001-placeholder", "scheduler_approval", "research_reviewer", workflow_action="SCHEDULER_APPROVAL"),
        ReviewRequest("neg-prod", "DCM-004", "pos-dcm004-placeholder", "production_approval", "research_reviewer", workflow_action="PRODUCTION_APPROVAL"),
        ReviewRequest("neg-budget", "DCM-001", "pos-dcm001-placeholder", "budget_approval", "research_reviewer", workflow_action="BUDGET_OPTIMIZATION_APPROVAL"),
        ReviewRequest("neg-unknown", "DCM-999", "pos-dcm001-placeholder", "unknown_row", "research_reviewer"),
    ]
    return positive + negative


def build_trustreport_research_mode_review_workflow_001() -> dict[str, Any]:
    inputs = _load_inputs()
    export_summary = inputs["artifact_export"]
    renderer = inputs["renderer_summary"]
    dry_run = inputs["integration_dry_run"]
    promotion = inputs["downstream_promotion"]
    manifest_doc = inputs["export_manifest"]
    registry = load_registry()

    if export_summary.get("governance_verdict") != "trustreport_research_mode_artifact_export_passed":
        raise ValueError("Artifact export must have passed before review workflow")
    if renderer.get("governance_verdict") != "trustreport_research_mode_renderer_passed":
        raise ValueError("Renderer artifact must have passed before review workflow")

    export_contracts = dict(export_summary.get("export_contracts") or {})
    review_contracts: dict[str, dict[str, Any]] = {}
    warning_contracts = dict(export_summary.get("warning_contracts") or ROW_EXPORT_WARNINGS)
    restriction_contracts = dict(export_summary.get("restriction_contracts") or {})

    requests = _build_review_requests()
    results: list[ReviewResult] = []
    review_records: dict[str, dict[str, Any]] = {}
    audit_records: list[dict[str, Any]] = []
    hash_verification: list[dict[str, Any]] = []
    manifest_verification: list[dict[str, Any]] = []
    sanitization_results: list[dict[str, Any]] = []

    deferred = [
        inv["investigation_id"]
        for inv in registry.get("investigations", [])
        if inv.get("status") == "DEFERRED_WITH_TRIGGER"
    ]

    for req in requests:
        result, review_contract = _evaluate_review(
            req,
            export_contracts=export_contracts,
            manifest_doc=manifest_doc,
            promotion=promotion,
            dry_run=dry_run,
        )
        results.append(result)

        if review_contract is not None:
            review_contract["open_investigation_check"] = {
                "deferred_investigations": deferred,
                "blocking_for_review": [],
            }
            review_contracts[review_contract["review_id"]] = review_contract
            review_records[req.request_id] = review_contract

        export_id = result.export_id or f"export-{req.export_request_id}"
        base = export_contracts.get(export_id)
        if base and req.request_id in EXPORT_REQUEST_MAP:
            h_ok, h_val = _verify_content_hash(base)
            hash_verification.append(
                {
                    "request_id": req.request_id,
                    "export_id": export_id,
                    "verified": h_ok,
                    "content_hash": h_val,
                }
            )
            m_ok = _verify_manifest(req.export_request_id, base, manifest_doc)
            manifest_verification.append(
                {
                    "request_id": req.request_id,
                    "export_id": export_id,
                    "verified": m_ok,
                }
            )
            sanitization_results.append(
                {
                    "request_id": req.request_id,
                    "sanitized": _payload_is_sanitized(base.get("sanitized_payload") or {}),
                    "measurement_label": (base.get("sanitized_payload") or {}).get("label"),
                }
            )

        audit_records.append(
            {
                "audit_record_id": result.audit_record_id,
                "request_id": req.request_id,
                "row_id": req.row_id,
                "decision": result.decision,
                "accepted": result.accepted,
                "review_status": result.review_status,
                "reviewer_role": req.reviewer_role,
                "research_mode_review_only": True,
                "production_approval": False,
                "live_api_authorized": False,
                "scheduler_authorized": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    accepted = [r for r in results if r.accepted]
    blocked = [r for r in results if not r.accepted]
    accepted_row_ids = {r.row_id for r in accepted}

    for r in accepted:
        if r.row_id not in PROMOTED_ROWS:
            raise ValueError(f"Unexpected review acceptance for {r.row_id}")

    contracts_complete = all(
        REVIEW_CONTRACT_FIELDS <= set(c.keys()) for c in review_contracts.values()
    )

    positive_pass = all(
        r.accepted for r in results if r.request_id in EXPORT_REQUEST_MAP
    )
    negative_pass = all(not r.accepted for r in results if r.request_id.startswith("neg-"))

    if contracts_complete and positive_pass and negative_pass:
        verdict: GovernanceVerdict = "trustreport_research_mode_review_workflow_passed"
        next_artifact = "TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001"
    elif not contracts_complete:
        verdict = "trustreport_research_mode_review_workflow_blocked_missing_contract"
        next_artifact = "TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001"
    else:
        verdict = "trustreport_research_mode_review_workflow_failed"
        next_artifact = "TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001"

    handoff = build_investigation_handoff(
        follow_up_issues=[],
        resolved_issues=[],
        terminal_dispositions=[],
        next_artifact=next_artifact,
    )

    limitations = [
        "This artifact defines the research-mode human-review workflow for exported TrustReport artifacts.",
        "It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, budget optimization, or global platform rollout.",
        "Review approval is research-mode review approval only.",
        "Only DCM-001 and DCM-004 are accepted for research-mode review.",
        "All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.",
    ]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "input_artifacts": inputs["_paths"],
        "review_scope": sorted(REVIEW_SCOPE),
        "review_requests": [r.to_dict() for r in requests],
        "accepted_reviews": [r.to_dict() for r in accepted],
        "blocked_reviews": [r.to_dict() for r in blocked],
        "accepted_rows": sorted(accepted_row_ids),
        "blocked_rows": sorted({r.row_id for r in blocked}),
        "review_contracts": review_contracts,
        "review_checklists": {
            rid: rc.get("review_checklist", {})
            for rid, rc in review_contracts.items()
        },
        "review_decision_records": review_records,
        "audit_records": audit_records,
        "negative_control_results": [r.to_dict() for r in results if r.request_id.startswith("neg-")],
        "hash_verification_results": hash_verification,
        "manifest_verification_results": manifest_verification,
        "sanitization_results": sanitization_results,
        "warning_contracts": warning_contracts,
        "restriction_contracts": restriction_contracts,
        "global_authorization_summary": {
            "trust_report_platform_authorized": False,
            "live_api_authorized": False,
            "scheduler_authorized": False,
        },
        "live_api_authorization_summary": {
            "live_api_authorized": False,
            "research_mode_review_only": True,
        },
        "scheduler_authorization_summary": {
            "scheduler_authorized": False,
            "research_mode_review_only": True,
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
            "blocking_for_review": [],
        },
        "governance_verdict": verdict,
        "limitations": limitations,
        "next_artifact": next_artifact,
        "investigation_handoff": handoff,
        "verdict": verdict,
        "contracts_complete": contracts_complete,
        "reviewer_role_model": {
            "valid_roles": sorted(VALID_REVIEWER_ROLES),
            "invalid_roles": sorted(INVALID_REVIEWER_ROLES),
            "workflow_action_allowed": "RESEARCH_MODE_REVIEW_APPROVAL",
            "workflow_actions_blocked": [
                "PRODUCTION_APPROVAL",
                "LIVE_API_APPROVAL",
                "SCHEDULER_APPROVAL",
                "CALIBRATION_SIGNAL_APPROVAL",
                "BUDGET_OPTIMIZATION_APPROVAL",
                "AUTO_RECOMMENDATION_APPROVAL",
                "GLOBAL_PLATFORM_APPROVAL",
            ],
        },
        "review_checklist_items": REVIEW_CHECKLIST_ITEMS,
        "dcm001_review_result": next(
            (r.to_dict() for r in results if r.request_id == "pos-dcm001-placeholder"),
            {},
        ),
        "dcm004_review_result": next(
            (r.to_dict() for r in results if r.request_id == "pos-dcm004-placeholder"),
            {},
        ),
        "review_results": [r.to_dict() for r in results],
        "_review_records_full": review_records,
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
        revisit_trigger="After TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001",
        decision_checkpoint="TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001",
        next_artifact=payload.get("next_artifact"),
    )
    lines = [
        f"# {_ARTIFACT_ID} Report",
        "",
        "## 1. Executive summary",
        "",
        "This artifact defines the research-mode human-review workflow for exported TrustReport artifacts.",
        "It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, budget optimization, or global platform rollout.",
        "Review approval is research-mode review approval only.",
        "Only DCM-001 and DCM-004 are accepted for research-mode review.",
        "All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.",
        "",
        f"**Governance verdict:** `{payload.get('governance_verdict')}`",
        f"**Accepted rows:** {payload.get('accepted_rows')}",
        "",
        "## 2. Scope",
        "",
        "Human-review workflow for DCM-001 (SCM+JK) and DCM-004 (DID+bootstrap) exported artifacts.",
        "",
        "## 3. Non-goals",
        "",
        "- No live API, scheduler, production automation",
        "- No CalibrationSignal, budget optimization, stakeholder production approval",
        "- No new statistical simulations or algorithm changes",
        "",
        "## 4. Input artifacts",
        "",
        json.dumps(payload.get("input_artifacts"), indent=2),
        "",
        "## 5. Research-mode review workflow contract",
        "",
        json.dumps(list(REVIEW_CONTRACT_FIELDS), indent=2),
        "",
        "## 6. Reviewer role model",
        "",
        json.dumps(payload.get("reviewer_role_model"), indent=2),
        "",
        "## 7. Review checklist",
        "",
        json.dumps(payload.get("review_checklist_items"), indent=2),
        "",
        "## 8. Review decision classes",
        "",
        "Accepted: `REVIEW_ACCEPTED_RESEARCH_MODE`, `REVIEW_ACCEPTED_MANIFEST_ONLY`. All other decisions block or reject.",
        "",
        "## 9. DCM-001 review result",
        "",
        json.dumps(payload.get("dcm001_review_result"), indent=2),
        "",
        "## 10. DCM-004 review result",
        "",
        json.dumps(payload.get("dcm004_review_result"), indent=2),
        "",
        "## 11. Manifest-only review behavior",
        "",
        "Manifest-only exports receive `REVIEW_ACCEPTED_MANIFEST_ONLY` when checklist passes.",
        "",
        "## 12. Hash verification behavior",
        "",
        json.dumps(payload.get("hash_verification_results"), indent=2),
        "",
        "## 13. Sanitization verification behavior",
        "",
        json.dumps(payload.get("sanitization_results"), indent=2),
        "",
        "## 14. Negative-control review requests",
        "",
        json.dumps(payload.get("negative_control_results"), indent=2),
        "",
        "## 15. Blocked diagnostic-only rows",
        "",
        "DCM-002, DCM-005-BRB, DCM-005-KFOLD, DCM-008 — REVIEW_BLOCKED_DIAGNOSTIC_ONLY",
        "",
        "## 16. Blocked null-monitor causal reuse",
        "",
        "DCM-005-PLACEBO — REVIEW_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
        "",
        "## 17. Blocked multi-cell/global claims",
        "",
        "DCM-006 — REVIEW_BLOCKED_NOT_PROMOTED",
        "",
        "## 18. Blocked stratified aggregate claims",
        "",
        "DCM-008 — REVIEW_BLOCKED_DIAGNOSTIC_ONLY",
        "",
        "## 19. CalibrationSignal boundary",
        "",
        json.dumps(payload.get("calibration_signal_summary"), indent=2),
        "",
        "## 20. Live API boundary",
        "",
        json.dumps(payload.get("live_api_authorization_summary"), indent=2),
        "",
        "## 21. Scheduler boundary",
        "",
        json.dumps(payload.get("scheduler_authorization_summary"), indent=2),
        "",
        "## 22. Production decisioning boundary",
        "",
        json.dumps(payload.get("production_decisioning_summary"), indent=2),
        "",
        "## 23. Budget optimization boundary",
        "",
        json.dumps(payload.get("budget_optimization_summary"), indent=2),
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
    review_output_path: Path | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    payload = build_trustreport_research_mode_review_workflow_001()
    full_records = payload.pop("_review_records_full", {})

    if review_output_path is not None:
        _atomic_write(
            review_output_path,
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
        for rec in payload.get("review_results") or []:
            if rec.get("row_id") in DIAGNOSTIC_ONLY_ROWS | {"DCM-006", "DCM-008"}:
                if rec.get("decision", "").startswith("REVIEW_ACCEPTED"):
                    raise RuntimeError(f"Excluded row {rec['row_id']} must not be reviewed")
        for audit in payload.get("audit_records") or []:
            if audit.get("production_approval"):
                raise RuntimeError("Review must not imply production approval")

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
    parser.add_argument("--review-output-local", type=Path, default=_DEFAULT_REVIEW_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    write_summary(
        args.summary_output,
        overwrite=args.overwrite,
        report_path=args.report_output,
        review_output_path=args.review_output_local,
        strict=args.strict,
    )


if __name__ == "__main__":
    main()
