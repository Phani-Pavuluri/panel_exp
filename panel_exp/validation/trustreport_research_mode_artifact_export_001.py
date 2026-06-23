"""TRUSTREPORT-RESEARCH-MODE-ARTIFACT-EXPORT-001 — governed research-mode artifact export.

Exports sanitized research-mode TrustReport artifacts for DCM-001 and DCM-004 only.
Loads renderer, dry-run, and promotion summaries; does not run new statistical simulations.
Does not authorize live APIs, scheduler, production decisioning, or CalibrationSignal.
"""

from __future__ import annotations

import argparse
import hashlib
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
_EXAMPLES = _REPO / "docs/track_d/examples"
_ARTIFACT_ID = "TRUSTREPORT-RESEARCH-MODE-ARTIFACT-EXPORT-001"
_ARTIFACT_VERSION = "1.0.0"
_SCHEMA_VERSION = "trustreport_research_mode_export_v1"
_DEFAULT_SUMMARY = _ARCHIVE / "TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_summary.json"
_DEFAULT_REPORT = _REPO / "docs/track_d/TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_REPORT.md"
_DEFAULT_EXPORT_OUTPUT = Path("/tmp/TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_exports")
_DEFAULT_MANIFEST = _EXAMPLES / "TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_manifest.json"

ExportDecision = Literal[
    "EXPORT_ACCEPTED_RESEARCH_MODE",
    "EXPORT_ACCEPTED_PLACEHOLDER_RESEARCH_MODE",
    "EXPORT_ACCEPTED_MANIFEST_ONLY",
    "EXPORT_BLOCKED_MISSING_CONTRACT",
    "EXPORT_BLOCKED_UNSUPPORTED_GEOMETRY",
    "EXPORT_BLOCKED_MISSING_DIAGNOSTICS",
    "EXPORT_BLOCKED_DIAGNOSTIC_ONLY",
    "EXPORT_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
    "EXPORT_BLOCKED_NOT_PROMOTED",
    "EXPORT_BLOCKED_CALIBRATION_SIGNAL",
    "EXPORT_BLOCKED_LIVE_API",
    "EXPORT_BLOCKED_SCHEDULER",
    "EXPORT_BLOCKED_PRODUCTION_DECISIONING",
    "EXPORT_BLOCKED_BUDGET_OPTIMIZATION",
    "EXPORT_BLOCKED_UNSANITIZED_PAYLOAD",
    "EXPORT_BLOCKED_MISSING_AUDIT_TRAIL",
    "EXPORT_BLOCKED_UNKNOWN_ROW",
]

GovernanceVerdict = Literal[
    "trustreport_research_mode_artifact_export_passed",
    "trustreport_research_mode_artifact_export_blocked_missing_contract",
    "trustreport_research_mode_artifact_export_failed",
]

REQUIRED_INPUTS: dict[str, str] = {
    "renderer_summary": "TRUSTREPORT_RESEARCH_MODE_RENDERER_001_summary.json",
    "integration_dry_run": "TRUSTREPORT_INTEGRATION_DRY_RUN_001_summary.json",
    "downstream_promotion": "TRUSTREPORT_DOWNSTREAM_PROMOTION_001_summary.json",
}

EXPORT_SCOPE = frozenset({"DCM-001", "DCM-004"})
PROMOTED_ROWS = frozenset({"DCM-001", "DCM-004"})

EXPORT_CONTRACT_FIELDS = frozenset(
    {
        "export_id",
        "artifact_id",
        "row_id",
        "render_source_artifact",
        "renderer_summary_artifact",
        "promotion_artifact",
        "dry_run_artifact",
        "method_identity",
        "estimand",
        "readout_scope",
        "research_mode_only",
        "sanitized_payload",
        "warnings",
        "restrictions",
        "blocked_uses",
        "authorization_boundaries",
        "audit_trail",
        "export_manifest",
        "content_hash",
        "schema_version",
        "created_at",
    }
)

DIAGNOSTIC_ONLY_ROWS = frozenset(
    {"DCM-002", "DCM-005-BRB", "DCM-005-KFOLD", "DCM-008"}
)
NULL_MONITOR_ROWS = frozenset({"DCM-005-PLACEBO", "SCM-PLACEBO"})

EXPORT_BANNER = [
    "RESEARCH MODE ONLY",
    "NOT FOR PRODUCTION DECISIONING",
    "NOT FOR BUDGET OPTIMIZATION",
    "NO CALIBRATIONSIGNAL AUTHORIZATION",
    "NO LIVE API AUTHORIZATION",
    "NO SCHEDULER AUTHORIZATION",
    "SANITIZED ARTIFACT EXPORT",
]

ROW_EXPORT_WARNINGS: dict[str, list[str]] = {
    "DCM-001": [
        "noisy_world_coverage_caveat",
        "type_i_caveat",
        "restricted_geometry_only",
        "fit_diagnostics_required",
    ],
    "DCM-004": [
        "parallel_trends_required",
        "common_timing_required",
        "unsupported_worlds_excluded",
        "fit_diagnostics_required",
    ],
}

