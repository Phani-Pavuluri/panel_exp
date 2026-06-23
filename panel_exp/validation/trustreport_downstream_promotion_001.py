"""TRUSTREPORT-DOWNSTREAM-PROMOTION-001 — governed downstream promotion gate.

Evaluates restricted row-level TrustReport promotion for DCM-001 and DCM-004 only.
Loads committed reassessment summaries; does not run new statistical simulations.
Does not authorize live APIs, scheduler execution, or global platform rollout.
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
_ARTIFACT_ID = "TRUSTREPORT-DOWNSTREAM-PROMOTION-001"
_ARTIFACT_VERSION = "1.0.0"
_DEFAULT_SUMMARY = _ARCHIVE / "TRUSTREPORT_DOWNSTREAM_PROMOTION_001_summary.json"
_DEFAULT_REPORT = _REPO / "docs/track_d/TRUSTREPORT_DOWNSTREAM_PROMOTION_001_REPORT.md"

PromotionDecision = Literal[
    "PROMOTE_RESTRICTED_TRUSTREPORT",
    "PROMOTE_DIAGNOSTIC_DISPLAY_ONLY",
    "PROMOTE_NULL_MONITOR_ONLY",
    "DO_NOT_PROMOTE_DIAGNOSTIC_ONLY",
    "DO_NOT_PROMOTE_INELIGIBLE",
    "DO_NOT_PROMOTE_DEFERRED",
    "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE",
    "DO_NOT_PROMOTE_BLOCKED_BY_INVESTIGATION",
    "DO_NOT_PROMOTE_NOT_IN_SCOPE",
    "DO_NOT_PROMOTE_BLOCKED_BY_MISSING_CONTRACT",
]

GovernanceVerdict = Literal[
    "trustreport_downstream_restricted_row_promotion_approved",
    "trustreport_downstream_promotion_no_row_promotion",
    "trustreport_downstream_promotion_inconclusive",
]

REQUIRED_INPUTS: dict[str, str] = {
    "full_reassessment": "FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
    "brb_post_remediation": "DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001_summary.json",
    "dcm001_reassessment": "TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
    "dcm004_reassessment": "DCM004_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
    "prior_validation": "TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json",
}

CANDIDATE_UNIVERSE = frozenset({"DCM-001", "DCM-004"})

RESTRICTED_TRUSTREPORT_ELIGIBILITY = frozenset(
    {"ELIGIBLE_WITH_RESTRICTIONS", "TRUSTREPORT_ELIGIBLE"}
)

CONTRACT_REQUIRED_FIELDS = frozenset(
    {
        "allowed_design_family",
        "allowed_estimator",
        "allowed_inference_method",
        "allowed_estimand",
        "allowed_geometry",
        "allowed_readout_scope",
        "required_interval_semantics",
        "required_warnings",
        "blocked_downstream_uses",
        "calibration_signal_allowed",
        "trustreport_role",
    }
)

BRB_EXCLUSION_TEXT = (
    "TBRRidge + BRB is excluded because post-remediation reassessment terminally marked it "
    "diagnostic-only after failed null calibration. It is not eligible for TrustReport, "
    "CalibrationSignal, production decisioning, or budget optimization input."
)

DCM006_EXCLUSION_TEXT = (
    "DCM-006 remains limited to governed marginal per-cell readouts under "
    "PARALLEL_MARGINAL_CELLS + REPORT_EACH_CELL_ONLY. This artifact does not promote "
    "any-cell success, winner/ranking selection, pooled multi-cell causal readout, or "
    "global TrustReport decisioning."
)

DCM008_EXCLUSION_TEXT = (
    "DCM-008 stratified SCM+JK remains diagnostic-only. Aggregate stratified readout is "
    "characterization only, not a governed pooled causal estimand."
)

PROMOTED_BLOCKED_DOWNSTREAM = frozenset(
    {
        "live_api",
        "scheduler",
        "production_automation",
        "calibration_signal",
        "budget_optimization_input",
        "global_trustreport_platform",
    }
)


@dataclass(frozen=True)
class RowPromotionReview:
    row_id: str
    decision: PromotionDecision
    trustreport_eligibility: str
    evidence_artifacts: tuple[str, ...]
    gate_results: dict[str, bool]
    gates_pass: bool
    restriction_contract: dict[str, Any] = field(default_factory=dict)
    exclusion_reason: str = ""
    blocking_investigations: tuple[str, ...] = ()
    required_warnings: tuple[str, ...] = ()
    required_restrictions: tuple[str, ...] = ()
    calibration_signal_allowed: bool = False
    trustreport_role: str = "blocked"
    row_level_restricted_promotion_allowed: bool = False

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


def _row_from_full(full: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in full.get("row_decisions") or []:
        if row.get("row_id") == row_id:
            return row
    raise KeyError(f"Row {row_id} not found in full reassessment")


def _contract_complete(contract: dict[str, Any]) -> bool:
    for field_name in CONTRACT_REQUIRED_FIELDS:
        if field_name not in contract:
            return False
        val = contract[field_name]
        if field_name == "required_warnings" and not val:
            return False
        if field_name == "blocked_downstream_uses" and not val:
            return False
    return True


def _build_dcm001_contract(
    full_row: dict[str, Any],
    dcm001: dict[str, Any],
) -> dict[str, Any]:
    provisional = dcm001.get("provisional_gates") or {}
    semantic = dcm001.get("semantic_gate_results") or {}
    reassess = dcm001.get("dcm_001_reassessment") or {}
    warnings = list(full_row.get("required_warnings") or reassess.get("warnings") or [])
    return {
        "allowed_design_family": full_row.get("design_family", "single_cell"),
        "allowed_estimator": full_row.get("estimator", "scm"),
        "allowed_inference_method": full_row.get("inference_method", "unit_jackknife"),
        "allowed_estimand": full_row.get("estimand", "treated_unit_effect_level"),
        "allowed_geometry": full_row.get("geometry", "unit_panel_single_cell"),
        "allowed_readout_scope": full_row.get("readout_scope", "restricted_causal_interval"),
        "minimum_pre_period": provisional.get("label", "support_gated"),
        "minimum_post_period": provisional.get("label", "support_gated"),
        "required_fit_diagnostics": ["prefit_warning_required", "donor_support_gate"],
        "required_interval_semantics": semantic.get(
            "semantic_class", "restricted_causal_interval_level_scale"
        ),
        "required_warnings": warnings,
        "blocked_geometries": ["aggregate_1x1", "multi_cell_pooled", "staggered_timing"],
        "blocked_downstream_uses": sorted(PROMOTED_BLOCKED_DOWNSTREAM),
        "calibration_signal_allowed": False,
        "trustreport_role": "restricted_trustreport_research_only",
    }


def _build_dcm004_contract(
    full_row: dict[str, Any],
    dcm004: dict[str, Any],
) -> dict[str, Any]:
    reassess = dcm004.get("dcm004_reassessment") or {}
    supported = reassess.get("supported_contract") or {}
    warnings = list(full_row.get("required_warnings") or reassess.get("warnings") or [])
    geom = supported.get("geometry") or {}
    timing = supported.get("timing") or {}
    estimand = supported.get("estimand") or {}
    semantic = supported.get("semantic") or {}
    return {
        "allowed_design_family": full_row.get("design_family", "single_cell"),
        "allowed_estimator": full_row.get("estimator", "did"),
        "allowed_inference_method": full_row.get("inference_method", "bootstrap"),
        "allowed_estimand": estimand.get("id", full_row.get("estimand", "cumulative_att_level")),
        "allowed_geometry": "unit_panel_single_cell",
        "allowed_readout_scope": full_row.get("readout_scope", "restricted_causal_interval"),
        "minimum_pre_period": geom.get("min_control", "support_gated"),
        "minimum_post_period": "support_gated",
        "required_fit_diagnostics": [
            "parallel_trends_diagnostic_required",
            "pretrend_diagnostic_required",
        ],
        "required_interval_semantics": semantic.get(
            "readout_class", "restricted_causal_interval"
        ),
        "required_warnings": warnings,
        "blocked_geometries": list(supported.get("excluded_regimes") or [])
        + ["staggered_pooled", "aggregate_1x1"],
        "blocked_downstream_uses": sorted(PROMOTED_BLOCKED_DOWNSTREAM),
        "calibration_signal_allowed": False,
        "trustreport_role": "restricted_trustreport_research_only",
        "timing_regime": timing.get("regime", "common_simultaneous_adoption"),
    }


def _evaluate_promotion_gates(
    *,
    full_row: dict[str, Any],
    contract: dict[str, Any],
    blocking_investigations: list[str],
) -> dict[str, bool]:
    elig = str(full_row.get("trustreport_eligibility") or "")
    artifacts = full_row.get("evidence_artifacts") or []
    restrictions = full_row.get("restrictions") or []
    return {
        "full_reassessment_eligible": elig in RESTRICTED_TRUSTREPORT_ELIGIBILITY,
        "no_blocking_investigations": len(blocking_investigations) == 0,
        "evidence_artifacts_present": bool(artifacts),
        "restrictions_present": bool(restrictions),
        "restriction_contract_complete": _contract_complete(contract),
        "interval_semantics_supported": bool(contract.get("required_interval_semantics")),
        "calibration_signal_not_requested_or_explicit": contract.get(
            "calibration_signal_allowed"
        )
        is False,
        "not_live_platform_authorization": True,
    }


def _review_candidate_row(
    row_id: str,
    *,
    full: dict[str, Any],
    dcm001: dict[str, Any] | None = None,
    dcm004: dict[str, Any] | None = None,
) -> RowPromotionReview:
    full_row = _row_from_full(full, row_id)
    blocking = tuple(full_row.get("blocking_investigations") or [])
    elig = str(full_row.get("trustreport_eligibility") or "")

    if row_id == "DCM-001":
        contract = _build_dcm001_contract(full_row, dcm001 or {})
    elif row_id == "DCM-004":
        contract = _build_dcm004_contract(full_row, dcm004 or {})
    else:
        raise ValueError(f"Unexpected candidate row: {row_id}")

    gates = _evaluate_promotion_gates(
        full_row=full_row,
        contract=contract,
        blocking_investigations=list(blocking),
    )
    gates_pass = all(gates.values())

    if not gates["restriction_contract_complete"]:
        decision: PromotionDecision = "DO_NOT_PROMOTE_BLOCKED_BY_MISSING_CONTRACT"
    elif not gates["full_reassessment_eligible"]:
        decision = "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE"
    elif blocking:
        decision = "DO_NOT_PROMOTE_BLOCKED_BY_INVESTIGATION"
    elif gates_pass:
        decision = "PROMOTE_RESTRICTED_TRUSTREPORT"
    else:
        decision = "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE"

    promoted = decision == "PROMOTE_RESTRICTED_TRUSTREPORT"
    return RowPromotionReview(
        row_id=row_id,
        decision=decision,
        trustreport_eligibility=elig,
        evidence_artifacts=tuple(full_row.get("evidence_artifacts") or ()),
        gate_results=gates,
        gates_pass=gates_pass,
        restriction_contract=contract,
        blocking_investigations=blocking,
        required_warnings=tuple(contract.get("required_warnings") or ()),
        required_restrictions=tuple(full_row.get("restrictions") or ()),
        calibration_signal_allowed=False,
        trustreport_role="restricted_trustreport_research_only" if promoted else "blocked",
        row_level_restricted_promotion_allowed=promoted,
    )


def _excluded_row(
    row_id: str,
    decision: PromotionDecision,
    *,
    full: dict[str, Any] | None = None,
    exclusion_reason: str = "",
    brb_summary: dict[str, Any] | None = None,
) -> RowPromotionReview:
    elig = ""
    artifacts: tuple[str, ...] = ()
    blocking: tuple[str, ...] = ()
    restrictions: tuple[str, ...] = ()
    if full is not None:
        try:
            full_row = _row_from_full(full, row_id)
            elig = str(full_row.get("trustreport_eligibility") or "")
            artifacts = tuple(full_row.get("evidence_artifacts") or ())
            blocking = tuple(full_row.get("blocking_investigations") or ())
            restrictions = tuple(full_row.get("restrictions") or ())
        except KeyError:
            pass
    if row_id == "DCM-005-BRB" and brb_summary is not None:
        exclusion_reason = BRB_EXCLUSION_TEXT
        elig = "DIAGNOSTIC_ONLY"
        decision = "DO_NOT_PROMOTE_DIAGNOSTIC_ONLY"
    return RowPromotionReview(
        row_id=row_id,
        decision=decision,
        trustreport_eligibility=elig,
        evidence_artifacts=artifacts,
        gate_results={"excluded": True},
        gates_pass=False,
        exclusion_reason=exclusion_reason,
        blocking_investigations=blocking,
        required_restrictions=restrictions,
        trustreport_role="blocked",
    )


def build_trustreport_downstream_promotion_001() -> dict[str, Any]:
    inputs = _load_inputs()
    full = inputs["full_reassessment"]
    brb = inputs["brb_post_remediation"]
    registry = load_registry()

    dcm001_review = _review_candidate_row(
        "DCM-001", full=full, dcm001=inputs["dcm001_reassessment"]
    )
    dcm004_review = _review_candidate_row(
        "DCM-004", full=full, dcm004=inputs["dcm004_reassessment"]
    )
    reviewed = [dcm001_review, dcm004_review]

    brb_decision = str(brb.get("path_decision") or brb.get("row_decision", {}).get("selected_decision"))
    brb_excluded = _excluded_row(
        "DCM-005-BRB",
        "DO_NOT_PROMOTE_DIAGNOSTIC_ONLY",
        full=full,
        exclusion_reason=BRB_EXCLUSION_TEXT,
        brb_summary=brb,
    )
    excluded_paths = [
        brb_excluded,
        _excluded_row(
            "DCM-005-KFOLD",
            "DO_NOT_PROMOTE_DIAGNOSTIC_ONLY",
            full=full,
            exclusion_reason="TBRRidge + KFold is diagnostic-only; not eligible for TrustReport promotion.",
        ),
        _excluded_row(
            "DCM-005-PLACEBO",
            "PROMOTE_NULL_MONITOR_ONLY",
            full=full,
            exclusion_reason=(
                "TBRRidge + Placebo is null-monitor/falsification-only; "
                "not eligible for causal-interval TrustReport promotion."
            ),
        ),
        _excluded_row(
            "DCM-006",
            "DO_NOT_PROMOTE_NOT_IN_SCOPE",
            full=full,
            exclusion_reason=DCM006_EXCLUSION_TEXT,
        ),
        _excluded_row(
            "DCM-008",
            "DO_NOT_PROMOTE_DIAGNOSTIC_ONLY",
            full=full,
            exclusion_reason=DCM008_EXCLUSION_TEXT,
        ),
        _excluded_row(
            "DCM-002",
            "DO_NOT_PROMOTE_DIAGNOSTIC_ONLY",
            full=full,
            exclusion_reason="AugSynth + UnitJackknife is diagnostic-only per full reassessment.",
        ),
        _excluded_row(
            "SCM-PLACEBO",
            "PROMOTE_NULL_MONITOR_ONLY",
            full=full,
            exclusion_reason="SCM Placebo is null-monitor-only; not eligible for causal TrustReport promotion.",
        ),
    ]

    for row_id in (
        "DCM-003",
        "DCM-007",
        "DCM-009",
        "DCM-010",
        "DCM-011",
        "DCM-012",
        "DCM-013",
        "DCM-014",
        "DCM-015",
        "DCM-016",
        "DCM-017",
        "DCM-018",
        "DCM-019",
    ):
        try:
            full_row = _row_from_full(full, row_id)
            elig = str(full_row.get("trustreport_eligibility") or "")
            if elig in ("INELIGIBLE",):
                decision: PromotionDecision = "DO_NOT_PROMOTE_INELIGIBLE"
            elif elig in ("INSUFFICIENT_EVIDENCE",):
                decision = "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE"
            elif elig in ("DEFERRED_REMEDIATION",):
                decision = "DO_NOT_PROMOTE_DEFERRED"
            elif elig in ("DIAGNOSTIC_ONLY",):
                decision = "DO_NOT_PROMOTE_DIAGNOSTIC_ONLY"
            else:
                decision = "DO_NOT_PROMOTE_NOT_IN_SCOPE"
            excluded_paths.append(
                _excluded_row(row_id, decision, full=full, exclusion_reason=f"Not in promotion candidate universe; status {elig}.")
            )
        except KeyError:
            excluded_paths.append(
                _excluded_row(
                    row_id,
                    "DO_NOT_PROMOTE_NOT_IN_SCOPE",
                    exclusion_reason="Not in promotion candidate universe.",
                )
            )

    promoted_rows = [r for r in reviewed if r.decision == "PROMOTE_RESTRICTED_TRUSTREPORT"]
    if brb_decision != "BRB_DIAGNOSTIC_ONLY" and any(
        r.decision == "PROMOTE_RESTRICTED_TRUSTREPORT" for r in reviewed if "BRB" in r.row_id
    ):
        raise ValueError("BRB must not be promoted")

    for exc in excluded_paths:
        if exc.row_id == "DCM-005-BRB" and exc.decision == "PROMOTE_RESTRICTED_TRUSTREPORT":
            raise ValueError("BRB must not receive PROMOTE_RESTRICTED_TRUSTREPORT")

    row_level_allowed = len(promoted_rows) > 0
    verdict: GovernanceVerdict = (
        "trustreport_downstream_restricted_row_promotion_approved"
        if row_level_allowed
        else "trustreport_downstream_promotion_no_row_promotion"
    )

    contracts_complete = all(
        r.gates_pass and r.decision == "PROMOTE_RESTRICTED_TRUSTREPORT" for r in promoted_rows
    )
    next_artifact = (
        "TRUSTREPORT_INTEGRATION_DRY_RUN_001"
        if row_level_allowed and contracts_complete
        else "TRUSTREPORT_RESTRICTED_ROW_CONTRACTS_001"
    )

    open_inv = [
        inv
        for inv in registry.get("investigations", [])
        if inv.get("status") in ("OPEN", "DEFERRED_WITH_TRIGGER", "PLANNED")
    ]
    deferred_inv = [
        inv["investigation_id"]
        for inv in registry.get("investigations", [])
        if inv.get("status") == "DEFERRED_WITH_TRIGGER"
    ]

    promotion_decisions = {r.row_id: r.decision for r in reviewed + excluded_paths}
    row_auth_matrix = {
        r.row_id: {
            "decision": r.decision,
            "row_level_restricted_promotion_allowed": r.row_level_restricted_promotion_allowed,
            "trustreport_role": r.trustreport_role,
            "calibration_signal_allowed": r.calibration_signal_allowed,
        }
        for r in reviewed + excluded_paths
    }
    cal_matrix = {r.row_id: r.calibration_signal_allowed for r in reviewed + excluded_paths}
    downstream_matrix = {
        r.row_id: {
            "trustreport_restricted": r.row_level_restricted_promotion_allowed,
            "production_decisioning": False,
            "live_api": False,
            "scheduler": False,
        }
        for r in reviewed + excluded_paths
    }

    all_warnings = sorted(
        {w for r in promoted_rows for w in r.required_warnings}
        | {w for r in promoted_rows for w in r.required_restrictions}
    )
    all_restrictions = sorted({x for r in promoted_rows for x in r.required_restrictions})

    handoff = build_investigation_handoff(
        follow_up_issues=[],
        resolved_issues=[],
        terminal_dispositions=[],
        next_artifact=next_artifact,
    )

    limitations = [
        "This artifact evaluates restricted downstream promotion after full TrustReport eligibility reassessment.",
        "It does not introduce new statistical evidence.",
        "It does not remediate any estimator or inference method.",
        "It does not authorize live APIs, scheduler execution, or global platform rollout.",
        "Diagnostic-only, null-monitor-only, deferred, and ineligible rows remain excluded from production decisioning.",
        BRB_EXCLUSION_TEXT,
        DCM006_EXCLUSION_TEXT,
        DCM008_EXCLUSION_TEXT,
    ]

    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "input_artifacts": inputs["_paths"],
        "candidate_universe": sorted(CANDIDATE_UNIVERSE),
        "reviewed_rows": [r.to_dict() for r in reviewed],
        "promotion_decisions": promotion_decisions,
        "promoted_rows": [r.row_id for r in promoted_rows],
        "excluded_rows": [r.row_id for r in excluded_paths],
        "blocked_rows": [
            r.row_id
            for r in reviewed + excluded_paths
            if r.decision.startswith("DO_NOT_PROMOTE")
        ],
        "diagnostic_only_rows": [
            r.row_id
            for r in reviewed + excluded_paths
            if "DIAGNOSTIC" in r.decision or r.trustreport_eligibility == "DIAGNOSTIC_ONLY"
        ],
        "null_monitor_only_rows": [
            r.row_id for r in excluded_paths if r.decision == "PROMOTE_NULL_MONITOR_ONLY"
        ],
        "deferred_rows": [
            r.row_id for r in excluded_paths if r.decision == "DO_NOT_PROMOTE_DEFERRED"
        ],
        "promotion_gates": {
            "gate_definitions": list(
                _evaluate_promotion_gates(
                    full_row={"trustreport_eligibility": "ELIGIBLE_WITH_RESTRICTIONS", "evidence_artifacts": ["x"], "restrictions": ["y"]},
                    contract={f: True for f in CONTRACT_REQUIRED_FIELDS} | {"required_warnings": ["w"], "blocked_downstream_uses": ["z"], "required_interval_semantics": "restricted", "calibration_signal_allowed": False, "trustreport_role": "restricted"},
                    blocking_investigations=[],
                ).keys()
            ),
            "global_live_authorization_forbidden": True,
        },
        "row_level_authorization_matrix": row_auth_matrix,
        "calibration_signal_matrix": cal_matrix,
        "downstream_role_matrix": downstream_matrix,
        "required_warnings": all_warnings,
        "required_restrictions": all_restrictions,
        "global_authorization_summary": {
            "trust_report_platform_authorized": False,
            "live_api_authorized": False,
            "scheduler_authorized": False,
        },
        "live_api_authorization_summary": {
            "live_api_authorized": False,
            "rationale": "Promotion gate artifact approves row-level restricted research roles only.",
        },
        "scheduler_authorization_summary": {
            "scheduler_authorized": False,
            "rationale": "No scheduler or production automation authorized.",
        },
        "row_level_restricted_promotion_allowed": row_level_allowed,
        "investigation_status": {
            "open_investigations": [i["investigation_id"] for i in open_inv],
            "deferred_investigations": deferred_inv,
            "blocking_for_promotion": deferred_inv,
        },
        "governance_verdict": verdict,
        "limitations": limitations,
        "next_artifact": next_artifact,
        "investigation_handoff": handoff,
        "verdict": verdict,
        "dcm001_decision": dcm001_review.decision,
        "dcm004_decision": dcm004_review.decision,
        "brb_post_remediation_decision": brb_decision,
        "promotion_evidence": {
            "artifact_id": _ARTIFACT_ID,
            "status": "RESTRICTED_ROW_APPROVED" if row_level_allowed else "NO_ROW_PROMOTION",
            "approved_roles": ["restricted_trustreport_research_only"] if row_level_allowed else [],
            "approved_dcm_rows": [r.row_id for r in promoted_rows],
            "approved_estimators": sorted(
                {_row_from_full(full, r.row_id).get("estimator", "") for r in promoted_rows}
            ),
            "approved_inference_paths": sorted(
                {_row_from_full(full, r.row_id).get("inference_method", "") for r in promoted_rows}
            ),
            "approved_readout_semantics": ["restricted_causal_interval"] if row_level_allowed else [],
            "expires_at": None,
            "evidence_version": _ARTIFACT_VERSION,
        },
    }


def write_report(payload: dict[str, Any], path: Path, *, overwrite: bool = False) -> None:
    handoff_lines = format_handoff_report_section(
        resolved_in_artifact=[],
        new_investigations=[],
        updated_investigations=[],
        deferred_issues=payload.get("investigation_status", {}).get("deferred_investigations", []),
        explicit_exclusions=sorted(CANDIDATE_UNIVERSE ^ frozenset(payload.get("promoted_rows") or [])),
        revisit_trigger="After TRUSTREPORT_RESTRICTED_ROW_CONTRACTS_001 or integration dry-run",
        decision_checkpoint="TRUSTREPORT_DOWNSTREAM_PROMOTION_001",
        next_artifact=payload.get("next_artifact"),
    )
    reviewed = payload.get("reviewed_rows") or []
    dcm001 = next((r for r in reviewed if r["row_id"] == "DCM-001"), {})
    dcm004 = next((r for r in reviewed if r["row_id"] == "DCM-004"), {})
    lines = [
        f"# {_ARTIFACT_ID} Report",
        "",
        "## 1. Executive summary",
        "",
        f"Governance verdict: `{payload.get('governance_verdict')}`. "
        f"Promoted rows: {payload.get('promoted_rows')}. "
        "Global platform, live API, and scheduler authorization remain false.",
        "",
        "## 2. Scope",
        "",
        "Restricted downstream promotion review for DCM-001 and DCM-004 only.",
        "",
        "## 3. Non-goals",
        "",
        "- No new statistical simulations",
        "- No estimator/inference remediation",
        "- No live API or scheduler authorization",
        "- No global TrustReport platform rollout",
        "",
        "## 4. Input artifacts",
        "",
        json.dumps(payload.get("input_artifacts"), indent=2),
        "",
        "## 5. Candidate universe",
        "",
        json.dumps(payload.get("candidate_universe"), indent=2),
        "",
        "## 6. Promotion gates",
        "",
        json.dumps(payload.get("promotion_gates"), indent=2),
        "",
        "## 7. DCM-001 review",
        "",
        json.dumps(dcm001, indent=2),
        "",
        "## 8. DCM-004 review",
        "",
        json.dumps(dcm004, indent=2),
        "",
        "## 9. Excluded DCM-005 paths",
        "",
        f"BRB: `{payload.get('brb_post_remediation_decision')}` — {BRB_EXCLUSION_TEXT}",
        "KFold: diagnostic-only — excluded.",
        "Placebo: null-monitor-only — excluded from causal TrustReport promotion.",
        "",
        "## 10. Excluded DCM-006 paths",
        "",
        DCM006_EXCLUSION_TEXT,
        "",
        "## 11. Excluded DCM-008 paths",
        "",
        DCM008_EXCLUSION_TEXT,
        "",
        "## 12. Other excluded/deferred paths",
        "",
        json.dumps(payload.get("excluded_rows"), indent=2),
        "",
        "## 13. Row-level authorization matrix",
        "",
        json.dumps(payload.get("row_level_authorization_matrix"), indent=2),
        "",
        "## 14. CalibrationSignal implications",
        "",
        "CalibrationSignal remains false for all rows. No CalibrationSignal promotion.",
        "",
        json.dumps(payload.get("calibration_signal_matrix"), indent=2),
        "",
        "## 15. Downstream role matrix",
        "",
        json.dumps(payload.get("downstream_role_matrix"), indent=2),
        "",
        "## 16. Required warnings and restrictions",
        "",
        json.dumps(
            {
                "required_warnings": payload.get("required_warnings"),
                "required_restrictions": payload.get("required_restrictions"),
            },
            indent=2,
        ),
        "",
        "## 17. Global TrustReport authorization boundary",
        "",
        json.dumps(payload.get("global_authorization_summary"), indent=2),
        "",
        "## 18. Live API and scheduler boundary",
        "",
        json.dumps(
            {
                "live_api": payload.get("live_api_authorization_summary"),
                "scheduler": payload.get("scheduler_authorization_summary"),
            },
            indent=2,
        ),
        "",
        "## 19. Open investigation check",
        "",
        json.dumps(payload.get("investigation_status"), indent=2),
        "",
        "## 20. Governance verdict",
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
    payload = build_trustreport_downstream_promotion_001()
    global_auth = payload["global_authorization_summary"]
    if strict:
        if global_auth.get("trust_report_platform_authorized"):
            raise RuntimeError("trust_report_platform_authorized must remain false")
        if global_auth.get("live_api_authorized"):
            raise RuntimeError("live_api_authorized must remain false")
        if global_auth.get("scheduler_authorized"):
            raise RuntimeError("scheduler_authorized must remain false")
        brb_dec = payload["promotion_decisions"].get("DCM-005-BRB")
        if brb_dec == "PROMOTE_RESTRICTED_TRUSTREPORT":
            raise RuntimeError("BRB must not be promoted")
        for row_id, decision in payload["promotion_decisions"].items():
            if "KFold" in row_id and decision == "PROMOTE_RESTRICTED_TRUSTREPORT":
                raise RuntimeError("KFold must not be promoted")
            if "Placebo" in row_id and decision == "PROMOTE_RESTRICTED_TRUSTREPORT":
                raise RuntimeError("Placebo must not be promoted")
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
