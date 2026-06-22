"""FULL-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001 — matrix-level TrustReport disposition.

Control-plane reassessment across governed DCM rows and open investigations.
Loads committed summary artifacts only; does not run new statistical simulations.
Does not authorize TrustReport unless every row-level and downstream gate passes.
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

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARCHIVE = _REPO_ROOT / "docs/track_d/archives"
_ARTIFACT_ID = "FULL-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001"
_ARTIFACT_VERSION = "1.0.0"
_DEFAULT_SUMMARY = _ARCHIVE / "FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json"
_DEFAULT_REPORT = _REPO_ROOT / "docs/track_d/FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md"

EligibilityDecision = Literal[
    "TRUSTREPORT_ELIGIBLE",
    "ELIGIBLE_WITH_RESTRICTIONS",
    "DIAGNOSTIC_ONLY",
    "NULL_MONITOR_ONLY",
    "INELIGIBLE",
    "DEFERRED_REMEDIATION",
    "INSUFFICIENT_EVIDENCE",
    "SUPERSEDED",
]

GovernanceVerdict = Literal[
    "full_trustreport_reassessment_no_global_authorization",
    "full_trustreport_reassessment_restricted_candidates_only",
    "full_trustreport_reassessment_inconclusive",
    "full_trustreport_reassessment_failed",
]

REQUIRED_INPUT_ARTIFACTS: dict[str, str] = {
    "prior_validation": "TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json",
    "dcm001_reassessment": "TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
    "dcm004_reassessment": "DCM004_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
    "dcm005_reassessment": "DCM005_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
    "dcm006_trust": "D5_TRUST_MULTICELL_PERCELL_INFERENCE_001_summary.json",
    "dcm008_trust": "D5_TRUST_STRATIFIED_SCM_JK_001_summary.json",
}

OPTIONAL_INPUT_ARTIFACTS: dict[str, str] = {
    "dcm005_brb_trust": "D5_TRUST_TBRRIDGE_BRB_001_summary.json",
    "dcm005_kfold_trust": "D5_TRUST_TBRRIDGE_KFOLD_001_summary.json",
    "dcm005_placebo_trust": "D5_TRUST_TBRRIDGE_PLACEBO_001_summary.json",
    "brb_correction": "TBRRIDGE_BRB_INTERVAL_CORRECTION_001_summary.json",
}

DEFERRED_INVESTIGATIONS = frozenset(
    {
        "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001",
        "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001",
    }
)

RESOLVE_AT_FULL_REASSESSMENT = frozenset(
    {
        "INV-SCM-PLACEBO-GOVERNED-SEMANTICS-001",
        "INV-AUGSYNTH-JK-TRUSTREPORT-DISPOSITION-001",
    }
)

ALREADY_RESOLVED = frozenset(
    {
        "INV-MULTICELL-PERCELL-INFERENCE-001",
        "INV-MULTICELL-CELL-RELATIONSHIP-DECISION-POLICY-001",
        "INV-STRATIFIED-SCM-JK-TRUSTREPORT-DISPOSITION-001",
        "INV-TBRRIDGE-KFOLD-NULL-FPR-001",
        "INV-TBRRIDGE-PLACEBO-GOVERNED-SEMANTICS-001",
    }
)


@dataclass(frozen=True)
class RowDecision:
    row_id: str
    design_family: str
    estimator: str
    inference_method: str
    geometry: str
    estimand: str
    readout_scope: str
    current_status: str
    prior_status: str
    evidence_artifacts: tuple[str, ...]
    open_investigations: tuple[str, ...] = ()
    blocking_investigations: tuple[str, ...] = ()
    deferred_investigations: tuple[str, ...] = ()
    statistical_decision: str = ""
    semantic_decision: str = ""
    production_role: str = "blocked"
    trustreport_eligibility: str = "INSUFFICIENT_EVIDENCE"
    downstream_authorization: bool = False
    calibration_signal_allowed: bool = False
    promotion_candidate: bool = False
    restrictions: tuple[str, ...] = ()
    required_warnings: tuple[str, ...] = ()
    next_action: str = ""
    trust_report_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReassessmentConfig:
    strict: bool = True
    registry_path: Path | None = None


def _git_commit() -> str | None:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_REPO_ROOT, stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_artifacts(*, strict: bool) -> tuple[dict[str, Any], dict[str, str]]:
    loaded: dict[str, Any] = {}
    paths: dict[str, str] = {}
    for key, fname in REQUIRED_INPUT_ARTIFACTS.items():
        path = _ARCHIVE / fname
        if strict and not path.is_file():
            raise FileNotFoundError(f"Required input missing: {path}")
        if path.is_file():
            loaded[key] = _load_json(path)
            paths[key] = str(path.relative_to(_REPO_ROOT))
    for key, fname in OPTIONAL_INPUT_ARTIFACTS.items():
        path = _ARCHIVE / fname
        if path.is_file():
            loaded[key] = _load_json(path)
            paths[key] = str(path.relative_to(_REPO_ROOT))
    return loaded, paths


def _prior_row(prior_validation: dict[str, Any], combination_key: str) -> dict[str, Any]:
    for row in prior_validation.get("combination_results") or []:
        if row.get("combination_key") == combination_key:
            return row
    return {}


def _assert_no_auth(summary: dict[str, Any], label: str) -> None:
    auth = summary.get("authorization_summary") or {}
    if auth.get("trust_report_authorized") is True or auth.get("trust_report_ready") is True:
        raise ValueError(f"{label} unexpectedly authorizes TrustReport")


def _row_dcm001(artifacts: dict[str, Any]) -> RowDecision:
    prior = _prior_row(artifacts["prior_validation"], "DCM-001")
    reassess = artifacts["dcm001_reassessment"]
    _assert_no_auth(reassess, "DCM-001 reassessment")
    status = str(reassess.get("dcm_001_reassessed_status") or "ELIGIBLE_WITH_RESTRICTIONS")
    return RowDecision(
        row_id="DCM-001",
        design_family="single_cell",
        estimator="scm",
        inference_method="unit_jackknife",
        geometry="unit_panel_single_cell",
        estimand="treated_unit_effect_level",
        readout_scope="restricted_causal_interval",
        current_status=status,
        prior_status=str(prior.get("eligibility_status") or "ELIGIBLE_WITH_RESTRICTIONS"),
        evidence_artifacts=(
            "TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
            "D5-STAT-SCM-JK-001",
        ),
        statistical_decision=status,
        semantic_decision="restricted_causal_interval_level_scale",
        production_role="restricted_research",
        trustreport_eligibility="ELIGIBLE_WITH_RESTRICTIONS",
        downstream_authorization=False,
        calibration_signal_allowed=False,
        promotion_candidate=False,
        restrictions=(
            "support_gated",
            "prefit_warning_required",
            "population_ate_blocked",
            "no_trustreport_authorization",
        ),
        required_warnings=("noisy_world_coverage_caveat", "type_i_caveat"),
        next_action="TRUSTREPORT_DOWNSTREAM_PROMOTION_001 if gates pass; else remain blocked",
    )


def _row_dcm002(artifacts: dict[str, Any]) -> RowDecision:
    prior = _prior_row(artifacts["prior_validation"], "DCM-002")
    return RowDecision(
        row_id="DCM-002",
        design_family="single_cell",
        estimator="augsynth",
        inference_method="unit_jackknife",
        geometry="unit_panel_single_cell",
        estimand="descriptive_point",
        readout_scope="point_and_unvalidated_interval",
        current_status="DIAGNOSTIC_ONLY",
        prior_status=str(prior.get("eligibility_status") or "ELIGIBLE_WITH_RESTRICTIONS"),
        evidence_artifacts=("TRUSTREPORT-ELIGIBILITY-VALIDATION-001",),
        open_investigations=(),
        blocking_investigations=("INV-AUGSYNTH-JK-TRUSTREPORT-DISPOSITION-001",),
        statistical_decision="INSUFFICIENT_CAUSAL_INTERVAL_EVIDENCE",
        semantic_decision="descriptive_point_only",
        production_role="diagnostic_only",
        trustreport_eligibility="DIAGNOSTIC_ONLY",
        restrictions=(
            "jk_causal_interval_not_validated",
            "no_trustreport_promotion",
            "calibration_signal_blocked",
        ),
        required_warnings=("interval_semantics_not_causal",),
        next_action="Optional ASCM-003 calibration lane; no TrustReport path",
    )


def _row_dcm003(artifacts: dict[str, Any]) -> RowDecision:
    prior = _prior_row(artifacts["prior_validation"], "DCM-003")
    return RowDecision(
        row_id="DCM-003",
        design_family="single_cell",
        estimator="tbr",
        inference_method="aggregate",
        geometry="unit_panel_single_cell",
        estimand="aggregate_att",
        readout_scope="geometry_mismatch",
        current_status="INELIGIBLE",
        prior_status=str(prior.get("eligibility_status") or "INELIGIBLE"),
        evidence_artifacts=("TRUSTREPORT-ELIGIBILITY-VALIDATION-001",),
        statistical_decision="GEOMETRY_MISMATCH",
        semantic_decision="aggregate_estimator_on_unit_panel_blocked",
        production_role="blocked",
        trustreport_eligibility="INELIGIBLE",
        restrictions=("permanent_geometry_block",),
        next_action="Use class TBR on aggregate 1x1 geometry only",
    )


def _row_dcm004(artifacts: dict[str, Any]) -> RowDecision:
    prior = _prior_row(artifacts["prior_validation"], "DCM-004")
    reassess = artifacts["dcm004_reassessment"]
    _assert_no_auth(reassess, "DCM-004 reassessment")
    status = str(reassess.get("reassessed_status") or "ELIGIBLE_WITH_RESTRICTIONS")
    return RowDecision(
        row_id="DCM-004",
        design_family="single_cell",
        estimator="did",
        inference_method="bootstrap",
        geometry="unit_panel_single_cell",
        estimand="cumulative_att_level",
        readout_scope="restricted_causal_interval",
        current_status=status,
        prior_status=str(prior.get("eligibility_status") or "INSUFFICIENT_EVIDENCE"),
        evidence_artifacts=(
            "DCM-004-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
            "D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001",
        ),
        statistical_decision=status,
        semantic_decision="restricted_causal_interval_common_timing",
        production_role="restricted_research",
        trustreport_eligibility="ELIGIBLE_WITH_RESTRICTIONS",
        restrictions=(
            "common_simultaneous_adoption_only",
            "parallel_trends_violation_excluded",
            "staggered_pooled_blocked",
            "no_trustreport_authorization",
        ),
        required_warnings=("unsupported_worlds_excluded",),
        next_action="TRUSTREPORT_DOWNSTREAM_PROMOTION_001 if gates pass; else remain blocked",
    )


def _row_dcm005_path(
    path: dict[str, Any],
    *,
    prior_validation: dict[str, Any],
) -> RowDecision:
    path_id = str(path["path_id"])
    prior = _prior_row(prior_validation, path_id)
    elig = str(path.get("trustreport_eligibility_status") or "INSUFFICIENT_EVIDENCE")
    trust_elig: EligibilityDecision
    if elig == "INELIGIBLE_FOR_CAUSAL_INTERVAL":
        trust_elig = "DEFERRED_REMEDIATION"
    elif elig == "DIAGNOSTIC_ONLY":
        trust_elig = "DIAGNOSTIC_ONLY"
    elif elig == "NULL_MONITOR_ONLY":
        trust_elig = "NULL_MONITOR_ONLY"
    else:
        trust_elig = "INSUFFICIENT_EVIDENCE"
    inv = path.get("investigation_id")
    deferred = (inv,) if inv in DEFERRED_INVESTIGATIONS else ()
    blocking = deferred if trust_elig in ("DEFERRED_REMEDIATION", "INELIGIBLE") else ()
    return RowDecision(
        row_id=path_id,
        design_family="single_cell",
        estimator=str(path.get("estimator_id") or "tbrridge"),
        inference_method=str(path.get("inference_id") or ""),
        geometry="unit_panel_single_cell",
        estimand="unit_level_relative_percent",
        readout_scope=str(path.get("semantic_class") or ""),
        current_status=elig,
        prior_status=str(prior.get("eligibility_status") or "INSUFFICIENT_EVIDENCE"),
        evidence_artifacts=("DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",),
        deferred_investigations=deferred,
        blocking_investigations=blocking,
        statistical_decision=str(path.get("statistical_status") or ""),
        semantic_decision=str(path.get("semantic_class") or ""),
        production_role=str(path.get("production_role") or "blocked"),
        trustreport_eligibility=trust_elig,
        restrictions=tuple(path.get("restrictions") or ()),
        required_warnings=tuple(path.get("reason_codes") or ()),
        next_action=(
            "TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001"
            if path_id == "DCM-005-BRB"
            else "no_promotion"
        ),
    )


def _row_dcm006(artifacts: dict[str, Any]) -> RowDecision:
    prior = _prior_row(artifacts["prior_validation"], "DCM-006")
    trust = artifacts["dcm006_trust"]
    _assert_no_auth(trust, "DCM-006 trust")
    return RowDecision(
        row_id="DCM-006",
        design_family="multi_cell",
        estimator="scm",
        inference_method="unit_jackknife",
        geometry="multi_cell_per_cell",
        estimand="per_cell_level_mean_relative_percent",
        readout_scope="per_cell_marginal_only",
        current_status="PER_CELL_RESTRICTED",
        prior_status=str(prior.get("eligibility_status") or "ELIGIBLE_WITH_RESTRICTIONS"),
        evidence_artifacts=(
            "D5-TRUST-MULTICELL-PERCELL-INFERENCE-001",
            "MULTICELL-CELL-RELATIONSHIP-AND-DECISION-POLICY-CONTRACT-001",
        ),
        deferred_investigations=(
            "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001",
            "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001",
        ),
        blocking_investigations=(
            "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001",
            "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001",
        ),
        statistical_decision="multicell_percell_multiplicity_unresolved",
        semantic_decision="parallel_marginal_per_cell_only",
        production_role="per_cell_diagnostic_restricted",
        trustreport_eligibility="ELIGIBLE_WITH_RESTRICTIONS",
        restrictions=(
            "PARALLEL_MARGINAL_CELLS+REPORT_EACH_CELL_ONLY",
            "familywise_decisioning_blocked",
            "winner_ranking_any_cell_pooled_global_blocked",
            "shared_control_warning_required",
            "no_trustreport_global_decision",
        ),
        required_warnings=(
            "familywise_null_type_i_elevated",
            "shared_control_dependence_deferred",
        ),
        next_action="Deferred multiplicity/shared-control remediation before promotion",
    )


def _row_dcm007(artifacts: dict[str, Any]) -> RowDecision:
    prior = _prior_row(artifacts["prior_validation"], "DCM-007")
    return RowDecision(
        row_id="DCM-007",
        design_family="multi_cell",
        estimator="any",
        inference_method="any",
        geometry="pooled_multicell",
        estimand="pooled_multicell_causal",
        readout_scope="blocked",
        current_status="INELIGIBLE",
        prior_status=str(prior.get("eligibility_status") or "INELIGIBLE"),
        evidence_artifacts=("TRUSTREPORT-ELIGIBILITY-VALIDATION-001",),
        statistical_decision="PERMANENTLY_BLOCKED",
        semantic_decision="pooled_multicell_not_supported",
        production_role="blocked",
        trustreport_eligibility="INELIGIBLE",
        restrictions=("permanent_exclusion",),
        next_action="No pooled multi-cell causal readout",
    )


def _row_dcm008(artifacts: dict[str, Any]) -> RowDecision:
    prior = _prior_row(artifacts["prior_validation"], "DCM-008")
    trust = artifacts["dcm008_trust"]
    _assert_no_auth(trust, "DCM-008 trust")
    return RowDecision(
        row_id="DCM-008",
        design_family="stratified",
        estimator="scm",
        inference_method="unit_jackknife",
        geometry="stratified_unit_panel",
        estimand="per_stratum_level_mean_relative_percent",
        readout_scope="per_stratum_diagnostic_aggregate_characterization_only",
        current_status="DIAGNOSTIC_ONLY",
        prior_status=str(prior.get("eligibility_status") or "ELIGIBLE_WITH_RESTRICTIONS"),
        evidence_artifacts=("D5-TRUST-STRATIFIED-SCM-JK-001",),
        statistical_decision="stratified_scm_jk_diagnostic_only",
        semantic_decision="aggregate_characterization_not_pooled_estimand",
        production_role="diagnostic_only",
        trustreport_eligibility="DIAGNOSTIC_ONLY",
        restrictions=(
            "per_stratum_diagnostic_or_restricted_display_only",
            "aggregate_stratified_readout_characterization_only_not_governed_pooled_causal_estimand",
            "within_stratum_donor_pool_preferred",
            "small_stratum_support_limited",
            "no_trustreport_authorization",
        ),
        required_warnings=(
            "aggregate_intervals_not_valid_pooled_estimand",
            "weight_dominance_and_small_stratum_caveats",
        ),
        next_action="Pooled stratified estimand artifact required before aggregate causal claims",
    )


def _row_scm_placebo() -> RowDecision:
    return RowDecision(
        row_id="SCM-PLACEBO",
        design_family="single_cell",
        estimator="scm",
        inference_method="placebo",
        geometry="unit_panel_single_cell",
        estimand="null_monitor",
        readout_scope="null_monitor_only",
        current_status="NULL_MONITOR_ONLY",
        prior_status="INELIGIBLE",
        evidence_artifacts=("TRUSTREPORT-ELIGIBILITY-VALIDATION-001",),
        statistical_decision="NULL_MONITOR_ACCEPTABLE",
        semantic_decision="null_monitor_not_causal_interval",
        production_role="null_monitor",
        trustreport_eligibility="NULL_MONITOR_ONLY",
        restrictions=(
            "no_causal_interval_relabeling",
            "calibration_signal_blocked",
            "no_trustreport_authorization",
        ),
        next_action="Governed null-monitor export only",
    )


def _registry_insufficient_rows() -> list[RowDecision]:
    extras = (
        ("DCM-009", "adapter_required"),
        ("DCM-010", "readout_mismatch"),
        ("DCM-011", "bridge_required"),
        ("DCM-012", "research_only"),
        ("DCM-013", "geometry_bridge"),
        ("DCM-014", "not_characterized"),
        ("DCM-015", "not_characterized"),
        ("DCM-016", "geometry_bridge"),
        ("DCM-017", "not_characterized"),
        ("DCM-018", "not_characterized"),
        ("DCM-019", "not_characterized"),
    )
    rows: list[RowDecision] = []
    for row_id, note in extras:
        rows.append(
            RowDecision(
                row_id=row_id,
                design_family="various",
                estimator="various",
                inference_method="various",
                geometry="various",
                estimand="not_executed",
                readout_scope="not_characterized",
                current_status="INSUFFICIENT_EVIDENCE",
                prior_status="INSUFFICIENT_EVIDENCE",
                evidence_artifacts=(),
                trustreport_eligibility="INSUFFICIENT_EVIDENCE",
                restrictions=(f"registry_note:{note}",),
                next_action="Dedicated validation artifact required",
            )
        )
    return rows


def _investigation_consumption(registry: dict[str, Any]) -> dict[str, Any]:
    by_id = {i["investigation_id"]: i for i in registry.get("investigations") or []}
    consumption: dict[str, Any] = {}
    for inv_id, inv in by_id.items():
        status = inv.get("status")
        if inv_id in ALREADY_RESOLVED:
            classification = "resolved_by_prior_artifacts"
        elif inv_id in RESOLVE_AT_FULL_REASSESSMENT:
            classification = "resolved_by_this_artifact"
        elif inv_id in DEFERRED_INVESTIGATIONS:
            classification = "deferred_with_trigger"
        elif status == "OPEN":
            classification = "still_open"
        elif status == "RESOLVED":
            classification = "resolved_by_prior_artifacts"
        elif status == "DEFERRED_WITH_TRIGGER":
            classification = "deferred_with_trigger"
        else:
            classification = "nonblocking_for_current_role"
        consumption[inv_id] = {
            "status": status,
            "classification": classification,
            "affected_combination": inv.get("affected_combination"),
            "blocking_for_trustreport": inv_id in DEFERRED_INVESTIGATIONS
            or (
                inv_id in RESOLVE_AT_FULL_REASSESSMENT
                and classification != "resolved_by_this_artifact"
            ),
            "current_decision": inv.get("current_decision"),
        }
    return consumption


def build_full_trustreport_eligibility_reassessment_001(
    cfg: ReassessmentConfig | None = None,
) -> dict[str, Any]:
    cfg = cfg or ReassessmentConfig()
    artifacts, input_paths = _load_artifacts(strict=cfg.strict)
    registry = load_registry(cfg.registry_path)

    rows: list[RowDecision] = [
        _row_dcm001(artifacts),
        _row_dcm002(artifacts),
        _row_dcm003(artifacts),
        _row_dcm004(artifacts),
        _row_dcm006(artifacts),
        _row_dcm007(artifacts),
        _row_dcm008(artifacts),
        _row_scm_placebo(),
    ]
    for path in artifacts["dcm005_reassessment"].get("path_decisions") or []:
        rows.append(_row_dcm005_path(path, prior_validation=artifacts["prior_validation"]))
    rows.extend(_registry_insufficient_rows())

    if cfg.strict:
        for row in rows:
            if not row.trustreport_eligibility:
                raise ValueError(f"Row {row.row_id} missing trustreport_eligibility decision")

    row_dicts = [r.to_dict() for r in rows]
    inv_consumption = _investigation_consumption(registry)

    resolved_here = sorted(RESOLVE_AT_FULL_REASSESSMENT)
    resolved_prior = sorted(ALREADY_RESOLVED)
    deferred = sorted(DEFERRED_INVESTIGATIONS)
    blocking = sorted(
        inv for inv, meta in inv_consumption.items() if meta.get("blocking_for_trustreport")
    )

    promotion_candidates = [
        r.row_id
        for r in rows
        if r.trustreport_eligibility in ("TRUSTREPORT_ELIGIBLE", "ELIGIBLE_WITH_RESTRICTIONS")
        and r.promotion_candidate
    ]
    blocked_candidates = [
        r.row_id for r in rows if r.trustreport_eligibility not in ("TRUSTREPORT_ELIGIBLE",)
    ]

    def _filter_rows(decisions: frozenset[str]) -> list[str]:
        return [r.row_id for r in rows if r.trustreport_eligibility in decisions]

    global_auth = False
    if any(r.trust_report_authorized for r in rows):
        raise ValueError("Row-level TrustReport authorization true while blockers remain")
    if blocking and global_auth:
        raise ValueError("Global TrustReport authorization incompatible with blocking investigations")

    has_restricted = any(
        r.trustreport_eligibility == "ELIGIBLE_WITH_RESTRICTIONS" for r in rows
    )
    verdict: GovernanceVerdict = (
        "full_trustreport_reassessment_restricted_candidates_only"
        if has_restricted and not promotion_candidates
        else "full_trustreport_reassessment_no_global_authorization"
    )

    next_artifact = (
        "TRUSTREPORT_DOWNSTREAM_PROMOTION_001"
        if promotion_candidates
        else "TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001"
    )

    summary: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "input_artifacts": input_paths,
        "dcm_rows": [r.row_id for r in rows],
        "row_decisions": row_dicts,
        "eligibility_matrix": {
            r.row_id: {
                "trustreport_eligibility": r.trustreport_eligibility,
                "production_role": r.production_role,
                "downstream_authorization": r.downstream_authorization,
                "promotion_candidate": r.promotion_candidate,
            }
            for r in rows
        },
        "authorization_matrix": {
            r.row_id: {
                "trust_report_authorized": r.trust_report_authorized,
                "downstream_authorization": r.downstream_authorization,
            }
            for r in rows
        },
        "calibration_signal_matrix": {
            r.row_id: r.calibration_signal_allowed for r in rows
        },
        "open_investigation_consumption": inv_consumption,
        "resolved_investigations": resolved_prior + resolved_here,
        "deferred_investigations": deferred,
        "blocking_investigations": blocking,
        "trustreport_authorization_summary": {
            "trust_report_authorized": global_auth,
            "trust_report_ready": False,
            "trust_report_authorized_count": 0,
            "blocking_investigation_count": len(blocking),
            "rationale": (
                "No row passes all TrustReport gates; deferred remediation and "
                "diagnostic/null-monitor semantics block global authorization"
            ),
        },
        "downstream_authorization_summary": {
            "any_downstream_authorized": any(r.downstream_authorization for r in rows),
            "research_restricted_rows": [
                r.row_id
                for r in rows
                if r.trustreport_eligibility == "ELIGIBLE_WITH_RESTRICTIONS"
            ],
        },
        "promotion_candidates": promotion_candidates,
        "blocked_candidates": blocked_candidates,
        "diagnostic_only_rows": _filter_rows(frozenset({"DIAGNOSTIC_ONLY"})),
        "null_monitor_only_rows": _filter_rows(frozenset({"NULL_MONITOR_ONLY"})),
        "ineligible_rows": _filter_rows(frozenset({"INELIGIBLE"})),
        "deferred_remediation_rows": _filter_rows(frozenset({"DEFERRED_REMEDIATION"})),
        "insufficient_evidence_rows": _filter_rows(frozenset({"INSUFFICIENT_EVIDENCE"})),
        "governance_verdict": verdict,
        "investigation_handoff": build_investigation_handoff(
            follow_up_issues=sorted(deferred),
            resolved_issues=resolved_prior + resolved_here,
            terminal_dispositions=resolved_prior + resolved_here,
            next_artifact=next_artifact,
        ),
        "limitations": [
            "Matrix-level reassessment only; no new statistical simulations.",
            "Does not remediate deferred statistical defects.",
            "Deferred remediation lanes remain blocked until target artifacts complete.",
            "DCM-008 aggregate stratified readout is characterization only, not a governed pooled causal estimand.",
            "DCM-006 familywise/multiplicity/shared-control lanes remain deferred.",
            "Global TrustReport authorization remains false.",
        ],
        "next_artifact": next_artifact,
        "verdict": verdict,
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


def _write_report(payload: dict[str, Any], path: Path, *, overwrite: bool = False) -> None:
    handoff = payload.get("investigation_handoff") or {}
    lines = [
        f"# {_ARTIFACT_ID} Report",
        "",
        "## 1. Executive summary",
        "",
        "This artifact performs a matrix-level TrustReport eligibility reassessment.",
        "It does not introduce new estimator, inference, or design algorithms.",
        "It does not remediate deferred statistical defects.",
        "It does not authorize TrustReport unless every required row-level and downstream gate passes.",
        "Deferred remediation lanes remain blocked until their target artifacts complete.",
        "",
        f"**Governance verdict:** `{payload.get('governance_verdict')}`",
        f"**Global TrustReport authorized:** `{payload.get('trustreport_authorization_summary', {}).get('trust_report_authorized')}`",
        "",
        "## 2. Scope",
        "",
        "All governed DCM rows and disposition paths after DCM-001/004/005/006/008 trust lanes.",
        "",
        "## 3. Non-goals",
        "",
        "No new simulations; no production algorithm changes; no silent promotion.",
        "",
        "## 4. Input artifacts",
        "",
        json.dumps(payload.get("input_artifacts", {}), indent=2),
        "",
        "## 5. Decision rules",
        "",
        "TrustReport requires statistical calibration, estimand alignment, valid interval semantics, "
        "geometry support, governed readout scope, no blocking investigations, and downstream authorization.",
        "",
        "## 6. DCM matrix overview",
        "",
        json.dumps(payload.get("eligibility_matrix", {}), indent=2)[:4000],
        "",
        "## 7. Row-by-row decisions",
        "",
        f"{len(payload.get('row_decisions', []))} rows characterized.",
        "",
        "## 8. DCM-001 decision",
        "",
        "ELIGIBLE_WITH_RESTRICTIONS; no TrustReport authorization.",
        "",
        "## 9. DCM-004 decision",
        "",
        "ELIGIBLE_WITH_RESTRICTIONS under supported parallel-timing contract; no TrustReport authorization.",
        "",
        "## 10. DCM-005 decisions",
        "",
        "BRB: DEFERRED_REMEDIATION; KFold: DIAGNOSTIC_ONLY; Placebo: NULL_MONITOR_ONLY.",
        "",
        "## 11. DCM-006 decision",
        "",
        "ELIGIBLE_WITH_RESTRICTIONS for parallel marginal per-cell readouts only; "
        "familywise/winner/pooled/global blocked; deferred shared-control and multiplicity lanes.",
        "",
        "## 12. DCM-008 decision",
        "",
        "DIAGNOSTIC_ONLY. Aggregate stratified readout is characterization only, "
        "not a governed pooled causal estimand.",
        "",
        "## 13. SCM Placebo disposition",
        "",
        "NULL_MONITOR_ONLY; investigation resolved at full reassessment.",
        "",
        "## 14. AugSynth JK disposition",
        "",
        "DIAGNOSTIC_ONLY / descriptive point; investigation resolved at full reassessment.",
        "",
        "## 15. Deferred remediation lanes",
        "",
        ", ".join(payload.get("deferred_investigations", [])),
        "",
        "## 16. Diagnostic-only lanes",
        "",
        ", ".join(payload.get("diagnostic_only_rows", [])),
        "",
        "## 17. Null-monitor-only lanes",
        "",
        ", ".join(payload.get("null_monitor_only_rows", [])),
        "",
        "## 18. Ineligible lanes",
        "",
        ", ".join(payload.get("ineligible_rows", [])),
        "",
        "## 19. Insufficient-evidence lanes",
        "",
        ", ".join(payload.get("insufficient_evidence_rows", [])),
        "",
        "## 20. CalibrationSignal implications",
        "",
        "CalibrationSignal remains blocked for all rows in current matrix.",
        "",
        "## 21. TrustReport implications",
        "",
        json.dumps(payload.get("trustreport_authorization_summary", {}), indent=2),
        "",
        "## 22. Downstream authorization implications",
        "",
        json.dumps(payload.get("downstream_authorization_summary", {}), indent=2),
        "",
        "## 23. Open investigation consumption",
        "",
        json.dumps(payload.get("open_investigation_consumption", {}), indent=2)[:6000],
        "",
        "## 24. Promotion candidates",
        "",
        json.dumps(payload.get("promotion_candidates", [])),
        "",
        "## 25. Blocked candidates",
        "",
        f"{len(payload.get('blocked_candidates', []))} rows blocked from TrustReport promotion.",
        "",
        "## 26. Governance verdict",
        "",
        f"**`{payload.get('governance_verdict')}`**",
        "",
    ]
    lines.extend(
        format_handoff_report_section(
            resolved_in_artifact=sorted(RESOLVE_AT_FULL_REASSESSMENT),
            new_investigations=[],
            updated_investigations=[
                f"{i} → RESOLVED at full reassessment" for i in sorted(RESOLVE_AT_FULL_REASSESSMENT)
            ],
            deferred_issues=sorted(DEFERRED_INVESTIGATIONS),
            explicit_exclusions=["No new statistical simulations in this artifact"],
            revisit_trigger="After deferred remediation lanes or promotion gate review",
            decision_checkpoint="TRUSTREPORT_DOWNSTREAM_PROMOTION_001",
            next_artifact=handoff.get("next_artifact"),
        )
    )
    _atomic_write(path, "\n".join(lines) + "\n", overwrite=overwrite)


def write_summary(
    path: Path | None = None,
    *,
    cfg: ReassessmentConfig | None = None,
    overwrite: bool = False,
    report_path: Path | None = None,
) -> Path:
    payload = build_full_trustreport_eligibility_reassessment_001(cfg)
    if path is None:
        path = _DEFAULT_SUMMARY
    _atomic_write(path, json.dumps(payload, indent=2) + "\n", overwrite=overwrite)
    _write_report(payload, report_path or _DEFAULT_REPORT, overwrite=overwrite)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--summary-output", default=str(_DEFAULT_SUMMARY))
    parser.add_argument("--report-output", default=str(_DEFAULT_REPORT))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true", default=True)
    parser.add_argument("--no-strict", action="store_false", dest="strict")
    args = parser.parse_args(argv)
    write_summary(
        Path(args.summary_output),
        cfg=ReassessmentConfig(strict=args.strict),
        overwrite=args.overwrite,
        report_path=Path(args.report_output),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
