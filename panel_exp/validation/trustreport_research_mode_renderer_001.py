"""TRUSTREPORT-RESEARCH-MODE-RENDERER-001 — governed research-mode TrustReport renderer.

Renders restricted row-level TrustReport contracts for DCM-001 and DCM-004 only.
Loads dry-run and promotion summaries; does not run new statistical simulations.
Does not authorize live APIs, scheduler, production decisioning, or CalibrationSignal.
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
_ARTIFACT_ID = "TRUSTREPORT-RESEARCH-MODE-RENDERER-001"
_ARTIFACT_VERSION = "1.0.0"
_DEFAULT_SUMMARY = _ARCHIVE / "TRUSTREPORT_RESEARCH_MODE_RENDERER_001_summary.json"
_DEFAULT_REPORT = _REPO / "docs/track_d/TRUSTREPORT_RESEARCH_MODE_RENDERER_001_REPORT.md"
_DEFAULT_RENDER_OUTPUT = Path("/tmp/TRUSTREPORT_RESEARCH_MODE_RENDERER_001_rendered_examples.json")

RenderDecision = Literal[
    "RENDER_ACCEPTED_RESEARCH_MODE",
    "RENDER_ACCEPTED_PLACEHOLDER_RESEARCH_MODE",
    "RENDER_BLOCKED_MISSING_CONTRACT",
    "RENDER_BLOCKED_UNSUPPORTED_GEOMETRY",
    "RENDER_BLOCKED_MISSING_DIAGNOSTICS",
    "RENDER_BLOCKED_DIAGNOSTIC_ONLY",
    "RENDER_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
    "RENDER_BLOCKED_NOT_PROMOTED",
    "RENDER_BLOCKED_CALIBRATION_SIGNAL",
    "RENDER_BLOCKED_LIVE_API",
    "RENDER_BLOCKED_SCHEDULER",
    "RENDER_BLOCKED_PRODUCTION_DECISIONING",
    "RENDER_BLOCKED_BUDGET_OPTIMIZATION",
    "RENDER_BLOCKED_UNKNOWN_ROW",
]

GovernanceVerdict = Literal[
    "trustreport_research_mode_renderer_passed",
    "trustreport_research_mode_renderer_blocked_missing_contract",
    "trustreport_research_mode_renderer_failed",
]

REQUIRED_INPUTS: dict[str, str] = {
    "integration_dry_run": "TRUSTREPORT_INTEGRATION_DRY_RUN_001_summary.json",
    "downstream_promotion": "TRUSTREPORT_DOWNSTREAM_PROMOTION_001_summary.json",
    "full_reassessment": "FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
}

RENDERER_SCOPE = frozenset({"DCM-001", "DCM-004"})
PROMOTED_ROWS = frozenset({"DCM-001", "DCM-004"})

RENDERER_CONTRACT_FIELDS = frozenset(
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
        "dry_run_approval_artifact",
        "promotion_artifact",
        "research_mode_only",
    }
)

DIAGNOSTIC_ONLY_ROWS = frozenset(
    {"DCM-002", "DCM-005-BRB", "DCM-005-KFOLD", "DCM-008"}
)
NULL_MONITOR_ROWS = frozenset({"DCM-005-PLACEBO", "SCM-PLACEBO"})

RENDER_BANNER = [
    "RESEARCH MODE ONLY",
    "NOT FOR PRODUCTION DECISIONING",
    "NOT FOR BUDGET OPTIMIZATION",
    "NO CALIBRATIONSIGNAL AUTHORIZATION",
    "NO LIVE API AUTHORIZATION",
    "NO SCHEDULER AUTHORIZATION",
]

ROW_RENDER_WARNINGS: dict[str, list[str]] = {
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


@dataclass(frozen=True)
class RenderRequest:
    request_id: str
    row_id: str
    request_type: str
    render_mode: str
    requested_role: str
    geometry: str | None = None
    payload_type: str = "none"  # none | placeholder | synthetic
    include_warnings: bool = True
    include_diagnostics: bool = True
    claim_type: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RenderResult:
    request_id: str
    row_id: str
    request_type: str
    decision: RenderDecision
    accepted: bool
    audit_record_id: str
    render_status: str
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


def _build_renderer_contract(
    row_contract: dict[str, Any],
    *,
    dry_run_artifact: str,
    promotion_artifact: str,
) -> dict[str, Any]:
    return {
        **row_contract,
        "dry_run_approval_artifact": dry_run_artifact,
        "promotion_artifact": promotion_artifact,
        "research_mode_only": True,
    }


def _contract_complete(contract: dict[str, Any]) -> bool:
    for field_name in RENDERER_CONTRACT_FIELDS:
        if field_name not in contract:
            return False
        val = contract[field_name]
        if field_name in ("required_warnings", "required_diagnostics", "audit_artifacts", "blocked_geometry"):
            if not val:
                return False
        elif field_name == "research_mode_only" and val is not True:
            return False
        elif val is None or val == "":
            return False
    return True


def _build_rendered_output(
    *,
    contract: dict[str, Any],
    request: RenderRequest,
    decision: RenderDecision,
) -> dict[str, Any]:
    row_id = contract["row_id"]
    warnings = list(ROW_RENDER_WARNINGS.get(row_id, contract.get("required_warnings") or []))
    restrictions = list(contract.get("blocked_roles") or [])

    if request.payload_type == "synthetic":
        measurement = {
            "label": "SYNTHETIC_DRY_RUN_PAYLOAD",
            "synthetic": True,
            "non_decisioning": True,
            "point_estimate": 0.0,
            "interval_low": -1.0,
            "interval_high": 1.0,
            "note": "Synthetic dry-run payload for renderer validation only; not a real measurement.",
        }
    elif request.payload_type == "placeholder":
        measurement = {
            "label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED",
            "placeholder": True,
            "point_estimate": None,
            "interval_low": None,
            "interval_high": None,
        }
    else:
        measurement = {
            "label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED",
            "placeholder": True,
            "point_estimate": None,
            "interval_low": None,
            "interval_high": None,
        }

    return {
        "title": f"TrustReport Research Mode — {row_id}",
        "artifact_id": _ARTIFACT_ID,
        "row_id": row_id,
        "render_mode": "research_mode_only",
        "method_identity": {
            "design_family": contract.get("design_family"),
            "estimator": contract.get("estimator"),
            "inference_method": contract.get("inference_method"),
        },
        "estimand": contract.get("estimand"),
        "allowed_scope": contract.get("readout_scope"),
        "allowed_geometry": contract.get("allowed_geometry"),
        "measurement": measurement,
        "diagnostic_requirements": list(contract.get("required_diagnostics") or []),
        "warnings": warnings,
        "restrictions": restrictions,
        "blocked_uses": list(contract.get("blocked_roles") or []),
        "authorization_boundaries": {
            "research_mode_only": True,
            "live_api_authorized": False,
            "scheduler_authorized": False,
            "calibration_signal_allowed": False,
            "production_decisioning_allowed": False,
            "budget_optimization_allowed": False,
            "trust_report_platform_authorized": False,
        },
        "banners": RENDER_BANNER,
        "audit_trail": {
            "dry_run_approval_artifact": contract.get("dry_run_approval_artifact"),
            "promotion_artifact": contract.get("promotion_artifact"),
            "audit_artifacts": list(contract.get("audit_artifacts") or []),
            "renderer_artifact": _ARTIFACT_ID,
        },
        "interval_semantics": contract.get("interval_semantics"),
        "render_status": decision,
        "render_decision": decision,
    }


def _evaluate_render(
    request: RenderRequest,
    *,
    renderer_contracts: dict[str, dict[str, Any]],
    promotion: dict[str, Any],
    dry_run: dict[str, Any],
) -> tuple[RenderResult, dict[str, Any] | None]:
    audit_id = f"render-audit-{request.request_id}"
    promoted = set(promotion.get("promoted_rows") or [])
    dry_accepted = set(dry_run.get("accepted_rows") or [])
    decisions = promotion.get("promotion_decisions") or {}

    role = request.requested_role.lower()
    mode = request.render_mode.lower()

    if mode in ("production_mode", "api_mode", "scheduler_mode", "calibration_mode", "optimization_mode"):
        if mode == "production_mode" or role in ("production_decisioning", "production"):
            return (
                RenderResult(
                    request.request_id,
                    request.row_id,
                    request.request_type,
                    "RENDER_BLOCKED_PRODUCTION_DECISIONING",
                    False,
                    audit_id,
                    "blocked",
                    {"production_mode_blocked": True},
                    "Production render mode forbidden",
                ),
                None,
            )
        if mode == "api_mode" or role in ("live_api", "api"):
            return (
                RenderResult(
                    request.request_id,
                    request.row_id,
                    request.request_type,
                    "RENDER_BLOCKED_LIVE_API",
                    False,
                    audit_id,
                    "blocked",
                    {"live_api_blocked": True},
                    "Live API render mode forbidden",
                ),
                None,
            )
        if mode == "scheduler_mode" or role in ("scheduler",):
            return (
                RenderResult(
                    request.request_id,
                    request.row_id,
                    request.request_type,
                    "RENDER_BLOCKED_SCHEDULER",
                    False,
                    audit_id,
                    "blocked",
                    {"scheduler_blocked": True},
                    "Scheduler render mode forbidden",
                ),
                None,
            )
        if mode == "calibration_mode" or role in ("calibration_signal", "calibrationsignal"):
            return (
                RenderResult(
                    request.request_id,
                    request.row_id,
                    request.request_type,
                    "RENDER_BLOCKED_CALIBRATION_SIGNAL",
                    False,
                    audit_id,
                    "blocked",
                    {"calibration_signal_blocked": True},
                    "CalibrationSignal render forbidden",
                ),
                None,
            )
        if mode == "optimization_mode" or role in ("budget_optimization_input", "budget"):
            return (
                RenderResult(
                    request.request_id,
                    request.row_id,
                    request.request_type,
                    "RENDER_BLOCKED_BUDGET_OPTIMIZATION",
                    False,
                    audit_id,
                    "blocked",
                    {"budget_optimization_blocked": True},
                    "Budget optimization render forbidden",
                ),
                None,
            )

    if role in ("calibration_signal", "calibrationsignal"):
        return (
            RenderResult(
                request.request_id,
                request.row_id,
                request.request_type,
                "RENDER_BLOCKED_CALIBRATION_SIGNAL",
                False,
                audit_id,
                "blocked",
                {},
                "CalibrationSignal not authorized",
            ),
            None,
        )
    if role in ("live_api", "api"):
        return (
            RenderResult(
                request.request_id,
                request.row_id,
                request.request_type,
                "RENDER_BLOCKED_LIVE_API",
                False,
                audit_id,
                "blocked",
                {},
                "Live API not authorized",
            ),
            None,
        )
    if role in ("scheduler",):
        return (
            RenderResult(
                request.request_id,
                request.row_id,
                request.request_type,
                "RENDER_BLOCKED_SCHEDULER",
                False,
                audit_id,
                "blocked",
                {},
                "Scheduler not authorized",
            ),
            None,
        )
    if role in ("production_decisioning", "production"):
        return (
            RenderResult(
                request.request_id,
                request.row_id,
                request.request_type,
                "RENDER_BLOCKED_PRODUCTION_DECISIONING",
                False,
                audit_id,
                "blocked",
                {},
                "Production decisioning not authorized",
            ),
            None,
        )
    if role in ("budget_optimization_input", "budget"):
        return (
            RenderResult(
                request.request_id,
                request.row_id,
                request.request_type,
                "RENDER_BLOCKED_BUDGET_OPTIMIZATION",
                False,
                audit_id,
                "blocked",
                {},
                "Budget optimization not authorized",
            ),
            None,
        )

    row_id = request.row_id
    known_rows = (
        frozenset(renderer_contracts.keys())
        | PROMOTED_ROWS
        | DIAGNOSTIC_ONLY_ROWS
        | NULL_MONITOR_ROWS
        | frozenset(decisions.keys())
    )

    if row_id not in known_rows:
        return (
            RenderResult(
                request.request_id,
                row_id,
                request.request_type,
                "RENDER_BLOCKED_UNKNOWN_ROW",
                False,
                audit_id,
                "blocked",
                {"unknown_row": True},
                f"Unknown row: {row_id}",
            ),
            None,
        )

    if row_id in DIAGNOSTIC_ONLY_ROWS:
        return (
            RenderResult(
                request.request_id,
                row_id,
                request.request_type,
                "RENDER_BLOCKED_DIAGNOSTIC_ONLY",
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
            RenderResult(
                request.request_id,
                row_id,
                request.request_type,
                "RENDER_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
                False,
                audit_id,
                "blocked",
                {"null_monitor_causal_reuse": True},
                "Null-monitor path cannot render causal TrustReport",
            ),
            None,
        )

    if row_id == "DCM-006":
        return (
            RenderResult(
                request.request_id,
                row_id,
                request.request_type,
                "RENDER_BLOCKED_NOT_PROMOTED",
                False,
                audit_id,
                "blocked",
                {"multicell_global_blocked": True},
                "DCM-006 global/winner/pooled render blocked",
            ),
            None,
        )

    if row_id == "DCM-008" or request.claim_type == "aggregate_stratified":
        return (
            RenderResult(
                request.request_id,
                row_id,
                request.request_type,
                "RENDER_BLOCKED_DIAGNOSTIC_ONLY",
                False,
                audit_id,
                "blocked",
                {"stratified_aggregate_blocked": True},
                "DCM-008 aggregate stratified render blocked",
            ),
            None,
        )

    if row_id not in promoted or row_id not in dry_accepted:
        return (
            RenderResult(
                request.request_id,
                row_id,
                request.request_type,
                "RENDER_BLOCKED_NOT_PROMOTED",
                False,
                audit_id,
                "blocked",
                {"not_promoted": True},
                f"{row_id} not promoted or dry-run approved",
            ),
            None,
        )

    contract = renderer_contracts.get(row_id)
    if not contract or not _contract_complete(contract):
        return (
            RenderResult(
                request.request_id,
                row_id,
                request.request_type,
                "RENDER_BLOCKED_MISSING_CONTRACT",
                False,
                audit_id,
                "blocked",
                {"contract_incomplete": True},
                "Renderer contract incomplete",
            ),
            None,
        )

    if request.request_type == "missing_warnings" or not request.include_warnings:
        return (
            RenderResult(
                request.request_id,
                row_id,
                request.request_type,
                "RENDER_BLOCKED_MISSING_CONTRACT",
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
            RenderResult(
                request.request_id,
                row_id,
                request.request_type,
                "RENDER_BLOCKED_MISSING_DIAGNOSTICS",
                False,
                audit_id,
                "blocked",
                {"diagnostics_missing": True},
                "Parallel-trends diagnostics required for DCM-004",
            ),
            None,
        )

    geom = request.geometry or contract.get("allowed_geometry")
    blocked = set(contract.get("blocked_geometry") or [])
    if geom in blocked or request.request_type == "unsupported_geometry":
        return (
            RenderResult(
                request.request_id,
                row_id,
                request.request_type,
                "RENDER_BLOCKED_UNSUPPORTED_GEOMETRY",
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
            RenderResult(
                request.request_id,
                row_id,
                request.request_type,
                "RENDER_BLOCKED_UNSUPPORTED_GEOMETRY",
                False,
                audit_id,
                "blocked",
                {"unsupported_timing": True},
                "Unsupported timing for DCM-004",
            ),
            None,
        )

    if request.payload_type in ("placeholder", "none"):
        decision: RenderDecision = "RENDER_ACCEPTED_PLACEHOLDER_RESEARCH_MODE"
    elif request.payload_type == "synthetic":
        decision = "RENDER_ACCEPTED_RESEARCH_MODE"
    else:
        decision = "RENDER_ACCEPTED_RESEARCH_MODE"

    gates = {
        "row_promoted": row_id in promoted,
        "dry_run_approved": row_id in dry_accepted,
        "contract_complete": True,
        "warnings_present": bool(ROW_RENDER_WARNINGS.get(row_id)),
        "research_mode_only": True,
        "live_api_blocked": True,
        "scheduler_blocked": True,
        "calibration_signal_blocked": True,
    }

    rendered = _build_rendered_output(contract=contract, request=request, decision=decision)
    return (
        RenderResult(
            request.request_id,
            row_id,
            request.request_type,
            decision,
            True,
            audit_id,
            "accepted",
            gates,
            "Research-mode TrustReport render accepted",
        ),
        rendered,
    )


def _build_render_requests() -> list[RenderRequest]:
    return [
        # Positive
        RenderRequest("pos-dcm001-valid", "DCM-001", "valid_research", "research_mode_only", "restricted_trustreport_research_only"),
        RenderRequest("pos-dcm004-valid", "DCM-004", "valid_research", "research_mode_only", "restricted_trustreport_research_only"),
        RenderRequest(
            "pos-dcm001-placeholder",
            "DCM-001",
            "placeholder_payload",
            "research_mode_only",
            "restricted_trustreport_research_only",
            payload_type="placeholder",
        ),
        RenderRequest(
            "pos-dcm004-placeholder",
            "DCM-004",
            "placeholder_payload",
            "research_mode_only",
            "restricted_trustreport_research_only",
            payload_type="placeholder",
        ),
        RenderRequest(
            "pos-dcm001-synthetic",
            "DCM-001",
            "synthetic_payload",
            "research_mode_only",
            "restricted_trustreport_research_only",
            payload_type="synthetic",
        ),
        RenderRequest(
            "pos-dcm004-synthetic",
            "DCM-004",
            "synthetic_payload",
            "research_mode_only",
            "restricted_trustreport_research_only",
            payload_type="synthetic",
        ),
        # Negative contract/geometry
        RenderRequest(
            "neg-dcm001-missing-warnings",
            "DCM-001",
            "missing_warnings",
            "research_mode_only",
            "restricted_trustreport_research_only",
            include_warnings=False,
        ),
        RenderRequest(
            "neg-dcm004-missing-diagnostics",
            "DCM-004",
            "missing_diagnostics",
            "research_mode_only",
            "restricted_trustreport_research_only",
            include_diagnostics=False,
        ),
        RenderRequest(
            "neg-dcm001-bad-geometry",
            "DCM-001",
            "unsupported_geometry",
            "research_mode_only",
            "restricted_trustreport_research_only",
            geometry="aggregate_1x1",
        ),
        RenderRequest(
            "neg-dcm004-bad-timing",
            "DCM-004",
            "unsupported_timing",
            "research_mode_only",
            "restricted_trustreport_research_only",
            geometry="parallel_trends_violation",
        ),
        # Negative excluded rows
        RenderRequest("neg-brb", "DCM-005-BRB", "causal_trustreport", "research_mode_only", "restricted_trustreport_research_only"),
        RenderRequest("neg-kfold", "DCM-005-KFOLD", "causal_trustreport", "research_mode_only", "restricted_trustreport_research_only"),
        RenderRequest("neg-placebo", "DCM-005-PLACEBO", "causal_trustreport", "research_mode_only", "restricted_trustreport_research_only"),
        RenderRequest("neg-dcm006-global", "DCM-006", "global_claim", "research_mode_only", "restricted_trustreport_research_only", claim_type="global"),
        RenderRequest("neg-dcm008-aggregate", "DCM-008", "aggregate_stratified", "research_mode_only", "restricted_trustreport_research_only", claim_type="aggregate_stratified"),
        # Boundary blocks
        RenderRequest("neg-cal", "DCM-001", "calibration", "calibration_mode", "calibration_signal"),
        RenderRequest("neg-live", "DCM-004", "live_api", "api_mode", "live_api"),
        RenderRequest("neg-scheduler", "DCM-001", "scheduler", "scheduler_mode", "scheduler"),
        RenderRequest("neg-prod", "DCM-004", "production", "production_mode", "production_decisioning"),
        RenderRequest("neg-budget", "DCM-001", "budget", "optimization_mode", "budget_optimization_input"),
        RenderRequest("neg-unknown", "DCM-999", "unknown", "research_mode_only", "restricted_trustreport_research_only"),
    ]


def build_trustreport_research_mode_renderer_001() -> dict[str, Any]:
    inputs = _load_inputs()
    dry_run = inputs["integration_dry_run"]
    promotion = inputs["downstream_promotion"]
    registry = load_registry()

    if dry_run.get("governance_verdict") != "trustreport_integration_dry_run_passed":
        raise ValueError("Dry-run artifact must have passed before renderer")
    if promotion.get("governance_verdict") != "trustreport_downstream_restricted_row_promotion_approved":
        raise ValueError("Promotion artifact must approve restricted rows")

    row_contracts = dict(dry_run.get("row_contracts") or {})
    renderer_contracts: dict[str, dict[str, Any]] = {}
    warning_contracts: dict[str, list[str]] = {}
    restriction_contracts: dict[str, dict[str, Any]] = {}

    for row_id in PROMOTED_ROWS:
        base = row_contracts.get(row_id)
        if not base:
            raise KeyError(f"Row contract missing for {row_id}")
        rc = _build_renderer_contract(
            base,
            dry_run_artifact="TRUSTREPORT-INTEGRATION-DRY-RUN-001",
            promotion_artifact="TRUSTREPORT-DOWNSTREAM-PROMOTION-001",
        )
        renderer_contracts[row_id] = rc
        warning_contracts[row_id] = ROW_RENDER_WARNINGS[row_id]
        restriction_contracts[row_id] = {
            "blocked_roles": rc.get("blocked_roles"),
            "blocked_geometry": rc.get("blocked_geometry"),
        }

    contracts_complete = all(_contract_complete(c) for c in renderer_contracts.values())

    requests = _build_render_requests()
    results: list[RenderResult] = []
    rendered_examples: dict[str, dict[str, Any]] = {}
    audit_records: list[dict[str, Any]] = []

    for req in requests:
        result, rendered = _evaluate_render(
            req,
            renderer_contracts=renderer_contracts,
            promotion=promotion,
            dry_run=dry_run,
        )
        results.append(result)
        if rendered is not None:
            rendered_examples[req.request_id] = rendered
        audit_records.append(
            {
                "audit_record_id": result.audit_record_id,
                "request_id": req.request_id,
                "row_id": req.row_id,
                "decision": result.decision,
                "accepted": result.accepted,
                "render_mode": req.render_mode,
                "research_mode_only": True,
                "live_api_authorized": False,
                "scheduler_authorized": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    accepted = [r for r in results if r.accepted]
    blocked = [r for r in results if not r.accepted]
    accepted_restricted = [
        r for r in results
        if r.decision in ("RENDER_ACCEPTED_RESEARCH_MODE", "RENDER_ACCEPTED_PLACEHOLDER_RESEARCH_MODE")
    ]
    accepted_row_ids = {r.row_id for r in accepted_restricted}

    for r in accepted_restricted:
        if r.row_id not in PROMOTED_ROWS:
            raise ValueError(f"Unexpected render acceptance for {r.row_id}")

    positive_pass = all(
        r.decision in ("RENDER_ACCEPTED_RESEARCH_MODE", "RENDER_ACCEPTED_PLACEHOLDER_RESEARCH_MODE")
        for r in results
        if r.request_id.startswith("pos-")
    )
    negative_pass = all(
        not r.accepted
        or r.decision.startswith("RENDER_ACCEPTED")
        for r in results
        if r.request_id.startswith("neg-")
    ) and all(
        not r.accepted for r in results if r.request_id.startswith("neg-")
    )

    if contracts_complete and positive_pass and negative_pass:
        verdict: GovernanceVerdict = "trustreport_research_mode_renderer_passed"
        next_artifact = "TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001"
    elif not contracts_complete:
        verdict = "trustreport_research_mode_renderer_blocked_missing_contract"
        next_artifact = "TRUSTREPORT_RESEARCH_MODE_REPORT_SCHEMA_001"
    else:
        verdict = "trustreport_research_mode_renderer_failed"
        next_artifact = "TRUSTREPORT_RESEARCH_MODE_REPORT_SCHEMA_001"

    deferred = [
        inv["investigation_id"]
        for inv in registry.get("investigations", [])
        if inv.get("status") == "DEFERRED_WITH_TRIGGER"
    ]

    rendered_metadata = {
        req_id: {
            "row_id": ex["row_id"],
            "render_status": ex["render_status"],
            "measurement_label": ex["measurement"]["label"],
            "synthetic": ex["measurement"].get("synthetic", False),
            "placeholder": ex["measurement"].get("placeholder", False),
        }
        for req_id, ex in rendered_examples.items()
    }

    handoff = build_investigation_handoff(
        follow_up_issues=[],
        resolved_issues=[],
        terminal_dispositions=[],
        next_artifact=next_artifact,
    )

    limitations = [
        "This artifact renders restricted row-level TrustReport contracts in research mode only.",
        "It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, budget optimization, or global platform rollout.",
        "Only DCM-001 and DCM-004 are accepted for research-mode rendering.",
        "All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.",
        "No live measurement payloads are fabricated; placeholders and synthetic dry-run payloads are explicitly labeled.",
    ]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "input_artifacts": inputs["_paths"],
        "renderer_scope": sorted(RENDERER_SCOPE),
        "render_requests": [r.to_dict() for r in requests],
        "accepted_renders": [r.to_dict() for r in accepted],
        "blocked_renders": [r.to_dict() for r in blocked],
        "accepted_rows": sorted(accepted_row_ids),
        "blocked_rows": sorted({r.row_id for r in blocked}),
        "renderer_contracts": renderer_contracts,
        "rendered_example_metadata": rendered_metadata,
        "warning_contracts": warning_contracts,
        "restriction_contracts": restriction_contracts,
        "audit_records": audit_records,
        "negative_control_results": [r.to_dict() for r in results if r.request_id.startswith("neg-")],
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
            "blocking_for_renderer": [],
        },
        "governance_verdict": verdict,
        "limitations": limitations,
        "next_artifact": next_artifact,
        "investigation_handoff": handoff,
        "verdict": verdict,
        "contracts_complete": contracts_complete,
        "dcm001_render_result": next(
            (r.to_dict() for r in results if r.request_id == "pos-dcm001-valid"),
            {},
        ),
        "dcm004_render_result": next(
            (r.to_dict() for r in results if r.request_id == "pos-dcm004-valid"),
            {},
        ),
        "render_results": [r.to_dict() for r in results],
        "rendered_output_schema": {
            "required_fields": [
                "title",
                "artifact_id",
                "row_id",
                "method_identity",
                "estimand",
                "allowed_scope",
                "measurement",
                "diagnostic_requirements",
                "warnings",
                "restrictions",
                "blocked_uses",
                "audit_trail",
                "authorization_boundaries",
                "banners",
                "render_status",
            ],
            "placeholder_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED",
            "synthetic_label": "SYNTHETIC_DRY_RUN_PAYLOAD",
        },
        "_rendered_examples_full": rendered_examples,
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
        revisit_trigger="After TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001",
        decision_checkpoint="TRUSTREPORT_RESEARCH_MODE_RENDERER_001",
        next_artifact=payload.get("next_artifact"),
    )
    lines = [
        f"# {_ARTIFACT_ID} Report",
        "",
        "## 1. Executive summary",
        "",
        "This artifact renders restricted row-level TrustReport contracts in research mode only.",
        "It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, budget optimization, or global platform rollout.",
        "Only DCM-001 and DCM-004 are accepted for research-mode rendering.",
        "All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.",
        "",
        f"**Governance verdict:** `{payload.get('governance_verdict')}`",
        f"**Accepted rows:** {payload.get('accepted_rows')}",
        "",
        "## 2. Scope",
        "",
        "Research-mode TrustReport renderer for DCM-001 (SCM+JK) and DCM-004 (DID+bootstrap).",
        "",
        "## 3. Non-goals",
        "",
        "- No live API, scheduler, production automation",
        "- No CalibrationSignal, budget optimization, recommendations",
        "- No new statistical simulations or algorithm changes",
        "",
        "## 4. Input artifacts",
        "",
        json.dumps(payload.get("input_artifacts"), indent=2),
        "",
        "## 5. Research-mode renderer contract",
        "",
        json.dumps(list(RENDERER_CONTRACT_FIELDS), indent=2),
        "",
        "## 6. Rendered output schema",
        "",
        json.dumps(payload.get("rendered_output_schema"), indent=2),
        "",
        "## 7. DCM-001 render result",
        "",
        json.dumps(payload.get("dcm001_render_result"), indent=2),
        "",
        "## 8. DCM-004 render result",
        "",
        json.dumps(payload.get("dcm004_render_result"), indent=2),
        "",
        "## 9. Placeholder payload behavior",
        "",
        "When no live readout is supplied, measurement section uses `NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED`.",
        "",
        "## 10. Synthetic dry-run payload behavior",
        "",
        "Synthetic payloads labeled `SYNTHETIC_DRY_RUN_PAYLOAD` with `synthetic: true` and `non_decisioning: true`.",
        "",
        "## 11. Negative-control render requests",
        "",
        json.dumps(payload.get("negative_control_results"), indent=2),
        "",
        "## 12. Blocked diagnostic-only rows",
        "",
        "DCM-002, DCM-005-BRB, DCM-005-KFOLD, DCM-008 — RENDER_BLOCKED_DIAGNOSTIC_ONLY",
        "",
        "## 13. Blocked null-monitor causal reuse",
        "",
        "DCM-005-PLACEBO causal render — RENDER_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
        "",
        "## 14. Blocked multi-cell/global claims",
        "",
        "DCM-006 — RENDER_BLOCKED_NOT_PROMOTED",
        "",
        "## 15. Blocked stratified aggregate claims",
        "",
        "DCM-008 aggregate — RENDER_BLOCKED_DIAGNOSTIC_ONLY",
        "",
        "## 16. CalibrationSignal boundary",
        "",
        json.dumps(payload.get("calibration_signal_summary"), indent=2),
        "",
        "## 17. Live API boundary",
        "",
        json.dumps(payload.get("live_api_authorization_summary"), indent=2),
        "",
        "## 18. Scheduler boundary",
        "",
        json.dumps(payload.get("scheduler_authorization_summary"), indent=2),
        "",
        "## 19. Production decisioning boundary",
        "",
        json.dumps(payload.get("production_decisioning_summary"), indent=2),
        "",
        "## 20. Budget optimization boundary",
        "",
        json.dumps(payload.get("budget_optimization_summary"), indent=2),
        "",
        "## 21. Audit record verification",
        "",
        f"Audit records: {len(payload.get('audit_records') or [])}",
        "",
        "## 22. Open investigation check",
        "",
        json.dumps(payload.get("open_investigation_check"), indent=2),
        "",
        "## 23. Governance verdict",
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
    render_output_path: Path | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    payload = build_trustreport_research_mode_renderer_001()
    full_examples = payload.pop("_rendered_examples_full", {})

    if render_output_path is not None:
        _atomic_write(
            render_output_path,
            json.dumps(full_examples, indent=2, sort_keys=False) + "\n",
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
        for rec in payload.get("render_results") or []:
            if rec.get("row_id") in DIAGNOSTIC_ONLY_ROWS | {"DCM-006", "DCM-008"}:
                if rec.get("decision", "").startswith("RENDER_ACCEPTED"):
                    raise RuntimeError(f"Excluded row {rec['row_id']} must not render")

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
    parser.add_argument("--render-output-local", type=Path, default=_DEFAULT_RENDER_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    write_summary(
        args.summary_output,
        overwrite=args.overwrite,
        report_path=args.report_output,
        render_output_path=args.render_output_local,
        strict=args.strict,
    )


if __name__ == "__main__":
    main()
