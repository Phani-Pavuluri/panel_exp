"""METHOD_PROMOTION_GENERIC_RUNTIME_001 — generic method promotion adapter runtime."""

from __future__ import annotations

import argparse
import json
import subprocess
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "METHOD_PROMOTION_GENERIC_RUNTIME_001"
_SCOPE = "generic_adapter_runtime_no_promotion_no_claim_authorization"
_VERDICT = (
    "generic_method_promotion_adapter_runtime_implemented_no_promotion_no_claim_authorization"
)
_RECOMMENDED_NEXT = "METHOD_PROMOTION_GENERIC_ADAPTER_PROFILE_APPLICATION_CHECKPOINT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/METHOD_PROMOTION_GENERIC_RUNTIME_001_summary.json"

TBRRIDGE_INSTRUMENT_IDENTITY = (
    "geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review"
)
SCM_INSTRUMENT_IDENTITY = "geo.scm.jackknife.single_cell.delta_mu.null_monitor"
SCM_CATALOG_ALIAS = "geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review"
AUGSYNTH_INSTRUMENT_IDENTITY = (
    "geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review"
)
AUGSYNTH_ALIAS_RELATED_IDENTITY = (
    "geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only"
)

_SUPPORTED_PROFILES = (
    TBRRIDGE_INSTRUMENT_IDENTITY,
    SCM_INSTRUMENT_IDENTITY,
    AUGSYNTH_INSTRUMENT_IDENTITY,
)

_REQUIRED_BOUNDARY_FIELDS = (
    "claim_authorization_status",
    "catalog_status",
    "production_compatibility_status",
    "method_promotion_status",
    "instrument_promotion_status",
)

_REQUIRED_PROHIBITED_ACTIONS = (
    "method_promotion",
    "instrument_promotion",
    "catalog_unblock",
    "production_compatibility_authorization",
    "causal_lift_claim_authorization",
    "business_lift_claim_authorization",
    "confidence_interval_claim_authorization",
    "p_value_claim_authorization",
    "statistical_significance_claim_authorization",
    "roi_roas_claim_authorization",
    "decision_recommendation_authorization",
    "production_readout_authorization",
    "mip_decision_surface_approval",
    "trust_report_bypass",
    "claim_authorization_runtime_bypass",
)

_TBRRIDGE_PACKET_STATUS_MAP = {
    "PACKET_READY_FOR_PROMOTION_REVIEW_INPUT": "PACKET_READY_FOR_REVIEW_INPUT",
    "PACKET_PARTIAL_DIAGNOSTIC_ONLY": "PACKET_PARTIAL_DIAGNOSTIC_ONLY",
    "PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE": "PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE",
    "PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING": "PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING",
    "PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH": "PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH",
    "PACKET_BLOCKED_UNSUPPORTED_SURFACE": "PACKET_BLOCKED_UNSUPPORTED_SURFACE",
    "PACKET_BLOCKED_CROSS_INFERENCE_FAMILY": "PACKET_BLOCKED_CROSS_INFERENCE_FAMILY",
    "PACKET_BLOCKED_CROSS_GEOMETRY": "PACKET_BLOCKED_CROSS_GEOMETRY",
    "PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED": "PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED",
    "PACKET_NOT_REQUESTED": "PACKET_NOT_REQUESTED",
}

_TBRRIDGE_ELIGIBILITY_MAP = {
    "ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT": "ELIGIBLE_AS_REVIEW_INPUT",
    "NOT_ELIGIBLE_MISSING_EVIDENCE": "NOT_ELIGIBLE_MISSING_EVIDENCE",
    "NOT_ELIGIBLE_IDENTITY_MISMATCH": "NOT_ELIGIBLE_IDENTITY_MISMATCH",
    "NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING": "NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING",
    "NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW": "NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW",
    "NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK": "NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK",
}

_TBRRIDGE_DECISION_MAP = {
    "APPROVE_RESTRICTED_REVIEW_CONTINUATION": "APPROVE_REVIEW_CONTINUATION",
    "REQUEST_ADDITIONAL_EVIDENCE": "REQUEST_ADDITIONAL_EVIDENCE",
    "REJECT_FOR_METHOD_VALIDITY": "REJECT_FOR_METHOD_VALIDITY",
    "REJECT_FOR_IDENTITY_MISMATCH": "REJECT_FOR_IDENTITY_MISMATCH",
    "REJECT_FOR_CLAIM_BOUNDARY_VIOLATION": "REJECT_FOR_CLAIM_BOUNDARY_VIOLATION",
    "REJECT_FOR_UNSUPPORTED_SURFACE": "REJECT_FOR_UNSUPPORTED_SURFACE",
    "REJECT_FOR_CROSS_INFERENCE_FAMILY": "REJECT_FOR_CROSS_INFERENCE_FAMILY",
    "REJECT_FOR_CROSS_GEOMETRY": "REJECT_FOR_CROSS_GEOMETRY",
    "DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW": "DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW",
    "DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW": "DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW",
    "NO_DECISION_PACKET_NOT_READY": "NO_DECISION_PACKET_NOT_READY",
}

_SCM_PACKET_STATUS_MAP = {
    "PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT": "PACKET_READY_FOR_REVIEW_INPUT",
    "PACKET_PARTIAL_DIAGNOSTIC_ONLY": "PACKET_PARTIAL_DIAGNOSTIC_ONLY",
    "PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE": "PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE",
    "PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING": "PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING",
    "PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH": "PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH",
    "PACKET_BLOCKED_UNSUPPORTED_SURFACE": "PACKET_BLOCKED_UNSUPPORTED_SURFACE",
    "PACKET_BLOCKED_CROSS_INFERENCE_FAMILY": "PACKET_BLOCKED_CROSS_INFERENCE_FAMILY",
    "PACKET_BLOCKED_CROSS_GEOMETRY": "PACKET_BLOCKED_CROSS_GEOMETRY",
    "PACKET_BLOCKED_CROSS_ESTIMAND": "PACKET_BLOCKED_CROSS_ESTIMAND",
    "PACKET_BLOCKED_NULL_MONITOR_SCOPE_VIOLATION": "PACKET_BLOCKED_SCOPE_VIOLATION",
    "PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED": "PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED",
    "PACKET_NOT_REQUESTED": "PACKET_NOT_REQUESTED",
}

