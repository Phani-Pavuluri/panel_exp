"""TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001 — promotion review decision runtime."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from panel_exp.validation.tbrridge_promotion_evidence_packet_assembly_runtime_001 import (
    EXACT_INSTRUMENT_IDENTITY,
    TBRRidgePacketReadinessStatus,
    TBRRidgePromotionEvidencePacket,
    TBRRidgePromotionReviewEligibilityStatus,
    assemble_tbrridge_promotion_evidence_packet,
    TBRRidgePromotionEvidencePacketInput,
    TBRRidgeEvidenceReference,
)

_ARTIFACT_ID = "TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001"
_SCOPE = "review_decision_runtime_no_promotion_no_claim_authorization"
_VERDICT = "tbrridge_promotion_review_decision_runtime_implemented_no_promotion_no_claim_authorization"
_RECOMMENDED_NEXT = "METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001_summary.json"
)

_METHOD_VALIDITY_BLOCKER_MARKERS = (
    "FAILED_NULL_CONTROL_EVIDENCE",
    "FAILED_POSITIVE_CONTROL_RECOVERY",
    "FAILED_DIRECTIONAL_ERROR_EVIDENCE",
    "FAILED_METHOD_VALIDITY",
    "METHOD_VALIDITY_FAILURE",
    "BLOCKED_METHOD_VALIDITY",
)

_PRODUCTION_SURFACES = frozenset(
    {
        "production",
        "production_readout",
        "production_review",
        "production_compatibility",
        "prod_compatibility",
        "PRODUCTION_READOUT",
    }
)

_CATALOG_SURFACES = frozenset(
    {
        "catalog",
        "catalog_unblock",
        "catalog_governance",
        "CATALOG_UNBLOCK",
    }
)

_UNSUPPORTED_SURFACES = frozenset(
    {
        "promotion",
        "method_promotion",
        "instrument_promotion",
        "decision_recommendation",
        "production_readout",
    }
)

_PROHIBITED_NEXT_ACTIONS = (
    "method_promotion",
    "instrument_promotion",
    "catalog_unblock",
    "production_compatibility_authorization",
    "confidence_interval_claim_authorization",
    "p_value_claim_authorization",
    "statistical_significance_claim_authorization",
    "statistical_power_claim_authorization",
    "causal_lift_claim_authorization",
    "business_lift_claim_authorization",
    "roi_roas_claim_authorization",
    "decision_recommendation_authorization",
    "production_readout_authorization",
    "mip_decision_surface_approval",
    "trust_report_bypass",
    "claim_authorization_runtime_bypass",
)

_APPROVAL_ALLOWED_ACTIONS = (
    "continue_restricted_review_diagnostics",
    "prepare_restricted_review_governance_notes",
    "collect_more_validation_evidence",
    "open_production_compatibility_review_as_separate_lane",
    "open_catalog_governance_review_as_separate_lane",
)

_REQUEST_EVIDENCE_ALLOWED_ACTIONS = (
    "collect_missing_evidence_refs",
    "rerun_packet_assembly_runtime",
    "repair_artifact_references",
    "update_evidence_packet",
)

_CLAIM_AUTHORIZATION_STATUS = "NOT_AUTHORIZED_BY_THIS_DECISION"
_CATALOG_STATUS = "NOT_UNBLOCKED_BY_THIS_DECISION"
_PRODUCTION_COMPATIBILITY_STATUS = "NOT_AUTHORIZED_BY_THIS_DECISION"
_METHOD_PROMOTION_STATUS = "NOT_PROMOTED_BY_THIS_DECISION"
_INSTRUMENT_PROMOTION_STATUS = "NOT_PROMOTED_BY_THIS_DECISION"


class TBRRidgePromotionReviewDecisionStatus(str, Enum):
    APPROVE_RESTRICTED_REVIEW_CONTINUATION = "APPROVE_RESTRICTED_REVIEW_CONTINUATION"
    REQUEST_ADDITIONAL_EVIDENCE = "REQUEST_ADDITIONAL_EVIDENCE"
    REJECT_FOR_METHOD_VALIDITY = "REJECT_FOR_METHOD_VALIDITY"
    REJECT_FOR_IDENTITY_MISMATCH = "REJECT_FOR_IDENTITY_MISMATCH"
    REJECT_FOR_CLAIM_BOUNDARY_VIOLATION = "REJECT_FOR_CLAIM_BOUNDARY_VIOLATION"
    REJECT_FOR_UNSUPPORTED_SURFACE = "REJECT_FOR_UNSUPPORTED_SURFACE"
    REJECT_FOR_CROSS_INFERENCE_FAMILY = "REJECT_FOR_CROSS_INFERENCE_FAMILY"
    REJECT_FOR_CROSS_GEOMETRY = "REJECT_FOR_CROSS_GEOMETRY"
    DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW = (
        "DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW"
    )
    DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW = "DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW"
    NO_DECISION_PACKET_NOT_READY = "NO_DECISION_PACKET_NOT_READY"


@dataclass(frozen=True)
class TBRRidgePromotionReviewDecisionInput:
    decision_id: str
    packet: TBRRidgePromotionEvidencePacket | dict[str, Any]
    requested_decision_surface: str = "restricted_review"
    reviewer_notes: str | None = None
    lineage: dict[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    created_from_artifacts: tuple[str, ...] = ()


@dataclass(frozen=True)
class TBRRidgePromotionReviewDecision:
    decision_id: str
    instrument_identity: str
    decision_status: TBRRidgePromotionReviewDecisionStatus
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
    warnings: tuple[str, ...]
    lineage: dict[str, Any]
    created_from_artifacts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["decision_status"] = self.decision_status.value
        return payload


def _normalize_surface(surface: str) -> str:
    return str(surface).strip().lower().replace("-", "_")


def _packet_view(packet: TBRRidgePromotionEvidencePacket | dict[str, Any]) -> dict[str, Any]:
    if isinstance(packet, TBRRidgePromotionEvidencePacket):
        return packet.to_dict()
    return dict(packet)


def _enum_value(
    value: Any,
    enum_cls: type[Enum],
    default: Enum,
) -> Enum:
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
    upper_blockers = [b.upper() for b in blockers]
    return any(
        marker in blocker
        for blocker in upper_blockers
        for marker in _METHOD_VALIDITY_BLOCKER_MARKERS
    )


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


def _base_decision_fields(
    inp: TBRRidgePromotionReviewDecisionInput,
    packet: dict[str, Any],
    *,
    decision_status: TBRRidgePromotionReviewDecisionStatus,
    decision_surface: str,
    required_followups: tuple[str, ...],
    allowed_next_actions: tuple[str, ...],
    extra_warnings: tuple[str, ...] = (),
) -> TBRRidgePromotionReviewDecision:
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
    return TBRRidgePromotionReviewDecision(
        decision_id=inp.decision_id,
        instrument_identity=str(packet.get("instrument_identity", EXACT_INSTRUMENT_IDENTITY)),
        decision_status=decision_status,
        decision_scope="restricted_review",
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
        warnings=tuple(sorted(set(packet_warnings + input_warnings + extra_warnings))),
        lineage=lineage,
        created_from_artifacts=created,
    )


def decide_tbrridge_promotion_review(
    inp: TBRRidgePromotionReviewDecisionInput,
) -> TBRRidgePromotionReviewDecision:
    """Emit a governed TBRRidge promotion review decision from an assembled evidence packet."""
    packet = _packet_view(inp.packet)
    requested_surface = _normalize_surface(inp.requested_decision_surface)

    if not packet or not packet.get("packet_id"):
        return _base_decision_fields(
            inp,
            packet or {},
            decision_status=TBRRidgePromotionReviewDecisionStatus.NO_DECISION_PACKET_NOT_READY,
            decision_surface=requested_surface,
            required_followups=("assemble_valid_evidence_packet_first",),
            allowed_next_actions=("assemble_valid_evidence_packet_first",),
        )

    readiness = _enum_value(
        packet.get("packet_readiness_status"),
        TBRRidgePacketReadinessStatus,
        TBRRidgePacketReadinessStatus.PACKET_NOT_REQUESTED,
    )
    eligibility = _enum_value(
        packet.get("promotion_review_eligibility_status"),
        TBRRidgePromotionReviewEligibilityStatus,
        TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
    )
    missing = _tuple_str(packet.get("missing_evidence"))
    blockers = _tuple_str(packet.get("blockers"))

    if requested_surface in _PRODUCTION_SURFACES:
        return _base_decision_fields(
            inp,
            packet,
            decision_status=(
                TBRRidgePromotionReviewDecisionStatus.DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW
            ),
            decision_surface=requested_surface,
            required_followups=("open_production_compatibility_review_lane",),
            allowed_next_actions=("open_production_compatibility_review_as_separate_lane",),
        )

    if requested_surface in _CATALOG_SURFACES:
        return _base_decision_fields(
            inp,
            packet,
            decision_status=TBRRidgePromotionReviewDecisionStatus.DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW,
            decision_surface=requested_surface,
            required_followups=("open_catalog_governance_review_lane",),
            allowed_next_actions=("open_catalog_governance_review_as_separate_lane",),
        )

    if readiness == TBRRidgePacketReadinessStatus.PACKET_NOT_REQUESTED:
        return _base_decision_fields(
            inp,
            packet,
            decision_status=TBRRidgePromotionReviewDecisionStatus.NO_DECISION_PACKET_NOT_READY,
            decision_surface=requested_surface,
            required_followups=("assemble_valid_evidence_packet_first",),
            allowed_next_actions=("assemble_valid_evidence_packet_first",),
        )

    if readiness == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_CROSS_INFERENCE_FAMILY:
        return _base_decision_fields(
            inp,
            packet,
            decision_status=TBRRidgePromotionReviewDecisionStatus.REJECT_FOR_CROSS_INFERENCE_FAMILY,
            decision_surface=requested_surface,
            required_followups=("create_separate_instrument_lane",),
            allowed_next_actions=("create_separate_instrument_lane",),
        )

    if readiness == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_CROSS_GEOMETRY:
        return _base_decision_fields(
            inp,
            packet,
            decision_status=TBRRidgePromotionReviewDecisionStatus.REJECT_FOR_CROSS_GEOMETRY,
            decision_surface=requested_surface,
            required_followups=("create_separate_instrument_lane",),
            allowed_next_actions=("create_separate_instrument_lane",),
        )

    if (
        readiness == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH
        or eligibility == TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH
    ):
        return _base_decision_fields(
            inp,
            packet,
            decision_status=TBRRidgePromotionReviewDecisionStatus.REJECT_FOR_IDENTITY_MISMATCH,
            decision_surface=requested_surface,
            required_followups=("rebuild_packet_with_exact_identity",),
            allowed_next_actions=("rebuild_packet_with_exact_identity",),
        )

    if (
        readiness == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING
        or eligibility == TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING
    ):
        return _base_decision_fields(
            inp,
            packet,
            decision_status=TBRRidgePromotionReviewDecisionStatus.REJECT_FOR_CLAIM_BOUNDARY_VIOLATION,
            decision_surface=requested_surface,
            required_followups=("repair_claim_boundary_evidence",),
            allowed_next_actions=("repair_claim_boundary_evidence",),
        )

    if _has_method_validity_blocker(blockers):
        return _base_decision_fields(
            inp,
            packet,
            decision_status=TBRRidgePromotionReviewDecisionStatus.REJECT_FOR_METHOD_VALIDITY,
            decision_surface=requested_surface,
            required_followups=("repair_or_reject_instrument_validation",),
            allowed_next_actions=("repair_or_reject_instrument_validation",),
        )

    if (
        missing
        or readiness == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE
        or eligibility == TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE
    ):
        return _base_decision_fields(
            inp,
            packet,
            decision_status=TBRRidgePromotionReviewDecisionStatus.REQUEST_ADDITIONAL_EVIDENCE,
            decision_surface=requested_surface,
            required_followups=(
                "collect_missing_evidence_refs",
                "rerun_packet_assembly_runtime",
            ),
            allowed_next_actions=_REQUEST_EVIDENCE_ALLOWED_ACTIONS,
        )

    if (
        readiness == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE
        or eligibility == TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW
        or requested_surface in _UNSUPPORTED_SURFACES
        or requested_surface not in {"restricted_review"}
    ):
        return _base_decision_fields(
            inp,
            packet,
            decision_status=TBRRidgePromotionReviewDecisionStatus.REJECT_FOR_UNSUPPORTED_SURFACE,
            decision_surface=requested_surface,
            required_followups=("restrict_scope_or_create_separate_review",),
            allowed_next_actions=("restrict_scope_or_create_separate_review",),
        )

    if (
        readiness == TBRRidgePacketReadinessStatus.PACKET_READY_FOR_PROMOTION_REVIEW_INPUT
        and eligibility == TBRRidgePromotionReviewEligibilityStatus.ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT
        and requested_surface == "restricted_review"
    ):
        followups: tuple[str, ...] = ()
        if inp.reviewer_notes:
            followups = ("continue_restricted_review_governance",)
        return _base_decision_fields(
            inp,
            packet,
            decision_status=(
                TBRRidgePromotionReviewDecisionStatus.APPROVE_RESTRICTED_REVIEW_CONTINUATION
            ),
            decision_surface=requested_surface,
            required_followups=followups,
            allowed_next_actions=_APPROVAL_ALLOWED_ACTIONS,
        )

    return _base_decision_fields(
        inp,
        packet,
        decision_status=TBRRidgePromotionReviewDecisionStatus.NO_DECISION_PACKET_NOT_READY,
        decision_surface=requested_surface,
        required_followups=("assemble_valid_evidence_packet_first",),
        allowed_next_actions=("assemble_valid_evidence_packet_first",),
    )


def _sample_packet() -> TBRRidgePromotionEvidencePacket:
    refs = (
        TBRRidgeEvidenceReference(
            evidence_category="instrument_identity",
            artifact_id="METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001",
            artifact_ref="docs/track_d/METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="claim_boundary",
            artifact_id="TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001",
            artifact_ref="docs/track_d/TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="metric_estimand_alignment",
            artifact_id="TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001",
            artifact_ref="docs/track_d/TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="null_control_false_positive",
            artifact_id="TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001",
            artifact_ref="docs/track_d/TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="directional_error",
            artifact_id="TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001",
            artifact_ref="docs/track_d/TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="positive_control_recovery",
            artifact_id="TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001",
            artifact_ref="docs/track_d/TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="sensitivity",
            artifact_id="TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001",
            artifact_ref="docs/track_d/TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001.md",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="readout_compatibility",
            artifact_id="TRUSTED_READOUT_REPORT_RUNTIME_001",
            artifact_ref="panel_exp/validation/trusted_readout_report_runtime_001.py",
        ),
    )
    return assemble_tbrridge_promotion_evidence_packet(
        TBRRidgePromotionEvidencePacketInput(
            packet_id="validation_sample_packet",
            instrument_identity=EXACT_INSTRUMENT_IDENTITY,
            evidence_references=refs,
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
    decision = decide_tbrridge_promotion_review(
        TBRRidgePromotionReviewDecisionInput(
            decision_id="validation_sample_decision",
            packet=packet,
        )
    )
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.APPROVE_RESTRICTED_REVIEW_CONTINUATION
    )
    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "tbrridge_promotion_review_decision_runtime",
        "lane": "Lane A - Method instrument promotion",
        "status": "completed",
        "scope": _SCOPE,
        "base_commit": _git_commit(),
        "instrument_identity": EXACT_INSTRUMENT_IDENTITY,
        "depends_on": [
            "TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001",
            "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001",
            "TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001",
            "CLAIM_AUTHORIZATION_RUNTIME_001",
        ],
        "review_decision_runtime_implemented": True,
        "decision_mapping_rules_implemented": True,
        "packet_status_consumed": True,
        "promotion_review_eligibility_consumed": True,
        "missing_evidence_preserved": True,
        "blockers_preserved": True,
        "allowed_next_actions_emitted": True,
        "prohibited_next_actions_emitted": True,
        "fixed_non_authorization_statuses_emitted": True,
        "claim_authorization_relationship_preserved": True,
        "catalog_governance_relationship_preserved": True,
        "production_compatibility_relationship_preserved": True,
        "lane_b_relationship_preserved": True,
        "evidence_quality_boundary_preserved": True,
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
    parser = argparse.ArgumentParser(description="TBRRidge promotion review decision validation")
    parser.add_argument("--write-summary", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    summary = run_validation(write_summary=args.write_summary, summary_path=args.summary_path)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
