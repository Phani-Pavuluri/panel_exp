"""Governance tests for SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_RUNTIME_DOC = _REPO / "docs/track_d/SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001_summary.json"
)
_RUNTIME = (
    _REPO
    / "panel_exp/validation/scm_jackknife_null_monitor_promotion_evidence_packet_runtime_001.py"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_INSTRUMENT = "geo.scm.jackknife.single_cell.delta_mu.null_monitor"
_CATALOG_ALIAS = "geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review"
_VERDICT = (
    "scm_jackknife_null_monitor_evidence_packet_runtime_implemented_no_promotion_no_claim_authorization"
)
_NEXT_DECISION_RUNTIME = "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001"
_NEXT_CONTRACT = "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001"
_NEXT_CHECKPOINT = "METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001"
_NEXT_GENERIC = "METHOD_PROMOTION_GENERIC_CONTRACTS_001"
_LANE_A_NEXT = "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001"

_FORBIDDEN_TRUE_FLAGS = (
    "scm_promoted",
    "scm_jackknife_promoted",
    "method_promoted",
    "instrument_promoted",
    "catalog_unblocked",
    "production_compatibility_authorized",
    "claim_authorization_changed",
    "statistical_claim_authorized",
    "confidence_interval_claim_authorized",
    "p_value_claim_authorized",
    "significance_claim_authorized",
    "statistical_power_claim_authorized",
    "causal_lift_claim_authorized",
    "business_lift_claim_authorized",
    "roi_roas_claim_authorized",
    "decision_recommendation_authorized",
    "estimator_implemented",
    "inference_implemented",
    "new_validation_experiments_run",
    "raw_evidence_quality_scored",
    "lane_b_runtime_changed",
    "mip_decisioning_authorized",
    "trust_report_bypassed",
)

_REQUIRED_TRUE_FLAGS = (
    "evidence_packet_runtime_implemented",
    "exact_instrument_identity_enforced",
    "catalog_alias_reconciled_without_substitution",
    "required_evidence_categories_validated",
    "scm_specific_categories_validated",
    "packet_readiness_statuses_emitted",
    "promotion_review_eligibility_emitted",
    "missing_evidence_preserved",
    "blockers_preserved",
    "warnings_lineage_preserved",
    "evidence_substitution_rules_enforced",
    "evidence_quality_boundary_preserved",
    "runtime_implemented",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_runtime_doc_exists() -> None:
    assert _RUNTIME_DOC.exists()
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001" in text
    assert _VERDICT in text
    assert "evidence quality boundary" in text.lower()


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "scm_jackknife_null_monitor_promotion_evidence_packet_runtime"


def test_runtime_module_exists() -> None:
    assert _RUNTIME.exists()
    text = _RUNTIME.read_text(encoding="utf-8")
    assert "assemble_scm_jackknife_null_monitor_promotion_evidence_packet" in text
    assert "SCMJackknifeNullMonitorPromotionEvidencePacket" in text


def test_import_api_works() -> None:
    from panel_exp.validation.scm_jackknife_null_monitor_promotion_evidence_packet_runtime_001 import (
        SCMJackknifeNullMonitorEvidenceReference,
        SCMJackknifeNullMonitorPacketReadinessStatus,
        SCMJackknifeNullMonitorPromotionEvidencePacket,
        SCMJackknifeNullMonitorPromotionEvidencePacketInput,
        SCMJackknifeNullMonitorPromotionReviewEligibilityStatus,
        assemble_scm_jackknife_null_monitor_promotion_evidence_packet,
    )

    assert SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT
    assert SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT
    assert SCMJackknifeNullMonitorPromotionEvidencePacketInput
    assert SCMJackknifeNullMonitorPromotionEvidencePacket
    assert SCMJackknifeNullMonitorEvidenceReference
    assert assemble_scm_jackknife_null_monitor_promotion_evidence_packet


def test_required_true_flags_present() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_exact_instrument_identity_enforced() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert _INSTRUMENT in text
    assert _load_summary()["instrument_identity"] == _INSTRUMENT
    assert _load_summary()["exact_instrument_identity_enforced"] is True


def test_catalog_alias_reconciliation_recorded() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert _CATALOG_ALIAS in text
    assert _load_summary()["catalog_alias"] == _CATALOG_ALIAS
    assert _load_summary()["catalog_alias_reconciled_without_substitution"] is True


def test_required_categories_validated() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "jackknife_stability" in text
    assert "donor_pool_diagnostics" in text
    assert _load_summary()["required_evidence_categories_validated"] is True


def test_scm_specific_categories_validated() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "pre_period_fit_diagnostics" in text
    assert _load_summary()["scm_specific_categories_validated"] is True


def test_readiness_eligibility_emitted() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT" in text
    assert "ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT" in text
    data = _load_summary()
    assert data["packet_readiness_statuses_emitted"] is True
    assert data["promotion_review_eligibility_emitted"] is True


def test_evidence_substitution_rules_enforced() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "TBRRidge" in text or "tbrridge" in text
    assert "Lane B" in text
    assert _load_summary()["evidence_substitution_rules_enforced"] is True


def test_evidence_quality_boundary_preserved() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "does not score" in text.lower() or "does **not** score" in text
    assert _load_summary()["evidence_quality_boundary_preserved"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == _NEXT_CONTRACT


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "SCM-JACKKNIFE-NULL-MONITOR-PROMOTION-EVIDENCE-PACKET-RUNTIME-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001" in text


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == _LANE_A_NEXT