UNSANITIZED_PAYLOAD_MARKERS = frozenset(
    {
        "live_measurement",
        "raw_customer_id",
        "raw_user_id",
        "raw_geo_unit",
        "production_recommendation",
        "budget_allocation",
        "calibration_signal",
        "scheduler_payload",
        "api_payload",
        "hidden_authorization",
    }
)


@dataclass(frozen=True)
class ExportRequest:
    request_id: str
    row_id: str
    request_type: str
    export_type: str
    requested_role: str
    geometry: str | None = None
    payload_type: str = "none"  # none | placeholder | synthetic | manifest_only | unsanitized
    include_warnings: bool = True
    include_diagnostics: bool = True
    include_audit_trail: bool = True
    claim_type: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExportResult:
    request_id: str
    row_id: str
    request_type: str
    decision: ExportDecision
    accepted: bool
    audit_record_id: str
    export_status: str
    gate_results: dict[str, bool] = field(default_factory=dict)
    reason: str = ""
    content_hash: str | None = None

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


def _content_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


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


def _contract_complete(contract: dict[str, Any]) -> bool:
    for field_name in EXPORT_CONTRACT_FIELDS:
        if field_name not in contract:
            return False
        val = contract[field_name]
        if field_name in ("warnings", "restrictions", "blocked_uses", "audit_trail", "export_manifest"):
            if not val:
                return False
        elif field_name == "research_mode_only" and val is not True:
            return False
        elif field_name == "sanitized_payload" and not isinstance(val, dict):
            return False
        elif val is None or val == "":
            return False
    return True


def _build_sanitized_payload(
    *,
    request: ExportRequest,
    manifest_only: bool = False,
) -> dict[str, Any]:
    if manifest_only:
        return {
            "label": "MANIFEST_ONLY_EXPORT",
            "manifest_only": True,
            "measurement_included": False,
            "note": "Manifest-only export; no measurement payload attached.",
        }
    if request.payload_type == "synthetic":
        return {
            "label": "SYNTHETIC_DRY_RUN_PAYLOAD",
            "synthetic": True,
            "non_decisioning": True,
            "point_estimate": 0.0,
            "interval_low": -1.0,
            "interval_high": 1.0,
            "note": "Synthetic dry-run payload for export validation only; not a real measurement.",
        }
    return {
        "label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED",
        "placeholder": True,
        "point_estimate": None,
        "interval_low": None,
        "interval_high": None,
    }


def _payload_is_sanitized(payload: dict[str, Any]) -> bool:
    safe_labels = frozenset(
        {
            "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED",
            "SYNTHETIC_DRY_RUN_PAYLOAD",
            "MANIFEST_ONLY_EXPORT",
        }
    )
    if payload.get("label") in safe_labels:
        if payload.get("manifest_only") is True:
            return True
        if payload.get("placeholder") is True:
            return True
        if payload.get("synthetic") is True and payload.get("non_decisioning") is True:
            return True
    if payload.get("live_data") is True:
        return False
    blob = json.dumps(payload).lower()
    for marker in UNSANITIZED_PAYLOAD_MARKERS:
        if f'"{marker}"' in blob or f'"{marker}": true' in blob:
            return False
    return False


def _build_export_contract(
    *,
    export_id: str,
    row_contract: dict[str, Any],
    request: ExportRequest,
    sanitized_payload: dict[str, Any],
    include_audit: bool = True,
) -> dict[str, Any]:
    created_at = datetime.now(timezone.utc).isoformat()
    row_id = row_contract["row_id"]
    warnings = list(ROW_EXPORT_WARNINGS.get(row_id, row_contract.get("required_warnings") or []))
    restrictions = list(row_contract.get("blocked_roles") or [])

    audit_trail = {
        "renderer_summary_artifact": "TRUSTREPORT-RESEARCH-MODE-RENDERER-001",
        "dry_run_approval_artifact": "TRUSTREPORT-INTEGRATION-DRY-RUN-001",
        "promotion_artifact": "TRUSTREPORT-DOWNSTREAM-PROMOTION-001",
        "export_artifact": _ARTIFACT_ID,
        "audit_artifacts": list(row_contract.get("audit_artifacts") or []),
    }
    if not include_audit:
        audit_trail = {}

    export_body = {
        "export_id": export_id,
        "artifact_id": _ARTIFACT_ID,
        "row_id": row_id,
        "render_source_artifact": "TRUSTREPORT-RESEARCH-MODE-RENDERER-001",
        "renderer_summary_artifact": "TRUSTREPORT-RESEARCH-MODE-RENDERER-001",
        "promotion_artifact": "TRUSTREPORT-DOWNSTREAM-PROMOTION-001",
        "dry_run_artifact": "TRUSTREPORT-INTEGRATION-DRY-RUN-001",
        "method_identity": {
            "design_family": row_contract.get("design_family"),
            "estimator": row_contract.get("estimator"),
            "inference_method": row_contract.get("inference_method"),
        },
        "estimand": row_contract.get("estimand"),
        "readout_scope": row_contract.get("readout_scope"),
        "research_mode_only": True,
        "sanitized_payload": sanitized_payload,
        "warnings": warnings,
        "restrictions": restrictions,
        "blocked_uses": list(row_contract.get("blocked_roles") or []),
        "authorization_boundaries": {
            "research_mode_only": True,
            "live_api_authorized": False,
            "scheduler_authorized": False,
            "calibration_signal_allowed": False,
            "production_decisioning_allowed": False,
            "budget_optimization_allowed": False,
            "trust_report_platform_authorized": False,
        },
        "audit_trail": audit_trail,
        "banners": EXPORT_BANNER,
        "schema_version": _SCHEMA_VERSION,
        "created_at": created_at,
    }

    content_hash = _content_hash(export_body)
    export_manifest = {
        "export_id": export_id,
        "row_id": row_id,
        "export_type": request.export_type,
        "schema_version": _SCHEMA_VERSION,
        "content_hash": content_hash,
        "sanitized": True,
        "research_mode_only": True,
        "measurement_label": sanitized_payload.get("label"),
        "created_at": created_at,
    }

    export_body["export_manifest"] = export_manifest
    export_body["content_hash"] = content_hash
    return export_body


