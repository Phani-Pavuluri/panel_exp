"""SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001 — null-monitor review decision runtime."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from panel_exp.validation.scm_jackknife_null_monitor_promotion_evidence_packet_runtime_001 import (
    CANONICAL_INSTRUMENT_IDENTITY,
    CATALOG_ALIAS,
    SCMJackknifeNullMonitorEvidenceReference,
    SCMJackknifeNullMonitorPacketReadinessStatus,
    SCMJackknifeNullMonitorPromotionEvidencePacket,
    SCMJackknifeNullMonitorPromotionEvidencePacketInput,
    SCMJackknifeNullMonitorPromotionReviewEligibilityStatus,
    assemble_scm_jackknife_null_monitor_promotion_evidence_packet,
)

_ARTIFACT_ID = "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001"
_SCOPE = "review_decision_runtime_no_promotion_no_claim_authorization"
_VERDICT = (
    "scm_jackknife_null_monitor_review_decision_runtime_implemented_no_promotion_no_claim_authorization"
)
_RECOMMENDED_NEXT = "METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001_summary.json"
)

_METHOD_VALIDITY_BLOCKER_MARKERS = (
    "failed_null_control_evidence",
    "failed_jackknife_stability_evidence",
    "failed_directional_error_evidence",
    "failed_donor_pool_diagnostics",
    "failed_pre_period_fit_diagnostics",
)

_PRODUCTION_SURFACES = frozenset(
    {
        "production",
        "production_readout",
        "production_compatibility",
        "prod_compatibility",
    }
)

_CATALOG_SURFACES = frozenset(
    {
        "catalog",
        "catalog_unblock",
        "catalog_promotion",
    }
)

_NULL_MONITOR_SURFACES = frozenset(
    {
        "null_monitor",
        "diagnostic_null_monitor",
        "restricted_review_null_monitor",
    }
)

_PROHIBITED_NEXT_ACTIONS = (
    "scm_promotion",
    "scm_jackknife_promotion",
    "method_promotion",
    "instrument_promotion",
    "catalog_unblock",
    "production_compatibility_authorization",
    "causal_lift_claim_authorization",
    "business_lift_claim_authorization",
    "confidence_interval_claim_authorization",
    "p_value_claim_authorization",
    "statistical_significance_claim_authorization",
    "statistical_power_claim_authorization",
    "roi_roas_claim_authorization",
    "decision_recommendation_authorization",
    "production_readout_authorization",
    "mip_decision_surface_approval",
    "trust_report_bypass",
    "claim_authorization_runtime_bypass",
)

_APPROVAL_ALLOWED_ACTIONS = (
    "continue_null_monitor_diagnostics",
    "prepare_null_monitor_governance_notes",
    "collect_additional_null_control_evidence",
    "collect_additional_scm_diagnostics",
    "open_catalog_governance_review_as_separate_lane",
    "open_production_compatibility_review_as_separate_lane",
)

_REQUEST_EVIDENCE_ALLOWED_ACTIONS = (
    "collect_missing_evidence_refs",
    "rerun_scm_jackknife_null_monitor_packet_runtime",
)

_CLAIM_AUTHORIZATION_STATUS = "NOT_AUTHORIZED_BY_THIS_DECISION"
_CATALOG_STATUS = "NOT_UNBLOCKED_BY_THIS_DECISION"
_PRODUCTION_COMPATIBILITY_STATUS = "NOT_AUTHORIZED_BY_THIS_DECISION"
_METHOD_PROMOTION_STATUS = "NOT_PROMOTED_BY_THIS_DECISION"
_INSTRUMENT_PROMOTION_STATUS = "NOT_PROMOTED_BY_THIS_DECISION"
_NULL_MONITOR_SCOPE_STATUS = "NULL_MONITOR_ONLY"


class SCMJackknifeNullMonitorReviewDecisionStatus(str, Enum):
    APPROVE_NULL_MONITOR_REVIEW_CONTINUATION = "APPROVE_NULL_MONITOR_REVIEW_CONTINUATION"
    REQUEST_ADDITIONAL_EVIDENCE = "REQUEST_ADDITIONAL_EVIDENCE"
    REJECT_FOR_METHOD_VALIDITY = "REJECT_FOR_METHOD_VALIDITY"
    REJECT_FOR_IDENTITY_MISMATCH = "REJECT_FOR_IDENTITY_MISMATCH"
    REJECT_FOR_CLAIM_BOUNDARY_VIOLATION = "REJECT_FOR_CLAIM_BOUNDARY_VIOLATION"
    REJECT_FOR_NULL_MONITOR_SCOPE_VIOLATION = "REJECT_FOR_NULL_MONITOR_SCOPE_VIOLATION"
    REJECT_FOR_UNSUPPORTED_SURFACE = "REJECT_FOR_UNSUPPORTED_SURFACE"
    REJECT_FOR_CROSS_INFERENCE_FAMILY = "REJECT_FOR_CROSS_INFERENCE_FAMILY"
    REJECT_FOR_CROSS_GEOMETRY = "REJECT_FOR_CROSS_GEOMETRY"
    REJECT_FOR_CROSS_ESTIMAND = "REJECT_FOR_CROSS_ESTIMAND"
    DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW = (
        "DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW"
    )
    DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW = "DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW"
    NO_DECISION_PACKET_NOT_READY = "NO_DECISION_PACKET_NOT_READY"


@dataclass(frozen=True)
class SCMJackknifeNullMonitorReviewDecisionInput:
    decision_id: str
    packet: SCMJackknifeNullMonitorPromotionEvidencePacket | dict[str, Any]
    requested_decision_surface: str = "null_monitor"
    reviewer_notes: str | None = None
    lineage: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    created_from_artifacts: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SCMJackknifeNullMonitorReviewDecision:
    decision_id: str
    instrument_identity: str
    catalog_alias: str | None
    decision_status: SCMJackknifeNullMonitorReviewDecisionStatus
    decision_scope: str
    decision_surface: str
    packet_ref: str
    evidence_summary: dict[str, Any]
    missing_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    required_followups: tuple[str, ...]
    allowed_next_actions: tuple[str, ...]
    prohibited_next_actions: tuple[str, ...]
    claim_authorization_status: str
    catalog_status: str
    production_compatibility_status: str
    method_promotion_status: str
    instrument_promotion_status: str
    null_monitor_scope_status: str
    warnings: tuple[str, ...]
    lineage: dict[str, Any]
    created_from_artifacts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["decision_status"] = self.decision_status.value
        return payload


def _normalize_surface(surface: str) -> str:
    return str(surface).strip().lower().replace("-", "_")


def _packet_view(
    packet: SCMJackknifeNullMonitorPromotionEvidencePacket | dict[str, Any],
) -> dict[str, Any]:
    if isinstance(packet, SCMJackknifeNullMonitorPromotionEvidencePacket):
        return packet.to_dict()
    return dict(packet)


def _enum_value(value: Any, enum_cls: type[Enum], default: Enum) -> Enum:
    if isinstance(value, enum_cls):
        return value
    text = str(value).strip()
    try:
        return enum_cls(text)
    except ValueError:
        return default


def _tuple_str(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return tuple(str(v) for v in value)
    if isinstance(value, list):
        return tuple(str(v) for v in value)
    return (str(value),)


def _has_method_validity_blocker(blockers: tuple[str, ...]) -> bool:
    lower_blockers = [b.lower() for b in blockers]
    return any(marker in blocker for blocker in lower_blockers for marker in _METHOD_VALIDITY_BLOCKER_MARKERS)


def _evidence_summary(packet: dict[str, Any]) -> dict[str, Any]:
    evidence_by_category = packet.get("evidence_by_category") or {}
    categories = sorted(str(k) for k in evidence_by_category.keys())
    return {
        "packet_id": packet.get("packet_id"),
        "evidence_category_count": len(categories),
        "evidence_categories_present": categories,
        "packet_readiness_status": str(packet.get("packet_readiness_status", "")),
        "promotion_review_eligibility_status": str(
            packet.get("promotion_review_eligibility_status", "")
        ),
        "missing_evidence_count": len(packet.get("missing_evidence") or ()),
        "blocker_count": len(packet.get("blockers") or ()),
    }


def _canonical_identity(packet: dict[str, Any]) -> str:
    identity = str(packet.get("instrument_identity", CANONICAL_INSTRUMENT_IDENTITY))
    if identity == CANONICAL_INSTRUMENT_IDENTITY:
        return CANONICAL_INSTRUMENT_IDENTITY
    return identity


def _catalog_alias(packet: dict[str, Any]) -> str | None:
    alias = packet.get("catalog_alias")
    if alias == CATALOG_ALIAS:
        return CATALOG_ALIAS
    return str(alias) if alias else None


def _base_decision_fields(
    inp: SCMJackknifeNullMonitorReviewDecisionInput,
    packet: dict[str, Any],
    *,
    decision_status: SCMJackknifeNullMonitorReviewDecisionStatus,
    decision_surface: str,
    required_followups: tuple[str, ...],
    allowed_next_actions: tuple[str, ...],
    extra_warnings: tuple[str, ...] = (),
) -> SCMJackknifeNullMonitorReviewDecision:
    packet_warnings = _tuple_str(packet.get("warnings"))
    input_warnings = tuple(inp.warnings)
    lineage = {**dict(packet.get("lineage") or {}), **dict(inp.lineage)}
    created = tuple(
        dict.fromkeys(
            list(inp.created_from_artifacts)
            + list(_tuple_str(packet.get("created_from_artifacts")))
            + [_ARTIFACT_ID]
        )
    )
    identity = _canonical_identity(packet)
    if decision_status == SCMJackknifeNullMonitorReviewDecisionStatus.APPROVE_NULL_MONITOR_REVIEW_CONTINUATION:
        identity = CANONICAL_INSTRUMENT_IDENTITY
    return SCMJackknifeNullMonitorReviewDecision(
        decision_id=inp.decision_id,
        instrument_identity=identity,
        catalog_alias=_catalog_alias(packet),
        decision_status=decision_status,
        decision_scope="null_monitor",
        decision_surface=decision_surface,
        packet_ref=str(packet.get("packet_id", "")),
        evidence_summary=_evidence_summary(packet),
        missing_evidence=_tuple_str(packet.get("missing_evidence")),
        blockers=_tuple_str(packet.get("blockers")),
        required_followups=required_followups,
        allowed_next_actions=allowed_next_actions,
        prohibited_next_actions=_PROHIBITED_NEXT_ACTIONS,
        claim_authorization_status=_CLAIM_AUTHORIZATION_STATUS,
        catalog_status=_CATALOG_STATUS,
        production_compatibility_status=_PRODUCTION_COMPATIBILITY_STATUS,
        method_promotion_status=_METHOD_PROMOTION_STATUS,
        instrument_promotion_status=_INSTRUMENT_PROMOTION_STATUS,
        null_monitor_scope_status=_NULL_MONITOR_SCOPE_STATUS,
        warnings=tuple(sorted(set(packet_warnings + input_warnings + extra_warnings))),
        lineage=lineage,
        created_from_artifacts=created,
    )


def decide_scm_jackknife_null_monitor_review(
    inp: SCMJackknifeNullMonitorReviewDecisionInput,
) -> SCMJackknifeNullMonitorReviewDecision:
    """Emit a governed SCM Jackknife null-monitor review decision from an assembled packet."""
    packet = _packet_view(inp.packet)
    requested_surface = _normalize_surface(inp.requested_decision_surface)

    if requested_surface in _PRODUCTION_SURFACES:
        return _base_decision_fields(
            inp,
            packet,
            decision_status=(
                SCMJackknifeNullMonitorReviewDecisionStatus.DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW
            ),
            decision_surface=requested_surface,
            required_followups=("open_production_compatibility_review_lane",),
            allowed_next_actions=("open_production_compatibility_review_as_separate_lane",),
        )

    if requested_surface in _CATALOG_SURFACES:
        return _base_decision_fields(
            inp,
            packet,
            decision_status=(
                SCMJackknifeNullMonitorReviewDecisionStatus.DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW
            ),
            decision_surface=requested_surface,
            required_followups=("open_catalog_governance_review_lane",),
            allowed_next_actions=("open_catalog_governance_review_as_separate_lane",),
        )

    if not packet or not packet.get("packet_id"):
        return _base_decision_fields(
            inp,
            packet or {},
            decision_status=SCMJackknifeNullMonitorReviewDecisionStatus.NO_DECISION_PACKET_NOT_READY,
            decision_surface=requested_surface,
            required_followups=("assemble_valid_scm_null_monitor_packet_first",),
            allowed_next_actions=("assemble_valid_scm_null_monitor_packet_first",),
        )

    readiness = _enum_value(
        packet.get("packet_readiness_status"),
        SCMJackknifeNullMonitorPacketReadinessStatus,
        SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_NOT_REQUESTED,
    )
    eligibility = _enum_value(
        packet.get("promotion_review_eligibility_status"),
        SCMJackknifeNullMonitorPromotionReviewEligibilityStatus,
        SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
    )
    missing = _tuple_str(packet.get("missing_evidence"))
    blockers = _tuple_str(packet.get("blockers"))

    if readiness == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_NOT_REQUESTED:
        return _base_decision_fields(
            inp,
            packet,
            decision_status=SCMJackknifeNullMonitorReviewDecisionStatus.NO_DECISION_PACKET_NOT_READY,
            decision_surface=requested_surface,
            required_followups=("assemble_valid_scm_null_monitor_packet_first",),
            allowed_next_actions=("assemble_valid_scm_null_monitor_packet_first",),
        )

    if (
        readiness == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH
        or eligibility
        == SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH
    ):
        return _base_decision_fields(
            inp,
            packet,
            decision_status=SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_IDENTITY_MISMATCH,
            decision_surface=requested_surface,
            required_followups=("repair_identity_or_scope",),
            allowed_next_actions=("repair_identity_or_scope",),
        )

    if readiness == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_CROSS_INFERENCE_FAMILY:
        return _base_decision_fields(
            inp,
            packet,
            decision_status=SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_CROSS_INFERENCE_FAMILY,
            decision_surface=requested_surface,
            required_followups=("separate_cross_instrument_review",),
            allowed_next_actions=("separate_cross_instrument_review",),
        )

    if readiness == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_CROSS_GEOMETRY:
        return _base_decision_fields(
            inp,
            packet,
            decision_status=SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_CROSS_GEOMETRY,
            decision_surface=requested_surface,
            required_followups=("separate_cross_instrument_review",),
            allowed_next_actions=("separate_cross_instrument_review",),
        )

    if readiness == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_CROSS_ESTIMAND:
        return _base_decision_fields(
            inp,
            packet,
            decision_status=SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_CROSS_ESTIMAND,
            decision_surface=requested_surface,
            required_followups=("separate_cross_instrument_review",),
            allowed_next_actions=("separate_cross_instrument_review",),
        )

    if (
        readiness == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING
        or eligibility
        == SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING
    ):
        return _base_decision_fields(
            inp,
            packet,
            decision_status=SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_CLAIM_BOUNDARY_VIOLATION,
            decision_surface=requested_surface,
            required_followups=("repair_claim_boundary",),
            allowed_next_actions=("repair_claim_boundary",),
        )

    if (
        readiness
        == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_NULL_MONITOR_SCOPE_VIOLATION
        or eligibility
        == SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_NULL_MONITOR_SCOPE_VIOLATION
        or eligibility
        == SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_CAUSAL_CLAIM_REVIEW
    ):
        return _base_decision_fields(
            inp,
            packet,
            decision_status=SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_NULL_MONITOR_SCOPE_VIOLATION,
            decision_surface=requested_surface,
            required_followups=("restrict_to_null_monitor_scope",),
            allowed_next_actions=("repair_identity_or_scope",),
        )

    if _has_method_validity_blocker(blockers):
        return _base_decision_fields(
            inp,
            packet,
            decision_status=SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_METHOD_VALIDITY,
            decision_surface=requested_surface,
            required_followups=("reject_or_rework_instrument_validation",),
            allowed_next_actions=("reject_or_rework_instrument_validation",),
        )

    if (
        missing
        or readiness
        == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE
        or readiness == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_PARTIAL_DIAGNOSTIC_ONLY
    ):
        followups: tuple[str, ...] = (
            "collect_missing_evidence_refs",
            "rerun_scm_jackknife_null_monitor_packet_runtime",
        )
        if missing:
            followups = followups + tuple(f"missing:{cat}" for cat in missing)
        return _base_decision_fields(
            inp,
            packet,
            decision_status=SCMJackknifeNullMonitorReviewDecisionStatus.REQUEST_ADDITIONAL_EVIDENCE,
            decision_surface=requested_surface,
            required_followups=followups,
            allowed_next_actions=_REQUEST_EVIDENCE_ALLOWED_ACTIONS,
        )

    if readiness == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE:
        return _base_decision_fields(
            inp,
            packet,
            decision_status=SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_UNSUPPORTED_SURFACE,
            decision_surface=requested_surface,
            required_followups=("restrict_scope_or_create_separate_review",),
            allowed_next_actions=("repair_identity_or_scope",),
        )

    if (
        readiness
        == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT
        and eligibility
        == SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT
        and requested_surface in _NULL_MONITOR_SURFACES
    ):
        followups = ()
        if inp.reviewer_notes:
            followups = ("continue_null_monitor_governance",)
        return _base_decision_fields(
            inp,
            packet,
            decision_status=(
                SCMJackknifeNullMonitorReviewDecisionStatus.APPROVE_NULL_MONITOR_REVIEW_CONTINUATION
            ),
            decision_surface=requested_surface,
            required_followups=followups,
            allowed_next_actions=_APPROVAL_ALLOWED_ACTIONS,
        )

    return _base_decision_fields(
        inp,
        packet,
        decision_status=SCMJackknifeNullMonitorReviewDecisionStatus.NO_DECISION_PACKET_NOT_READY,
        decision_surface=requested_surface,
        required_followups=("inspect_packet_status_and_requested_surface",),
        allowed_next_actions=("inspect_packet_status_and_requested_surface",),
    )


def _sample_packet() -> SCMJackknifeNullMonitorPromotionEvidencePacket:
    refs = [
        SCMJackknifeNullMonitorEvidenceReference(
            evidence_id=f"{cat}_001",
            evidence_category=cat,
            artifact_ref=f"docs/track_d/{cat.upper()}_001.md",
        )
        for cat in (
            "instrument_identity",
            "claim_boundary",
            "metric_estimand_alignment",
            "null_control_false_positive",
            "jackknife_stability",
            "directional_error",
            "donor_pool_diagnostics",
            "pre_period_fit_diagnostics",
            "sensitivity",
            "readout_compatibility",
        )
    ]
    return assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        SCMJackknifeNullMonitorPromotionEvidencePacketInput(
            packet_id="validation_sample_packet",
            catalog_alias=CATALOG_ALIAS,
            evidence_refs=refs,
            lineage={"runtime": _ARTIFACT_ID},
        )
    )


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=_REPO)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    packet = _sample_packet()
    decision = decide_scm_jackknife_null_monitor_review(
        SCMJackknifeNullMonitorReviewDecisionInput(
            decision_id="validation_sample_decision",
            packet=packet,
        )
    )
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.APPROVE_NULL_MONITOR_REVIEW_CONTINUATION
    )
    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "scm_jackknife_null_monitor_review_decision_runtime",
        "lane": "Lane A - Method instrument promotion framework application",
        "status": "completed",
        "scope": _SCOPE,
        "base_commit": _git_commit(),
        "instrument_identity": CANONICAL_INSTRUMENT_IDENTITY,
        "catalog_alias": CATALOG_ALIAS,
        "depends_on": [
            "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001",
            "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001",
            "METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001",
            "CLAIM_AUTHORIZATION_RUNTIME_001",
        ],
        "review_decision_runtime_implemented": True,
        "exact_instrument_identity_enforced": True,
        "catalog_alias_preserved_without_substitution": True,
        "decision_mapping_rules_implemented": True,
        "precedence_rules_implemented": True,
        "allowed_next_actions_emitted": True,
        "prohibited_next_actions_emitted": True,
        "fixed_non_authorization_statuses_emitted": True,
        "null_monitor_continuation_semantics_preserved": True,
        "missing_evidence_preserved": True,
        "blockers_preserved": True,
        "warnings_lineage_preserved": True,
        "evidence_quality_boundary_preserved": True,
        "runtime_implemented": True,
        "scm_promoted": False,
        "scm_jackknife_promoted": False,
        "method_promoted": False,
        "instrument_promoted": False,
        "catalog_unblocked": False,
        "production_compatibility_authorized": False,
        "claim_authorization_changed": False,
        "statistical_claim_authorized": False,
        "confidence_interval_claim_authorized": False,
        "p_value_claim_authorized": False,
        "significance_claim_authorized": False,
        "statistical_power_claim_authorized": False,
        "causal_lift_claim_authorized": False,
        "business_lift_claim_authorized": False,
        "roi_roas_claim_authorized": False,
        "decision_recommendation_authorized": False,
        "production_readout_authorized": False,
        "estimator_implemented": False,
        "inference_implemented": False,
        "new_validation_experiments_run": False,
        "raw_evidence_quality_scored": False,
        "lane_b_runtime_changed": False,
        "mip_decisioning_authorized": False,
        "trust_report_bypassed": False,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "final_verdict": _VERDICT,
        "validation_sample_decision_status": decision.decision_status.value,
    }
    if write_summary:
        path = summary_path or _DEFAULT_SUMMARY
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SCM Jackknife null-monitor review decision validation"
    )
    parser.add_argument("--write-summary", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    summary = run_validation(write_summary=args.write_summary, summary_path=args.summary_path)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