_SCM_ELIGIBILITY_MAP = {
    "ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT": "ELIGIBLE_AS_REVIEW_INPUT",
    "NOT_ELIGIBLE_MISSING_EVIDENCE": "NOT_ELIGIBLE_MISSING_EVIDENCE",
    "NOT_ELIGIBLE_IDENTITY_MISMATCH": "NOT_ELIGIBLE_IDENTITY_MISMATCH",
    "NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING": "NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING",
    "NOT_ELIGIBLE_NULL_MONITOR_SCOPE_VIOLATION": "NOT_ELIGIBLE_SCOPE_VIOLATION",
    "NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW": "NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW",
    "NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK": "NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK",
    "NOT_ELIGIBLE_FOR_CAUSAL_CLAIM_REVIEW": "NOT_ELIGIBLE_FOR_CLAIM_REVIEW",
}

_SCM_DECISION_MAP = {
    "APPROVE_NULL_MONITOR_REVIEW_CONTINUATION": "APPROVE_REVIEW_CONTINUATION",
    "REQUEST_ADDITIONAL_EVIDENCE": "REQUEST_ADDITIONAL_EVIDENCE",
    "REJECT_FOR_METHOD_VALIDITY": "REJECT_FOR_METHOD_VALIDITY",
    "REJECT_FOR_IDENTITY_MISMATCH": "REJECT_FOR_IDENTITY_MISMATCH",
    "REJECT_FOR_CLAIM_BOUNDARY_VIOLATION": "REJECT_FOR_CLAIM_BOUNDARY_VIOLATION",
    "REJECT_FOR_NULL_MONITOR_SCOPE_VIOLATION": "REJECT_FOR_SCOPE_VIOLATION",
    "REJECT_FOR_UNSUPPORTED_SURFACE": "REJECT_FOR_UNSUPPORTED_SURFACE",
    "REJECT_FOR_CROSS_INFERENCE_FAMILY": "REJECT_FOR_CROSS_INFERENCE_FAMILY",
    "REJECT_FOR_CROSS_GEOMETRY": "REJECT_FOR_CROSS_GEOMETRY",
    "REJECT_FOR_CROSS_ESTIMAND": "REJECT_FOR_CROSS_ESTIMAND",
    "DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW": "DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW",
    "DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW": "DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW",
    "NO_DECISION_PACKET_NOT_READY": "NO_DECISION_PACKET_NOT_READY",
}

_AUGSYNTH_PACKET_STATUS_MAP = {
    "PACKET_READY_FOR_PROMOTION_REVIEW_INPUT": "PACKET_READY_FOR_REVIEW_INPUT",
    "PACKET_PARTIAL_DIAGNOSTIC_ONLY": "PACKET_PARTIAL_DIAGNOSTIC_ONLY",
    "PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE": "PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE",
    "PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING": "PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING",
    "PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH": "PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH",
    "PACKET_BLOCKED_UNSUPPORTED_SURFACE": "PACKET_BLOCKED_UNSUPPORTED_SURFACE",
    "PACKET_BLOCKED_CROSS_INFERENCE_FAMILY": "PACKET_BLOCKED_CROSS_INFERENCE_FAMILY",
    "PACKET_BLOCKED_CROSS_GEOMETRY": "PACKET_BLOCKED_CROSS_GEOMETRY",
    "PACKET_BLOCKED_CROSS_ESTIMAND": "PACKET_BLOCKED_CROSS_ESTIMAND",
    "PACKET_BLOCKED_SCOPE_VIOLATION": "PACKET_BLOCKED_SCOPE_VIOLATION",
    "PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED": "PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED",
    "PACKET_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT": "PACKET_BLOCKED_SCOPE_VIOLATION",
    "PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT": "PACKET_BLOCKED_SCOPE_VIOLATION",
    "PACKET_NOT_REQUESTED": "PACKET_NOT_REQUESTED",
}

_AUGSYNTH_ELIGIBILITY_MAP = {
    "ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT": "ELIGIBLE_AS_REVIEW_INPUT",
    "NOT_ELIGIBLE_MISSING_EVIDENCE": "NOT_ELIGIBLE_MISSING_EVIDENCE",
    "NOT_ELIGIBLE_IDENTITY_MISMATCH": "NOT_ELIGIBLE_IDENTITY_MISMATCH",
    "NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING": "NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING",
    "NOT_ELIGIBLE_SCOPE_VIOLATION": "NOT_ELIGIBLE_SCOPE_VIOLATION",
    "NOT_ELIGIBLE_ALIAS_SUBSTITUTION": "NOT_ELIGIBLE_SCOPE_VIOLATION",
    "NOT_ELIGIBLE_RESEARCH_ONLY_SUBSTITUTION": "NOT_ELIGIBLE_SCOPE_VIOLATION",
    "NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW": "NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW",
    "NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK": "NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK",
    "NOT_ELIGIBLE_FOR_CLAIM_REVIEW": "NOT_ELIGIBLE_FOR_CLAIM_REVIEW",
}

_AUGSYNTH_DECISION_MAP = {
    "APPROVE_RESTRICTED_REVIEW_CONTINUATION": "APPROVE_REVIEW_CONTINUATION",
    "REQUEST_ADDITIONAL_EVIDENCE": "REQUEST_ADDITIONAL_EVIDENCE",
    "REJECT_FOR_METHOD_VALIDITY": "REJECT_FOR_METHOD_VALIDITY",
    "REJECT_FOR_IDENTITY_MISMATCH": "REJECT_FOR_IDENTITY_MISMATCH",
    "REJECT_FOR_CLAIM_BOUNDARY_VIOLATION": "REJECT_FOR_CLAIM_BOUNDARY_VIOLATION",
    "REJECT_FOR_SCOPE_VIOLATION": "REJECT_FOR_SCOPE_VIOLATION",
    "REJECT_FOR_ALIAS_SUBSTITUTION": "REJECT_FOR_SCOPE_VIOLATION",
    "REJECT_FOR_RESEARCH_ONLY_SUBSTITUTION": "REJECT_FOR_SCOPE_VIOLATION",
    "REJECT_FOR_UNSUPPORTED_SURFACE": "REJECT_FOR_UNSUPPORTED_SURFACE",
    "REJECT_FOR_CROSS_INFERENCE_FAMILY": "REJECT_FOR_CROSS_INFERENCE_FAMILY",
    "REJECT_FOR_CROSS_GEOMETRY": "REJECT_FOR_CROSS_GEOMETRY",
    "REJECT_FOR_CROSS_ESTIMAND": "REJECT_FOR_CROSS_ESTIMAND",
    "DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW": "DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW",
    "DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW": "DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW",
    "NO_DECISION_PACKET_NOT_READY": "NO_DECISION_PACKET_NOT_READY",
}