def _evaluate_export(
    request: ExportRequest,
    *,
    export_contracts: dict[str, dict[str, Any]],
    renderer_contracts: dict[str, dict[str, Any]],
    promotion: dict[str, Any],
    dry_run: dict[str, Any],
) -> tuple[ExportResult, dict[str, Any] | None]:
    audit_id = f"export-audit-{request.request_id}"
    promoted = set(promotion.get("promoted_rows") or [])
    dry_accepted = set(dry_run.get("accepted_rows") or [])

    role = request.requested_role.lower()
    export_type = request.export_type.lower()

    blocked_mode_map = {
        "production_report_export": "EXPORT_BLOCKED_PRODUCTION_DECISIONING",
        "live_api_payload": "EXPORT_BLOCKED_LIVE_API",
        "scheduler_payload": "EXPORT_BLOCKED_SCHEDULER",
        "calibration_signal_payload": "EXPORT_BLOCKED_CALIBRATION_SIGNAL",
        "budget_optimization_payload": "EXPORT_BLOCKED_BUDGET_OPTIMIZATION",
        "decisioning_payload": "EXPORT_BLOCKED_PRODUCTION_DECISIONING",
    }
    if export_type in blocked_mode_map:
        decision = blocked_mode_map[export_type]
        return (
            ExportResult(
                request.request_id,
                request.row_id,
                request.request_type,
                decision,  # type: ignore[arg-type]
                False,
                audit_id,
                "blocked",
                {f"{export_type}_blocked": True},
                f"Export type {export_type} forbidden",
            ),
            None,
        )

    if role in ("calibration_signal", "calibrationsignal"):
        return (
            ExportResult(
                request.request_id,
                request.row_id,
                request.request_type,
                "EXPORT_BLOCKED_CALIBRATION_SIGNAL",
                False,
                audit_id,
                "blocked",
                {},
                "CalibrationSignal export not authorized",
            ),
            None,
        )
    if role in ("live_api", "api"):
        return (
            ExportResult(
                request.request_id,
                request.row_id,
                request.request_type,
                "EXPORT_BLOCKED_LIVE_API",
                False,
                audit_id,
                "blocked",
                {},
                "Live API export not authorized",
            ),
            None,
        )
    if role in ("scheduler",):
        return (
            ExportResult(
                request.request_id,
                request.row_id,
                request.request_type,
                "EXPORT_BLOCKED_SCHEDULER",
                False,
                audit_id,
                "blocked",
                {},
                "Scheduler export not authorized",
            ),
            None,
        )
    if role in ("production_decisioning", "production"):
        return (
            ExportResult(
                request.request_id,
                request.row_id,
                request.request_type,
                "EXPORT_BLOCKED_PRODUCTION_DECISIONING",
                False,
                audit_id,
                "blocked",
                {},
                "Production decisioning export not authorized",
            ),
            None,
        )
    if role in ("budget_optimization_input", "budget"):
        return (
            ExportResult(
                request.request_id,
                request.row_id,
                request.request_type,
                "EXPORT_BLOCKED_BUDGET_OPTIMIZATION",
                False,
                audit_id,
                "blocked",
                {},
                "Budget optimization export not authorized",
            ),
            None,
        )

    row_id = request.row_id
    known_rows = (
        frozenset(renderer_contracts.keys())
        | PROMOTED_ROWS
        | DIAGNOSTIC_ONLY_ROWS
        | NULL_MONITOR_ROWS
        | frozenset((promotion.get("promotion_decisions") or {}).keys())
    )

    if row_id not in known_rows:
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_UNKNOWN_ROW",
                False,
                audit_id,
                "blocked",
                {"unknown_row": True},
                f"Unknown row: {row_id}",
            ),
            None,
        )

    if request.request_type == "unsanitized_payload" or request.payload_type == "unsanitized":
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_UNSANITIZED_PAYLOAD",
                False,
                audit_id,
                "blocked",
                {"unsanitized_payload": True},
                "Unsanitized live measurement payload blocked",
            ),
            None,
        )

    if request.request_type == "missing_audit_trail" or not request.include_audit_trail:
        if row_id in PROMOTED_ROWS:
            return (
                ExportResult(
                    request.request_id,
                    row_id,
                    request.request_type,
                    "EXPORT_BLOCKED_MISSING_AUDIT_TRAIL",
                    False,
                    audit_id,
                    "blocked",
                    {"audit_trail_missing": True},
                    "Audit trail required for export",
                ),
                None,
            )

    if row_id in DIAGNOSTIC_ONLY_ROWS:
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_DIAGNOSTIC_ONLY",
                False,
                audit_id,
                "blocked",
                {"diagnostic_only": True},
                f"{row_id} is diagnostic-only",
            ),
            None,
        )

    if row_id in NULL_MONITOR_ROWS and request.request_type == "causal_trustreport":
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
                False,
                audit_id,
                "blocked",
                {"null_monitor_causal_reuse": True},
                "Null-monitor path cannot export causal TrustReport",
            ),
            None,
        )

    if row_id == "DCM-006":
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_NOT_PROMOTED",
                False,
                audit_id,
                "blocked",
                {"multicell_global_blocked": True},
                "DCM-006 global/winner/pooled export blocked",
            ),
            None,
        )

    if row_id == "DCM-008" or request.claim_type == "aggregate_stratified":
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_DIAGNOSTIC_ONLY",
                False,
                audit_id,
                "blocked",
                {"stratified_aggregate_blocked": True},
                "DCM-008 aggregate stratified export blocked",
            ),
            None,
        )

    if row_id not in promoted or row_id not in dry_accepted:
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_NOT_PROMOTED",
                False,
                audit_id,
                "blocked",
                {"not_promoted": True},
                f"{row_id} not promoted or dry-run approved",
            ),
            None,
        )

    row_contract = renderer_contracts.get(row_id)
    if not row_contract:
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_MISSING_CONTRACT",
                False,
                audit_id,
                "blocked",
                {"contract_missing": True},
                "Renderer contract missing",
            ),
            None,
        )

    if request.request_type == "missing_warnings" or not request.include_warnings:
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_MISSING_CONTRACT",
                False,
                audit_id,
                "blocked",
                {"warnings_missing": True},
                "Required warnings missing",
            ),
            None,
        )

    if row_id == "DCM-004" and (
        request.request_type == "missing_diagnostics" or not request.include_diagnostics
    ):
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_MISSING_DIAGNOSTICS",
                False,
                audit_id,
                "blocked",
                {"diagnostics_missing": True},
                "Parallel-trends diagnostics required for DCM-004",
            ),
            None,
        )

    geom = request.geometry or row_contract.get("allowed_geometry")
    blocked_geom = set(row_contract.get("blocked_geometry") or [])
    if geom in blocked_geom or request.request_type == "unsupported_geometry":
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_UNSUPPORTED_GEOMETRY",
                False,
                audit_id,
                "blocked",
                {"unsupported_geometry": True},
                f"Geometry {geom} blocked",
            ),
            None,
        )

    if row_id == "DCM-004" and request.request_type == "unsupported_timing":
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_UNSUPPORTED_GEOMETRY",
                False,
                audit_id,
                "blocked",
                {"unsupported_timing": True},
                "Unsupported timing for DCM-004",
            ),
            None,
        )

    manifest_only = request.payload_type == "manifest_only" or request.request_type == "manifest_only"
    sanitized_payload = _build_sanitized_payload(request=request, manifest_only=manifest_only)

    if not _payload_is_sanitized(sanitized_payload):
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_UNSANITIZED_PAYLOAD",
                False,
                audit_id,
                "blocked",
                {"payload_not_sanitized": True},
                "Payload failed sanitization checks",
            ),
            None,
        )

    export_id = f"export-{request.request_id}"
    export_body = _build_export_contract(
        export_id=export_id,
        row_contract=row_contract,
        request=request,
        sanitized_payload=sanitized_payload,
        include_audit=request.include_audit_trail,
    )

    if not _contract_complete(export_body):
        return (
            ExportResult(
                request.request_id,
                row_id,
                request.request_type,
                "EXPORT_BLOCKED_MISSING_CONTRACT",
                False,
                audit_id,
                "blocked",
                {"export_contract_incomplete": True},
                "Export contract incomplete",
            ),
            None,
        )

    if manifest_only:
        decision: ExportDecision = "EXPORT_ACCEPTED_MANIFEST_ONLY"
    elif request.payload_type in ("placeholder", "none"):
        decision = "EXPORT_ACCEPTED_PLACEHOLDER_RESEARCH_MODE"
    elif request.payload_type == "synthetic":
        decision = "EXPORT_ACCEPTED_RESEARCH_MODE"
    else:
        decision = "EXPORT_ACCEPTED_PLACEHOLDER_RESEARCH_MODE"

    gates = {
        "row_promoted": row_id in promoted,
        "dry_run_approved": row_id in dry_accepted,
        "contract_complete": True,
        "warnings_present": bool(ROW_EXPORT_WARNINGS.get(row_id)),
        "sanitized_payload": True,
        "research_mode_only": True,
        "live_api_blocked": True,
        "scheduler_blocked": True,
        "calibration_signal_blocked": True,
    }

    export_body["export_status"] = decision
    export_body["export_decision"] = decision
    export_contracts[export_id] = export_body

    return (
        ExportResult(
            request.request_id,
            row_id,
            request.request_type,
            decision,
            True,
            audit_id,
            "accepted",
            gates,
            "Research-mode TrustReport export accepted",
            export_body["content_hash"],
        ),
        export_body,
    )


