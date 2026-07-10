"""Tests for METHOD_PROMOTION_GENERIC_RUNTIME_001."""

from __future__ import annotations

from panel_exp.validation.method_promotion_generic_runtime_001 import (
    MethodPromotionGenericAdapterStatus,
    SCM_CATALOG_ALIAS,
    SCM_INSTRUMENT_IDENTITY,
    TBRRIDGE_INSTRUMENT_IDENTITY,
    adapt_method_promotion_decision_to_generic_summary,
    adapt_method_promotion_packet_to_generic_summary,
    build_method_promotion_governance_summary,
    run_validation,
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


def _tbrridge_ready_packet():
    return assemble_tbrridge_promotion_evidence_packet(
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
            lineage={"source": "unit_test"},
            warnings=["packet_warning"],
        )
    )


def _scm_ready_packet():
    return assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
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
            lineage={"source": "unit_test"},
            warnings=["scm_warning"],
        )
    )


def _tbrridge_ready_decision():
    packet = _tbrridge_ready_packet()
    return decide_tbrridge_promotion_review(
        TBRRidgePromotionReviewDecisionInput(
            decision_id="tbrridge_decision",
            packet=packet,
            lineage={"decision": "unit_test"},
            warnings=["decision_warning"],
        )
    )


def _scm_ready_decision():
    packet = _scm_ready_packet()
    return decide_scm_jackknife_null_monitor_review(
        SCMJackknifeNullMonitorReviewDecisionInput(
            decision_id="scm_decision",
            packet=packet,
            lineage={"decision": "unit_test"},
            warnings=["decision_warning"],
        )
    )


def test_tbrridge_ready_packet_adapts_to_generic_packet_ready() -> None:
    summary = adapt_method_promotion_packet_to_generic_summary(_tbrridge_ready_packet())
    assert summary.adapter_status == MethodPromotionGenericAdapterStatus.ADAPTED
    assert summary.generic_packet_readiness_status == "PACKET_READY_FOR_REVIEW_INPUT"
    assert (
        summary.instrument_specific_packet_readiness_status
        == "PACKET_READY_FOR_PROMOTION_REVIEW_INPUT"
    )
    assert summary.generic_review_eligibility_status == "ELIGIBLE_AS_REVIEW_INPUT"


def test_scm_ready_packet_adapts_to_generic_packet_ready() -> None:
    summary = adapt_method_promotion_packet_to_generic_summary(_scm_ready_packet())
    assert summary.adapter_status == MethodPromotionGenericAdapterStatus.ADAPTED
    assert summary.generic_packet_readiness_status == "PACKET_READY_FOR_REVIEW_INPUT"
    assert (
        summary.instrument_specific_packet_readiness_status
        == "PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT"
    )


def test_tbrridge_approval_adapts_with_restricted_review_scope() -> None:
    summary = adapt_method_promotion_decision_to_generic_summary(_tbrridge_ready_decision())
    assert summary.adapter_status == MethodPromotionGenericAdapterStatus.ADAPTED
    assert summary.generic_decision_status == "APPROVE_REVIEW_CONTINUATION"
    assert summary.decision_scope == "restricted_review"
    assert (
        summary.instrument_specific_decision_status
        == "APPROVE_RESTRICTED_REVIEW_CONTINUATION"
    )


def test_scm_approval_adapts_with_null_monitor_scope() -> None:
    summary = adapt_method_promotion_decision_to_generic_summary(_scm_ready_decision())
    assert summary.adapter_status == MethodPromotionGenericAdapterStatus.ADAPTED
    assert summary.generic_decision_status == "APPROVE_REVIEW_CONTINUATION"
    assert summary.decision_scope == "null_monitor"
    assert (
        summary.instrument_specific_decision_status
        == "APPROVE_NULL_MONITOR_REVIEW_CONTINUATION"
    )


def test_request_additional_evidence_remains_request_additional_evidence() -> None:
    packet = _tbrridge_ready_packet()
    packet_dict = packet.to_dict()
    packet_dict["packet_readiness_status"] = "PACKET_PARTIAL_DIAGNOSTIC_ONLY"
    packet_dict["promotion_review_eligibility_status"] = "NOT_ELIGIBLE_MISSING_EVIDENCE"
    packet_dict["missing_evidence"] = ["sensitivity"]
    decision = decide_tbrridge_promotion_review(
        TBRRidgePromotionReviewDecisionInput(decision_id="req_evidence", packet=packet_dict)
    )
    summary = adapt_method_promotion_decision_to_generic_summary(decision)
    assert summary.generic_decision_status == "REQUEST_ADDITIONAL_EVIDENCE"
    assert summary.instrument_specific_decision_status == "REQUEST_ADDITIONAL_EVIDENCE"


def test_unknown_instrument_identity_blocks() -> None:
    summary = adapt_method_promotion_packet_to_generic_summary(
        {
            "packet_id": "unknown",
            "instrument_identity": "geo.unknown.method",
            "packet_readiness_status": "PACKET_READY_FOR_PROMOTION_REVIEW_INPUT",
            "promotion_review_eligibility_status": "ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT",
        }
    )
    assert summary.adapter_status == MethodPromotionGenericAdapterStatus.BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY
    assert "GENERIC_ADAPTER_BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY" in summary.adapter_blockers


def test_alias_substitution_attempt_blocks() -> None:
    packet = _scm_ready_packet().to_dict()
    packet["instrument_identity"] = SCM_CATALOG_ALIAS
    summary = adapt_method_promotion_packet_to_generic_summary(packet)
    assert summary.adapter_status == MethodPromotionGenericAdapterStatus.BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT
    assert "GENERIC_ADAPTER_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT" in summary.adapter_blockers


