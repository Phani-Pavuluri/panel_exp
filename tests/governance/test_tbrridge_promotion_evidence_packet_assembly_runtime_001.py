"""Governance tests for TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_RUNTIME_DOC = _REPO / "docs/track_d/TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001_summary.json"
)
_RUNTIME = _REPO / "panel_exp/validation/tbrridge_promotion_evidence_packet_assembly_runtime_001.py"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_INSTRUMENT = "geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review"
_VERDICT = "tbrridge_promotion_evidence_packet_runtime_implemented_no_promotion_no_claim_authorization"

_FORBIDDEN_TRUE_FLAGS = (
    "method_promoted",
    "instrument_promoted",
    "catalog_unblocked",
    "production_compatibility_authorized",
    "claim_authorization_changed",
    "statistical_claim_authorized",
    "confidence_interval_claim_authorized",
    "p_value_claim_authorized",
    "significance_claim_authorized",
    "causal_lift_claim_authorized",
    "business_lift_claim_authorized",
    "roi_roas_claim_authorized",
    "decision_recommendation_authorized",
    "estimator_implemented",
    "inference_implemented",
    "new_validation_experiments_run",
    "lane_b_runtime_changed",
)

_REQUIRED_TRUE_FLAGS = (
    "evidence_packet_runtime_implemented",
    "exact_instrument_identity_enforced",
    "required_evidence_categories_validated",
    "claim_boundary_required",
    "missing_evidence_blockers_emitted",
    "promotion_review_eligibility_emitted",
    "allowed_surfaces_preserved",
    "prohibited_surfaces_preserved",
    "lane_b_not_substituted_for_method_validity",
    "no_evidence_fabrication",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_runtime_doc_exists() -> None:
    assert _RUNTIME_DOC.exists()
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001" in text
    assert _VERDICT in text
    assert "no evidence fabrication" in text.lower()


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "tbrridge_promotion_evidence_packet_assembly_runtime"


def test_runtime_module_exists() -> None:
    assert _RUNTIME.exists()
    text = _RUNTIME.read_text(encoding="utf-8")
    assert "assemble_tbrridge_promotion_evidence_packet" in text
    assert "TBRRidgePromotionEvidencePacket" in text


def test_import_api_works() -> None:
    from panel_exp.validation.tbrridge_promotion_evidence_packet_assembly_runtime_001 import (
        TBRRidgeEvidenceReference,
        TBRRidgePacketReadinessStatus,
        TBRRidgePromotionEvidencePacket,
        TBRRidgePromotionEvidencePacketInput,
        TBRRidgePromotionReviewEligibilityStatus,
        assemble_tbrridge_promotion_evidence_packet,
    )

    assert TBRRidgePacketReadinessStatus.PACKET_READY_FOR_PROMOTION_REVIEW_INPUT
    assert TBRRidgePromotionReviewEligibilityStatus.ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT
    assert TBRRidgePromotionEvidencePacketInput
    assert TBRRidgePromotionEvidencePacket
    assert TBRRidgeEvidenceReference
    assert assemble_tbrridge_promotion_evidence_packet


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


def test_required_categories_validated() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "null_control_false_positive" in text
    assert "positive_control_recovery" in text
    assert _load_summary()["required_evidence_categories_validated"] is True


def test_claim_boundary_required() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "claim_boundary" in text
    assert _load_summary()["claim_boundary_required"] is True


def test_missing_evidence_blockers_emitted() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "BLOCKED_MISSING" in text
    assert _load_summary()["missing_evidence_blockers_emitted"] is True


def test_promotion_review_eligibility_emitted() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT" in text
    assert _load_summary()["promotion_review_eligibility_emitted"] is True


def test_no_evidence_fabrication_stated() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "fabricat" in text.lower() or "no evidence fabrication" in text.lower()
    assert _load_summary()["no_evidence_fabrication"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001"


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "TBRRIDGE-PROMOTION-EVIDENCE-PACKET-ASSEMBLY-RUNTIME-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001" in text


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == "METHOD_PROMOTION_GENERIC_RUNTIME_001"