class MethodPromotionGenericAdapterStatus(str, Enum):
    ADAPTED = "ADAPTED"
    BLOCKED_MISSING_SOURCE_PACKET = "BLOCKED_MISSING_SOURCE_PACKET"
    BLOCKED_MISSING_SOURCE_DECISION = "BLOCKED_MISSING_SOURCE_DECISION"
    BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY = "BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY"
    BLOCKED_UNMAPPED_PACKET_STATUS = "BLOCKED_UNMAPPED_PACKET_STATUS"
    BLOCKED_UNMAPPED_ELIGIBILITY_STATUS = "BLOCKED_UNMAPPED_ELIGIBILITY_STATUS"
    BLOCKED_UNMAPPED_DECISION_STATUS = "BLOCKED_UNMAPPED_DECISION_STATUS"
    BLOCKED_MISSING_BOUNDARY_STATUS = "BLOCKED_MISSING_BOUNDARY_STATUS"
    BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT = "BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT"
    BLOCKED_PROHIBITED_ACTION_WEAKENED = "BLOCKED_PROHIBITED_ACTION_WEAKENED"
    BLOCKED_SOURCE_OF_TRUTH_MISMATCH = "BLOCKED_SOURCE_OF_TRUTH_MISMATCH"


_ADAPTER_STATUS_PRIORITY = (
    MethodPromotionGenericAdapterStatus.BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY,
    MethodPromotionGenericAdapterStatus.BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT,
    MethodPromotionGenericAdapterStatus.BLOCKED_SOURCE_OF_TRUTH_MISMATCH,
    MethodPromotionGenericAdapterStatus.BLOCKED_UNMAPPED_PACKET_STATUS,
    MethodPromotionGenericAdapterStatus.BLOCKED_UNMAPPED_ELIGIBILITY_STATUS,
    MethodPromotionGenericAdapterStatus.BLOCKED_UNMAPPED_DECISION_STATUS,
    MethodPromotionGenericAdapterStatus.BLOCKED_MISSING_BOUNDARY_STATUS,
    MethodPromotionGenericAdapterStatus.BLOCKED_PROHIBITED_ACTION_WEAKENED,
    MethodPromotionGenericAdapterStatus.BLOCKED_MISSING_SOURCE_PACKET,
    MethodPromotionGenericAdapterStatus.BLOCKED_MISSING_SOURCE_DECISION,
)


@dataclass(frozen=True)
class MethodPromotionInstrumentAdapterProfile:
    profile_id: str
    instrument_identity: str
    aliases: tuple[str, ...]
    decision_scope: str
    packet_status_mapping: dict[str, str]
    eligibility_status_mapping: dict[str, str]
    decision_status_mapping: dict[str, str]
    required_boundary_fields: tuple[str, ...]
    source_of_truth_runtime_ids: tuple[str, ...]
    source_packet_artifact_id: str
    source_decision_artifact_id: str
    notes: str = ""


@dataclass(frozen=True)
class MethodPromotionEvidencePacketSummary:
    summary_id: str
    adapter_status: MethodPromotionGenericAdapterStatus
    adapter_blockers: tuple[str, ...]
    source_packet_ref: str
    source_artifact_id: str
    source_runtime_id: str
    instrument_identity: str
    aliases: tuple[str, ...]
    generic_packet_readiness_status: str | None
    instrument_specific_packet_readiness_status: str | None
    generic_review_eligibility_status: str | None
    instrument_specific_review_eligibility_status: str | None
    required_evidence_categories: tuple[str, ...]
    optional_evidence_categories: tuple[str, ...]
    evidence_category_count: int
    missing_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    allowed_surfaces: tuple[str, ...]
    prohibited_surfaces: tuple[str, ...]
    boundary_statuses: dict[str, Any]
    lineage: dict[str, Any]
    created_from_artifacts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["adapter_status"] = self.adapter_status.value
        return payload


@dataclass(frozen=True)
class MethodPromotionReviewDecisionSummary:
    summary_id: str
    adapter_status: MethodPromotionGenericAdapterStatus
    adapter_blockers: tuple[str, ...]
    source_decision_ref: str
    source_artifact_id: str
    source_runtime_id: str
    instrument_identity: str
    aliases: tuple[str, ...]
    generic_decision_status: str | None
    instrument_specific_decision_status: str | None
    decision_scope: str
    decision_surface: str
    evidence_summary: dict[str, Any]
    missing_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    required_followups: tuple[str, ...]
    allowed_next_actions: tuple[str, ...]
    prohibited_next_actions: tuple[str, ...]
    boundary_statuses: dict[str, Any]
    warnings: tuple[str, ...]
    lineage: dict[str, Any]
    created_from_artifacts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["adapter_status"] = self.adapter_status.value
        return payload


@dataclass(frozen=True)
class MethodPromotionGovernanceSummary:
    governance_summary_id: str
    adapter_status: MethodPromotionGenericAdapterStatus
    adapter_blockers: tuple[str, ...]
    instrument_identity: str
    aliases: tuple[str, ...]
    packet_summary_ref: str | None
    decision_summary_ref: str | None
    current_framework_stage: str
    current_review_state: str
    next_allowed_actions: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    claim_authorization_status: str | None
    catalog_status: str | None
    production_compatibility_status: str | None
    method_promotion_status: str | None
    instrument_promotion_status: str | None
    mip_decisioning_status: str
    trust_report_bypass_status: str
    unresolved_blockers: tuple[str, ...]
    unresolved_missing_evidence: tuple[str, ...]
    lineage: dict[str, Any]
    created_from_artifacts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["adapter_status"] = self.adapter_status.value
        return payload