def _build_export_requests() -> list[ExportRequest]:
    return [
        # Positive
        ExportRequest(
            "pos-dcm001-placeholder",
            "DCM-001",
            "placeholder_export",
            "research_mode_artifact_export",
            "restricted_trustreport_research_only",
            payload_type="placeholder",
        ),
        ExportRequest(
            "pos-dcm004-placeholder",
            "DCM-004",
            "placeholder_export",
            "research_mode_artifact_export",
            "restricted_trustreport_research_only",
            payload_type="placeholder",
        ),
        ExportRequest(
            "pos-dcm001-synthetic",
            "DCM-001",
            "synthetic_export",
            "research_mode_artifact_export",
            "restricted_trustreport_research_only",
            payload_type="synthetic",
        ),
        ExportRequest(
            "pos-dcm004-synthetic",
            "DCM-004",
            "synthetic_export",
            "research_mode_artifact_export",
            "restricted_trustreport_research_only",
            payload_type="synthetic",
        ),
        ExportRequest(
            "pos-dcm001-manifest",
            "DCM-001",
            "manifest_only",
            "research_mode_artifact_export",
            "restricted_trustreport_research_only",
            payload_type="manifest_only",
        ),
        ExportRequest(
            "pos-dcm004-manifest",
            "DCM-004",
            "manifest_only",
            "research_mode_artifact_export",
            "restricted_trustreport_research_only",
            payload_type="manifest_only",
        ),
        # Negative contract/geometry
        ExportRequest(
            "neg-dcm001-missing-warnings",
            "DCM-001",
            "missing_warnings",
            "research_mode_artifact_export",
            "restricted_trustreport_research_only",
            include_warnings=False,
        ),
        ExportRequest(
            "neg-dcm004-missing-diagnostics",
            "DCM-004",
            "missing_diagnostics",
            "research_mode_artifact_export",
            "restricted_trustreport_research_only",
            include_diagnostics=False,
        ),
        ExportRequest(
            "neg-dcm001-bad-geometry",
            "DCM-001",
            "unsupported_geometry",
            "research_mode_artifact_export",
            "restricted_trustreport_research_only",
            geometry="aggregate_1x1",
        ),
        ExportRequest(
            "neg-dcm004-bad-timing",
            "DCM-004",
            "unsupported_timing",
            "research_mode_artifact_export",
            "restricted_trustreport_research_only",
            geometry="parallel_trends_violation",
        ),
        # Negative excluded rows
        ExportRequest("neg-brb", "DCM-005-BRB", "causal_trustreport", "research_mode_artifact_export", "restricted_trustreport_research_only"),
        ExportRequest("neg-kfold", "DCM-005-KFOLD", "causal_trustreport", "research_mode_artifact_export", "restricted_trustreport_research_only"),
        ExportRequest("neg-placebo", "DCM-005-PLACEBO", "causal_trustreport", "research_mode_artifact_export", "restricted_trustreport_research_only"),
        ExportRequest("neg-dcm006-global", "DCM-006", "global_claim", "research_mode_artifact_export", "restricted_trustreport_research_only", claim_type="global"),
        ExportRequest("neg-dcm008-aggregate", "DCM-008", "aggregate_stratified", "research_mode_artifact_export", "restricted_trustreport_research_only", claim_type="aggregate_stratified"),
        # Boundary blocks
        ExportRequest("neg-cal", "DCM-001", "calibration", "calibration_signal_payload", "calibration_signal"),
        ExportRequest("neg-live", "DCM-004", "live_api", "live_api_payload", "live_api"),
        ExportRequest("neg-scheduler", "DCM-001", "scheduler", "scheduler_payload", "scheduler"),
        ExportRequest("neg-prod", "DCM-004", "production", "decisioning_payload", "production_decisioning"),
        ExportRequest("neg-budget", "DCM-001", "budget", "budget_optimization_payload", "budget_optimization_input"),
        ExportRequest("neg-unknown", "DCM-999", "unknown", "research_mode_artifact_export", "restricted_trustreport_research_only"),
        ExportRequest(
            "neg-unsanitized",
            "DCM-001",
            "unsanitized_payload",
            "research_mode_artifact_export",
            "restricted_trustreport_research_only",
            payload_type="unsanitized",
        ),
        ExportRequest(
            "neg-missing-audit",
            "DCM-004",
            "missing_audit_trail",
            "research_mode_artifact_export",
            "restricted_trustreport_research_only",
            include_audit_trail=False,
        ),
    ]


