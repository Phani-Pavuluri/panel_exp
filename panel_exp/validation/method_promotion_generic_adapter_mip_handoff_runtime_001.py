"""METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001 — package-side MIP handoff builder."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from panel_exp.validation.method_promotion_generic_runtime_001 import (
    AUGSYNTH_ADAPTER_PROFILE,
    MethodPromotionGovernanceSummary,
    SCM_NULL_MONITOR_ADAPTER_PROFILE,
    TBRRIDGE_ADAPTER_PROFILE,
    _resolve_profile,
)

_ARTIFACT_ID = "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001"
_SCOPE = "package_side_handoff_runtime_no_mip_runtime_no_decision_authorization"
_VERDICT = (
    "package_side_mip_handoff_runtime_implemented_no_mip_runtime_no_decision_authorization"
)
_RECOMMENDED_NEXT = (
    "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001_summary.json"
)
_SOURCE_PACKAGE = "panel_exp"
_SOURCE_RUNTIME = "METHOD_PROMOTION_GENERIC_RUNTIME_001"

_SUPPORTED_PROFILES = (
    TBRRIDGE_ADAPTER_PROFILE.profile_id,
    SCM_NULL_MONITOR_ADAPTER_PROFILE.profile_id,
    AUGSYNTH_ADAPTER_PROFILE.profile_id,
)

MIP_ALLOWED_USES: tuple[str, ...] = (
    "governance_context",
    "method_review_lineage",
    "profile_identity_display",
    "decision_scope_display",
    "missing_evidence_display",
    "blockers_display",
    "warnings_display",
    "prohibited_actions_display",
    "non_authorization_status_display",
    "routing_to_separate_catalog_review",
    "routing_to_separate_claim_review",
    "routing_to_separate_production_review",
    "preventing_unsupported_recommendations",
    "explaining_restricted_review_or_null_monitor_scope",
)

MIP_PROHIBITED_USES: tuple[str, ...] = (
    "decision_surface_approval",
    "trust_report_bypass",
    "recommendation_contract_authorization",
    "spend_movement_recommendation",
    "budget_optimization_authorization",
    "roi_roas_calculation_or_authorization",
    "production_readout_authorization",
    "production_compatibility_authorization",
    "catalog_unblock",
    "claim_authorization",
    "causal_lift_claim",
    "business_lift_claim",
    "statistical_significance_claim",
    "confidence_interval_claim",
    "p_value_claim",
    "statistical_power_claim",
    "method_promotion",
    "instrument_promotion",
    "overriding_source_packet_runtime",
    "overriding_source_decision_runtime",
    "raw_evidence_quality_scoring",
)


class MethodPromotionGenericAdapterMIPHandoffStatus(str, Enum):
    HANDOFF_READY_FOR_MIP_GOVERNANCE_CONTEXT = "HANDOFF_READY_FOR_MIP_GOVERNANCE_CONTEXT"
    HANDOFF_BLOCKED_MISSING_GOVERNANCE_SUMMARY = "HANDOFF_BLOCKED_MISSING_GOVERNANCE_SUMMARY"
    HANDOFF_BLOCKED_MISSING_PROFILE_ID = "HANDOFF_BLOCKED_MISSING_PROFILE_ID"
    HANDOFF_BLOCKED_MISSING_CANONICAL_IDENTITY = "HANDOFF_BLOCKED_MISSING_CANONICAL_IDENTITY"
    HANDOFF_BLOCKED_MISSING_DECISION_SCOPE = "HANDOFF_BLOCKED_MISSING_DECISION_SCOPE"
    HANDOFF_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS = "HANDOFF_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS"
    HANDOFF_BLOCKED_MISSING_BOUNDARY_STATUSES = "HANDOFF_BLOCKED_MISSING_BOUNDARY_STATUSES"
    HANDOFF_BLOCKED_AUTHORIZATION_FLAG_PRESENT = "HANDOFF_BLOCKED_AUTHORIZATION_FLAG_PRESENT"
    HANDOFF_BLOCKED_INVALID_PROHIBITED_USE_POLICY = "HANDOFF_BLOCKED_INVALID_PROHIBITED_USE_POLICY"


class MethodPromotionGenericAdapterMIPAuthorizationStatus(str, Enum):
    NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF = "NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF"


class MethodPromotionGenericAdapterMIPBypassStatus(str, Enum):
    NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF = "NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF"


class MethodPromotionGenericAdapterMIPPromotionStatus(str, Enum):
    NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF = "NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF"


_AUTH = MethodPromotionGenericAdapterMIPAuthorizationStatus.NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF
_BYPASS = MethodPromotionGenericAdapterMIPBypassStatus.NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF
_PROMO = MethodPromotionGenericAdapterMIPPromotionStatus.NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF

_HANDOFF_STATUS_PRIORITY = (
    MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_GOVERNANCE_SUMMARY,
    MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_CANONICAL_IDENTITY,
    MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_PROFILE_ID,
    MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_DECISION_SCOPE,
    MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS,
    MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_BOUNDARY_STATUSES,
    MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_AUTHORIZATION_FLAG_PRESENT,
    MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_INVALID_PROHIBITED_USE_POLICY,
)


@dataclass(frozen=True)
class MethodPromotionGenericAdapterMIPHandoffInput:
    handoff_id: str
    source_artifact_id: str = _ARTIFACT_ID
    source_runtime: str = _SOURCE_RUNTIME
    source_runtime_version: str | None = None
    governance_summary: MethodPromotionGovernanceSummary | dict[str, Any] | None = None
    source_packet_ref: str | None = None
    source_decision_ref: str | None = None
    source_governance_summary_ref: str | None = None
    created_from_artifacts: tuple[str, ...] | list[str] | None = None
    lineage: dict[str, Any] | None = None
    # Optional enrichment from adapter summaries (not recomputed; pass-through only).
    generic_packet_status: str | None = None
    generic_eligibility_status: str | None = None
    generic_decision_status: str | None = None
    decision_scope: str | None = None
    warnings: tuple[str, ...] | list[str] | None = None
    boundary_statuses: dict[str, Any] | None = None
    source_of_truth_refs: tuple[str, ...] | list[str] | None = None
    profile_id: str | None = None


@dataclass(frozen=True)
class MethodPromotionGenericAdapterMIPHandoff:
    handoff_id: str
    source_package: str
    source_artifact_id: str
    source_runtime: str
    source_runtime_version: str | None
    profile_id: str | None
    canonical_identity: str | None
    decision_scope: str | None
    generic_packet_status: str | None
    generic_eligibility_status: str | None
    generic_decision_status: str | None
    generic_governance_stage: str | None
    source_packet_ref: str | None
    source_decision_ref: str | None
    source_governance_summary_ref: str | None
    source_of_truth_refs: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    prohibited_actions: tuple[str, ...]
    boundary_statuses: dict[str, Any]
    mip_allowed_uses: tuple[str, ...]
    mip_prohibited_uses: tuple[str, ...]
    decision_surface_authorization_status: MethodPromotionGenericAdapterMIPAuthorizationStatus
    trust_report_bypass_status: MethodPromotionGenericAdapterMIPBypassStatus
    recommendation_authorization_status: MethodPromotionGenericAdapterMIPAuthorizationStatus
    catalog_authorization_status: MethodPromotionGenericAdapterMIPAuthorizationStatus
    production_readout_authorization_status: MethodPromotionGenericAdapterMIPAuthorizationStatus
    production_compatibility_authorization_status: MethodPromotionGenericAdapterMIPAuthorizationStatus
    claim_authorization_status: MethodPromotionGenericAdapterMIPAuthorizationStatus
    method_promotion_status: MethodPromotionGenericAdapterMIPPromotionStatus
    instrument_promotion_status: MethodPromotionGenericAdapterMIPPromotionStatus
    spend_roi_authorization_status: MethodPromotionGenericAdapterMIPAuthorizationStatus
    causal_lift_authorization_status: MethodPromotionGenericAdapterMIPAuthorizationStatus
    statistical_claim_authorization_status: MethodPromotionGenericAdapterMIPAuthorizationStatus
    lineage: dict[str, Any]
    created_from_artifacts: tuple[str, ...]
    handoff_status: MethodPromotionGenericAdapterMIPHandoffStatus
    handoff_blockers: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for key, val in list(payload.items()):
            if isinstance(val, Enum):
                payload[key] = val.value
            elif isinstance(val, tuple):
                payload[key] = list(val)
        return payload


def _tuple_str(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return tuple(str(v) for v in value)
    if isinstance(value, list):
        return tuple(str(v) for v in value)
    return (str(value),)


def _governance_view(
    summary: MethodPromotionGovernanceSummary | dict[str, Any] | None,
) -> dict[str, Any] | None:
    if summary is None:
        return None
    if hasattr(summary, "to_dict"):
        return summary.to_dict()
    return dict(summary)


def _boundary_from_governance(gov: dict[str, Any]) -> dict[str, Any]:
    boundary: dict[str, Any] = {}
    for field_name in (
        "claim_authorization_status",
        "catalog_status",
        "production_compatibility_status",
        "method_promotion_status",
        "instrument_promotion_status",
    ):
        if gov.get(field_name) is not None:
            boundary[field_name] = gov[field_name]
    if gov.get("mip_decisioning_status") is not None:
        boundary["mip_decisioning_status"] = gov["mip_decisioning_status"]
    if gov.get("trust_report_bypass_status") is not None:
        boundary["trust_report_bypass_status"] = gov["trust_report_bypass_status"]
    return boundary


def _authorization_flag_present(boundary: dict[str, Any]) -> bool:
    authorizing_tokens = (
        "AUTHORIZED",
        "UNBLOCKED",
        "PROMOTED",
        "BYPASSED",
        "APPROVED",
    )
    non_auth_prefixes = ("NOT_", "NO_")
    for value in boundary.values():
        text = str(value).upper()
        if any(text.startswith(prefix) for prefix in non_auth_prefixes):
            continue
        if any(token in text for token in authorizing_tokens):
            return True
    return False


def _pick_status(statuses: list[MethodPromotionGenericAdapterMIPHandoffStatus]) -> MethodPromotionGenericAdapterMIPHandoffStatus:
    if not statuses:
        return MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_READY_FOR_MIP_GOVERNANCE_CONTEXT
    for preferred in _HANDOFF_STATUS_PRIORITY:
        if preferred in statuses:
            return preferred
    return statuses[0]


def build_method_promotion_generic_adapter_mip_handoff(
    handoff_input: MethodPromotionGenericAdapterMIPHandoffInput,
) -> MethodPromotionGenericAdapterMIPHandoff:
    """Build a non-authorizing MIP handoff from a generic governance summary."""
    gov = _governance_view(handoff_input.governance_summary)
    handoff_blockers: list[str] = []
    blocked_statuses: list[MethodPromotionGenericAdapterMIPHandoffStatus] = []

    if gov is None:
        handoff_blockers.append("HANDOFF_BLOCKED_MISSING_GOVERNANCE_SUMMARY")
        blocked_statuses.append(
            MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_GOVERNANCE_SUMMARY
        )
        return MethodPromotionGenericAdapterMIPHandoff(
            handoff_id=handoff_input.handoff_id,
            source_package=_SOURCE_PACKAGE,
            source_artifact_id=handoff_input.source_artifact_id,
            source_runtime=handoff_input.source_runtime,
            source_runtime_version=handoff_input.source_runtime_version,
            profile_id=None,
            canonical_identity=None,
            decision_scope=None,
            generic_packet_status=None,
            generic_eligibility_status=None,
            generic_decision_status=None,
            generic_governance_stage=None,
            source_packet_ref=handoff_input.source_packet_ref,
            source_decision_ref=handoff_input.source_decision_ref,
            source_governance_summary_ref=handoff_input.source_governance_summary_ref,
            source_of_truth_refs=(),
            missing_evidence=(),
            blockers=tuple(handoff_blockers),
            warnings=(),
            prohibited_actions=(),
            boundary_statuses={},
            mip_allowed_uses=MIP_ALLOWED_USES,
            mip_prohibited_uses=MIP_PROHIBITED_USES,
            decision_surface_authorization_status=_AUTH,
            trust_report_bypass_status=_BYPASS,
            recommendation_authorization_status=_AUTH,
            catalog_authorization_status=_AUTH,
            production_readout_authorization_status=_AUTH,
            production_compatibility_authorization_status=_AUTH,
            claim_authorization_status=_AUTH,
            method_promotion_status=_PROMO,
            instrument_promotion_status=_PROMO,
            spend_roi_authorization_status=_AUTH,
            causal_lift_authorization_status=_AUTH,
            statistical_claim_authorization_status=_AUTH,
            lineage=dict(handoff_input.lineage or {}),
            created_from_artifacts=tuple(
                dict.fromkeys(
                    list(_tuple_str(handoff_input.created_from_artifacts)) + [_ARTIFACT_ID]
                )
            ),
            handoff_status=_pick_status(blocked_statuses),
            handoff_blockers=tuple(handoff_blockers),
        )

    canonical_identity = str(gov.get("instrument_identity") or "").strip() or None
    profile = None
    if canonical_identity:
        profile = _resolve_profile(canonical_identity, None)
    profile_id = handoff_input.profile_id or (profile.profile_id if profile else None)

    decision_scope = handoff_input.decision_scope
    if not decision_scope and profile is not None:
        decision_scope = profile.decision_scope

    stage = str(gov.get("current_framework_stage") or "") or None
    review_state = str(gov.get("current_review_state") or "") or None

    generic_decision_status = handoff_input.generic_decision_status
    generic_packet_status = handoff_input.generic_packet_status
    generic_eligibility_status = handoff_input.generic_eligibility_status
    if stage == "decision_ready" and generic_decision_status is None:
        generic_decision_status = review_state
    elif stage == "packet_only" and generic_packet_status is None:
        generic_packet_status = review_state

    source_of_truth_refs = _tuple_str(handoff_input.source_of_truth_refs)
    if not source_of_truth_refs and profile is not None:
        source_of_truth_refs = tuple(profile.source_of_truth_runtime_ids)

    boundary_statuses = dict(handoff_input.boundary_statuses or {})
    if not boundary_statuses:
        boundary_statuses = _boundary_from_governance(gov)

    missing_evidence = _tuple_str(gov.get("unresolved_missing_evidence"))
    blockers = _tuple_str(gov.get("unresolved_blockers"))
    warnings = _tuple_str(handoff_input.warnings)
    prohibited_actions = _tuple_str(gov.get("blocked_actions"))

    if not canonical_identity:
        handoff_blockers.append("HANDOFF_BLOCKED_MISSING_CANONICAL_IDENTITY")
        blocked_statuses.append(
            MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_CANONICAL_IDENTITY
        )
    if not profile_id:
        handoff_blockers.append("HANDOFF_BLOCKED_MISSING_PROFILE_ID")
        blocked_statuses.append(
            MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_PROFILE_ID
        )
    if not decision_scope:
        handoff_blockers.append("HANDOFF_BLOCKED_MISSING_DECISION_SCOPE")
        blocked_statuses.append(
            MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_DECISION_SCOPE
        )
    if not source_of_truth_refs:
        handoff_blockers.append("HANDOFF_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS")
        blocked_statuses.append(
            MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS
        )
    if not boundary_statuses:
        handoff_blockers.append("HANDOFF_BLOCKED_MISSING_BOUNDARY_STATUSES")
        blocked_statuses.append(
            MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_BOUNDARY_STATUSES
        )
    if _authorization_flag_present(boundary_statuses):
        handoff_blockers.append("HANDOFF_BLOCKED_AUTHORIZATION_FLAG_PRESENT")
        blocked_statuses.append(
            MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_AUTHORIZATION_FLAG_PRESENT
        )
    # Policy completeness: required prohibited uses must remain present.
    required_prohibited = {
        "decision_surface_approval",
        "trust_report_bypass",
        "recommendation_contract_authorization",
        "method_promotion",
        "instrument_promotion",
        "claim_authorization",
        "catalog_unblock",
        "production_readout_authorization",
    }
    if not required_prohibited.issubset(set(MIP_PROHIBITED_USES)):
        handoff_blockers.append("HANDOFF_BLOCKED_INVALID_PROHIBITED_USE_POLICY")
        blocked_statuses.append(
            MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_INVALID_PROHIBITED_USE_POLICY
        )

    lineage = dict(gov.get("lineage") or {})
    if handoff_input.lineage:
        lineage.update(handoff_input.lineage)

    created = list(_tuple_str(gov.get("created_from_artifacts")))
    created.extend(_tuple_str(handoff_input.created_from_artifacts))
    created.append(_ARTIFACT_ID)

    source_packet_ref = handoff_input.source_packet_ref or gov.get("packet_summary_ref")
    source_decision_ref = handoff_input.source_decision_ref or gov.get("decision_summary_ref")
    source_governance_summary_ref = (
        handoff_input.source_governance_summary_ref or gov.get("governance_summary_id")
    )

    handoff_status = _pick_status(blocked_statuses)

    return MethodPromotionGenericAdapterMIPHandoff(
        handoff_id=handoff_input.handoff_id,
        source_package=_SOURCE_PACKAGE,
        source_artifact_id=handoff_input.source_artifact_id,
        source_runtime=handoff_input.source_runtime,
        source_runtime_version=handoff_input.source_runtime_version,
        profile_id=profile_id,
        canonical_identity=canonical_identity,
        decision_scope=decision_scope,
        generic_packet_status=generic_packet_status,
        generic_eligibility_status=generic_eligibility_status,
        generic_decision_status=generic_decision_status,
        generic_governance_stage=stage,
        source_packet_ref=source_packet_ref,
        source_decision_ref=source_decision_ref,
        source_governance_summary_ref=source_governance_summary_ref,
        source_of_truth_refs=source_of_truth_refs,
        missing_evidence=missing_evidence,
        blockers=tuple(dict.fromkeys(list(blockers) + handoff_blockers)),
        warnings=warnings,
        prohibited_actions=prohibited_actions,
        boundary_statuses=boundary_statuses,
        mip_allowed_uses=MIP_ALLOWED_USES,
        mip_prohibited_uses=MIP_PROHIBITED_USES,
        decision_surface_authorization_status=_AUTH,
        trust_report_bypass_status=_BYPASS,
        recommendation_authorization_status=_AUTH,
        catalog_authorization_status=_AUTH,
        production_readout_authorization_status=_AUTH,
        production_compatibility_authorization_status=_AUTH,
        claim_authorization_status=_AUTH,
        method_promotion_status=_PROMO,
        instrument_promotion_status=_PROMO,
        spend_roi_authorization_status=_AUTH,
        causal_lift_authorization_status=_AUTH,
        statistical_claim_authorization_status=_AUTH,
        lineage=lineage,
        created_from_artifacts=tuple(dict.fromkeys(created)),
        handoff_status=handoff_status,
        handoff_blockers=tuple(handoff_blockers),
    )


def serialize_method_promotion_generic_adapter_mip_handoff(
    handoff: MethodPromotionGenericAdapterMIPHandoff,
) -> dict[str, Any]:
    """Serialize handoff to a JSON-safe dict (enums as strings)."""
    return handoff.to_dict()


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=_REPO)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    from panel_exp.validation.method_promotion_generic_runtime_001 import (
        TBRRIDGE_INSTRUMENT_IDENTITY,
        adapt_method_promotion_decision_to_generic_summary,
        adapt_method_promotion_packet_to_generic_summary,
        build_method_promotion_governance_summary,
    )
    from panel_exp.validation.tbrridge_promotion_evidence_packet_assembly_runtime_001 import (
        TBRRidgeEvidenceReference,
        TBRRidgePromotionEvidencePacketInput,
        assemble_tbrridge_promotion_evidence_packet,
    )
    from panel_exp.validation.tbrridge_promotion_review_decision_runtime_001 import (
        TBRRidgePromotionReviewDecisionInput,
        decide_tbrridge_promotion_review,
    )

    cats = (
        "instrument_identity",
        "claim_boundary",
        "metric_estimand_alignment",
        "null_control_false_positive",
        "directional_error",
        "positive_control_recovery",
        "sensitivity",
        "readout_compatibility",
    )
    packet = assemble_tbrridge_promotion_evidence_packet(
        TBRRidgePromotionEvidencePacketInput(
            packet_id="validation_tbrridge_packet",
            instrument_identity=TBRRIDGE_INSTRUMENT_IDENTITY,
            evidence_references=tuple(
                TBRRidgeEvidenceReference(
                    evidence_category=cat,
                    artifact_id=f"{cat}_001",
                    artifact_ref=f"docs/track_d/{cat.upper()}_001.md",
                )
                for cat in cats
            ),
        )
    )
    decision = decide_tbrridge_promotion_review(
        TBRRidgePromotionReviewDecisionInput(
            decision_id="validation_tbrridge_decision",
            packet=packet,
        )
    )
    packet_summary = adapt_method_promotion_packet_to_generic_summary(packet)
    decision_summary = adapt_method_promotion_decision_to_generic_summary(decision)
    governance = build_method_promotion_governance_summary(packet_summary, decision_summary)
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="validation_handoff",
            governance_summary=governance,
            generic_packet_status=packet_summary.generic_packet_readiness_status,
            generic_eligibility_status=packet_summary.generic_review_eligibility_status,
            generic_decision_status=decision_summary.generic_decision_status,
            decision_scope=decision_summary.decision_scope,
        )
    )
    serialized = serialize_method_promotion_generic_adapter_mip_handoff(handoff)
    assert (
        handoff.handoff_status
        == MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_READY_FOR_MIP_GOVERNANCE_CONTEXT
    )
    assert handoff.decision_surface_authorization_status == _AUTH
    assert handoff.trust_report_bypass_status == _BYPASS
    assert handoff.method_promotion_status == _PROMO
    assert handoff.generic_decision_status == "APPROVE_REVIEW_CONTINUATION"
    assert serialized["source_package"] == "panel_exp"
    assert isinstance(serialized["decision_surface_authorization_status"], str)

    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "method_promotion_generic_adapter_mip_handoff_runtime",
        "lane": "Lane A - Method instrument promotion framework application",
        "status": "completed",
        "scope": _SCOPE,
        "base_commit": _git_commit(),
        "depends_on": [
            "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_CONTRACT_001",
            "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_READINESS_AUDIT_001",
            "METHOD_PROMOTION_GENERIC_RUNTIME_001",
        ],
        "runtime_module_added": (
            "panel_exp.validation.method_promotion_generic_adapter_mip_handoff_runtime_001"
        ),
        "handoff_runtime_implemented": True,
        "handoff_builder_implemented": True,
        "handoff_serializer_implemented": True,
        "handoff_object_implemented": True,
        "fixed_mip_non_authorization_statuses_enforced": True,
        "mip_allowed_uses_enforced": True,
        "mip_prohibited_uses_enforced": True,
        "generic_approve_review_continuation_preserved_as_weak_context": True,
        "source_of_truth_boundary_preserved": True,
        "raw_evidence_not_inspected": True,
        "packet_readiness_not_recomputed": True,
        "decision_status_not_recomputed": True,
        "missing_evidence_not_repaired": True,
        "supported_profile_count": 3,
        "supported_profiles": list(_SUPPORTED_PROFILES),
        "decision_surface_authorization_blocked": True,
        "trust_report_bypass_blocked": True,
        "recommendation_authorization_blocked": True,
        "catalog_authorization_blocked": True,
        "production_readout_authorization_blocked": True,
        "production_compatibility_authorization_blocked": True,
        "claim_authorization_blocked": True,
        "spend_roi_authorization_blocked": True,
        "causal_lift_authorization_blocked": True,
        "statistical_claim_authorization_blocked": True,
        "generic_runtime_changed": False,
        "new_profile_registered": False,
        "mip_runtime_implemented": False,
        "decision_surface_authorized": False,
        "trust_report_bypassed": False,
        "recommendation_contract_authorized": False,
        "method_promoted": False,
        "instrument_promoted": False,
        "tbrridge_promoted": False,
        "scm_promoted": False,
        "augsynth_promoted": False,
        "did_promoted": False,
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
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "final_verdict": _VERDICT,
        "validation_handoff_status": handoff.handoff_status.value,
        "validation_generic_decision_status": handoff.generic_decision_status,
    }
    if write_summary:
        path = summary_path or _DEFAULT_SUMMARY
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Generic adapter MIP handoff runtime validation")
    parser.add_argument("--write-summary", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    summary = run_validation(write_summary=args.write_summary, summary_path=args.summary_path)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