TBRRIDGE_ADAPTER_PROFILE = MethodPromotionInstrumentAdapterProfile(
    profile_id="tbrridge_restricted_review_v1",
    instrument_identity=TBRRIDGE_INSTRUMENT_IDENTITY,
    aliases=(),
    decision_scope="restricted_review",
    packet_status_mapping=_TBRRIDGE_PACKET_STATUS_MAP,
    eligibility_status_mapping=_TBRRIDGE_ELIGIBILITY_MAP,
    decision_status_mapping=_TBRRIDGE_DECISION_MAP,
    required_boundary_fields=_REQUIRED_BOUNDARY_FIELDS,
    source_of_truth_runtime_ids=(
        "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001",
        "TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001",
    ),
    source_packet_artifact_id="TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001",
    source_decision_artifact_id="TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001",
    notes="TBRRidge restricted-review adapter profile",
)

SCM_NULL_MONITOR_ADAPTER_PROFILE = MethodPromotionInstrumentAdapterProfile(
    profile_id="scm_jackknife_null_monitor_v1",
    instrument_identity=SCM_INSTRUMENT_IDENTITY,
    aliases=(SCM_CATALOG_ALIAS,),
    decision_scope="null_monitor",
    packet_status_mapping=_SCM_PACKET_STATUS_MAP,
    eligibility_status_mapping=_SCM_ELIGIBILITY_MAP,
    decision_status_mapping=_SCM_DECISION_MAP,
    required_boundary_fields=_REQUIRED_BOUNDARY_FIELDS,
    source_of_truth_runtime_ids=(
        "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001",
        "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001",
    ),
    source_packet_artifact_id="SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001",
    source_decision_artifact_id="SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001",
    notes="SCM Jackknife null-monitor adapter profile",
)

AUGSYNTH_ADAPTER_PROFILE = MethodPromotionInstrumentAdapterProfile(
    profile_id="augsynth_jackknife_restricted_review_v1",
    instrument_identity=AUGSYNTH_INSTRUMENT_IDENTITY,
    aliases=(AUGSYNTH_ALIAS_RELATED_IDENTITY,),
    decision_scope="restricted_review",
    packet_status_mapping=_AUGSYNTH_PACKET_STATUS_MAP,
    eligibility_status_mapping=_AUGSYNTH_ELIGIBILITY_MAP,
    decision_status_mapping=_AUGSYNTH_DECISION_MAP,
    required_boundary_fields=_REQUIRED_BOUNDARY_FIELDS,
    source_of_truth_runtime_ids=(
        "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001",
        "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001",
    ),
    source_packet_artifact_id="AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001",
    source_decision_artifact_id="AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001",
    notes="AugSynth Jackknife restricted-review adapter profile",
)