def build_trustreport_research_mode_artifact_export_001() -> dict[str, Any]:
    inputs = _load_inputs()
    renderer = inputs["renderer_summary"]
    dry_run = inputs["integration_dry_run"]
    promotion = inputs["downstream_promotion"]
    registry = load_registry()

    if renderer.get("governance_verdict") != "trustreport_research_mode_renderer_passed":
        raise ValueError("Renderer artifact must have passed before export")
    if dry_run.get("governance_verdict") != "trustreport_integration_dry_run_passed":
        raise ValueError("Dry-run artifact must have passed before export")
    if promotion.get("governance_verdict") != "trustreport_downstream_restricted_row_promotion_approved":
        raise ValueError("Promotion artifact must approve restricted rows")

    renderer_contracts = dict(renderer.get("renderer_contracts") or {})
    export_contracts: dict[str, dict[str, Any]] = {}
    warning_contracts: dict[str, list[str]] = {}
    restriction_contracts: dict[str, dict[str, Any]] = {}

    for row_id in PROMOTED_ROWS:
        if row_id not in renderer_contracts:
            raise KeyError(f"Renderer contract missing for {row_id}")
        warning_contracts[row_id] = ROW_EXPORT_WARNINGS[row_id]
        restriction_contracts[row_id] = {
            "blocked_roles": renderer_contracts[row_id].get("blocked_roles"),
            "blocked_geometry": renderer_contracts[row_id].get("blocked_geometry"),
        }

    requests = _build_export_requests()
    results: list[ExportResult] = []
    export_examples: dict[str, dict[str, Any]] = {}
    audit_records: list[dict[str, Any]] = []
    content_hashes: dict[str, str] = {}
    sanitization_results: list[dict[str, Any]] = []

    for req in requests:
        result, exported = _evaluate_export(
            req,
            export_contracts=export_contracts,
            renderer_contracts=renderer_contracts,
            promotion=promotion,
            dry_run=dry_run,
        )
        results.append(result)
        if exported is not None:
            export_examples[req.request_id] = exported
            content_hashes[req.request_id] = exported["content_hash"]
            sanitization_results.append(
                {
                    "request_id": req.request_id,
                    "row_id": req.row_id,
                    "sanitized": _payload_is_sanitized(exported["sanitized_payload"]),
                    "measurement_label": exported["sanitized_payload"].get("label"),
                    "content_hash": exported["content_hash"],
                }
            )
        audit_records.append(
            {
                "audit_record_id": result.audit_record_id,
                "request_id": req.request_id,
                "row_id": req.row_id,
                "decision": result.decision,
                "accepted": result.accepted,
                "export_type": req.export_type,
                "research_mode_only": True,
                "live_api_authorized": False,
                "scheduler_authorized": False,
                "content_hash": result.content_hash,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    accepted = [r for r in results if r.accepted]
    blocked = [r for r in results if not r.accepted]
    accepted_restricted = [
        r
        for r in results
        if r.decision
        in (
            "EXPORT_ACCEPTED_RESEARCH_MODE",
            "EXPORT_ACCEPTED_PLACEHOLDER_RESEARCH_MODE",
            "EXPORT_ACCEPTED_MANIFEST_ONLY",
        )
    ]
    accepted_row_ids = {r.row_id for r in accepted_restricted}

    for r in accepted_restricted:
        if r.row_id not in PROMOTED_ROWS:
            raise ValueError(f"Unexpected export acceptance for {r.row_id}")

    contracts_complete = all(
        _contract_complete(c) for c in export_contracts.values()
    )

    positive_pass = all(
        r.decision
        in (
            "EXPORT_ACCEPTED_RESEARCH_MODE",
            "EXPORT_ACCEPTED_PLACEHOLDER_RESEARCH_MODE",
            "EXPORT_ACCEPTED_MANIFEST_ONLY",
        )
        for r in results
        if r.request_id.startswith("pos-")
    )
    negative_pass = all(not r.accepted for r in results if r.request_id.startswith("neg-"))
    sanitization_pass = all(s["sanitized"] for s in sanitization_results)

    if contracts_complete and positive_pass and negative_pass and sanitization_pass:
        verdict: GovernanceVerdict = "trustreport_research_mode_artifact_export_passed"
        next_artifact = "TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001"
    elif not contracts_complete:
        verdict = "trustreport_research_mode_artifact_export_blocked_missing_contract"
        next_artifact = "TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001"
    else:
        verdict = "trustreport_research_mode_artifact_export_failed"
        next_artifact = "TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001"

    deferred = [
        inv["investigation_id"]
        for inv in registry.get("investigations", [])
        if inv.get("status") == "DEFERRED_WITH_TRIGGER"
    ]

    export_manifest_metadata = {
        req_id: export_examples[req_id]["export_manifest"]
        for req_id in export_examples
    }

    handoff = build_investigation_handoff(
        follow_up_issues=[],
        resolved_issues=[],
        terminal_dispositions=[],
        next_artifact=next_artifact,
    )

    limitations = [
        "This artifact exports restricted row-level TrustReport research-mode artifacts only.",
        "It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, budget optimization, or global platform rollout.",
        "Only DCM-001 and DCM-004 are accepted for sanitized research-mode artifact export.",
        "All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.",
        "No unsanitized live measurement payloads are exported; placeholders, synthetic dry-run payloads, and manifest-only exports are explicitly labeled.",
    ]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "input_artifacts": inputs["_paths"],
        "export_scope": sorted(EXPORT_SCOPE),
        "export_requests": [r.to_dict() for r in requests],
        "accepted_exports": [r.to_dict() for r in accepted],
        "blocked_exports": [r.to_dict() for r in blocked],
        "accepted_rows": sorted(accepted_row_ids),
        "blocked_rows": sorted({r.row_id for r in blocked}),
        "export_contracts": {k: v for k, v in export_contracts.items()},
        "export_manifest_metadata": export_manifest_metadata,
        "content_hashes": content_hashes,
        "warning_contracts": warning_contracts,
        "restriction_contracts": restriction_contracts,
        "audit_records": audit_records,
        "negative_control_results": [r.to_dict() for r in results if r.request_id.startswith("neg-")],
        "sanitization_results": sanitization_results,
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
            "blocking_for_export": [],
        },
        "governance_verdict": verdict,
        "limitations": limitations,
        "next_artifact": next_artifact,
        "investigation_handoff": handoff,
        "verdict": verdict,
        "contracts_complete": contracts_complete,
        "dcm001_export_result": next(
            (r.to_dict() for r in results if r.request_id == "pos-dcm001-placeholder"),
            {},
        ),
        "dcm004_export_result": next(
            (r.to_dict() for r in results if r.request_id == "pos-dcm004-placeholder"),
            {},
        ),
        "export_results": [r.to_dict() for r in results],
        "exported_artifact_schema": {
            "required_fields": list(EXPORT_CONTRACT_FIELDS),
            "banners": EXPORT_BANNER,
            "placeholder_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED",
            "synthetic_label": "SYNTHETIC_DRY_RUN_PAYLOAD",
            "manifest_only_label": "MANIFEST_ONLY_EXPORT",
        },
        "manifest_schema": {
            "required_fields": [
                "export_id",
                "row_id",
                "export_type",
                "schema_version",
                "content_hash",
                "sanitized",
                "research_mode_only",
                "measurement_label",
                "created_at",
            ],
        },
        "_export_examples_full": export_examples,
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
        revisit_trigger="After TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001",
        decision_checkpoint="TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001",
        next_artifact=payload.get("next_artifact"),
    )
    lines = [
        f"# {_ARTIFACT_ID} Report",
        "",
        "## 1. Executive summary",
        "",
        "This artifact exports restricted row-level TrustReport research-mode artifacts only.",
        "It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, budget optimization, or global platform rollout.",
        "Only DCM-001 and DCM-004 are accepted for sanitized research-mode artifact export.",
        "All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.",
        "",
        f"**Governance verdict:** `{payload.get('governance_verdict')}`",
        f"**Accepted rows:** {payload.get('accepted_rows')}",
        "",
        "## 2. Scope",
        "",
        "Sanitized research-mode artifact export for DCM-001 (SCM+JK) and DCM-004 (DID+bootstrap).",
        "",
        "## 3. Non-goals",
        "",
        "- No live API, scheduler, production automation",
        "- No CalibrationSignal, budget optimization, recommendations",
        "- No new statistical simulations or algorithm changes",
        "- No unsanitized live measurement payloads",
        "",
        "## 4. Input artifacts",
        "",
        json.dumps(payload.get("input_artifacts"), indent=2),
        "",
        "## 5. Research-mode artifact export contract",
        "",
        json.dumps(list(EXPORT_CONTRACT_FIELDS), indent=2),
        "",
        "## 6. Exported artifact schema",
        "",
        json.dumps(payload.get("exported_artifact_schema"), indent=2),
        "",
        "## 7. Manifest schema",
        "",
        json.dumps(payload.get("manifest_schema"), indent=2),
        "",
        "## 8. Sanitization rules",
        "",
        "Accepted exports must not include live data, raw identifiers, production recommendations, "
        "budget allocation, CalibrationSignal fields, scheduler/API payloads, or hidden authorization flags. "
        "Synthetic payloads require `synthetic: true` and `non_decisioning: true`. "
        "Placeholder payloads use `NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED`.",
        "",
        "## 9. DCM-001 export result",
        "",
        json.dumps(payload.get("dcm001_export_result"), indent=2),
        "",
        "## 10. DCM-004 export result",
        "",
        json.dumps(payload.get("dcm004_export_result"), indent=2),
        "",
        "## 11. Placeholder export behavior",
        "",
        "Placeholder exports use `NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED` with null point/interval.",
        "",
        "## 12. Synthetic export behavior",
        "",
        "Synthetic exports labeled `SYNTHETIC_DRY_RUN_PAYLOAD` with `synthetic: true` and `non_decisioning: true`.",
        "",
        "## 13. Manifest-only export behavior",
        "",
        "Manifest-only exports include metadata and content hash without measurement payload.",
        "",
        "## 14. Negative-control export requests",
        "",
        json.dumps(payload.get("negative_control_results"), indent=2),
        "",
        "## 15. Blocked diagnostic-only rows",
        "",
        "DCM-002, DCM-005-BRB, DCM-005-KFOLD, DCM-008 — EXPORT_BLOCKED_DIAGNOSTIC_ONLY",
        "",
        "## 16. Blocked null-monitor causal reuse",
        "",
        "DCM-005-PLACEBO causal export — EXPORT_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
        "",
        "## 17. Blocked multi-cell/global claims",
        "",
        "DCM-006 — EXPORT_BLOCKED_NOT_PROMOTED",
        "",
        "## 18. Blocked stratified aggregate claims",
        "",
        "DCM-008 aggregate — EXPORT_BLOCKED_DIAGNOSTIC_ONLY",
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
        "## 25. Content-hash verification",
        "",
        json.dumps(payload.get("content_hashes"), indent=2),
        "",
        "## 26. Open investigation check",
        "",
        json.dumps(payload.get("open_investigation_check"), indent=2),
        "",
        "## 27. Governance verdict",
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


def _write_local_exports(
    export_dir: Path,
    examples: dict[str, dict[str, Any]],
    *,
    overwrite: bool,
) -> None:
    if export_dir.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing export dir: {export_dir}")
    export_dir.mkdir(parents=True, exist_ok=True)
    for req_id, body in examples.items():
        path = export_dir / f"{req_id}.json"
        _atomic_write(path, json.dumps(body, indent=2, sort_keys=False) + "\n", overwrite=True)


def _write_committed_manifest(
    manifest_path: Path,
    manifest_metadata: dict[str, Any],
    *,
    overwrite: bool,
) -> None:
    manifest_doc = {
        "artifact_id": _ARTIFACT_ID,
        "schema_version": _SCHEMA_VERSION,
        "research_mode_only": True,
        "sanitized": True,
        "exports": manifest_metadata,
        "banners": EXPORT_BANNER,
    }
    _atomic_write(
        manifest_path,
        json.dumps(manifest_doc, indent=2, sort_keys=False) + "\n",
        overwrite=overwrite,
    )


def write_summary(
    summary_path: Path,
    *,
    overwrite: bool = False,
    report_path: Path | None = None,
    export_output_path: Path | None = None,
    manifest_path: Path | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    payload = build_trustreport_research_mode_artifact_export_001()
    full_examples = payload.pop("_export_examples_full", {})

    if export_output_path is not None:
        _write_local_exports(export_output_path, full_examples, overwrite=overwrite)

    if manifest_path is not None:
        _write_committed_manifest(
            manifest_path,
            payload.get("export_manifest_metadata") or {},
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
        for rec in payload.get("export_results") or []:
            if rec.get("row_id") in DIAGNOSTIC_ONLY_ROWS | {"DCM-006", "DCM-008"}:
                if rec.get("decision", "").startswith("EXPORT_ACCEPTED"):
                    raise RuntimeError(f"Excluded row {rec['row_id']} must not export")
        for s in payload.get("sanitization_results") or []:
            if not s.get("sanitized"):
                raise RuntimeError(f"Unsanitized export: {s.get('request_id')}")

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
    parser.add_argument("--export-output-local", type=Path, default=_DEFAULT_EXPORT_OUTPUT)
    parser.add_argument("--manifest-output", type=Path, default=_DEFAULT_MANIFEST)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    write_summary(
        args.summary_output,
        overwrite=args.overwrite,
        report_path=args.report_output,
        export_output_path=args.export_output_local,
        manifest_path=args.manifest_output,
        strict=args.strict,
    )


if __name__ == "__main__":
    main()