def test_unmapped_packet_status_blocks() -> None:
    packet = _tbrridge_ready_packet().to_dict()
    packet["packet_readiness_status"] = "PACKET_STATUS_DOES_NOT_EXIST"
    summary = adapt_method_promotion_packet_to_generic_summary(packet)
    assert summary.adapter_status == MethodPromotionGenericAdapterStatus.BLOCKED_UNMAPPED_PACKET_STATUS
    assert summary.generic_packet_readiness_status is None


def test_unmapped_eligibility_status_blocks() -> None:
    packet = _tbrridge_ready_packet().to_dict()
    packet["promotion_review_eligibility_status"] = "ELIGIBILITY_STATUS_DOES_NOT_EXIST"
    summary = adapt_method_promotion_packet_to_generic_summary(packet)
    assert (
        summary.adapter_status
        == MethodPromotionGenericAdapterStatus.BLOCKED_UNMAPPED_ELIGIBILITY_STATUS
    )


def test_unmapped_decision_status_blocks() -> None:
    decision = _tbrridge_ready_decision().to_dict()
    decision["decision_status"] = "DECISION_STATUS_DOES_NOT_EXIST"
    summary = adapt_method_promotion_decision_to_generic_summary(decision)
    assert summary.adapter_status == MethodPromotionGenericAdapterStatus.BLOCKED_UNMAPPED_DECISION_STATUS


def test_missing_boundary_status_blocks() -> None:
    decision = _tbrridge_ready_decision().to_dict()
    decision.pop("claim_authorization_status")
    summary = adapt_method_promotion_decision_to_generic_summary(decision)
    assert summary.adapter_status == MethodPromotionGenericAdapterStatus.BLOCKED_MISSING_BOUNDARY_STATUS


def test_prohibited_action_weakening_blocks() -> None:
    decision = _tbrridge_ready_decision().to_dict()
    decision["prohibited_next_actions"] = ["method_promotion"]
    summary = adapt_method_promotion_decision_to_generic_summary(decision)
    assert (
        summary.adapter_status
        == MethodPromotionGenericAdapterStatus.BLOCKED_PROHIBITED_ACTION_WEAKENED
    )


def test_missing_evidence_blockers_warnings_lineage_preserved() -> None:
    packet = _tbrridge_ready_packet()
    packet_dict = packet.to_dict()
    packet_dict["missing_evidence"] = ["sensitivity"]
    packet_dict["blockers"] = ["BLOCKED_MISSING_SENSITIVITY_EVIDENCE"]
    summary = adapt_method_promotion_packet_to_generic_summary(packet_dict)
    assert summary.missing_evidence == ("sensitivity",)
    assert summary.blockers == ("BLOCKED_MISSING_SENSITIVITY_EVIDENCE",)
    assert "packet_warning" in summary.warnings
    assert summary.lineage.get("source") == "unit_test"


def test_governance_summary_combines_packet_and_decision() -> None:
    packet_summary = adapt_method_promotion_packet_to_generic_summary(_scm_ready_packet())
    decision_summary = adapt_method_promotion_decision_to_generic_summary(_scm_ready_decision())
    governance = build_method_promotion_governance_summary(packet_summary, decision_summary)
    assert governance.current_framework_stage == "decision_ready"
    assert governance.current_review_state == "APPROVE_REVIEW_CONTINUATION"
    assert governance.packet_summary_ref == packet_summary.summary_id
    assert governance.decision_summary_ref == decision_summary.summary_id
    assert governance.instrument_identity == SCM_INSTRUMENT_IDENTITY


def test_governance_summary_does_not_authorize_claims_catalog_production() -> None:
    packet_summary = adapt_method_promotion_packet_to_generic_summary(_tbrridge_ready_packet())
    decision_summary = adapt_method_promotion_decision_to_generic_summary(_tbrridge_ready_decision())
    governance = build_method_promotion_governance_summary(packet_summary, decision_summary)
    assert governance.claim_authorization_status == "NOT_AUTHORIZED_BY_THIS_DECISION"
    assert governance.catalog_status == "NOT_UNBLOCKED_BY_THIS_DECISION"
    assert governance.production_compatibility_status == "NOT_AUTHORIZED_BY_THIS_DECISION"
    assert governance.method_promotion_status == "NOT_PROMOTED_BY_THIS_DECISION"
    assert governance.instrument_promotion_status == "NOT_PROMOTED_BY_THIS_DECISION"
    assert governance.mip_decisioning_status == "NOT_AUTHORIZED_BY_THIS_ADAPTER"
    assert governance.trust_report_bypass_status == "NOT_BYPASSED_BY_THIS_ADAPTER"


def test_no_augsynth_or_did_support() -> None:
    summary = adapt_method_promotion_packet_to_generic_summary(
        {
            "packet_id": "augsynth",
            "instrument_identity": "geo.augsynth.jackknife.single_cell.delta_mu.null_monitor",
            "packet_readiness_status": "PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT",
            "promotion_review_eligibility_status": "ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT",
        }
    )
    assert summary.adapter_status == MethodPromotionGenericAdapterStatus.BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY


def test_no_raw_evidence_quality_scoring() -> None:
    packet = _tbrridge_ready_packet().to_dict()
    packet["evidence_by_category"] = {
        "null_control_false_positive": [{"artifact_ref": "x", "quality_score": 0.99}]
    }
    summary = adapt_method_promotion_packet_to_generic_summary(packet)
    assert summary.adapter_status == MethodPromotionGenericAdapterStatus.ADAPTED
    assert summary.evidence_category_count == 1


def test_run_validation_passes() -> None:
    summary = run_validation(write_summary=False)
    assert summary["runtime_implemented"] is True
    assert summary["final_verdict"].startswith("generic_method_promotion_adapter_runtime_implemented")