_PROFILE_BY_IDENTITY: dict[str, MethodPromotionInstrumentAdapterProfile] = {
    TBRRIDGE_INSTRUMENT_IDENTITY: TBRRIDGE_ADAPTER_PROFILE,
    SCM_INSTRUMENT_IDENTITY: SCM_NULL_MONITOR_ADAPTER_PROFILE,
    AUGSYNTH_INSTRUMENT_IDENTITY: AUGSYNTH_ADAPTER_PROFILE,
}


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _tuple_str(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return tuple(str(v) for v in value)
    if isinstance(value, list):
        return tuple(str(v) for v in value)
    return (str(value),)


def _object_view(obj: Any) -> dict[str, Any]:
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dataclass_fields__"):
        payload = asdict(obj)
        for key, val in list(payload.items()):
            if isinstance(val, Enum):
                payload[key] = val.value
        return payload
    return dict(obj) if obj is not None else {}


def _status_text(value: Any) -> str:
    if isinstance(value, Enum):
        return value.value
    return str(value).strip()


def _resolve_profile(
    identity: str,
    profile: MethodPromotionInstrumentAdapterProfile | None,
) -> MethodPromotionInstrumentAdapterProfile | None:
    if profile is not None:
        return profile
    if identity in _PROFILE_BY_IDENTITY:
        return _PROFILE_BY_IDENTITY[identity]
    for candidate in _PROFILE_BY_IDENTITY.values():
        if identity in candidate.aliases:
            return candidate
    return None


def _aliases_from_source(source: dict[str, Any], profile: MethodPromotionInstrumentAdapterProfile) -> tuple[str, ...]:
    aliases: list[str] = []
    catalog_alias = source.get("catalog_alias")
    if catalog_alias:
        aliases.append(str(catalog_alias))
    alias_related = source.get("alias_related_identity")
    if alias_related:
        aliases.append(str(alias_related))
    for alias in profile.aliases:
        if alias not in aliases:
            aliases.append(alias)
    return tuple(aliases)


def _canonical_identity(
    source: dict[str, Any],
    profile: MethodPromotionInstrumentAdapterProfile,
) -> str:
    identity = str(source.get("instrument_identity", "")).strip()
    if identity == profile.instrument_identity:
        return profile.instrument_identity
    return identity


def _adapter_status_from_blockers(
    blockers: list[str],
) -> MethodPromotionGenericAdapterStatus:
    if not blockers:
        return MethodPromotionGenericAdapterStatus.ADAPTED
    status_by_blocker = {
        "GENERIC_ADAPTER_BLOCKED_MISSING_SOURCE_PACKET": (
            MethodPromotionGenericAdapterStatus.BLOCKED_MISSING_SOURCE_PACKET
        ),
        "GENERIC_ADAPTER_BLOCKED_MISSING_SOURCE_DECISION": (
            MethodPromotionGenericAdapterStatus.BLOCKED_MISSING_SOURCE_DECISION
        ),
        "GENERIC_ADAPTER_BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY": (
            MethodPromotionGenericAdapterStatus.BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY
        ),
        "GENERIC_ADAPTER_BLOCKED_UNMAPPED_PACKET_STATUS": (
            MethodPromotionGenericAdapterStatus.BLOCKED_UNMAPPED_PACKET_STATUS
        ),
        "GENERIC_ADAPTER_BLOCKED_UNMAPPED_ELIGIBILITY_STATUS": (
            MethodPromotionGenericAdapterStatus.BLOCKED_UNMAPPED_ELIGIBILITY_STATUS
        ),
        "GENERIC_ADAPTER_BLOCKED_UNMAPPED_DECISION_STATUS": (
            MethodPromotionGenericAdapterStatus.BLOCKED_UNMAPPED_DECISION_STATUS
        ),
        "GENERIC_ADAPTER_BLOCKED_MISSING_BOUNDARY_STATUS": (
            MethodPromotionGenericAdapterStatus.BLOCKED_MISSING_BOUNDARY_STATUS
        ),
        "GENERIC_ADAPTER_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT": (
            MethodPromotionGenericAdapterStatus.BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT
        ),
        "GENERIC_ADAPTER_BLOCKED_PROHIBITED_ACTION_WEAKENED": (
            MethodPromotionGenericAdapterStatus.BLOCKED_PROHIBITED_ACTION_WEAKENED
        ),
        "GENERIC_ADAPTER_BLOCKED_SOURCE_OF_TRUTH_MISMATCH": (
            MethodPromotionGenericAdapterStatus.BLOCKED_SOURCE_OF_TRUTH_MISMATCH
        ),
    }
    statuses = [status_by_blocker[b] for b in blockers if b in status_by_blocker]
    if not statuses:
        return MethodPromotionGenericAdapterStatus.ADAPTED
    for preferred in _ADAPTER_STATUS_PRIORITY:
        if preferred in statuses:
            return preferred
    return statuses[0]


def _prohibited_actions_weakened(actions: tuple[str, ...]) -> bool:
    lower = {a.lower() for a in actions}
    return not all(req in lower for req in _REQUIRED_PROHIBITED_ACTIONS)


def _extract_boundary_statuses(source: dict[str, Any]) -> dict[str, Any]:
    boundary: dict[str, Any] = {}
    for field_name in _REQUIRED_BOUNDARY_FIELDS:
        if field_name in source and source[field_name] is not None:
            boundary[field_name] = source[field_name]
    if source.get("null_monitor_scope_status") is not None:
        boundary["scope_status"] = source["null_monitor_scope_status"]
    elif source.get("scope_status") is not None:
        boundary["scope_status"] = source["scope_status"]
    return boundary


def _missing_boundary_fields(boundary: dict[str, Any], required: tuple[str, ...]) -> list[str]:
    return [field_name for field_name in required if not boundary.get(field_name)]


def adapt_method_promotion_packet_to_generic_summary(
    packet: Any,
    *,
    profile: MethodPromotionInstrumentAdapterProfile | None = None,
    summary_id: str | None = None,
    source_packet_ref: str | None = None,
) -> MethodPromotionEvidencePacketSummary:
    """Adapt an instrument-specific packet to a generic packet summary."""
    if packet is None:
        blockers = ("GENERIC_ADAPTER_BLOCKED_MISSING_SOURCE_PACKET",)
        return MethodPromotionEvidencePacketSummary(
            summary_id=summary_id or _new_id("packet_summary"),
            adapter_status=MethodPromotionGenericAdapterStatus.BLOCKED_MISSING_SOURCE_PACKET,
            adapter_blockers=tuple(blockers),
            source_packet_ref=source_packet_ref or "",
            source_artifact_id="",
            source_runtime_id="",
            instrument_identity="",
            aliases=(),
            generic_packet_readiness_status=None,
            instrument_specific_packet_readiness_status=None,
            generic_review_eligibility_status=None,
            instrument_specific_review_eligibility_status=None,
            required_evidence_categories=(),
            optional_evidence_categories=(),
            evidence_category_count=0,
            missing_evidence=(),
            blockers=(),
            warnings=(),
            allowed_surfaces=(),
            prohibited_surfaces=(),
            boundary_statuses={},
            lineage={},
            created_from_artifacts=(_ARTIFACT_ID,),
        )

    source = _object_view(packet)
    identity = str(source.get("instrument_identity", "")).strip()
    resolved = _resolve_profile(identity, profile)
    adapter_blockers: list[str] = []

    if not resolved:
        adapter_blockers.append("GENERIC_ADAPTER_BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY")
        canonical = identity
        aliases: tuple[str, ...] = ()
        runtime_id = ""
        artifact_id = ""
    else:
        canonical = _canonical_identity(source, resolved)
        aliases = _aliases_from_source(source, resolved)
        runtime_id = resolved.source_of_truth_runtime_ids[0]
        artifact_id = resolved.source_packet_artifact_id
        if identity in resolved.aliases and identity != resolved.instrument_identity:
            adapter_blockers.append("GENERIC_ADAPTER_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT")
        elif identity != resolved.instrument_identity:
            adapter_blockers.append("GENERIC_ADAPTER_BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY")

    inst_readiness = _status_text(source.get("packet_readiness_status", ""))
    inst_eligibility = _status_text(source.get("promotion_review_eligibility_status", ""))

    generic_readiness: str | None = None
    generic_eligibility: str | None = None

    if resolved and inst_readiness:
        generic_readiness = resolved.packet_status_mapping.get(inst_readiness)
        if generic_readiness is None:
            adapter_blockers.append("GENERIC_ADAPTER_BLOCKED_UNMAPPED_PACKET_STATUS")
    if resolved and inst_eligibility:
        generic_eligibility = resolved.eligibility_status_mapping.get(inst_eligibility)
        if generic_eligibility is None:
            adapter_blockers.append("GENERIC_ADAPTER_BLOCKED_UNMAPPED_ELIGIBILITY_STATUS")

    evidence_by_category = source.get("evidence_by_category") or {}
    evidence_category_count = len(evidence_by_category)
    required_categories = _tuple_str(source.get("required_evidence_categories"))
    if not required_categories and evidence_by_category:
        required_categories = tuple(sorted(str(k) for k in evidence_by_category.keys()))

    optional_categories = _tuple_str(source.get("optional_evidence_categories"))
    missing = _tuple_str(source.get("missing_evidence"))
    blockers = _tuple_str(source.get("blockers"))
    warnings = _tuple_str(source.get("warnings"))
    allowed_surfaces = _tuple_str(source.get("allowed_surfaces"))
    prohibited_surfaces = _tuple_str(source.get("prohibited_surfaces"))
    lineage = dict(source.get("lineage") or {})
    created = tuple(
        dict.fromkeys(list(_tuple_str(source.get("created_from_artifacts"))) + [_ARTIFACT_ID])
    )

    adapter_status = _adapter_status_from_blockers(adapter_blockers)

    return MethodPromotionEvidencePacketSummary(
        summary_id=summary_id or _new_id("packet_summary"),
        adapter_status=adapter_status,
        adapter_blockers=tuple(adapter_blockers),
        source_packet_ref=source_packet_ref or str(source.get("packet_id", "")),
        source_artifact_id=artifact_id,
        source_runtime_id=runtime_id,
        instrument_identity=canonical if resolved else identity,
        aliases=aliases,
        generic_packet_readiness_status=generic_readiness,
        instrument_specific_packet_readiness_status=inst_readiness or None,
        generic_review_eligibility_status=generic_eligibility,
        instrument_specific_review_eligibility_status=inst_eligibility or None,
        required_evidence_categories=required_categories,
        optional_evidence_categories=optional_categories,
        evidence_category_count=evidence_category_count,
        missing_evidence=missing,
        blockers=blockers,
        warnings=warnings,
        allowed_surfaces=allowed_surfaces,
        prohibited_surfaces=prohibited_surfaces,
        boundary_statuses={},
        lineage=lineage,
        created_from_artifacts=created,
    )


def adapt_method_promotion_decision_to_generic_summary(
    decision: Any,
    *,
    profile: MethodPromotionInstrumentAdapterProfile | None = None,
    summary_id: str | None = None,
    source_decision_ref: str | None = None,
) -> MethodPromotionReviewDecisionSummary:
    """Adapt an instrument-specific decision to a generic decision summary."""
    if decision is None:
        blockers = ("GENERIC_ADAPTER_BLOCKED_MISSING_SOURCE_DECISION",)
        return MethodPromotionReviewDecisionSummary(
            summary_id=summary_id or _new_id("decision_summary"),
            adapter_status=MethodPromotionGenericAdapterStatus.BLOCKED_MISSING_SOURCE_DECISION,
            adapter_blockers=tuple(blockers),
            source_decision_ref=source_decision_ref or "",
            source_artifact_id="",
            source_runtime_id="",
            instrument_identity="",
            aliases=(),
            generic_decision_status=None,
            instrument_specific_decision_status=None,
            decision_scope="",
            decision_surface="",
            evidence_summary={},
            missing_evidence=(),
            blockers=(),
            required_followups=(),
            allowed_next_actions=(),
            prohibited_next_actions=(),
            boundary_statuses={},
            warnings=(),
            lineage={},
            created_from_artifacts=(_ARTIFACT_ID,),
        )

    source = _object_view(decision)
    identity = str(source.get("instrument_identity", "")).strip()
    resolved = _resolve_profile(identity, profile)
    adapter_blockers: list[str] = []

    if not resolved:
        adapter_blockers.append("GENERIC_ADAPTER_BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY")
        canonical = identity
        aliases: tuple[str, ...] = ()
        runtime_id = ""
        artifact_id = ""
        decision_scope = str(source.get("decision_scope", ""))
    else:
        canonical = _canonical_identity(source, resolved)
        aliases = _aliases_from_source(source, resolved)
        runtime_id = resolved.source_of_truth_runtime_ids[-1]
        artifact_id = resolved.source_decision_artifact_id
        decision_scope = str(source.get("decision_scope") or resolved.decision_scope)
        if identity in resolved.aliases and identity != resolved.instrument_identity:
            adapter_blockers.append("GENERIC_ADAPTER_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT")
        elif identity != resolved.instrument_identity:
            adapter_blockers.append("GENERIC_ADAPTER_BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY")

    inst_decision = _status_text(source.get("decision_status", ""))
    generic_decision: str | None = None
    if resolved and inst_decision:
        generic_decision = resolved.decision_status_mapping.get(inst_decision)
        if generic_decision is None:
            adapter_blockers.append("GENERIC_ADAPTER_BLOCKED_UNMAPPED_DECISION_STATUS")

    boundary_statuses = _extract_boundary_statuses(source)
    if resolved:
        missing_boundary = _missing_boundary_fields(boundary_statuses, resolved.required_boundary_fields)
        if missing_boundary:
            adapter_blockers.append("GENERIC_ADAPTER_BLOCKED_MISSING_BOUNDARY_STATUS")

    prohibited = _tuple_str(source.get("prohibited_next_actions"))
    if _prohibited_actions_weakened(prohibited):
        adapter_blockers.append("GENERIC_ADAPTER_BLOCKED_PROHIBITED_ACTION_WEAKENED")

    adapter_status = _adapter_status_from_blockers(adapter_blockers)

    return MethodPromotionReviewDecisionSummary(
        summary_id=summary_id or _new_id("decision_summary"),
        adapter_status=adapter_status,
        adapter_blockers=tuple(adapter_blockers),
        source_decision_ref=source_decision_ref or str(source.get("decision_id", "")),
        source_artifact_id=artifact_id,
        source_runtime_id=runtime_id,
        instrument_identity=canonical if resolved else identity,
        aliases=aliases,
        generic_decision_status=generic_decision,
        instrument_specific_decision_status=inst_decision or None,
        decision_scope=decision_scope,
        decision_surface=str(source.get("decision_surface", "")),
        evidence_summary=dict(source.get("evidence_summary") or {}),
        missing_evidence=_tuple_str(source.get("missing_evidence")),
        blockers=_tuple_str(source.get("blockers")),
        required_followups=_tuple_str(source.get("required_followups")),
        allowed_next_actions=_tuple_str(source.get("allowed_next_actions")),
        prohibited_next_actions=prohibited,
        boundary_statuses=boundary_statuses,
        warnings=_tuple_str(source.get("warnings")),
        lineage=dict(source.get("lineage") or {}),
        created_from_artifacts=tuple(
            dict.fromkeys(list(_tuple_str(source.get("created_from_artifacts"))) + [_ARTIFACT_ID])
        ),
    )


def build_method_promotion_governance_summary(
    packet_summary: MethodPromotionEvidencePacketSummary | None = None,
    decision_summary: MethodPromotionReviewDecisionSummary | None = None,
    *,
    governance_summary_id: str | None = None,
) -> MethodPromotionGovernanceSummary:
    """Build a governance rollup from generic packet and/or decision summaries."""
    adapter_blockers: list[str] = []
    if packet_summary:
        adapter_blockers.extend(packet_summary.adapter_blockers)
    if decision_summary:
        adapter_blockers.extend(decision_summary.adapter_blockers)
    adapter_blockers = list(dict.fromkeys(adapter_blockers))

    identity = ""
    aliases: tuple[str, ...] = ()
    if decision_summary and decision_summary.instrument_identity:
        identity = decision_summary.instrument_identity
        aliases = decision_summary.aliases
    elif packet_summary and packet_summary.instrument_identity:
        identity = packet_summary.instrument_identity
        aliases = packet_summary.aliases

    blocked = (
        packet_summary is not None
        and packet_summary.adapter_status != MethodPromotionGenericAdapterStatus.ADAPTED
    ) or (
        decision_summary is not None
        and decision_summary.adapter_status != MethodPromotionGenericAdapterStatus.ADAPTED
    )

    if blocked:
        framework_stage = "blocked_adapter"
        review_state = "blocked_adapter"
    elif decision_summary:
        framework_stage = "decision_ready"
        review_state = decision_summary.generic_decision_status or "unknown"
    elif packet_summary:
        framework_stage = "packet_only"
        review_state = packet_summary.generic_packet_readiness_status or "unknown"
    else:
        framework_stage = "blocked_adapter"
        review_state = "blocked_adapter"
        adapter_blockers.append("GENERIC_ADAPTER_BLOCKED_MISSING_SOURCE_PACKET")

    next_allowed = decision_summary.allowed_next_actions if decision_summary else ()
    blocked_actions = (
        decision_summary.prohibited_next_actions
        if decision_summary
        else (packet_summary.prohibited_surfaces if packet_summary else ())
    )

    boundary = decision_summary.boundary_statuses if decision_summary else {}
    unresolved_blockers: list[str] = []
    unresolved_missing: list[str] = []
    if packet_summary:
        unresolved_blockers.extend(packet_summary.blockers)
        unresolved_missing.extend(packet_summary.missing_evidence)
    if decision_summary:
        unresolved_blockers.extend(decision_summary.blockers)
        unresolved_missing.extend(decision_summary.missing_evidence)
    unresolved_blockers = list(dict.fromkeys(unresolved_blockers + adapter_blockers))
    unresolved_missing = list(dict.fromkeys(unresolved_missing))

    lineage: dict[str, Any] = {}
    created: list[str] = [_ARTIFACT_ID]
    if packet_summary:
        lineage.update(packet_summary.lineage)
        created.extend(packet_summary.created_from_artifacts)
    if decision_summary:
        lineage.update(decision_summary.lineage)
        created.extend(decision_summary.created_from_artifacts)

    adapter_status = _adapter_status_from_blockers(adapter_blockers)

    return MethodPromotionGovernanceSummary(
        governance_summary_id=governance_summary_id or _new_id("governance_summary"),
        adapter_status=adapter_status,
        adapter_blockers=tuple(adapter_blockers),
        instrument_identity=identity,
        aliases=aliases,
        packet_summary_ref=packet_summary.summary_id if packet_summary else None,
        decision_summary_ref=decision_summary.summary_id if decision_summary else None,
        current_framework_stage=framework_stage,
        current_review_state=review_state,
        next_allowed_actions=next_allowed,
        blocked_actions=blocked_actions,
        claim_authorization_status=boundary.get("claim_authorization_status"),
        catalog_status=boundary.get("catalog_status"),
        production_compatibility_status=boundary.get("production_compatibility_status"),
        method_promotion_status=boundary.get("method_promotion_status"),
        instrument_promotion_status=boundary.get("instrument_promotion_status"),
        mip_decisioning_status="NOT_AUTHORIZED_BY_THIS_ADAPTER",
        trust_report_bypass_status="NOT_BYPASSED_BY_THIS_ADAPTER",
        unresolved_blockers=tuple(unresolved_blockers),
        unresolved_missing_evidence=tuple(unresolved_missing),
        lineage=lineage,
        created_from_artifacts=tuple(dict.fromkeys(created)),
    )


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=_REPO)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    from panel_exp.validation.scm_jackknife_null_monitor_promotion_evidence_packet_runtime_001 import (
        SCMJackknifeNullMonitorEvidenceReference,
        SCMJackknifeNullMonitorPromotionEvidencePacketInput,
        assemble_scm_jackknife_null_monitor_promotion_evidence_packet,
    )
    from panel_exp.validation.scm_jackknife_null_monitor_review_decision_runtime_001 import (
        SCMJackknifeNullMonitorReviewDecisionInput,
        decide_scm_jackknife_null_monitor_review,
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

    tbrridge_cats = (
        "instrument_identity",
        "claim_boundary",
        "metric_estimand_alignment",
        "null_control_false_positive",
        "directional_error",
        "positive_control_recovery",
        "sensitivity",
        "readout_compatibility",
    )
    tbrridge_packet = assemble_tbrridge_promotion_evidence_packet(
        TBRRidgePromotionEvidencePacketInput(
            packet_id="validation_tbrridge_packet",
            instrument_identity=TBRRIDGE_INSTRUMENT_IDENTITY,
            evidence_references=tuple(
                TBRRidgeEvidenceReference(
                    evidence_category=cat,
                    artifact_id=f"{cat}_001",
                    artifact_ref=f"docs/track_d/{cat.upper()}_001.md",
                )
                for cat in tbrridge_cats
            ),
        )
    )
    tbrridge_decision = decide_tbrridge_promotion_review(
        TBRRidgePromotionReviewDecisionInput(
            decision_id="validation_tbrridge_decision",
            packet=tbrridge_packet,
        )
    )
    tbrridge_packet_summary = adapt_method_promotion_packet_to_generic_summary(tbrridge_packet)
    tbrridge_decision_summary = adapt_method_promotion_decision_to_generic_summary(tbrridge_decision)
    tbrridge_governance = build_method_promotion_governance_summary(
        tbrridge_packet_summary, tbrridge_decision_summary
    )

    scm_cats = (
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
    scm_packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        SCMJackknifeNullMonitorPromotionEvidencePacketInput(
            packet_id="validation_scm_packet",
            catalog_alias=SCM_CATALOG_ALIAS,
            evidence_refs=[
                SCMJackknifeNullMonitorEvidenceReference(
                    evidence_id=f"{cat}_001",
                    evidence_category=cat,
                    artifact_ref=f"docs/track_d/{cat.upper()}_001.md",
                )
                for cat in scm_cats
            ],
        )
    )
    scm_decision = decide_scm_jackknife_null_monitor_review(
        SCMJackknifeNullMonitorReviewDecisionInput(
            decision_id="validation_scm_decision",
            packet=scm_packet,
        )
    )
    scm_packet_summary = adapt_method_promotion_packet_to_generic_summary(scm_packet)
    scm_decision_summary = adapt_method_promotion_decision_to_generic_summary(scm_decision)
    scm_governance = build_method_promotion_governance_summary(
        scm_packet_summary, scm_decision_summary
    )

    from panel_exp.validation.augsynth_jackknife_promotion_evidence_packet_runtime_001 import (
        AugSynthJackknifeEvidenceReference,
        AugSynthJackknifePromotionEvidencePacketInput,
        assemble_augsynth_jackknife_promotion_evidence_packet,
    )
    from panel_exp.validation.augsynth_jackknife_review_decision_runtime_001 import (
        AugSynthJackknifeReviewDecisionInput,
        decide_augsynth_jackknife_review,
    )

    augsynth_cats = (
        "instrument_identity",
        "claim_boundary",
        "metric_estimand_alignment",
        "null_control_false_positive",
        "directional_error",
        "positive_control_recovery",
        "sensitivity",
        "readout_compatibility",
        "donor_pool_diagnostics",
        "pre_period_fit_diagnostics",
        "augmentation_component_diagnostics",
        "synthetic_weight_diagnostics",
        "regularization_or_model_component_diagnostics",
        "jackknife_stability",
        "method_disagreement_or_scm_bridge",
        "support_overlap_or_donor_hull_stress",
    )
    augsynth_packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        AugSynthJackknifePromotionEvidencePacketInput(
            packet_id="validation_augsynth_packet",
            instrument_identity=AUGSYNTH_INSTRUMENT_IDENTITY,
            evidence_references=[
                AugSynthJackknifeEvidenceReference(
                    evidence_id=f"{cat}_001",
                    evidence_category=cat,
                    artifact_ref=f"docs/track_d/{cat.upper()}_001.md",
                )
                for cat in augsynth_cats
            ],
        )
    )
    augsynth_decision = decide_augsynth_jackknife_review(
        AugSynthJackknifeReviewDecisionInput(
            decision_id="validation_augsynth_decision",
            packet=augsynth_packet,
        )
    )
    augsynth_packet_summary = adapt_method_promotion_packet_to_generic_summary(augsynth_packet)
    augsynth_decision_summary = adapt_method_promotion_decision_to_generic_summary(augsynth_decision)
    augsynth_governance = build_method_promotion_governance_summary(
        augsynth_packet_summary, augsynth_decision_summary
    )

    assert tbrridge_packet_summary.adapter_status == MethodPromotionGenericAdapterStatus.ADAPTED
    assert tbrridge_packet_summary.generic_packet_readiness_status == "PACKET_READY_FOR_REVIEW_INPUT"
    assert tbrridge_decision_summary.generic_decision_status == "APPROVE_REVIEW_CONTINUATION"
    assert tbrridge_decision_summary.decision_scope == "restricted_review"
    assert scm_packet_summary.generic_packet_readiness_status == "PACKET_READY_FOR_REVIEW_INPUT"
    assert scm_decision_summary.generic_decision_status == "APPROVE_REVIEW_CONTINUATION"
    assert scm_decision_summary.decision_scope == "null_monitor"
    assert tbrridge_governance.claim_authorization_status == "NOT_AUTHORIZED_BY_THIS_DECISION"
    assert scm_governance.method_promotion_status == "NOT_PROMOTED_BY_THIS_DECISION"
    assert augsynth_packet_summary.generic_packet_readiness_status == "PACKET_READY_FOR_REVIEW_INPUT"
    assert augsynth_decision_summary.generic_decision_status == "APPROVE_REVIEW_CONTINUATION"
    assert augsynth_decision_summary.decision_scope == "restricted_review"
    assert augsynth_governance.claim_authorization_status == "NOT_AUTHORIZED_BY_THIS_DECISION"

    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "method_promotion_generic_runtime",
        "lane": "Lane A - Method instrument promotion framework generic runtime",
        "status": "completed",
        "scope": _SCOPE,
        "base_commit": _git_commit(),
        "depends_on": [
            "METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001",
            "METHOD_PROMOTION_GENERIC_CONTRACTS_001",
            "TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001",
            "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001",
            "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001",
            "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001",
            "CLAIM_AUTHORIZATION_RUNTIME_001",
        ],
        "supported_profiles": list(_SUPPORTED_PROFILES),
        "supported_profile_count": 3,
        "generic_runtime_implemented": True,
        "generic_runtime_changed": True,
        "adapter_runtime_only": True,
        "supported_profiles_limited_to_completed_applications": True,
        "tbrridge_profile_supported": True,
        "scm_null_monitor_profile_supported": True,
        "augsynth_profile_supported": True,
        "augsynth_profile_id": "augsynth_jackknife_restricted_review_v1",
        "generic_adapter_profile_for_augsynth_implemented": True,
        "augsynth_profile_registered": True,
        "packet_summary_adapter_implemented": True,
        "decision_summary_adapter_implemented": True,
        "governance_summary_builder_implemented": True,
        "instrument_specific_runtimes_source_of_truth": True,
        "status_mapping_implemented": True,
        "boundary_preservation_implemented": True,
        "prohibited_action_non_weakening_implemented": True,
        "alias_substitution_blocked": True,
        "unmapped_status_blocked": True,
        "missing_boundary_status_blocked": True,
        "missing_evidence_preserved": True,
        "blockers_preserved": True,
        "warnings_lineage_preserved": True,
        "mip_facing_summary_boundary_preserved": True,
        "runtime_implemented": True,
        "generic_dataclasses_implemented": True,
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
        "mip_decisioning_authorized": False,
        "trust_report_bypassed": False,
        "augsynth_did_support_implemented": False,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "final_verdict": _VERDICT,
        "validation_tbrridge_generic_decision": tbrridge_decision_summary.generic_decision_status,
        "validation_scm_generic_decision": scm_decision_summary.generic_decision_status,
        "validation_augsynth_generic_decision": augsynth_decision_summary.generic_decision_status,
    }
    if write_summary:
        path = summary_path or _DEFAULT_SUMMARY
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Method promotion generic adapter runtime validation")
    parser.add_argument("--write-summary", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    summary = run_validation(write_summary=args.write_summary, summary_path=args.summary_path)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
