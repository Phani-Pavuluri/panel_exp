"""Governance tests for AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_RUNTIME = _REPO / "panel_exp/validation/augsynth_jackknife_promotion_evidence_packet_runtime_001.py"
_DOC = _REPO / "docs/track_d/AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_INSTRUMENT = "geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review"
_ALIAS = "geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only"
_VERDICT = (
    "augsynth_jackknife_evidence_packet_runtime_implemented_no_promotion_no_claim_authorization"
)
_NEXT_CONTRACT = "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001"
_LANE_A_NEXT = "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001"

_ALLOWED_TRUE_FLAGS = ("runtime_implemented", "augsynth_runtime_implemented")

_FORBIDDEN_TRUE_FLAGS = (
    "augsynth_decision_contract_implemented",
    "generic_runtime_changed",
    "generic_adapter_profile_for_augsynth_implemented",
    "method_promoted",
    "instrument_promoted",
    "augsynth_promoted",
    "did_promoted",
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
    "production_readout_authorized",
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
    "alias_substitution_blocked",
    "research_only_substitution_blocked",
    "allowed_surface_enforced",
    "required_evidence_categories_enforced",
    "non_empty_artifact_ref_required",
    "scm_evidence_substitution_blocked",
    "tbrridge_evidence_substitution_blocked",
    "lane_b_evidence_substitution_blocked",
    "readiness_precedence_implemented",
    "eligibility_mapping_implemented",
    "blockers_emitted",
    "warnings_emitted",
    "fixed_non_authorization_statuses_emitted",
    "generic_framework_compatibility_preserved",
    "evidence_quality_boundary_preserved",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_runtime_module_exists() -> None:
    assert _RUNTIME.exists()


def test_import_api_works() -> None:
    mod = importlib.import_module(
        "panel_exp.validation.augsynth_jackknife_promotion_evidence_packet_runtime_001"
    )
    assert hasattr(mod, "AugSynthJackknifeEvidenceReference")
    assert hasattr(mod, "AugSynthJackknifePromotionEvidencePacketInput")
    assert hasattr(mod, "AugSynthJackknifePromotionEvidencePacket")
    assert hasattr(mod, "AugSynthJackknifePacketReadinessStatus")
    assert hasattr(mod, "AugSynthJackknifePromotionReviewEligibilityStatus")
    assert hasattr(mod, "assemble_augsynth_jackknife_promotion_evidence_packet")


def test_doc_exists() -> None:
    assert _DOC.exists()
    text = _DOC.read_text(encoding="utf-8")
    assert "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001" in text
    assert _VERDICT in text


def test_summary_json_validates() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "augsynth_jackknife_promotion_evidence_packet_runtime"


def test_exact_identity_enforced() -> None:
    data = _load_summary()
    text = _DOC.read_text(encoding="utf-8")
    assert data["instrument_identity"] == _INSTRUMENT
    assert _INSTRUMENT in text
    assert data["exact_instrument_identity_enforced"] is True


def test_alias_and_research_only_substitution_blocked() -> None:
    data = _load_summary()
    text = _DOC.read_text(encoding="utf-8")
    assert data["alias_substitution_blocked"] is True
    assert data["research_only_substitution_blocked"] is True
    assert _ALIAS in text
    assert "PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT" in text


def test_allowed_surface_enforced() -> None:
    text = _DOC.read_text(encoding="utf-8")
    assert "restricted_review" in text
    assert _load_summary()["allowed_surface_enforced"] is True


def test_required_categories_and_artifact_ref_enforced() -> None:
    text = _DOC.read_text(encoding="utf-8")
    assert "augmentation_component_diagnostics" in text
    data = _load_summary()
    assert data["required_evidence_categories_enforced"] is True
    assert data["non_empty_artifact_ref_required"] is True


def test_substitution_blocked() -> None:
    data = _load_summary()
    text = _DOC.read_text(encoding="utf-8")
    assert data["scm_evidence_substitution_blocked"] is True
    assert data["tbrridge_evidence_substitution_blocked"] is True
    assert data["lane_b_evidence_substitution_blocked"] is True
    assert "cannot substitute" in text.lower() or "SUBSTITUTION" in text


def test_readiness_precedence_and_eligibility_mapping() -> None:
    text = _DOC.read_text(encoding="utf-8")
    assert "Readiness precedence" in text
    assert "ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT" in text
    data = _load_summary()
    assert data["readiness_precedence_implemented"] is True
    assert data["eligibility_mapping_implemented"] is True


def test_blockers_warnings_and_boundary_statuses() -> None:
    text = _DOC.read_text(encoding="utf-8")
    assert "AUGSYNTH_PACKET_BLOCKED" in text
    assert "AUGSYNTH_WARNING_DIAGNOSTIC_INTERVAL_NOT_PRODUCTION_CI" in text
    assert "NOT_AUTHORIZED_BY_THIS_PACKET" in text
    data = _load_summary()
    assert data["blockers_emitted"] is True
    assert data["warnings_emitted"] is True
    assert data["fixed_non_authorization_statuses_emitted"] is True


def test_generic_compatibility_and_evidence_quality_boundary() -> None:
    text = _DOC.read_text(encoding="utf-8")
    assert "generic runtime" in text.lower()
    assert "quality" in text.lower()
    data = _load_summary()
    assert data["generic_framework_compatibility_preserved"] is True
    assert data["evidence_quality_boundary_preserved"] is True


def test_required_true_flags_present() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag
    for flag in _ALLOWED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == _NEXT_CONTRACT
    assert _NEXT_CONTRACT in _DOC.read_text(encoding="utf-8")


def test_roadmap_references_artifact() -> None:
    assert "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001" in _ROADMAP.read_text(
        encoding="utf-8"
    )


def test_mip_audit_registry_references_artifact() -> None:
    assert "AUGSYNTH-JACKKNIFE-PROMOTION-EVIDENCE-PACKET-RUNTIME-001" in _MIP_AUDIT_REGISTRY.read_text(
        encoding="utf-8"
    )


def test_method_soundness_references_artifact() -> None:
    assert "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001" in _METHOD_SOUNDNESS.read_text(
        encoding="utf-8"
    )


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == _LANE_A_NEXT
