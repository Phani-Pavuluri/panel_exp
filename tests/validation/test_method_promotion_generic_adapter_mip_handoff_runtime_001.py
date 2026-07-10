"""Validation tests for METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001."""

from __future__ import annotations

import json

from panel_exp.validation.method_promotion_generic_adapter_mip_handoff_runtime_001 import (
    MIP_ALLOWED_USES,
    MIP_PROHIBITED_USES,
    MethodPromotionGenericAdapterMIPAuthorizationStatus,
    MethodPromotionGenericAdapterMIPBypassStatus,
    MethodPromotionGenericAdapterMIPHandoff,
    MethodPromotionGenericAdapterMIPHandoffInput,
    MethodPromotionGenericAdapterMIPHandoffStatus,
    MethodPromotionGenericAdapterMIPPromotionStatus,
    build_method_promotion_generic_adapter_mip_handoff,
    serialize_method_promotion_generic_adapter_mip_handoff,
)
from panel_exp.validation.method_promotion_generic_runtime_001 import (
    SCM_CATALOG_ALIAS,
    SCM_INSTRUMENT_IDENTITY,
    TBRRIDGE_INSTRUMENT_IDENTITY,
    adapt_method_promotion_decision_to_generic_summary,
    adapt_method_promotion_packet_to_generic_summary,
    build_method_promotion_governance_summary,
)
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

_TBRRIDGE_CATS = (
    "instrument_identity",
    "claim_boundary",
    "metric_estimand_alignment",
    "null_control_false_positive",
    "directional_error",
    "positive_control_recovery",
    "sensitivity",
    "readout_compatibility",
)

_SCM_CATS = (
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

_AUTH = MethodPromotionGenericAdapterMIPAuthorizationStatus.NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF
_BYPASS = MethodPromotionGenericAdapterMIPBypassStatus.NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF
_PROMO = MethodPromotionGenericAdapterMIPPromotionStatus.NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF

_FORBIDDEN_TRUE_KEYS = (
    "decision_surface_authorized",
    "trust_report_bypassed",
    "recommendation_contract_authorized",
    "method_promoted",
    "instrument_promoted",
    "catalog_unblocked",
    "production_compatibility_authorized",
    "claim_authorization_changed",
    "statistical_claim_authorized",
    "production_readout_authorized",
)


def _tbrridge_governance():
    packet = assemble_tbrridge_promotion_evidence_packet(
        TBRRidgePromotionEvidencePacketInput(
            packet_id="tbrridge_packet",
            instrument_identity=TBRRIDGE_INSTRUMENT_IDENTITY,
            evidence_references=tuple(
                TBRRidgeEvidenceReference(
                    evidence_category=cat,
                    artifact_id=f"{cat}_001",
                    artifact_ref=f"docs/track_d/{cat.upper()}_001.md",
                )
                for cat in _TBRRIDGE_CATS
            ),
        )
    )
    decision = decide_tbrridge_promotion_review(
        TBRRidgePromotionReviewDecisionInput(decision_id="tbrridge_decision", packet=packet)
    )
    packet_summary = adapt_method_promotion_packet_to_generic_summary(packet)
    decision_summary = adapt_method_promotion_decision_to_generic_summary(decision)
    governance = build_method_promotion_governance_summary(packet_summary, decision_summary)
    return governance, packet_summary, decision_summary


def _scm_governance():
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        SCMJackknifeNullMonitorPromotionEvidencePacketInput(
            packet_id="scm_packet",
            catalog_alias=SCM_CATALOG_ALIAS,
            evidence_refs=[
                SCMJackknifeNullMonitorEvidenceReference(
                    evidence_id=f"{cat}_001",
                    evidence_category=cat,
                    artifact_ref=f"docs/track_d/{cat.upper()}_001.md",
                )
                for cat in _SCM_CATS
            ],
        )
    )
    decision = decide_scm_jackknife_null_monitor_review(
        SCMJackknifeNullMonitorReviewDecisionInput(decision_id="scm_decision", packet=packet)
    )
    packet_summary = adapt_method_promotion_packet_to_generic_summary(packet)
    decision_summary = adapt_method_promotion_decision_to_generic_summary(decision)
    governance = build_method_promotion_governance_summary(packet_summary, decision_summary)
    return governance, packet_summary, decision_summary


def test_public_api_import() -> None:
    assert MethodPromotionGenericAdapterMIPHandoff is not None
    assert callable(build_method_promotion_generic_adapter_mip_handoff)
    assert callable(serialize_method_promotion_generic_adapter_mip_handoff)


def test_build_ready_handoff_from_valid_governance_summary() -> None:
    governance, packet_summary, decision_summary = _tbrridge_governance()
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="ready_handoff",
            governance_summary=governance,
            generic_packet_status=packet_summary.generic_packet_readiness_status,
            generic_eligibility_status=packet_summary.generic_review_eligibility_status,
            generic_decision_status=decision_summary.generic_decision_status,
        )
    )
    assert (
        handoff.handoff_status
        == MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_READY_FOR_MIP_GOVERNANCE_CONTEXT
    )
    assert handoff.source_package == "panel_exp"
    assert handoff.profile_id == "tbrridge_restricted_review_v1"
    assert handoff.canonical_identity == TBRRIDGE_INSTRUMENT_IDENTITY
    assert handoff.decision_scope == "restricted_review"
    assert handoff.source_of_truth_refs


def test_fixed_non_authorization_statuses_always_present() -> None:
    governance, _, decision_summary = _tbrridge_governance()
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="fixed_status_handoff",
            governance_summary=governance,
            generic_decision_status=decision_summary.generic_decision_status,
        )
    )
    assert handoff.decision_surface_authorization_status == _AUTH
    assert handoff.trust_report_bypass_status == _BYPASS
    assert handoff.recommendation_authorization_status == _AUTH
    assert handoff.catalog_authorization_status == _AUTH
    assert handoff.production_readout_authorization_status == _AUTH
    assert handoff.production_compatibility_authorization_status == _AUTH
    assert handoff.claim_authorization_status == _AUTH
    assert handoff.method_promotion_status == _PROMO
    assert handoff.instrument_promotion_status == _PROMO
    assert handoff.spend_roi_authorization_status == _AUTH
    assert handoff.causal_lift_authorization_status == _AUTH
    assert handoff.statistical_claim_authorization_status == _AUTH


def test_allowed_uses_exact() -> None:
    governance, _, _ = _tbrridge_governance()
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="allowed_uses",
            governance_summary=governance,
        )
    )
    assert handoff.mip_allowed_uses == MIP_ALLOWED_USES
    assert "governance_context" in handoff.mip_allowed_uses
    assert "explaining_restricted_review_or_null_monitor_scope" in handoff.mip_allowed_uses


def test_prohibited_uses_exact() -> None:
    governance, _, _ = _tbrridge_governance()
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="prohibited_uses",
            governance_summary=governance,
        )
    )
    assert handoff.mip_prohibited_uses == MIP_PROHIBITED_USES
    for required in (
        "decision_surface_approval",
        "trust_report_bypass",
        "recommendation_contract_authorization",
        "claim_authorization",
        "catalog_unblock",
        "method_promotion",
        "instrument_promotion",
        "production_readout_authorization",
    ):
        assert required in handoff.mip_prohibited_uses


def test_approve_review_continuation_remains_weak_context() -> None:
    governance, _, decision_summary = _tbrridge_governance()
    assert decision_summary.generic_decision_status == "APPROVE_REVIEW_CONTINUATION"
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="weak_approve",
            governance_summary=governance,
            generic_decision_status=decision_summary.generic_decision_status,
        )
    )
    assert handoff.generic_decision_status == "APPROVE_REVIEW_CONTINUATION"
    assert handoff.decision_surface_authorization_status == _AUTH
    assert handoff.recommendation_authorization_status == _AUTH
    assert handoff.method_promotion_status == _PROMO
    assert (
        handoff.handoff_status
        == MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_READY_FOR_MIP_GOVERNANCE_CONTEXT
    )


def test_restricted_review_profile_handoff() -> None:
    governance, packet_summary, decision_summary = _tbrridge_governance()
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="restricted_review",
            governance_summary=governance,
            generic_packet_status=packet_summary.generic_packet_readiness_status,
            generic_decision_status=decision_summary.generic_decision_status,
        )
    )
    assert handoff.decision_scope == "restricted_review"
    assert handoff.profile_id == "tbrridge_restricted_review_v1"


def test_null_monitor_profile_handoff() -> None:
    governance, packet_summary, decision_summary = _scm_governance()
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="null_monitor",
            governance_summary=governance,
            generic_packet_status=packet_summary.generic_packet_readiness_status,
            generic_decision_status=decision_summary.generic_decision_status,
        )
    )
    assert handoff.decision_scope == "null_monitor"
    assert handoff.profile_id == "scm_jackknife_null_monitor_v1"
    assert handoff.canonical_identity == SCM_INSTRUMENT_IDENTITY
    assert (
        handoff.handoff_status
        == MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_READY_FOR_MIP_GOVERNANCE_CONTEXT
    )


def test_blocked_if_profile_id_missing() -> None:
    governance, _, _ = _tbrridge_governance()
    payload = governance.to_dict()
    payload["instrument_identity"] = "geo.unknown.instrument.identity"
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="missing_profile",
            governance_summary=payload,
        )
    )
    assert (
        handoff.handoff_status
        == MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_PROFILE_ID
    )


def test_blocked_if_canonical_identity_missing() -> None:
    governance, _, _ = _tbrridge_governance()
    payload = governance.to_dict()
    payload["instrument_identity"] = ""
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="missing_identity",
            governance_summary=payload,
        )
    )
    assert (
        handoff.handoff_status
        == MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_CANONICAL_IDENTITY
    )


def test_blocked_if_decision_scope_missing() -> None:
    governance, _, _ = _tbrridge_governance()
    payload = governance.to_dict()
    payload["instrument_identity"] = "geo.unknown.instrument.identity"
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="missing_scope",
            governance_summary=payload,
            profile_id="synthetic_profile_without_scope",
            decision_scope=None,
            source_of_truth_refs=("SOME_RUNTIME",),
            boundary_statuses={"claim_authorization_status": "NOT_AUTHORIZED_BY_THIS_DECISION"},
        )
    )
    assert (
        handoff.handoff_status
        == MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_DECISION_SCOPE
    )


def test_blocked_if_source_of_truth_refs_missing() -> None:
    governance, _, _ = _tbrridge_governance()
    payload = governance.to_dict()
    payload["instrument_identity"] = "geo.unknown.instrument.identity"
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="missing_sot",
            governance_summary=payload,
            profile_id="synthetic_profile",
            decision_scope="restricted_review",
            source_of_truth_refs=(),
            boundary_statuses={"claim_authorization_status": "NOT_AUTHORIZED_BY_THIS_DECISION"},
        )
    )
    assert (
        handoff.handoff_status
        == MethodPromotionGenericAdapterMIPHandoffStatus.HANDOFF_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS
    )


def test_does_not_recompute_readiness_or_decision_status() -> None:
    governance, _, _ = _tbrridge_governance()
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="no_recompute",
            governance_summary=governance,
            generic_packet_status="PACKET_PARTIAL_DIAGNOSTIC_ONLY",
            generic_eligibility_status="ELIGIBLE_AS_REVIEW_INPUT",
            generic_decision_status="REQUEST_ADDITIONAL_EVIDENCE",
        )
    )
    assert handoff.generic_packet_status == "PACKET_PARTIAL_DIAGNOSTIC_ONLY"
    assert handoff.generic_eligibility_status == "ELIGIBLE_AS_REVIEW_INPUT"
    assert handoff.generic_decision_status == "REQUEST_ADDITIONAL_EVIDENCE"
    # Pass-through must not upgrade to approve.
    assert handoff.generic_decision_status != "APPROVE_REVIEW_CONTINUATION"


def test_serializer_returns_json_safe_dict() -> None:
    governance, _, decision_summary = _tbrridge_governance()
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="serialize_me",
            governance_summary=governance,
            generic_decision_status=decision_summary.generic_decision_status,
        )
    )
    payload = serialize_method_promotion_generic_adapter_mip_handoff(handoff)
    assert isinstance(payload, dict)
    assert isinstance(payload["handoff_status"], str)
    assert isinstance(payload["decision_surface_authorization_status"], str)
    assert isinstance(payload["mip_allowed_uses"], list)
    json.dumps(payload)


def test_no_forbidden_true_authorization_fields() -> None:
    governance, _, _ = _tbrridge_governance()
    handoff = build_method_promotion_generic_adapter_mip_handoff(
        MethodPromotionGenericAdapterMIPHandoffInput(
            handoff_id="no_auth_fields",
            governance_summary=governance,
        )
    )
    payload = serialize_method_promotion_generic_adapter_mip_handoff(handoff)
    for key in _FORBIDDEN_TRUE_KEYS:
        assert key not in payload or payload[key] is not True
    assert payload["decision_surface_authorization_status"] == _AUTH.value
    assert payload["method_promotion_status"] == _PROMO.value
